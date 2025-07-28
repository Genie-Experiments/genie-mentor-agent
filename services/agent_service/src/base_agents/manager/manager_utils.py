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
    reasoning,
    contexts: List[str],
    attempt: int,
) -> Tuple[str, dict]:
    """Single call to the EditorAgent, returns (new_answer, editor_log)."""
    logger.info(f"[EditorAgent] Editing (Attempt {attempt})")

    # Convert reasoning to string format for editor agent
    if isinstance(reasoning, list):
        reasoning_str = "\n".join([
            f"- {item.get('type', 'fact')}: {item.get('message', str(item))}"
            for item in reasoning
        ])
    else:
        reasoning_str = str(reasoning) if reasoning else ""

    payload = EditorAgentInput(
        question=question,
        previous_answer=previous_answer,
        score=score,
        reasoning=reasoning_str,
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
) -> Tuple[str, List[dict], List[dict], dict]:
    """
    Runs up to `max_attempts` Eval→Edit cycles.
    Returns (final_answer, eval_history, editor_history, completeness_info).
    """
    current_answer = initial_answer
    eval_history: List[dict] = []
    editor_history: List[dict] = []
    completeness_info = {"is_incomplete": False, "details": None}

    # ── 1. Completeness Check ─────────────────────────────────────────
    logger.info(f"[EvaluationAgent] Initial completeness check")
    
    eval_payload = EvalAgentInput(
        question=question,
        answer=current_answer,
        contexts=contexts,
    )
    eval_resp = await send_message_func(
        Message(content=eval_payload.model_dump_json()), eval_agent_id
    )
    eval_result = EvalAgentOutput.model_validate_json(eval_resp.content)

    # Extract completeness details
    completeness_details = None
    if isinstance(eval_result.reasoning, list):
        for item in eval_result.reasoning:
            if isinstance(item, dict) and item.get("type") in ["completeness_check", "completeness_warning"]:
                completeness_details = {
                    "is_complete": item.get("type") == "completeness_check",
                    "reasoning": item.get("assessment", item.get("message", "No reasoning provided"))
                }
                break

    # Check if answer is incomplete
    is_incomplete = False
    if isinstance(eval_result.reasoning, list):
        for item in eval_result.reasoning:
            if isinstance(item, dict) and item.get("type") == "completeness_warning":
                is_incomplete = True
                break
    elif isinstance(eval_result.reasoning, str) and "completeness_warning" in eval_result.reasoning.lower():
        is_incomplete = True

    # Log initial completeness check
    eval_history.append({
        "execution_time_ms": getattr(eval_result, "execution_time_ms", None),
        "evaluation_history": {
            "score": float(eval_result.score),
            "reasoning": eval_result.reasoning,
            "error": eval_result.error,
            "llm_usage": eval_result.llm_usage.model_dump() if eval_result.llm_usage else None,
        },
        "attempt": 1,
        "completeness_details": completeness_details
    })
    
    logger.info(f"[ManagerUtils] Initial completeness check - Completeness details: {completeness_details}")

    # If incomplete, return early
    if is_incomplete:
        logger.info("[EvaluationAgent] Answer is incomplete, skipping fact evaluation and editing.")
        completeness_info = {"is_incomplete": True, "details": completeness_details}
        return current_answer, eval_history, editor_history, completeness_info

    # ── 2. Fact Evaluation and Editing Loop ───────────────────────────────────
    logger.info("[EvaluationAgent] Answer is complete, proceeding with fact evaluation and editing.")
    
    for attempt in range(max_attempts):
        # Evaluate facts (completeness already checked)
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
        
        # Extract completeness details from every evaluation attempt
        completeness_details = None
        if isinstance(eval_result.reasoning, list):
            for item in eval_result.reasoning:
                if isinstance(item, dict) and item.get("type") in ["completeness_check", "completeness_warning"]:
                    completeness_details = {
                        "is_complete": item.get("type") == "completeness_check",
                        "reasoning": item.get("assessment", item.get("message", "No reasoning provided"))
                    }
                    break
        
        # Filter out completeness items from reasoning for fact evaluation
        if isinstance(eval_result.reasoning, list):
            reasoning = [
                item for item in eval_result.reasoning 
                if not (isinstance(item, dict) and item.get("type") in ["completeness_check", "completeness_warning"])
            ]
        else:
            reasoning = eval_result.reasoning
        error = eval_result.error
        llm_usage = eval_result.llm_usage.model_dump() if eval_result.llm_usage else None
        execution_time_ms = getattr(eval_result, "execution_time_ms", None)

        eval_history.append({
            "execution_time_ms": execution_time_ms,
            "evaluation_history": {
                "score": score,
                "reasoning": reasoning,
                "error": error,
                "llm_usage": llm_usage,
            },
            "attempt": attempt + 2,  # +2 because attempt 1 was completeness check
            "completeness_details": completeness_details
        })
        
        logger.info(f"[ManagerUtils] Evaluation attempt {attempt + 2} - Completeness details: {completeness_details}")

        # Handle evaluation error
        if error is not None:
            logger.error(f"[ManagerUtils] EvalAgent returned error: {error}")
            break

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
            reasoning=reasoning,
            contexts=documents_by_source,
            attempt=attempt + 1,
        )
        editor_history.append(editor_log)
        current_answer = new_answer

    return current_answer, eval_history, editor_history, completeness_info