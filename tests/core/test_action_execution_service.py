import sys
import uuid
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.repositories.action_execution_repository import ActionExecutionRepository

from app.contracts.action_contract import ActionProposal
from app.contracts.execution_adapter_contract import ExecutionAdapter, ExecutionAdapterResult
from app.services.action_execution_service import (
    ActionExecutionService,
    AdapterExecutionError,
    NotApprovedError,
)

# ── helpers ───────────────────────────────────────────────────────────────────

def _proposal(
    action_id: str = "act-1",
    *,
    status: str = "approved",
    traceable_origin: dict | None = None,
) -> ActionProposal:
    return ActionProposal(
        action_id=action_id,
        source_id="src-1",
        source_type="finding",
        title="Acción aprobada",
        description="Descripción.",
        recommended_action="Revisión recomendada",
        status=status,
        requires_confirmation=True,
        traceable_origin=traceable_origin or {},
    )


# ── execute — happy path ──────────────────────────────────────────────────────

def test_execute_approved_returns_executed_proposal():
    service = ActionExecutionService()
    executed = service.execute(_proposal(status="approved"))

    assert executed.status == "executed"


def test_execute_returns_new_instance_not_same_object():
    service = ActionExecutionService()
    original = _proposal(status="approved")
    executed = service.execute(original)

    assert executed is not original


def test_execute_preserves_all_other_fields():
    service = ActionExecutionService()
    origin = {"key": "value"}
    original = _proposal(action_id="act-xyz", traceable_origin=origin)
    executed = service.execute(original)

    assert executed.action_id == "act-xyz"
    assert executed.source_id == original.source_id
    assert executed.source_type == original.source_type
    assert executed.title == original.title
    assert executed.description == original.description
    assert executed.recommended_action == original.recommended_action
    assert executed.requires_confirmation == original.requires_confirmation
    assert executed.traceable_origin == origin


def test_execute_does_not_mutate_original():
    service = ActionExecutionService()
    original = _proposal(status="approved")
    service.execute(original)

    assert original.status == "approved"


def test_execute_preserves_traceable_origin_unchanged():
    service = ActionExecutionService()
    origin = {"finding_id": "f-1", "metric": "price"}
    executed = service.execute(_proposal(traceable_origin=origin))

    assert executed.traceable_origin == origin


# ── execute — guard: non-approved statuses ────────────────────────────────────

def test_execute_proposed_raises_not_approved_error():
    service = ActionExecutionService()
    with pytest.raises(NotApprovedError, match="proposed"):
        service.execute(_proposal(status="proposed"))


def test_execute_rejected_raises_not_approved_error():
    service = ActionExecutionService()
    with pytest.raises(NotApprovedError, match="rejected"):
        service.execute(_proposal(status="rejected"))


def test_execute_already_executed_raises_not_approved_error():
    service = ActionExecutionService()
    with pytest.raises(NotApprovedError, match="executed"):
        service.execute(_proposal(status="executed"))


def test_execute_error_message_contains_action_id():
    service = ActionExecutionService()
    with pytest.raises(NotApprovedError, match="act-special"):
        service.execute(_proposal(action_id="act-special", status="proposed"))


# ── full lifecycle: propose → approve → execute ───────────────────────────────

def test_full_lifecycle_propose_approve_execute():
    from app.services.action_decision_service import ActionDecisionService

    decision_service = ActionDecisionService()
    execution_service = ActionExecutionService()

    proposed = _proposal(status="proposed")
    approved = decision_service.approve(proposed)
    executed = execution_service.execute(approved)

    assert proposed.status == "proposed"
    assert approved.status == "approved"
    assert executed.status == "executed"
    # All three are distinct objects.
    assert proposed is not approved
    assert approved is not executed


def test_full_lifecycle_propose_reject_cannot_execute():
    from app.services.action_decision_service import ActionDecisionService

    decision_service = ActionDecisionService()
    execution_service = ActionExecutionService()

    proposed = _proposal(status="proposed")
    rejected = decision_service.reject(proposed, reason="Fuera de rango.")

    with pytest.raises(NotApprovedError):
        execution_service.execute(rejected)


# ── adapter integration ───────────────────────────────────────────────────────


class _MockAdapter(ExecutionAdapter):
    def __init__(self, status: str = "executed", message: str = "OK") -> None:
        self._status = status
        self._message = message

    @property
    def adapter_id(self) -> str:
        return "mock"

    def execute(self, proposal: Any) -> ExecutionAdapterResult:
        return ExecutionAdapterResult(
            adapter_id=self.adapter_id,
            action_id=proposal.action_id,
            status=self._status,
            message=self._message,
        )


def test_execute_with_adapter_executed_returns_executed_proposal():
    service = ActionExecutionService(adapter=_MockAdapter(status="executed"))
    executed = service.execute(_proposal(status="approved"))
    assert executed.status == "executed"


def test_execute_with_adapter_blocked_raises_adapter_execution_error():
    service = ActionExecutionService(adapter=_MockAdapter(status="blocked", message="Bloqueado."))
    with pytest.raises(AdapterExecutionError, match="blocked"):
        service.execute(_proposal(status="approved"))


def test_execute_with_adapter_failed_raises_adapter_execution_error():
    service = ActionExecutionService(adapter=_MockAdapter(status="failed", message="Error."))
    with pytest.raises(AdapterExecutionError, match="failed"):
        service.execute(_proposal(status="approved"))


def test_execute_with_adapter_error_contains_adapter_id():
    service = ActionExecutionService(adapter=_MockAdapter(status="blocked"))
    with pytest.raises(AdapterExecutionError, match="mock"):
        service.execute(_proposal(status="approved"))


def test_execute_with_adapter_blocked_does_not_mutate_original():
    service = ActionExecutionService(adapter=_MockAdapter(status="blocked"))
    original = _proposal(status="approved")
    try:
        service.execute(original)
    except AdapterExecutionError:
        pass
    assert original.status == "approved"


def test_execute_without_adapter_still_works():
    service = ActionExecutionService()  # no adapter
    executed = service.execute(_proposal(status="approved"))
    assert executed.status == "executed"


def test_execute_guard_fires_before_adapter_call():
    """NotApprovedError must be raised before the adapter is even called."""
    called = []

    class _TrackingAdapter(ExecutionAdapter):
        @property
        def adapter_id(self) -> str:
            return "tracking"

        def execute(self, proposal: Any) -> ExecutionAdapterResult:
            called.append(True)
            return ExecutionAdapterResult(
                adapter_id=self.adapter_id,
                action_id=proposal.action_id,
                status="executed",
                message="OK",
            )

    service = ActionExecutionService(adapter=_TrackingAdapter())
    with pytest.raises(NotApprovedError):
        service.execute(_proposal(status="proposed"))

    assert called == [], "Adapter must not be called for non-approved proposals"


# ── execution_repository integration ─────────────────────────────────────────


def _repo_path() -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_exec_service_repo"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"exec-{uuid.uuid4().hex[:8]}.db"


def test_execute_with_adapter_and_repo_persists_executed_result():
    repo = ActionExecutionRepository(cliente_id="test-client", db_path=_repo_path())
    service = ActionExecutionService(
        adapter=_MockAdapter(status="executed"),
        execution_repository=repo,
    )
    service.execute(_proposal(action_id="act-persist"))

    results = repo.list_results(action_id="act-persist")
    assert len(results) == 1
    assert results[0].status == "executed"
    assert results[0].adapter_id == "mock"


def test_execute_with_adapter_blocked_persists_result_before_raising():
    repo = ActionExecutionRepository(cliente_id="test-client", db_path=_repo_path())
    service = ActionExecutionService(
        adapter=_MockAdapter(status="blocked", message="Bloqueado."),
        execution_repository=repo,
    )
    with pytest.raises(AdapterExecutionError):
        service.execute(_proposal(action_id="act-blocked"))

    results = repo.list_results(action_id="act-blocked")
    assert len(results) == 1
    assert results[0].status == "blocked"


def test_execute_with_adapter_failed_persists_result_before_raising():
    repo = ActionExecutionRepository(cliente_id="test-client", db_path=_repo_path())
    service = ActionExecutionService(
        adapter=_MockAdapter(status="failed", message="Error interno."),
        execution_repository=repo,
    )
    with pytest.raises(AdapterExecutionError):
        service.execute(_proposal(action_id="act-failed"))

    results = repo.list_results(action_id="act-failed")
    assert len(results) == 1
    assert results[0].status == "failed"


def test_execute_guard_fires_before_repo_save():
    """NotApprovedError must be raised before any persistence occurs."""
    repo = ActionExecutionRepository(cliente_id="test-client", db_path=_repo_path())
    service = ActionExecutionService(
        adapter=_MockAdapter(status="executed"),
        execution_repository=repo,
    )
    with pytest.raises(NotApprovedError):
        service.execute(_proposal(status="proposed"))

    assert repo.list_results() == []


def test_execute_without_adapter_does_not_persist():
    """No adapter → no persistence, even if repo is configured."""
    repo = ActionExecutionRepository(cliente_id="test-client", db_path=_repo_path())
    service = ActionExecutionService(execution_repository=repo)
    service.execute(_proposal(action_id="act-no-adapter"))

    assert repo.list_results() == []


def test_execute_with_adapter_no_repo_still_works():
    """Adapter without repo: existing behaviour unchanged."""
    service = ActionExecutionService(adapter=_MockAdapter(status="executed"))
    executed = service.execute(_proposal(status="approved"))
    assert executed.status == "executed"
