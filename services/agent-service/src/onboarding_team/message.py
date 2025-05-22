# Third-party imports
from pydantic import BaseModel

class Message(BaseModel):
    content: str

class RefinerOutput(BaseModel):
    refined_plan: str
    feedback: str