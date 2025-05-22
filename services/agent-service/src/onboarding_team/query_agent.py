# Standard library imports
import json
import os
from typing import Any, Dict, Optional

# Third-party imports
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Local application imports
from ..rag.rag import query_knowledgebase
from .message import Message


class QueryAgent(RoutedAgent):
    def __init__(self, workbench_agent_id: AgentId) -> None:
        super().__init__("query_agent")
        self.workbench_agent_id = workbench_agent_id
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        

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
        aggregated = await self.aggregate_results(
            plan["user_query"], 
            results, 
            strategy=execution_order.get("aggregation")
        )
        return Message(content=aggregated)

    async def execute_query(self, qid: str, query_components: Dict[str, Any]) -> Dict[str, Any]:
        q = query_components[qid]
        sub_query = q["sub_query"]
        source = q["source"]

        if source == "knowledgebase":
            response = await self.query_knowledgebase(sub_query)
            
        elif source == "notion":
            response = await self.send_message(
                Message(
                    content=f"Use Notion to find relevant information about the following query: {sub_query}. Retrieve key information from all the relevant pages, and based on the information retrieved, answer the user query. The answer should be detailed and include information from all the sources used. Your final response should be a json object, with an 'answer' key, which is the answer to the query based on the information fetched, and a 'sources' key"
                ), 
                self.workbench_agent_id
            )
        

        if "sources" in response:
            self._sources_used.extend(response["sources"])
        return response["answer"]

    

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

