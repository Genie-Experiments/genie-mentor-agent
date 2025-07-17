import asyncio
import json
import os
import re
from typing import Any, Dict
from autogen_core import MessageContext, RoutedAgent, message_handler
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from ..prompts.multihop_prompts import GENERATOR_PROMPT, GLOBAL_SUMMARIZER_PROMPT, LOCAL_SUMMARIZER_PROMPT, PLANNER_REASONER_PROMPT, GENIE_DOCS_TOC
from ..protocols.message import Message
from ..utils.logging import get_logger, setup_logger
from ..protocols.schemas import KBResponse

setup_logger()
logger = get_logger("KBAgent")

# Load reranker model
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-reranker-base")
reranker = AutoModelForSequenceClassification.from_pretrained(
    "BAAI/bge-reranker-base")


def rerank(query, docs):
    """Rerank documents using BGE reranker"""
    if not docs:
        return []
    pairs = [(query, doc.page_content) for doc in docs]
    inputs = tokenizer.batch_encode_plus(
        pairs, padding=True, truncation=True, return_tensors="pt"
    )
    with torch.no_grad():
        scores = reranker(**inputs).logits.squeeze()
    return [doc for _, doc in sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)]


def boost_by_metadata(query, docs):
    """Boost documents based on metadata relevance"""
    query_lower = query.lower()
    return sorted(
        docs,
        key=lambda doc: (
            query_lower in doc.metadata.get("title", "").lower() or
            query_lower in doc.metadata.get("section_title", "").lower()
        ),
        reverse=True
    )


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Get the embedding model"""
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")


def get_chroma_retriever(persist_directory, embedding_model, k=15):
    """Get Chroma retriever"""
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
    )
    return vector_store.as_retriever(search_kwargs={"k": k})


def retrieve_docs(query, retriever):
    """Retrieve documents using the retriever"""
    return retriever.invoke(query)


def parse_reasoner_json(text: str) -> dict:
    """
    Robustly extract the first {...} JSON object appearing in `text`.
    Returns {} if nothing parsable is found.
    """
    match = re.search(r'\{.*\}', text, flags=re.S)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


class KBAgent(RoutedAgent):
    def __init__(self, persist_directory: str = None):
        super().__init__("knowledgebase_agent")
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_DB_PATH")
        if not self.persist_directory:
            raise ValueError(
                "persist_directory not set and CHROMA_DB_PATH missing in .env"
            )

        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        # Initialize components
        self.embedding_model = get_embedding_model()
        self.retriever = get_chroma_retriever(
            self.persist_directory,
            self.embedding_model,
            k=15
        )
        self.llm = ChatGroq(
            temperature=0.1,
            groq_api_key=self.groq_api_key,
            model_name="meta-llama/llama-4-maverick-17b-128e-instruct"
        )

    def run_resp_pipeline(self, main_question: str, max_hops: int = 5) -> Dict[str, Any]:
        """Run the ReSP (Retrieval-enhanced Summarization Pipeline) for multi-hop reasoning"""
        global_memory = []
        local_memory = []
        all_sub_questions = []  # Flat list of all sub-questions ever asked
        hops_trace = []
        hop = 0

        # --- First hop: always answer the main question ---
        hop += 1
        hop_info = {"hop": hop, "sub_questions": []}

        # Retrieve and summarize for main question
        docs = retrieve_docs(main_question, self.retriever)
        docs = rerank(main_question, docs)
        docs = boost_by_metadata(main_question, docs)
        docs = docs[:5]

        doc_texts = [
            f"[Metadata: {', '.join(f'{k}: {v}' for k, v in doc.metadata.items())}]\n{doc.page_content}" for doc in docs]

        global_summary_prompt = GLOBAL_SUMMARIZER_PROMPT.format(
            main_question=main_question,
            docs="\n".join(doc_texts)
        )
        global_summary = self.llm.invoke(global_summary_prompt).content

        local_summary_prompt = LOCAL_SUMMARIZER_PROMPT.format(
            sub_question=main_question,
            docs="\n".join(doc_texts)
        )
        local_summary = self.llm.invoke(local_summary_prompt).content

        global_memory.append(global_summary)
        local_memory.append(
            {"sub_question": main_question, "response": local_summary})

        hop_info["sub_questions"].append({
            "sub_question": main_question,
            "retrieved_docs": [
                {"content": doc.page_content, "metadata": dict(doc.metadata)} for doc in docs
            ],
            "global_summary": global_summary,
            "local_summary": local_summary
        })

        # --- Now call planner to get next_sub_questions ---
        planner_reasoner_prompt = PLANNER_REASONER_PROMPT.format(
            main_question=main_question,
            global_memory="\n".join(global_memory),
            local_memory="\n".join(
                [f"Sub-question: {m['sub_question']}\nResponse: {m['response']}" for m in local_memory]),
            genie_docs_toc=GENIE_DOCS_TOC,
            previous_sub_questions=""
        )

        logger.debug(f"[Planner Prompt Debug] {planner_reasoner_prompt}")
        reasoner_raw = self.llm.invoke(planner_reasoner_prompt).content
        logger.info(f"[Hop 1] Reasoner raw: {reasoner_raw}")
        reasoner = parse_reasoner_json(reasoner_raw)
        hop_info["reasoner_output"] = reasoner
        hops_trace.append(hop_info)

        # --- Use 'next_sub_questions' as the key for sub-questions ---
        current_sub_questions = reasoner.get("next_sub_questions", [])
        if not current_sub_questions:
            sq = reasoner.get("next_sub_question")
            if sq:
                current_sub_questions = [sq]
            else:
                logger.warning(
                    "[Hop 1] No sub-questions generated by planner. Stopping.")
                return {"answer": None, "trace": hops_trace, "num_hops": 1}

        # Ensure all_sub_questions only contains strings
        for sq in current_sub_questions:
            if isinstance(sq, dict):
                all_sub_questions.append(sq.get("sub_question", ""))
            else:
                all_sub_questions.append(sq)

        sufficient = reasoner.get("sufficient", False)

        while hop < max_hops and not sufficient:
            hop += 1
            hop_info = {"hop": hop, "sub_questions": []}
            subq_results = []

            for subq in current_sub_questions:
                # Ensure subq is a string (handle dicts with 'sub_question' key)
                if isinstance(subq, dict):
                    query_text = subq.get("sub_question", "")
                else:
                    query_text = subq

                docs = retrieve_docs(query_text, self.retriever)
                docs = rerank(query_text, docs)
                docs = boost_by_metadata(query_text, docs)
                docs = docs[:5]

                doc_texts = [
                    f"[Metadata: {', '.join(f'{k}: {v}' for k, v in doc.metadata.items())}]\n{doc.page_content}" for doc in docs]

                global_summary_prompt = GLOBAL_SUMMARIZER_PROMPT.format(
                    main_question=main_question,
                    docs="\n".join(doc_texts)
                )
                global_summary = self.llm.invoke(global_summary_prompt).content

                local_summary_prompt = LOCAL_SUMMARIZER_PROMPT.format(
                    sub_question=query_text,
                    docs="\n".join(doc_texts)
                )
                local_summary = self.llm.invoke(local_summary_prompt).content

                global_memory.append(global_summary)
                local_memory.append(
                    {"sub_question": query_text, "response": local_summary})

                subq_results.append({
                    "sub_question": query_text,
                    "retrieved_docs": [
                        {"content": doc.page_content, "metadata": dict(doc.metadata)} for doc in docs
                    ],
                    "global_summary": global_summary,
                    "local_summary": local_summary
                })

            # When joining previous_sub_questions, ensure only strings
            previous_sub_questions_str = "\n".join(
                sq.get("sub_question", "") if isinstance(sq, dict) else sq
                for sq in all_sub_questions
            )

            planner_reasoner_prompt = PLANNER_REASONER_PROMPT.format(
                main_question=main_question,
                global_memory="\n".join(global_memory),
                local_memory="\n".join(
                    [f"Sub-question: {m['sub_question']}\nResponse: {m['response']}" for m in local_memory]),
                genie_docs_toc=GENIE_DOCS_TOC,
                previous_sub_questions=previous_sub_questions_str
            )

            logger.debug(f"[Planner Prompt Debug] {planner_reasoner_prompt}")
            reasoner_raw = self.llm.invoke(planner_reasoner_prompt).content
            logger.info(f"[Hop {hop}] Reasoner raw: {reasoner_raw}")
            reasoner = parse_reasoner_json(reasoner_raw)

            hop_info["sub_questions"] = subq_results
            hop_info["reasoner_output"] = reasoner
            hops_trace.append(hop_info)

            sufficient = reasoner.get("sufficient", False)
            if sufficient:
                break

            next_subqs = reasoner.get("next_sub_questions", [])
            if not next_subqs:
                sq = reasoner.get("next_sub_question")
                if sq:
                    next_subqs = [sq]

            # Ensure next_subqs are strings
            next_subqs = [q.get("sub_question", "") if isinstance(
                q, dict) else q for q in next_subqs if q]
            next_subqs = [
                q for q in next_subqs if q and q not in all_sub_questions]

            if not next_subqs:
                logger.warning(
                    f"[Hop {hop}] No new sub-questions found. Stopping.")
                break

            for q in next_subqs:
                all_sub_questions.append(q)
            current_sub_questions = next_subqs

        # --- Final answer ---
        logger.info(
            "[ReSPPipeline] Generating final answer from all accumulated evidence.")
        combined_memory = "\n".join(
            global_memory + [f"{m['sub_question']}\n{m['response']}" for m in local_memory])
        logger.info(
            f"[ReSPPipeline] main_question passed to generator_prompt: {main_question}")

        generator_prompt = GENERATOR_PROMPT.format(
            combined_memory=combined_memory,
            main_question=main_question
        )
        answer = self.llm.invoke(generator_prompt).content

        hops_trace.append({
            "hop": "final",
            "generator": answer,
            "global_memory": list(global_memory),
            "local_memory": list(local_memory)
        })

        num_real_hops = sum(
            1 for h in hops_trace if isinstance(h.get("hop"), int))
        return {"answer": answer, "trace": hops_trace, "num_hops": num_real_hops}

    def query_knowledgebase(self, query: str, max_hops: int = 5) -> Dict[str, Any]:
        """Query the knowledge base using ReSP pipeline"""
        try:
            # Use ReSP pipeline for multi-hop reasoning
            result = self.run_resp_pipeline(query, max_hops=max_hops)

            # Extract sources and metadata from the trace
            sources = []
            metadata_list = []

            for hop_info in result.get("trace", []):
                # Handle the new structure where documents are nested under "sub_questions"
                if "sub_questions" in hop_info:
                    for subq_info in hop_info["sub_questions"]:
                        if "retrieved_docs" in subq_info:
                            for doc in subq_info["retrieved_docs"]:
                                sources.append(doc["content"])

                                # Extract metadata
                                meta = doc["metadata"]
                                pdf_name = (
                                    os.path.basename(meta.get("source", ""))
                                    if "source" in meta
                                    else "Unknown Document"
                                )
                                page_number = meta.get("page", 0)
                                entry = {
                                    "title": pdf_name,
                                    "source": meta.get("source", ""),
                                    "page": page_number,
                                }
                                if meta.get("title"):
                                    entry["document_title"] = meta["title"]
                                metadata_list.append(entry)
                # Also handle old structure for backward compatibility
                elif "retrieved_docs" in hop_info:
                    for doc in hop_info["retrieved_docs"]:
                        sources.append(doc["content"])

                        # Extract metadata
                        meta = doc["metadata"]
                        pdf_name = (
                            os.path.basename(meta.get("source", ""))
                            if "source" in meta
                            else "Unknown Document"
                        )
                        page_number = meta.get("page", 0)
                        entry = {
                            "title": pdf_name,
                            "source": meta.get("source", ""),
                            "page": page_number,
                        }
                        if meta.get("title"):
                            entry["document_title"] = meta["title"]
                        metadata_list.append(entry)

            # Remove duplicates from sources and metadata
            unique_sources = list(dict.fromkeys(sources))
            unique_metadata = []
            seen_entries = set()
            for entry in metadata_list:
                entry_key = (entry["source"], entry["page"])
                if entry_key not in seen_entries:
                    unique_metadata.append(entry)
                    seen_entries.add(entry_key)

            return {
                "answer": result.get("answer", "No answer generated"),
                "sources": unique_sources,
                "metadata": unique_metadata,
                "error": None,
                "num_hops": result.get("num_hops", 0),
                "trace": result.get("trace", [])
            }

        except Exception as e:
            logger.error(f"Error querying knowledge base with ReSP: {e}")
            return {
                "answer": "Knowledge Base is currently unavailable",
                "sources": [],
                "metadata": [],
                "error": str(e),
                "num_hops": 0,
                "trace": []
            }

    @message_handler
    async def handle(self, message: Message, ctx: MessageContext) -> Message:
        query = message.content.strip()
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.query_knowledgebase, query)

            # Validate the result
            validated = KBResponse(**result)
            return Message(content=validated.model_dump_json())

        except Exception as e:
            logger.error(f"Error in KnowledgeBaseAgent handler: {e}")
            return Message(content=json.dumps({
                "answer": "An error occurred while processing your request",
                "sources": [],
                "metadata": [],
                "error": str(e),
                "num_hops": 0,
                "trace": []
            }))
