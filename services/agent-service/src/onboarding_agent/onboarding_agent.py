from ..rag.rag import query_knowledgebase
from autogen_core import (
    AgentId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
)
from autogen_core.tools import Tool
from dataclasses import dataclass
from ..rag.rag import query_knowledgebase
from typing import List

@dataclass
class Message:
    content: str

class OnBoardingAgent(RoutedAgent):
    def __init__(self, tool_schema: List[Tool]) -> None:
        super().__init__("onboarding_agent")
        self._tools = tool_schema

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        return await self.onboarding_agent(message.content)

    async def onboarding_agent(self, query: str) -> Message:
        response = query_knowledgebase(query)
        return Message(content=response["answer"])

# Global runtime and agent registration
runtime = SingleThreadedAgentRuntime()
onboarding_agent_id = AgentId("onboarding_agent", "default")


# Flag to ensure the agent is only initialized once
agent_initialized = False

async def initialize_agent():
    global agent_initialized
    if not agent_initialized:
        tools: List[Tool] = []  # Add your tools here if needed
        await OnBoardingAgent.register(runtime, "onboarding_agent", lambda: OnBoardingAgent(tools))
        runtime.start()
        agent_initialized = True


async def send_to_agent(user_message: str) -> str:
    response = await runtime.send_message(Message(content=user_message), onboarding_agent_id)
    return response.content

async def shutdown_agent():
    await runtime.stop()