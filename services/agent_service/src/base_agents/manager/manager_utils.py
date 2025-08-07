"""
Shared helpers for ManagerAgent:
• run_editor_pass – calls EditorAgent once
• run_evaluation_loop – drives Eval-then-Edit iterations
"""
from typing import List, Tuple

from ...protocols.message import Message
from ...protocols.schemas import (
    EvalAgentInput,
    EvalAgentOutput,
    EditorAgentInput,
    EditorAgentOutput,
)
from ...utils.logging import get_logger

logger = get_logger("ManagerUtils")

EVALUATION_PASS_THRESHOLD = 1.0
async def run_editor_pass(
    send_message_func,
    editor_agent_id: str,
    question: str,
    previous_answer: str,
    score: float,
    contexts: List[str],
    attempt: int,
) -> Tuple[str, dict]:
    """Single call to the EditorAgent, returns (new_answer, editor_log)."""
    logger.info(f"[EditorAgent] Editing (Attempt {attempt})")

    payload = EditorAgentInput(
        question=question,
        previous_answer=previous_answer,
        score=score,
        contexts=contexts,
    )

    resp = await send_message_func(Message(content=payload.json()), editor_agent_id)
    result = EditorAgentOutput.model_validate_json(resp.content)

    new_answer = result.answer or previous_answer
    editor_log = {
        "editor_history": {
            "answer": new_answer,
            "error": result.error,
            "skipped": False,
        },
        "attempt": attempt,
    }
    return new_answer, editor_log


async def run_evaluation_loop(
    *,
    send_message_func,
    eval_agent_id: str,
    editor_agent_id: str,
    question: str,
    initial_answer: str,
    contexts: List[str],
    documents_by_source: List[str],
    max_attempts: int = 2,
) -> Tuple[str, List[dict], List[dict]]:
    """
    Runs up to `max_attempts` Eval→Edit cycles.
    Returns (final_answer, eval_history, editor_history).
    """
    current_answer = initial_answer
    eval_history: List[dict] = []
    editor_history: List[dict] = []
    
    eval_payload = EvalAgentInput(
        question=question,
        answer=current_answer,
        contexts=contexts,
    )
    eval_resp = await send_message_func(
        Message(content=eval_payload.model_dump_json()), eval_agent_id
    )
    eval_result = EvalAgentOutput.model_validate_json(eval_resp.content)

    # ── 2. Fact Evaluation and Editing Loop ───────────────────────────────────
    logger.info("[EvaluationAgent] Answer is complete, proceeding with fact evaluation and editing.")
    
    for attempt in range(max_attempts):
        logger.info(f"[EvaluationAgent] Fact evaluation (Attempt {attempt + 1})")

        eval_payload = EvalAgentInput(
            question=question,
            answer=current_answer,
            contexts=contexts,
        )
        eval_resp = await send_message_func(
            Message(content=eval_payload.model_dump_json()), eval_agent_id
        )
        eval_result = EvalAgentOutput.model_validate_json(eval_resp.content)

        score = float(eval_result.score)

        # Threshold met → stop looping, no edit needed
        if score >= EVALUATION_PASS_THRESHOLD:
            logger.info("[EvaluationAgent] Score ≥ threshold, skipping edits.")
            break

        # ── Edit ───────────────────────────────────────────────────────────────
        new_answer, editor_log = await run_editor_pass(
            send_message_func=send_message_func,
            editor_agent_id=editor_agent_id,
            question=question,
            previous_answer=current_answer,
            score=score,
            contexts=documents_by_source,
            attempt=attempt + 1,
        )
        editor_history.append(editor_log)
        current_answer = new_answer

    return current_answer, eval_history, editor_history