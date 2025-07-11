import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

from dotenv import load_dotenv
from llama_index.core import Document
from llama_index.core.llama_dataset.generator import RagDatasetGenerator
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import TextNode
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from openai import RateLimitError

# Load environment variables
load_dotenv()

# Setup OpenAI LLM
llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Prompt for generating RAG questions
qa_generate_prompt_tmpl = """\
You are an expert assistant helping build high-quality evaluation questions for RAG (Retrieval-Augmented Generation) systems.

Below is a context passage extracted from a document.
Your task is to generate exactly {num_questions_per_chunk} clear and direct questions, answerable **only using this context**.

---------------------
{context_str}
---------------------

Important Instructions:
- Do **not** include any introductory lines (e.g., "Here are the questions:", "Based on the passage:", etc.)
- Do **not** explain or repeat the context in your output.
- Do **not** number or bullet the questions.
- Each question must be written on a new line, with **no extra text** above or below.
- Questions must be *fact-based*, *precise*, and *grounded* in the context.

Your output must be:
- {num_questions_per_chunk} standalone questions
- Each on its own line
- No formatting, no headers, no summaries

Example Output:
What is the main benefit of using X?
How does the system handle Y?
Who is responsible for Z?
"""

def load_json_as_documents(json_path: str) -> List[Document]:
    with open(json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return [Document(text=chunk["text"], metadata=chunk["metadata"]) for chunk in chunks]

def generate_eval_dataset(documents: List[Document], num_per_chunk=3) -> List[Dict[str, Any]]:
    nodes = [TextNode(text=doc.text, metadata=doc.metadata) for doc in documents]

    dataset_generator = RagDatasetGenerator.from_documents(
        nodes,
        llm=llm,
        num_questions_per_chunk=num_per_chunk,
        show_progress=True,
        text_question_template=PromptTemplate(qa_generate_prompt_tmpl)
    )

    dataset = dataset_generator.generate_dataset_from_nodes()
    examples = dataset.examples

    enriched = []
    for i, node in enumerate(nodes):
        for j in range(num_per_chunk):
            idx = i * num_per_chunk + j
            if idx < len(examples):
                enriched.append({
                    "question": examples[idx].query,
                    "answer": examples[idx].reference_answer,
                    "context": examples[idx].reference_contexts,
                    "metadata": node.metadata
                })

    return enriched

def group_by_chunk(dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = defaultdict(lambda: {"questions": [], "metadata": {}, "context": None})
    for item in dataset:
        meta = item["metadata"]
        chunk_id = (meta["file_path"], meta["chunk_index"])
        grouped[chunk_id]["questions"].append({
            "question": item["question"],
            "answer": item["answer"]
        })
        grouped[chunk_id]["metadata"] = meta
        if grouped[chunk_id]["context"] is None:
            grouped[chunk_id]["context"] = item["context"][0] if item["context"] else ""
    return list(grouped.values())

def save_dataset(grouped_dataset: List[Dict[str, Any]], output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(grouped_dataset, f, indent=2, ensure_ascii=False)

def safe_generate_eval_dataset(documents: List[Document], num_per_chunk=3) -> List[Dict[str, Any]]:
    while True:
        try:
            return generate_eval_dataset(documents, num_per_chunk)
        except RateLimitError as e:
            print(f"Rate limit hit. Waiting 7 minutes...\n{e}")
            time.sleep(7 * 60)
