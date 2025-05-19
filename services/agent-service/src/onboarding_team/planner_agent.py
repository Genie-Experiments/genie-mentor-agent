import os
import sys
import asyncio
from typing import List
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Add the path to the 'schemas' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agent-service', 'src')))
from ..schemas.planner_schema import QueryPlan
from .message import Message
persist_path = os.getenv("CHROMA_DB_PATH")

class PlannerAgent(RoutedAgent):
    def __init__(self, query_agent_id):
        super().__init__("planner_agent")
        self.query_agent_id = query_agent_id
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        plan =  await self.process_query(message.content)
        result = await self.send_message(plan, self.query_agent_id)

        return result

    def determine_data_sources(self, query: str) -> List[str]:
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        persist_path = os.getenv("CHROMA_DB_PATH")
        print(f"[DEBUG] CHROMA_DB_PATH used = {persist_path}")
        kb_store = Chroma(
            persist_directory=persist_path,
            embedding_function=embedding_model
        )
        print("[DEBUG] Chroma loaded docs:", kb_store._collection.count())

        results = kb_store.similarity_search_with_score(query, k=3)
        scores = [1 / (1 + score) for _, score in results if score is not None]
        kb_score = max(scores) if scores else 0.0


        print("\n[DEBUG] Top matching KB documents:")
        for i, (doc, score) in enumerate(results):
            print(f"KB Match {i+1}: ({score:.3f}) {doc.page_content}...\n")
        print(f"[DEBUG] Knowledgebase similarity score: {kb_score:.3f}")

        # Mock Notion scores (TF-IDF)
        notion_docs = ["project roadmap", "meeting notes", "internal OKRs", "release timeline"]
        notion_vectorizer = TfidfVectorizer().fit_transform([query] + notion_docs)
        notion_score = cosine_similarity(notion_vectorizer[0:1], notion_vectorizer[1:]).mean()
        print(f"[DEBUG] Notion similarity score: {notion_score:.3f}")

        sources = []
        if kb_score >= 0.5:
            sources.append("knowledgebase")
        if notion_score >= 0.5:
            sources.append("notion")

        if not sources:
            return ["knowledgebase" if kb_score > notion_score else "notion"]

        return sources


    async def process_query(self, query: str) -> Message:
        selected_sources = self.determine_data_sources(query)

        prompt = f"""
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
"""
        response = await self.model_client.create(
            messages=[UserMessage(content=prompt, source="user")],
            json_output=QueryPlan
        )
        return Message(content=response.content)