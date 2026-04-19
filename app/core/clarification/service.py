from app.core.clarification.models import ClarificationRecord, ClarificationRequest
from app.core.clarification.persistence import (
    list_pending_clarifications,
    resolve_clarification,
    save_clarification,
)


def create_clarification(
    request: ClarificationRequest | None = None,
    *,
    clarification_id: str | None = None,
    entity_type: str | None = None,
    value_a: str | None = None,
    value_b: str | None = None,
    reason: str | None = None,
    blocking: bool | None = None,
) -> ClarificationRecord:
    if request is None:
        if (
            clarification_id is None
            or entity_type is None
            or value_a is None
            or value_b is None
            or reason is None
            or blocking is None
        ):
            raise ValueError("REQUEST_INVALIDA: faltan campos requeridos para crear la aclaracion.")
        request = ClarificationRequest(
            clarification_id=clarification_id,
            entity_type=entity_type,
            value_a=value_a,
            value_b=value_b,
            reason=reason,
            blocking=blocking,
        )

    save_clarification(request)
    return ClarificationRecord(
        clarification_id=request.clarification_id,
        entity_type=request.entity_type,
        value_a=request.value_a,
        value_b=request.value_b,
        reason=request.reason,
        blocking=request.blocking,
        status="pending",
        resolution=None,
    )


def get_pending_clarifications() -> list[ClarificationRecord]:
    return list_pending_clarifications()


def resolve_existing_clarification(clarification_id: str, resolution: str) -> bool:
    return resolve_clarification(clarification_id, resolution)
