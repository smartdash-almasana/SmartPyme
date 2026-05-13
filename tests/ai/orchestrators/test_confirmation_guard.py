from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from app.ai.orchestrators.owner_confirmation_orchestrator import OwnerConfirmationOrchestrator


@dataclass
class FakeCurationResult:
    status: str = "CURATION_OK"
    cleaned_payload: dict[str, object] | None = None
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.cleaned_payload is None:
            self.cleaned_payload = {
                "objective": "analizar margen",
                "variables": {"period": "2024"},
                "evidence": ["ev-1"],
            }
        if self.errors is None:
            self.errors = []


class FakeCurator:
    def __init__(self, result: FakeCurationResult | None = None) -> None:
        self.result = result or FakeCurationResult()

    def curate_input(self, **kwargs):
        return self.result


class FakeValidator:
    def __init__(self, result: dict[str, object] | None = None) -> None:
        self.result = result or {"status": "CONDITIONS_OK"}

    def validate_operational_conditions(self, **kwargs):
        return self.result


def _confirmation_payload(**overrides):
    payload = {
        "cliente_id": "C1",
        "skill_id": "skill_reconciliation_v1",
        "action": "CONFIRM",
        "overrides": {
            "objective": "analizar margen",
            "variables": {"period": "2024"},
            "evidence": ["ev-1"],
        },
    }
    payload.update(overrides)
    return payload


def test_confirm_job_blocks_blocked_overrides_before_curation_and_persistence() -> None:
    curator = FakeCurator()
    validator = FakeValidator()
    orchestrator = OwnerConfirmationOrchestrator(curator=curator, validator=validator)
    input_data = _confirmation_payload(overrides={"status": "NEEDS_EVIDENCE"})

    with patch("app.ai.orchestrators.owner_confirmation_orchestrator.save_job") as save_job:
        result = orchestrator.confirm_job(input_data)

    assert result["status"] == "REJECTED"
    assert result["error_type"] == "INVALID_JOB_PAYLOAD"
    assert "confirm_job.input.overrides" in result["reason"]
    save_job.assert_not_called()


def test_confirm_job_blocks_curated_payload_status_before_persistence() -> None:
    curator = FakeCurator(
        FakeCurationResult(
            cleaned_payload={
                "objective": "analizar margen",
                "variables": {"period": "2024"},
                "evidence": ["ev-1"],
                "status": "BLOCKED",
            }
        )
    )
    validator = FakeValidator()
    orchestrator = OwnerConfirmationOrchestrator(curator=curator, validator=validator)

    with patch("app.ai.orchestrators.owner_confirmation_orchestrator.save_job") as save_job:
        result = orchestrator.confirm_job(_confirmation_payload())

    assert result["status"] == "REJECTED"
    assert result["error_type"] == "INVALID_JOB_PAYLOAD"
    assert "confirm_job.cleaned_payload" in result["reason"]
    save_job.assert_not_called()


def test_confirm_job_accepts_executable_payload() -> None:
    curator = FakeCurator()
    validator = FakeValidator()
    orchestrator = OwnerConfirmationOrchestrator(curator=curator, validator=validator)

    with patch("app.ai.orchestrators.owner_confirmation_orchestrator.save_job") as save_job:
        result = orchestrator.confirm_job(_confirmation_payload())

    assert result["status"] == "JOB_CREATED"
    save_job.assert_called_once()
