from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OwnerMessageInterpretation(BaseModel):
    """Validated soft interpretation of an owner message.

    This is not a decision, diagnosis, finding, or persisted business fact.
    """

    model_config = ConfigDict(extra="forbid")

    intent: str | None = None
    entities: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    doubts: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    symptom_id: str | None = None

    rubro_posible: str | None = None
    dolores_detectados: tuple[str, ...] = ()
    fuentes_mencionadas: tuple[str, ...] = ()
    datos_mencionados: tuple[str, ...] = ()
    hipotesis_sistema: tuple[str, ...] = ()
    preguntas_sugeridas: tuple[str, ...] = ()
    nivel_confianza: float = Field(default=0.0, ge=0.0, le=1.0)
    necesita_confirmacion: bool = True
