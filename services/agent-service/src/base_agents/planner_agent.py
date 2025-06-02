import json
import os
from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from ..prompts.prompts import PLANNER_PROMPT
from ..protocols.planner_schema import QueryPlan
from ..protocols.message import Message

class PlannerAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__('planner_agent')
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-4o',
            api_key=os.getenv('OPENAI_API_KEY')
        )

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        try:
            return await self.process_query(message.content)
        except Exception as e:
            return Message(content=json.dumps({'error': str(e)}))


    async def process_query(self, query: str) -> Message:
        prompt = PLANNER_PROMPT.format(user_query=query)
        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source='user')],
            json_output=QueryPlan
        )
        return Message(content=response.content)