# services/agent_service/src/utils/memory_client.py
from typing import List
import asyncio
from mem0 import AsyncMemory
from ..utils.logging import get_logger

logger      = get_logger("MemoryClient")
_mem        = AsyncMemory()
_semaphore  = asyncio.Semaphore(1)          # prevents concurrent disk writes

# ---------- WRITE ----------
async def remember(user_id: str, question: str, answer: str) -> None:
    """Store a single Q-A pair for this user/session."""
    text = f"Q: {question}\nA: {answer}"
    async with _semaphore:
        await _mem.add(text, user_id=user_id)
        logger.debug(f"[Mem0] saved -> {text[:80]}…")

# ---------- READ ----------

async def recall(user_id: str, query: str, k: int = 3) -> List[str]:
    """
    Return up to *k* past Q-A snippets relevant to `query`.
    Handles both the old dict-based hits and the new string-based hits.
    """
    hits = await _mem.search(query=query, user_id=user_id, limit=k)
    logger.debug(f"[Mem0] search hits → {hits}")

    if not hits:
        return []

    # if each hit is already a string, just return it
    if isinstance(hits[0], str):
        return hits

    # else, expect dicts with either 'memory' or 'text'
    out = []
    for h in hits:
        if isinstance(h, dict):
            out.append(h.get("memory") or h.get("text"))
        else:
            # fallback to string-conversion
            out.append(str(h))
    return out
