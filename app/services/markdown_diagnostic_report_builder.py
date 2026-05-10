"""
Generador de informe operacional exportable en Markdown.

Sin IA. Sin templates externos. Sin markdown libs.
String builder simple. Determinístico. Fail-closed.
"""
from __future__ import annotations

from typing import Any

# Orden de severidad descendente para ordenar findings.
_SEVERITY_ORDER: dict[str, int] = {
    "HIGH": 0,
    "MEDIUM": 1,
    "LOW": 2,
}

_NO_FINDINGS_MSG = "No se detectaron hallazgos operacionales."


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _severity_rank(finding: dict[str, Any]) -> int:
    return _SEVERITY_ORDER.get(finding.get("severity", ""), 99)


class MarkdownDiagnosticReportBuilder:
    """
    Construye un informe Markdown determinístico a partir del dict
    retornado por BasicOperationalDiagnosticService.build_report().
    """

    def build_markdown_report(self, diagnostic: dict[str, Any]) -> str:
        """
        Genera el informe Markdown.

        Parámetros
        ----------
        diagnostic:
            Dict con claves: tenant_id, findings, evidence_count.

        Retorna
        -------
        str con el informe Markdown completo.

        Falla si diagnostic no es dict o si tenant_id está vacío.
        """
        if not isinstance(diagnostic, dict):
            raise TypeError("diagnostic debe ser un dict")

        tenant_id = diagnostic.get("tenant_id", "")
        _require_non_empty(tenant_id, "tenant_id")

        evidence_count = diagnostic.get("evidence_count", 0)
        findings: list[dict[str, Any]] = diagnostic.get("findings", [])

        if not isinstance(findings, list):
            raise TypeError("findings debe ser una lista")

        sorted_findings = sorted(findings, key=_severity_rank)

        lines: list[str] = []

        lines.append("# Diagnóstico Operacional")
        lines.append("")
        lines.append(f"**Tenant:** {tenant_id}")
        lines.append(f"**Cantidad de evidencias:** {evidence_count}")
        lines.append("")
        lines.append("## Hallazgos")
        lines.append("")

        if not sorted_findings:
            lines.append(_NO_FINDINGS_MSG)
        else:
            # Agrupar por finding_type para encabezados de sección.
            # Dentro de cada tipo los findings ya vienen ordenados por severity.
            seen_types: list[str] = []
            for finding in sorted_findings:
                ftype = finding.get("finding_type", "DESCONOCIDO")
                if ftype not in seen_types:
                    seen_types.append(ftype)
                    lines.append(f"### {ftype}")
                    lines.append("")

                severity = finding.get("severity", "")
                message = finding.get("message", "")
                evidence_id = finding.get("evidence_id", "")

                lines.append(f"- **Severidad:** {severity}")
                lines.append(f"- **Mensaje:** {message}")
                lines.append(f"- **Evidence ID:** {evidence_id}")
                lines.append("")

        return "\n".join(lines)
