from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from uptrain import EvalLLM, Evals

from .message import Message

logger = logging.getLogger("evaluation_agent")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())



class EvaluationAgent(RoutedAgent):
    """Run UpTrain factual-accuracy check.  
    If incorrect and caller allows another correction, pass to EditorAgent **once** and return
    the edited answer; do **not** recurse back into ourselves.
    """

    def __init__(self) -> None:
        super().__init__("evaluation_agent")
        self.eval_llm = EvalLLM(openai_api_key=os.getenv("OPENAI_API_KEY"))
        logger.debug("Initialised EvaluationAgent (UpTrain backend)")

  
    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> Message:
        try:
            data: Dict[str, Any] = json.loads(message.content)
            logger.info("Incoming payload:\n%s", json.dumps(data, indent=2))

            evaluation = await self._evaluate_response(
                question=data["question"],
                context=data["context"],
                answer=data["answer"],
                attempt=data.get("correction_attempt", 0),
            )
            logger.info(
                "UpTrain result: %s (score %.2f)",
                evaluation["response_verified"],
                evaluation["factual_accuracy_score"],
            )

            max_attempts = data.get("max_corrections", 0) 
            if (
                evaluation["response_verified"] == "Incorrect"
                and evaluation["correction_attempt"] < max_attempts
            ):
                return await self._edit_once(data, evaluation)

            return Message(content=json.dumps(evaluation))

        except Exception as exc:
            logger.exception("EvaluationAgent crashed:")
            return Message(
                content=json.dumps(
                    {
                        "response_verified": "Incorrect",
                        "error": str(exc),
                        "factual_accuracy_score": 0.0,
                        "explanation_factual_accuracy": "Evaluation failed",
                    }
                )
            )

    
    async def _evaluate_response(
        self, *, question: str, context: str, answer: str, attempt: int
    ) -> Dict[str, Any]:
        result = self.eval_llm.evaluate(
            data=[{"question": question, "context": context, "response": answer}],
            checks=[Evals.FACTUAL_ACCURACY],
        )[0]

        return {
            "response_verified": "Correct"
            if result["score_factual_accuracy"] == 1.0
            else "Incorrect",
            "factual_accuracy_score": result["score_factual_accuracy"],
            "explanation_factual_accuracy": result["explanation_factual_accuracy"],
            "correction_attempt": attempt,
            "answer": answer,
            "error": None,
        }

    async def _edit_once(
        self,
        original: Dict[str, Any],
        evaluation: Dict[str, Any],
    ) -> Message:
        """Call EditorAgent a single time and return its answer to the caller."""
        attempt = evaluation["correction_attempt"] + 1
        logger.info("Forwarding to EditorAgent (attempt %d)", attempt)

        editor_payload = {
            "question": original["question"],
            "context": original["context"],
            "answer": original["answer"],
            "explanation": evaluation["explanation_factual_accuracy"],
            "correction_attempt": attempt,
        }

        editor_response = await self.send_message(
            Message(content=json.dumps(editor_payload)),
            AgentId("editor_agent", "default"),
        )
        return editor_response
