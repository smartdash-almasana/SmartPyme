from app.factory.orchestrator.models import (
    STATE_BLOCKED,
    STATE_COMPLETED,
    STATE_CREATED,
    STATE_RUNNING,
    Job,
)
from app.factory.orchestrator.persistence import save_job
from app.factory.orchestrator.transitions import ensure_transition_allowed
from app.factory.skills.registry import SkillRegistry
from app.factory.skills.runner import run_skill


class OrchestrationStateError(ValueError):
    pass


def _transition(job: Job, to_state: str) -> None:
    ensure_transition_allowed(job.current_state, to_state)
    job.current_state = to_state


def _block_job(job: Job, reason: str, error_code: str) -> Job:
    _transition(job, STATE_BLOCKED)
    job.status = "blocked"
    job.output = None
    job.blocking_reason = reason
    job.error_code = error_code
    save_job(job) # Persist final blocked state
    return job


def orchestrate_job(job: Job, registry: SkillRegistry | None = None) -> Job:
    if job.current_state != STATE_CREATED:
        raise OrchestrationStateError(
            f"Solo se puede orquestar desde CREATED. Estado actual: {job.current_state}"
        )
    
    # It is assumed the caller has already saved the initial CREATED state.
    # Persist the transition to RUNNING.
    _transition(job, STATE_RUNNING)
    job.status = "running"
    save_job(job)

    if not job.skill_id:
        return _block_job(
            job,
            reason="Falta skill_id; no se puede ejecutar el trabajo.",
            error_code="SKILL_ID_MISSING",
        )

    result = run_skill(job.skill_id, job.payload, registry=registry)
    if result["status"] == "ok":
        _transition(job, STATE_COMPLETED)
        job.status = "ok"
        job.output = result["output"]
        job.blocking_reason = None
        job.error_code = None
        save_job(job) # Persist final completed state
        return job

    error_code = result.get("error_code") or "SKILL_EXECUTION_ERROR"
    error_message = result.get("error_message") or "Error de ejecucion de skill"

    return _block_job(
        job,
        reason=f"Trabajo bloqueado por falla de skill: {error_message}",
        error_code=error_code,
    )
