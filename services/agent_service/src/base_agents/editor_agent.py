import json
import time

from autogen_core import MessageContext, RoutedAgent, message_handler
from openai import OpenAI

from ..prompts.editor_agent_prompt import EDITOR_PROMPT
from ..protocols.message import Message
from ..protocols.schemas import EditorAgentInput, EditorAgentOutput, LLMUsage
from ..utils.logging import get_logger, setup_logger
from ..utils.parsing import extract_json_with_regex
from ..utils.settings import settings, create_light_llm_client
from ..utils.token_tracker import token_tracker

setup_logger()
logger = get_logger("EditorAgent")


class EditorAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("editor_agent")
        self.client, self.model = create_light_llm_client("editor")

    @message_handler
    async def fix_answer(self, message: Message, ctx: MessageContext) -> Message:
        try:

            payload = EditorAgentInput.model_validate_json(message.content)
            prompt = EDITOR_PROMPT.format(
                question=payload.question,
                previous_answer=payload.previous_answer,
                score=payload.score,
                reasoning=payload.reasoning,
                contexts=payload.contexts
            )

            logger.info(f"[EditorAgent] Formulated Prompt : {prompt}")
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], model=self.model
            )

            # Track token usage
            token_usage = token_tracker.track_completion("editor_agent", response, self.model)

            content = response.choices[0].message.content

            result = extract_json_with_regex(content)
            final_answer = result.get("edited_answer")
            logger.info(f"[EditorAgent] Final Answer : {final_answer}")
            
            # Create LLMUsage object if token usage is available
            llm_usage_obj = None
            if token_usage:
                llm_usage_obj = LLMUsage(
                    model=token_usage.model,
                    input_tokens=token_usage.input_tokens,
                    output_tokens=token_usage.output_tokens,
                    total_tokens=token_usage.total_tokens
                )


            return Message(content=EditorAgentOutput(
                answer=final_answer,
                llm_usage=llm_usage_obj,
                error=None).model_dump_json())


        except Exception as e:
            logger.error(f"EditorAgent Encountered Error : {e}")
            # Use the previous_answer from the payload if available, otherwise use error message
            fallback_answer = getattr(payload, 'previous_answer', "Error Occurred in Editor Agent") if 'payload' in locals() else "Error Occurred in Editor Agent"
            return Message(content=json.dumps({
                "answer": fallback_answer,
                "error": str(e)
            }))
