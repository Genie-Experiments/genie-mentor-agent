import json
import os
from itertools import chain
from typing import List
import time

from autogen_core import MessageContext, RoutedAgent, message_handler
from groq import Groq

from ..prompts.evaluation_agent_prompts import (
    EVALUATE_FEW_SHOT_EXAMPLES, EVALUATE_OUTPUT_FORMAT,
    EVALUATE_PROMPTING_INSTRUCTIONS, EVALUATE_SCENARIO_DESCRIPTION,
    FACT_EVAL_PROMPT_TEMPLATE, FACT_EXTRACT_FEW_SHOT_EXAMPLES,
    FACT_EXTRACT_OUTPUT_FORMAT, FACT_EXTRACT_PROMPT_TEMPLATE,
    FACT_EXTRACT_SCENARIO_DESCRIPTION)
from ..protocols.message import Message
from ..protocols.schemas import EvalAgentInput, EvalAgentOutput, LLMUsage
from ..utils.logging import get_logger, setup_logger
from ..utils.parsing import extract_json_with_brace_counting
from ..utils.settings import settings
from ..utils.token_tracker import token_tracker

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

        # Track token usage for fact extraction
        token_tracker.track_completion("eval_agent_fact_extraction", result, self.model)

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

        # Track token usage for fact evaluation
        token_tracker.track_completion("eval_agent_fact_evaluation", result, self.model)

        content = result.choices[0].message.content
        logger.info(f"[EvalAgent] Fact Evaluation Output: {content}")
        parsed = extract_json_with_brace_counting(content)
        return parsed.get("Evaluations")

    def _compute_score_and_reasoning(self, evaluations: List[dict]) -> tuple[float, list]:
        total = len(evaluations)
        yes_count = sum(1 for e in evaluations if e.get("label", "").lower() == "yes")
        score = round(yes_count / total, 2) if total else 0.0

        # Return the list of evaluation dicts as reasoning (JSON-friendly)
        return score, evaluations

    @message_handler
    async def evaluate_answer(self, message: Message, ctx: MessageContext) -> Message:
        start_time = time.time()
        try:

            payload = EvalAgentInput.model_validate_json(message.content)
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
            
            # Get combined token usage for both fact extraction and evaluation
            fact_extraction_usage = token_tracker.get_agent_usage("eval_agent_fact_extraction")
            fact_evaluation_usage = token_tracker.get_agent_usage("eval_agent_fact_evaluation")
            
            # Combine token usage
            combined_usage = None
            if fact_extraction_usage and fact_evaluation_usage:
                combined_usage = LLMUsage(
                    model=fact_extraction_usage.model,
                    input_tokens=fact_extraction_usage.input_tokens + fact_evaluation_usage.input_tokens,
                    output_tokens=fact_extraction_usage.output_tokens + fact_evaluation_usage.output_tokens,
                    total_tokens=fact_extraction_usage.total_tokens + fact_evaluation_usage.total_tokens
                )
            elif fact_extraction_usage:
                combined_usage = LLMUsage(
                    model=fact_extraction_usage.model,
                    input_tokens=fact_extraction_usage.input_tokens,
                    output_tokens=fact_extraction_usage.output_tokens,
                    total_tokens=fact_extraction_usage.total_tokens
                )
            elif fact_evaluation_usage:
                combined_usage = LLMUsage(
                    model=fact_evaluation_usage.model,
                    input_tokens=fact_evaluation_usage.input_tokens,
                    output_tokens=fact_evaluation_usage.output_tokens,
                    total_tokens=fact_evaluation_usage.total_tokens
                )
           
            execution_time_ms = int((time.time() - start_time) * 1000)
            eval_output = EvalAgentOutput(
                score=score, 
                reasoning=reasoning, 
                error=None,
                llm_usage=combined_usage,
                execution_time_ms=execution_time_ms
            )
            
            return Message(content=eval_output.model_dump_json())
            
        except Exception as e:
            logger.error(f"[EvalAgent] Evaluation Failed: {e}")
            execution_time_ms = int((time.time() - start_time) * 1000)
            return Message(content=json.dumps({
                "score": 0,
                "reasoning": "Error Occured During Evaluation",
                "error": str(e),
                "execution_time_ms": execution_time_ms
            }))
