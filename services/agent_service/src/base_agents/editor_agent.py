import json
import os

from autogen_core import MessageContext, RoutedAgent, message_handler
from groq import Groq

from ..prompts.editor_agent_prompt import EDITOR_PROMPT
from ..protocols.message import Message
from ..protocols.schemas import EditorAgentInput, EditorAgentOutput, LLMUsage
from ..utils.logging import get_logger, setup_logger
from ..utils.parsing import extract_json_with_brace_counting
from ..utils.settings import settings
from ..utils.token_tracker import token_tracker

setup_logger()
logger = get_logger("EditorAgent")


class EditorAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("editor_agent")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.WEBRAG_LLM_DEFAULT_MODEL

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

            result = extract_json_with_brace_counting(content)
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
            return Message(content=json.dumps({
                "answer": payload.get("previous_answer","Error Occured in Editor Agent"),
                "error": str(e)
            }))
