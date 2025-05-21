from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .message import Message  


_handler = logging.StreamHandler()
logger = logging.getLogger("editor_agent")
logger.setLevel(logging.INFO)       
logger.addHandler(_handler)
logger.propagate = False


class EditorAgent(RoutedAgent):

    def __init__(self) -> None:
        super().__init__("editor_agent")

        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

       

   
    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> Message:  # noqa: D401
        
        data: Dict[str, Any] = json.loads(message.content)
        logger.info("Incoming payload:\n%s", json.dumps(data, indent=2))

        correction_prompt = self._build_prompt(data)

        response = await self.model_client.create(
            messages=[UserMessage(content=correction_prompt, source=self.id.key)]
        )


        outgoing = Message(
            content=json.dumps(
                {
                    "question": data["question"],
                    "context": data["context"],
                    "answer": response.content,
                    "explanation_factual_accuracy": data.get("explanation", ""),
                    "correction_attempt": data.get("correction_attempt", 0),
                }
            )
        )

        logger.debug("Outgoing payload:\n%s", outgoing.content)
        return outgoing

   
    @staticmethod
    def _build_prompt(data: Dict[str, Any]) -> str:
        return (
            "You are **EditorGPT**.  Your job is to FIX factual issues in the answer so it "
            "is fully supported by the supplied *Context*.\n\n"
            "──────────────────────────────── CONTEXT ────────────────────────────────\n"
            f"{data['context']}\n"
            "──────────────────────────────── QUESTION ───────────────────────────────\n"
            f"{data['question']}\n"
            "──────────────────────────── PREVIOUS ANSWER ────────────────────────────\n"
            f"{data['answer']}\n"
            "──────────────────────────── IDENTIFIED ISSUES ──────────────────────────\n"
            f"{data.get('explanation', 'No specific issues provided.')}\n\n"
            "=========================  EDITING INSTRUCTIONS  =========================\n"
            "1. Read the issues above and correct ONLY those errors.\n"
            "2. Keep any parts that are already correct and useful.\n"
            "3. Remove or re-write statements not supported by the context.\n"
            "4. Do **NOT** introduce new facts that are not in the context.\n"
            "5. Write in the same voice as the original answer unless changes are needed for clarity.\n"
            "6. Return **just the revised answer text** — no extra commentary, no markdown headings.\n"
            "=========================================================================="
        )

