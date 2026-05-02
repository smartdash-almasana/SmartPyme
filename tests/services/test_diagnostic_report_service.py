import pytest
from app.services.diagnostic_report_service import DiagnosticReportService
from app.contracts.operational_case_contract import FindingRecord, QuantifiedImpact

@pytest.fixture
def service():
    return DiagnosticReportService()

def test_confirmed_report(service):
    finding = FindingRecord(
        entity="Producto A",
        finding_type="Diferencia de costo",
        measured_difference={"diff": 10},
        compared_sources=["POS", "Factura"],
        evidence_used=["doc1"],
        severity="HIGH",
        recommendation="Ajustar precio"
    )
    impact = QuantifiedImpact(amount=100.0, currency="USD")
    
    report = service.create_report(
        "case1", "cli1", "job1", "Investigar si...",
        [finding], ["doc1"], [], impact, "Resumen"
    )
    assert report.diagnosis_status == "CONFIRMED"

def test_insufficient_evidence_missing_sources(service):
    finding = FindingRecord(
        entity="Producto A",
        finding_type="Diferencia de costo",
        measured_difference={"diff": 10},
        compared_sources=[], # Missing
        evidence_used=["doc1"],
        severity="HIGH",
        recommendation="Ajustar precio"
    )
    impact = QuantifiedImpact(amount=100.0, currency="USD")
    
    report = service.create_report(
        "case1", "cli1", "job1", "Investigar si...",
        [finding], ["doc1"], [], impact, "Resumen"
    )
    assert report.diagnosis_status == "INSUFFICIENT_EVIDENCE"

def test_insufficient_evidence_missing_difference(service):
    finding = FindingRecord(
        entity="Producto A",
        finding_type="Diferencia de costo",
        measured_difference={}, # Missing
        compared_sources=["POS"],
        evidence_used=["doc1"],
        severity="HIGH",
        recommendation="Ajustar precio"
    )
    impact = QuantifiedImpact(amount=100.0, currency="USD")
    
    report = service.create_report(
        "case1", "cli1", "job1", "Investigar si...",
        [finding], ["doc1"], [], impact, "Resumen"
    )
    assert report.diagnosis_status == "INSUFFICIENT_EVIDENCE"
