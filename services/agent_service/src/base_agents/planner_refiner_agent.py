import json
import os
import time
from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from groq import Groq
from pydantic import ValidationError
from ..protocols.planner_schema import QueryPlan, RefinerOutput
from ..protocols.message import Message
from ..prompts.prompts import REFINEMENT_NEEDED_PROMPT
from ..utils.parsing import _extract_json_with_regex
from ..utils.logging import setup_logger, get_logger
from ..utils.settings import settings

setup_logger()
logger = get_logger("my_module")

class PlannerRefinerAgent(RoutedAgent):
    def __init__(self) -> None:  
        super().__init__('planner_refiner_agent')
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.DEFAULT_MODEL

    @message_handler
    async def handle_plan_message(self, message: Message, ctx: MessageContext) -> Message:
        start_time = time.time()
        try:
            # Parse the incoming message content
            content = json.loads(message.content)
            plan = content.get('plan', content)  # Handle both direct plan and wrapped plan
            
            # Validate the plan
            parsed_plan = QueryPlan.model_validate(plan)
            
            # Get feedback on the plan
            feedback = await self.get_plan_feedback(json.dumps(plan))
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Ensure feedback_reasoning is a list
            feedback_reasoning = feedback.get("feedback_reasoning", [])
            if isinstance(feedback_reasoning, str):
                feedback_reasoning = [feedback_reasoning]
            
            # Create refiner output
            refiner_output = RefinerOutput(
                execution_time_ms=execution_time_ms,
                refinement_required=feedback["refinement_required"],
                feedback_summary=feedback["feedback_summary"],
                feedback_reasoning=feedback_reasoning,
                error=None
            )
            
            return Message(content=refiner_output.model_dump_json())
            
        except ValidationError as e:
            error_msg = f"Invalid QueryPlan format: {e}"
            logger.error(error_msg)
            return Message(content=json.dumps({
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "refinement_required": "no",
                "feedback_summary": "Invalid plan format",
                "feedback_reasoning": [str(e)],
                "error": error_msg
            }))
        except Exception as e:
            logger.error(f"Error processing plan: {str(e)}")
            return Message(content=json.dumps({
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "refinement_required": "no",
                "feedback_summary": "Error processing plan",
                "feedback_reasoning": [str(e)],
                "error": str(e)
            }))

    async def get_plan_feedback(self, plan_json: str) -> dict:
        prompt = REFINEMENT_NEEDED_PROMPT.format(plan_json=plan_json)
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model
        )
        
        try:
            # Parse the response to get feedback
            content = response.choices[0].message.content
            logger.debug(f"Debug groq feedback: {content}")
            feedback = _extract_json_with_regex(content)
            
            # Ensure feedback_reasoning is a list
            feedback_reasoning = feedback.get("feedback_reasoning", [])
            if isinstance(feedback_reasoning, str):
                feedback_reasoning = [feedback_reasoning]
            
            return {
                "refinement_required": feedback.get("refinement_required", "no"),
                "feedback_summary": feedback.get("feedback_summary", ""),
                "feedback_reasoning": feedback_reasoning
            }
        except Exception as e:
            logger.error(f"Failed to parse feedback: {e}")
            # If response is not JSON, try to parse yes/no from text
            content = response.choices[0].message.content.strip().lower()
            return {
                "refinement_required": "yes" if content.startswith("yes") else "no",
                "feedback_summary": "Basic feedback based on yes/no response",
                "feedback_reasoning": [content]
            }