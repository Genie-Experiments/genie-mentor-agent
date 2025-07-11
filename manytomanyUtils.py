import os
import numpy as np
import json
from dotenv import load_dotenv
from typing import List
from sklearn.metrics.pairwise import cosine_similarity

from llama_index.core.schema import TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import TokenTextSplitter

# Load OpenAI API key
load_dotenv()
embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))


def load_all_chunks_from_json(json_paths: List[str]) -> List[TextNode]:
    """Load JSON files and convert each chunk into a TextNode with metadata, preserving file info."""
    nodes = []
    for path in json_paths:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for entry in data:
                metadata = {
                    **entry["metadata"],
                    "file_path": os.path.basename(path)  # add file origin
                }
                node = TextNode(text=entry["text"], metadata=metadata)
                nodes.append(node)
    return nodes


def preprocess_nodes_for_embedding(nodes: List[TextNode], max_tokens: int = 7000) -> List[TextNode]:
    """Split nodes into sub-nodes under token limit while preserving metadata."""
    splitter = TokenTextSplitter(chunk_size=max_tokens, chunk_overlap=0)
    split_nodes = []

    for node in nodes:
        sub_chunks = splitter.split_text(node.text)
        for i, sub_text in enumerate(sub_chunks):
            sub_node = TextNode(
                text=sub_text,
                metadata={**node.metadata, "sub_chunk_index": i}
            )
            split_nodes.append(sub_node)

    return split_nodes


import random

def group_chunks_randomly(nodes: List[TextNode], min_group_size: int = 3, max_group_size: int = 4, max_groups: int = 10) -> List[List[TextNode]]:
    """Randomly group TextNodes into small groups of 3–4 chunks, capped at 10 groups."""
    safe_nodes = preprocess_nodes_for_embedding(nodes)
    random.shuffle(safe_nodes)

    groups = []
    i = 0

    while i < len(safe_nodes) and len(groups) < max_groups:
        group_size = random.randint(min_group_size, max_group_size)
        group = safe_nodes[i:i + group_size]
        if len(group) < min_group_size:
            break  # skip small last group
        groups.append(group)
        i += group_size

    return groups
