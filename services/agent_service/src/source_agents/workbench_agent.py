import json
from typing import List

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

    def contains_answer(self, messages):
        for m in messages:
            if isinstance(m, dict) and "answer" in m:
                return True
            if isinstance(m, str):
                try:
                    parsed = json.loads(m)
                    if isinstance(parsed, dict) and "answer" in parsed:
                        return True
                except json.JSONDecodeError:
                    continue
        return False

    def is_code_result(self, result):
        try:
            # Try to parse the result content as JSON to extract file info
            content = result.to_text()
            data = json.loads(content)
            # Handle both list and dict (single file or multiple)
            if isinstance(data, list):
                files = data
            else:
                files = [data]
            for file in files:
                name = file.get('name', '').lower()
                print("---------File Name-----------")
                print(name)
                if name == 'readme.md' or name == 'readme' or name.endswith('readme.md') or name == 'requirements.txt':
                    return False
            return True

        except Exception:
            return False

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
        get_file_contents_tools = [tool for tool in all_tools if tool['name'] == 'get_file_contents']
        if len(get_file_contents_tools) == 0:
            print("No get_file_contents tool found, breaking the flow")
            return
        
        try:
            create_result = await self._model_client.create(
                messages=self._system_messages + (await self._model_context.get_messages()),
                tools=get_file_contents_tools,
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
                    tools=get_file_contents_tools,
                    cancellation_token=ctx.cancellation_token,
                )

                print("------------Retrying------------")
                print(create_result)
            else:
                # return error in expected output json 
                result_json = {
                    "answer": "An error occurred while processing your request",
                    "sources": [],
                    "metadata": [],
                    "error": str(e),
                    
                }
                create_result = Message(content=json.dumps(result_json))
                return create_result

        # Run tool call loop.
        while (isinstance(create_result.content, list) and all(
            isinstance(call, FunctionCall) for call in create_result.content
        )) or self.is_function_calls_string(create_result.content):

            # If the content is a tool call string, parse it into a list of FunctionCall objects
            if isinstance(create_result.content, str) and self.is_function_calls_string(create_result.content):
                function_calls = self.parse_function_calls_from_string(create_result.content)
                create_result.content = function_calls

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
            valid_results = []
            for call in create_result.content:
                result = await self._workbench.call_tool(
                    call.name,
                    arguments=json.loads(call.arguments),
                    cancellation_token=ctx.cancellation_token,
                )
                results.append(result)
                #print(result)
                
                # Check if this is a directory listing (path ends with /)
                args = json.loads(call.arguments)
                is_directory_listing = args.get('path', '').endswith('/')
                
                # Don't filter directory listings, only filter individual file reads
                if not getattr(result, 'is_error', False):
                    if is_directory_listing or self.is_code_result(result):
                        valid_results.append((call, result))

            # Add only valid function execution results to the model context (non-error and valid code results)
            func_exec_result_msg = FunctionExecutionResultMessage(
                content=[
                    FunctionExecutionResult(
                        call_id=call.id,
                        content=result.to_text(),
                        is_error=result.is_error,
                        name=result.name,
                    )
                    for call, result in valid_results
                ]
            )
            if any(
                call.name
                in ["get_file_contents"]
                for call, result in valid_results
            ):
                self._response_context.append(str(func_exec_result_msg))

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
                tools=get_file_contents_tools,
                cancellation_token=ctx.cancellation_token,
            )
        assert isinstance(create_result.content, str)

        # Add the assistant message to the model context.
        await self._model_context.add_message(
            AssistantMessage(content=create_result.content, source="assistant")
        )

        try:
            """ print("---------Context------------")
            print(self._response_context) """
            result_json = parse_source_response(create_result.content)
            print("---------Final Response From MCP Agent-----------")
            print(result_json)
            response = WorkbenchResponse(
                answer=result_json.get("answer"),
                sources=self._response_context,
                metadata=result_json.get("metadata"),
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
            return Message(content=response.model_dump_json())
        except Exception as e:
            print(f"Error extracting JSON from response: {e}")
            # Create a fallback result with the original content as the answer
            result_json = {
                "answer": create_result.content,
                "sources": [],
                "metadata": [],
                "error": str(e)
            }
            return Message(content=json.dumps(result_json))
