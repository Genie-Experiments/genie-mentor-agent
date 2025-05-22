import os
from typing import Optional

from autogen_core import AgentId, SingleThreadedAgentRuntime
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench

from .message import Message
from .planner_agent import PlannerAgent
from .refiner_agent import RefinerAgent
from .query_agent import QueryAgent
from .evaluation_agent import EvaluationAgent
from .editor_agent import EditorAgent
from .workbench_agent import WorkbenchAgent

# Agent IDs
RUNTIME = SingleThreadedAgentRuntime()
PLANNER_AGENT_ID = AgentId('planner_agent', 'default')
REFINER_AGENT_ID = AgentId('refiner_agent', 'default')
QUERY_AGENT_ID = AgentId('query_agent', 'default')
WORKBENCH_AGENT_ID = AgentId('workbench_agent', 'default')
EVALUATION_AGENT_ID = AgentId('evaluation_agent', 'default')
EDITOR_AGENT_ID = AgentId('editor_agent', 'default')

agent_initialized = False

notion_mcp_server_params = StdioServerParams(
    command="npx",
    args=["-y", "@suekou/mcp-notion-server"],
    env={
        "NOTION_API_TOKEN": os.getenv('NOTION_API_KEY'),
        "NOTION_MARKDOWN_CONVERSION": "true"
    },
    read_timeout_seconds=45
)

async def initialize_agent() -> None:
    global agent_initialized
    if not agent_initialized:
        required_envs = ['CHROMA_DB_PATH', 'OPENAI_API_KEY', 'GROQ_API_KEY']
        missing = [var for var in required_envs if not os.getenv(var)]
        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

        async with McpWorkbench(notion_mcp_server_params) as workbench:
            await PlannerAgent.register(
                RUNTIME,
                'planner_agent',
                lambda: PlannerAgent(REFINER_AGENT_ID, QUERY_AGENT_ID),
            )
            await RefinerAgent.register(
                RUNTIME,
                'refiner_agent',
                lambda: RefinerAgent(QUERY_AGENT_ID),
            )
            await QueryAgent.register(
                RUNTIME,
                'query_agent',
                lambda: QueryAgent(WORKBENCH_AGENT_ID),
            )
            await EvaluationAgent.register(
                RUNTIME,
                'evaluation_agent',
                lambda: EvaluationAgent(),
            )
            await EditorAgent.register(
                RUNTIME,
                'editor_agent',
                lambda: EditorAgent(),
            )
            await WorkbenchAgent.register(
                RUNTIME,
                'workbench_agent',
                lambda: WorkbenchAgent(
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
