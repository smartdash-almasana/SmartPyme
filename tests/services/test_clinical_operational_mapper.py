from __future__ import annotations

import pytest

from app.services.clinical_operational_mapper import ClinicalOperationalMapper


def test_mapper_maps_findings_to_signals() -> None:
    mapper = ClinicalOperationalMapper()
    report = {
        "tenant_id": "tenant-a",
        "findings": [
            {
                "finding_type": "VENTA_BAJO_COSTO",
                "severity": "HIGH",
                "evidence_id": "ev-001",
                "message": "Venta debajo del costo.",
            }
        ],
    }

    result = mapper.map_report(report)

    assert len(result["signals"]) == 1
    signal = result["signals"][0]
    assert signal.signal_type == "VENTA_BAJO_COSTO"
    assert signal.severity == "HIGH"
    assert signal.evidence_refs == ["ev-001"]
    assert signal.explanation == "Venta debajo del costo."


def test_mapper_creates_crisis_de_margen_hypothesis_and_clarification() -> None:
    mapper = ClinicalOperationalMapper()
    report = {
        "tenant_id": "tenant-a",
        "findings": [
            {
                "finding_type": "DESCUENTO_EXCESIVO",
                "severity": "MEDIUM",
                "evidence_id": "ev-100",
                "message": "Descuento excesivo detectado.",
            }
        ],
    }

    result = mapper.map_report(report)

    assert len(result["hypotheses"]) == 1
    hypothesis = result["hypotheses"][0]
    assert hypothesis.hypothesis_type == "CRISIS_DE_MARGEN"
    assert hypothesis.confidence == 0.60
    assert hypothesis.supporting_signals == ["DESCUENTO_EXCESIVO"]
    assert hypothesis.requires_clarification is True

    assert len(result["clarification_requests"]) == 1
    request = result["clarification_requests"][0]
    assert request.related_hypothesis == "CRISIS_DE_MARGEN"
    assert "crisis de margen" in request.question.lower()


def test_mapper_without_margin_signals_does_not_create_hypothesis() -> None:
    mapper = ClinicalOperationalMapper()
    report = {
        "tenant_id": "tenant-a",
        "findings": [
            {
                "finding_type": "STOCK_NEGATIVO",
                "severity": "MEDIUM",
                "evidence_id": "ev-900",
                "message": "Stock negativo.",
            }
        ],
    }

    result = mapper.map_report(report)
    assert len(result["signals"]) == 1
    assert result["hypotheses"] == []
    assert result["clarification_requests"] == []


def test_mapper_fail_closed_on_invalid_report() -> None:
    mapper = ClinicalOperationalMapper()

    with pytest.raises(ValueError, match="tenant_id"):
        mapper.map_report({"tenant_id": " ", "findings": []})

    with pytest.raises(ValueError, match="findings"):
        mapper.map_report({"tenant_id": "tenant-a", "findings": "bad"})  # type: ignore[arg-type]
