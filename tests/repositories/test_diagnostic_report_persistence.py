import pytest
from app.repositories.operational_case_repository import OperationalCaseRepository
from app.contracts.operational_case_contract import DiagnosticReport, FindingRecord, QuantifiedImpact

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"

@pytest.fixture
def repo(db_path):
    return OperationalCaseRepository(cliente_id="C1", db_path=db_path)

def test_diagnostic_report_persistence(repo):
    impact = QuantifiedImpact(amount=100.0, currency="USD")
    finding = FindingRecord(
        entity="e1", finding_type="t1", measured_difference={"diff": 10},
        compared_sources=["s1"], evidence_used=["ev1"], severity="LOW", recommendation="rec"
    )
    report = DiagnosticReport(
        report_id="r1", case_id="c1", cliente_id="C1", job_id="j1",
        hypothesis="Investigar si A?", diagnosis_status="CONFIRMED",
        findings=[finding], evidence_used=["ev1"], formulas_used=["f1"],
        quantified_impact=impact, reasoning_summary="...",
        proposed_next_actions=["..."], owner_question="..."
    )
    
    repo.create_report(report)
    
    fetched = repo.get_report("r1")
    assert fetched is not None
    assert fetched.report_id == "r1"
    assert fetched.quantified_impact.amount == 100.0
    assert len(fetched.findings) == 1

def test_diagnostic_report_isolation(db_path):
    repo_c1 = OperationalCaseRepository(cliente_id="C1", db_path=db_path)
    repo_c2 = OperationalCaseRepository(cliente_id="C2", db_path=db_path)
    
    impact = QuantifiedImpact(amount=10.0, currency="USD")
    report = DiagnosticReport(
        report_id="r1", case_id="c1", cliente_id="C1", job_id="j1",
        hypothesis="Investigar si A?", diagnosis_status="NOT_CONFIRMED",
        findings=[], evidence_used=[], formulas_used=[],
        quantified_impact=impact, reasoning_summary="...",
        proposed_next_actions=["..."], owner_question="..."
    )
    
    repo_c1.create_report(report)
    
    assert repo_c2.get_report("r1") is None
