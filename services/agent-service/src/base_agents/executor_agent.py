import json
import os
from typing import Any, Dict,Optional
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage

from ..prompts.prompts import GITHUB_QUERY_PROMPT, NOTION_QUERY_PROMPT
from ..prompts.dummy_data import dummy_data_1
from ..source_agents.knowledgebaserag.knowledgebaserag import query_knowledgebase
from ..protocols.message import Message
from ..prompts.prompts import GENERATE_AGGREAGATED_ANSWER
from ..utils.parsing import _extract_json_with_regex

import logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("autogen_core").setLevel(logging.WARNING)
logging.getLogger("autogen_core.events").setLevel(logging.WARNING)



class ExecutorAgent(RoutedAgent):
    def __init__(self, notion_workbench_agent_id: AgentId, 
                 github_workbench_agent_id: AgentId, 
                 webrag_agent_id: AgentId) -> None:
        super().__init__("executor_agent")
        self.notion_workbench_agent_id = notion_workbench_agent_id
        self.github_workbench_agent_id = github_workbench_agent_id
        self.webrag_agent_id = webrag_agent_id
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )

    @message_handler
    async def handle_query_plan(self, message: Message, ctx: MessageContext) -> Message:
        try:
            content = json.loads(message.content)
            plan = json.loads(content.get('refined_plan', message.content))

            query_components = {q["id"]: q for q in plan["query_components"]}
            execution_order = plan["execution_order"]
            self._sources_used = []
            results = {}

            for qid in execution_order["nodes"]:
                logging.info(f"Executing query ID: {qid}")
                result = await self.execute_query(qid, query_components)
                results[qid] = result
                logging.info(f"Result for {qid}: {result}")

            logging.info("Combining answers from all data sources.")
            combined_execution_results = await self._combine_answer_from_sources(
                plan["user_query"],
                results,
                strategy=execution_order.get("aggregation")
            )
            web_urls = []
            for result in results.values():
                if isinstance(result, dict):
                    web_urls.extend(result.get("web_search_urls", []))
           
            logging.info("Returning combined results.")


            return Message(content=json.dumps({
                "combined_answer_of_sources": combined_execution_results["combined_answer_of_sources"],
                "top_documents": self._sources_used,
                "web_search_urls": web_urls


            }))

        except Exception as e:
            logging.exception("Error while executing query plan.")
            return Message(content=json.dumps({"error": str(e)}))

    
    async def execute_query(self, qid: str, query_components: Dict[str, Any]) -> Dict[str, Any]:
        q = query_components[qid]
        sub_query = q["sub_query"]
        source = q.get("source", "websearch")  
        source = "knowledgebase"

        logging.info(f"Executing sub-query from source: {source}")
       
        try:
            
            if source == "knowledgebase":
                logging.info(f"[{qid}] Querying Knowledgebase: {sub_query}")
                response = query_knowledgebase(sub_query)
            '''
            elif source == "notion":
                logging.info(f"[{qid}] Querying Notion")
                prompt = f"Use Notion to find relevant info: {sub_query}"
                response_message = await self.send_message(
                    Message(content=prompt),
                    self.notion_workbench_agent_id
                )
               # response = json.loads(response_message.content)

            elif source == "websearch":
                logging.info(f"[{qid}] Querying WebRAG")
                response_message = await self.send_message(
                    Message(content=sub_query),
                    self.webrag_agent_id
                )
                response = json.loads(response_message.content)

            elif source == "github":
                logging.info(f"[{qid}] Querying GitHub")
                prompt = GITHUB_QUERY_PROMPT.format(sub_query=sub_query)
                response_message = await self.send_message(
                    Message(content=prompt),
                    self.github_workbench_agent_id
                )
                #response = json.loads(response_message.content)

            else:
                raise ValueError(f"Unknown source: {source}")'''

          
            if "sources" in response:
                self._sources_used.extend(response["sources"])
            


            #if "_sources_used" in dummy_data_1:
            #  self._sources_used.extend(dummy_data_1["sources"])
           
            # return dummy_data_1
            return response

        except Exception as e:
            logging.exception(f"Error during execution of sub-query {qid} - {e}")
            raise


    async def _combine_answer_from_sources(self, user_query: str, results: Dict[str, Any], strategy: Optional[str] = None) -> Dict[str, Any]:
        prompt = GENERATE_AGGREAGATED_ANSWER.format(
            user_query=user_query,
            results=results,
            strategy=strategy
        )

        logging.info("Sending aggregation prompt to model.")
        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source=self.id.key)],
        )

        response_text = response.content.strip()

        try:
            result = _extract_json_with_regex(response_text)
            logging.info("Extracted and parsed aggregated answer successfully.")
            return {
                "combined_answer_of_sources": result["answer"],
            }
        except Exception as e:
            logging.warning(f"Failed to parse structured JSON: {e}")
            return {
                "combined_answer_of_sources": response.content,
            }