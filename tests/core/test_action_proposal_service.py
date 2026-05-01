import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.action_contract import ActionProposal
from app.contracts.communication_contract import FindingMessage, build_message_id
from app.services.action_proposal_service import ActionProposalService
from app.services.findings_service import Finding

# ── helpers ──────────────────────────────────────────────────────────────────

def _finding(
    finding_id: str = "finding-1",
    *,
    entity_id_a: str = "ent-a",
    entity_id_b: str = "ent-b",
    entity_type: str = "cuit",
    metric: str = "price",
    source_a_value: Any = 1500.25,
    source_b_value: Any = 1800.00,
    difference: float = 299.75,
    difference_pct: float = 20.0,
    severity: str = "ALTO",
    suggested_action: str = "Revisión recomendada",
    traceable_origin: dict | None = None,
) -> Finding:
    return Finding(
        finding_id=finding_id,
        entity_id_a=entity_id_a,
        entity_id_b=entity_id_b,
        entity_type=entity_type,
        metric=metric,
        source_a_value=source_a_value,
        source_b_value=source_b_value,
        difference=difference,
        difference_pct=difference_pct,
        severity=severity,
        suggested_action=suggested_action,
        traceable_origin=traceable_origin or {},
    )


def _message(
    finding_id: str = "finding-1",
    *,
    severity: str = "ALTO",
    action_text: str = "Revisión recomendada",
    traceable_origin: dict | None = None,
) -> FindingMessage:
    msg_id = build_message_id(finding_id, "internal")
    return FindingMessage(
        message_id=msg_id,
        finding_id=finding_id,
        channel="internal",
        title=f"[{severity}] Diferencia detectada",
        body="Cuerpo del mensaje.",
        action_text=action_text,
        severity=severity,
        traceable_origin=traceable_origin or {},
    )


# ── propose_from_finding ─────────────────────────────────────────────────────

def test_propose_from_finding_returns_action_proposal():
    service = ActionProposalService()
    proposal = service.propose_from_finding(_finding())
    assert isinstance(proposal, ActionProposal)


def test_propose_from_finding_status_is_proposed():
    service = ActionProposalService()
    proposal = service.propose_from_finding(_finding())
    assert proposal.status == "proposed"


def test_propose_from_finding_source_type_is_finding():
    service = ActionProposalService()
    proposal = service.propose_from_finding(_finding())
    assert proposal.source_type == "finding"


def test_propose_from_finding_source_id_is_finding_id():
    service = ActionProposalService()
    proposal = service.propose_from_finding(_finding("f-xyz"))
    assert proposal.source_id == "f-xyz"


def test_propose_from_finding_action_id_is_deterministic():
    service = ActionProposalService()
    f = _finding("f-stable")
    p1 = service.propose_from_finding(f)
    p2 = service.propose_from_finding(f)
    assert p1.action_id == p2.action_id
    assert p1.action_id.startswith("action_")


def test_propose_from_finding_recommended_action_matches_suggested_action():
    service = ActionProposalService()
    proposal = service.propose_from_finding(
        _finding(suggested_action="Revisión inmediata requerida")
    )
    assert proposal.recommended_action == "Revisión inmediata requerida"


def test_propose_from_finding_title_contains_severity_and_metric():
    service = ActionProposalService()
    proposal = service.propose_from_finding(_finding(severity="CRITICO", metric="amount"))
    assert "CRITICO" in proposal.title
    assert "amount" in proposal.title


def test_propose_from_finding_description_contains_entity_ids_and_values():
    service = ActionProposalService()
    proposal = service.propose_from_finding(
        _finding(entity_id_a="ent-001", entity_id_b="ent-002",
                 source_a_value=100.0, source_b_value=200.0)
    )
    assert "ent-001" in proposal.description
    assert "ent-002" in proposal.description
    assert "100" in proposal.description
    assert "200" in proposal.description


def test_propose_from_finding_preserves_traceable_origin():
    origin = {"finding_id": "f-1", "metric": "price"}
    service = ActionProposalService()
    proposal = service.propose_from_finding(_finding(traceable_origin=origin))
    assert proposal.traceable_origin == origin


def test_propose_from_finding_requires_confirmation_for_high_severity():
    service = ActionProposalService()
    for severity in ("CRITICO", "ALTO", "MEDIO"):
        proposal = service.propose_from_finding(_finding(severity=severity))
        assert proposal.requires_confirmation is True, f"Expected True for {severity}"


def test_propose_from_finding_no_confirmation_for_low_severity():
    service = ActionProposalService()
    for severity in ("BAJO", "INFO"):
        proposal = service.propose_from_finding(_finding(severity=severity))
        assert proposal.requires_confirmation is False, f"Expected False for {severity}"


# ── propose_from_message ─────────────────────────────────────────────────────

def test_propose_from_message_returns_action_proposal():
    service = ActionProposalService()
    proposal = service.propose_from_message(_message())
    assert isinstance(proposal, ActionProposal)


def test_propose_from_message_status_is_proposed():
    service = ActionProposalService()
    proposal = service.propose_from_message(_message())
    assert proposal.status == "proposed"


def test_propose_from_message_source_type_is_message():
    service = ActionProposalService()
    proposal = service.propose_from_message(_message())
    assert proposal.source_type == "message"


def test_propose_from_message_source_id_is_message_id():
    service = ActionProposalService()
    msg = _message("f-1")
    proposal = service.propose_from_message(msg)
    assert proposal.source_id == msg.message_id


def test_propose_from_message_title_matches_message_title():
    service = ActionProposalService()
    msg = _message()
    proposal = service.propose_from_message(msg)
    assert proposal.title == msg.title


def test_propose_from_message_recommended_action_matches_action_text():
    service = ActionProposalService()
    msg = _message(action_text="Revisión inmediata requerida")
    proposal = service.propose_from_message(msg)
    assert proposal.recommended_action == "Revisión inmediata requerida"


def test_propose_from_message_preserves_traceable_origin():
    origin = {"key": "val"}
    service = ActionProposalService()
    proposal = service.propose_from_message(_message(traceable_origin=origin))
    assert proposal.traceable_origin == origin


# ── propose_batch_from_messages ───────────────────────────────────────────────

def test_propose_batch_from_messages_returns_one_per_message():
    service = ActionProposalService()
    messages = [_message("f-1"), _message("f-2"), _message("f-3")]
    proposals = service.propose_batch_from_messages(messages)
    assert len(proposals) == 3


def test_propose_batch_from_messages_empty_input():
    service = ActionProposalService()
    assert service.propose_batch_from_messages([]) == []


def test_propose_batch_all_status_proposed():
    service = ActionProposalService()
    messages = [_message("f-1"), _message("f-2")]
    proposals = service.propose_batch_from_messages(messages)
    assert all(p.status == "proposed" for p in proposals)
