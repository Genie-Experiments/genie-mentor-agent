# services/agent-service/src/schemas/chat.py
from pydantic import BaseModel
from typing import List, Tuple, Optional

class ChatHistory(BaseModel):
    history: List[Tuple[Optional[str], Optional[str]]]
