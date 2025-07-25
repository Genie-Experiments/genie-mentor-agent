import json
import time

from autogen_core import MessageContext, RoutedAgent, message_handler
from openai import OpenAI

# Make sure this prompt is defined
from ..prompts.prompts import ANSWER_CLEANING_PROMPT
from ..protocols.message import Message
from ..protocols.schemas import LLMUsage
from ..utils.logging import get_logger, setup_logger
from ..utils.settings import settings, create_light_llm_client
from ..utils.token_tracker import token_tracker

setup_logger()
logger = get_logger("answer_cleaner")


class AnswerCleanerAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("answer_cleaner_agent")
        self.client, self.model = create_light_llm_client("answer_cleaner")

    @message_handler
    async def handle_cleaning_request(self, message: Message, ctx: MessageContext) -> Message:
        start_time = time.time()
        original_content = message.content

        logger.info(f"[AnswerCleaner] Received content for cleaning: {original_content}")

        try:
            # Inject raw answer into prompt template
            prompt = ANSWER_CLEANING_PROMPT.format(raw_answer=original_content)

            logger.info(
                f"[AnswerCleaner] Generated prompt for LLM: {prompt}")

            # Call LLM
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model
            )

            logger.info(
                f"[AnswerCleaner] LLM response received: {response}")

            # Track token usage
            token_usage = token_tracker.track_completion(
                "answer_cleaner_agent", response, self.model)

            # Extract cleaned content
            content = response.choices[0].message.content
            logger.info(
                f"[AnswerCleaner] Raw LLM Response Length: {len(content)} characters")
            logger.info(
                f"[AnswerCleaner] Raw LLM Response: {content}")

            try:
                cleaned = {
                    "cleaned_answer": content.strip()
                }

                logger.info(
                    f"[AnswerCleaner] Extracting JSON from LLM response: {cleaned['cleaned_answer']}")

                if token_usage:
                    cleaned["llm_usage"] = LLMUsage(
                        model=token_usage.model,
                        input_tokens=token_usage.input_tokens,
                        output_tokens=token_usage.output_tokens,
                        total_tokens=token_usage.total_tokens
                    ).model_dump()

                cleaned["execution_time_ms"] = int(
                    (time.time() - start_time) * 1000)
                return Message(content=json.dumps(cleaned))

            except Exception as parse_err:
                logger.error(
                    f"[AnswerCleaner] Failed to parse LLM output: {parse_err}")
                fallback = {
                    "cleaned_answer": original_content,
                    "error": str(parse_err),
                    "execution_time_ms": int((time.time() - start_time) * 1000),
                }
                if token_usage:
                    fallback["llm_usage"] = LLMUsage(
                        model=token_usage.model,
                        input_tokens=token_usage.input_tokens,
                        output_tokens=token_usage.output_tokens,
                        total_tokens=token_usage.total_tokens
                    ).model_dump()
                return Message(content=json.dumps(fallback))

        except Exception as e:
            logger.error(f"[AnswerCleaner] Failed to clean answer: {e}")
            return Message(
                content=json.dumps({
                    "cleaned_answer": original_content,
                    "error": str(e),
                    "execution_time_ms": int((time.time() - start_time) * 1000),
                })
            )
