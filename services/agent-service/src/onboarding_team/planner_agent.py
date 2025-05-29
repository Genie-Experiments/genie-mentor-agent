import json
import os
from typing import Any, Dict, List, Optional

from autogen_core import AgentId, MessageContext, RoutedAgent,  message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .prompts import PLANNER_PROMPT
from ..schemas.planner_schema import QueryPlan
from .message import Message

persist_path = os.getenv('CHROMA_DB_PATH')

class PlannerAgent(RoutedAgent):
    def __init__(self, refiner_agent_id: AgentId,editor_agent_id:AgentId,evaluation_agent_id:AgentId) -> None:
        super().__init__('planner_agent')
        self.refiner_agent_id = refiner_agent_id
        self.editor_agent_id = editor_agent_id
        self.evaluation_agent_id=evaluation_agent_id

        self.model_client = OpenAIChatCompletionClient(
            model='gpt-4o',
            api_key=os.getenv('OPENAI_API_KEY')
        )

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        try:
            plan = await self.process_query(message.content)
            plan_dict = json.loads(plan.content)

            query_result = await self.send_message(plan, self.refiner_agent_id)
            print(f'[DEBUG] Query result content: {query_result.content}')

            try:                                                                   
                qdict = json.loads(query_result.content)                           
                # pull answer + contexts (contexts list could come from QueryAgent)
                answer_txt = qdict["answer"]["aggregated_results"]                 
                contexts   = qdict.get("sources_used", [])        
                                                  
                print("[DEBUG] MAKING EVALUATION PAYLOAD")                                             
                eval_payload = {                                                   
                    "question": message.content,                                                  
                    "answer":   answer_txt,                                        
                    "contexts": contexts                                           
                }                                                                  
                                                                               
                attempts = []               
                prev_score = None
                corrections = 0

                while True:
                    print("[DEBUG] RUNNING EVALUATION AGENT")  
                    eval_resp = await self.send_message(
                        Message(content=json.dumps(eval_payload)),
                        self.evaluation_agent_id,
                    )
                    score = float(json.loads(eval_resp.content)["score"])

                    delta = None if prev_score is None else round(score - prev_score, 4)
                    attempts.append({
                        "answer": eval_payload["answer"],
                        "score":  round(score, 4),
                        "delta":  delta
                    })
                    prev_score = score

                    if score >= 0.7 or corrections == 2:
                        break
                    

                    print("[DEBUG] RUNNING EDITOR AGENT") 
                    editor_resp = await self.send_message(
                        Message(content=json.dumps(eval_payload)),
                        self.editor_agent_id,
                    )
                    eval_payload["answer"] = json.loads(editor_resp.content)["answer"]
                    corrections += 1
                final_answer = eval_payload["answer"]
                final_score  = prev_score                                  
                                                                               
                qdict["attempts"]         = attempts
                qdict["final_answer"]     = final_answer
                qdict["evaluation_score"] = final_score
                qdict["corrections_made"] = corrections
                qdict["answer"]["aggregated_results"] = final_answer

                       
                                                                               
                query_result = Message(content=json.dumps(qdict))                  
            except Exception as ex:                                                
                print("[WARNING] Eval loop failed:", ex)                           

            try:
                query_dict = json.loads(query_result.content)
                if 'answer' in query_dict:
                    answer = query_dict['answer']
                    if isinstance(answer, dict):
                        plan_dict['execution_results'] = {
                            'answer': answer.get('aggregated_results', ''),
                            'confidence_score': answer.get('confidence_score', 0)
                        }
                    else:
                        plan_dict['execution_results'] = {
                            'answer': str(answer),
                            'confidence_score': 0
                        }
                else:
                    plan_dict['execution_results'] = {
                        'answer': str(query_dict),
                        'confidence_score': 0
                    }

                refiner_metadata = query_dict.get('refiner_metadata', {})
                plan_dict['refiner_metadata'] = {
                    'refined_plan':  refiner_metadata.get('refined_plan', '{}'),
                    'feedback':      refiner_metadata.get('feedback', ''),
                    'changes_made':  refiner_metadata.get('changes_made', [])
                }
                # add evaluation info if present                                
                if "evaluation_score" in query_dict:                             
                    plan_dict['evaluation_score'] = query_dict['evaluation_score']
                    plan_dict['corrections_made'] = query_dict['corrections_made']
            except json.JSONDecodeError:
                print(f'[WARNING] Failed to parse query result as JSON: {query_result.content}')
                plan_dict['execution_results'] = {
                    'answer': query_result.content,
                    'confidence_score': 0
                }
                plan_dict['refiner_metadata'] = {}

            return Message(content=json.dumps(plan_dict))

        except Exception as e:
            print(f'[ERROR] Error in handle_user_message: {str(e)}')
            return Message(content=json.dumps({
                'error': str(e),
                'plan': json.dumps(plan_dict) if 'plan_dict' in locals() else None,
                'query_result': query_result.content if 'query_result' in locals() else None
            }))


    async def process_query(self, query: str) -> Message:

        prompt = PLANNER_PROMPT.format(
            user_query=query
        )

        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source='user')],
            json_output=QueryPlan
        )
        print("lllllllllllllllllllllllllllllllllll")
        print(response)
        return Message(content=response.content)