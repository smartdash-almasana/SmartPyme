"""
Contratos Pydantic — Capa 03: Apertura del Caso Operativo
TS_030_001_CONTRATO_OPERATIONAL_CASE_V2

OperationalCase v2: contrato Pydantic aislado con los 4 estados de Capa 03.

Principios:
  - Capa 03 no diagnostica.
  - Capa 03 determina si existe un caso investigable.
  - La única salida de Capa 03 es OperationalCase.
  - Cada estado exige su campo de razón/pregunta correspondiente.

Relación con contratos existentes:
  - NO reemplaza operational_case.py ni operational_case_contract.py (legacy).
  - Recibe OperationalCaseCandidate de Capa 02 (investigation_contract.py).
  - Es la entrada para Capa 04+ (investigación, diagnóstico, hallazgos).

Documento rector:
  docs/product/SMARTPYME_CAPA_03_DIAGNOSTICO_VALIDACION_OPERATIVA.md
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Tipos literales
# ---------------------------------------------------------------------------

OperationalCaseStatus = Literal[
    "READY_FOR_INVESTIGATION",
    "CLARIFICATION_REQUIRED",
    "INSUFFICIENT_EVIDENCE",
    "REJECTED_OUT_OF_SCOPE",
]
"""
Estado del OperationalCase producido por Capa 03.

READY_FOR_INVESTIGATION
  → El caso tiene suficiencia mínima, está dentro del alcance y no requiere
    aclaración previa. Capa 04+ puede iniciar la investigación formal.

CLARIFICATION_REQUIRED
  → El caso tiene potencial investigable pero necesita que el dueño confirme
    o aporte algo antes de continuar. Requiere clarification_question.

INSUFFICIENT_EVIDENCE
  → El caso no tiene suficiencia mínima para investigar y las brechas no
    pueden resolverse con una acción simple del dueño. Requiere
    insufficiency_reason.

REJECTED_OUT_OF_SCOPE
  → El caso no corresponde al alcance operativo de SmartPyme o duplica un
    caso ya abierto. Requiere rejection_reason.
"""


# ---------------------------------------------------------------------------
# OperationalCase v2
# ---------------------------------------------------------------------------


class OperationalCase(BaseModel):
    """
    Output exclusivo de Capa 03: Apertura del Caso Operativo.

    Determina si el OperationalCaseCandidate de Capa 02 tiene suficiencia
    para convertirse en un caso investigable formal.

    NO es un diagnóstico.
    NO contiene DiagnosticReport ni FindingRecord.
    NO ejecuta acciones.

    Validaciones cruzadas por estado:
      CLARIFICATION_REQUIRED  → clarification_question obligatorio
      INSUFFICIENT_EVIDENCE   → insufficiency_reason obligatorio
      REJECTED_OUT_OF_SCOPE   → rejection_reason obligatorio
    """

    case_id: str = Field(
        ..., description="UUID único del caso operativo."
    )
    cliente_id: str = Field(
        ..., description="Tenant al que pertenece el caso."
    )
    candidate_id: Optional[str] = Field(
        default=None,
        description=(
            "ID del OperationalCaseCandidate de Capa 02 que originó este caso. "
            "Permite trazabilidad hacia atrás."
        ),
    )
    source_admission_case_id: Optional[str] = Field(
        default=None,
        description="ID del InitialCaseAdmission de origen.",
    )
    source_normalized_package_id: Optional[str] = Field(
        default=None,
        description="ID del NormalizedEvidencePackage de origen.",
    )
    primary_pathology: str = Field(
        ...,
        description="Patología principal candidata a investigar (no confirmada).",
    )
    hypothesis: str = Field(
        ...,
        description=(
            "Hipótesis investigable heredada del OperationalCaseCandidate. "
            "No afirma: investiga."
        ),
    )
    status: OperationalCaseStatus = Field(
        ...,
        description=(
            "Estado del caso: "
            "READY_FOR_INVESTIGATION | CLARIFICATION_REQUIRED | "
            "INSUFFICIENT_EVIDENCE | REJECTED_OUT_OF_SCOPE."
        ),
    )
    clarification_question: Optional[str] = Field(
        default=None,
        description=(
            "Pregunta mayéutica concreta para el dueño. "
            "Obligatorio si status=CLARIFICATION_REQUIRED."
        ),
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        description=(
            "Razón explícita del rechazo. "
            "Obligatorio si status=REJECTED_OUT_OF_SCOPE."
        ),
    )
    insufficiency_reason: Optional[str] = Field(
        default=None,
        description=(
            "Razón técnica de la insuficiencia de evidencia. "
            "Obligatorio si status=INSUFFICIENT_EVIDENCE."
        ),
    )
    opened_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp de apertura del caso.",
    )
    next_step: str = Field(
        ...,
        description=(
            "Instrucción para Capa 04+ o para el dueño según el estado del caso."
        ),
    )

    # -----------------------------------------------------------------------
    # Validaciones de campos individuales
    # -----------------------------------------------------------------------

    @field_validator("case_id", "cliente_id", "primary_pathology", "next_step")
    @classmethod
    def required_strings_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(f"El campo no puede estar vacío.")
        return v

    @field_validator("hypothesis")
    @classmethod
    def hypothesis_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("hypothesis no puede estar vacía.")
        return v

    # -----------------------------------------------------------------------
    # Validaciones cruzadas por estado
    # -----------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_status_requires_reason(self) -> "OperationalCase":
        """
        Cada estado exige su campo de razón/pregunta correspondiente.

        CLARIFICATION_REQUIRED  → clarification_question obligatorio
        INSUFFICIENT_EVIDENCE   → insufficiency_reason obligatorio
        REJECTED_OUT_OF_SCOPE   → rejection_reason obligatorio
        READY_FOR_INVESTIGATION → ningún campo de razón requerido
        """
        if self.status == "CLARIFICATION_REQUIRED":
            if not self.clarification_question or not self.clarification_question.strip():
                raise ValueError(
                    "clarification_question es obligatorio cuando "
                    "status=CLARIFICATION_REQUIRED."
                )

        if self.status == "INSUFFICIENT_EVIDENCE":
            if not self.insufficiency_reason or not self.insufficiency_reason.strip():
                raise ValueError(
                    "insufficiency_reason es obligatorio cuando "
                    "status=INSUFFICIENT_EVIDENCE."
                )

        if self.status == "REJECTED_OUT_OF_SCOPE":
            if not self.rejection_reason or not self.rejection_reason.strip():
                raise ValueError(
                    "rejection_reason es obligatorio cuando "
                    "status=REJECTED_OUT_OF_SCOPE."
                )

        return self
