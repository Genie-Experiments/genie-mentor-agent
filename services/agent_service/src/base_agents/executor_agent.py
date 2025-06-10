import json
import os
from typing import Any, Dict,Optional
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from groq import Groq
from autogen_core.models import UserMessage

from ..prompts.prompts import GITHUB_QUERY_PROMPT, NOTION_QUERY_PROMPT, SHORT_GITHUB_PROMPT
from ..protocols.message import Message
from ..prompts.aggregation_prompt import generate_aggregated_answer
from ..utils.parsing import _extract_json_with_regex, extract_json_with_brace_counting

from ..utils.logging import setup_logger, get_logger

setup_logger()
logger = get_logger("ExecutorAgent")


class ExecutorAgent(RoutedAgent):
    def __init__(self, notion_workbench_agent_id: AgentId, 
                 github_workbench_agent_id: AgentId, 
                 webrag_agent_id: AgentId,
                 kb_agent_id:AgentId) -> None:
        super().__init__("executor_agent")
        self.notion_workbench_agent_id = notion_workbench_agent_id
        self.github_workbench_agent_id = github_workbench_agent_id
        self.webrag_agent_id = webrag_agent_id
        self.kb_agent_id = kb_agent_id
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    @message_handler
    async def handle_query_plan(self, message: Message, ctx: MessageContext) -> Message:
        try:
            content = json.loads(message.content)
            plan = content.get('plan', content)  # Handle both direct plan and wrapped plan

            query_components = {q["id"]: q for q in plan["query_components"]}
            execution_order = plan["execution_order"]
            self._sources_used = []
            self._sources_documents = {}
            self._sources_metadata = {}
            results = {}

            for qid in execution_order["nodes"]:
                logger.info(f"Executing query ID: {qid}")
                result = await self.execute_query(qid, query_components)
                results[qid] = result
                

            if len(execution_order["nodes"]) == 1:
                single_result = results[execution_order["nodes"][0]]

                return Message(content=json.dumps({
                    "combined_answer_of_sources": single_result["answer"],
                    "all_documents": [
                        doc for docs in self._sources_documents.values() for doc in docs
                    ],
                    "documents_by_source": self._sources_documents,
                    "metadata_by_source": self._sources_metadata,
                    "error": None
                }))


            logger.info("Combining answers from all data sources.")
            combined_execution_results = await self._combine_answer_from_sources(
                plan["user_query"],
                results,
                strategy=execution_order.get("aggregation")
            )

            
            all_documents = [
                doc 
                for docs in self._sources_documents.values() 
                for doc in docs
            ]

            logger.info("Returning combined results.")
            return Message(content=json.dumps({
                "combined_answer_of_sources": combined_execution_results["combined_answer_of_sources"],
                "all_documents": all_documents,
                "documents_by_source": self._sources_documents,
                "metadata_by_source": self._sources_metadata,
                "error": None
            }))


        except Exception as e:
            logger.error("Error while executing query plan : {e}")
            return Message(content=json.dumps({"error": str(e)}))

    
    async def execute_query(self, qid: str, query_components: Dict[str, Any]) -> Dict[str, Any]:
        q = query_components[qid]
        sub_query = q["sub_query"]
        source = q.get("source")  

        logger.info(f"Executing sub-query from source: {source}")
       
        try:
            
            if source == "knowledgebase":
                
                logger.info(f"[{qid}] Querying Knowledgebase: {sub_query}")
                response_message = await self.send_message(
                    Message(content=sub_query),
                    self.kb_agent_id
                )
                response = json.loads(response_message.content)
                logger.info(f"[KB] Agent Response : {response}")

            
            elif source == "notion":
                logger.info(f"[{qid}] Querying Notion")
              
                prompt = NOTION_QUERY_PROMPT.format(sub_query=sub_query)
                response_message = await self.send_message(
                    Message(content=prompt),
                    self.notion_workbench_agent_id
                )
                try:
                    response = extract_json_with_brace_counting(response_message.content.strip())
                except Exception as e:
                    logger.warning(f"Failed to parse structured JSON from GitHub response: {e}")
                    response = {
                        "answer": response_message.content.strip(),
                        "sources": []
                    }
              

            elif source == "websearch":
              
                logger.info(f"[{qid}] Querying WebRAG")
                response_message = await self.send_message(
                    Message(content=sub_query),
                    self.webrag_agent_id
                )
                response = json.loads(response_message.content)
                logger.info(f"[WebSearch] Agent Response : {response}")
                

            elif source == "github":
                
                logger.info(f"[{qid}] Querying GitHub")
                
                prompt = SHORT_GITHUB_PROMPT.format(sub_query=sub_query)
                response_message = await self.send_message(
                    Message(content=prompt),
                    self.github_workbench_agent_id
                )
                try:
                    response = extract_json_with_brace_counting(response_message.content.strip())
                except Exception as e:
                    logger.warning(f"Failed to parse structured JSON from GitHub response: {e}")
                    response = {
                        "answer": response_message.content.strip(),
                        "sources": []
                    }
                

            else:
                raise ValueError(f"Unknown source: {source}")

            
            if "sources" in response:
                source_docs = response["sources"]
                
                if source not in self._sources_documents:
                    self._sources_documents[source] = []
                
                self._sources_documents[source].extend(source_docs)


            if "metadata" in response:
                source_meta = response["metadata"]
                if source not in self._sources_metadata:
                    self._sources_metadata[source] = []
                self._sources_metadata[source].extend(source_meta)
           
            
            return response

        except Exception as e:
            logger.exception(f"Error during execution of sub-query {qid} - {e}")
            raise


    async def _combine_answer_from_sources(self, user_query: str, results: Dict[str, Any], strategy: Optional[str] = None) -> Dict[str, Any]:
        prompt = generate_aggregated_answer.format(
            user_query=user_query,
            results=results,
            strategy=strategy
        )

        logger.info(f"[Executor] Sending aggregation prompt to model : {prompt}")
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model
        )

        content = response.choices[0].message.content

        try:
            result = _extract_json_with_regex(content)
            logger.info(f"Extracted and parsed aggregated answer successfully : {result}")
            return {
                "combined_answer_of_sources": result["answer"],
            }
        except Exception as e:
            logger.error(f"Failed to parse structured JSON: {e}")
            return {
                "combined_answer_of_sources": content,
            }