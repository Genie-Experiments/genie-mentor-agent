import json
import os
import time

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from groq import Groq
from pydantic import ValidationError

from ..prompts.prompts import REFINEMENT_NEEDED_PROMPT
from ..protocols.message import Message
from ..protocols.planner_schema import QueryPlan, RefinerOutput
from ..protocols.schemas import LLMUsage
from ..utils.logging import get_logger, setup_logger
from ..utils.parsing import extract_json_with_regex
from ..utils.settings import settings, GROQ_API_KEY_PLANNER_REFINER
from ..utils.token_tracker import token_tracker

setup_logger()
logger = get_logger("planner_refiner")


class PlannerRefinerAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("planner_refiner_agent")
        self.client = Groq(api_key=GROQ_API_KEY_PLANNER_REFINER)
        self.model = settings.DEFAULT_MODEL

    @message_handler
    async def handle_plan_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        start_time = time.time()
        try:
            # Parse the incoming message content
            content = json.loads(message.content)
            plan = content.get(
                "plan", content
            )  # Handle both direct plan and wrapped plan

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
                error=None,
            )

            # Add token usage to the response
            response_dict = refiner_output.model_dump()
            if "llm_usage" in feedback:
                response_dict["llm_usage"] = feedback["llm_usage"]

            return Message(content=json.dumps(response_dict))

        except ValidationError as e:
            error_msg = f"Invalid QueryPlan format: {e}"
            logger.error(error_msg)
            return Message(
                content=json.dumps(
                    {
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "refinement_required": "no",
                        "feedback_summary": "Invalid plan format",
                        "feedback_reasoning": [str(e)],
                        "error": error_msg,
                    }
                )
            )
        except Exception as e:
            logger.error(f"Error processing plan: {str(e)}")
            return Message(
                content=json.dumps(
                    {
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                        "refinement_required": "no",
                        "feedback_summary": "Error processing plan",
                        "feedback_reasoning": [str(e)],
                        "error": str(e),
                    }
                )
            )

    async def get_plan_feedback(self, plan_json: str) -> dict:
        prompt = REFINEMENT_NEEDED_PROMPT.format(plan_json=plan_json)

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=self.model
        )

        # Track token usage
        token_usage = token_tracker.track_completion("planner_refiner_agent", response, self.model)

        try:
            # Parse the response to get feedback
            content = response.choices[0].message.content
            logger.info(f"[PlannerRefiner] Raw LLM Response Length: {len(content)} characters")
            logger.info(f"[PlannerRefiner] Raw LLM Response: {content}")
            logger.debug(f"Debug groq feedback: {content}")
            feedback = extract_json_with_regex(content)

            # Ensure feedback_reasoning is a list
            feedback_reasoning = feedback.get("feedback_reasoning", [])
            if isinstance(feedback_reasoning, str):
                feedback_reasoning = [feedback_reasoning]

            # Create LLMUsage object if token usage is available
            llm_usage_obj = None
            if token_usage:
                llm_usage_obj = LLMUsage(
                    model=token_usage.model,
                    input_tokens=token_usage.input_tokens,
                    output_tokens=token_usage.output_tokens,
                    total_tokens=token_usage.total_tokens
                )

            return {
                "refinement_required": feedback.get("refinement_required", "no"),
                "feedback_summary": feedback.get("feedback_summary", ""),
                "feedback_reasoning": feedback_reasoning,
                "llm_usage": llm_usage_obj.model_dump() if llm_usage_obj else None,
            }
        except Exception as e:
            logger.error(f"Failed to parse feedback: {e}")
            # If response is not JSON, try to parse yes/no from text
            content = response.choices[0].message.content.strip().lower()
            
            # Create LLMUsage object if token usage is available
            llm_usage_obj = None
            if token_usage:
                llm_usage_obj = LLMUsage(
                    model=token_usage.model,
                    input_tokens=token_usage.input_tokens,
                    output_tokens=token_usage.output_tokens,
                    total_tokens=token_usage.total_tokens
                )
            
            return {
                "refinement_required": "yes" if content.startswith("yes") else "no",
                "feedback_summary": "Basic feedback based on yes/no response",
                "feedback_reasoning": [content],
                "llm_usage": llm_usage_obj.model_dump() if llm_usage_obj else None,
            }
