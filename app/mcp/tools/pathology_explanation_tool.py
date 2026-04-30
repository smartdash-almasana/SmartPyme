from pathlib import Path

from app.contracts.pathology_contract import PathologyFinding, PathologyStatus
from app.repositories.pathology_repository import PathologyRepository


def get_pathology_findings(
    cliente_id: str,
    pathology_id: str | None = None,
    status: str | PathologyStatus | None = None,
) -> list[dict]:
    repo = PathologyRepository(cliente_id, Path("data/pathologies.db"))
    findings = repo.list_findings(pathology_id=pathology_id, status=status)
    return [_serialize_pathology_finding(finding) for finding in findings]


def get_pathology_finding(cliente_id: str, pathology_finding_id: str) -> dict | None:
    repo = PathologyRepository(cliente_id, Path("data/pathologies.db"))
    finding = repo.get(pathology_finding_id)
    if finding is None:
        return None
    return _serialize_pathology_finding(finding)


def explain_pathology_finding(finding: dict) -> str:
    pathology_id = finding.get("pathology_id", "patologia")
    status = finding.get("status")
    severity = finding.get("severity")
    explanation = finding.get("explanation", "Sin explicación disponible.")
    suggested_action = finding.get("suggested_action")
    source_refs = finding.get("source_refs", [])

    if status == PathologyStatus.ACTIVE.value or status == "ACTIVE":
        return (
            f"Alerta de negocio: {pathology_id}. "
            f"Severidad: {severity}. "
            f"{explanation} "
            f"Acción sugerida: {suggested_action}. "
            f"Fuentes usadas: {len(source_refs)}."
        )

    if status == PathologyStatus.NOT_DETECTED.value or status == "NOT_DETECTED":
        return (
            f"Control saludable: {pathology_id}. "
            f"{explanation} "
            f"Fuentes revisadas: {len(source_refs)}."
        )

    return (
        f"Diagnóstico pendiente: {pathology_id}. "
        f"{explanation} "
        f"Fuentes disponibles: {len(source_refs)}."
    )


def get_pathology_status_for_owner(cliente_id: str) -> dict:
    findings = get_pathology_findings(cliente_id)
    messages = [explain_pathology_finding(finding) for finding in findings]
    return {
        "cliente_id": cliente_id,
        "count": len(findings),
        "pathology_findings": findings,
        "messages": messages,
    }


def _serialize_pathology_finding(finding: PathologyFinding) -> dict:
    return finding.model_dump(mode="json")
