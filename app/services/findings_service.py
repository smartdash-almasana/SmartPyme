from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any

from app.services.comparison_service import ComparisonResult


@dataclass(frozen=True, slots=True)
class Finding:
    finding_id: str
    entity_id_a: str
    entity_id_b: str
    entity_type: str
    metric: str
    source_a_value: Any
    source_b_value: Any
    difference: float
    difference_pct: float
    severity: str
    suggested_action: str
    traceable_origin: dict[str, Any] = field(default_factory=dict)


class FindingsService:
    def generate_findings(self, comparison_results: list[ComparisonResult]) -> list[Finding]:
        findings = []
        for result in comparison_results:
            if result.difference == 0:
                continue

            severity = self._calculate_severity(result.difference_pct)
            suggested_action = self._suggest_action(severity)
            finding_id = self._build_finding_id(result)

            findings.append(
                Finding(
                    finding_id=finding_id,
                    entity_id_a=result.entity_id_a,
                    entity_id_b=result.entity_id_b,
                    entity_type=result.entity_type,
                    metric=result.attribute,
                    source_a_value=result.value_a,
                    source_b_value=result.value_b,
                    difference=result.difference,
                    difference_pct=result.difference_pct,
                    severity=severity,
                    suggested_action=suggested_action,
                    traceable_origin={"comparison_result": asdict(result)}
                )
            )
        return findings

    def _calculate_severity(self, difference_pct: float) -> str:
        abs_diff_pct = abs(difference_pct)
        if abs_diff_pct >= 20:
            return "CRITICO"
        if 10 <= abs_diff_pct < 20:
            return "ALTO"
        if 5 <= abs_diff_pct < 10:
            return "MEDIO"
        if 0 < abs_diff_pct < 5:
            return "BAJO"
        return "INFO"

    def _suggest_action(self, severity: str) -> str:
        if severity == "CRITICO":
            return "Revisión inmediata requerida"
        if severity == "ALTO":
            return "Revisión recomendada"
        if severity == "MEDIO":
            return "Monitorear"
        return "N/A"

    def _build_finding_id(self, result: ComparisonResult) -> str:
        digest = hashlib.sha256(
            f"{result.entity_id_a}:{result.entity_id_b}:{result.attribute}".encode()
        ).hexdigest()
        return f"finding_{digest[:16]}"
