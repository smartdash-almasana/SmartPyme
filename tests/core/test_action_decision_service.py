import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.action_contract import ActionProposal
from app.services.action_decision_service import ActionDecisionService, InvalidDecisionError


# ── helpers ──────────────────────────────────────────────────────────────────

def _proposal(
    action_id: str = "act-1",
    *,
    status: str = "proposed",
    requires_confirmation: bool = True,
    traceable_origin: dict | None = None,
) -> ActionProposal:
    return ActionProposal(
        action_id=action_id,
        source_id="src-1",
        source_type="finding",
        title="Acción propuesta",
        description="Descripción de la acción.",
        recommended_action="Revisión recomendada",
        status=status,
        requires_confirmation=requires_confirmation,
        traceable_origin=traceable_origin or {},
    )


# ── approve ───────────────────────────────────────────────────────────────────

def test_approve_returns_new_proposal_with_approved_status():
    service = ActionDecisionService()
    original = _proposal(status="proposed")
    approved = service.approve(original)

    assert approved.status == "approved"


def test_approve_returns_new_instance_not_same_object():
    service = ActionDecisionService()
    original = _proposal()
    approved = service.approve(original)

    assert approved is not original


def test_approve_preserves_all_other_fields():
    service = ActionDecisionService()
    origin = {"key": "value"}
    original = _proposal(action_id="act-xyz", traceable_origin=origin)
    approved = service.approve(original)

    assert approved.action_id == "act-xyz"
    assert approved.source_id == original.source_id
    assert approved.source_type == original.source_type
    assert approved.title == original.title
    assert approved.description == original.description
    assert approved.recommended_action == original.recommended_action
    assert approved.requires_confirmation == original.requires_confirmation
    assert approved.traceable_origin == origin


def test_approve_already_proposed_succeeds():
    service = ActionDecisionService()
    approved = service.approve(_proposal(status="proposed"))
    assert approved.status == "approved"


def test_approve_already_approved_succeeds():
    service = ActionDecisionService()
    # Re-approving an already-approved proposal is allowed (idempotent-ish).
    approved = service.approve(_proposal(status="approved"))
    assert approved.status == "approved"


def test_approve_already_rejected_succeeds():
    service = ActionDecisionService()
    # Overriding a rejection with an approval is allowed.
    approved = service.approve(_proposal(status="rejected"))
    assert approved.status == "approved"


def test_approve_executed_raises_invalid_decision_error():
    service = ActionDecisionService()
    with pytest.raises(InvalidDecisionError, match="already executed"):
        service.approve(_proposal(status="executed"))


# ── reject ────────────────────────────────────────────────────────────────────

def test_reject_returns_new_proposal_with_rejected_status():
    service = ActionDecisionService()
    rejected = service.reject(_proposal())

    assert rejected.status == "rejected"


def test_reject_returns_new_instance_not_same_object():
    service = ActionDecisionService()
    original = _proposal()
    rejected = service.reject(original)

    assert rejected is not original


def test_reject_preserves_all_other_fields_without_reason():
    service = ActionDecisionService()
    original = _proposal(action_id="act-abc", traceable_origin={"k": "v"})
    rejected = service.reject(original)

    assert rejected.action_id == "act-abc"
    assert rejected.source_id == original.source_id
    assert rejected.traceable_origin == {"k": "v"}


def test_reject_with_reason_appends_to_traceable_origin():
    service = ActionDecisionService()
    original = _proposal(traceable_origin={"existing": "data"})
    rejected = service.reject(original, reason="Monto fuera de rango aceptable.")

    assert rejected.traceable_origin["rejection_reason"] == "Monto fuera de rango aceptable."
    assert rejected.traceable_origin["existing"] == "data"


def test_reject_without_reason_does_not_add_rejection_reason_key():
    service = ActionDecisionService()
    rejected = service.reject(_proposal(traceable_origin={}))

    assert "rejection_reason" not in rejected.traceable_origin


def test_reject_executed_raises_invalid_decision_error():
    service = ActionDecisionService()
    with pytest.raises(InvalidDecisionError, match="already executed"):
        service.reject(_proposal(status="executed"))


def test_reject_already_approved_succeeds():
    service = ActionDecisionService()
    rejected = service.reject(_proposal(status="approved"), reason="Cambio de criterio.")
    assert rejected.status == "rejected"
    assert rejected.traceable_origin["rejection_reason"] == "Cambio de criterio."


# ── original immutability ─────────────────────────────────────────────────────

def test_approve_does_not_mutate_original():
    service = ActionDecisionService()
    original = _proposal(status="proposed")
    service.approve(original)

    assert original.status == "proposed"


def test_reject_does_not_mutate_original():
    service = ActionDecisionService()
    original = _proposal(traceable_origin={"k": "v"})
    service.reject(original, reason="Razón de rechazo.")

    assert "rejection_reason" not in original.traceable_origin
    assert original.status == "proposed"
