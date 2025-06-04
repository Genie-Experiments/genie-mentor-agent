import json
import os
import time
from typing import Optional
from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from groq import Groq
from ..prompts.prompts import PLANNER_PROMPT
from ..protocols.planner_schema import QueryPlan
from ..protocols.message import Message
import logging
from ..utils.parsing import _extract_json_with_regex

class PlannerAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__('planner_agent')
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.max_retries = 3

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        start_time = time.time()
        try:
            # Handle both string and JSON inputs
            try:
                content = json.loads(message.content)
                if isinstance(content, dict) and 'feedback' in content:
                    return await self.process_query(content['query'], content['feedback'])
            except json.JSONDecodeError:
                # If not JSON, treat as direct query
                pass
            
            # If we get here, either it wasn't JSON or didn't have feedback
            return await self.process_query(message.content)
            
        except Exception as e:
            logging.error(f"Error in handle_user_message: {str(e)}")
            return Message(content=json.dumps({
                'error': str(e),
                'execution_time_ms': int((time.time() - start_time) * 1000)
            }))

    async def process_query(self, query: str, feedback: Optional[dict] = None) -> Message:
        start_time = time.time()
        retry_count = 0
        current_plan = None

        while retry_count < self.max_retries:
            try:
                # Prepare prompt with feedback if available
                feedback_str = "No feedback available"
                if feedback:
                    feedback_str = json.dumps({
                        "refinement_required": feedback.get("refinement_required", "no"),
                        "feedback_summary": feedback.get("feedback_summary", ""),
                        "feedback_reasoning": feedback.get("feedback_reasoning", []),
                        "current_plan": current_plan if current_plan else "No previous plan"
                    }, indent=2)
                    logging.info(f"Processing query with feedback: {feedback_str}")

                prompt = PLANNER_PROMPT.format(
                    user_query=query,
                    feedback=feedback_str
                )

                # Generate plan using Groq
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model
                )
                
                content = response.choices[0].message.content
                logging.info(f"Raw planner response: {content}")
                
                # Extract and validate the plan
                plan_data = _extract_json_with_regex(content)
                current_plan = plan_data
                
                # Validate against QueryPlan schema
                QueryPlan.model_validate(current_plan)
                
                execution_time = int((time.time() - start_time) * 1000)

                # Return the plan
                return Message(content=json.dumps({
                    "plan": current_plan,
                    "execution_time_ms": execution_time,
                    "retry_count": retry_count
                }))

            except Exception as e:
                logging.error(f"Error in process_query: {str(e)}")
                if retry_count >= self.max_retries - 1:
                    raise ValueError(f"Failed to generate valid plan after {retry_count + 1} attempts: {str(e)}")
                retry_count += 1
                continue

        # If we've exhausted retries, return the last plan
        return Message(content=json.dumps({
            "plan": current_plan,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "retry_count": retry_count,
            "warning": "Max retries reached"
        }))