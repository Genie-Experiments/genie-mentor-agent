import json
import os
from enum import Enum
from typing import Any, Dict, Optional

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from openai import OpenAI

from ..prompts.aggregation_prompt import generate_aggregated_answer
from ..prompts.prompts import GITHUB_PROMPT
from ..protocols.message import Message
from ..protocols.schemas import KBResponse, LLMUsage
from ..utils.exceptions import (AgentServiceException, ExecutionError,
                                ExternalServiceError, NetworkError,
                                TimeoutError, ValidationError,
                                handle_agent_error)
from ..utils.logging import get_logger, setup_logger
from ..utils.parsing import extract_json_with_regex, strip_markdown_code_fence, escape_unescaped_newlines_in_json_strings
from ..utils.settings import settings, create_llm_client
from ..utils.token_tracker import token_tracker

setup_logger()
logger = get_logger("ExecutorAgent")

class SourceType(Enum):
    KNOWLEDGEBASE = "knowledgebase"
    GITHUB = "github"
    WEBSEARCH = "websearch"

class ExecutorAgent(RoutedAgent):
    def __init__(
        self,
        github_workbench_agent_id: AgentId,
        webrag_agent_id: AgentId,
        kb_agent_id: AgentId,
        answer_cleaner_agent_id: AgentId,
    ) -> None:
        super().__init__("executor_agent")
        self.github_workbench_agent_id = github_workbench_agent_id
        self.webrag_agent_id = webrag_agent_id
        self.kb_agent_id = kb_agent_id
        self.answer_cleaner_agent_id = answer_cleaner_agent_id
        
        # Validate API key
        if not settings.GROQ_API_KEY_EXECUTOR:
            raise ValidationError(
                message="GROQ_API_KEY is required for ExecutorAgent",
                field="GROQ_API_KEY_EXECUTOR"
            )
        
        self.client, self.model = create_llm_client("executor")

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
        import time
        start_time = time.time()
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

            # Handle greeting plan
            if plan.get("is_greeting"):
                return Message(content=json.dumps({
                    "combined_answer_of_sources": "Hello! How can I assist you today?",
                    "executor_answer": "Hello! How can I assist you today?",
                    "all_documents": [],
                    "documents_by_source": {},
                    "metadata_by_source": {},
                    "error": None,
                    "llm_usage": None
                }))

            query_components = {q["id"]: q for q in plan["query_components"]}
            execution_order = plan["execution_order"]
            self._sources_used = []
            self._sources_documents = {}
            self._sources_metadata = {}
            results = {}

            for qid in execution_order["nodes"]:
                logger.info(f"Executing query ID: {qid}")
                try:
                    # Pass plan and results to execute_query for dependency handling
                    result = await self.execute_query(qid, query_components, plan, results)
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
                if source_type in {SourceType.GITHUB.value}:
                    # For GitHub we don't require sources to be present.
                    valid_results[qid] = res
                    # Ensure we have entries so downstream aggregation doesn't fail.
                    if source_type not in self._sources_documents:
                        self._sources_documents[source_type] = res.get("sources", []) or []
                    if source_type not in self._sources_metadata:
                        self._sources_metadata[source_type] = res.get("metadata", {}) or {}
                else:
                    # For other sources require at least one source document.
                    if res.get("sources"):
                        valid_results[qid] = res

            if len(valid_results) == 1:
                only_result = list(valid_results.values())[0]
                logger.info("Only one valid source present. Skipping aggregation, proceeding with single valid result.")
                execution_time_ms = int((time.time() - start_time) * 1000)

                # Extract optional KB trace
                kb_trace = only_result.get("trace") or None
                kb_num_hops = only_result.get("num_hops") or None

                payload = {
                    "combined_answer_of_sources": only_result["answer"],
                    "executor_answer": only_result["answer"],
                    "all_documents": [
                        doc for docs in self._sources_documents.values() for doc in docs
                    ],
                    "documents_by_source": self._sources_documents,
                    "metadata_by_source": self._sources_metadata,
                    "error": None,
                    "llm_usage": None,
                    "execution_time_ms": execution_time_ms,
                }

                if kb_trace:
                    payload["trace"] = kb_trace
                if kb_num_hops:
                    payload["num_hops"] = kb_num_hops

                return Message(content=json.dumps(payload))

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
                combined_execution_results = await self._combine_answer_from_sources(
                    plan["user_query"],
                    valid_results,
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
            execution_time_ms = int((time.time() - start_time) * 1000)
            return Message(
                content=json.dumps(
                    {
                        "combined_answer_of_sources": combined_execution_results[
                            "combined_answer_of_sources"
                        ],
                        "executor_answer": combined_execution_results[
                            "combined_answer_of_sources"
                        ],
                        "all_documents": all_documents,
                        "documents_by_source": self._sources_documents,
                        "metadata_by_source": self._sources_metadata,
                        "error": None,
                        "llm_usage": combined_execution_results.get("llm_usage"),
                        "execution_time_ms": execution_time_ms
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
        self, qid: str, query_components: Dict[str, Any], plan: dict = None, results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        q = query_components[qid]
        sub_query = q["sub_query"]
        source = q.get("source")

        logger.info(f"Executing sub-query from source: {source}")

        # Handle dependencies - if this query depends on others, append their answers
        dependency_context = ""
        workflow_steps = plan.get("execution_order", {}).get("workflow", [])
        current_step = None

        logger.info(f"[{qid}] Checking for dependencies from workflow steps: {workflow_steps}")

        # Find the current step in workflow
        for step in workflow_steps:
            if step.get("query_id") == qid:
                current_step = step
                break

        if current_step and current_step.get("dependencies") and results:
            logger.info(f"[{qid}] Found dependencies: {current_step.get('dependencies')}")

            dependency_answers = []
            step_dependencies = current_step.get("dependencies", [])

            for step_dep in step_dependencies:
                # Find the query_id for this step dependency
                dep_query_id = None
                for step in workflow_steps:
                    if step.get("step_id") == step_dep:
                        dep_query_id = step.get("query_id")
                        break

                # Get the result for the dependent query
                if dep_query_id and dep_query_id in results and results[dep_query_id].get("answer"):
                    dep_answer = results[dep_query_id]["answer"]
                    # Ensure the answer is a string
                    if not isinstance(dep_answer, str):
                        dep_answer = str(dep_answer)
                    dependency_answers.append(
                        f"Context from {step_dep} ({dep_query_id}): {dep_answer}")

            if dependency_answers:
                dependency_context = "\n\nContext from previous sources:\n" + \
                    "\n".join(dependency_answers) + \
                    "\n\nBased on the above context, please provide a comprehensive answer to: "
                sub_query = dependency_context + sub_query
                logger.info(f"[{qid}] Enhanced sub-query with dependency context from steps: {step_dependencies}")
                logger.info(f"[{qid}] Modified sub-query to: {sub_query}")

        try:
            # Use enum for all source checks
            if source == SourceType.KNOWLEDGEBASE.value:
                # Use sub_query for knowledgebase (not main user query)
                logger.info(f"[{qid}] Querying Knowledgebase with sub_query: {sub_query}")
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
                source_docs = response["sources"]

                if source not in self._sources_documents:
                    self._sources_documents[source] = []

                self._sources_documents[source].extend(source_docs)

            if "metadata" in response:
                source_meta = response["metadata"]
                # Normalize to list of dicts
                if isinstance(source_meta, dict):
                    source_meta = [source_meta]
                elif not isinstance(source_meta, list):
                    source_meta = []
                if source not in self._sources_metadata:
                    self._sources_metadata[source] = []
                self._sources_metadata[source].extend(source_meta)

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

    def _fallback_aggregation(self, user_query: str, results: Dict[str, Any], strategy: Optional[str] = None) -> Dict[str, Any]:
        """Fallback aggregation when LLM aggregation fails or times out."""
        logger.info("Using fallback aggregation due to LLM failure")
        
        if not results:
            return {"combined_answer_of_sources": "No valid results to combine"}
        
        # Strategy 1: Use the first valid result
        if strategy == "single_source" or len(results) == 1:
            first_result = list(results.values())[0]
            answer = first_result.get("answer", "No answer available")
            # Ensure answer is a valid string
            if not isinstance(answer, str):
                answer = str(answer) if answer is not None else "No answer available"
            return {"combined_answer_of_sources": answer}
        
        # Strategy 2: Simple concatenation of answers
        answers = []
        for qid, result in results.items():
            answer = result.get("answer", "")
            if answer and answer.strip():
                # Ensure each answer is a valid string
                if not isinstance(answer, str):
                    answer = str(answer)
                answers.append(f"[Source {qid}]: {answer}")
        
        if answers:
            combined = "\n\n".join(answers)
            return {"combined_answer_of_sources": combined}
        else:
            return {"combined_answer_of_sources": "No valid answers found in any source"}

    async def _combine_answer_from_sources(
        self, user_query: str, results: Dict[str, Any], strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            # Filter out unnecessary fields that cause token limit issues
            filtered_results = {}
            for qid, result in results.items():
                filtered_result = {
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "metadata": result.get("metadata", []),
                    "error": result.get("error")
                }
                # Only include essential fields, exclude trace, global_summary, local_summary
                filtered_results[qid] = filtered_result
            
            prompt = generate_aggregated_answer.format(
                user_query=user_query, results=filtered_results, strategy=strategy
            )

            logger.info(f"[Executor] Sending aggregation prompt to model (filtered out trace/summaries to prevent token limits)")
            
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
                logger.error("LLM aggregation request timed out, using fallback")
                return self._fallback_aggregation(user_query, results, strategy)
            except Exception as e:
                logger.error(f"LLM call failed: {e}, using fallback")
                return self._fallback_aggregation(user_query, results, strategy)

            # Track token usage
            token_usage = token_tracker.track_completion("executor_agent", response, self.model)

            content = response.choices[0].message.content
            if not content or not content.strip():
                logger.error("LLM returned empty content, using fallback")
                return self._fallback_aggregation(user_query, results, strategy)

            try:
                # Clean LLM output of markdown code fences before parsing
                content_clean = strip_markdown_code_fence(content)
                content_clean = escape_unescaped_newlines_in_json_strings(content_clean)
                
                logger.debug(f"[Executor] Attempting to parse cleaned content: {content_clean[:500]}...")
                
                result = extract_json_with_regex(content_clean)
                logger.info(
                    f"Extracted and parsed aggregated answer successfully : {result}"
                )
                
                # Validate that result has the expected structure
                if not isinstance(result, dict):
                    raise ValueError(f"Expected dict result, got {type(result)}")
                
                if "answer" not in result:
                    logger.warning("LLM response missing 'answer' field, using raw content")
                    result["answer"] = content
                
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
                    "combined_answer_of_sources": result["answer"],
                    "llm_usage": llm_usage_obj.model_dump() if llm_usage_obj else None,
                }
            except Exception as e:
                logger.error(f"Failed to parse structured JSON: {e}")
                logger.error(f"Raw LLM output that failed to parse: {content}")
                
                # Try alternative parsing method
                try:
                    logger.info("Attempting alternative parsing with safe_json_parse")
                    from ..utils.parsing import safe_json_parse
                    result = safe_json_parse(content)
                    
                    if isinstance(result, dict) and "answer" in result:
                        answer = result["answer"]
                    else:
                        answer = content
                        
                except Exception as fallback_error:
                    logger.error(f"Fallback parsing also failed: {fallback_error}")
                    answer = content
                
                # Create LLMUsage object if token usage is available
                llm_usage_obj = None
                if token_usage:
                    llm_usage_obj = LLMUsage(
                        model=token_usage.model,
                        input_tokens=token_usage.input_tokens,
                        output_tokens=token_usage.output_tokens,
                        total_tokens=token_usage.total_tokens
                    )
                
                # Ensure answer is a valid string
                if not isinstance(answer, str):
                    answer = str(answer) if answer is not None else "Error: Invalid response format"
                
                return {
                    "combined_answer_of_sources": answer,
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
