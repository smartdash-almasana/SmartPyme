from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_active_client
from app.repositories.finding_repository import FindingRepository

router = APIRouter()


class FindingsDbPath(BaseModel):
    findings: str


async def get_findings_db_path() -> FindingsDbPath:
    return FindingsDbPath(findings="data/findings.db")


@router.get("/findings")
async def list_findings(
    entity_type: str | None = None,
    cliente_id: str = Depends(get_active_client),
    db_path: FindingsDbPath = Depends(get_findings_db_path),
):
    repo = FindingRepository(cliente_id, Path(db_path.findings))
    findings = repo.list_findings(entity_type=entity_type)

    return {
        "cliente_id": cliente_id,
        "count": len(findings),
        "findings": [
            {
                "finding_id": f.finding_id,
                "entity_type": f.entity_type,
                "severity": f.severity,
                "suggested_action": f.suggested_action,
                "traceable_origin": f.traceable_origin,
            }
            for f in findings
        ],
    }
