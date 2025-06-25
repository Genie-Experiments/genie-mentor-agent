import json
import time
from typing import Dict, List

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler

from services.agent_service.src.protocols.message import Message
from services.agent_service.src.utils.parsing import safe_json_parse
from services.agent_service.src.utils.logging import setup_logger, get_logger
from services.agent_service.src.base_agents.manager.utils import run_evaluation_loop

setup_logger()
logger = get_logger("ManagerAgent")


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

        self.trace_info: Dict = {}
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}


    def _get_context(self, session_id: str) -> str:
        history = self.conversation_history.get(session_id, [])
        if not history:
            return ""
        last_qa = history[-1]
        return f"\nPrevious conversation:\nQ: {last_qa['question']}\nA: {last_qa['answer']}\n"

    def _update_history(self, session_id: str, question: str, answer: str):
        self.conversation_history.setdefault(session_id, []).append(
            {"question": question, "answer": answer}
        )
        self.conversation_history[session_id] = self.conversation_history[session_id][
            -5:
        ]


    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        start_time = time.time()
        session_id = getattr(ctx, "session_id", "default")

        user_query = message.content
        context = self._get_context(session_id)
        if context:
            user_query = user_query  # (placeholder for future concatenation)

        # trace skeleton
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
            # ── 1. Planner
            logger.info(f"[PlannerAgent] Input: {user_query}")
            plan_msg = await self.send_message(Message(content=user_query), self.planner_agent_id)
            plan_data = safe_json_parse(plan_msg.content)
            self.trace_info["planner_agent"] = [plan_data]

            # Planner-Refiner loop
            current_plan = plan_data.get("plan")
            plan_versions, refinement_attempts, retry_count, max_retries = [plan_data], [], 0, 3

            while retry_count < max_retries:
                refined_msg = await self.send_message(
                    Message(content=json.dumps(current_plan)), self.planner_refiner_agent_id
                )
                refiner_data = safe_json_parse(refined_msg.content)
                refinement_attempts.append(refiner_data)

                if refiner_data.get("refinement_required") == "no":
                    break

                feedback_payload = {
                    "query": user_query,
                    "feedback": {
                        "refinement_required": refiner_data.get("refinement_required", "no"),
                        "feedback_summary": refiner_data.get("feedback_summary", ""),
                        "feedback_reasoning": refiner_data.get("feedback_reasoning", []),
                        "current_plan": current_plan,
                    },
                }
                plan_msg = await self.send_message(
                    Message(content=json.dumps(feedback_payload)), self.planner_agent_id
                )
                plan_data = safe_json_parse(plan_msg.content)
                if plan_data.get("error") or not plan_data.get("plan"):
                    logger.error("[PlannerAgent] Refinement returned error or no plan")
                    break

                current_plan = plan_data["plan"]
                plan_versions.append(plan_data)
                retry_count += 1

            self.trace_info["planner_agent"] = plan_versions
            self.trace_info["planner_refiner_agent"] = refinement_attempts

            # ── 2. Executor
            exec_msg = await self.send_message(
                Message(content=json.dumps(current_plan)), self.executor_agent_id
            )
            exec_out = safe_json_parse(exec_msg.content)
            self.trace_info["executor_agent"] = exec_out

            if exec_out.get("error"):
                self.trace_info.update(
                    {
                        "final_answer": exec_out.get("answer", "Execution failed."),
                        "evaluation_skipped": True,
                        "skip_reason": f"Executor returned error: {exec_out['error']}",
                        "total_time": time.time() - start_time,
                    }
                )
                self._update_history(session_id, message.content, self.trace_info["final_answer"])
                return Message(content=json.dumps({"trace_info": self.trace_info}))

            answer = exec_out.get("executor_answer", "")
            if not answer.strip():
                self.trace_info.update(
                    {
                        "final_answer": "No valid answer generated by executor.",
                        "evaluation_skipped": True,
                        "skip_reason": "Executor produced no answer for evaluation.",
                        "total_time": time.time() - start_time,
                    }
                )
                self._update_history(session_id, message.content, self.trace_info["final_answer"])
                return Message(content=json.dumps({"trace_info": self.trace_info}))

            documents = exec_out.get("all_documents", [])
            documents_by_source = exec_out.get("documents_by_source", {})

            # ── 3. Evaluation / Editor
            skip_evaluation = any(
                src.lower().find("notion") != -1 or src.lower().find("github") != -1
                for src in documents_by_source
            )
            skip_reason = "Evaluation skipped because Notion/GitHub source was used" if skip_evaluation else None

            if skip_evaluation:
                final_answer, eval_history, editor_history = answer, [], []
            else:
                try:
                    final_answer, eval_history, editor_history = await run_evaluation_loop(
                        send_message_func=self.send_message,
                        eval_agent_id=self.eval_agent_id,
                        editor_agent_id=self.editor_agent_id,
                        question=user_query,
                        initial_answer=answer,
                        contexts=documents,
                        documents_by_source=documents_by_source,
                    )
                except Exception as e:
                    logger.error(f"[ManagerAgent] Evaluation loop failed: {e}")
                    final_answer, eval_history, editor_history = answer, [], []
                    skip_reason = "Evaluation or Editor failed."
                    skip_evaluation = False

            # ── 4. Trace & return
            self.trace_info.update(
                {
                    "evaluation_agent": eval_history,
                    "editor_agent": editor_history,
                    "final_answer": final_answer,
                    "total_time": time.time() - start_time,
                    "evaluation_skipped": skip_evaluation,
                    "skip_reason": skip_reason,
                }
            )
            self._update_history(session_id, message.content, final_answer)
            return Message(content=json.dumps({"trace_info": self.trace_info}))

        except Exception as e:
            self.trace_info["errors"].append(str(e))
            self.trace_info["total_time"] = time.time() - start_time
            return Message(content=json.dumps({"error": str(e), "trace_info": self.trace_info}))
