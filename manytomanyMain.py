import os
import time
import json
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.prompts import PromptTemplate
from manytomanyUtils import (
    load_all_chunks_from_json,
    group_chunks_randomly,  
)

load_dotenv()

token_counter = TokenCountingHandler()
callback_manager = CallbackManager([token_counter])

llm = OpenAI(
    model="gpt-4o",
    callback_manager=callback_manager,
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.3
)

rag_multi_context_prompt = """\
You are helping evaluate Retrieval-Augmented Generation (RAG) systems by generating realistic, grounded, and **cross-context** questions.

Below is a combined context consisting of multiple passages from different documents. Your task is to generate {num_questions} high-quality questions that require information from **two or more** passages in the provided context.

---------------------
{context_str}
---------------------

Instructions:
- Each question should synthesize information from at least **two different parts** of the context.
- Do NOT create a separate question for each paragraph or passage.
- Do NOT include any introductions or explanations.
- Do NOT number or bullet the questions.
- Return exactly {num_questions} questions, each on a separate line.

Only output:
<question>
<question>
<question>
"""

def build_context_from_group(group):
    """Concatenate texts for LLM prompt context."""
    return "\n\n".join([node.text for node in group])

def extract_metadata_from_group(group):
    """Extract useful metadata (file, chunk, subchunk) for each node."""
    return [
        {
            "file_path": node.metadata.get("file_path", ""),
            "chunk_index": node.metadata.get("chunk_index", None),
            "sub_chunk_index": node.metadata.get("sub_chunk_index", None)
        }
        for node in group
    ]

def run_single_group_test():
    chunk_dir = "test_output"
    chunk_files = [os.path.join(chunk_dir, f) for f in os.listdir(chunk_dir) if f.endswith(".json")]
    print(f"Loaded {len(chunk_files)} files.")

    all_nodes = load_all_chunks_from_json(chunk_files)
    groups = group_chunks_randomly(all_nodes, min_group_size=3, max_group_size=4, max_groups=10)

    test_group = groups[0]
    context = build_context_from_group(test_group)
    metadata = extract_metadata_from_group(test_group)

    prompt = PromptTemplate(rag_multi_context_prompt).format(
        context_str=context,
        num_questions=3
    )

    print("Sending request to LLM...\n")
    response = llm.complete(prompt)
    questions = [q.strip() for q in response.text.strip().split("\n") if q.strip()]
    print("Questions:\n", questions)
    print("Total tokens used:", token_counter.total_llm_token_count)

    try:
        usage = response.usage
    except AttributeError:
        usage = {}

    output = {
        "questions": questions,
        "chunks_used": metadata,
        "token_usage": usage
    }

    print("\nFinal Output:")
    print(json.dumps(output, indent=2, ensure_ascii=False))

    with open("group_eval_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_single_group_test()
