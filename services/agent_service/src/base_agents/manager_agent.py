import json
import time
from typing import Any, Dict, List

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler

from ..protocols.message import Message
from ..utils.logging import get_logger, setup_logger
from ..utils.parsing import extract_all_sources_from_plan, safe_json_parse
import time
from ..utils.logging import setup_logger, get_logger
from ..protocols.schemas import EvalAgentInput,EvalAgentOutput
from ..protocols.schemas import EditorAgentInput,EditorAgentOutput
from ..utils.exceptions import (
    AgentServiceException, PlanningError, ExecutionError, EvaluationError,
    ExternalServiceError, ValidationError, TimeoutError, NetworkError,
    handle_agent_error, create_error_response
)

setup_logger()
logger = get_logger("ManagerAgent")
EVALUATION_PASS_THRESHOLD=1.0
class ManagerAgent(RoutedAgent):

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
        # Store conversation history per session
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}

    def _get_context(self, session_id: str) -> str:
        """Get conversation context for the current session."""
        if session_id not in self.conversation_history:
            return ""

        history = self.conversation_history[session_id]
        if not history:
            return ""

        # Get only the last Q&A pair for context
        last_qa = history[-1]
        context = "\nPrevious conversation:\n"
        context += f"Q: {last_qa['question']}\nA: {last_qa['answer']}\n"
        return context

    def _update_history(self, session_id: str, question: str, answer: str):
        """Update conversation history for the session."""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        self.conversation_history[session_id].append(
            {"question": question, "answer": answer}
        )

        # Keep only last 5 conversations to manage memory
        if len(self.conversation_history[session_id]) > 5:
            self.conversation_history[session_id] = self.conversation_history[
                session_id
            ][-5:]

    def _handle_planning_error(self, error: Exception, user_query: str, session_id: str) -> Message:
        """Handle planning phase errors with structured error handling."""
        logger.error(f"[ManagerAgent] Planning error: {error}")
        
        if isinstance(error, PlanningError):
            error_response = create_error_response(error, self.trace_info, session_id)
        else:
            error_response = handle_agent_error(
                error, 
                "planning", 
                self.trace_info, 
                session_id
            )
        
        self._update_history(session_id, user_query, error_response.get("user_message", "Planning failed"))
        return Message(content=json.dumps(error_response))

    def _handle_execution_error(self, error: Exception, user_query: str, session_id: str) -> Message:
        """Handle execution phase errors with structured error handling."""
        logger.error(f"[ManagerAgent] Execution error: {error}")
        
        if isinstance(error, ExecutionError):
            error_response = create_error_response(error, self.trace_info, session_id)
        else:
            error_response = handle_agent_error(
                error, 
                "execution", 
                self.trace_info, 
                session_id
            )
        
        self._update_history(session_id, user_query, error_response.get("user_message", "Execution failed"))
        return Message(content=json.dumps(error_response))

    def _handle_evaluation_error(self, error: Exception, user_query: str, session_id: str, fallback_answer: str) -> Message:
        """Handle evaluation phase errors with fallback to executor answer."""
        logger.error(f"[ManagerAgent] Evaluation error: {error}")
        
        # Use fallback answer but still provide error context
        self.trace_info.update({
            'final_answer': fallback_answer,
            'evaluation_agent': [],
            'editor_agent': [],
            'evaluation_skipped': True,
            'skip_reason': f"Evaluation failed: {str(error)}",
            'total_time': time.time() - self.trace_info.get("start_time", time.time())
        })
        
        # Create a warning-level error response
        if isinstance(error, EvaluationError):
            error_response = create_error_response(error, self.trace_info, session_id)
        else:
            error_response = handle_agent_error(
                error, 
                "evaluation", 
                self.trace_info, 
                session_id
            )
        
        self._update_history(session_id, user_query, fallback_answer)
        return Message(content=json.dumps(error_response))

    @message_handler
    async def handle_user_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        start_time = time.time()
        session_id = ctx.session_id if hasattr(ctx, "session_id") else "default"

        # Get conversation context
        context = self._get_context(session_id)
        user_query = message.content

        # If there's context, prepend it to the query
        if context:
            user_query = user_query

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
            try:
                plan = await self.send_message(
                    Message(content=user_query), self.planner_agent_id
                )
                logger.info(f"[PlannerAgent] Output: {plan.content}")
                plan_data = safe_json_parse(plan.content)
            except Exception as e:
                return self._handle_planning_error(e, user_query, session_id)

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
                try:
                    refined = await self.send_message(
                        Message(content=json.dumps(current_plan)),
                        self.planner_refiner_agent_id,
                    )
                    logger.info(f"[PlannerRefinerAgent] Output: {refined.content}")
                    refiner_data = safe_json_parse(refined.content)
                    refinement_attempts.append(refiner_data)
                except Exception as e:
                    logger.warning(f"[ManagerAgent] Refiner error, continuing with current plan: {e}")
                    break

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
                
                try:
                    plan = await self.send_message(
                        Message(content=json.dumps(feedback_payload)), self.planner_agent_id
                    )
                    logger.info(f"[PlannerAgent] Refined output: {plan.content}")
                    
                    plan_data = safe_json_parse(plan.content)
                    if 'error' in plan_data:
                        logger.error(f"Error in planner refinement: {plan_data['error']}")
                        break

                    current_plan = plan_data.get("plan")
                    if not current_plan:
                        logger.error("No plan returned from planner after refinement")
                        break

                    # Store refined plan
                    plan_versions.append(plan_data)
                    self.trace_info["planner_agent"] = plan_versions
                except Exception as e:
                    logger.error(f"Error in planner refinement: {e}")
                    break

                retry_count += 1
                logger.info(f"Refinement attempt {retry_count}/{max_retries}")

                logger.info(f"Refined plan: {json.dumps(current_plan, indent=2)}")

            self.trace_info["planner_refiner_agent"] = refinement_attempts

            # Execute the plan
            try:
                query_result = await self.send_message(Message(content=json.dumps(current_plan)), self.executor_agent_id)
                self.trace_info['executor_agent'] = safe_json_parse(query_result.content)
                q_output = self.trace_info['executor_agent']
            except Exception as e:
                return self._handle_execution_error(e, user_query, session_id)

            execution_error = q_output.get('error')
            if execution_error:
                self.trace_info.update({
                    'final_answer': q_output.get("answer", "Execution failed."),
                    'evaluation_skipped': True,
                    'skip_reason': f"Executor returned error: {execution_error}",
                    'total_time': time.time() - start_time
                })
                self._update_history(session_id, message.content, self.trace_info['final_answer'])
                return Message(content=json.dumps({'trace_info': self.trace_info}))

            answer = q_output.get("combined_answer_of_sources")
            
            if not answer or not isinstance(answer, str) or answer.strip() == "":
                self.trace_info.update({
                    'final_answer': "No valid answer generated by executor.",
                    'evaluation_skipped': True,
                    'skip_reason': "Executor produced no answer for evaluation.",
                    'total_time': time.time() - start_time
                })
                self._update_history(session_id, message.content, self.trace_info['final_answer'])
                return Message(content=json.dumps({'trace_info': self.trace_info}))

            documents = q_output.get("all_documents", [])
            documents_by_source = q_output.get("documents_by_source", {})
            
            # Check if Notion or GitHub sources are used
            skip_evaluation = False
            skip_reason = None
            
            for source_name in documents_by_source.keys():
                source_lower = source_name.lower() if isinstance(source_name, str) else ""
                if "notion" in source_lower or "github" in source_lower:
                    skip_evaluation = True
                    skip_reason = f"Evaluation skipped because {source_name} source was used"
                    break
                    
            if skip_evaluation:
                # Skip evaluation and return the answer directly
                final_answer = answer
                eval_history = []
                editor_history = []
                logger.info(f"[ManagerAgent] {skip_reason}")
            else:
                try:
                    final_answer, eval_history, editor_history = await self.run_evaluation_loop(
                        question=user_query,
                        initial_answer=answer,
                        contexts=documents,
                        documents_by_source=documents_by_source,
                    )
                except Exception as e:
                    return self._handle_evaluation_error(e, user_query, session_id, answer)

            self.trace_info.update({
                'evaluation_agent': eval_history,
                'editor_agent': editor_history,
                'final_answer': final_answer,
                'total_time': time.time() - start_time,
                'evaluation_skipped': False,
                'skip_reason': None
            })
            self._update_history(session_id, message.content, final_answer)

            return Message(content=json.dumps({'trace_info': self.trace_info}))

        except Exception as e:
            # Handle any unexpected errors
            logger.error(f"[ManagerAgent] Unexpected error: {e}")
            error_response = handle_agent_error(
                e, 
                "manager_workflow", 
                self.trace_info, 
                session_id
            )
            self._update_history(session_id, message.content, error_response.get("user_message", "Workflow failed"))
            return Message(content=json.dumps(error_response))

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

        try:
            while attempts < max_attempts:
                logger.info(f"[EvaluationAgent] Input (Attempt {attempts + 1})")
                eval_payload = EvalAgentInput(
                    question=question,
                    answer=current_answer,
                    contexts=contexts,
                )
                eval_resp = await self.send_message(
                    Message(content=eval_payload.model_dump_json()), self.eval_agent_id
                )
                eval_result = EvalAgentOutput.model_validate_json(eval_resp.content)

                score = float(eval_result.score)
                reasoning = eval_result.reasoning or ""
                error = eval_result.error

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

                if error is None and score >= EVALUATION_PASS_THRESHOLD:
                    # Evaluation passed, editor never called
                    editor_agent.append({
                        "attempt": attempts
                    })
                    break

                if attempts == max_attempts - 1:
                    # Final evaluation attempt failed
                    break

                logger.info(f"[EditorAgent] Input (Attempt {attempts + 1})")
                editor_payload = EditorAgentInput(
                    question=question,
                    previous_answer=current_answer,
                    score=score,
                    reasoning=reasoning,
                    contexts=documents_by_source,
                )
                editor_resp = await self.send_message(
                    Message(content=editor_payload.json()), self.editor_agent_id
                )
                editor_result = EditorAgentOutput.model_validate_json(editor_resp.content)

                new_answer = editor_result.get("answer", current_answer)
                editor_error = editor_result.get("error", None)

                editor_agent.append({
                    "editor_history": {
                        "answer": new_answer,
                        "error": editor_error,
                        "skipped": False
                    },
                    "attempt": attempts + 1
                })

                current_answer = new_answer
                attempts += 1

            return current_answer, eval_history, editor_agent

        except Exception as e:
            logger.error(f"[ManagerAgent] Evaluation or editing failed: {e}")
            raise EvaluationError(
                message=f"Evaluation loop failed: {str(e)}",
                details={"attempts": attempts, "max_attempts": max_attempts}
            )
