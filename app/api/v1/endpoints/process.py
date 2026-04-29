import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_active_client
from app.core.pipeline import Pipeline
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository

router = APIRouter()


class ProcessRequest(BaseModel):
    evidence_id_a: str
    text_a: str
    evidence_id_b: str
    text_b: str
    job_id: str | None = None
    plan_id: str | None = None


def _tmp_db(name: str):
    return f"/tmp/{name}-{uuid.uuid4().hex}.db"


@router.post("/process")
async def process(payload: ProcessRequest, cliente_id: str = Depends(get_active_client)):
    pipeline = Pipeline(
        cliente_id=cliente_id,
        fact_repo=FactRepository(_tmp_db("facts")),
        canonical_repo=CanonicalRepository(_tmp_db("canonical")),
        entity_repo=EntityRepository(cliente_id, _tmp_db("entities")),
    )

    result = pipeline.process_texts(
        payload.evidence_id_a,
        payload.text_a,
        payload.evidence_id_b,
        payload.text_b,
        job_id=payload.job_id,
        plan_id=payload.plan_id,
    )

    return {
        "cliente_id": result.cliente_id,
        "status": result.status
    }
