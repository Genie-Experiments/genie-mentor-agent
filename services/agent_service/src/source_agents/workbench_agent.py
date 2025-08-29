import json
from typing import List, Dict, Any

from autogen_core import (FunctionCall, MessageContext, RoutedAgent,
                          message_handler)
from autogen_core.model_context import ChatCompletionContext
from autogen_core.models import (AssistantMessage, ChatCompletionClient,
                                 FunctionExecutionResult,
                                 FunctionExecutionResultMessage, LLMMessage,
                                 SystemMessage, UserMessage)
from autogen_core.tools import ToolResult, Workbench

from ..protocols.message import Message
from ..utils.parsing import parse_source_response
from ..protocols.schemas import WorkbenchResponse


class WorkbenchAgent(RoutedAgent):
    def __init__(
        self,
        model_client: ChatCompletionClient,
        model_context: ChatCompletionContext,
        workbench: Workbench,
    ) -> None:
        super().__init__("An agent with a workbench")
        self._system_messages: List[LLMMessage] = [
            SystemMessage(content="You are a helpful AI assistant.")
        ]
        self._model_client = model_client
        self._model_context = model_context
        self._workbench = workbench
        self._response_context = []
        self._metadata_context = []

    def extract_metadata_from_result(self, result: ToolResult) -> List[Dict[str, Any]]:
        """Extract metadata from tool results, especially for chunking tool results."""
        metadata_list = []
        
        try:
            content = result.to_text()
            data = json.loads(content)
            
            # Handle query_chromadb_tool or get_chunks_tool results
            if isinstance(data, dict):
                # Check if this is a chunking tool result
                if 'chunks' in data or 'results' in data:
                    chunks = data.get('chunks', []) or data.get('results', [])
                    for chunk in chunks:
                        if isinstance(chunk, dict) and 'metadata' in chunk:
                            chunk_metadata = chunk['metadata']
                            # Extract relevant metadata
                            metadata_entry = {
                                'repo_name': chunk_metadata.get('repo_name', ''),
                                'repo_link': chunk_metadata.get('repo_link', ''), 
                            } 
                            metadata_list.append(metadata_entry)
                
                # Handle direct metadata field
                elif 'metadata' in data:
                    if isinstance(data['metadata'], list):
                        metadata_list.extend(data['metadata'])
                    elif isinstance(data['metadata'], dict):
                        metadata_list.append(data['metadata'])
        
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return metadata_list

    def _build_compact_metadata(self, items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Convert list of metadata dicts into a compact object with de-duplicated lists.

        Output shape:
        {
            "repo_names": [unique repo names],
            "repo_links": [unique repo links]
        }
        Empty values are ignored.
        """
        repo_names: List[str] = []
        repo_links: List[str] = []
        seen_names = set()
        seen_links = set()

        for item in items or []:
            if isinstance(item, dict):
                name = (item.get("repo_name") or "").strip()
                link = (item.get("repo_link") or "").strip()

                if name and name not in seen_names:
                    seen_names.add(name)
                    repo_names.append(name)

                if link and link not in seen_links:
                    seen_links.add(link)
                    repo_links.append(link)

        return [{"repo_names": repo_names, "repo_links": repo_links}]

    def extract_sources_from_result(self, result: ToolResult) -> List[str]:
        """Extract source content from tool results."""
        sources = []
        
        try:
            content = result.to_text()
            data = json.loads(content)
            
            # Handle query_chromadb_tool or get_chunks_tool results
            if isinstance(data, dict):
                # Check if this is a chunking tool result
                if 'chunks' in data or 'results' in data:
                    chunks = data.get('chunks', []) or data.get('results', [])
                    for chunk in chunks:
                        if isinstance(chunk, dict) and 'page_content' in chunk:
                            sources.append(chunk['page_content'])
                
                # Handle source_documents field
                elif 'source_documents' in data:
                    for doc in data['source_documents']:
                        if isinstance(doc, dict) and 'page_content' in doc:
                            sources.append(doc['page_content'])
                        elif isinstance(doc, str):
                            sources.append(doc)
                
                # Handle direct content field
                elif 'content' in data and isinstance(data['content'], str):
                    sources.append(data['content'])
        
        except (json.JSONDecodeError, AttributeError):
            # If parsing fails, try to use the raw text as a source
            text = result.to_text()
            if text and len(text) > 0:
                sources.append(text)
        
        return sources


    def is_function_calls_string(self, content: str) -> bool:
        print("---------Content-----------")
        print(content)
        return (isinstance(content, str) and 
                (
                    content.strip().startswith('{"type": "function"') or
                    content.strip().startswith('{"function":')
                ))

    def parse_function_calls_from_string(self, content: str) -> List[FunctionCall]:
        """Parse function calls from string format to FunctionCall objects."""
        function_calls = []

        # Split by newlines and parse each JSON object
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            try:
                func_data = json.loads(line)
                
                # Handle both formats: {"type": "function", ...} and {"function": "name", "params": {...}}
                if func_data.get('type') == 'function':
                    # Original format
                    function_call = FunctionCall(
                        id=f"call_{len(function_calls)}",
                        name=func_data['name'],
                        arguments=json.dumps(func_data['parameters'])
                    )
                elif 'function' in func_data and 'params' in func_data:
                    # New format that the model is actually using
                    function_call = FunctionCall(
                        id=f"call_{len(function_calls)}",
                        name=func_data['function'],
                        arguments=json.dumps(func_data['params'])
                    )
                else:
                    print(f"Unrecognized function call format: {func_data}")
                    continue
                    
                function_calls.append(function_call)
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse function call: {line}, Error: {e}")
                continue
        print("---------Function Calls-----------")
        print(function_calls)           
        return function_calls

    @message_handler
    async def handle_user_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        # Cumulative token usage trackers
        cumulative_prompt_tokens = 0
        cumulative_completion_tokens = 0
        
        # Reset context for new message
        self._response_context = []
        self._metadata_context = []
        
        # Add the user message to the model context.
        await self._model_context.add_message(
            UserMessage(content=message.content, source="user")
        )

        # Run the chat completion with the tools.
        # Use full message history from the model context
        all_user_messages = await self._model_context.get_messages()
        messages = self._system_messages + all_user_messages
        # Only provide the 'get_file_contents' tool
        all_tools = await self._workbench.list_tools()
        print("---------All Tools-----------")
        print(all_tools)
        
        try:
            create_result = await self._model_client.create(
                messages=self._system_messages + (await self._model_context.get_messages()),
                tools=all_tools,
                cancellation_token=ctx.cancellation_token,
            )
        except Exception as e:
            print(e)
            if "tool_use_failed" in str(e) and "failed_generation" in str(e):
                # Add a correction message
                correction_msg = UserMessage(
                    content="The previous function calls failed due to incorrect format. "
                            "Please use the exact JSON format shown in the examples, "
                            "not XML tags. Make the function calls again properly.",
                            source="assistant"
                )
                await self._model_context.add_message(correction_msg)
            
                # Retry
                create_result = await self._model_client.create(
                    messages=self._system_messages + (await self._model_context.get_messages()),
                    tools=all_tools,
                    cancellation_token=ctx.cancellation_token,
                )

                print("------------Retrying------------")
                print(create_result)
            else:
                # return error in expected output json 
                result_json = {
                    "answer": "An error occurred while processing your request",
                    "sources": [],
                    "metadata": {"repo_names": [], "repo_links": []},
                    "error": str(e),
                    
                }
                create_result = Message(content=json.dumps(result_json))
                return create_result

        # Run tool call loop.
        while (isinstance(create_result.content, list) and all(
            isinstance(call, FunctionCall) for call in create_result.content
        )) or self.is_function_calls_string(create_result.content):

            print("---------Function Calls-----------")
            for call in create_result.content:
                print(call)

            # Add the function calls to the model context.
            await self._model_context.add_message(
                AssistantMessage(content=create_result.content,
                                 source="assistant")
            )

            # Call the tools using the workbench.
            print("---------Function Call Results-----------")
            results: List[ToolResult] = []
            all_results = []
            
            for call in create_result.content:
                result = await self._workbench.call_tool(
                    call.name,
                    arguments=json.loads(call.arguments),
                    cancellation_token=ctx.cancellation_token,
                )
                results.append(result)
                print(result)
                
                # Extract sources and metadata from ALL tool results
                if call.name in ["query_chromadb_tool", "search_by_file_tool"]:
                    # Extract sources
                    sources = self.extract_sources_from_result(result)
                    self._response_context.extend(sources)
                    
                    # Extract metadata
                    metadata = self.extract_metadata_from_result(result)
                    self._metadata_context.extend(metadata)
                    
                    print("---------Tool Result-----------")
                    try:
                        content = result.to_text()
                        data = json.loads(content)
                        print(data)
                    except:
                        print(result.to_text())

                all_results.append((call, result))
                
                

            # Add only valid function execution results to the model context (non-error and valid code results)
            func_exec_result_msg = FunctionExecutionResultMessage(
                content=[
                    FunctionExecutionResult(
                        call_id=call.id,
                        content=result.to_text(),
                        is_error=result.is_error,
                        name=result.name,
                    )
                    for call, result in all_results
                ]
            )

            await self._model_context.add_message(func_exec_result_msg)

            print("---------TOKEN USAGE-----------")
            print(create_result.usage.prompt_tokens)
            print(create_result.usage.completion_tokens)
            # Update cumulative token usage
            if hasattr(create_result, 'usage'):
                cumulative_prompt_tokens += getattr(create_result.usage, 'prompt_tokens', 0)
                cumulative_completion_tokens += getattr(create_result.usage, 'completion_tokens', 0)

            # Run the chat completion again to reflect on the history and function execution results.
            # Check if this is the final response phase
            messages = self._system_messages + (await self._model_context.get_messages())
            create_result = await self._model_client.create(
                messages=messages,
                tools=all_tools,
                cancellation_token=ctx.cancellation_token,
            )
        assert isinstance(create_result.content, str)

        # Add the assistant message to the model context.
        await self._model_context.add_message(
            AssistantMessage(content=create_result.content, source="assistant")
        )

        # Print debug information
        print("---------Content (Sources)------------")
        print(f"Number of sources: {len(self._response_context)}")
        
        print("---------Metadata------------")
        print(f"Number of metadata items: {len(self._metadata_context)}")
        for meta in self._metadata_context:
            print(f"Repo: {meta.get('repo_name', 'Unknown')}")
            

        try:
            print("-------Pasing Source Response-------")
            print(create_result.content)
            
            # Use the collected sources and metadata
            compact_metadata = self._build_compact_metadata(self._metadata_context)
            response = WorkbenchResponse(
                answer=create_result.content,
                sources=self._response_context,
                metadata=compact_metadata,
                error=None
            )
    
            
            
            print("---------Final Response From MCP Agent-----------")
            print(response)
            print("---------Token Usage-----------")
            print(create_result.usage.prompt_tokens)
            print(create_result.usage.completion_tokens)
            # Update cumulative token usage
            if hasattr(create_result, 'usage'):
                cumulative_prompt_tokens += getattr(create_result.usage, 'prompt_tokens', 0)
                cumulative_completion_tokens += getattr(create_result.usage, 'completion_tokens', 0)
            print("========= CUMULATIVE TOKEN USAGE =========")
            print(f"Total prompt tokens: {cumulative_prompt_tokens}")
            print(f"Total completion tokens: {cumulative_completion_tokens}")
            print(f"Total tokens: {cumulative_prompt_tokens + cumulative_completion_tokens}")
            # Use json.dumps with proper escaping
            return Message(content=json.dumps({
                "answer": create_result.content,
                "sources": self._response_context,
                "metadata": compact_metadata,
                "error": None
            }, ensure_ascii=False, indent=None))
        except Exception as e:
            print(f"Error extracting JSON from response: {e}")
            # Create a fallback result with the collected context
            compact_metadata = self._build_compact_metadata(self._metadata_context)
            result_json = {
                "answer": json.dumps(create_result.content),  # Double-encode if needed
                "sources": self._response_context,
                "metadata": compact_metadata,
                "error": str(e)
            }
            return Message(content=json.dumps(result_json))