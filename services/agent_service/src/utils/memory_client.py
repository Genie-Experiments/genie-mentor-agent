import os
import asyncio
from typing import List
from mem0 import Memory

from ..utils.logging import get_logger

logger = get_logger("MemoryClient")

# Ensure the Groq key is available
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Configure Memory with Groq LLM + HuggingFace embedder
_mem = Memory.from_config({
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "multi-qa-MiniLM-L6-cos-v1"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "embedding_model_dims": 384  # ✅ IMPORTANT
        }
    }
})

_semaphore = asyncio.Semaphore(1)

# ---------- WRITE ----------
async def remember(session_id: str, question: str, answer: str) -> None:
    text = f"Q: {question}\nA: {answer}"
    async with _semaphore:
        _mem.add(text, user_id=session_id)
        logger.debug(f"[Mem0] Saved: {text[:80]}…")

# ---------- READ ----------
async def recall(session_id: str, query: str, k: int = 1) -> List[str]:
    results = _mem.search(query, user_id=session_id, limit=k)
    logger.debug(f"[Mem0] Raw results: {results}")

    out = []
    for h in results.get("results", []):
        out.append(h.get("memory") or h.get("text") or str(h))
    return out
