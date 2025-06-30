import json
from enum import Enum
from typing import Any, Dict, Optional

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from groq import Groq

from ..prompts.aggregation_prompt import generate_aggregated_answer
from ..prompts.prompts import GITHUB_PROMPT, NOTION_QUERY_PROMPT
from ..protocols.message import Message
from ..protocols.schemas import  LLMUsage
from ..utils.parsing import extract_json_with_regex
from ..utils.settings import settings
from ..utils.token_tracker import token_tracker

from ..protocols.schemas import KBResponse
from ..utils.logging import setup_logger, get_logger
from ..utils.exceptions import (
    ExecutionError, ExternalServiceError, ValidationError, TimeoutError,
    NetworkError, AgentServiceException, handle_agent_error
)
import string
setup_logger()
logger = get_logger("ExecutorAgent")

class SourceType(Enum):
    KNOWLEDGEBASE = "knowledgebase"
    NOTION = "notion"
    GITHUB = "github"
    WEBSEARCH = "websearch"

class ExecutorAgent(RoutedAgent):
    def __init__(
        self,
        notion_workbench_agent_id: AgentId,
        github_workbench_agent_id: AgentId,
        webrag_agent_id: AgentId,
        kb_agent_id: AgentId,
        answer_cleaner_agent_id: AgentId,
    ) -> None:
        super().__init__("executor_agent")
        self.notion_workbench_agent_id = notion_workbench_agent_id
        self.github_workbench_agent_id = github_workbench_agent_id
        self.webrag_agent_id = webrag_agent_id
        self.kb_agent_id = kb_agent_id
        self.answer_cleaner_agent_id = answer_cleaner_agent_id
        
        # Validate API key
        if not settings.GROQ_API_KEY:
            raise ValidationError(
                message="GROQ_API_KEY is required for ExecutorAgent",
                field="GROQ_API_KEY"
            )
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.DEFAULT_MODEL

    def _handle_source_error(self, error: Exception, source: str, sub_query: str) -> Dict[str, Any]:
        """Handle errors from specific data sources with structured error handling."""
        logger.error(f"[ExecutorAgent] Error in {source} source: {error}")
        
        if isinstance(error, ExternalServiceError):
            return {
                "answer": f"Unable to retrieve information from {source} at this time.",
                "sources": [],
                "metadata": [],
                "error": error.to_dict()
            }
        elif isinstance(error, TimeoutError):
            return {
                "answer": f"Request to {source} timed out. Please try again.",
                "sources": [],
                "metadata": [],
                "error": error.to_dict()
            }
        elif isinstance(error, NetworkError):
            return {
                "answer": f"Network error while accessing {source}. Please check your connection.",
                "sources": [],
                "metadata": [],
                "error": error.to_dict()
            }
        else:
            # Convert generic errors to structured format
            structured_error = handle_agent_error(error, f"{source}_execution")
            return {
                "answer": f"Error occurred while processing {source} request.",
                "sources": [],
                "metadata": [],
                "error": structured_error
            }

    @message_handler
    async def handle_query_plan(self, message: Message, ctx: MessageContext) -> Message:
        try:
            # Validate input
            if not message.content:
                raise ValidationError(
                    message="Query plan content is required",
                    field="message.content"
                )

            content = json.loads(message.content)
            plan = content.get(
                "plan", content
            )  # Handle both direct plan and wrapped plan

            if not plan:
                raise ValidationError(
                    message="Plan is required in message content",
                    field="plan"
                )

            query_components = {q["id"]: q for q in plan["query_components"]}
            execution_order = plan["execution_order"]
            self._sources_used = []
            self._sources_documents = {}
            self._sources_metadata = {}
            results = {}

            for qid in execution_order["nodes"]:
                logger.info(f"Executing query ID: {qid}")
                try:
                    result = await self.execute_query(qid, query_components)
                    results[qid] = result
                except Exception as e:
                    logger.error(f"Error executing query {qid}: {e}")
                    results[qid] = self._handle_source_error(e, query_components[qid].get("source", "unknown"), query_components[qid].get("sub_query", ""))

            # Build valid_results with custom rules:
            valid_results = {}
            for qid, res in results.items():
                source_type = query_components[qid].get("source", "").lower()
                # Must have a non-empty answer and no error regardless of source
                if not res.get("answer") or res.get("error"):
                    continue
                if source_type in {SourceType.GITHUB.value, SourceType.NOTION.value}:
                    # For GitHub/Notion we don't require sources to be present.
                    valid_results[qid] = res
                    # Ensure we have an entry so downstream aggregation doesn't fail.
                    if source_type not in self._sources_documents:
                        self._sources_documents[source_type] = res.get("sources", []) or []
                else:
                    # For other sources require at least one source document.
                    if res.get("sources"):
                        valid_results[qid] = res

            if len(valid_results) == 1:
                # Only one valid source, use it directly (and allow downstream evaluation)
                only_result = list(valid_results.values())[0]
                logger.info("Only one valid source present. Skipping aggregation, proceeding with single valid result.")
                return Message(content=json.dumps({
                    "executor_answer": only_result["answer"],
                    "all_documents": [
                        doc for docs in self._sources_documents.values() for doc in docs
                    ],
                    "documents_by_source": self._sources_documents,
                    "metadata_by_source": self._sources_metadata,
                    "error": None,
                    "llm_usage": None  # No LLM call made for single source aggregation
                }))

            elif len(valid_results) < 1:
                logger.warning("No valid sources. Returning error.")
                raise ExecutionError(
                    message="All data sources failed to provide valid responses",
                    details={
                        "failed_sources": list(results.keys()),
                        "total_sources": len(results)
                    },
                    user_message="I'm unable to retrieve information from any of my data sources at the moment. Please try again later."
                )

            logger.info("Combining answers from all data sources.")

            try:
                original_ids = list(valid_results.keys())
                id_mapping = {qid: string.ascii_uppercase[i] for i, qid in enumerate(original_ids)}
                minimal_results = {
                    id_mapping[qid]: {
                        "id": id_mapping[qid],
                        "source": query_components[qid].get("source"),
                        "answer": res["answer"]
                    }
                    for qid, res in valid_results.items()
                }
                combined_execution_results = await self._combine_answer_from_sources(
                    plan["user_query"],
                    minimal_results,
                    strategy=execution_order.get("aggregation")
                )
            except Exception as e:
                logger.error(f"Error combining answers: {e}")
                raise ExecutionError(
                    message=f"Failed to combine answers from sources: {str(e)}",
                    details={"valid_sources": list(valid_results.keys())}
                )

            all_documents = [
                doc for docs in self._sources_documents.values() for doc in docs
            ]

            logger.info("Returning combined results.")
            return Message(
                content=json.dumps(
                    {
                        "executor_answer": combined_execution_results[
                            "executor_answer"
                        ],
                        "all_documents": all_documents,
                        "documents_by_source": self._sources_documents,
                        "metadata_by_source": self._sources_metadata,
                        "error": None,
                        "llm_usage": combined_execution_results.get("llm_usage"),
                    }
                )
            )

        except AgentServiceException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Error while executing query plan: {e}")
            error_response = handle_agent_error(e, "query_plan_execution")
            return Message(content=json.dumps(error_response))

    async def execute_query(
        self, qid: str, query_components: Dict[str, Any]
    ) -> Dict[str, Any]:
        q = query_components[qid]
        sub_query = q["sub_query"]
        source = q.get("source")

        logger.info(f"Executing sub-query from source: {source}")

        try:
            # Use enum for all source checks
            if source == SourceType.KNOWLEDGEBASE.value:
                logger.info(f"[{qid}] Querying Knowledgebase: {sub_query}")
                try:
                    response_message = await self.send_message(
                        Message(content=sub_query), self.kb_agent_id
                    )
                    response = KBResponse.model_validate_json(response_message.content).dict()
                    logger.info(f"[KB] Agent Response : {response}")
                except Exception as e:
                    logger.error(f"[KB] Error: {e}")
                    raise ExternalServiceError(
                        message=f"Knowledge base query failed: {str(e)}",
                        service=SourceType.KNOWLEDGEBASE.value,
                        details={"sub_query": sub_query, "original_error": str(e)}
                    )

            elif source == SourceType.NOTION.value:
                logger.info(f"[{qid}] Querying Notion")
                try:
                    prompt = NOTION_QUERY_PROMPT.format(sub_query=sub_query)
                    response_message = await self.send_message(
                        Message(content=prompt), self.notion_workbench_agent_id
                    )
                    response = json.loads(response_message.content)
                    logger.info(f"[Notion] Agent Response : {response}")
                    try:
                        cleaner_response = await self.send_message(
                            Message(content=json.dumps(response.get("answer", ""))), self.answer_cleaner_agent_id
                        )
                        cleaned_payload = json.loads(cleaner_response.content)
                        cleaned_answer = cleaned_payload.get("cleaned_answer", response.get("answer", ""))
                        response["answer"] = cleaned_answer
                    except Exception as cleaning_error:
                        logger.warning(f"[Notion] Failed to clean answer, using raw: {cleaning_error}")
                except Exception as e:
                    logger.error(f"[Notion] Error: {e}")
                    raise ExternalServiceError(
                        message=f"Notion query failed: {str(e)}",
                        service=SourceType.NOTION.value,
                        details={"sub_query": sub_query, "original_error": str(e)}
                    )

            elif source == SourceType.WEBSEARCH.value:
                logger.info(f"[{qid}] Querying WebRAG")
                try:
                    response_message = await self.send_message(
                        Message(content=sub_query), self.webrag_agent_id
                    )
                    response = json.loads(response_message.content)
                    logger.info(f"[WebSearch] Agent Response : {response}")
                except Exception as e:
                    logger.error(f"[WebSearch] Error: {e}")
                    raise ExternalServiceError(
                        message=f"Web search failed: {str(e)}",
                        service=SourceType.WEBSEARCH.value,
                        details={"sub_query": sub_query, "original_error": str(e)}
                    )

            elif source == SourceType.GITHUB.value:
                logger.info(f"[{qid}] Querying GitHub")
                try:
                    prompt = GITHUB_PROMPT.format(sub_query=sub_query)
                    response_message = await self.send_message(
                        Message(content=prompt), self.github_workbench_agent_id
                    )
                    response = json.loads(response_message.content)
                    logger.info(f"[GitHub] Agent Response : {response}")
                    try:
                        cleaner_response = await self.send_message(
                            Message(content=json.dumps(response)), self.answer_cleaner_agent_id
                        )
                        cleaned_payload = json.loads(cleaner_response.content)
                        cleaned_answer = cleaned_payload.get("cleaned_answer", response.get("answer", ""))
                        response["answer"] = cleaned_answer
                    except Exception as cleaning_error:
                        logger.warning(f"[GitHub] Failed to clean answer, using raw: {cleaning_error}")
                except Exception as e:
                    logger.error(f"[GitHub] Error: {e}")
                    raise ExternalServiceError(
                        message=f"GitHub query failed: {str(e)}",
                        service=SourceType.GITHUB.value,
                        details={"sub_query": sub_query, "original_error": str(e)}
                    )

            else:
                raise ValidationError(
                    message=f"Unknown source: {source}",
                    field="source",
                    details={"available_sources": [s.value for s in SourceType]}
                )

            if "sources" in response:
                self._append_sources(source, response["sources"])
            if "metadata" in response:
                self._append_metadata(source, response["metadata"])

            return response

        except AgentServiceException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.exception(f"Error during execution of sub-query {qid} - {e}")
            raise ExecutionError(
                message=f"Failed to execute query from {source}: {str(e)}",
                source=source,
                details={"qid": qid, "sub_query": sub_query, "original_error": str(e)}
            )

    async def _combine_answer_from_sources(
        self, user_query: str, results: Dict[str, Any], strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            prompt = generate_aggregated_answer.format(
                user_query=user_query, results=results, strategy=strategy
            )

            logger.info(f"[Executor] Sending aggregation prompt to model : {prompt}")
            
            # Add timeout for LLM call
            import asyncio
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.chat.completions.create,
                        messages=[{"role": "user", "content": prompt}],
                        model=self.model
                    ),
                    timeout=60  # 1 minute timeout for LLM call
                )
            except asyncio.TimeoutError:
                raise TimeoutError(
                    message="LLM aggregation request timed out",
                    timeout_seconds=60,
                    details={"user_query": user_query, "strategy": strategy}
                )

            # Track token usage
            token_usage = token_tracker.track_completion("executor_agent", response, self.model)

            content = response.choices[0].message.content

            try:
                result = extract_json_with_regex(content)
                logger.info(
                    f"Extracted and parsed aggregated answer successfully : {result}"
                )

                # Create LLMUsage object if token usage is available
                llm_usage_obj = None
                if token_usage:
                    llm_usage_obj = LLMUsage(
                        model=token_usage.model,
                        input_tokens=token_usage.input_tokens,
                        output_tokens=token_usage.output_tokens,
                        total_tokens=token_usage.total_tokens
                    )

                return {
                    "executor_answer": result["answer"],

                    "llm_usage": llm_usage_obj.model_dump() if llm_usage_obj else None,
                }
            except Exception as e:
                logger.error(f"Failed to parse structured JSON: {e}")

                # Create LLMUsage object if token usage is available
                llm_usage_obj = None
                if token_usage:
                    llm_usage_obj = LLMUsage(
                        model=token_usage.model,
                        input_tokens=token_usage.input_tokens,
                        output_tokens=token_usage.output_tokens,
                        total_tokens=token_usage.total_tokens
                    )

                return {
                    "executor_answer": content,

                    "llm_usage": llm_usage_obj.model_dump() if llm_usage_obj else None,
                }

        except AgentServiceException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Error in answer aggregation: {e}")
            raise ExecutionError(
                message=f"Failed to combine answers from sources: {str(e)}",
                details={"user_query": user_query, "strategy": strategy, "original_error": str(e)}
            )

    def _append_sources(self, source, docs):
        self._sources_documents.setdefault(source, []).extend(docs)

    def _append_metadata(self, source, meta):
        if isinstance(meta, dict): meta = [meta]
        if isinstance(meta, list):
            self._sources_metadata.setdefault(source, []).extend(meta)