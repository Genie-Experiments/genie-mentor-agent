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
                AssistantMessage(content=create_result.content,
                                 source="assistant")
            )

            # Call the tools using the workbench.
            print("---------Function Call Results-----------")
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
            func_exec_result_msg = FunctionExecutionResultMessage(
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
            if any(
                call.name
                in ["notion_retrieve_block_children", "get_file_contents"]
                for call in create_result.content
            ):
                self._response_context.append(str(func_exec_result_msg))

            await self._model_context.add_message(func_exec_result_msg)

            # Run the chat completion again to reflect on the history and function execution results.
            # Check if this is the final response phase
            messages = self._system_messages + (await self._model_context.get_messages())

            if self.contains_answer(messages):
                tools = []
            else:
                tools = await self._workbench.list_tools()
            # print("---------Tools Available-----------")
            # print(tools)
            # print("---------Messages Sent to MCP Agent-----------")
            # print(messages)
            create_result = await self._model_client.create(
                messages=messages,
                tools=tools,
                cancellation_token=ctx.cancellation_token,
            )
        assert isinstance(create_result.content, str)

        # Add the assistant message to the model context.
        await self._model_context.add_message(
            AssistantMessage(content=create_result.content, source="assistant")
        )

        try:
            print("---------Context------------")
            print(self._response_context)
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
