from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from app.contracts.bem_payloads import (
    BemConfidenceScore,
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)


class BemCuratedEvidenceAdapter:
    def __init__(self, now_provider: Callable[[], datetime] | None = None) -> None:
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def build_curated_evidence(
        self,
        tenant_id: str,
        payload: dict[str, Any],
    ) -> CuratedEvidenceRecord:
        _require_non_empty_str(tenant_id, "tenant_id")
        _require_non_empty_dict(payload, "payload")

        evidence_id = payload.get("evidence_id")
        _require_non_empty_str(evidence_id, "evidence_id")

        kind_value = payload.get("kind")
        if not isinstance(kind_value, str) or not kind_value.strip():
            raise ValueError("kind es obligatorio y no puede estar vacío")
        try:
            kind = EvidenceKind(kind_value.strip().lower())
        except ValueError as exc:
            raise ValueError(f"kind inválido: {kind_value}") from exc

        data = payload.get("data")
        _require_non_empty_dict(data, "data")

        source_raw = payload.get("source")
        _require_non_empty_dict(source_raw, "source")
        source_metadata = BemSourceMetadata(**source_raw)

        confidence_raw = payload.get("confidence")
        confidence: BemConfidenceScore | None = None
        if confidence_raw is not None:
            if not isinstance(confidence_raw, dict):
                raise TypeError("confidence debe ser dict o None")
            confidence = BemConfidenceScore(**confidence_raw)

        trace_id_raw = payload.get("trace_id")
        trace_id: str | None = None
        if trace_id_raw is not None:
            if not isinstance(trace_id_raw, str):
                raise TypeError("trace_id debe ser str o None")
            trace_id = trace_id_raw

        received_at = _to_utc_isoformat(self._now_provider())

        return CuratedEvidenceRecord(
            tenant_id=tenant_id,
            evidence_id=evidence_id.strip(),
            kind=kind,
            payload=data,
            source_metadata=source_metadata,
            received_at=received_at,
            confidence=confidence,
            trace_id=trace_id,
        )


def _require_non_empty_str(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _require_non_empty_dict(value: Any, field_name: str) -> None:
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _to_utc_isoformat(value: datetime) -> str:
    if not isinstance(value, datetime):
        raise TypeError("now_provider debe retornar datetime")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat()
