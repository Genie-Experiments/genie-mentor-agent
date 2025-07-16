
# services/agent_service/src/multihop_resp/resp_pipeline.py

import os
from dotenv import load_dotenv
load_dotenv()
from .prompts import JUDGE_PROMPT, PLAN_PROMPT, SUMMARIZER_PROMPT_GLOBAL, SUMMARIZER_PROMPT_LOCAL, GENERATOR_PROMPT, GLOBAL_SUMMARIZER_PROMPT, LOCAL_SUMMARIZER_PROMPT, PLANNER_REASONER_PROMPT, GENIE_DOCS_TOC
from .utils import get_chroma_retriever, retrieve_docs
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
# Use the colored logger from utils.logging
from ..utils.logging import setup_logger, get_logger
setup_logger()
logger = get_logger("ReSPPipeline")

from ..prompts.kb_agent_prompt import kb_assistant_prompt
from langchain_community.vectorstores import Chroma
from ..source_agents.knowledgebase_agent import rerank, boost_by_metadata
import json, re

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


# For local testing, set CHROMA_DB_PATH directly
CHROMA_DB_PATH = r"C:\Users\Emumba\Downloads\Projects\genie-mentor-agent\services\genie-kbdocs-v1-wed3\chroma_db"

db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=None)
print("Number of documents/chunks in the database:", db._collection.count())  # Should print the number of documents/chunks

class ReSPPipeline:
    def __init__(
        self,
        persist_directory,
        groq_api_key,
        model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
        embedding_model_name="BAAI/bge-small-en-v1.5",
        retrieval_k=15
    ):
        self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.retriever = get_chroma_retriever(persist_directory, self.embedding_model, k=retrieval_k)
        self.llm = ChatGroq(temperature=0.1, groq_api_key=groq_api_key, model_name=model_name)
        self.retrieval_k = retrieval_k

    def run(self, main_question, max_hops=5):
        global_memory = []
        local_memory = []
        sub_questions = []  # Maintain as a list for order
        current_question = main_question
        hops_trace = []
        for hop in range(max_hops):
            hop_info = {"hop": hop+1, "sub_question": current_question}
            logger.info(f"[Hop {hop+1}] Retrieval k: {self.retrieval_k}")
            # 1. Retrieve
            docs = retrieve_docs(current_question, self.retriever)
            docs = rerank(current_question, docs)
            docs = boost_by_metadata(current_question, docs)
            docs = docs[:5]
            # Print all metadata fields for each chunk (first hop only)
            if hop == 0:
                for i, doc in enumerate(docs):
                    print(f"Chunk {i+1} metadata: {doc.metadata}")
            hop_info["retrieved_docs"] = [
                {
                    "content": doc.page_content,
                    "metadata": dict(doc.metadata)
                } for doc in docs
            ]
            logger.info(f"[Hop {hop+1}] Sub-question: {current_question}")
            logger.info(f"[Hop {hop+1}] Retrieved {len(docs)} docs.")
            for i, doc in enumerate(docs):
                logger.info(f"  Chunk {i+1}: {doc.page_content[:120].replace('\n',' ')}...")
                logger.info(f"    Source: {doc.metadata.get('source','')} | Page: {doc.metadata.get('page',0)} | Title: {doc.metadata.get('title','')}")
            if not docs:
                logger.warning(f"[Hop {hop+1}] No documents retrieved for question: '{current_question}'")
                return {"answer": "No relevant documents found in the knowledge base.", "trace": hops_trace, "num_hops": hop+1}
            def format_doc_with_metadata(doc):
                meta_str = ", ".join(f"{k}: {v}" for k, v in doc.metadata.items())
                return f"[Metadata: {meta_str}]\n{doc.page_content}"
            doc_texts = [format_doc_with_metadata(doc) for doc in docs]
            # 2. Summarize (Global)
            global_summary_prompt = GLOBAL_SUMMARIZER_PROMPT.format(
                main_question=main_question,
                docs="\n".join(doc_texts)
            )
            global_summary = self.llm.invoke(global_summary_prompt).content
            logger.info(f"[Hop {hop+1}] Global Summary: {global_summary}")
            hop_info["global_summary"] = global_summary
            global_memory.append(global_summary)
            # 2. Summarize (Local)
            local_summary_prompt = LOCAL_SUMMARIZER_PROMPT.format(
                sub_question=current_question,
                docs="\n".join(doc_texts)
            )
            local_summary = self.llm.invoke(local_summary_prompt).content
            logger.info(f"[Hop {hop+1}] Local Summary: {local_summary}")
            hop_info["local_summary"] = local_summary
            local_memory.append({"sub_question": current_question, "response": local_summary})
            # 3. Planner-Reasoner
            planner_reasoner_prompt = PLANNER_REASONER_PROMPT.format(
                main_question=main_question,
                global_memory="\n".join(global_memory),
                local_memory="\n".join([f"Sub-question: {m['sub_question']}\nResponse: {m['response']}" for m in local_memory]),
                genie_docs_toc=GENIE_DOCS_TOC,
                previous_sub_questions="\n".join(sub_questions)
            )
            logger.debug(f"[Planner Prompt Debug] {planner_reasoner_prompt}")
            reasoner_raw = self.llm.invoke(planner_reasoner_prompt).content
            logger.info(f"[Hop {hop+1}] Reasoner raw: {reasoner_raw}")
            reasoner = parse_reasoner_json(reasoner_raw)
            hop_info["reasoner_output"] = reasoner
            hop_info["global_memory"] = list(global_memory)
            if reasoner.get("sufficient") is True:
                # ✔ enough evidence → generate final answer
                logger.info(f"[Hop {hop+1}] Generator")
                combined_memory = "\n".join(global_memory + [f"{m['sub_question']}\n{m['response']}" for m in local_memory])
                generator_prompt = GENERATOR_PROMPT.format(
                    combined_memory=combined_memory, main_question=main_question
                )
                answer = self.llm.invoke(generator_prompt).content
                logger.info(f"[Hop {hop+1}] Generator Response: {answer}")
                hop_info["generator"] = answer
                hops_trace.append(hop_info)
                num_real_hops = sum(1 for h in hops_trace if isinstance(h.get("hop"), int))
                return {"answer": answer, "trace": hops_trace, "num_hops": num_real_hops}
            else:
                new_subq = reasoner.get("next_sub_question")
                if not new_subq or new_subq in sub_questions:
                    logger.warning(f"[Hop {hop+1}] No new sub-question found or repeated. Stopping.")
                    hops_trace.append(hop_info)
                    break
                sub_questions.append(new_subq)
                current_question = new_subq
                logger.info(f"[Hop {hop+1}] Next sub-question: {new_subq}")
                hop_info["next_sub_question"] = new_subq
                hops_trace.append(hop_info)
                continue
        # If we've reached here, max hops were reached without a YES from the reasoner
        logger.info("[ReSPPipeline] Max hops reached. Generating final answer from all accumulated evidence.")
        combined_memory = "\n".join(global_memory + [f"{m['sub_question']}\n{m['response']}" for m in local_memory])
        generator_prompt = GENERATOR_PROMPT.format(
                combined_memory=combined_memory, main_question=main_question
        )
        answer = self.llm.invoke(generator_prompt).content
        hops_trace.append({
            "hop": "final",
            "generator": answer,
            "global_memory": list(global_memory),
            "local_memory": list(local_memory)
        })
        num_real_hops = sum(1 for h in hops_trace if isinstance(h.get("hop"), int))
        return {"answer": answer, "trace": hops_trace, "num_hops": num_real_hops}

if __name__ == "__main__":
    persist_dir = CHROMA_DB_PATH
    groq_api_key = os.environ["GROQ_API_KEY"]
    pipeline = ReSPPipeline(
        persist_dir,
        groq_api_key,
        model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
        retrieval_k=20
    )
    question = input("Enter your question: ")
    result = pipeline.run(question)
    print(json.dumps(result, indent=2, ensure_ascii=False))