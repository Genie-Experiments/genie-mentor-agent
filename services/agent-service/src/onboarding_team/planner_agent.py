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
            # Get original plan
            plan = await self.process_query(message.content)
            plan_dict = json.loads(plan.content)
            print("\n[PLANNER AGENT] Original Plan:")
            print(json.dumps(plan_dict, indent=2))

            # Get refiner output
            query_result = await self.send_message(plan, self.refiner_agent_id)
            print(f'\n[REFINER AGENT] Refiner Metadata:')
            try:
                qdict = json.loads(query_result.content)
                refiner_metadata = qdict.get('refiner_metadata', {})
                print(json.dumps(refiner_metadata, indent=2))
            except json.JSONDecodeError:
                print("Failed to parse refiner metadata")

            try:                                                                   
                qdict = json.loads(query_result.content)                           
                # Get query agent results
                answer_txt = qdict["answer"]["aggregated_results"]                 
                contexts = qdict.get("sources_used", [])        
                                                  
                print("\n[QUERY AGENT] Results:")
                print(f"Answer: {answer_txt}")
                print(f"Confidence Score: {qdict['answer'].get('confidence_score', 'N/A')}")
                                                                               
                attempts = []               
                prev_score = None
                corrections = 0

                while True:
                    print("\n[EVALUATION AGENT] Running evaluation")  
                    eval_resp = await self.send_message(
                        Message(content=json.dumps({
                            "question": message.content,                                                  
                            "answer": answer_txt,                                        
                            "contexts": contexts                                           
                        })),
                        self.evaluation_agent_id,
                    )
                    score = float(json.loads(eval_resp.content)["score"])

                    delta = None if prev_score is None else round(score - prev_score, 4)
                    attempts.append({
                        "answer": answer_txt,
                        "score": round(score, 4),
                        "delta": delta
                    })
                    prev_score = score

                    if score >= 1.0 or corrections == 1:
                        break
                    
                    print("\n[EDITOR AGENT] Running editor") 
                    editor_resp = await self.send_message(
                        Message(content=json.dumps({
                            "question": message.content,
                            "answer": answer_txt,
                            "contexts": contexts
                        })),
                        self.editor_agent_id,
                    )
                    edited_answer = json.loads(editor_resp.content)["answer"]
                    print(f"Edited Answer: {edited_answer}")
                    answer_txt = edited_answer
                    corrections += 1

                final_answer = answer_txt
                final_score = prev_score                                  
                                                                               
                print("\n[EVALUATION AGENT] Final Results:")
                print(f"Final Score: {final_score}")
                print(f"Corrections Made: {corrections}")
                print("Attempts:", json.dumps(attempts, indent=2))

                # Structure the final output
                plan_dict['refiner_metadata'] = refiner_metadata
                plan_dict['query_results'] = {
                    'answer': answer_txt,
                    'confidence_score': qdict['answer'].get('confidence_score', 0)
                }
                plan_dict['evaluation_results'] = {
                    'final_answer': final_answer,
                    'evaluation_score': final_score,
                    'corrections_made': corrections,
                    'attempts': attempts
                }

                print("\n[FINAL COMBINED OUTPUT]")
                print(json.dumps(plan_dict, indent=2))

            except json.JSONDecodeError as e:
                print(f'[WARNING] Failed to parse query result as JSON: {e}')
                plan_dict['query_results'] = {
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