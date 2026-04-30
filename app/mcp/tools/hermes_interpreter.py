from typing import Any


def interpret_finding(finding: dict[str, Any]) -> str:
    entity_type = finding.get("entity_type", "dato")
    severity = finding.get("severity", "SIN_PRIORIDAD")
    difference = finding.get("difference", 0)
    suggested_action = finding.get("suggested_action", "revisar el dato")

    return (
        f"Detecté una diferencia en {entity_type}. "
        f"La diferencia es de {difference}. "
        f"Prioridad: {severity}. "
        f"Acción sugerida: {suggested_action}."
    )


def interpret_findings(findings: list[dict[str, Any]]) -> list[str]:
    return [interpret_finding(finding) for finding in findings]
