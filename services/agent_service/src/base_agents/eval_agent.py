import json
import os
from itertools import chain
from typing import List
from itertools import chain
from autogen_core import RoutedAgent, MessageContext, message_handler
from autogen_core import MessageContext, RoutedAgent, message_handler
from ..protocols.message import Message
from ..prompts.evaluation_agent_prompts import (
    FACT_EXTRACT_PROMPT_TEMPLATE, 
    FACT_EXTRACT_SCENARIO_DESCRIPTION, 
    FACT_EXTRACT_FEW_SHOT_EXAMPLES, 
    FACT_EXTRACT_OUTPUT_FORMAT,
    FACT_EVAL_PROMPT_TEMPLATE,
    EVALUATE_PROMPTING_INSTRUCTIONS,
    EVALUATE_FEW_SHOT_EXAMPLES,
    EVALUATE_OUTPUT_FORMAT,
    EVALUATE_SCENARIO_DESCRIPTION )
from ..utils.parsing import extract_json_with_brace_counting
from ..protocols.schemas import EvalAgentInput,EvalAgentOutput

from groq import Groq
from ..utils.logging import get_logger, setup_logger
from ..utils.settings import settings

setup_logger()
logger = get_logger("EvalAgent")

class EvalAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("eval_agent")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.WEBRAG_LLM_DEFAULT_MODEL

    def _flatten_context(self, contexts: List[List[str]]) -> str:
        return " ".join(chain.from_iterable(contexts))

    async def _extract_facts(self, question: str, response: str) -> List[str]:
        prompt = FACT_EXTRACT_PROMPT_TEMPLATE.format(
            scenario_description=FACT_EXTRACT_SCENARIO_DESCRIPTION,
            few_shot_examples=FACT_EXTRACT_FEW_SHOT_EXAMPLES,
            output_format=FACT_EXTRACT_OUTPUT_FORMAT,
            question=question,
            response=response
        )

        result = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        content = result.choices[0].message.content
        logger.info(f"[EvalAgent] Fact Extraction Output: {content}")
        parsed = extract_json_with_brace_counting(content)
        return parsed.get("Facts")

    async def _evaluate_facts(self, facts: List[str], context: str) -> List[dict]:
        formatted_facts = ", ".join(facts)

        prompt = FACT_EVAL_PROMPT_TEMPLATE.format(
        prompting_instructions=EVALUATE_PROMPTING_INSTRUCTIONS,
        scenario_description=EVALUATE_SCENARIO_DESCRIPTION,
        few_shot_examples=EVALUATE_FEW_SHOT_EXAMPLES,
        output_format=EVALUATE_OUTPUT_FORMAT,
        facts=formatted_facts,
        context=context
    )

        result = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        content = result.choices[0].message.content
        logger.info(f"[EvalAgent] Fact Evaluation Output: {content}")
        parsed = extract_json_with_brace_counting(content)
        return parsed.get("Evaluations")

    def _compute_score_and_reasoning(self, evaluations: List[dict]) -> tuple[float, str]:
        total = len(evaluations)
        yes_count = sum(1 for e in evaluations if e.get("label", "").lower() == "yes")
        score = round(yes_count / total, 2) if total else 0.0

        reasoning_lines = []
        for e in evaluations:
            reasoning_lines.append(f"• **Fact**: {e['fact']}\n  - **Label**: {e['label']}\n  - **Reason**: {e['reasoning']}")
        full_reasoning = "\n".join(reasoning_lines)

        return score, full_reasoning

    @message_handler
    async def evaluate_answer(self, message: Message, ctx: MessageContext) -> Message:
        try:
            print("---------Received Message-----------")
            print(message.content)
            payload = EvalAgentInput.model_validate_json(message.content)
            print(payload)
            question = payload.question
            response = payload.answer
            contexts = payload.contexts
            context_text = self._flatten_context(contexts)

            logger.info(f"[EvalAgent] Received Payload: {payload}")

            facts = await self._extract_facts(question, response)
            if not facts:
                raise ValueError("[EvalAgent] No facts could be extracted from the response.")

            evaluations = await self._evaluate_facts(facts, context_text)
            score, reasoning = self._compute_score_and_reasoning(evaluations)
           
            return Message(content=EvalAgentOutput
                           (score=score, 
                            reasoning=reasoning, 
                            error=None).model_dump_json())
            
        except Exception as e:
            logger.error(f"[EvalAgent] Evaluation Failed: {e}")
            return Message(content=json.dumps({
                "score": 0,
                "reasoning": "Error Occured During Evaluation",
                "error": str(e)
            }))
