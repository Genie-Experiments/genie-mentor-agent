import json
import os
from autogen_core import RoutedAgent, MessageContext, message_handler
from ..prompts.editor_agent_prompt import EDITOR_PROMPT
from ..protocols.message import Message
from ..utils.parsing import extract_json_with_brace_counting
from groq import Groq
from ..utils.logging import setup_logger, get_logger
from ..utils.settings import settings

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
            payload = json.loads(message.content)
         
            prompt = EDITOR_PROMPT.format(
                question=payload.get("question"),
                previous_answer=payload.get("previous_answer"),
                score=payload.get("score", 0),
                reasoning=payload.get("reasoning", ""),
                contexts=payload.get("contexts")
            )
            logger.info(f"[EditorAgent] Formulated Prompt : {prompt}")
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model
            )
          
            content = response.choices[0].message.content
        
            result = extract_json_with_brace_counting(content)
            final_answer = result.get("edited_answer", "")
            logger.info(f"[EditorAgent] Final Answer : {final_answer}")
            return Message(content=json.dumps({
                "answer": final_answer,
                "error": None
            }))

        except Exception as e:
            logger.error(f"EditorAgent Encountered Error : {e}")
            return Message(content=json.dumps({
                "answer": payload.get("previous_answer", ""),
                "error": str(e)
            }))
