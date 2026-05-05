"""
CaseOpeningService — Capa 03: Apertura del Caso Operativo
TS_030_002_SERVICIO_APERTURA_CASO

Servicio mínimo y determinístico que evalúa un OperationalCaseCandidate
de Capa 02 y produce un OperationalCase v2 con el estado correcto.

Reglas:
  - Sin IA ni modelos de lenguaje.
  - Sin diagnóstico.
  - Sin acciones.
  - Evaluación por reglas determinísticas sobre el candidato.
  - No toca contratos legacy.

Lógica de evaluación (en orden de prioridad):

  1. REJECTED_OUT_OF_SCOPE
     → primary_pathology vacía.
     → status BLOCKED_MISSING_VARIABLES + brechas CRITICAL sin required_source.

  2. INSUFFICIENT_EVIDENCE
     → Sin available_variables Y sin brechas HIGH/CRITICAL con required_source.

  3. CLARIFICATION_REQUIRED
     → status PENDING_OWNER_VALIDATION.
     → O brechas HIGH con required_source conocida.

  4. READY_FOR_INVESTIGATION (default)
     → Hay available_variables, hipótesis válida, sin brechas CRITICAL sin fuente.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.contracts.investigation_contract import EvidenceGap, OperationalCaseCandidate
from app.contracts.operational_case_v2_contract import OperationalCase

_CRITICAL: frozenset[str] = frozenset(["CRITICAL"])
_HIGH_OR_CRITICAL: frozenset[str] = frozenset(["HIGH", "CRITICAL"])


def _critical_gaps_without_source(gaps: list[EvidenceGap]) -> list[EvidenceGap]:
    return [g for g in gaps if g.priority in _CRITICAL and not g.required_source]


def _high_gaps_with_source(gaps: list[EvidenceGap]) -> list[EvidenceGap]:
    return [g for g in gaps if g.priority in _HIGH_OR_CRITICAL and g.required_source]


class CaseOpeningService:
    """
    Evalúa un OperationalCaseCandidate y produce un OperationalCase v2.

    Uso:
        service = CaseOpeningService()
        case = service.evaluate(candidate)
    """

    def evaluate(
        self,
        candidate: OperationalCaseCandidate,
        case_id: Optional[str] = None,
    ) -> OperationalCase:
        resolved_id = case_id or str(uuid.uuid4())
        opened_at = datetime.now(timezone.utc)

        # Campos comunes a todos los estados
        base = dict(
            case_id=resolved_id,
            cliente_id=candidate.cliente_id,
            candidate_id=candidate.candidate_id,
            source_admission_case_id=candidate.source_admission_case_id,
            source_normalized_package_id=candidate.source_normalized_package_id,
            primary_pathology=candidate.primary_pathology or "UNKNOWN",
            hypothesis=candidate.hypothesis,
            opened_at=opened_at,
        )

        # ------------------------------------------------------------------
        # 1. REJECTED_OUT_OF_SCOPE
        # ------------------------------------------------------------------
        if not candidate.primary_pathology or not candidate.primary_pathology.strip():
            return OperationalCase(
                case_id=resolved_id,
                cliente_id=candidate.cliente_id,
                candidate_id=candidate.candidate_id,
                source_admission_case_id=candidate.source_admission_case_id,
                source_normalized_package_id=candidate.source_normalized_package_id,
                primary_pathology="UNKNOWN",
                hypothesis=candidate.hypothesis,
                opened_at=opened_at,
                status="REJECTED_OUT_OF_SCOPE",
                rejection_reason="El candidato no tiene patología principal identificada.",
                next_step=(
                    "Caso rechazado por falta de patología principal. "
                    "Volver a Capa 02 para reconstruir el candidato."
                ),
            )

        critical_no_src = _critical_gaps_without_source(candidate.evidence_gaps)
        if candidate.status == "BLOCKED_MISSING_VARIABLES" and critical_no_src:
            names = ", ".join(g.variable_canonical_name for g in critical_no_src[:3])
            return OperationalCase(
                **base,
                status="REJECTED_OUT_OF_SCOPE",
                rejection_reason=(
                    f"Brechas críticas sin fuente conocida: {names}. "
                    f"No hay forma de obtener la evidencia necesaria."
                ),
                next_step=(
                    "Caso rechazado. Informar al dueño que el caso no puede "
                    "investigarse con la evidencia disponible."
                ),
            )

        # ------------------------------------------------------------------
        # 2. INSUFFICIENT_EVIDENCE
        # ------------------------------------------------------------------
        has_available = len(candidate.available_variables) > 0
        high_with_src = _high_gaps_with_source(candidate.evidence_gaps)

        if not has_available and not high_with_src:
            all_critical = [g for g in candidate.evidence_gaps if g.priority in _CRITICAL]
            if all_critical:
                names = ", ".join(g.variable_canonical_name for g in all_critical[:3])
                reason = (
                    f"Variables críticas sin evidencia trazable: {names}. "
                    f"Sin estas variables no es posible investigar "
                    f"'{candidate.primary_pathology}'."
                )
            else:
                reason = (
                    f"No hay variables disponibles con evidencia trazable para "
                    f"investigar '{candidate.primary_pathology}'."
                )
            return OperationalCase(
                **base,
                status="INSUFFICIENT_EVIDENCE",
                insufficiency_reason=reason,
                next_step=(
                    "Volver a Capa 1.5 para obtener nueva evidencia. "
                    "Sin variables disponibles no es posible iniciar la investigación."
                ),
            )

        # ------------------------------------------------------------------
        # 3. CLARIFICATION_REQUIRED
        # ------------------------------------------------------------------
        if candidate.status == "PENDING_OWNER_VALIDATION" or high_with_src:
            if high_with_src:
                gap = high_with_src[0]
                question = (
                    f"Para investigar '{candidate.primary_pathology}' necesito "
                    f"'{gap.variable_canonical_name}'. "
                    f"Fuente sugerida: {gap.required_source}. "
                    f"¿Podés conseguirla?"
                )
            else:
                question = (
                    f"Para avanzar con la investigación de '{candidate.primary_pathology}' "
                    f"necesito que confirmes el alcance. ¿Querés continuar?"
                )
            return OperationalCase(
                **base,
                status="CLARIFICATION_REQUIRED",
                clarification_question=question,
                next_step="Esperar respuesta del dueño antes de iniciar la investigación.",
            )

        # ------------------------------------------------------------------
        # 4. READY_FOR_INVESTIGATION
        # ------------------------------------------------------------------
        return OperationalCase(
            **base,
            status="READY_FOR_INVESTIGATION",
            next_step=(
                f"Capa 04+: iniciar investigación formal sobre "
                f"'{candidate.primary_pathology}'."
            ),
        )
