import json
import os
from typing import List
from autogen_core import RoutedAgent, MessageContext, message_handler
from ..protocols.message import Message
from uptrain import Evals, EvalLLM, Settings
from ..utils.logging import setup_logger, get_logger

setup_logger()
logger = get_logger("my_module")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class EvalAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("eval_agent")
        settings = Settings(model="gpt-4o", openai_api_key=OPENAI_API_KEY)
        self.eval_llm = EvalLLM(settings)

    @staticmethod
    def _prepare_input(question: str, answer: str, contexts: List[str]) -> dict:
        return {
            "question": question,
            "response": answer,
            "context": " ".join(contexts)
        }

    @message_handler
    async def evaluate_answer(self, message: Message, ctx: MessageContext) -> Message:
        try:
            payload = json.loads(message.content)
            data_item = self._prepare_input(payload["question"], payload["answer"], payload["contexts"])
            result = self.eval_llm.evaluate(data=[data_item], checks=[Evals.FACTUAL_ACCURACY])[0]

            score = float(result.get("score_factual_accuracy", 0))
            reasoning = result.get("explanation_factual_accuracy", "")

            return Message(content=json.dumps({
                "score": score,
                "reasoning": reasoning,
                "error": None
            }))

        except Exception as e:
            logger.exception("Evaluation failed")
            return Message(content=json.dumps({
                "score": 0,
                "reasoning": "",
                "error": str(e)
            }))
