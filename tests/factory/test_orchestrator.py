import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.factory.orchestrator.models import (
    STATE_BLOCKED,
    STATE_COMPLETED,
    STATE_CREATED,
    Job,
)
from app.factory.orchestrator.service import OrchestrationStateError, orchestrate_job
from app.factory.orchestrator.transitions import InvalidTransitionError, ensure_transition_allowed


def test_orchestrate_created_job_completes_with_valid_skill():
    job = Job(job_id="job-1", skill_id="echo_skill", payload={"message": "hola"})

    result = orchestrate_job(job)

    assert result.current_state == STATE_COMPLETED
    assert result.status == "ok"
    assert result.output == {"echoed_message": "hola"}
    assert result.blocking_reason is None
    assert result.error_code is None


def test_orchestrate_created_job_blocks_with_unknown_skill():
    job = Job(job_id="job-2", skill_id="skill_inexistente", payload={"message": "hola"})

    result = orchestrate_job(job)

    assert result.current_state == STATE_BLOCKED
    assert result.status == "blocked"
    assert result.output is None
    assert result.error_code == "SKILL_NOT_FOUND"
    assert "falla de skill" in (result.blocking_reason or "")


def test_orchestrate_created_job_blocks_with_invalid_payload():
    job = Job(job_id="job-3", skill_id="echo_skill", payload={"message": 123})

    result = orchestrate_job(job)

    assert result.current_state == STATE_BLOCKED
    assert result.status == "blocked"
    assert result.output is None
    assert result.error_code == "INPUT_SCHEMA_INVALID"


def test_orchestrate_created_job_blocks_when_skill_id_missing():
    job = Job(job_id="job-4", skill_id=None, payload={"message": "hola"})

    result = orchestrate_job(job)

    assert result.current_state == STATE_BLOCKED
    assert result.status == "blocked"
    assert result.output is None
    assert result.error_code == "SKILL_ID_MISSING"
    assert "Falta skill_id" in (result.blocking_reason or "")


def test_invalid_transition_is_rejected():
    with pytest.raises(InvalidTransitionError):
        ensure_transition_allowed(STATE_CREATED, STATE_COMPLETED)


def test_job_not_in_created_cannot_be_orchestrated_again():
    job = Job(
        job_id="job-5",
        current_state=STATE_COMPLETED,
        status="ok",
        skill_id="echo_skill",
        payload={"message": "hola"},
    )

    with pytest.raises(OrchestrationStateError):
        orchestrate_job(job)
