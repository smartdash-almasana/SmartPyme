from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, TypedDict

FindingSeverity: TypeAlias = Literal["info", "warning", "critical"]
FindingType: TypeAlias = Literal["mismatch_valor", "faltante_en_fuente", "incertidumbre"]
FindingStatus: TypeAlias = Literal["pending", "in_progress", "done", "blocked"]

class MismatchEvidence(TypedDict):
    field: str
    value_a: Any
    value_b: Any
    delta: float | None

class MissingEvidence(TypedDict):
    missing_in: Literal["source_a", "source_b"]
    data: dict[str, Any]

class UncertaintyEvidence(TypedDict):
    reason: str
    raw_value: Any

@dataclass(frozen=True, slots=True)
class Hallazgo:
    id: str  # SHA-256 de dedupe_key
    tipo: FindingType
    severidad: FindingSeverity
    entidad_id: str
    entidad_tipo: str
    diferencia_cuantificada: float | str | None
    evidencia: MismatchEvidence | MissingEvidence | UncertaintyEvidence
    dedupe_key: str
    status: FindingStatus = "pending"
