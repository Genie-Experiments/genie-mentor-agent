import json
import os
import time
from typing import Optional

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from groq import Groq

from ..prompts.prompts import PLANNER_PROMPT, IS_GREETING_PROMPT_CONTEXT
from ..protocols.message import Message
from ..protocols.planner_schema import QueryPlan
from ..protocols.schemas import LLMUsage
from ..utils.logging import get_logger, setup_logger
from ..utils.parsing import extract_json_with_regex
from ..utils.settings import settings, GROQ_API_KEY_PLANNER
from ..utils.token_tracker import token_tracker

setup_logger()
logger = get_logger("PlannerAgent")


class PlannerAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("planner_agent")
        self.client = Groq(api_key=GROQ_API_KEY_PLANNER)
        self.model = settings.DEFAULT_MODEL
        self.max_retries = 3

    @message_handler
    async def handle_user_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        start_time = time.time()
        try:
            # Handle both string and JSON inputs
            try:
                content = json.loads(message.content)
                # TODO: Update feedback key here
                if isinstance(content, dict) and "feedback" in content:
                    return await self.process_query(
                        content["query"], content["feedback"]
                    )
            except json.JSONDecodeError:
                # If not JSON, treat as direct query
                pass

            # If we get here, either it wasn't JSON or didn't have feedback
            return await self.process_query(message.content)

        except Exception as e:
            logger.error(f"Error in handle_user_message: {str(e)}")
            return Message(
                content=json.dumps(
                    {
                        "error": str(e),
                        "execution_time_ms": int((time.time() - start_time) * 1000),
                    }
                )
            )

    async def is_greeting(self, query: str) -> tuple[bool, str]:
        """Classify if the query is a greeting or chit-chat using the LLM, and generate a response if so."""
        prompt = IS_GREETING_PROMPT_CONTEXT.replace("{{query}}", query)
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=self.model
        )
        content = response.choices[0].message.content.strip()
        if content.lower() == "no":
            return False, ""
        return True, content

    async def process_query(
        self, query: str, feedback: Optional[dict] = None
    ) -> Message:
        start_time = time.time()
        retry_count = 0
        current_plan = None
        token_usage = None

        # Greeting detection step
        is_greet, greet_response = await self.is_greeting(query)
        if is_greet:
            return Message(content=json.dumps({
                "plan": {
                    "is_greeting": True,
                    "greeting_response": greet_response,
                    "user_query": query,
                    "query_intent": "greeting",
                    "data_sources": [],
                    "query_components": [],
                    "execution_order": {
                        "nodes": [],
                        "edges": [],
                        "aggregation": "single_source"
                    },
                    "think": {
                        "query_analysis": "Greeting detected.",
                        "sub_query_reasoning": "",
                        "source_selection": "",
                        "execution_strategy": ""
                    }
                },
                "execution_time_ms": 0,
                "llm_usage": None,
            }))

        while retry_count < self.max_retries:
            try:
                # Prepare prompt with feedback if available
                feedback_str = "No feedback available"
                if feedback:
                    feedback_str = json.dumps(
                        {
                            "refinement_required": feedback.get(
                                "refinement_required", "no"
                            ),
                            "feedback_summary": feedback.get("feedback_summary", ""),
                            "feedback_reasoning": feedback.get(
                                "feedback_reasoning", []
                            ),
                            "current_plan": (
                                current_plan if current_plan else "No previous plan"
                            ),
                        },
                        indent=2,
                    )
                    logger.info(f"Processing query with feedback: {feedback_str}")

                prompt = PLANNER_PROMPT.format(user_query=query, feedback=feedback_str)

                # Generate plan using Groq
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}], model=self.model
                )

                # Track token usage
                token_usage = token_tracker.track_completion("planner_agent", response, self.model)

                content = response.choices[0].message.content
                logger.info(f"Raw planner response: {content}")

                # Extract and validate the plan
                plan_data = extract_json_with_regex(content)
                current_plan = plan_data

                # Validate against QueryPlan schema
                QueryPlan.model_validate(current_plan)

                execution_time = int((time.time() - start_time) * 1000)

                # Create LLMUsage object if token usage is available
                llm_usage_obj = None
                if token_usage:
                    llm_usage_obj = LLMUsage(
                        model=token_usage.model,
                        input_tokens=token_usage.input_tokens,
                        output_tokens=token_usage.output_tokens,
                        total_tokens=token_usage.total_tokens
                    )

                # Return the plan with token usage
                return Message(
                    content=json.dumps(
                        {
                            "plan": current_plan,
                            "execution_time_ms": execution_time,
                            "retry_count": retry_count,
                            "llm_usage": llm_usage_obj.model_dump() if llm_usage_obj else None,
                        }
                    )
                )

            except Exception as e:
                logger.error(f"Error in process_query: {str(e)}")
                if retry_count >= self.max_retries - 1:
                    raise ValueError(
                        f"Failed to generate valid plan after {retry_count + 1} attempts: {str(e)}"
                    )
                retry_count += 1
                continue

        # If we've exhausted retries, return the last plan
        return Message(
            content=json.dumps(
                {
                    "plan": current_plan,
                    "execution_time_ms": int((time.time() - start_time) * 1000),
                    "retry_count": retry_count,
                    "warning": "Max retries reached",
                    "llm_usage": llm_usage_obj.model_dump() if llm_usage_obj else None,
                }
            )
        )
