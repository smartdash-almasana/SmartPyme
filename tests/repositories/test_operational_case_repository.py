import pytest
import sqlite3
from pathlib import Path
from app.repositories.operational_case_repository import OperationalCaseRepository
from app.contracts.operational_case_contract import (
    OperationalCase,
    DiagnosticReport,
    ValidatedCaseRecord,
    FindingRecord,
    QuantifiedImpact,
)

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_operational_cases.db"

@pytest.fixture
def repo(db_path):
    return OperationalCaseRepository(cliente_id="CLIENT_A", db_path=db_path)

def test_create_and_get_operational_case(repo):
    case = OperationalCase(
        case_id="case-123",
        cliente_id="CLIENT_A",
        job_id="job-abc",
        skill_id="skill-test",
        demanda_original="Revisar stock",
        hypothesis="Investigar si hay perdida?",
        taxonomia_pyme={"sector": "almacen"},
        variables_curadas={"periodo": "2026-05"},
        evidencia_disponible=["ev-1", "ev-2"],
        condiciones_validadas=["auth-ok"],
        formula_applicable="F1",
        pathology_possible="P1",
        referencias_necesarias=["ref-1"],
        investigation_plan=["step1"],
        status="OPEN"
    )
    
    repo.create_case(case)
    fetched = repo.get_case("case-123")
    
    assert fetched == case
    assert fetched.taxonomia_pyme == {"sector": "almacen"}
    assert fetched.evidencia_disponible == ["ev-1", "ev-2"]

def test_create_and_get_diagnostic_report(repo):
    impact = QuantifiedImpact(amount=1500.0, currency="USD", risk_level="HIGH")
    finding = FindingRecord(
        entity="factura-001",
        finding_type="DUPLICATE",
        measured_difference={"diff": 500},
        compared_sources=["erp", "pdf"],
        evidence_used=["ev-1"],
        severity="CRITICAL",
        recommendation="Anular factura"
    )
    
    report = DiagnosticReport(
        report_id="rep-999",
        case_id="case-123",
        cliente_id="CLIENT_A",
        job_id="job-abc",
        hypothesis="Investigar si hay perdida?",
        diagnosis_status="CONFIRMED",
        findings=[finding],
        evidence_used=["ev-1"],
        references_used=["http://example.com/ref1", "manual_agro_v2"],
        formulas_used=["sum()"],
        quantified_impact=impact,
        reasoning_summary="Deteccion automatica",
        proposed_next_actions=["action-1"],
        owner_question="¿Desea anular?"
    )
    
    repo.create_report(report)
    fetched = repo.get_report("rep-999")
    
    assert fetched == report
    assert fetched.quantified_impact.amount == 1500.0
    assert fetched.findings[0].entity == "factura-001"
    assert fetched.references_used == ["http://example.com/ref1", "manual_agro_v2"]

def test_create_and_get_validated_case(repo):
    impact = QuantifiedImpact(percentage=15.5)
    record = ValidatedCaseRecord(
        validated_case_id="v-777",
        cliente_id="CLIENT_A",
        job_id="job-abc",
        case_id="case-123",
        report_id="rep-999",
        timestamp="2026-05-01T10:00:00Z",
        hypothesis="Investigar si...?",
        diagnosis_status="CONFIRMED",
        evidence_used=["ev-1"],
        formulas_used=["f1"],
        findings_summary="Se encontro duplicidad",
        quantified_impact=impact,
        owner_visible_report="## Reporte Final\nExito.",
        next_question="¿Confirmar cierre?",
        metadata={"engine_version": "2.0"}
    )
    
    repo.create_validated_case(record)
    fetched = repo.get_validated_case("v-777")
    
    assert fetched == record
    assert fetched.quantified_impact.percentage == 15.5
    assert fetched.metadata == {"engine_version": "2.0"}

def test_list_and_isolation(db_path):
    repo_a = OperationalCaseRepository(cliente_id="CLIENT_A", db_path=db_path)
    repo_b = OperationalCaseRepository(cliente_id="CLIENT_B", db_path=db_path)
    
    case_a = OperationalCase(
        case_id="case-A", cliente_id="CLIENT_A", job_id="j1", skill_id="s1",
        demanda_original="...", hypothesis="Investigar si A?",
        taxonomia_pyme={}, variables_curadas={}, evidencia_disponible=[],
        condiciones_validadas=[], formula_applicable=None, pathology_possible=None,
        referencias_necesarias=[], investigation_plan=[], status="OPEN"
    )
    
    case_b = OperationalCase(
        case_id="case-B", cliente_id="CLIENT_B", job_id="j1", skill_id="s1",
        demanda_original="...", hypothesis="Investigar si B?",
        taxonomia_pyme={}, variables_curadas={}, evidencia_disponible=[],
        condiciones_validadas=[], formula_applicable=None, pathology_possible=None,
        referencias_necesarias=[], investigation_plan=[], status="OPEN"
    )
    
    repo_a.create_case(case_a)
    repo_b.create_case(case_b)
    
    # List isolation
    list_a = repo_a.list_cases()
    assert len(list_a) == 1
    assert list_a[0].case_id == "case-A"
    
    list_b = repo_b.list_cases()
    assert len(list_b) == 1
    assert list_b[0].case_id == "case-B"
    
    # Get isolation
    assert repo_a.get_case("case-B") is None
    assert repo_b.get_case("case-A") is None

def test_client_id_mismatch_raises_value_error(repo):
    case = OperationalCase(
        case_id="case-evil", cliente_id="OTHER_CLIENT", job_id="j1", skill_id="s1",
        demanda_original="...", hypothesis="Investigar si...?",
        taxonomia_pyme={}, variables_curadas={}, evidencia_disponible=[],
        condiciones_validadas=[], formula_applicable=None, pathology_possible=None,
        referencias_necesarias=[], investigation_plan=[], status="OPEN"
    )
    
    with pytest.raises(ValueError, match="Violación de aislamiento"):
        repo.create_case(case)

def test_json_roundtrip_complex_nested(repo):
    impact = QuantifiedImpact(amount=100.0, risk_level="LOW")
    finding = FindingRecord(
        entity="E", finding_type="T", measured_difference={"nested": {"key": [1,2,3]}},
        compared_sources=["S"], evidence_used=["EV"], severity="LOW", recommendation="R"
    )
    report = DiagnosticReport(
        report_id="r1", case_id="c1", cliente_id="CLIENT_A", job_id="j1",
        hypothesis="Investigar si...?", diagnosis_status="CONFIRMED",
        findings=[finding], evidence_used=["EV"], formulas_used=[],
        quantified_impact=impact, reasoning_summary="R", proposed_next_actions=[], owner_question="Q"
    )
    
    repo.create_report(report)
    fetched = repo.get_report("r1")
    
    assert fetched.findings[0].measured_difference == {"nested": {"key": [1,2,3]}}
    assert fetched.quantified_impact.amount == 100.0
