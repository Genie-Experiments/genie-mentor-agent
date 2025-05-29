import json
from typing import List

from autogen_core import RoutedAgent, MessageContext, message_handler
from datasets import Dataset
from ragas.metrics import FaithfulnesswithHHEM
from ragas import evaluate

from .message import Message
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
faithfulness_with_hhem = FaithfulnesswithHHEM()

class EvalAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("eval_agent")

    @staticmethod
    def _score_one(q: str, a: str, ctxs: List[str]) -> float:
        ds = Dataset.from_dict(
            {"question": [q], "answer": [a], "contexts": [ctxs]}
        )
        res = evaluate(ds, metrics=[faithfulness_with_hhem])  
        
        score = float(res["faithfulness_with_hhem"][0])

        return score

    @message_handler
    async def evaluate_answer(
        self, message: Message, ctx: MessageContext
    ) -> Message:
        payload = json.loads(message.content)
        score = self._score_one(
            payload["question"], payload["answer"], payload["contexts"]
        )
        return Message(content=json.dumps({"score": score}))
