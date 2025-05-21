# Standard library imports
from typing import Optional

# Third-party imports
from autogen_core import AgentId, SingleThreadedAgentRuntime

# Local application imports
from .message import Message
from .planner_agent import PlannerAgent
from .refiner_agent import RefinerAgent
from .query_agent import QueryAgent

# Constants
RUNTIME = SingleThreadedAgentRuntime()
PLANNER_AGENT_ID = AgentId('planner_agent', 'default')
REFINER_AGENT_ID = AgentId('refiner_agent', 'default')
QUERY_AGENT_ID = AgentId('query_agent', 'default')

# Flag to ensure the agent is only initialized once
agent_initialized = False

async def initialize_agent() -> None:
    global agent_initialized
    if not agent_initialized:
        await PlannerAgent.register(RUNTIME, 'planner_agent', lambda: PlannerAgent(REFINER_AGENT_ID))
        await RefinerAgent.register(RUNTIME, 'refiner_agent', lambda: RefinerAgent(QUERY_AGENT_ID))
        await QueryAgent.register(RUNTIME, 'query_agent', lambda: QueryAgent())
        RUNTIME.start()
        agent_initialized = True

async def send_to_agent(user_message: Message) -> str:
    response = await RUNTIME.send_message(user_message, PLANNER_AGENT_ID)
    return response.content

async def shutdown_agent() -> None:
    await RUNTIME.stop()