import asyncio
import os
import random
from pathlib import Path
from onetomanyUtils import (
    load_json_as_documents,
    safe_generate_eval_dataset,
    save_dataset,
    group_by_chunk
)

INPUT_DIR = "test_output"
OUTPUT_DIR = "data"

async def process_file(input_path: Path):
    print(f"\nLoading: {input_path}")
    documents = load_json_as_documents(str(input_path))

    print(f"Generating evaluation dataset with GROQ for {input_path.name}...")
    sampled_docs = random.sample(documents, min(5, len(documents)))
    eval_dataset = safe_generate_eval_dataset(sampled_docs)
    grouped = group_by_chunk(eval_dataset)

    output_file = Path(OUTPUT_DIR) / input_path.name
    print(f"Saving to: {output_file}")
    save_dataset(grouped, str(output_file))

async def main():
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = list(input_dir.glob("*.json"))
    if not json_files:
        print("No JSON files found in input directory.")
        return

    await asyncio.gather(*(process_file(file_path) for file_path in json_files))
    print("\nAll files processed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
