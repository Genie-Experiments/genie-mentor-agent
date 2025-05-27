# Standard library imports
from typing import Optional
import os

# Third-party imports
from autogen_core import AgentId, SingleThreadedAgentRuntime
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

# Local application imports
from .message import Message
from .planner_agent import PlannerAgent
from .refiner_agent import RefinerAgent
from .query_agent import QueryAgent
from .workbench_agent import WorkbenchAgent

# Constants
RUNTIME = SingleThreadedAgentRuntime()
PLANNER_AGENT_ID = AgentId('planner_agent', 'default')
REFINER_AGENT_ID = AgentId('refiner_agent', 'default')
QUERY_AGENT_ID = AgentId('query_agent', 'default')
WORKBENCH_AGENT_ID = AgentId('workbench_agent', 'default')

# Flag to ensure the agent is only initialized once
agent_initialized = False

notion_mcp_server_params = StdioServerParams(
                command="docker",
    args=[
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
    ],
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv('GITHUB_MCP_TOKEN')
    },
    read_timeout_seconds=45
            )

async def initialize_agent() -> None:
    global agent_initialized
    async with McpWorkbench(notion_mcp_server_params) as workbench:
        
        if not agent_initialized:
            await PlannerAgent.register(RUNTIME, 'planner_agent', lambda: PlannerAgent(REFINER_AGENT_ID))
            await RefinerAgent.register(RUNTIME, 'refiner_agent', lambda: RefinerAgent(QUERY_AGENT_ID))
            await QueryAgent.register(RUNTIME, 'query_agent', lambda: QueryAgent(WORKBENCH_AGENT_ID))
            await WorkbenchAgent.register(RUNTIME, 'workbench_agent',
                factory=lambda: WorkbenchAgent(


                    model_client=OpenAIChatCompletionClient(model="gpt-4.1-nano"),
                    model_context=BufferedChatCompletionContext(buffer_size=10),
                    workbench=workbench,
                ),
            )
        
            RUNTIME.start()
            agent_initialized = True

async def send_to_agent(user_message: Message) -> str:
    print(f"[INFO] Sending message to agent: {user_message.content}")
    response = await RUNTIME.send_message(user_message, PLANNER_AGENT_ID)
    return response.content

async def shutdown_agent() -> None:
    await RUNTIME.stop()