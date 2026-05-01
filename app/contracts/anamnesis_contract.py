from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DeclaredBusinessContext:
    cliente_id: str
    rubro_declarado: str | None = None
    tipo_operativo_probable: str | None = None
    empleados_declarados: int | None = None
    canales_venta: tuple[str, ...] = field(default_factory=tuple)
    fuentes_datos: tuple[str, ...] = field(default_factory=tuple)
    dolores_declarados: tuple[str, ...] = field(default_factory=tuple)
    preguntas_pendientes: tuple[str, ...] = field(default_factory=tuple)
    taxonomia_candidata_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class AnamnesisInput:
    cliente_id: str
    owner_message: str
    current_context: DeclaredBusinessContext | None = None


@dataclass(frozen=True, slots=True)
class AnamnesisResult:
    cliente_id: str
    context: DeclaredBusinessContext
    extracted_fields: tuple[str, ...]
    status: str
