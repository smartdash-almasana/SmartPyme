import pytest
from app.contracts.action_contract import ActionProposal

def test_action_proposal_defaults():
    proposal = ActionProposal(
        action_id="a1", source_id="s1", source_type="finding",
        title="T", description="D", recommended_action="R"
    )
    assert proposal.action_type == "GENERAL"
    assert proposal.case_id is None

def test_action_proposal_with_operational_data():
    proposal = ActionProposal(
        action_id="a1", source_id="s1", source_type="finding",
        title="T", description="D", recommended_action="R",
        action_type="CASE_CLOSED", case_id="case_123", report_id="rep_123"
    )
    assert proposal.action_type == "CASE_CLOSED"
    assert proposal.case_id == "case_123"
    assert proposal.report_id == "rep_123"
