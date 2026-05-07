"""Contratos tipados del Laboratorio de Análisis PyME MVP.

Patrón tenant-first: cliente_id es el primer campo en todos los contratos
de nivel de caso, alineado con app/contracts/operational_case.py y
app/contracts/evidence_contract.py.

Alineación con identificadores core de SmartPyme:
- job_id: enlace opcional al job que originó el caso/hallazgo
- decision_id: enlace opcional a la decisión asociada
- user_id: enlace opcional al usuario que inició el flujo

Estos campos son opcionales (None por defecto) para no romper el scaffold
existente. LaboratorioReportDraft es un objeto transiente — no es un modelo
de persistencia.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app.laboratorio_pyme.tipos import TipoLaboratorio

_PRIORIDADES_VALIDAS = frozenset({"alta", "media", "baja"})
_ESTADOS_BORRADOR_VALIDOS = frozenset({"pendiente_revision", "finalizado"})


def _require_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")


@dataclass(frozen=True, slots=True)
class LaboratorioPymeCase:
    """Caso diagnóstico abierto para un dueño de PyME.

    cliente_id es el primer campo — patrón tenant-first obligatorio.
    job_id y user_id son enlaces opcionales a entidades core de SmartPyme.
    """

    cliente_id: str
    case_id: str
    dueno_nombre: str
    laboratorios: list[TipoLaboratorio]
    estado: str
    creado_en: str
    job_id: str | None = field(default=None)
    user_id: str | None = field(default=None)

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.case_id, "case_id")
        _require_non_empty(self.dueno_nombre, "dueno_nombre")
        if not self.laboratorios:
            raise ValueError("laboratorios: se requiere al menos un laboratorio")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LaboratorioSelection:
    """Selección formal de laboratorios para un caso.

    cliente_id es el primer campo — patrón tenant-first obligatorio.
    job_id es enlace opcional al job que originó la selección.
    """

    cliente_id: str
    case_id: str
    laboratorios_seleccionados: list[TipoLaboratorio]
    job_id: str | None = field(default=None)

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.case_id, "case_id")
        if not self.laboratorios_seleccionados:
            raise ValueError("laboratorios_seleccionados: la selección no puede estar vacía")


@dataclass(frozen=True, slots=True)
class EvidenceRequirement:
    """Requerimiento de evidencia para un laboratorio en un caso.

    cliente_id es el primer campo — patrón tenant-first obligatorio.
    job_id es enlace opcional al job que generó el requerimiento.
    """

    cliente_id: str
    case_id: str
    laboratorio: TipoLaboratorio
    descripcion: str
    obligatorio: bool
    job_id: str | None = field(default=None)

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.case_id, "case_id")
        _require_non_empty(self.descripcion, "descripcion")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DiagnosticFinding:
    """Hallazgo accionable producido por un laboratorio.

    cliente_id es el primer campo — patrón tenant-first obligatorio.
    job_id y decision_id son enlaces opcionales a entidades core de SmartPyme.
    """

    cliente_id: str
    finding_id: str
    case_id: str
    laboratorio: TipoLaboratorio
    hallazgo: str
    prioridad: str
    impacto_estimado: str
    job_id: str | None = field(default=None)
    decision_id: str | None = field(default=None)

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.finding_id, "finding_id")
        _require_non_empty(self.case_id, "case_id")
        _require_non_empty(self.hallazgo, "hallazgo")
        _require_non_empty(self.impacto_estimado, "impacto_estimado")
        if self.prioridad not in _PRIORIDADES_VALIDAS:
            raise ValueError(
                f"prioridad inválida: '{self.prioridad}'. "
                f"Valores permitidos: {sorted(_PRIORIDADES_VALIDAS)}"
            )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LaboratorioReportDraft:
    """Borrador de informe que agrega hallazgos de todos los laboratorios.

    Objeto transiente — NO es un modelo de persistencia.
    cliente_id es el primer campo — patrón tenant-first obligatorio.
    job_id, decision_id y user_id son enlaces opcionales a entidades core.
    """

    cliente_id: str
    report_id: str
    case_id: str
    hallazgos: list[DiagnosticFinding]
    estado_borrador: str
    generado_en: str
    job_id: str | None = field(default=None)
    decision_id: str | None = field(default=None)
    user_id: str | None = field(default=None)

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.report_id, "report_id")
        _require_non_empty(self.case_id, "case_id")
        if self.estado_borrador not in _ESTADOS_BORRADOR_VALIDOS:
            raise ValueError(
                f"estado_borrador inválido: '{self.estado_borrador}'. "
                f"Valores permitidos: {sorted(_ESTADOS_BORRADOR_VALIDOS)}"
            )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
