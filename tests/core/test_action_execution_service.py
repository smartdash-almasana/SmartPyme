import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.action_contract import ActionProposal
from app.services.action_execution_service import ActionExecutionService, NotApprovedError


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
