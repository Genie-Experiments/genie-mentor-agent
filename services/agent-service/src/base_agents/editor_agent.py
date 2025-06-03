import json
import os
from autogen_core import RoutedAgent, MessageContext, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from ..prompts.prompts import EDITOR_PROMPT
from ..protocols.message import Message
import logging
from ..utils.parsing import _extract_json_with_regex


class EditorAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("editor_agent")
        self.llm = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )

    @message_handler
    async def fix_answer(self, message: Message, ctx: MessageContext) -> Message:
        try:
            payload = json.loads(message.content)

            prompt = EDITOR_PROMPT.format(
                question=payload.get("question", ""),
                previous_answer=payload.get("previous_answer", ""),
                score=payload.get("score", 0),
                reasoning=payload.get("reasoning", ""),
                contexts="\n".join(payload.get("contexts", []))
            )

            resp = await self.llm.create(
                messages=[UserMessage(content=prompt, source="eval_agent")]
            )
           
            try:
                result = _extract_json_with_regex(resp.content)
                final_answer = result.get("edited_answer", "")
            except Exception as e:
                logging.warning("Failed to parse editor output as JSON.")
                return Message(content=json.dumps({
                    "answer": "",
                    "error": f"Invalid JSON from editor: {str(e)}"
                }))

            return Message(content=json.dumps({
                "answer": final_answer,
                "error": None
            }))

        except Exception as e:
            logging.exception("EditorAgent failed to fix the answer.")
            return Message(content=json.dumps({
                "answer": "",
                "error": str(e)
            }))
