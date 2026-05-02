import pytest
from pathlib import Path
from app.repositories.operational_case_repository import OperationalCaseRepository
from app.services.case_closure_service import CaseClosureService
from app.contracts.operational_case_contract import OperationalCase, DiagnosticReport, QuantifiedImpact, FindingRecord

@pytest.fixture
def repo(tmp_path):
    return OperationalCaseRepository(cliente_id="CLIENT_A", db_path=tmp_path / "test.db")

@pytest.fixture
def closure_service(repo):
    return CaseClosureService(repo)

def test_close_case_success(repo, closure_service):
    case = OperationalCase(
        case_id="c1", cliente_id="CLIENT_A", job_id="j1", skill_id="s1",
        demanda_original="...", hypothesis="Investigar si A?",
        taxonomia_pyme={}, variables_curadas={}, evidencia_disponible=[],
        condiciones_validadas=[], formula_applicable=None, pathology_possible=None,
        referencias_necesarias=[], investigation_plan=[], status="OPEN"
    )
    repo.create_case(case)
    
    report = DiagnosticReport(
        report_id="r1", case_id="c1", cliente_id="CLIENT_A", job_id="j1",
        hypothesis="Investigar si A?", diagnosis_status="CONFIRMED",
        findings=[FindingRecord(entity="e", finding_type="t", measured_difference={"d":1}, compared_sources=["s"], evidence_used=["e1"], severity="LOW", recommendation="r")],
        evidence_used=["e1"], formulas_used=[],
        quantified_impact=QuantifiedImpact(percentage=10.0),
        reasoning_summary="Ok", proposed_next_actions=[], owner_question="Q"
    )
    repo.create_report(report)
    
    vid = closure_service.close_case("c1", "r1")
    assert vid is not None
    
    updated_case = repo.get_case("c1")
    assert updated_case.status == "CLOSED"
    
    record = repo.get_validated_case(vid)
    assert record is not None
    assert record.case_id == "c1"
