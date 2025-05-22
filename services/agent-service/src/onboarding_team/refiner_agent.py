# Standard library imports
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Third-party imports
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import ValidationError
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Local application imports
from ..schemas.planner_schema import QueryPlan
from .message import Message, RefinerOutput


class RefinerAgent(RoutedAgent):
    def __init__(self, query_agent_id: AgentId) -> None:
        super().__init__('refiner_agent')
        self.query_agent_id = query_agent_id
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-4o',
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def determine_data_sources(self, query: str) -> List[str]:
        embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        persist_path = os.getenv('CHROMA_DB_PATH')
        print(f'[DEBUG] CHROMA_DB_PATH used = {persist_path}')
        kb_store = Chroma(
            persist_directory=persist_path,
            embedding_function=embedding_model
        )
        print('[DEBUG] Chroma loaded docs:', kb_store._collection.count())

        results = kb_store.similarity_search_with_score(query, k=3)
        scores = [1 / (1 + score) for _, score in results if score is not None]
        kb_score = max(scores) if scores else 0.0

        print('\n[DEBUG] Top matching KB documents:')
        for i, (doc, score) in enumerate(results):
            print(f'KB Match {i+1}: ({score:.3f}) {doc.page_content}...\n')
        print(f'[DEBUG] Knowledgebase similarity score: {kb_score:.3f}')

        # Mock Notion scores (TF-IDF)
        notion_docs = ['project roadmap', 'meeting notes', 'internal OKRs', 'release timeline']
        notion_vectorizer = TfidfVectorizer().fit_transform([query] + notion_docs)
        notion_score = cosine_similarity(notion_vectorizer[0:1], notion_vectorizer[1:]).mean()
        print(f'[DEBUG] Notion similarity score: {notion_score:.3f}')

        sources = []
        if kb_score >= 0.5:
            sources.append('knowledgebase')
        if notion_score >= 0.5:
            sources.append('notion')

        if not sources:
            return ['knowledgebase' if kb_score > notion_score else 'notion']

        return sources

    @message_handler
    async def handle_plan_message(self, message: Message, ctx: MessageContext) -> Message:
        # Step 1: Validate incoming JSON
        try:
            parsed_plan = QueryPlan.model_validate_json(message.content)
        except ValidationError as e:
            error_msg = f"Invalid QueryPlan format: {e}"
            print("[ERROR]", error_msg)
            return Message(content=json.dumps({"error": error_msg}))

        # Step 2: Determine if refinement is needed
        refinement_needed = await self.check_if_refinement_needed(message.content)
        if refinement_needed:
            print("[INFO] Refinement needed. Proceeding to refine.")
            raw_str = await self.refine_plan(message.content)
            result = RefinerOutput.model_validate_json(raw_str)
        else:
            print("[INFO] No refinement needed.")
            result = RefinerOutput(
                refined_plan=message.content,
                feedback="No changes needed.",
                original_plan=message.content,
                changes_made=["No changes required"]
            )
        
        print(f"[DEBUG] Refined plan: {result.refined_plan}")
        
        # Step 3: Forward to Query Agent with both original and refined plan
        response = await self.send_message(
            Message(content=json.dumps({
                "refined_plan": result.refined_plan,
                "original_plan": result.original_plan,
                "feedback": result.feedback,
                "changes_made": result.changes_made
            })),
            self.query_agent_id
        )

        return response

    async def check_if_refinement_needed(self, plan_json: str) -> bool:
        prompt = f"""
        You are a refinement detector. A query plan is given below.
        
        Determine whether it needs refinement in terms of:
        - redundant or missing data sources (only use 'knowledgebase' or 'notion')
        - ambiguous execution order
        - unclear intent or subqueries
        - inappropriate aggregation strategy
        
        Plan:
        {plan_json}
        
        Respond with one word only: "Yes" or "No"
        """
        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source="planner_agent")],
        )
        content = response.content.strip().lower()
        return content.startswith("yes")

    async def refine_plan(self, plan_json: str) -> RefinerOutput:
        # Parse the plan to get the user query
        plan = json.loads(plan_json)
        user_query = plan["user_query"]
        
        # Determine appropriate data sources
        selected_sources = self.determine_data_sources(user_query)
        
        prompt = f"""
        You are a Refiner Agent responsible for reviewing and optimizing a query plan generated by another agent.
        
        Here is the input plan (as JSON):
        {plan_json}
        
        Available data sources: {selected_sources}
        
        Check for:
        - redundant sources (only use the available sources listed above)
        - poor execution ordering
        - missing query components
        - ambiguous subqueries or intent
        - better aggregation strategies
        
        Important: Only use the available data sources listed above. Do not introduce any other sources.
        
        Reply with a JSON object:
        {{
          "refined_plan": <refined JSON query plan>,
          "feedback": <what was changed and why; or 'No changes needed.'>,
          "original_plan": <original plan JSON>,
          "changes_made": [<list of specific changes made>]
        }}
        """
        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source="planner_agent")],
            json_output=RefinerOutput
        )
        return response.content