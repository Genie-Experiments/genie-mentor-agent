import json
import os
from typing import List
from autogen_core import RoutedAgent, MessageContext, message_handler
from ..protocols.message import Message
from uptrain import Evals, EvalLLM, Settings as UptrainSettings
from ..utils.logging import setup_logger, get_logger
from ..utils.settings import settings
from itertools import chain

setup_logger()
logger = get_logger("EvalAgent")

class EvalAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("eval_agent")
        uptrain_settings = UptrainSettings(model="gpt-4", openai_api_key=settings.OPENAI_API_KEY)
        self.eval_llm = EvalLLM(uptrain_settings)

    @staticmethod
    def _prepare_input(question: str, answer: str, contexts: List[List[str]]) -> dict:
        flat_contexts = list(chain.from_iterable(contexts))  
        return {
            "question": question,
            "response": answer,
            "context": " ".join(flat_contexts)
        }

    @message_handler
    async def evaluate_answer(self, message: Message, ctx: MessageContext) -> Message:
        try:
            payload = json.loads(message.content)
            logger.info(f"[EvalAgent] Recieved Payload: {payload}")
            data_item = self._prepare_input(payload["question"], payload["answer"], payload["contexts"])
            result = self.eval_llm.evaluate(data=[data_item], checks=[Evals.FACTUAL_ACCURACY])[0]
            logger.info(f"[EvalAgent] Evaluation Result: {result}")
            score = float(result.get("score_factual_accuracy", 0))
            reasoning = result.get("explanation_factual_accuracy", "")
            logger.info(f"[EvalAgent] Score: {score}, Reasoning: {reasoning}")
            return Message(content=json.dumps({
                "score": score,
                "reasoning": reasoning,
                "error": None
            }))

        except Exception as e:
            logger.error(f"[EvalAgent] Evaluation failed : {e}")
            return Message(content=json.dumps({
                "score": 0,
                "reasoning": "",
                "error": str(e)
            }))
