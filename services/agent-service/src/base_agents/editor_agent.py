import json
import os
from autogen_core import RoutedAgent, MessageContext, message_handler
from ..prompts.editor_agent_prompt import EDITOR_PROMPT
from ..protocols.message import Message
import logging
from ..utils.parsing import _extract_json_with_regex
from groq import Groq


class EditorAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("editor_agent")
        self.client = Groq(api_key=os.getenv("WEBRAG_GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile" 

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
           
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model
            )
          
            content = response.choices[0].message.content
            try:
                result = _extract_json_with_regex(content)
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
