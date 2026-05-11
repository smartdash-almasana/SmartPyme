from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from app.contracts.bem_payloads import (
    BemConfidenceScore,
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)

# Campos de transformedContent que se extraen como data operacional
_DATA_FIELDS = ("precio_venta", "costo_unitario", "cantidad", "producto")

# Campos de response_payload que se preservan como source_metadata externa
_SOURCE_META_FIELDS = ("callID", "callReferenceID", "inputType", "s3URL", "workflow_id")


class BemCuratedEvidenceAdapter:
    def __init__(self, now_provider: Callable[[], datetime] | None = None) -> None:
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------------
    # Método principal: payload SmartPyme normalizado → CuratedEvidenceRecord
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Método secundario: BEM response_payload real → CuratedEvidenceRecord
    # ------------------------------------------------------------------

    def build_curated_evidence_from_bem_response(
        self,
        tenant_id: str,
        response_payload: dict[str, Any],
        run_id: str | None = None,
    ) -> CuratedEvidenceRecord:
        """
        Mapea el response_payload real de BEM a un CuratedEvidenceRecord.

        Estructura esperada de response_payload:
            {
                "outputs": [{"transformedContent": {...}}],
                "callReferenceID": "...",   # opcional
                "callID": "...",            # opcional
                "avgConfidence": 0.9,       # opcional
                "inputType": "excel",       # opcional
                "s3URL": "...",             # opcional
                "workflow_id": "...",       # opcional
            }

        Fail-closed:
        - tenant_id vacío → ValueError
        - response_payload no dict → TypeError
        - falta outputs / vacío / falta transformedContent → ValueError
        - transformedContent no dict → ValueError
        - no se puede resolver evidence_id → ValueError
        """
        _require_non_empty_str(tenant_id, "tenant_id")

        if not isinstance(response_payload, dict):
            raise TypeError("response_payload debe ser dict")

        # --- outputs[0].transformedContent ---
        outputs = response_payload.get("outputs")
        if not isinstance(outputs, list) or len(outputs) == 0:
            raise ValueError("response_payload.outputs es obligatorio y no puede estar vacío")

        transformed = outputs[0].get("transformedContent") if isinstance(outputs[0], dict) else None
        if transformed is None:
            raise ValueError("outputs[0].transformedContent es obligatorio")
        if not isinstance(transformed, dict):
            raise ValueError("outputs[0].transformedContent debe ser dict")

        # --- evidence_id: callReferenceID → callID → bem-run-{run_id} → fail ---
        evidence_id: str | None = None
        raw_ref = response_payload.get("callReferenceID")
        if isinstance(raw_ref, str) and raw_ref.strip():
            evidence_id = raw_ref.strip()
        if evidence_id is None:
            raw_call = response_payload.get("callID")
            if isinstance(raw_call, str) and raw_call.strip():
                evidence_id = raw_call.strip()
        if evidence_id is None and run_id is not None:
            if isinstance(run_id, str) and run_id.strip():
                evidence_id = f"bem-run-{run_id.strip()}"
        if evidence_id is None:
            raise ValueError(
                "No se puede resolver evidence_id: falta callReferenceID, callID y run_id"
            )

        # --- kind: inferido desde inputType o source_type dentro de transformedContent ---
        input_type_raw = (
            response_payload.get("inputType")
            or transformed.get("source_type")
            or ""
        )
        kind = _infer_kind(input_type_raw)

        # --- data: campos operacionales desde transformedContent ---
        data: dict[str, Any] = {
            k: transformed[k] for k in _DATA_FIELDS if k in transformed
        }
        if not data:
            # Si no hay campos conocidos, preservar todo transformedContent como data
            data = dict(transformed)

        # --- source_metadata: source_name / source_type desde transformedContent ---
        source_name = (
            transformed.get("source_name")
            or response_payload.get("inputType")
            or "bem"
        )
        source_type = (
            transformed.get("source_type")
            or response_payload.get("inputType")
            or "unknown"
        )

        # Preservar campos de trazabilidad BEM en external_reference_id como JSON compacto
        import json as _json
        meta_extra: dict[str, Any] = {
            k: response_payload[k]
            for k in _SOURCE_META_FIELDS
            if k in response_payload and response_payload[k] is not None
        }
        external_ref = _json.dumps(meta_extra, ensure_ascii=False) if meta_extra else None

        source_metadata = BemSourceMetadata(
            source_name=source_name,
            source_type=source_type,
            external_reference_id=external_ref,
        )

        # --- confidence: avgConfidence si existe y es válido ---
        confidence: BemConfidenceScore | None = None
        avg_conf = response_payload.get("avgConfidence")
        if avg_conf is not None:
            if not isinstance(avg_conf, (int, float)):
                raise TypeError("avgConfidence debe ser numérico")
            confidence = BemConfidenceScore(score=float(avg_conf), provider="bem")

        received_at = _to_utc_isoformat(self._now_provider())

        return CuratedEvidenceRecord(
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            kind=kind,
            payload=data,
            source_metadata=source_metadata,
            received_at=received_at,
            confidence=confidence,
            trace_id=None,
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


def _infer_kind(raw: str) -> EvidenceKind:
    """Infiere EvidenceKind desde un string de tipo de fuente. Fail-safe a MIXED."""
    normalized = raw.strip().lower() if isinstance(raw, str) else ""
    _MAP = {
        "excel": EvidenceKind.EXCEL,
        "xlsx": EvidenceKind.EXCEL,
        "xls": EvidenceKind.EXCEL,
        "pdf": EvidenceKind.PDF,
        "image": EvidenceKind.IMAGE,
        "img": EvidenceKind.IMAGE,
        "email": EvidenceKind.EMAIL,
        "audio": EvidenceKind.AUDIO,
        "mixed": EvidenceKind.MIXED,
    }
    return _MAP.get(normalized, EvidenceKind.MIXED)
