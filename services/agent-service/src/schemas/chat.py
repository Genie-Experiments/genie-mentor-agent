# services/agent-service/src/schemas/chat.py
# Standard library imports
from typing import List, Optional, Tuple

# Third-party imports
from pydantic import BaseModel

class ChatHistory(BaseModel):
    history: List[Tuple[Optional[str], Optional[str]]]
