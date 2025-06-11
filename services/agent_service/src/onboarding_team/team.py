import logging

from autogen_core import AgentId, SingleThreadedAgentRuntime
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, SseServerParams

from ..base_agents.editor_agent import EditorAgent
from ..base_agents.eval_agent import EvalAgent
from ..base_agents.executor_agent import ExecutorAgent
from ..base_agents.manager_agent import ManagerAgent
from ..base_agents.planner_agent import PlannerAgent
from ..base_agents.planner_refiner_agent import PlannerRefinerAgent
from ..protocols.message import Message
from ..source_agents.knowledgebase_agent import KBAgent
from ..source_agents.webrag_agent import WebRAGAgent
from ..source_agents.workbench_agent import WorkbenchAgent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

RUNTIME = SingleThreadedAgentRuntime()
PLANNER_AGENT_ID = AgentId("planner_agent", "default")
PLANNER_REFINER_AGENT_ID = AgentId("planner_refiner_agent", "default")
EXECUTOR_AGENT_ID = AgentId("executor_agent", "default")
NOTION_WORKBENCH_AGENT_ID = AgentId("notion_workbench_agent", "default")
GITHUB_WORKBENCH_AGENT_ID = AgentId("github_workbench_agent", "default")
EVAL_AGENT_ID = AgentId("eval_agent", "default")
EDITOR_AGENT_ID = AgentId("editor_agent", "default")
WEBRAG_AGENT_ID = AgentId("webrag_agent", "default")
KB_AGENT_ID = AgentId("kb_agent", "default")
MANAGER_AGENT_ID = AgentId("manager_agent", "default")

agent_initialized = False

notion_mcp_server_params = SseServerParams(
    url="http://localhost:8009/sse",
)

github_mcp_server_params = SseServerParams(
    url="http://localhost:8010/sse",
)


async def initialize_agent() -> None:
    global agent_initialized
    async with McpWorkbench(notion_mcp_server_params) as notion_workbench:
        async with McpWorkbench(github_mcp_server_params) as github_workbench:

            if not agent_initialized:
                await PlannerAgent.register(RUNTIME, "planner_agent", PlannerAgent)
                await PlannerRefinerAgent.register(
                    RUNTIME, "planner_refiner_agent", lambda: PlannerRefinerAgent()
                )

                await ExecutorAgent.register(
                    RUNTIME,
                    "executor_agent",
                    lambda: ExecutorAgent(
                        notion_workbench_agent_id=NOTION_WORKBENCH_AGENT_ID,
                        github_workbench_agent_id=GITHUB_WORKBENCH_AGENT_ID,
                        webrag_agent_id=WEBRAG_AGENT_ID,
                        kb_agent_id=KB_AGENT_ID,
                    ),
                )
                await WorkbenchAgent.register(
                    RUNTIME,
                    "notion_workbench_agent",
                    factory=lambda: WorkbenchAgent(
                        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
                        model_context=BufferedChatCompletionContext(buffer_size=10),
                        workbench=notion_workbench,
                    ),
                )
                await WorkbenchAgent.register(
                    RUNTIME,
                    "github_workbench_agent",
                    factory=lambda: WorkbenchAgent(
                        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
                        model_context=BufferedChatCompletionContext(buffer_size=10),
                        workbench=github_workbench,
                    ),
                )
                await WebRAGAgent.register(RUNTIME, "webrag_agent", WebRAGAgent)
                await KBAgent.register(RUNTIME, "kb_agent", KBAgent)

                await EvalAgent.register(RUNTIME, "eval_agent", EvalAgent)
                await EditorAgent.register(RUNTIME, "editor_agent", EditorAgent)

                await ManagerAgent.register(
                    RUNTIME,
                    "manager_agent",
                    lambda: ManagerAgent(
                        planner_agent_id=PLANNER_AGENT_ID,
                        planner_refiner_agent_id=PLANNER_REFINER_AGENT_ID,
                        executor_agent_id=EXECUTOR_AGENT_ID,
                        eval_agent_id=EVAL_AGENT_ID,
                        editor_agent_id=EDITOR_AGENT_ID,
                    ),
                )

                RUNTIME.start()
                agent_initialized = True


async def send_to_agent(user_message: Message) -> str:
    logging.info(f"Sending message to Manager of Mentor Agent: {user_message.content}")
    response = await RUNTIME.send_message(user_message, MANAGER_AGENT_ID)
    return response.content


async def shutdown_agent() -> None:
    await RUNTIME.stop()
