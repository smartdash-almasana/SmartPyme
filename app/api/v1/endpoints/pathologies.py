from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_active_client
from app.contracts.pathology_contract import PathologyFinding, PathologyStatus
from app.factory.agents.pathology_auditor_agent import PathologyAuditorAgent
from app.repositories.pathology_repository import PathologyRepository

router = APIRouter()


class PathologyDbPaths(BaseModel):
    formula_results: str
    pathologies: str


class PathologyAuditRequest(BaseModel):
    formula_result_id: str
    pathology_id: str = "margen_bruto_negativo"
    pathology_finding_id: str | None = None


async def get_pathology_db_paths() -> PathologyDbPaths:
    return PathologyDbPaths(
        formula_results="data/formula_results.db",
        pathologies="data/pathologies.db",
    )


def serialize_pathology_finding(finding: PathologyFinding) -> dict:
    return finding.model_dump(mode="json")


@router.post("/pathologies/audit")
async def audit_pathology(
    payload: PathologyAuditRequest,
    cliente_id: str = Depends(get_active_client),
    db_paths: PathologyDbPaths = Depends(get_pathology_db_paths),
):
    agent = PathologyAuditorAgent(
        cliente_id=cliente_id,
        formula_results_db_path=Path(db_paths.formula_results),
        pathologies_db_path=Path(db_paths.pathologies),
    )
    finding = agent.audit_formula_result(
        formula_result_id=payload.formula_result_id,
        pathology_id=payload.pathology_id,
        pathology_finding_id=payload.pathology_finding_id,
    )
    if finding is None:
        raise HTTPException(status_code=404, detail="Formula result not found")

    return serialize_pathology_finding(finding)


@router.get("/pathologies/findings")
async def list_pathology_findings(
    pathology_id: str | None = None,
    status: PathologyStatus | None = None,
    cliente_id: str = Depends(get_active_client),
    db_paths: PathologyDbPaths = Depends(get_pathology_db_paths),
):
    repo = PathologyRepository(cliente_id, Path(db_paths.pathologies))
    findings = repo.list_findings(pathology_id=pathology_id, status=status)

    return {
        "cliente_id": cliente_id,
        "count": len(findings),
        "findings": [serialize_pathology_finding(finding) for finding in findings],
    }


@router.get("/pathologies/findings/{pathology_finding_id}")
async def get_pathology_finding(
    pathology_finding_id: str,
    cliente_id: str = Depends(get_active_client),
    db_paths: PathologyDbPaths = Depends(get_pathology_db_paths),
):
    repo = PathologyRepository(cliente_id, Path(db_paths.pathologies))
    finding = repo.get(pathology_finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Pathology finding not found")

    return serialize_pathology_finding(finding)
