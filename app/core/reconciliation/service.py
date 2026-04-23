from datetime import datetime, timedelta, timezone
from decimal import Decimal
from math import isfinite
from collections.abc import Callable
from dataclasses import asdict, replace
from typing import Any

from app.core.reconciliation.models import (
    AmountDifferenceAssessment,
    AmountReconciliationFinding,
    AmountReconciliationResult,
    ClarificationQuestion,
    ClarificationState,
    ComparableRecord,
    DeterministicDiscrepancySnapshot,
    DeterministicHitlEvaluation,
    DifferenceRecord,
    EconomicImpact,
    FailClosedStateEvaluation,
    HumanReviewDecision,
    MeliSuggestedAction,
    QuantifiedDiscrepancy,
    ReconciledMatch,
    ReconciliationJob,
    ReconciliationJobScope,
    ReconciliationJobStatus,
    ReconciliationRow,
    ReconciliationResult,
    ReconciliationStateMachineResult,
    SimpleReconciliationFinding,
    SimpleReconciliationResult,
    UncertaintyRecord,
    UncertaintyLevel,
    OperationalDifferenceEngineResult,
    WarningItem,
    WorkflowDecision,
)

BLOCKING_FIELDS = {"cuit", "cuil", "sku", "entity_id"}
LOCKED_RECONCILIATION_STATUS = "handoff_confirmed"
LOCKED_RECONCILIATION_CANCELLED_STATUS = "handoff_cancelled"
PENDING_VALIDATION_STATUS = "pending_validation"
RECOGNIZED_RECONCILIATION_STATUSES = {
    PENDING_VALIDATION_STATUS,
    LOCKED_RECONCILIATION_STATUS,
    LOCKED_RECONCILIATION_CANCELLED_STATUS,
}
HUMAN_REVIEW_ISSUE_CODES = {
    "missing_core_fields",
    "too_few_columns",
    "empty_dataset",
}
GUIDED_CURATION_ISSUE_CODES = {
    "alias_headers_used",
    "currency_noise",
    "fecha_needs_normalization",
    "fecha_vencimiento_needs_normalization",
    "unknown_headers",
    "mostly_empty_columns",
    "duplicate_rows",
}
CRITICAL_WARNING_CODES = {"color_semantics_out_of_scope"}
EXPECTED_AMOUNT_FIELD_ALIASES = ("amount_expected", "expected_amount")
ACTUAL_AMOUNT_FIELD_ALIASES = ("paid_amount", "amount_paid", "actual_amount")
RECONCILIATION_JOB_STATUSES: set[ReconciliationJobStatus] = {
    "pending",
    "running",
    "failed",
    "done",
    "dead_letter",
}
RECONCILIATION_JOB_SCOPES: set[ReconciliationJobScope] = {"orders"}
RECONCILIATION_JOB_RETRY_BASE_SECONDS = 60
RECONCILIATION_JOB_RETRY_CAP_SECONDS = 1800
RECONCILIATION_JOB_MAX_ATTEMPTS = 10


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_present(value: str | int | float | bool | None) -> bool:
    return value is not None


def _to_float_or_zero(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_aware_datetime(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{field_name}_INVALIDO: {field_name} debe tener timezone.")


def _normalize_job_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name}_INVALIDO: {field_name} debe ser texto.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name}_INVALIDO: {field_name} no puede ser vacio.")
    return normalized


def _validate_reconciliation_job(job: ReconciliationJob) -> None:
    _normalize_job_text(job.job_id, "JOB_ID")
    _normalize_job_text(job.store_id, "STORE_ID")
    if job.scope not in RECONCILIATION_JOB_SCOPES:
        raise ValueError("RECONCILIATION_SCOPE_INVALIDO: scope no reconocido.")
    if job.status not in RECONCILIATION_JOB_STATUSES:
        raise ValueError("RECONCILIATION_JOB_STATUS_INVALIDO: status no reconocido.")
    if job.cursor is not None and not isinstance(job.cursor, dict):
        raise ValueError("RECONCILIATION_CURSOR_INVALIDO: cursor debe ser dict o None.")
    if job.attempts < 0:
        raise ValueError("RECONCILIATION_ATTEMPTS_INVALIDO: attempts no puede ser negativo.")
    _validate_aware_datetime(job.next_eligible_at, "NEXT_ELIGIBLE_AT")
    _validate_aware_datetime(job.created_at, "CREATED_AT")
    _validate_aware_datetime(job.updated_at, "UPDATED_AT")
    if job.locked_at is not None:
        _validate_aware_datetime(job.locked_at, "LOCKED_AT")
    if job.dead_letter_at is not None:
        _validate_aware_datetime(job.dead_letter_at, "DEAD_LETTER_AT")
    if job.locked_at is not None and not job.locked_by:
        raise ValueError(
            "RECONCILIATION_LOCK_INVALIDO: locked_by es obligatorio cuando locked_at existe."
        )
    if job.status == "running" and (job.locked_at is None or not job.locked_by):
        raise ValueError(
            "RECONCILIATION_LOCK_INVALIDO: jobs running requieren lock activo."
        )
    if job.status == "dead_letter" and job.dead_letter_at is None:
        raise ValueError(
            "RECONCILIATION_DEAD_LETTER_INVALIDO: dead_letter_at es obligatorio."
        )


def create_reconciliation_job(
    *,
    job_id: str,
    store_id: str,
    scope: ReconciliationJobScope = "orders",
    cursor: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> ReconciliationJob:
    timestamp = now or _utc_now()
    _validate_aware_datetime(timestamp, "NOW")
    if cursor is not None and not isinstance(cursor, dict):
        raise ValueError("RECONCILIATION_CURSOR_INVALIDO: cursor debe ser dict o None.")

    job = ReconciliationJob(
        job_id=_normalize_job_text(job_id, "JOB_ID"),
        store_id=_normalize_job_text(store_id, "STORE_ID"),
        scope=scope,
        cursor=dict(cursor) if cursor is not None else None,
        status="pending",
        attempts=0,
        next_eligible_at=timestamp,
        created_at=timestamp,
        updated_at=timestamp,
    )
    _validate_reconciliation_job(job)
    return job


def claim_reconciliation_jobs(
    jobs: list[ReconciliationJob],
    *,
    worker: str,
    limit: int = 1,
    scope: ReconciliationJobScope = "orders",
    now: datetime | None = None,
) -> list[ReconciliationJob]:
    if limit <= 0:
        raise ValueError("RECONCILIATION_CLAIM_LIMIT_INVALIDO: limit debe ser positivo.")
    if scope not in RECONCILIATION_JOB_SCOPES:
        raise ValueError("RECONCILIATION_SCOPE_INVALIDO: scope no reconocido.")

    worker_id = _normalize_job_text(worker, "WORKER")
    timestamp = now or _utc_now()
    _validate_aware_datetime(timestamp, "NOW")
    for job in jobs:
        _validate_reconciliation_job(job)

    eligible_jobs = [
        job
        for job in jobs
        if job.scope == scope
        and job.status in {"pending", "failed"}
        and job.locked_at is None
        and job.next_eligible_at <= timestamp
    ]
    eligible_jobs.sort(key=lambda job: (job.next_eligible_at, job.created_at, job.job_id))

    return [
        replace(
            job,
            status="running",
            attempts=job.attempts + 1,
            locked_at=timestamp,
            locked_by=worker_id,
            updated_at=timestamp,
        )
        for job in eligible_jobs[:limit]
    ]


def complete_reconciliation_job(
    job: ReconciliationJob,
    *,
    cursor: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> ReconciliationJob:
    _validate_reconciliation_job(job)
    if job.status != "running":
        raise ValueError("RECONCILIATION_JOB_NO_RUNNING: solo jobs running pueden cerrarse.")
    if cursor is not None and not isinstance(cursor, dict):
        raise ValueError("RECONCILIATION_CURSOR_INVALIDO: cursor debe ser dict o None.")
    timestamp = now or _utc_now()
    _validate_aware_datetime(timestamp, "NOW")

    completed = replace(
        job,
        cursor=dict(cursor) if cursor is not None else job.cursor,
        status="done",
        locked_at=None,
        locked_by=None,
        last_error=None,
        updated_at=timestamp,
    )
    _validate_reconciliation_job(completed)
    return completed


def fail_reconciliation_job(
    job: ReconciliationJob,
    *,
    error: str,
    now: datetime | None = None,
    max_attempts: int = RECONCILIATION_JOB_MAX_ATTEMPTS,
) -> ReconciliationJob:
    _validate_reconciliation_job(job)
    if job.status != "running":
        raise ValueError("RECONCILIATION_JOB_NO_RUNNING: solo jobs running pueden fallar.")
    if max_attempts <= 0:
        raise ValueError("RECONCILIATION_MAX_ATTEMPTS_INVALIDO: max_attempts debe ser positivo.")
    error_message = _normalize_job_text(error, "ERROR")
    timestamp = now or _utc_now()
    _validate_aware_datetime(timestamp, "NOW")

    if job.attempts >= max_attempts:
        failed = replace(
            job,
            status="dead_letter",
            locked_at=None,
            locked_by=None,
            last_error=error_message,
            dead_letter_at=timestamp,
            updated_at=timestamp,
        )
    else:
        delay_seconds = min(
            RECONCILIATION_JOB_RETRY_BASE_SECONDS * (2 ** max(job.attempts - 1, 0)),
            RECONCILIATION_JOB_RETRY_CAP_SECONDS,
        )
        failed = replace(
            job,
            status="failed",
            locked_at=None,
            locked_by=None,
            last_error=error_message,
            next_eligible_at=timestamp + timedelta(seconds=delay_seconds),
            updated_at=timestamp,
        )
    _validate_reconciliation_job(failed)
    return failed


def _normalize_reconciliation_status(job_state: Any) -> str:
    if not isinstance(job_state, dict):
        raise ValueError(
            "RECONCILIATION_STATE_INVALIDO: estado invalido para reconciliacion."
        )
    status = job_state.get("status")
    if not isinstance(status, str):
        raise ValueError(
            "RECONCILIATION_STATUS_INVALIDO: estado no reconocido para reconciliacion."
        )
    normalized_status = status.strip().lower()
    if normalized_status not in RECOGNIZED_RECONCILIATION_STATUSES:
        raise ValueError(
            "RECONCILIATION_STATUS_INVALIDO: estado no reconocido para reconciliacion."
        )
    return normalized_status


def compare_records(record_a: ComparableRecord, record_b: ComparableRecord) -> list[DifferenceRecord]:
    if record_a.entity_id != record_b.entity_id:
        raise ValueError(
            "ENTITY_ID_MISMATCH: los records comparables deben tener el mismo entity_id."
        )

    if record_a.entity_type != record_b.entity_type:
        raise ValueError(
            "ENTITY_TYPE_MISMATCH: los records comparables deben tener el mismo entity_type."
        )

    field_names = sorted(set(record_a.fields.keys()) | set(record_b.fields.keys()))
    differences: list[DifferenceRecord] = []

    for field_name in field_names:
        value_a = record_a.fields.get(field_name)
        value_b = record_b.fields.get(field_name)

        if value_a == value_b:
            continue

        present_a = _is_present(value_a)
        present_b = _is_present(value_b)

        if not present_a and present_b:
            difference_type = "faltante_en_a"
        elif present_a and not present_b:
            difference_type = "faltante_en_b"
        else:
            difference_type = "valor_distinto"

        differences.append(
            DifferenceRecord(
                entity_id=record_a.entity_id,
                entity_type=record_a.entity_type,
                field_name=field_name,
                source_a=record_a.source,
                source_b=record_b.source,
                value_a=value_a,
                value_b=value_b,
                difference_type=difference_type,
                blocking=field_name in BLOCKING_FIELDS,
            )
        )

    return differences


def _validate_key_field(key_field: str) -> None:
    if not key_field or not key_field.strip():
        raise ValueError("KEY_FIELD_INVALIDO: key_field no puede ser vacio.")


def _index_records(
    source: list[dict[str, Any]], key_field: str, source_name: str
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for raw_record in source:
        try:
            record = ReconciliationRow.model_validate(raw_record).root
        except Exception as exc:
            raise ValueError(
                f"ROW_INVALIDA: registro invalido en {source_name}. Ejecucion bloqueada."
            ) from exc
        if key_field not in record:
            raise ValueError(
                f"KEY_FIELD_FALTANTE: falta '{key_field}' en un registro de {source_name}."
            )
        key_value = record[key_field]
        if key_value is None:
            raise ValueError(
                f"KEY_FIELD_NULO: '{key_field}' es nulo en un registro de {source_name}."
            )
        key = str(key_value)
        if key in indexed:
            raise ValueError(
                f"KEY_DUPLICADA: '{key}' duplicada en {source_name}. Ejecucion bloqueada."
            )
        indexed[key] = record
    return indexed


def reconcile_records(
    source_a: list[dict[str, Any]], source_b: list[dict[str, Any]], key_field: str
) -> ReconciliationResult:
    _validate_key_field(key_field)

    indexed_a = _index_records(source_a, key_field, "source_a")
    indexed_b = _index_records(source_b, key_field, "source_b")

    keys_a = set(indexed_a.keys())
    keys_b = set(indexed_b.keys())

    common_keys = sorted(keys_a & keys_b)
    missing_in_a_keys = sorted(keys_b - keys_a)
    missing_in_b_keys = sorted(keys_a - keys_b)

    matches: list[ReconciledMatch] = []
    mismatches: list[QuantifiedDiscrepancy] = []

    for key in common_keys:
        record_a = indexed_a[key]
        record_b = indexed_b[key]
        common_fields = sorted((set(record_a.keys()) & set(record_b.keys())) - {key_field})

        key_has_mismatch = False
        for field_name in common_fields:
            value_a = record_a[field_name]
            value_b = record_b[field_name]
            if value_a == value_b:
                continue

            key_has_mismatch = True
            if _is_number(value_a) and _is_number(value_b):
                delta = float(value_b) - float(value_a)
                detail = "mismatch_numerico"
            else:
                delta = None
                detail = "mismatch_no_numerico"

            mismatches.append(
                QuantifiedDiscrepancy(
                    key=key,
                    field_name=field_name,
                    value_a=value_a,
                    value_b=value_b,
                    delta=delta,
                    detail=detail,
                )
            )

        if not key_has_mismatch:
            matches.append(
                ReconciledMatch(
                    key=key,
                    record_a=ReconciliationRow.model_validate(record_a),
                    record_b=ReconciliationRow.model_validate(record_b),
                )
            )

    missing_in_a = [ReconciliationRow.model_validate(indexed_b[key]) for key in missing_in_a_keys]
    missing_in_b = [ReconciliationRow.model_validate(indexed_a[key]) for key in missing_in_b_keys]

    return ReconciliationResult(
        matches=matches,
        mismatches=mismatches,
        missing_in_a=missing_in_a,
        missing_in_b=missing_in_b,
    )


def _read_numeric_field(record: dict[str, Any], field_name: str, key: str) -> float:
    if field_name not in record:
        raise ValueError(f"CAMPO_FALTANTE: falta '{field_name}' en registro key={key}.")
    value = record[field_name]
    if value is None:
        raise ValueError(f"CAMPO_NULO: '{field_name}' es nulo en registro key={key}.")
    if not _is_number(value):
        raise ValueError(
            f"CAMPO_NO_NUMERICO: '{field_name}' debe ser numerico en registro key={key}."
        )
    return float(value)


def _parse_amount_with_reason(value: Any) -> tuple[float | None, str | None]:
    if _is_number(value):
        return float(value), None
    if not isinstance(value, str):
        return None, "non_numeric"

    normalized = value.strip().replace(" ", "")
    for symbol in ("$", "€", "£", "¥"):
        normalized = normalized.replace(symbol, "")

    if not normalized:
        return None, "non_numeric"
    if any(char.isalpha() for char in normalized):
        return None, "non_numeric"
    if "," in normalized and "." in normalized:
        return None, "currency_ambiguous"
    if normalized.count(".") > 1:
        return None, "currency_ambiguous"

    if "," in normalized:
        left, right = normalized.rsplit(",", 1)
        if not left or not right:
            return None, "non_numeric"
        left_no_sign = left[1:] if left[0] in "+-" else left
        if not left_no_sign.isdigit() or not right.isdigit():
            return None, "non_numeric"
        if len(right) == 3:
            return None, "currency_ambiguous"
        normalized = f"{left}.{right}"

    try:
        return float(normalized), None
    except ValueError:
        return None, "non_numeric"


def detect_deterministic_ambiguity(value: Any) -> tuple[float | None, str | None]:
    return _parse_amount_with_reason(value)


def _resolve_amount_field(
    record: dict[str, Any], primary_field: str, aliases: tuple[str, ...]
) -> tuple[Any, str | None]:
    if primary_field in record:
        return record.get(primary_field), primary_field

    for alias in aliases:
        if alias in record:
            return record.get(alias), alias

    return None, None


def _build_human_question(
    *,
    key: str,
    expected_amount: float | None,
    actual_amount: float | None,
    reason: str,
) -> str:
    if reason == "monto_diferente" and expected_amount is not None and actual_amount is not None:
        return (
            f"Registro {key}: monto esperado {expected_amount:.2f} y pagado {actual_amount:.2f}. "
            "¿Confirmas el ajuste manual de conciliacion?"
        )
    if reason == "monto_incierto":
        return (
            f"Registro {key}: no se pudo confirmar uno o ambos montos. "
            "¿Puedes validar manualmente los importes esperados y pagados?"
        )
    if reason == "currency_ambiguous":
        return (
            f"Registro {key}: el formato monetario es ambiguo. "
            "¿Puedes confirmar manualmente la moneda y el monto correcto?"
        )
    return (
        f"Registro {key}: se detecto un monto no numerico. "
        "¿Puedes corregir o confirmar manualmente el valor?"
    )


def _build_clarification_question(
    *,
    key: str,
    reason: str,
    question: str,
    expected_amount: float | None,
    actual_amount: float | None,
    delta: float | None,
) -> ClarificationQuestion:
    return ClarificationQuestion(
        key=key,
        reason=reason,
        question=question,
        clarification_state="pending_validation",
        expected_amount=expected_amount,
        actual_amount=actual_amount,
        delta=delta,
        pending_validation=True,
    )


def _build_uncertainty_finding(
    *,
    key: str,
    expected_amount: float | None,
    actual_amount: float | None,
    reason: str,
) -> AmountReconciliationFinding:
    return AmountReconciliationFinding(
        key=key,
        expected_amount=expected_amount if expected_amount is not None else 0.0,
        actual_amount=actual_amount if actual_amount is not None else 0.0,
        delta=float("inf"),
        blocking=True,
        reason=reason,
        uncertainty_level="high",
        clarification_state="pending_validation",
        pending_validation=True,
        suggested_action="solicitar_revision_humana",
        human_question=_build_human_question(
            key=key,
            expected_amount=expected_amount,
            actual_amount=actual_amount,
            reason=reason,
        ),
    )


def _build_suggested_action(delta: float, is_uncertain: bool) -> str:
    if is_uncertain:
        return "solicitar_revision_humana"
    if delta > 0:
        return "sugerir_cobro_diferencia"
    return "sugerir_revision_sobrepago"


def _uncertainty_level_for_reason(reason: str) -> UncertaintyLevel:
    if reason in {"non_numeric", "currency_ambiguous", "monto_incierto"}:
        return "high"
    if reason == "monto_diferente":
        return "medium"
    return "high"


def _max_uncertainty_level(levels: list[UncertaintyLevel]) -> UncertaintyLevel:
    if not levels:
        return "low"
    if "high" in levels:
        return "high"
    if "medium" in levels:
        return "medium"
    return "low"


def _route_workflow_from_uncertainty(level: UncertaintyLevel) -> WorkflowDecision:
    if level == "high":
        return "human_review_required"
    if level == "medium":
        return "guided_curation"
    return "direct_parse"


def _max_workflow_decision(
    left: WorkflowDecision, right: WorkflowDecision
) -> WorkflowDecision:
    ranking: dict[WorkflowDecision, int] = {
        "direct_parse": 0,
        "guided_curation": 1,
        "human_review_required": 2,
    }
    return left if ranking[left] >= ranking[right] else right


def _clarification_state_from_blocking(has_blocking_pending: bool) -> ClarificationState:
    return "pending_validation" if has_blocking_pending else "no_requiere"


def _accumulate_warnings(warnings: list[WarningItem] | None) -> list[WarningItem]:
    if not warnings:
        return []

    deduped: list[WarningItem] = []
    seen: set[tuple[str, str, str, str, str, str, bool]] = set()
    for warning in warnings:
        signature = (
            warning.code,
            warning.key or "",
            warning.field_name or "",
            warning.message,
            repr(warning.details) if warning.details is not None else "",
            warning.severity,
            warning.blocking,
        )
        if signature in seen:
            continue
        seen.add(signature)
        deduped.append(warning)
    return deduped


def evaluate_warnings_fail_closed(warnings: list[WarningItem] | None) -> WorkflowDecision:
    accumulated_warnings = _accumulate_warnings(warnings)
    if not accumulated_warnings:
        return "direct_parse"

    for warning in accumulated_warnings:
        if warning.blocking:
            return "human_review_required"
        if warning.severity == "critical":
            return "human_review_required"
        if warning.code in CRITICAL_WARNING_CODES:
            return "human_review_required"

    return "direct_parse"


def evaluate_fail_closed_rules(
    *,
    warnings: list[WarningItem] | None,
    uncertainty_records: list[UncertaintyRecord],
    findings: list[AmountReconciliationFinding],
) -> FailClosedStateEvaluation:
    warning_decision = evaluate_warnings_fail_closed(warnings)
    has_warning_blocker = warning_decision == "human_review_required"
    has_uncertainty_blocker = bool(uncertainty_records) or bool(findings)
    has_blocking_pending = has_warning_blocker or has_uncertainty_blocker

    if has_warning_blocker and has_uncertainty_blocker:
        trigger = "warnings_and_uncertainties"
    elif has_warning_blocker:
        trigger = "warnings"
    elif has_uncertainty_blocker:
        trigger = "uncertainties"
    else:
        trigger = "none"

    workflow_decision = "human_review_required" if has_blocking_pending else "direct_parse"
    return FailClosedStateEvaluation(
        workflow_decision=workflow_decision,
        clarification_state=_clarification_state_from_blocking(has_blocking_pending),
        has_blocking_pending=has_blocking_pending,
        trigger=trigger,
    )


def initialize_fail_closed_human_validation(
    *,
    warnings: list[WarningItem] | None,
    uncertainty_records: list[UncertaintyRecord],
    findings: list[AmountReconciliationFinding],
) -> FailClosedStateEvaluation:
    return evaluate_fail_closed_rules(
        warnings=warnings,
        uncertainty_records=uncertainty_records,
        findings=findings,
    )


def _append_uncertainty_blocking_findings(
    *,
    key: str,
    expected_amount_field: str,
    actual_amount_field: str,
    expected_raw: Any,
    actual_raw: Any,
    reason: str,
    findings: list[AmountReconciliationFinding],
    uncertainty_records: list[UncertaintyRecord],
    suggested_actions: list[str],
) -> None:
    if expected_raw is None:
        uncertainty_records.append(
            UncertaintyRecord(
                key=key,
                field_name=expected_amount_field,
                raw_value=expected_raw,
                reason=reason,
                uncertainty_level="high",
                blocking=True,
                clarification_state="pending_validation",
                pending_validation=True,
            )
        )

    if actual_raw is None:
        uncertainty_records.append(
            UncertaintyRecord(
                key=key,
                field_name=actual_amount_field,
                raw_value=actual_raw,
                reason=reason,
                uncertainty_level="high",
                blocking=True,
                clarification_state="pending_validation",
                pending_validation=True,
            )
        )

    findings.append(
        _build_uncertainty_finding(
            key=key,
            expected_amount=expected_raw if _is_number(expected_raw) else None,
            actual_amount=actual_raw if _is_number(actual_raw) else None,
            reason=reason,
        )
    )
    suggested_actions.append("solicitar_revision_humana")


def _compute_exact_delta(expected_amount: float, actual_amount: float) -> float:
    expected_decimal = Decimal(str(expected_amount))
    actual_decimal = Decimal(str(actual_amount))
    return float(expected_decimal - actual_decimal)


def calculate_economic_impact(expected_amount: float, actual_amount: float) -> EconomicImpact:
    delta = _compute_exact_delta(expected_amount, actual_amount)
    if delta > 0:
        direction = "shortfall"
    elif delta < 0:
        direction = "overpayment"
    else:
        direction = "balanced"

    return EconomicImpact(delta=delta, absolute_delta=abs(delta), direction=direction)


def detect_amount_difference(
    *,
    expected_amount: float,
    actual_amount: float,
    tolerance: float,
    uncertainty_threshold: float | None,
) -> AmountDifferenceAssessment:
    engine_result = compute_operational_difference_engine(
        expected_amount=expected_amount,
        actual_amount=actual_amount,
        tolerance=tolerance,
        uncertainty_threshold=uncertainty_threshold,
    )
    return AmountDifferenceAssessment(
        delta=engine_result.delta,
        has_difference=engine_result.has_difference,
        uncertain=engine_result.uncertain,
        reason=engine_result.reason,
    )


def compute_operational_difference_engine(
    *,
    expected_amount: float,
    actual_amount: float,
    tolerance: float,
    uncertainty_threshold: float | None,
) -> OperationalDifferenceEngineResult:
    impact = calculate_economic_impact(expected_amount, actual_amount)
    if impact.absolute_delta == 0:
        return OperationalDifferenceEngineResult(
            delta=impact.delta,
            absolute_delta=impact.absolute_delta,
            has_difference=False,
            uncertain=False,
            reason=None,
        )

    uncertain = uncertainty_threshold is not None and impact.absolute_delta <= uncertainty_threshold
    reason = "monto_incierto" if uncertain else "monto_diferente"
    return OperationalDifferenceEngineResult(
        delta=impact.delta,
        absolute_delta=impact.absolute_delta,
        has_difference=True,
        uncertain=uncertain,
        reason=reason,
    )


def _build_amount_difference_finding(
    *,
    key: str,
    expected_amount: float,
    actual_amount: float,
    tolerance: float,
    uncertainty_threshold: float | None,
) -> AmountReconciliationFinding | None:
    difference = detect_amount_difference(
        expected_amount=expected_amount,
        actual_amount=actual_amount,
        tolerance=tolerance,
        uncertainty_threshold=uncertainty_threshold,
    )
    if not difference.has_difference:
        return None

    suggested_action = _build_suggested_action(difference.delta, difference.uncertain)
    return AmountReconciliationFinding(
        key=key,
        expected_amount=expected_amount,
        actual_amount=actual_amount,
        delta=difference.delta,
        blocking=True,
        reason=difference.reason or "monto_diferente",
        uncertainty_level="high",
        clarification_state="pending_validation",
        pending_validation=True,
        suggested_action=suggested_action,
        human_question=_build_human_question(
            key=key,
            expected_amount=expected_amount,
            actual_amount=actual_amount,
            reason=difference.reason or "monto_diferente",
        ),
    )


def resolve_deterministic_amount_finding(
    *,
    key: str,
    expected_amount: float,
    actual_amount: float,
    tolerance: float,
    uncertainty_threshold: float | None,
) -> AmountReconciliationFinding | None:
    return _build_amount_difference_finding(
        key=key,
        expected_amount=expected_amount,
        actual_amount=actual_amount,
        tolerance=tolerance,
        uncertainty_threshold=uncertainty_threshold,
    )


def route_amount_reconciliation_for_human_review(
    *,
    findings: list[AmountReconciliationFinding],
    uncertainty_levels: list[UncertaintyLevel],
    suggested_actions: list[str],
) -> tuple[ReconciliationStateMachineResult, UncertaintyLevel, list[str]]:
    has_blocking_pending = bool(findings)
    max_uncertainty_level = _max_uncertainty_level(uncertainty_levels)
    amount_workflow_decision: WorkflowDecision = (
        "human_review_required"
        if has_blocking_pending
        else _route_workflow_from_uncertainty(max_uncertainty_level)
    )
    state_machine = resolve_reconciliation_state_machine(
        amount_workflow_decision=amount_workflow_decision,
    )

    resolved_actions = list(suggested_actions)
    if state_machine.has_blocking_pending:
        resolved_actions.append("solicitar_revision_humana")
    return state_machine, max_uncertainty_level, sorted(set(resolved_actions))


def decide_next_action_from_issues(issues: list[dict[str, Any]]) -> WorkflowDecision:
    if not issues:
        return "direct_parse"

    issue_codes: set[str | None] = set()
    for issue in issues:
        if not isinstance(issue, dict):
            return "human_review_required"
        issue_codes.add(issue.get("code"))

    if None in issue_codes:
        return "human_review_required"
    if issue_codes & HUMAN_REVIEW_ISSUE_CODES:
        return "human_review_required"
    if issue_codes & GUIDED_CURATION_ISSUE_CODES:
        return "guided_curation"
    return "human_review_required"


def build_deterministic_discrepancy_snapshot(
    findings: list[AmountReconciliationFinding],
) -> DeterministicDiscrepancySnapshot:
    mapped_findings: list[dict[str, Any]] = []
    orders_with_diff = 0
    total_diff_amount = 0.0
    for finding in findings:
        finite_delta = isfinite(finding.delta)
        if finite_delta:
            orders_with_diff += 1
            total_diff_amount += finding.delta
        mapped_findings.append(
            {
                "severity": "high",
                "message": f"Diferencia detectada en orden {finding.key}",
                "entity": finding.key,
                "diff": finding.delta if finite_delta else None,
                "money_impact": abs(finding.delta) if finite_delta else None,
                "clarification_state": finding.clarification_state,
                "pending_validation": finding.pending_validation,
                "reason": finding.reason,
                "human_question": finding.human_question,
            }
        )

    return DeterministicDiscrepancySnapshot(
        findings=mapped_findings,
        orders_with_diff=orders_with_diff,
        total_diff_amount=total_diff_amount,
    )


def evaluate_deterministic_hitl_state(
    *,
    amount_workflow_decision: WorkflowDecision,
    issues: list[dict[str, Any]] | None,
    warnings: list[WarningItem] | None,
    uncertainty_records: list[UncertaintyRecord],
    findings: list[AmountReconciliationFinding],
) -> DeterministicHitlEvaluation:
    issue_decision = decide_next_action_from_issues(issues or [])
    fail_closed_state = initialize_fail_closed_human_validation(
        warnings=warnings,
        uncertainty_records=uncertainty_records,
        findings=findings,
    )
    workflow_decision = _max_workflow_decision(amount_workflow_decision, issue_decision)
    workflow_decision = _max_workflow_decision(
        workflow_decision, fail_closed_state.workflow_decision
    )
    state_machine = resolve_reconciliation_state_machine(
        amount_workflow_decision=workflow_decision,
    )
    return DeterministicHitlEvaluation(
        issue_decision=issue_decision,
        amount_decision=amount_workflow_decision,
        fail_closed_decision=fail_closed_state.workflow_decision,
        workflow_decision=state_machine.workflow_decision,
        clarification_state=state_machine.clarification_state,
        has_blocking_pending=state_machine.has_blocking_pending,
    )


def _meli_action_to_dict(action: MeliSuggestedAction) -> dict[str, Any]:
    payload = asdict(action)
    if payload["economic_impact"] is None:
        payload.pop("economic_impact")
    return payload


def analyze_meli_reconciliation(rows: list[dict[str, Any]] | Any) -> dict[str, Any]:
    if not isinstance(rows, list):
        raise ValueError(
            "ROW_INVALIDA: rows debe ser una lista de registros. Ejecucion bloqueada."
        )
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(
                "ROW_INVALIDA: registro invalido en rows. Ejecucion bloqueada."
            )
    safe_rows = rows
    result = analyze_amount_reconciliation(
        safe_rows,
        key_field="order_id",
        expected_amount_field="amount_expected",
        actual_amount_field="amount_paid",
    )

    discrepancy_snapshot = build_deterministic_discrepancy_snapshot(result.findings)
    findings = discrepancy_snapshot.findings
    orders_with_diff = discrepancy_snapshot.orders_with_diff
    total_diff_amount = discrepancy_snapshot.total_diff_amount

    suggested_actions: list[dict[str, Any]] = []
    if result.has_blocking_pending:
        suggested_actions.append(
            _meli_action_to_dict(
                MeliSuggestedAction(
                    action_type="solicitar_revision_humana",
                    title="Revisión humana requerida",
                    description=(
                        "Flujo bloqueado en pending_validation por diferencias o incertidumbre."
                    ),
                    payload={
                        "workflow_decision": result.workflow_decision,
                        "clarification_state": result.clarification_state,
                        "human_review_questions": result.human_review_questions,
                    },
                )
            )
        )

    if orders_with_diff > 0:
        suggested_actions.append(
            _meli_action_to_dict(
                MeliSuggestedAction(
                    action_type="generar_documento",
                    title="Resumen de diferencias de conciliación",
                    description=(
                        "Se detectaron diferencias entre montos esperados y pagos recibidos"
                    ),
                    economic_impact=abs(total_diff_amount),
                    payload={
                        "format": "pdf",
                        "template": "meli_reconciliation_diff",
                        "data": {
                            "orders_with_diff": orders_with_diff,
                            "total_diff_amount": total_diff_amount,
                            "workflow_decision": result.workflow_decision,
                            "clarification_state": result.clarification_state,
                            "requires_human_validation": result.has_blocking_pending,
                        },
                    },
                )
            )
        )

    summary = {
        "total_orders": result.total_records,
        "orders_with_diff": orders_with_diff,
        "total_diff_amount": total_diff_amount,
        "estimated_recoverable_amount": abs(total_diff_amount),
        "workflow_decision": result.workflow_decision,
        "clarification_state": result.clarification_state,
        "has_blocking_pending": result.has_blocking_pending,
        "human_review_questions": result.human_review_questions,
    }
    return {
        "canonical_rows": safe_rows,
        "findings": findings,
        "summary": summary,
        "suggested_actions": suggested_actions,
    }


def raise_if_job_confirmed(result: dict[str, Any]) -> None:
    normalized_status = _normalize_reconciliation_status(result)
    if normalized_status in {
        LOCKED_RECONCILIATION_STATUS,
        LOCKED_RECONCILIATION_CANCELLED_STATUS,
    }:
        raise ValueError(
            "JOB_YA_CONFIRMADO: el job fue confirmado y quedo cerrado para nuevas mutaciones."
        )


def apply_human_review_decision(
    job_state: dict[str, Any],
    decision: HumanReviewDecision,
    persist_decision: (
        Callable[[dict[str, Any], HumanReviewDecision, dict[str, Any]], dict[str, Any] | None]
        | None
    ) = None,
) -> dict[str, Any]:
    raise_if_job_confirmed(job_state)
    normalized_status = _normalize_reconciliation_status(job_state)
    if normalized_status != PENDING_VALIDATION_STATUS:
        raise ValueError(
            "JOB_NO_BLOQUEADO: solo se puede resolver un job en estado pending_validation."
        )

    if not isinstance(decision.actor, str):
        raise ValueError("ACTOR_INVALIDO: actor debe ser texto.")
    actor = decision.actor.strip()
    if not actor:
        raise ValueError("ACTOR_INVALIDO: actor no puede ser vacio.")
    if decision.verdict not in {"confirm", "cancel"}:
        raise ValueError(
            "VERDICT_INVALIDO: verdict debe ser 'confirm' o 'cancel'."
        )

    resolved_status = (
        LOCKED_RECONCILIATION_STATUS
        if decision.verdict == "confirm"
        else LOCKED_RECONCILIATION_CANCELLED_STATUS
    )
    resolved_state = dict(job_state)
    resolved_state["status"] = resolved_status
    resolved_state["human_review_actor"] = actor
    resolved_state["human_review_verdict"] = decision.verdict
    resolved_state["human_review_note"] = decision.note
    if persist_decision is None:
        return resolved_state

    try:
        persisted_state = persist_decision(job_state, decision, resolved_state)
    except Exception as exc:
        raise ValueError(
            "HUMAN_REVIEW_PERSISTENCE_FALLIDA: no se pudo persistir la decision humana."
        ) from exc

    if persisted_state is None:
        return resolved_state
    if not isinstance(persisted_state, dict):
        raise ValueError(
            "HUMAN_REVIEW_PERSISTENCE_INVALIDA: la persistencia debe devolver dict o None."
        )
    persisted_status = persisted_state.get("status")
    normalized_persisted_status = (
        persisted_status.strip().lower()
        if isinstance(persisted_status, str)
        else persisted_status
    )
    if normalized_persisted_status != resolved_status:
        raise ValueError(
            "HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA: la persistencia no puede reabrir ni alterar el estado resuelto."
        )
    persisted_actor = persisted_state.get("human_review_actor")
    if persisted_actor != actor:
        raise ValueError(
            "HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA: la persistencia no puede alterar el actor de la decision humana."
        )
    persisted_verdict = persisted_state.get("human_review_verdict")
    if persisted_verdict != decision.verdict:
        raise ValueError(
            "HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA: la persistencia no puede alterar el veredicto humano resuelto."
        )
    if persisted_state.get("human_review_note") != decision.note:
        raise ValueError(
            "HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA: la persistencia no puede alterar la nota de la decision humana."
        )
    return persisted_state


def resolve_discrepancy(
    job_state: dict[str, Any],
    decision: HumanReviewDecision,
    persist_decision: (
        Callable[[dict[str, Any], HumanReviewDecision, dict[str, Any]], dict[str, Any] | None]
        | None
    ) = None,
) -> dict[str, Any]:
    return apply_human_review_decision(
        job_state,
        decision,
        persist_decision=persist_decision,
    )


def analyze_amount_reconciliation(
    records: list[dict[str, Any]],
    *,
    key_field: str = "order_id",
    expected_amount_field: str = "expected_amount",
    actual_amount_field: str = "actual_amount",
    tolerance: float = 0.0,
    uncertainty_threshold: float | None = None,
) -> AmountReconciliationResult:
    _validate_key_field(key_field)
    if tolerance < 0:
        raise ValueError("TOLERANCE_INVALIDA: tolerance no puede ser negativa.")
    if uncertainty_threshold is not None and uncertainty_threshold < tolerance:
        raise ValueError(
            "UNCERTAINTY_THRESHOLD_INVALIDO: uncertainty_threshold no puede ser menor a tolerance."
        )

    findings: list[AmountReconciliationFinding] = []
    uncertainty_records: list[UncertaintyRecord] = []
    suggested_actions: list[str] = []
    uncertainty_levels: list[UncertaintyLevel] = []
    human_review_questions: list[str] = []
    clarification_questions: list[ClarificationQuestion] = []
    ok_records = 0
    seen_keys: set[str] = set()

    for raw_record in records:
        try:
            record = ReconciliationRow.model_validate(raw_record).root
        except Exception as exc:
            raise ValueError("ROW_INVALIDA: registro invalido en records. Ejecucion bloqueada.") from exc
        if key_field not in record:
            raise ValueError(f"KEY_FIELD_FALTANTE: falta '{key_field}' en un registro.")
        key_value = record[key_field]
        if key_value is None:
            raise ValueError(f"KEY_FIELD_NULO: '{key_field}' es nulo en un registro.")
        key = str(key_value)
        if key in seen_keys:
            raise ValueError(f"KEY_DUPLICADA: '{key}' duplicada en records. Ejecucion bloqueada.")
        seen_keys.add(key)

        expected_raw, resolved_expected_field = _resolve_amount_field(
            record, expected_amount_field, EXPECTED_AMOUNT_FIELD_ALIASES
        )
        actual_raw, resolved_actual_field = _resolve_amount_field(
            record, actual_amount_field, ACTUAL_AMOUNT_FIELD_ALIASES
        )
        expected_field_for_uncertainty = resolved_expected_field or expected_amount_field
        actual_field_for_uncertainty = resolved_actual_field or actual_amount_field

        if resolved_expected_field is None or resolved_actual_field is None:
            question = _build_human_question(
                key=key,
                expected_amount=expected_raw if _is_number(expected_raw) else None,
                actual_amount=actual_raw if _is_number(actual_raw) else None,
                reason="monto_incierto",
            )
            _append_uncertainty_blocking_findings(
                key=key,
                expected_amount_field=expected_field_for_uncertainty,
                actual_amount_field=actual_field_for_uncertainty,
                expected_raw=expected_raw,
                actual_raw=actual_raw,
                reason="monto_incierto",
                findings=findings,
                uncertainty_records=uncertainty_records,
                suggested_actions=suggested_actions,
            )
            uncertainty_levels.append("high")
            human_review_questions.append(question)
            clarification_questions.append(
                _build_clarification_question(
                    key=key,
                    reason="monto_incierto",
                    question=question,
                    expected_amount=expected_raw if _is_number(expected_raw) else None,
                    actual_amount=actual_raw if _is_number(actual_raw) else None,
                    delta=None,
                )
            )
            continue

        if expected_raw is None or actual_raw is None:
            question = _build_human_question(
                key=key,
                expected_amount=expected_raw if _is_number(expected_raw) else None,
                actual_amount=actual_raw if _is_number(actual_raw) else None,
                reason="monto_incierto",
            )
            _append_uncertainty_blocking_findings(
                key=key,
                expected_amount_field=expected_field_for_uncertainty,
                actual_amount_field=actual_field_for_uncertainty,
                expected_raw=expected_raw,
                actual_raw=actual_raw,
                reason="monto_incierto",
                findings=findings,
                uncertainty_records=uncertainty_records,
                suggested_actions=suggested_actions,
            )
            uncertainty_levels.append("high")
            human_review_questions.append(question)
            clarification_questions.append(
                _build_clarification_question(
                    key=key,
                    reason="monto_incierto",
                    question=question,
                    expected_amount=expected_raw if _is_number(expected_raw) else None,
                    actual_amount=actual_raw if _is_number(actual_raw) else None,
                    delta=None,
                )
            )
            continue

        expected_amount, expected_reason = detect_deterministic_ambiguity(expected_raw)
        actual_amount, actual_reason = detect_deterministic_ambiguity(actual_raw)

        if expected_reason is not None:
            uncertainty_records.append(
                UncertaintyRecord(
                    key=key,
                    field_name=expected_field_for_uncertainty,
                    raw_value=expected_raw,
                    reason=expected_reason,
                    uncertainty_level=_uncertainty_level_for_reason(expected_reason),
                    blocking=True,
                    clarification_state="pending_validation",
                    pending_validation=True,
                )
            )
            uncertainty_finding = _build_uncertainty_finding(
                key=key,
                expected_amount=expected_amount,
                actual_amount=actual_amount,
                reason=expected_reason,
            )
            findings.append(uncertainty_finding)
            uncertainty_levels.append(uncertainty_finding.uncertainty_level)
            if uncertainty_finding.human_question is not None:
                human_review_questions.append(uncertainty_finding.human_question)
                clarification_questions.append(
                    _build_clarification_question(
                        key=key,
                        reason=uncertainty_finding.reason,
                        question=uncertainty_finding.human_question,
                        expected_amount=uncertainty_finding.expected_amount,
                        actual_amount=uncertainty_finding.actual_amount,
                        delta=None,
                    )
                )
            suggested_actions.append("solicitar_revision_humana")
            continue

        if actual_reason is not None:
            uncertainty_records.append(
                UncertaintyRecord(
                    key=key,
                    field_name=actual_field_for_uncertainty,
                    raw_value=actual_raw,
                    reason=actual_reason,
                    uncertainty_level=_uncertainty_level_for_reason(actual_reason),
                    blocking=True,
                    clarification_state="pending_validation",
                    pending_validation=True,
                )
            )
            uncertainty_finding = _build_uncertainty_finding(
                key=key,
                expected_amount=expected_amount,
                actual_amount=actual_amount,
                reason=actual_reason,
            )
            findings.append(uncertainty_finding)
            uncertainty_levels.append(uncertainty_finding.uncertainty_level)
            if uncertainty_finding.human_question is not None:
                human_review_questions.append(uncertainty_finding.human_question)
                clarification_questions.append(
                    _build_clarification_question(
                        key=key,
                        reason=uncertainty_finding.reason,
                        question=uncertainty_finding.human_question,
                        expected_amount=uncertainty_finding.expected_amount,
                        actual_amount=uncertainty_finding.actual_amount,
                        delta=None,
                    )
                )
            suggested_actions.append("solicitar_revision_humana")
            continue

        if expected_amount is None or actual_amount is None:
            raise ValueError(
                f"CAMPO_NO_NUMERICO: no se pudo parsear monto en registro key={key}."
            )

        finding = resolve_deterministic_amount_finding(
            key=key,
            expected_amount=expected_amount,
            actual_amount=actual_amount,
            tolerance=tolerance,
            uncertainty_threshold=uncertainty_threshold,
        )
        if finding is None:
            ok_records += 1
            continue

        findings.append(finding)
        uncertainty_levels.append(finding.uncertainty_level)
        if finding.human_question is not None:
            human_review_questions.append(finding.human_question)
            clarification_questions.append(
                _build_clarification_question(
                    key=key,
                    reason=finding.reason,
                    question=finding.human_question,
                    expected_amount=finding.expected_amount,
                    actual_amount=finding.actual_amount,
                    delta=finding.delta,
                )
            )
        suggested_actions.append(finding.suggested_action)

    state_machine, max_uncertainty_level, resolved_actions = (
        route_amount_reconciliation_for_human_review(
            findings=findings,
            uncertainty_levels=uncertainty_levels,
            suggested_actions=suggested_actions,
        )
    )
    return AmountReconciliationResult(
        total_records=len(records),
        ok_records=ok_records,
        findings=findings,
        uncertainty_records=uncertainty_records,
        suggested_actions=resolved_actions,
        workflow_decision=state_machine.workflow_decision,
        clarification_state=state_machine.clarification_state,
        max_uncertainty_level=max_uncertainty_level,
        has_blocking_pending=state_machine.has_blocking_pending,
        human_review_questions=human_review_questions,
        clarification_questions=clarification_questions,
        warnings=[],
    )


def run_reconciliation_engine(
    records: list[dict[str, Any]],
    *,
    job_state: dict[str, Any] | None = None,
    issues: list[dict[str, Any]] | None = None,
    warnings: list[WarningItem] | None = None,
    key_field: str = "order_id",
    expected_amount_field: str = "expected_amount",
    actual_amount_field: str = "actual_amount",
    tolerance: float = 0.0,
    uncertainty_threshold: float | None = None,
) -> AmountReconciliationResult:
    if job_state is not None:
        raise_if_job_confirmed(job_state)

    accumulated_warnings = _accumulate_warnings(warnings)
    result = analyze_amount_reconciliation(
        records,
        key_field=key_field,
        expected_amount_field=expected_amount_field,
        actual_amount_field=actual_amount_field,
        tolerance=tolerance,
        uncertainty_threshold=uncertainty_threshold,
    )
    hitl_state = evaluate_deterministic_hitl_state(
        amount_workflow_decision=result.workflow_decision,
        issues=issues,
        warnings=accumulated_warnings,
        uncertainty_records=result.uncertainty_records,
        findings=result.findings,
    )

    suggested_actions = list(result.suggested_actions)
    if hitl_state.has_blocking_pending:
        suggested_actions.append("solicitar_revision_humana")

    return AmountReconciliationResult(
        total_records=result.total_records,
        ok_records=result.ok_records,
        findings=result.findings,
        uncertainty_records=result.uncertainty_records,
        suggested_actions=sorted(set(suggested_actions)),
        workflow_decision=hitl_state.workflow_decision,
        clarification_state=hitl_state.clarification_state,
        max_uncertainty_level=result.max_uncertainty_level,
        has_blocking_pending=hitl_state.has_blocking_pending,
        human_review_questions=result.human_review_questions,
        clarification_questions=result.clarification_questions,
        warnings=accumulated_warnings,
    )


def run_meli_reconciliation(
    rows: list[dict[str, Any]] | Any,
    *,
    job_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if job_state is not None:
        raise_if_job_confirmed(job_state)
    return analyze_meli_reconciliation(rows)


def resolve_reconciliation_state_machine(
    *,
    amount_workflow_decision: WorkflowDecision,
) -> ReconciliationStateMachineResult:
    has_blocking_pending = amount_workflow_decision != "direct_parse"
    return ReconciliationStateMachineResult(
        workflow_decision=amount_workflow_decision,
        clarification_state=_clarification_state_from_blocking(has_blocking_pending),
        has_blocking_pending=has_blocking_pending,
    )


def analyze_simple_amount_reconciliation(
    rows: list[dict],
    *,
    key_field: str = "order_id",
    expected_amount_field: str = "amount_expected",
    actual_amount_field: str = "amount_paid",
) -> SimpleReconciliationResult:
    findings: list[SimpleReconciliationFinding] = []
    total_records = 0
    records_with_diff = 0
    total_diff_amount = 0.0

    safe_rows = rows if isinstance(rows, list) else []

    for row in safe_rows:
        if not isinstance(row, dict):
            continue

        total_records += 1

        entity_id = str(row.get(key_field) or "unknown")
        amount_expected = _to_float_or_zero(row.get(expected_amount_field))
        amount_paid = _to_float_or_zero(row.get(actual_amount_field))
        diff = amount_expected - amount_paid

        if abs(diff) > 0:
            records_with_diff += 1
            total_diff_amount += diff

            findings.append(
                SimpleReconciliationFinding(
                    entity_id=entity_id,
                    diff=diff,
                    money_impact=abs(diff),
                )
            )

    return SimpleReconciliationResult(
        findings=findings,
        total_records=total_records,
        records_with_diff=records_with_diff,
        total_diff_amount=total_diff_amount,
    )


def build_reconciliation_summary(
    result: AmountReconciliationResult,
    *,
    warnings: list[WarningItem] | None = None,
) -> dict[str, Any]:
    accumulated_warnings = _accumulate_warnings(
        warnings if warnings is not None else result.warnings
    )
    fail_closed_state = initialize_fail_closed_human_validation(
        warnings=accumulated_warnings,
        uncertainty_records=result.uncertainty_records,
        findings=result.findings,
    )
    if fail_closed_state.has_blocking_pending:
        return {
            "status": "blocked",
            "human_in_the_loop": True,
            "workflow_decision": fail_closed_state.workflow_decision,
            "clarification_state": fail_closed_state.clarification_state,
            "fail_closed_trigger": fail_closed_state.trigger,
            "message": (
                "Se detectaron advertencias o incertidumbres que bloquean el flujo "
                "hasta revision humana."
            ),
            "human_review_questions": result.human_review_questions,
            "clarification_questions": result.clarification_questions,
            "warnings": accumulated_warnings,
        }

    return {
        "status": "ok" if not result.has_blocking_pending else "blocked",
        "human_in_the_loop": result.has_blocking_pending,
        "workflow_decision": result.workflow_decision,
        "total_records": result.total_records,
        "ok_records": result.ok_records,
        "findings": result.findings,
        "clarification_questions": result.clarification_questions,
        "warnings": accumulated_warnings,
    }

