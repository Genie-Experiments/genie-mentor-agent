# Standard library imports
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Third-party imports
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Local application imports
from ..schemas.planner_schema import QueryPlan
from .message import Message

persist_path = os.getenv('CHROMA_DB_PATH')

class PlannerAgent(RoutedAgent):
    def __init__(self, refiner_agent_id: AgentId) -> None:
        super().__init__('planner_agent')
        self.refiner_agent_id = refiner_agent_id
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-4o',
            api_key=os.getenv('OPENAI_API_KEY')
        )

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        try:
            # Generate the plan
            plan = await self.process_query(message.content)
            plan_dict = json.loads(plan.content)
            
            # Send the plan to query agent and get results
            query_result = await self.send_message(plan, self.refiner_agent_id)
            
            # Debug print
            print(f'[DEBUG] Query result content: {query_result.content}')
            
            # Try to parse query result
            try:
                query_dict = json.loads(query_result.content)
                # Add execution results to plan
                plan_dict['execution_results'] = {
                    'answer': query_dict['aggregated_results'],
                    'confidence_score': query_dict['confidence_score']
                }
            except json.JSONDecodeError:
                print(f'[WARNING] Failed to parse query result as JSON: {query_result.content}')
                plan_dict['execution_results'] = {
                    'answer': query_result.content,
                    'confidence_score': 0
                }
            
            return Message(content=json.dumps(plan_dict))
        except Exception as e:
            print(f'[ERROR] Error in handle_user_message: {str(e)}')
            # Return error in a structured format
            error_response = {
                'error': str(e),
                'plan': plan_dict if 'plan_dict' in locals() else None,
                'query_result': query_result.content if 'query_result' in locals() else None
            }
            return Message(content=json.dumps(error_response))

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

    async def process_query(self, query: str) -> Message:
        selected_sources = self.determine_data_sources(query)

        prompt = f'''
You are a Planner Agent responsible for generating a structured query plan based on the user's input.

User Query: "{query}"

Define query intent using 2–3 words.
Use only the following data sources: {selected_sources}

Provide a JSON object with the following structure:
{{
  "user_query": "...",
  "query_intent": "...",
  "data_sources": ["knowledgebase", "notion"],
  "query_components": [
    {{
      "id": "q1",
      "sub_query": "...",
      "source": "knowledgebase"
    }},
    {{
      "id": "q2",
      "sub_query": "...",
      "source": "notion"
    }}
  ],
  "execution_order": {{
    "nodes": ["q1", "q2"],
    "edges": [],
    "aggregation": "combine_and_summarize"
  }}
}}

Ensure the JSON is properly formatted.
'''
        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source='user')],
            json_output=QueryPlan
        )
        return Message(content=response.content)