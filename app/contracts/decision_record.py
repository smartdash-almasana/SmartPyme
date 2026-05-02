from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    decision_id: str
    cliente_id: str
    timestamp: str
    tipo_decision: Literal["INFORMAR", "EJECUTAR", "RECHAZAR"]
    mensaje_original: str
    propuesta: dict[str, Any]
    accion: str
    overrides: dict[str, Any] | None = None
    job_id: str | None = None
