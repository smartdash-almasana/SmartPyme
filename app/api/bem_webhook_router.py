from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.bem_curated_evidence_adapter import BemCuratedEvidenceAdapter

router = APIRouter()


@router.post("/webhooks/bem")
def bem_webhook(body: dict[str, Any]) -> dict[str, str]:
    tenant_id = body.get("tenant_id")
    payload = body.get("payload")

    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id es obligatorio")
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(status_code=400, detail="payload es obligatorio")

    try:
        record = BemCuratedEvidenceAdapter().build_curated_evidence(
            tenant_id=tenant_id,
            payload=payload,
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "accepted",
        "evidence_id": record.evidence_id,
        "tenant_id": record.tenant_id,
    }
