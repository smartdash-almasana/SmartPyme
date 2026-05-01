from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, TypeAlias

ReconciliationFieldValue: TypeAlias = str | int | float | bool | None
DifferenceType: TypeAlias = Literal["faltante_en_a", "faltante_en_b", "valor_distinto"]
MismatchDetail: TypeAlias = Literal["mismatch_numerico", "mismatch_no_numerico"]
ClarificationState: TypeAlias = Literal["no_requiere", "pending_validation"]
UncertaintyReason: TypeAlias = Literal["currency_ambiguous", "non_numeric", "monto_incierto"]
SuggestedAction: TypeAlias = Literal[
    "sin_accion",
    "solicitar_revision_humana",
    "sugerir_cobro_diferencia",
    "sugerir_revision_sobrepago",
]
MeliActionType: TypeAlias = Literal["solicitar_revision_humana", "generar_documento"]
AmountFindingReason: TypeAlias = Literal[
    "monto_diferente",
    "monto_incierto",
    "non_numeric",
    "currency_ambiguous",
]
WorkflowDecision: TypeAlias = Literal[
    "direct_parse",
    "guided_curation",
    "human_review_required",
]
EconomicImpactDirection: TypeAlias = Literal["balanced", "shortfall", "overpayment"]
HumanReviewVerdict: TypeAlias = Literal["confirm", "cancel"]
ResolutionStatus: TypeAlias = Literal[
    "pending_validation",
    "handoff_confirmed",
    "handoff_cancelled",
]
UncertaintyLevel: TypeAlias = Literal["low", "medium", "high"]
WarningCode: TypeAlias = Literal[
    "color_semantics_out_of_scope",
    "currency_ambiguous",
    "formula_without_value",
    "unknown_semantic_mapping",
]
WarningSeverity: TypeAlias = Literal["info", "warning", "critical"]
WarningDetails: TypeAlias = dict[str, Any]
FailClosedTrigger: TypeAlias = Literal[
    "none",
    "warnings",
    "uncertainties",
    "warnings_and_uncertainties",
]
ReconciliationJobStatus: TypeAlias = Literal[
    "pending",
    "running",
    "failed",
    "done",
    "dead_letter",
]
ReconciliationJobScope: TypeAlias = Literal["orders"]


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ReconciliationRow:
    root: dict[str, ReconciliationFieldValue]

    @classmethod
    def model_validate(cls, value: Any) -> "ReconciliationRow":
        if not isinstance(value, dict):
            raise ValueError("RECONCILIATION_ROW_INVALIDA: row debe ser dict.")

        validated: dict[str, ReconciliationFieldValue] = {}
        for field_name, field_value in value.items():
            if not isinstance(field_name, str):
                raise ValueError("RECONCILIATION_ROW_INVALIDA: headers deben ser texto.")
            if field_value is not None and not isinstance(field_value, (str, int, float, bool)):
                raise ValueError("RECONCILIATION_ROW_INVALIDA: valor no soportado.")
            validated[field_name] = field_value
        return cls(root=validated)


@dataclass(frozen=True, slots=True)
class ComparableRecord:
    entity_id: str
    entity_type: str
    source: str
    fields: dict[str, ReconciliationFieldValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DifferenceRecord:
    entity_id: str
    entity_type: str
    field_name: str
    source_a: str
    source_b: str
    value_a: ReconciliationFieldValue
    value_b: ReconciliationFieldValue
    difference_type: DifferenceType
    blocking: bool


@dataclass(frozen=True, slots=True)
class ReconciledMatch:
    key: str
    record_a: ReconciliationRow
    record_b: ReconciliationRow


@dataclass(frozen=True, slots=True)
class QuantifiedDiscrepancy:
    key: str
    field_name: str
    value_a: ReconciliationFieldValue
    value_b: ReconciliationFieldValue
    delta: float | None
    detail: MismatchDetail


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    matches: list[ReconciledMatch]
    mismatches: list[QuantifiedDiscrepancy]
    missing_in_a: list[ReconciliationRow]
    missing_in_b: list[ReconciliationRow]


@dataclass(frozen=True, slots=True)
class UncertaintyRecord:
    key: str
    field_name: str
    raw_value: ReconciliationFieldValue
    reason: UncertaintyReason
    uncertainty_level: UncertaintyLevel
    blocking: bool
    clarification_state: ClarificationState
    pending_validation: bool


@dataclass(frozen=True, slots=True)
class AmountReconciliationFinding:
    key: str
    expected_amount: float
    actual_amount: float
    delta: float
    blocking: bool
    reason: AmountFindingReason
    uncertainty_level: UncertaintyLevel
    clarification_state: ClarificationState
    pending_validation: bool
    suggested_action: SuggestedAction
    human_question: str | None = None


@dataclass(frozen=True, slots=True)
class ClarificationQuestion:
    key: str
    reason: AmountFindingReason
    question: str
    clarification_state: ClarificationState
    expected_amount: float | None = None
    actual_amount: float | None = None
    delta: float | None = None
    pending_validation: bool = True


@dataclass(frozen=True, slots=True)
class AmountReconciliationResult:
    total_records: int
    ok_records: int
    findings: list[AmountReconciliationFinding]
    uncertainty_records: list[UncertaintyRecord]
    suggested_actions: list[SuggestedAction]
    workflow_decision: WorkflowDecision
    clarification_state: ClarificationState
    max_uncertainty_level: UncertaintyLevel
    has_blocking_pending: bool
    human_review_questions: list[str] = field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = field(default_factory=list)
    warnings: list["WarningItem"] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class AmountDifferenceAssessment:
    delta: float
    has_difference: bool
    uncertain: bool
    reason: AmountFindingReason | None


@dataclass(frozen=True, slots=True)
class OperationalDifferenceEngineResult:
    delta: float
    absolute_delta: float
    has_difference: bool
    uncertain: bool
    reason: AmountFindingReason | None


@dataclass(frozen=True, slots=True)
class EconomicImpact:
    delta: float
    absolute_delta: float
    direction: EconomicImpactDirection


@dataclass(frozen=True, slots=True)
class HumanReviewDecision:
    verdict: HumanReviewVerdict
    actor: str
    note: str | None = None


@dataclass(frozen=True, slots=True)
class WarningItem:
    code: WarningCode
    message: str
    key: str | None = None
    field_name: str | None = None
    details: WarningDetails | None = None
    severity: WarningSeverity = "warning"
    blocking: bool = False


@dataclass(frozen=True, slots=True)
class ReconciliationStateMachineResult:
    workflow_decision: WorkflowDecision
    clarification_state: ClarificationState
    has_blocking_pending: bool


@dataclass(frozen=True, slots=True)
class FailClosedStateEvaluation:
    workflow_decision: WorkflowDecision
    clarification_state: ClarificationState
    has_blocking_pending: bool
    trigger: FailClosedTrigger


@dataclass(frozen=True, slots=True)
class ReconciliationJob:
    job_id: str
    store_id: str
    scope: ReconciliationJobScope = "orders"
    cursor: dict[str, Any] | None = None
    status: ReconciliationJobStatus = "pending"
    attempts: int = 0
    next_eligible_at: datetime = field(default_factory=_utc_now)
    locked_at: datetime | None = None
    locked_by: str | None = None
    last_error: str | None = None
    dead_letter_at: datetime | None = None
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)


@dataclass(frozen=True, slots=True)
class DeterministicDiscrepancySnapshot:
    findings: list[dict[str, Any]]
    orders_with_diff: int
    total_diff_amount: float


@dataclass(frozen=True, slots=True)
class DeterministicHitlEvaluation:
    issue_decision: WorkflowDecision
    amount_decision: WorkflowDecision
    fail_closed_decision: WorkflowDecision
    workflow_decision: WorkflowDecision
    clarification_state: ClarificationState
    has_blocking_pending: bool


@dataclass(frozen=True, slots=True)
class MeliSuggestedAction:
    action_type: MeliActionType
    title: str
    description: str
    payload: dict[str, Any]
    economic_impact: float | None = None


@dataclass(frozen=True, slots=True)
class SimpleReconciliationFinding:
    entity_id: str
    diff: float
    money_impact: float


@dataclass(frozen=True, slots=True)
class SimpleReconciliationResult:
    findings: list[SimpleReconciliationFinding]
    total_records: int
    records_with_diff: int
    total_diff_amount: float
