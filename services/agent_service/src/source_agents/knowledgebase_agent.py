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
        sub_questions = []
        current_question = main_question
        hops_trace = []

        for hop in range(max_hops):
            hop_info = {"hop": hop+1, "sub_question": current_question}
            logger.info(f"[Hop {hop+1}] Sub-question: {current_question}")

            # 1. Retrieve documents
            docs = retrieve_docs(current_question, self.retriever)
            docs = rerank(current_question, docs)
            docs = boost_by_metadata(current_question, docs)
            docs = docs[:5]  # Top 5 documents

            hop_info["retrieved_docs"] = [
                {
                    "content": doc.page_content,
                    "metadata": dict(doc.metadata)
                } for doc in docs
            ]

            logger.info(f"[Hop {hop+1}] Retrieved {len(docs)} docs.")

            if not docs:
                logger.warning(
                    f"[Hop {hop+1}] No documents retrieved for question: '{current_question}'")
                return {
                    "answer": "No relevant documents found in the knowledge base.",
                    "trace": hops_trace,
                    "num_hops": hop+1
                }

            # Format documents with metadata
            def format_doc_with_metadata(doc):
                meta_str = ", ".join(
                    f"{k}: {v}" for k, v in doc.metadata.items())
                return f"[Metadata: {meta_str}]\n{doc.page_content}"

            doc_texts = [format_doc_with_metadata(doc) for doc in docs]

            # 2. Global summarization
            global_summary_prompt = GLOBAL_SUMMARIZER_PROMPT.format(
                main_question=main_question,
                docs="\n".join(doc_texts)
            )
            global_summary = self.llm.invoke(global_summary_prompt).content
            logger.info(f"[Hop {hop+1}] Global Summary: {global_summary}")

            hop_info["global_summary"] = global_summary
            global_memory.append(global_summary)

            # 3. Local summarization
            local_summary_prompt = LOCAL_SUMMARIZER_PROMPT.format(
                sub_question=current_question,
                docs="\n".join(doc_texts)
            )
            local_summary = self.llm.invoke(local_summary_prompt).content
            logger.info(f"[Hop {hop+1}] Local Summary: {local_summary}")

            hop_info["local_summary"] = local_summary
            local_memory.append(
                {"sub_question": current_question, "response": local_summary})

            # 4. Planner-Reasoner
            planner_reasoner_prompt = PLANNER_REASONER_PROMPT.format(
                main_question=main_question,
                global_memory="\n".join(global_memory),
                local_memory="\n".join(
                    [f"Sub-question: {m['sub_question']}\nResponse: {m['response']}" for m in local_memory]),
                genie_docs_toc=GENIE_DOCS_TOC,
                previous_sub_questions="\n".join(sub_questions)
            )

            reasoner_raw = self.llm.invoke(planner_reasoner_prompt).content
            logger.info(f"[Hop {hop+1}] Reasoner raw: {reasoner_raw}")

            reasoner = parse_reasoner_json(reasoner_raw)
            hop_info["reasoner_output"] = reasoner
            hop_info["global_memory"] = list(global_memory)

            # 5. Check if sufficient evidence
            if reasoner.get("sufficient") is True:
                logger.info(
                    f"[Hop {hop+1}] Sufficient evidence found. Generating final answer.")

                combined_memory = "\n".join(
                    global_memory +
                    [f"{m['sub_question']}\n{m['response']}" for m in local_memory]
                )
                generator_prompt = GENERATOR_PROMPT.format(
                    combined_memory=combined_memory,
                    main_question=main_question
                )
                answer = self.llm.invoke(generator_prompt).content
                logger.info(f"[Hop {hop+1}] Generator Response: {answer}")

                hop_info["generator"] = answer
                hops_trace.append(hop_info)

                num_real_hops = sum(
                    1 for h in hops_trace if isinstance(h.get("hop"), int))
                return {
                    "answer": answer,
                    "trace": hops_trace,
                    "num_hops": num_real_hops
                }
            else:
                # Need more information
                new_subq = reasoner.get("next_sub_question")
                if not new_subq or new_subq in sub_questions:
                    logger.warning(
                        f"[Hop {hop+1}] No new sub-question found or repeated. Stopping.")
                    hops_trace.append(hop_info)
                    break

                sub_questions.append(new_subq)
                current_question = new_subq
                logger.info(f"[Hop {hop+1}] Next sub-question: {new_subq}")

                hop_info["next_sub_question"] = new_subq
                hops_trace.append(hop_info)
                continue

        # Max hops reached - generate final answer
        logger.info(
            "[ReSPPipeline] Max hops reached. Generating final answer from accumulated evidence.")
        combined_memory = "\n".join(
            global_memory +
            [f"{m['sub_question']}\n{m['response']}" for m in local_memory]
        )
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
        return {
            "answer": answer,
            "trace": hops_trace,
            "num_hops": num_real_hops
        }

    def query_knowledgebase(self, query: str, max_hops: int = 5) -> Dict[str, Any]:
        """Query the knowledge base using ReSP pipeline"""
        try:
            # Use ReSP pipeline for multi-hop reasoning
            result = self.run_resp_pipeline(query, max_hops=max_hops)

            # Extract sources and metadata from the trace
            sources = []
            metadata_list = []

            for hop_info in result.get("trace", []):
                if "retrieved_docs" in hop_info:
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
