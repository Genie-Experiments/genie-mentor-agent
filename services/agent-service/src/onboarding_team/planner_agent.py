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
#rom langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Local application imports
from ..schemas.planner_schema import QueryPlan
from .message import Message
import logging, json
logger = logging.getLogger("pipeline")          
logger.setLevel(logging.INFO)    
persist_path = os.getenv('CHROMA_DB_PATH')

class PlannerAgent(RoutedAgent):
    def __init__(self, query_agent_id: AgentId) -> None:
        super().__init__('planner_agent')
        self.query_agent_id = query_agent_id
        self.evaluation_agent_id = AgentId('evaluation_agent', 'default')
        self.editor_agent_id = AgentId('editor_agent', 'default')
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-4o',
            api_key=os.getenv('OPENAI_API_KEY')
        )

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        try:
            
            plan_msg = await self.process_query(message.content)
            plan_content = plan_msg.content

            query_msg = await self.send_message(plan_msg, self.query_agent_id)
            query_content = query_msg.content

            final_dict = await self.process_results(
                plan_content=plan_content,
                query_result=query_content,
                context=ctx
            )
            return Message(content=json.dumps(final_dict))
            
        except Exception as e:
            print(f'[ERROR] Planner error: {str(e)}')
            return Message(content=json.dumps({
                'error': str(e),
                'verification_status': 'failed',
                'correction_attempts': 0
            }))

    async def process_results(self, plan_content: str, query_result: str, context: MessageContext) -> Dict[str, Any]:
        plan_dict = json.loads(plan_content)
        initial_answer = query_result
        initial_confidence = 0
        
        try:
            query_data = json.loads(query_result)
            initial_answer = query_data.get('aggregated_results', query_result)
            initial_confidence = query_data.get('confidence_score', 0)
        except json.JSONDecodeError:
            pass
 
        query_data = json.loads(query_result)  
        sources = []
        for comp_res in query_data.get("individual_results", {}).values():
            sources.extend(comp_res.get("sources", []))

        evaluation_payload = {
        "question":           plan_dict["user_query"],
        "context":            "\n".join(sources),     
        "answer":    query_data["aggregated_results"],
        "correction_attempt": 0
        }

        evaluation_history = []
        final_answer = initial_answer
        final_confidence = initial_confidence
        verification_status = "unverified"
        error = None
        
        try:
           
            eval_result = await self.evaluate_and_correct(
                Message(content=json.dumps(evaluation_payload)),
                context,
                evaluation_history,
                max_attempts=2
            )
            
            final_answer = eval_result.get('answer', initial_answer)
            final_confidence = eval_result.get('factual_accuracy_score', initial_confidence)
            verification_status = eval_result.get('response_verified', 'unknown')
            error = eval_result.get('error')
            
        except Exception as e:
            error = str(e)
            verification_status = "evaluation_failed"

        return {
            'execution_plan': plan_dict,
            'initial_answer': initial_answer,
            'initial_confidence': initial_confidence,
            'evaluation_history': evaluation_history,
            'correction_attempts': len([h for h in evaluation_history if h['type'] == 'correction']),
            'final_answer': final_answer,
            'confidence_score': final_confidence,
            'verification_status': verification_status,
            'error': error
        }


    async def evaluate_and_correct(
    self,
    message: Message,
    ctx: MessageContext,
    history: list,
    max_attempts: int,
) -> Dict[str, Any]:
        attempt = 0
        result: Dict[str, Any] = {}

        logger.info("Starting evaluate_and_correct (max_attempts=%d)", max_attempts)

        while attempt <= max_attempts:
            logger.info("Evaluation round %d", attempt + 1)
            eval_response = await self.send_message(message, self.evaluation_agent_id)
            result = json.loads(eval_response.content)
            logger.debug("EvaluationAgent reply:\n%s", json.dumps(result, indent=2))

            history.append(
                {
                    "type": "evaluation",
                    "attempt": attempt,
                    "score": result.get("factual_accuracy_score", 0),
                    "explanation": result.get("explanation_factual_accuracy", ""),
                    "status": result.get("response_verified", "unknown"),
                }
            )

            if result.get("response_verified") == "Correct":
                logger.info("Verified correct on attempt %d", attempt + 1)
                break
            if attempt >= max_attempts:
                logger.warning("Max attempts (%d) reached without success", max_attempts)
                break


            logger.info("Answer incorrect – sending to EditorAgent (attempt %d)", attempt + 1)

            editor_payload = {
                **json.loads(message.content),       
                **result,                             
                "correction_attempt": attempt,
            }
            logger.debug("Payload to EditorAgent:\n%s", json.dumps(editor_payload, indent=2))

            edit_response = await self.send_message(
                Message(content=json.dumps(editor_payload)),
                self.editor_agent_id,
            )
            edited_data = json.loads(edit_response.content)
            logger.debug("EditorAgent reply:\n%s", json.dumps(edited_data, indent=2))

            history.append(
                {
                    "type": "correction",
                    "attempt": attempt,
                    "answer": result.get("answer", ""),
                    "new_answer": edited_data.get("answer", ""),
                    "explanation": edited_data.get("explanation_factual_accuracy", ""),
                }
            )

            message = Message(content=edit_response.content)
            attempt += 1

        logger.info("evaluate_and_correct finished after %d attempt(s)", attempt + 1)
        return result


   
    def get_context_sources(self, plan_dict: Dict[str, Any]) -> str:
        sources = [
            f"{comp['source']}: {comp['sub_query']}"
            for comp in plan_dict.get("query_components", [])
        ]
        return "\n".join(sources)
   
    def determine_data_sources(self, query: str) -> List[str]:
        embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        
       # print(f'[DEBUG] CHROMA_DB_PATH used = {persist_path}')
        kb_store = Chroma(
            persist_directory=persist_path,
            embedding_function=embedding_model
        )
        #print('[DEBUG] Chroma loaded docs:', kb_store._collection.count())

        results = kb_store.similarity_search_with_score(query, k=3)
        scores = [1 / (1 + score) for _, score in results if score is not None]
        kb_score = max(scores) if scores else 0.0

        #print('\n[DEBUG] Top matching KB documents:')
        #for i, (doc, score) in enumerate(results):
        #    print(f'KB Match {i+1}: ({score:.3f}) {doc.page_content}...\n')
        #print(f'[DEBUG] Knowledgebase similarity score: {kb_score:.3f}')

        # Mock Notion scores (TF-IDF)
        notion_docs = ['project roadmap', 'meeting notes', 'internal OKRs', 'release timeline']
        notion_vectorizer = TfidfVectorizer().fit_transform([query] + notion_docs)
        notion_score = cosine_similarity(notion_vectorizer[0:1], notion_vectorizer[1:]).mean()
        #print(f'[DEBUG] Notion similarity score: {notion_score:.3f}')

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
        print("Response from process query")
        print(response)
        return Message(content=response.content)