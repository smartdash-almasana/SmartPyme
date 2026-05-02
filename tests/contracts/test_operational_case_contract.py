import pytest
from app.contracts.operational_case_contract import (
    OperationalCase, FindingRecord, QuantifiedImpact, DiagnosticReport, ValidatedCaseRecord
)

def test_operational_case_valid():
    case = OperationalCase(
        case_id="case-123",
        cliente_id="C1",
        job_id="job-abc",
        skill_id="skill-1",
        demanda_original="Revisar stock",
        hypothesis="Investigar si existe perdida de stock en deposito A?",
        taxonomia_pyme={},
        variables_curadas={},
        evidencia_disponible=[],
        condiciones_validadas=[],
        formula_applicable=None,
        pathology_possible=None,
        referencias_necesarias=[],
        investigation_plan=[],
        status="OPEN",
        symptom_id_orientativo="symptom-001"
    )
    assert case.case_id == "case-123"
    assert case.symptom_id_orientativo == "symptom-001"

def test_operational_case_valid_no_symptom_id():
    case = OperationalCase(
        case_id="case-123-no-symptom",
        cliente_id="C1",
        job_id="job-abc-no-symptom",
        skill_id="skill-1",
        demanda_original="Revisar stock sin síntoma",
        hypothesis="Investigar si existe perdida de stock en deposito A sin síntoma?",
        taxonomia_pyme={},
        variables_curadas={},
        evidencia_disponible=[],
        condiciones_validadas=[],
        formula_applicable=None,
        pathology_possible=None,
        referencias_necesarias=[],
        investigation_plan=[],
        status="OPEN"
    )
    assert case.case_id == "case-123-no-symptom"
    assert case.symptom_id_orientativo is None

def test_operational_case_invalid_hypothesis():
    with pytest.raises(ValueError, match="HYPOTHESIS_INVALIDA"):
        OperationalCase(
            case_id="case-123",
            cliente_id="C1",
            job_id="job-abc",
            skill_id="skill-1",
            demanda_original="Revisar stock",
            hypothesis="Hay perdida de stock", # Afirmativo, no investigable
            taxonomia_pyme={},
            variables_curadas={},
            evidencia_disponible=[],
            condiciones_validadas=[],
            formula_applicable=None,
            pathology_possible=None,
            referencias_necesarias=[],
            investigation_plan=[],
            status="OPEN"
        )

def test_finding_record_no_evidence():
    with pytest.raises(ValueError, match="EVIDENCE_USED_REQUERIDA"):
        FindingRecord(
            entity="item-1",
            finding_type="DUPLICATE",
            measured_difference={},
            compared_sources=[],
            evidence_used=[], # Empty
            severity="HIGH",
            recommendation="fix it"
        )

def test_quantified_impact_empty():
    with pytest.raises(ValueError, match="IMPACTO_VACIO"):
        QuantifiedImpact()

def test_diagnostic_report_confirmed_no_findings():
    impact = QuantifiedImpact(amount=100.0)
    with pytest.raises(ValueError, match="FINDINGS_REQUERIDOS"):
        DiagnosticReport(
            report_id="rep-1",
            case_id="case-1",
            cliente_id="C1",
            job_id="job-1",
            hypothesis="Investigar si...?",
            diagnosis_status="CONFIRMED",
            findings=[], # Empty
            evidence_used=["ev-1"],
            formulas_used=[],
            quantified_impact=impact,
            reasoning_summary="...",
            proposed_next_actions=[],
            owner_question="?"
        )

def test_diagnostic_report_confirmed_no_evidence():
    impact = QuantifiedImpact(amount=100.0)
    finding = FindingRecord(
        entity="e", finding_type="t", measured_difference={}, 
        compared_sources=[], evidence_used=["ev-1"], severity="LOW", recommendation="r"
    )
    with pytest.raises(ValueError, match="EVIDENCE_REQUERIDA"):
        DiagnosticReport(
            report_id="rep-1",
            case_id="case-1",
            cliente_id="C1",
            job_id="job-1",
            hypothesis="Investigar si...?",
            diagnosis_status="CONFIRMED",
            findings=[finding],
            evidence_used=[], # Empty
            formulas_used=[],
            quantified_impact=impact,
            reasoning_summary="...",
            proposed_next_actions=[],
            owner_question="?"
        )

def test_diagnostic_report_with_empty_references_used():
    impact = QuantifiedImpact(amount=100.0)
    finding = FindingRecord(
        entity="e", finding_type="t", measured_difference={},
        compared_sources=[], evidence_used=["ev-1"], severity="LOW", recommendation="r"
    )
    report = DiagnosticReport(
        report_id="rep-empty-ref",
        case_id="case-1",
        cliente_id="C1",
        job_id="job-1",
        hypothesis="Investigar si...?",
        diagnosis_status="NOT_CONFIRMED",
        findings=[finding],
        evidence_used=["ev-1"],
        references_used=[], # Empty
        formulas_used=[],
        quantified_impact=impact,
        reasoning_summary="...",
        proposed_next_actions=[],
        owner_question="?"
    )
    assert report.references_used == []

def test_diagnostic_report_with_references_used():
    impact = QuantifiedImpact(amount=100.0)
    finding = FindingRecord(
        entity="e", finding_type="t", measured_difference={},
        compared_sources=[], evidence_used=["ev-1"], severity="LOW", recommendation="r"
    )
    report = DiagnosticReport(
        report_id="rep-with-ref",
        case_id="case-1",
        cliente_id="C1",
        job_id="job-1",
        hypothesis="Investigar si...?",
        diagnosis_status="NOT_CONFIRMED",
        findings=[finding],
        evidence_used=["ev-1"],
        references_used=["ref-1", "ref-2"], # With values
        formulas_used=[],
        quantified_impact=impact,
        reasoning_summary="...",
        proposed_next_actions=[],
        owner_question="?"
    )
    assert report.references_used == ["ref-1", "ref-2"]

def test_validated_case_record_valid():
    impact = QuantifiedImpact(amount=500.0, currency="USD")
    record = ValidatedCaseRecord(
        validated_case_id="v-1",
        cliente_id="C1",
        job_id="j-1",
        case_id="c-1",
        report_id="r-1",
        timestamp="2026-05-01T12:00:00Z",
        hypothesis="Investigar si...?",
        diagnosis_status="CONFIRMED",
        evidence_used=["ev-1"],
        formulas_used=["f-1"],
        findings_summary="Summary",
        quantified_impact=impact,
        owner_visible_report="Report",
        next_question="Next?",
        metadata={"version": "1.0"}
    )
    assert record.validated_case_id == "v-1"
