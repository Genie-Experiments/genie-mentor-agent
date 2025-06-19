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
from ..utils.parsing import extract_json_with_brace_counting, parse_source_response

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

    @message_handler
    async def handle_user_message(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        # Add the user message to the model context.
        await self._model_context.add_message(
            UserMessage(content=message.content, source="user")
        )

        # Run the chat completion with the tools.
        create_result = await self._model_client.create(
            messages=self._system_messages + (await self._model_context.get_messages()),
            tools=(await self._workbench.list_tools()),
            cancellation_token=ctx.cancellation_token,
        )

        # Run tool call loop.
        while isinstance(create_result.content, list) and all(
            isinstance(call, FunctionCall) for call in create_result.content
        ):
            print("---------Function Calls-----------")
            for call in create_result.content:
                print(call)

            # Add the function calls to the model context.
            await self._model_context.add_message(
                AssistantMessage(content=create_result.content, source="assistant")
            )

            # Call the tools using the workbench.
            # print("---------Function Call Results-----------")
            results: List[ToolResult] = []
            for call in create_result.content:
                result = await self._workbench.call_tool(
                    call.name,
                    arguments=json.loads(call.arguments),
                    cancellation_token=ctx.cancellation_token,
                )
                results.append(result)
                print(result)

            # Add the function execution results to the model context.
            await self._model_context.add_message(
                FunctionExecutionResultMessage(
                    content=[
                        FunctionExecutionResult(
                            call_id=call.id,
                            content=result.to_text(),
                            is_error=result.is_error,
                            name=result.name,
                        )
                        for call, result in zip(
                            create_result.content, results, strict=False
                        )
                    ]
                )
            )

            # Run the chat completion again to reflect on the history and function execution results.
            create_result = await self._model_client.create(
                messages=self._system_messages
                + (await self._model_context.get_messages()),
                tools=(await self._workbench.list_tools()),
                cancellation_token=ctx.cancellation_token,
            )
        assert isinstance(create_result.content, str)

        

        # Add the assistant message to the model context.
        await self._model_context.add_message(
            AssistantMessage(content=create_result.content, source="assistant")
        )
        
        try:
            print("---------Final Response From MCP Agent-----------")
            print(create_result.content)
            
            # Use our new parser that handles GitHub and Notion content
            result_json = parse_source_response(create_result.content)

            return Message(content=json.dumps(result_json))
        except Exception as e:
            print(f"Error extracting JSON from response: {e}")
            # Create a fallback result with the original content as the answer
            result_json = {
                "answer": create_result.content,
                "metadata": {},
                "error": str(e)
            }
            return Message(content=json.dumps(result_json))
        
