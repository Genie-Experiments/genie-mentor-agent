import json, os
from autogen_core import RoutedAgent, MessageContext, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from ..prompts.prompts import EDITOR_PROMPT
from ..protocols.message import Message
class EditorAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("editor_agent")
        self.llm = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )

    @message_handler
    async def fix_answer(                      
        self,
        message: Message,                       
        ctx: MessageContext
    ) -> Message:
        payload = json.loads(message.content)
        prompt = EDITOR_PROMPT.format(**payload)

        resp = await self.llm.create(
            messages=[UserMessage(content=prompt, source="eval_agent")]
        )
        return Message(content=json.dumps({"answer": resp.content.strip()}))
