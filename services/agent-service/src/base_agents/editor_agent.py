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
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

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
          
            content = response.choices[0].message.content
            try:
                result = _extract_json_with_regex(content)
                final_answer = result.get("edited_answer", "")
            except Exception as e:
                logging.warning(f"Failed to parse editor output as JSON: {e}")
                # If both parsing methods fail, use the raw content
                final_answer = content.strip()
                if final_answer.startswith('{') and final_answer.endswith('}'):
                    # Try to extract just the edited_answer value
                    try:
                        start = final_answer.find('"edited_answer": "') + 17
                        end = final_answer.rfind('"')
                        if start > 16 and end > start:
                            final_answer = final_answer[start:end]
                    except:
                        pass

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
