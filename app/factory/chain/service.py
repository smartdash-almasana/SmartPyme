from typing import Any

from app.factory.chain.models import ChainExecutionResult, ChainStep
from app.factory.skills.registry import SkillRegistry
from app.factory.skills.runner import run_skill


def run_skill_chain(
    steps: list[ChainStep],
    initial_payload: dict[str, Any],
    registry: SkillRegistry | None = None,
) -> ChainExecutionResult:
    if not steps:
        return ChainExecutionResult(
            status="error",
            completed_steps=[],
            final_output=None,
            failed_step_id=None,
            error_code="CHAIN_EMPTY",
            error_message="La cadena de skills esta vacia.",
        )

    completed_steps: list[str] = []
    current_payload: dict[str, Any] = initial_payload

    for step in steps:
        result = run_skill(step.skill_id, current_payload, registry=registry)
        if result["status"] == "error":
            return ChainExecutionResult(
                status="blocked",
                completed_steps=completed_steps,
                final_output=None,
                failed_step_id=step.step_id,
                error_code=result.get("error_code"),
                error_message=result.get("error_message"),
            )

        completed_steps.append(step.step_id)
        current_payload = result["output"]

    return ChainExecutionResult(
        status="ok",
        completed_steps=completed_steps,
        final_output=current_payload,
        failed_step_id=None,
        error_code=None,
        error_message=None,
    )
