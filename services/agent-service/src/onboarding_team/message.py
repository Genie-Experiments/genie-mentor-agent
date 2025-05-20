# Third-party imports
from pydantic import BaseModel

class Message(BaseModel):
    content: str