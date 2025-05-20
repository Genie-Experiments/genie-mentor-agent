# backend/services/llm_handler.py
"""
Mock LLM handler.
Returns hard‑coded answers so the whole app works offline.
"""

from itertools import cycle
from typing import List, Tuple

# ── canned responses ──────────────────────────────────────────────────────
_RESPONSES = cycle(
    [
        "Sure! How can I help you further?",
        "Here’s a quick answer for you.",
        "Got it. Let me know if you need more details.",
        "Absolutely. Anything else on your mind?",
    ]
)

def get_llm_response(query: str, history: List[Tuple[str, str]]) -> str:
    """
    Ignore `query` and `history`, just return the next canned response.
    """
    return next(_RESPONSES)


# # backend/services/llm_handler.py
# import os
# from dotenv import load_dotenv
# from openai import OpenAI, OpenAIError   # pip install openai>=1.14.0

# load_dotenv()                                       # ① load .env

# API_KEY = os.getenv("OPENROUTER_API_KEY")
# if not API_KEY:
#     raise RuntimeError("OPENROUTER_API_KEY missing in environment!")

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",        # ② point to OpenRouter
#     api_key=API_KEY,
# )

# MODEL_NAME = "qwen/qwen3-0.6b-04-28:free"           # ③ pick any model slug

# def get_llm_response(query: str, history: list[list[str]]) -> str:
#     """
#     history = [[user1, assistant1], [user2, assistant2], ...]
#     returns assistant response text
#     """
#     messages = [{"role": "system", "content": "You are a helpful assistant."}]
#     for user_msg, bot_msg in history:
#         messages += [
#             {"role": "user",      "content": user_msg},
#             {"role": "assistant", "content": bot_msg},
#         ]
#     messages.append({"role": "user", "content": query})

#     try:
#         resp = client.chat.completions.create(
#             model       = MODEL_NAME,
#             messages    = messages,
#             max_tokens  = 512,
#             temperature = 0.7,
#             extra_headers = {              # optional – safe to omit
#                 # "HTTP-Referer": os.getenv("SITE_URL",  "http://localhost"),
#                 # "X-Title"     : os.getenv("SITE_NAME", "AgenticRAG"),
#             },
#         )
#         return resp.choices[0].message.content.strip()

#     except OpenAIError as e:
#         # bubble up a clear error for FastAPI to catch ‑‑ you’ll see 500 + message
#         raise RuntimeError(f"OpenRouter API failed → {e}")

