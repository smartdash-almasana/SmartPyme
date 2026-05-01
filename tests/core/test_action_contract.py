import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.action_contract import ActionProposal


def test_action_proposal_is_dataclass():
    from dataclasses import fields
    field_names = {f.name for f in fields(ActionProposal)}
    required = {
        "action_id", "source_id", "source_type", "title", "description",
        "recommended_action", "status", "requires_confirmation", "traceable_origin",
    }
    assert required.issubset(field_names)


def test_action_proposal_default_status_is_proposed():
    proposal = ActionProposal(
        action_id="act-1",
        source_id="src-1",
        source_type="finding",
        title="T",
        description="D",
        recommended_action="R",
    )
    assert proposal.status == "proposed"


def test_action_proposal_default_requires_confirmation_is_true():
    proposal = ActionProposal(
        action_id="act-1",
        source_id="src-1",
        source_type="finding",
        title="T",
        description="D",
        recommended_action="R",
    )
    assert proposal.requires_confirmation is True


def test_action_proposal_default_traceable_origin_is_empty_dict():
    proposal = ActionProposal(
        action_id="act-1",
        source_id="src-1",
        source_type="finding",
        title="T",
        description="D",
        recommended_action="R",
    )
    assert proposal.traceable_origin == {}


def test_action_proposal_is_frozen():
    proposal = ActionProposal(
        action_id="act-1",
        source_id="src-1",
        source_type="finding",
        title="T",
        description="D",
        recommended_action="R",
    )
    try:
        object.__setattr__(proposal, "status", "approved")
        raise AssertionError("Should have raised FrozenInstanceError")
    except Exception:
        pass


def test_action_proposal_valid_statuses():
    for status in ("proposed", "approved", "rejected", "executed"):
        p = ActionProposal(
            action_id="act-1",
            source_id="src-1",
            source_type="finding",
            title="T",
            description="D",
            recommended_action="R",
            status=status,
        )
        assert p.status == status
