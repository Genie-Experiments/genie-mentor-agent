import asyncio
import json
import logging
import os
from typing import Any, Dict, List

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..schemas.planner_schema import QueryPlan
from .message import Message

logger = logging.getLogger("pipeline")
logger.setLevel(logging.INFO)

persist_path = os.getenv("CHROMA_DB_PATH")


class PlannerAgent(RoutedAgent):
    MAX_CORRECTIONS = 2

    def __init__(self, refiner_agent_id: AgentId, query_agent_id: AgentId) -> None:
        super().__init__("planner_agent")
        self.refiner_agent_id = refiner_agent_id
        self.query_agent_id = query_agent_id
        self.evaluation_agent_id = AgentId("evaluation_agent", "default")
        self.editor_agent_id = AgentId("editor_agent", "default")

        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")
        )

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        try:
            plan_msg = await self.process_query(message.content)
            plan_dict = json.loads(plan_msg.content)

            query_msg = await self.send_message(plan_msg, self.refiner_agent_id)
            query_dict = json.loads(query_msg.content)

            # Store execution results
            plan_dict["execution_results"] = {
                "answer": query_dict.get("aggregated_results", ""),
                "confidence_score": query_dict.get("confidence_score", 0)
            }

            # Handle refiner metadata if present
            refiner_metadata = query_dict.get("refiner_metadata", {})
            plan_dict["refiner_metadata"] = {
                "refined_plan": refiner_metadata.get("refined_plan", "{}"),
                "feedback": refiner_metadata.get("feedback", ""),
                "changes_made": refiner_metadata.get("changes_made", [])
            }

            final = await self.process_results(plan_dict, query_dict, ctx)
            return Message(content=json.dumps(final))

        except Exception as exc:
            logger.exception("PlannerAgent failed:")
            return Message(
                content=json.dumps({
                    "error": str(exc),
                    "verification_status": "failed",
                    "correction_attempts": 0
                })
            )

    async def process_results(self, plan: Dict[str, Any], query: Dict[str, Any], ctx: MessageContext) -> Dict[str, Any]:
        srcs: List[str] = []
        for comp in query.get("individual_results", {}).values():
            srcs.extend(comp.get("sources", []))

        eval_payload = {
            "question": plan["user_query"],
            "context": "\n".join(srcs),
            "answer": query["aggregated_results"],
            "correction_attempt": 0,
        }

        history: List[Dict[str, Any]] = []
        attempt = 0

        while attempt <= self.MAX_CORRECTIONS:
            eval_resp = await self.send_message(Message(content=json.dumps(eval_payload)), self.evaluation_agent_id)
            eval_data = json.loads(eval_resp.content)

            history.append({
                "type": "evaluation",
                "attempt": attempt,
                "score": eval_data.get("factual_accuracy_score", 0.0),
                "status": eval_data.get("response_verified", "unknown"),
                "explanation": eval_data.get("explanation_factual_accuracy", ""),
            })

            if eval_data.get("response_verified") == "Correct":
                break

            if attempt == self.MAX_CORRECTIONS:
                break

            editor_payload = {
                **eval_payload,
                "explanation": eval_data.get("explanation_factual_accuracy", ""),
                "correction_attempt": attempt,
            }

            edit_resp = await self.send_message(Message(content=json.dumps(editor_payload)), self.editor_agent_id)
            edit_data = json.loads(edit_resp.content)

            history.append({
                "type": "correction",
                "attempt": attempt,
                "new_answer": edit_data["answer"],
            })

            eval_payload["answer"] = edit_data["answer"]
            eval_payload["correction_attempt"] += 1
            attempt += 1

        return {
            "execution_plan": plan,
            "initial_answer": {
                "content": query["aggregated_results"],
                "confidence": query["confidence_score"],
            },
            "evaluation_history": history,
            "correction_attempts": attempt,
            "final_answer": {
                "content": eval_payload["answer"],
                "confidence": eval_data.get("factual_accuracy_score", 0.0),
                "verification_status": eval_data.get("response_verified", "unknown"),
            },
        }

    def determine_data_sources(self, user_query: str) -> List[str]:
        embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        kb = Chroma(persist_directory=persist_path, embedding_function=embedder)

        kb_hits = kb.similarity_search_with_score(user_query, k=3)
        kb_score = max((1 / (1 + s) for _, s in kb_hits), default=0.0)

        dummy_docs = ["project roadmap", "meeting notes", "internal OKRs", "release"]
        tfidf = TfidfVectorizer().fit_transform([user_query] + dummy_docs)
        notion_score = cosine_similarity(tfidf[0:1], tfidf[1:]).mean()

        sources: List[str] = []
        if kb_score >= 0.5:
            sources.append("knowledgebase")
        if notion_score >= 0.5:
            sources.append("notion")
        if not sources:
            sources.append("knowledgebase" if kb_score >= notion_score else "notion")
        return sources

    async def process_query(self, user_query: str) -> Message:
        sources = self.determine_data_sources(user_query)

        prompt = f"""
You are a Planner Agent. Build a JSON plan for the user's query.

User Query: "{user_query}"
Use only these sources: {sources}

Return JSON matching this schema:

{{
  "user_query": "...",
  "query_intent": "...",
  "data_sources": [...],
  "query_components": [
    {{ "id": "q1", "sub_query": "...", "source": "knowledgebase" }},
    ...
  ],
  "execution_order": {{
      "nodes": ["q1", "q2"],
      "edges": [],
      "aggregation": "combine_and_summarize"
  }}
}}
"""
        llm_resp = await self.model_client.create(
            messages=[UserMessage(content=prompt, source="user")],
            json_output=QueryPlan,
        )
        return Message(content=llm_resp.content)
