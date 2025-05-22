# Standard library imports
from typing import Optional

# Third-party imports
from autogen_core import AgentId, SingleThreadedAgentRuntime

# Local application imports
from .message import Message
from .planner_agent import PlannerAgent
from .refiner_agent import RefinerAgent
from .query_agent import QueryAgent
from .evaluation_agent import EvaluationAgent
from .editor_agent import EditorAgent
import os
# Constants
RUNTIME = SingleThreadedAgentRuntime()
PLANNER_AGENT_ID = AgentId('planner_agent', 'default')
REFINER_AGENT_ID = AgentId('refiner_agent', 'default')
QUERY_AGENT_ID = AgentId('query_agent', 'default')
EVALUATION_AGENT_ID = AgentId("evaluation_agent", "default")
EDITOR_AGENT_ID = AgentId("editor_agent", "default")
# Flag to ensure the agent is only initialized once
agent_initialized = False

async def initialize_agent() -> None:
    global agent_initialized
    if not agent_initialized:
        required_envs = ['CHROMA_DB_PATH', 'OPENAI_API_KEY','GROQ_API_KEY']
        missing = [var for var in required_envs if not os.getenv(var)]
        
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        await PlannerAgent.register(RUNTIME, 'planner_agent', lambda: PlannerAgent(REFINER_AGENT_ID))
        await RefinerAgent.register(RUNTIME, 'refiner_agent', lambda: RefinerAgent(QUERY_AGENT_ID))
        await QueryAgent.register(RUNTIME, 'query_agent', lambda: QueryAgent())
        await EvaluationAgent.register(RUNTIME, 'evaluation_agent', lambda: EvaluationAgent())
        await EditorAgent.register(RUNTIME, 'editor_agent', lambda: EditorAgent())
        
        RUNTIME.start()
        agent_initialized = True

async def send_to_agent(user_message: Message) -> str:
    response = await RUNTIME.send_message(user_message, PLANNER_AGENT_ID)
    return response.content

async def shutdown_agent() -> None:
    await RUNTIME.stop()