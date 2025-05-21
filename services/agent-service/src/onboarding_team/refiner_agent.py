# Standard library imports
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Third-party imports
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Local application imports
from .message import Message

persist_path = os.getenv('CHROMA_DB_PATH')

class RefinerAgent(RoutedAgent):
    def __init__(self, query_agent_id: AgentId) -> None:
        super().__init__('planner_agent')
        self.query_agent_id = query_agent_id
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-4o',
            api_key=os.getenv('OPENAI_API_KEY')
        )

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:

        # add refiner agent logic

        return await self.send_message(message, self.query_agent_id)