import logging
import os  # Or from ..utils.settings import settings

from autogen_core import AgentId, SingleThreadedAgentRuntime
from autogen_core.model_context import BufferedChatCompletionContext
# The OpenAIChatCompletionClient can be used for any OpenAI-compatible API, including Groq
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, SseServerParams

from ..base_agents.editor_agent import EditorAgent
from ..base_agents.eval_agent import EvalAgent
from ..base_agents.executor_agent import ExecutorAgent
from ..base_agents.manager.manager_agent import ManagerAgent
from ..base_agents.planner_agent import PlannerAgent
from ..base_agents.planner_refiner_agent import PlannerRefinerAgent
from ..protocols.message import Message
from ..source_agents.knowledgebase_agent import KBAgent
from ..source_agents.websearch_agent import WebSearchAgent
from ..source_agents.workbench_agent import WorkbenchAgent
from ..utils.exceptions import (AgentServiceException, ExternalServiceError,
                                ValidationError, create_error_response,
                                handle_agent_error)

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
WEBSEARCH_AGENT_ID = AgentId("websearch_agent", "default")
KB_AGENT_ID = AgentId("kb_agent", "default")
MANAGER_AGENT_ID = AgentId("manager_agent", "default")

agent_initialized = False

notion_mcp_server_params = SseServerParams(
    url="http://notion-mcp-gateway:8009/sse",
    timeout=60*60,
    sse_read_timeout=60*60,
)

github_mcp_server_params = SseServerParams(
    url="http://github-mcp-gateway:8010/sse",
    timeout=60*60,
    sse_read_timeout=60*60,
)
# For local testing
'''
notion_mcp_server_params = SseServerParams(
    url="http://localhost:8009/sse",
)

github_mcp_server_params = SseServerParams(
    url="http://localhost:8010/sse",
)'''


async def initialize_agent() -> None:
    global agent_initialized, notion_workbench, github_workbench

    if agent_initialized:
        return

    notion_workbench = McpWorkbench(notion_mcp_server_params)
    github_workbench = McpWorkbench(github_mcp_server_params)

    await notion_workbench.__aenter__()
    await github_workbench.__aenter__()

    if not agent_initialized:
        # Validate required environment variables
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValidationError(
                message="OPENAI_API_KEY environment variable is required",
                field="OPENAI_API_KEY",
                user_message="Service configuration error. Please contact support."
            )

        gpt_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
            model_info={
                "context_length": 128000,
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": True,
                "family": "gpt"
            }
        )


        # Register all agents with error handling
    try:
        await PlannerAgent.register(
            RUNTIME, "planner_agent", lambda: PlannerAgent()
        )
        await PlannerRefinerAgent.register(
            RUNTIME, "planner_refiner_agent", lambda: PlannerRefinerAgent()
        )

        await ExecutorAgent.register(
            RUNTIME,
            "executor_agent",
            lambda: ExecutorAgent(
                notion_workbench_agent_id=NOTION_WORKBENCH_AGENT_ID,
                github_workbench_agent_id=GITHUB_WORKBENCH_AGENT_ID,
                webrag_agent_id=WEBSEARCH_AGENT_ID,
                kb_agent_id=KB_AGENT_ID
            )
        )

        # 2. Update the WorkbenchAgent for Notion to use the Groq client.
        await WorkbenchAgent.register(
            RUNTIME,
            "notion_workbench_agent",
            factory=lambda: WorkbenchAgent(
                model_client=gpt_client, # Use the configured Groq client
                model_context=BufferedChatCompletionContext(buffer_size=10),
                workbench=notion_workbench,
            ),
        )

        # 3. Update the WorkbenchAgent for GitHub to use the Groq client.
        await WorkbenchAgent.register(
            RUNTIME,
            "github_workbench_agent",
            factory=lambda: WorkbenchAgent(
                model_client=gpt_client, # Use the configured Groq client
                model_context=BufferedChatCompletionContext(buffer_size=10),
                workbench=github_workbench,
            ),
        )

        await WebSearchAgent.register(RUNTIME, 'websearch_agent', WebSearchAgent)
        await KBAgent.register(RUNTIME, 'kb_agent', KBAgent)

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
        logging.info("Agent service initialized successfully")

    except Exception as e:
        logging.error(f"Failed to register agents: {e}")
        raise AgentServiceException(
            message=f"Failed to initialize agent service: {str(e)}",
            error_code="AGENT_REGISTRATION_ERROR",
            details={"original_error": str(e)}
        )

    except Exception as e:
        logging.error(f"Failed to initialize agent service: {e}")
        if "notion" in str(e).lower():
            raise ExternalServiceError(
                message=f"Failed to connect to Notion service: {str(e)}",
                service="notion",
                details={"original_error": str(e)}
            )
        elif "github" in str(e).lower():
            raise ExternalServiceError(
                message=f"Failed to connect to GitHub service: {str(e)}",
                service="github",
                details={"original_error": str(e)}
            )
        else:
            raise AgentServiceException(
                message=f"Failed to initialize agent service: {str(e)}",
                error_code="INITIALIZATION_ERROR",
                details={"original_error": str(e)}
            )


async def send_to_agent(user_message: Message) -> str:
    """Send message to agent with comprehensive error handling."""
    try:
        # Validate input
        if not user_message or not user_message.content:
            raise ValidationError(
                message="User message is required and cannot be empty",
                field="user_message",
                user_message="Please provide a valid message."
            )

        # Check if agent is initialized
        if not agent_initialized:
            raise AgentServiceException(
                message="Agent service is not initialized",
                error_code="SERVICE_NOT_INITIALIZED",
                user_message="Service is starting up. Please try again in a moment."
            )

        logging.info(f"Sending message to Manager of Mentor Agent: {user_message.content}")
        
        # Add timeout handling
        import asyncio
        try:
            response = await asyncio.wait_for(
                RUNTIME.send_message(user_message, MANAGER_AGENT_ID),
                timeout=300  # 5 minutes timeout
            )
            return response.content
        except asyncio.TimeoutError:
            raise AgentServiceException(
                message="Request timed out after 5 minutes",
                error_code="REQUEST_TIMEOUT",
                user_message="The request is taking longer than expected. Please try again."
            )
            
    except AgentServiceException:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert any other exceptions to structured errors
        logging.error(f"Unexpected error in send_to_agent: {e}")
        error_response = handle_agent_error(e, "send_to_agent")
        return error_response


async def shutdown_agent() -> None:
    """Shutdown agent service gracefully."""
    try:
        if agent_initialized:
            await RUNTIME.stop()
            logging.info("Agent service shutdown successfully")
            if notion_workbench:
                await notion_workbench.__aexit__(None, None, None)
            if github_workbench:
                await github_workbench.__aexit__(None, None, None)
    except Exception as e:
        logging.error(f"Error during agent shutdown: {e}")
        # Don't raise during shutdown to avoid masking other errors