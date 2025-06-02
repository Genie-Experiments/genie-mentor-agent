import json
import logging
from typing import Any, List
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from ..protocols.message import Message
import time
import logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("autogen_core").setLevel(logging.WARNING)
logging.getLogger("autogen_core.events").setLevel(logging.WARNING)
class ManagerAgent(RoutedAgent):
    def __init__(
        self,
        planner_agent_id: AgentId,
        planner_refiner_agent_id: AgentId,
        executor_agent_id: AgentId,
        eval_agent_id: AgentId,
        editor_agent_id: AgentId
    ) -> None:
        super().__init__('manager_agent')
        self.planner_agent_id = planner_agent_id
        self.planner_refiner_agent_id = planner_refiner_agent_id
        self.executor_agent_id = executor_agent_id
        self.eval_agent_id = eval_agent_id
        self.editor_agent_id = editor_agent_id
        
        self.trace_info = {}
        self.attempts = []

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        start_time = time.time()
        self.trace_info = {
            'start_time': start_time,
            'user_query': message.content,
            'planner_output': None,
            'refiner_output': None,
            'executor_output': None,
            'evaluation_history': [],
            'editor_history': [],
            'final_answer': None,
            'errors': [],
            'total_time': None
        }
        
        try:
            logging.info(f"[PlannerAgent] Input: {message.content}")
            plan = await self.send_message(message, self.planner_agent_id)
            logging.info(f"[PlannerAgent] Output: {plan.content}")
            self.trace_info['planner_output'] = self.safe_json_parse(plan.content)
            
            logging.info(f"[PlannerRefinerAgent] Input: {plan.content}")
            refined = await self.send_message(plan, self.planner_refiner_agent_id)
            logging.info(f"[PlannerRefinerAgent] Output: {refined.content}")
            self.trace_info['refiner_output'] = self.safe_json_parse(refined.content)
            
            logging.info(f"[ExecutorAgent] Input: {refined.content}")
            query_result = await self.send_message(refined, self.executor_agent_id)
            logging.info(f"[ExcutorAgent] Output: {query_result.content}")
            self.trace_info['executor_output'] = self.safe_json_parse(query_result.content)
            
            q_output = self.trace_info['executor_output']
            if 'error' in q_output:
                raise ValueError(f"Query execution failed: {q_output['error']}")
                
            answer = q_output.get("combined_answer_of_sources", "")
            documents = q_output.get("top_documents", [])
            
            final_answer, eval_history, editor_history = await self.run_evaluation_loop(
                question=message.content,
                initial_answer=answer,
                contexts=documents
            )
            
            self.trace_info['evaluation_history'] = eval_history
            self.trace_info['editor_history'] = editor_history
            self.trace_info['final_answer'] = final_answer
            self.trace_info['total_time'] = time.time() - start_time
            
            return Message(content=json.dumps({
                'answer': final_answer,
                'trace_info': self.trace_info
            }))
            
        except Exception as e:
            self.trace_info['errors'].append(str(e))
            self.trace_info['total_time'] = time.time() - start_time
            return Message(content=json.dumps({
                'error': f"Workflow failed: {str(e)}",
                'trace_info': self.trace_info
            }))

    def safe_json_parse(self, content: str) -> Any:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_content": content}

    async def run_evaluation_loop(self, question: str, initial_answer: str, contexts: List[str]) -> tuple:
        current_answer = initial_answer
        max_attempts = 2
        attempts = 0
        eval_history = []
        editor_history = []
        
        while attempts < max_attempts:
            eval_payload = {
                "question": question,
                "answer": current_answer,
                "contexts": contexts
            }

            logging.info(f"[EvaluationAgent] Input (Attempt {attempts + 1}): {json.dumps(eval_payload)}")
            eval_resp = await self.send_message(
                Message(content=json.dumps(eval_payload)),
                self.eval_agent_id
            )
            logging.info(f"[EvaluationAgent] Output (Attempt {attempts + 1}): {eval_resp.content}")
            
            eval_result = self.safe_json_parse(eval_resp.content)
            eval_history.append({
                "input": eval_payload,
                "output": eval_result,
                "attempt": attempts + 1
            })
            
            score = float(eval_result.get("score", 0))
            if score >= 0.7:
                return current_answer, eval_history, editor_history
                
            logging.info(f"[EditorAgent] Input (Attempt {attempts + 1}): {json.dumps(eval_payload)}")
            editor_resp = await self.send_message(
                Message(content=json.dumps(eval_payload)),
                self.editor_agent_id
            )
            logging.info(f"[EditorAgent] Output (Attempt {attempts + 1}): {editor_resp.content}")
            
            edit_result = self.safe_json_parse(editor_resp.content)
            editor_history.append({
                "input": eval_payload,
                "output": edit_result,
                "attempt": attempts + 1
            })
            current_answer = edit_result.get("answer", current_answer)
            
            attempts += 1
        
        return current_answer, eval_history, editor_history
