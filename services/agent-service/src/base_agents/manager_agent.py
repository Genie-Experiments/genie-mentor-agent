import json
import logging
from typing import Any, List, Dict
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
        
        self.conversation_history[session_id].append({
            "question": question,
            "answer": answer
        })
        
        # Keep only last 5 conversations to manage memory
        if len(self.conversation_history[session_id]) > 5:
            self.conversation_history[session_id] = self.conversation_history[session_id][-5:]

    def _should_skip_evaluation(self, plan_data: Dict[str, Any]) -> bool:
        """
        Check if evaluation and editing should be skipped based on selected sources.
        Returns True if GitHub or Notion are selected as sources.
        """
        try:
            # Get the plan from plan_data
            plan = plan_data.get('plan', {})
            
            # Check for sources in various possible locations within the plan
            sources_to_check = []
            
            # Common possible locations for sources in the plan
            if isinstance(plan, dict):
                # Check if sources are directly in the plan
                if 'sources' in plan:
                    sources_to_check.extend(plan['sources'])
                
                # Check if there are selected_sources
                if 'selected_sources' in plan:
                    sources_to_check.extend(plan['selected_sources'])
                
                # Check for data_sources
                if 'data_sources' in plan:
                    sources_to_check.extend(plan['data_sources'])
                
                # Check if plan has steps with sources
                if 'steps' in plan:
                    for step in plan['steps']:
                        if isinstance(step, dict) and 'sources' in step:
                            sources_to_check.extend(step['sources'])
                        if isinstance(step, dict) and 'source' in step:
                            sources_to_check.append(step['source'])
            
            # Check if plan itself is a list of sources
            elif isinstance(plan, list):
                sources_to_check.extend(plan)
            
            # Convert all sources to lowercase strings for comparison
            sources_lower = [str(source).lower() for source in sources_to_check]
            
            # Check if github or notion are in the sources
            skip_sources = ['github', 'notion']
            for skip_source in skip_sources:
                for source in sources_lower:
                    if skip_source in source:
                        logging.info(f"Found {skip_source} in sources. Skipping evaluation and editing.")
                        return True
            
            return False
            
        except Exception as e:
            logging.warning(f"Error checking sources for evaluation skip: {e}")
            return False

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        start_time = time.time()
        session_id = ctx.session_id if hasattr(ctx, 'session_id') else 'default'
        
        # Get conversation context
        context = self._get_context(session_id)
        user_query = message.content
        
        # If there's context, prepend it to the query
        if context:
            user_query = f"{context}\nCurrent question: {user_query}"
        
        self.trace_info = {
            'start_time': start_time,
            'user_query': user_query,
            'planner_agent': None,
            'planner_refiner_agent': None,
            'executor_agent': None,
            'evaluation_agent': [],
            'editor_agent': [],
            'errors': [],
            'total_time': None,
            'evaluation_skipped': False,
            'skip_reason': None
        }
        
        try:
            # Initial plan generation
            logging.info(f"[PlannerAgent] Input: {user_query}")
            plan = await self.send_message(Message(content=user_query), self.planner_agent_id)
            logging.info(f"[PlannerAgent] Output: {plan.content}")
            plan_data = self.safe_json_parse(plan.content)
            self.trace_info['planner_agent'] = plan_data
            
            # Feedback loop between planner and refiner
            max_retries = 3
            retry_count = 0
            current_plan = plan_data.get('plan')
            
            while retry_count < max_retries:
                # Get feedback from refiner
                logging.info(f"[PlannerRefinerAgent] Input: {current_plan}")
                refined = await self.send_message(Message(content=json.dumps(current_plan)), self.planner_refiner_agent_id)
                logging.info(f"[PlannerRefinerAgent] Output: {refined.content}")
                refiner_data = self.safe_json_parse(refined.content)
                self.trace_info['planner_refiner_agent'] = refiner_data
                
                # If no refinement needed, break the loop
                if refiner_data.get('refinement_required') == 'no':
                    break
                
                # Get refined plan from planner with feedback
                logging.info(f"[PlannerAgent] Refining with feedback: {refiner_data}")
                feedback_payload = {
                    'query': user_query,
                    'feedback': {
                        'refinement_required': refiner_data.get('refinement_required', 'no'),
                        'feedback_summary': refiner_data.get('feedback_summary', ''),
                        'feedback_reasoning': refiner_data.get('feedback_reasoning', []),
                        'current_plan': current_plan
                    }
                }
                
                # Send feedback to planner and get refined plan
                plan = await self.send_message(
                    Message(content=json.dumps(feedback_payload)), 
                    self.planner_agent_id
                )
                logging.info(f"[PlannerAgent] Refined output: {plan.content}")
                
                # Parse the new plan
                plan_data = self.safe_json_parse(plan.content)
                if 'error' in plan_data:
                    logging.error(f"Error in planner refinement: {plan_data['error']}")
                    break
                    
                current_plan = plan_data.get('plan')
                if not current_plan:
                    logging.error("No plan returned from planner after refinement")
                    break
                    
                retry_count += 1
                logging.info(f"Refinement attempt {retry_count}/{max_retries}")
                
                logging.info(f"Refined plan: {json.dumps(current_plan, indent=2)}")
            
            logging.info(f"[ExecutorAgent] Input: {current_plan}")
            query_result = await self.send_message(Message(content=json.dumps(current_plan)), self.executor_agent_id)
            logging.info(f"[ExecutorAgent] Output: {query_result.content}")
            self.trace_info['executor_agent'] = self.safe_json_parse(query_result.content)
            
            q_output = self.trace_info['executor_agent']
            if q_output.get('error') is not None:
                raise ValueError(f"Query execution failed: {q_output['error']}")
                
            answer = q_output.get("combined_answer_of_sources", "")
            documents = q_output.get("top_documents", [])
            
            # Check if we should skip evaluation and editing
            should_skip = self._should_skip_evaluation(plan_data)
            
            if should_skip:
                # Skip evaluation and editing, use the answer directly
                final_answer = answer
                eval_history = []
                editor_agent = []
                self.trace_info['evaluation_skipped'] = True
                self.trace_info['skip_reason'] = "GitHub or Notion source detected"
                logging.info("Skipping evaluation and editing due to GitHub/Notion source selection")
            else:
                # Run normal evaluation loop
                final_answer, eval_history, editor_agent = await self.run_evaluation_loop(
                    question=user_query,
                    initial_answer=answer,
                    contexts=documents
                )
            
            self.trace_info['evaluation_agent'] = eval_history
            self.trace_info['editor_agent'] = editor_agent
            self.trace_info['final_answer'] = final_answer
            self.trace_info['total_time'] = time.time() - start_time
            
            # Update conversation history
            self._update_history(session_id, message.content, final_answer)
            
            return Message(content=json.dumps({
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
        editor_agent = []
       
        while attempts < max_attempts:
            eval_payload = {
                "question": question,
                "answer": current_answer,
                "contexts": contexts
            }

            logging.info(f"[EvaluationAgent] Input (Attempt {attempts + 1}): {json.dumps(eval_payload)}")
            eval_resp = await self.send_message(Message(content=json.dumps(eval_payload)), self.eval_agent_id)
            logging.info(f"[EvaluationAgent] Output (Attempt {attempts + 1}): {eval_resp.content}")

            eval_result = self.safe_json_parse(eval_resp.content)
            score = float(eval_result.get("score", 0))
            reasoning = eval_result.get("reasoning", "")
            error = eval_result.get("error", None)

            eval_history.append({
                "evaluation_history": {
                    "score": score,
                    "reasoning": reasoning,
                    "error": error
                },
                "attempt": attempts + 1
            })

            if error is None and score >= 2.0 or attempts == max_attempts - 1:
                break

            editor_payload = {
                "question": question,
                "previous_answer": current_answer,
                "contexts": contexts,
                "score": score,
                "reasoning": reasoning
            }

            logging.info(f"[EditorAgent] Input (Attempt {attempts + 1}): {json.dumps(editor_payload)}")
            editor_resp = await self.send_message(Message(content=json.dumps(editor_payload)), self.editor_agent_id)
            logging.info(f"[EditorAgent] Output (Attempt {attempts + 1}): {editor_resp.content}")

            editor_result = self.safe_json_parse(editor_resp.content)
            new_answer = editor_result.get("answer", current_answer)
            editor_error = editor_result.get("error", None)

            editor_agent.append({
                "editor_history": {
                    "answer": new_answer,
                    "error": editor_error
                },
                "attempt": attempts + 1
            })

            current_answer = new_answer
            attempts += 1

        return current_answer, eval_history, editor_agent