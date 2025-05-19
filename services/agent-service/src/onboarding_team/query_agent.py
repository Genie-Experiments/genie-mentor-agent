from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from .message import Message

class QueryAgent(RoutedAgent):
    def __init__(self):
        super().__init__("query_agent")

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> Message:
        print(f"Query Agent Received: {message.content}\n\n")
        return Message(content=f"Query Agent received: {message.content}")