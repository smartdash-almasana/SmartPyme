from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.contracts.execution_guard import enforce_execution_contract


@dataclass
class ContractLike:
    job_id: str = "job-1"
    current_state: str = "RUNNING"
    payload: dict[str, object] | None = None
    blocking_reason: str | None = None


def test_guard_blocks_missing_contract() -> None:
    with pytest.raises(ValueError, match="missing execution contract"):
        enforce_execution_contract(None, context="unit")


@pytest.mark.parametrize("status", ["BLOCKED", "NEEDS_EVIDENCE", "MISSING_CONTRACT"])
def test_guard_blocks_non_executable_status(status: str) -> None:
    contract = {"job_id": "job-1", "current_state": status, "payload": {}}

    with pytest.raises(ValueError, match="contract is not executable"):
        enforce_execution_contract(contract, context="unit")


def test_guard_blocks_missing_required_fields() -> None:
    contract = {"job_id": "job-1", "current_state": "RUNNING"}

    with pytest.raises(ValueError, match="missing required fields: payload"):
        enforce_execution_contract(
            contract,
            context="unit",
            required_fields=("job_id", "current_state", "payload"),
        )


def test_guard_blocks_blocking_reason_without_blocking_status() -> None:
    contract = {
        "job_id": "job-1",
        "current_state": "RUNNING",
        "payload": {},
        "blocking_reason": "faltan datos",
    }

    with pytest.raises(ValueError, match="blocking_reason present without blocking status"):
        enforce_execution_contract(contract, context="unit")


def test_guard_blocks_nested_payload_status() -> None:
    contract = {
        "job_id": "job-1",
        "current_state": "RUNNING",
        "payload": {"status": "NEEDS_EVIDENCE"},
    }

    with pytest.raises(ValueError, match="payload"):
        enforce_execution_contract(contract, context="unit")


def test_guard_accepts_executable_mapping_contract() -> None:
    contract = {
        "job_id": "job-1",
        "current_state": "RUNNING",
        "payload": {"objective": "analizar margen"},
    }

    enforce_execution_contract(
        contract,
        context="unit",
        required_fields=("job_id", "current_state", "payload"),
    )


def test_guard_accepts_object_like_contract() -> None:
    contract = ContractLike(payload={"objective": "analizar margen"})

    enforce_execution_contract(
        contract,
        context="unit",
        required_fields=("job_id", "current_state", "payload"),
    )
