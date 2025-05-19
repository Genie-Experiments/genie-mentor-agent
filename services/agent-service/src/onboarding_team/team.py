from autogen_core import AgentId, SingleThreadedAgentRuntime
from .planner_agent import PlannerAgent
from .query_agent import QueryAgent
from .message import Message

runtime = SingleThreadedAgentRuntime()

planner_agent_id = AgentId("planner_agent", "default")
query_agent_id = AgentId("query_agent", "default")

# Flag to ensure the agent is only initialized once
agent_initialized = False

async def initialize_agent():
    global agent_initialized
    if not agent_initialized:
        await PlannerAgent.register(runtime, "planner_agent", lambda: PlannerAgent(query_agent_id ))
        await QueryAgent.register(runtime, "query_agent", lambda: QueryAgent())
        runtime.start()
        agent_initialized = True

async def send_to_agent(user_message: str) -> str:
    response = await runtime.send_message(Message(content=user_message.content), planner_agent_id)
    return response.content

async def shutdown_agent():
    await runtime.stop()