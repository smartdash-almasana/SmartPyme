import pytest
import uuid
from app.repositories.operational_case_repository import OperationalCaseRepository
from app.services.case_closure_service import CaseClosureService
from app.contracts.operational_case_contract import (
    OperationalCase, DiagnosticReport, QuantifiedImpact, FindingRecord
)

@pytest.fixture
def repo_a(tmp_path):
    return OperationalCaseRepository(cliente_id="CLIENT_A", db_path=tmp_path / "test.db")

@pytest.fixture
def repo_b(tmp_path):
    return OperationalCaseRepository(cliente_id="CLIENT_B", db_path=tmp_path / "test.db")

@pytest.fixture
def closure_service_a(repo_a):
    return CaseClosureService(repo_a)

def create_case_fixture(repo, case_id="c1"):
    case = OperationalCase(
        case_id=case_id, cliente_id=repo.cliente_id, job_id="j1", skill_id="s1",
        demanda_original="...", hypothesis="Investigar si A?",
        taxonomia_pyme={}, variables_curadas={}, evidencia_disponible=[],
        condiciones_validadas=[], formula_applicable=None, pathology_possible=None,
        referencias_necesarias=[], investigation_plan=[], status="OPEN"
    )
    repo.create_case(case)
    return case

def test_happy_path_lifecycle(repo_a, closure_service_a):
    case = create_case_fixture(repo_a)
    
    report = DiagnosticReport(
        report_id="r1", case_id=case.case_id, cliente_id=repo_a.cliente_id, job_id=case.job_id,
        hypothesis="H", diagnosis_status="CONFIRMED",
        findings=[FindingRecord(
            entity="entity_001", finding_type="DATA_DIFFERENCE", 
            measured_difference={"v": 1}, compared_sources=["source_a", "source_b"], 
            evidence_used=["e1"], severity="LOW", recommendation="r"
        )],
        evidence_used=["e1"], formulas_used=[],
        quantified_impact=QuantifiedImpact(percentage=15.0),
        reasoning_summary="Summary", proposed_next_actions=[], owner_question="Q"
    )
    repo_a.save_diagnostic_report(report)
    
    validated_case_id = closure_service_a.close_case(case.case_id, report.report_id)
    assert validated_case_id is not None
    
    record = repo_a.get_validated_case(validated_case_id)
    assert record is not None
    assert record.report_id == report.report_id
    assert record.quantified_impact['percentage'] == 15.0

def test_tenant_isolation(repo_a, repo_b):
    case = create_case_fixture(repo_a, "c1")
    report = DiagnosticReport(
        report_id="r1", case_id=case.case_id, cliente_id=repo_a.cliente_id, job_id=case.job_id,
        hypothesis="H", diagnosis_status="CONFIRMED",
        findings=[FindingRecord(
            entity="entity_001", finding_type="DATA_DIFFERENCE", 
            measured_difference={"v": 1}, compared_sources=["source_a", "source_b"], 
            evidence_used=["e1"], severity="LOW", recommendation="r"
        )],
        evidence_used=["e1"], formulas_used=[],
        quantified_impact=QuantifiedImpact(percentage=10.0),
        reasoning_summary="Summary", proposed_next_actions=[], owner_question="Q"
    )
    repo_a.save_diagnostic_report(report)
    
    # Intentar acceder desde B
    assert repo_b.get_diagnostic_report_by_case("c1") is None

def test_insufficient_evidence_lifecycle(repo_a, closure_service_a):
    case = create_case_fixture(repo_a, "c2")
    
    # Estado sin hallazgos, diagnóstico INSUFFICIENT_EVIDENCE
    report = DiagnosticReport(
        report_id="r2", case_id=case.case_id, cliente_id=repo_a.cliente_id, job_id=case.job_id,
        hypothesis="H", diagnosis_status="INSUFFICIENT_EVIDENCE",
        findings=[],
        evidence_used=["e1"], formulas_used=[],
        quantified_impact=QuantifiedImpact(percentage=0.0),
        reasoning_summary="No data", proposed_next_actions=[], owner_question="Q"
    )
    repo_a.save_diagnostic_report(report)
    
    # Intentar cerrar: debería fallar porque el contrato exige hallazgos para cerrar (definido en TS_022)
    assert closure_service_a.close_case(case.case_id, report.report_id) is None
    assert repo_a.get_case(case.case_id).status == "OPEN"
