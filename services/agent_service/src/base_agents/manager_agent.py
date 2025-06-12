import asyncio
import json
import time
from typing import Any, Dict, List

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler

from ..protocols.message import Message
from ..utils.logging import get_logger, setup_logger
from ..utils.memory_client import remember, recall
from ..utils.parsing import extract_all_sources_from_plan, safe_json_parse

setup_logger()
logger = get_logger("ManagerAgent")


class ManagerAgent(RoutedAgent):
    _SKIP_EVALUATION_SOURCES = frozenset(["github", "notion"])

    def __init__(
        self,
        planner_agent_id: AgentId,
        planner_refiner_agent_id: AgentId,
        executor_agent_id: AgentId,
        eval_agent_id: AgentId,
        editor_agent_id: AgentId,
    ) -> None:
        super().__init__("manager_agent")
        self.planner_agent_id = planner_agent_id
        self.planner_refiner_agent_id = planner_refiner_agent_id
        self.executor_agent_id = executor_agent_id
        self.eval_agent_id = eval_agent_id
        self.editor_agent_id = editor_agent_id

        self.trace_info = {}
        self.attempts = []

    def _should_skip_evaluation(self, plan_data: Dict[str, Any]) -> bool:
        """
        Check if evaluation and editing should be skipped based on selected sources.
        Returns True if GitHub or Notion are selected as sources.
        """
        try:
            all_extracted_sources = extract_all_sources_from_plan(plan_data)
            # Convert all sources to lowercase strings for comparison
            sources_lower = {str(source).lower() for source in all_extracted_sources}

            # Check for intersection with the skip sources
            if sources_lower.intersection(self._SKIP_EVALUATION_SOURCES):
                logger.info(
                    f"Found intersection with skip sources: {sources_lower.intersection(self._SKIP_EVALUATION_SOURCES)}. Skipping evaluation and editing."
                )
                return True

            return False

        except Exception as e:
            logger.warning(f"Error checking sources for evaluation skip: {e}")
            return False

    @message_handler
    async def handle_user_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        start_time = time.time()
        session_id = getattr(ctx, "session_id", "default")
        mem_snips  = await recall(session_id, message.content, k=3)
        context    = "\n".join(mem_snips) if mem_snips else ""
        user_query = f"{context}\n\n{message.content}" if context else message.content

        logger.info(f"[ManagerAgent] Final query with context: {user_query}")

        self.trace_info = {
            "start_time": start_time,
            "user_query": user_query,
            "planner_agent": None,
            "planner_refiner_agent": None,
            "executor_agent": None,
            "evaluation_agent": [],
            "editor_agent": [],
            "errors": [],
            "total_time": None,
            "evaluation_skipped": False,
            "skip_reason": None,
        }

        try:
            # Initial plan generation
            logger.info(f"[PlannerAgent] Input: {user_query}")
            plan = await self.send_message(
                Message(content=user_query), self.planner_agent_id
            )
            logger.info(f"[PlannerAgent] Output: {plan.content}")
            plan_data = safe_json_parse(plan.content)

            # Store original plan
            plan_versions = [plan_data]
            self.trace_info["planner_agent"] = plan_versions

            # Feedback loop between planner and refiner
            max_retries = 3
            retry_count = 0
            current_plan = plan_data.get("plan")
            refinement_attempts = []

            while retry_count < max_retries:
                # Get feedback from refiner
                logger.info(f"[PlannerRefinerAgent] Input: {current_plan}")
                refined = await self.send_message(
                    Message(content=json.dumps(current_plan)),
                    self.planner_refiner_agent_id,
                )
                logger.info(f"[PlannerRefinerAgent] Output: {refined.content}")
                refiner_data = safe_json_parse(refined.content)
                refinement_attempts.append(refiner_data)

                # If no refinement needed, break the loop
                if refiner_data.get("refinement_required") == "no":
                    break

                # Get refined plan from planner with feedback
                logger.info(f"[PlannerAgent] Refining with feedback: {refiner_data}")
                feedback_payload = {
                    "query": user_query,
                    "feedback": {
                        "refinement_required": refiner_data.get(
                            "refinement_required", "no"
                        ),
                        "feedback_summary": refiner_data.get("feedback_summary", ""),
                        "feedback_reasoning": refiner_data.get(
                            "feedback_reasoning", []
                        ),
                        "current_plan": current_plan,
                    },
                }

                # Send feedback to planner and get refined plan
                plan = await self.send_message(
                    Message(content=json.dumps(feedback_payload)), self.planner_agent_id
                )
                logger.info(f"[PlannerAgent] Refined output: {plan.content}")

                # Parse the new plan
                plan_data = safe_json_parse(plan.content)
                if "error" in plan_data:
                    logger.error(f"Error in planner refinement: {plan_data['error']}")
                    break

                current_plan = plan_data.get("plan")
                if not current_plan:
                    logger.error("No plan returned from planner after refinement")
                    break

                # Store refined plan
                plan_versions.append(plan_data)
                self.trace_info["planner_agent"] = plan_versions

                retry_count += 1
                logger.info(f"Refinement attempt {retry_count}/{max_retries}")

                logger.info(f"Refined plan: {json.dumps(current_plan, indent=2)}")

            # Store all refinement attempts in trace_info
            self.trace_info["planner_refiner_agent"] = refinement_attempts

            query_result = await self.send_message(
                Message(content=json.dumps(current_plan)), self.executor_agent_id
            )
            self.trace_info["executor_agent"] = safe_json_parse(query_result.content)

            q_output = self.trace_info["executor_agent"]
            if q_output.get("error") is not None:
                raise ValueError(f"Query execution failed: {q_output['error']}")

            answer = q_output.get("combined_answer_of_sources", "")
            documents = q_output.get("all_documents", [])
            documents_by_source = q_output.get("documents_by_source", [])

            # Check if we should skip evaluation and editing
            should_skip = self._should_skip_evaluation(plan_data)

            if should_skip:
                # Skip evaluation and editing, use the answer directly
                final_answer = answer
                eval_history = []
                editor_agent = []
                self.trace_info["evaluation_skipped"] = True
                self.trace_info["skip_reason"] = "GitHub or Notion source detected"
                logger.info(
                    "Skipping evaluation and editing due to GitHub/Notion source selection"
                )
            else:
                # Run normal evaluation loop
                final_answer, eval_history, editor_agent = (
                    await self.run_evaluation_loop(
                        question=user_query,
                        initial_answer=answer,
                        contexts=documents,
                        documents_by_source=documents_by_source,
                    )
                )

            self.trace_info["evaluation_agent"] = eval_history
            self.trace_info["editor_agent"] = editor_agent
            self.trace_info["final_answer"] = final_answer
            self.trace_info["total_time"] = time.time() - start_time

            # Update conversation history
            memory_content = json.dumps({
                "type": "plan",
                "question": user_query,
                "answer": json.dumps(final_answer),   # or store plan directly
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            logger.debug(f"[ManagerAgent] Remembering: {json.dumps(memory_content, indent=2)}")
            try:
                await remember(
                session_id,
                f"Q: {message.content}",
                f"A: {final_answer}\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            except Exception as e:
                logger.error(f"Failed to store memory: {e}")
                # Don't raise the error - memory storage failure shouldn't break the main flow
                self.trace_info["errors"].append(f"Memory storage failed: {str(e)}")
            
            return Message(content=json.dumps({"trace_info": self.trace_info}))

        except Exception as e:
            self.trace_info["errors"].append(str(e))
            self.trace_info["total_time"] = time.time() - start_time
            return Message(
                content=json.dumps(
                    {
                        "error": f"Workflow failed: {str(e)}",
                        "trace_info": self.trace_info,
                    }
                )
            )

    async def run_evaluation_loop(
        self,
        question: str,
        initial_answer: str,
        contexts: List[str],
        documents_by_source: List[str],
    ) -> tuple:
        current_answer = initial_answer
        max_attempts = 2
        attempts = 0
        eval_history = []
        editor_agent = []

        while attempts < max_attempts:
            eval_payload = {
                "question": question,
                "answer": current_answer,
                "contexts": contexts,
            }

            logger.info(f"[EvaluationAgent] Input (Attempt {attempts + 1})")
            eval_resp = await self.send_message(
                Message(content=json.dumps(eval_payload)), self.eval_agent_id
            )

            eval_result = safe_json_parse(eval_resp.content)
            score = float(eval_result.get("score", 0))
            reasoning = eval_result.get("reasoning", "")
            error = eval_result.get("error", None)

            eval_history.append(
                {
                    "evaluation_history": {
                        "score": score,
                        "reasoning": reasoning,
                        "error": error,
                    },
                    "attempt": attempts + 1,
                }
            )

            if error is None and score >= 1.0 or attempts == max_attempts - 1:
                break

            editor_payload = {
                "question": question,
                "previous_answer": current_answer,
                "contexts": documents_by_source,
                "score": score,
                "reasoning": reasoning,
            }

            logger.info(f"[EditorAgent] Input (Attempt {attempts + 1}")
            editor_resp = await self.send_message(
                Message(content=json.dumps(editor_payload)), self.editor_agent_id
            )

            editor_result = safe_json_parse(editor_resp.content)
            new_answer = editor_result.get("answer", current_answer)
            editor_error = editor_result.get("error", None)

            editor_agent.append(
                {
                    "editor_history": {"answer": new_answer, "error": editor_error},
                    "attempt": attempts + 1,
                }
            )

            current_answer = new_answer
            attempts += 1

        return current_answer, eval_history, editor_agent
