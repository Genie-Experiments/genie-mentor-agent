# Standard library imports
import json
import os
import subprocess
import asyncio
from typing import Any, Dict, Optional, List

# Third-party imports
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import mcp_server_tools, StdioServerParams

# Local application imports
from ..rag.rag import query_knowledgebase
from .message import Message


class QueryAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("query_agent")
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize notion tools to None - we'll connect on first use
        self.notion_tools = None
        self._notion_initialized = False
        
        # Set environment variable for tokenizers
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

    async def _ensure_notion_mcp_initialized(self) -> bool:
        """
        Ensure Notion MCP is initialized using suekou implementation.
        Returns True if successful, False otherwise.
        """
        if self._notion_initialized and self.notion_tools:
            return len(self.notion_tools) > 0
            
        self._notion_initialized = True
        
        # Try suekou's implementation
        try:
            print("[INFO] Trying suekou's Notion MCP implementation")
            
            # Install the package if needed
            try:
                subprocess.run(["npx", "-y", "@suekou/mcp-notion-server", "--version"], 
                              check=True, capture_output=True, text=True)
                print("[INFO] suekou's MCP server is available")
            except Exception as e:
                print(f"[WARNING] Package check failed, will attempt installation: {e}")
                # Let npx handle the installation directly
            
            # Configure suekou's MCP server
            server_params = StdioServerParams(
                command="npx",
                args=["-y", "@suekou/mcp-notion-server"],
                env={
                    "NOTION_API_TOKEN": os.getenv('NOTION_API_KEY'),
                    "NOTION_MARKDOWN_CONVERSION": "true"  # Enable markdown conversion for better token usage
                },
                read_timeout_seconds=15
            )
            
            # Connect with timeout to avoid hanging
            try:
                self.notion_tools = await asyncio.wait_for(
                    mcp_server_tools(server_params), 
                    timeout=30
                )
                
                print(f"[INFO] Successfully connected to suekou's Notion MCP server. {len(self.notion_tools)} tools available.")
                if self.notion_tools:
                    print(f"[INFO] Available tools: {[tool.name for tool in self.notion_tools]}")
                return True
            except asyncio.TimeoutError:
                print("[ERROR] Timeout connecting to suekou's Notion MCP server")
                
        except Exception as e:
            print(f"[ERROR] Failed to connect to suekou's Notion MCP server: {str(e)}")
        
        print("[ERROR] suekou's MCP server connection attempt failed")
        self.notion_tools = []
        return False

    @message_handler
    async def handle_query_plan(self, message: Message, ctx: MessageContext) -> Message:
        plan = json.loads(message.content)
        query_components = {q["id"]: q for q in plan["query_components"]}
        execution_order = plan["execution_order"]

        self._sources_used = []
        results = {}

        for qid in execution_order["nodes"]:
            result = await self.execute_query(qid, query_components)
            results[qid] = result

        # Aggregate results using custom strategy
        aggregated = await self.aggregate_results(plan["user_query"], results, strategy=execution_order.get("aggregation"))
        return Message(content=aggregated)

    async def execute_query(self, qid: str, query_components: Dict[str, Any]) -> Dict[str, Any]:
        q = query_components[qid]
        sub_query = q["sub_query"]
        source = q["source"]

        if source == "knowledgebase":
            notion_available = await self._ensure_notion_mcp_initialized()
            
            if notion_available and self.notion_tools:
                response = await self.query_notion(sub_query)
            else:
                print("[ERROR] Could not connect to Notion MCP server")
                response = {
                    "answer": "I couldn't connect to your Notion workspace. Please verify that you have a valid Notion API token set as the NOTION_API_TOKEN environment variable.",
                    "sources": []
                }
        elif source == "notion":
            # Initialize notion MCP if not already done
            notion_available = await self._ensure_notion_mcp_initialized()
            
            if notion_available and self.notion_tools:
                response = await self.query_notion(sub_query)
            else:
                print("[ERROR] Could not connect to Notion MCP server")
                response = {
                    "answer": "I couldn't connect to your Notion workspace. Please verify that you have a valid Notion API token set as the NOTION_API_TOKEN environment variable.",
                    "sources": []
                }
        else:
            raise ValueError(f"Unsupported source: {source}")

        if "sources" in response:
            self._sources_used.extend(response["sources"])
        return response["answer"]

    async def query_notion(self, sub_query: str) -> Dict[str, Any]:

        print(f"[INFO] Querying Notion for: {sub_query}")
        
        if not self.notion_tools:
            return {
                "answer": "Notion integration is not available.",
                "sources": []
            }
        
        # Create a prompt that will allow the model to decide which tools to use
        prompt = f"""
        You have access to Notion tools to find information about: "{sub_query}"
        
        Available Notion tools: {[tool.name for tool in self.notion_tools]}
        
        Use these tools to find the most relevant information. Think step by step about which tools to use and in what order.
        Return the information in a clear, concise format. Call these tools as well and provide the final information fetched once.
        """
        
        # Let the model decide which tools to use by providing them to model.create()
        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source=self.id.key)],
            tools=self.notion_tools  # Provide the Notion tools to the model
        )
        print(f"[INFO] Notion query response: {response}")
        # Process the model's response which should include tool calls
        if response.content:
            print(f"[INFO] Notion query result: {response.content}")
            return {
                "answer": response.content,
                "sources": ["notion_mcp"]
            }
        else:
            return {
                "answer": "No relevant information found in Notion.",
                "sources": []
            }

    async def aggregate_results(self, user_query: str, results: Dict[str, Any], strategy: Optional[str] = None) -> Dict[str, Any]:
        prompt = f'''
        You are an assistant tasked with aggregating results fetched from multiple sources in response to a user query.
        When aggregating the results, ensure they are relevant to the user's query and follow the given aggregation strategy.
        
        User Query: "{user_query}"
        Results: {results}
        Aggregation Strategy: "{strategy}"
        
        Instructions:
        - Aggregate the provided results into a coherent and concise response.
        - Assess the relevance of the results to the user's query.
        - Provide a confidence score (0–100) indicating how relevant and accurate the aggregated answer is.
        - Return the response as a properly formatted JSON object using the following structure:
        
        {{
            "aggregated_results": "<your aggregated response here>",
            "confidence_score": <integer between 0 and 100>
        }}
        '''

        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source=self.id.key)],
            tools=self.notion_tools
        )

        try:
            # First try to parse the response content
            content = response.content.strip()
            
            # If the content is wrapped in markdown code blocks, extract the JSON
            if content.startswith('```json') and content.endswith('```'):
                content = content[7:-3].strip()  #
            
            # Parse the JSON
            result = json.loads(content)
            
            # Return both aggregated results and confidence score
            return json.dumps({
                "aggregated_results": result["aggregated_results"],
                "confidence_score": result["confidence_score"]
            })
        except json.JSONDecodeError:
            # If parsing fails, wrap the raw response
            return json.dumps({
                "aggregated_results": response.content,
                "confidence_score": 0
            })

def query_notion(sub_query: str) -> Dict[str, Any]:
    return {
        "answer": "",
        "sources": []
    }