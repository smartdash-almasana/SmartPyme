"""
Tests determinísticos para MarkdownDiagnosticReportBuilder.

Sin mocks. Sin side effects. Fail-closed.
"""
from __future__ import annotations

import pytest

from app.services.markdown_diagnostic_report_builder import MarkdownDiagnosticReportBuilder


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def builder() -> MarkdownDiagnosticReportBuilder:
    return MarkdownDiagnosticReportBuilder()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _diagnostic(
    tenant_id: str = "tenant-1",
    evidence_count: int = 1,
    findings: list | None = None,
) -> dict:
    return {
        "tenant_id": tenant_id,
        "evidence_count": evidence_count,
        "findings": findings or [],
    }


def _finding(
    finding_type: str = "VENTA_BAJO_COSTO",
    severity: str = "HIGH",
    message: str = "precio menor que costo",
    evidence_id: str = "ev-001",
) -> dict:
    return {
        "finding_type": finding_type,
        "severity": severity,
        "message": message,
        "evidence_id": evidence_id,
    }


# ---------------------------------------------------------------------------
# Markdown válido — estructura básica
# ---------------------------------------------------------------------------


def test_markdown_contains_header(builder: MarkdownDiagnosticReportBuilder) -> None:
    md = builder.build_markdown_report(_diagnostic())
    assert "# Diagnóstico Operacional" in md


def test_markdown_contains_tenant_id(builder: MarkdownDiagnosticReportBuilder) -> None:
    md = builder.build_markdown_report(_diagnostic(tenant_id="tenant-abc"))
    assert "tenant-abc" in md


def test_markdown_contains_evidence_count(builder: MarkdownDiagnosticReportBuilder) -> None:
    md = builder.build_markdown_report(_diagnostic(evidence_count=7))
    assert "7" in md


def test_markdown_contains_hallazgos_section(builder: MarkdownDiagnosticReportBuilder) -> None:
    md = builder.build_markdown_report(_diagnostic())
    assert "## Hallazgos" in md


def test_markdown_returns_str(builder: MarkdownDiagnosticReportBuilder) -> None:
    result = builder.build_markdown_report(_diagnostic())
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Sin findings
# ---------------------------------------------------------------------------


def test_markdown_no_findings_message(builder: MarkdownDiagnosticReportBuilder) -> None:
    md = builder.build_markdown_report(_diagnostic(findings=[]))
    assert "No se detectaron hallazgos operacionales." in md


def test_markdown_no_findings_no_finding_type_header(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    md = builder.build_markdown_report(_diagnostic(findings=[]))
    assert "### " not in md


# ---------------------------------------------------------------------------
# Múltiples findings
# ---------------------------------------------------------------------------


def test_markdown_multiple_findings_all_present(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [
        _finding("VENTA_BAJO_COSTO", "HIGH", "precio bajo", "ev-001"),
        _finding("STOCK_NEGATIVO", "MEDIUM", "stock negativo", "ev-002"),
        _finding("MOVIMIENTO_INCONSISTENTE", "MEDIUM", "inconsistente", "ev-003"),
    ]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    assert "VENTA_BAJO_COSTO" in md
    assert "STOCK_NEGATIVO" in md
    assert "MOVIMIENTO_INCONSISTENTE" in md
    assert "ev-001" in md
    assert "ev-002" in md
    assert "ev-003" in md


def test_markdown_multiple_findings_evidence_count(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [
        _finding("VENTA_BAJO_COSTO", "HIGH", "msg", "ev-001"),
        _finding("STOCK_NEGATIVO", "MEDIUM", "msg", "ev-002"),
    ]
    md = builder.build_markdown_report(_diagnostic(evidence_count=2, findings=findings))
    assert "2" in md


# ---------------------------------------------------------------------------
# Ordering por severity desc (HIGH → MEDIUM → LOW)
# ---------------------------------------------------------------------------


def test_markdown_ordering_high_before_medium(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [
        _finding("STOCK_NEGATIVO", "MEDIUM", "stock", "ev-002"),
        _finding("VENTA_BAJO_COSTO", "HIGH", "precio", "ev-001"),
    ]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    pos_high = md.index("HIGH")
    pos_medium = md.index("MEDIUM")
    assert pos_high < pos_medium


def test_markdown_ordering_high_before_low(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [
        _finding("STOCK_NEGATIVO", "LOW", "stock", "ev-002"),
        _finding("VENTA_BAJO_COSTO", "HIGH", "precio", "ev-001"),
    ]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    pos_high = md.index("HIGH")
    pos_low = md.index("LOW")
    assert pos_high < pos_low


def test_markdown_ordering_medium_before_low(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [
        _finding("TIPO_A", "LOW", "bajo", "ev-003"),
        _finding("TIPO_B", "MEDIUM", "medio", "ev-002"),
    ]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    pos_medium = md.index("MEDIUM")
    pos_low = md.index("LOW")
    assert pos_medium < pos_low


def test_markdown_ordering_all_three_severities(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [
        _finding("TIPO_LOW", "LOW", "bajo", "ev-003"),
        _finding("TIPO_HIGH", "HIGH", "alto", "ev-001"),
        _finding("TIPO_MED", "MEDIUM", "medio", "ev-002"),
    ]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    pos_high = md.index("HIGH")
    pos_medium = md.index("MEDIUM")
    pos_low = md.index("LOW")
    assert pos_high < pos_medium < pos_low


# ---------------------------------------------------------------------------
# Tenant vacío — fail-closed
# ---------------------------------------------------------------------------


def test_markdown_fails_on_empty_tenant_id(builder: MarkdownDiagnosticReportBuilder) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        builder.build_markdown_report(_diagnostic(tenant_id=""))


def test_markdown_fails_on_blank_tenant_id(builder: MarkdownDiagnosticReportBuilder) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        builder.build_markdown_report(_diagnostic(tenant_id="   "))


def test_markdown_fails_on_non_dict_input(builder: MarkdownDiagnosticReportBuilder) -> None:
    with pytest.raises(TypeError):
        builder.build_markdown_report("no es un dict")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Payload parcial (findings con campos faltantes)
# ---------------------------------------------------------------------------


def test_markdown_partial_finding_missing_message(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [{"finding_type": "VENTA_BAJO_COSTO", "severity": "HIGH", "evidence_id": "ev-1"}]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    assert "VENTA_BAJO_COSTO" in md
    assert "ev-1" in md
    # message vacío no rompe el builder
    assert "**Mensaje:**" in md


def test_markdown_partial_finding_missing_severity(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [
        {"finding_type": "STOCK_NEGATIVO", "message": "stock bajo", "evidence_id": "ev-2"}
    ]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    assert "STOCK_NEGATIVO" in md
    assert "ev-2" in md


def test_markdown_finding_with_all_fields_rendered(
    builder: MarkdownDiagnosticReportBuilder,
) -> None:
    findings = [_finding("VENTA_BAJO_COSTO", "HIGH", "precio menor que costo", "ev-xyz")]
    md = builder.build_markdown_report(_diagnostic(findings=findings))

    assert "### VENTA_BAJO_COSTO" in md
    assert "**Severidad:** HIGH" in md
    assert "**Mensaje:** precio menor que costo" in md
    assert "**Evidence ID:** ev-xyz" in md


# ---------------------------------------------------------------------------
# Determinismo: misma entrada → mismo output
# ---------------------------------------------------------------------------


def test_markdown_is_deterministic(builder: MarkdownDiagnosticReportBuilder) -> None:
    diag = _diagnostic(
        findings=[
            _finding("VENTA_BAJO_COSTO", "HIGH", "precio bajo", "ev-001"),
            _finding("STOCK_NEGATIVO", "MEDIUM", "stock negativo", "ev-002"),
        ]
    )
    md1 = builder.build_markdown_report(diag)
    md2 = builder.build_markdown_report(diag)
    assert md1 == md2
