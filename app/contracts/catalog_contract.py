from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CatalogItem:
    id: str
    domain: str
    name: str
    description: str
    symptoms: tuple[str, ...]
    anamnesis_signals: tuple[str, ...]
    minimum_data: tuple[str, ...]
    associated_formulas: tuple[str, ...]
    impact: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Catalog:
    catalog_id: str
    version: str
    description: str
    criteria: str
    items: tuple[CatalogItem, ...]


@dataclass(frozen=True, slots=True)
class FormulaVariable:
    nombre: str
    descripcion: str
    tipo: str


@dataclass(frozen=True, slots=True)
class FormulaCatalogItem:
    id: str
    nombre: str
    dominio: str
    descripcion_operativa: str
    formula: str
    variables_requeridas: tuple[FormulaVariable, ...]
    datos_minimos_a_pedir: tuple[str, ...]
    sirve_para_detectar: tuple[str, ...]
    patologias_asociadas: tuple[str, ...]
    tipos_de_negocio_aplicables: tuple[str, ...]
    frecuencia_recomendada: str
    salida_esperada: str
    accion_sugerida_si_alerta: str
    criticidad: str
    complejidad: str


@dataclass(frozen=True, slots=True)
class FormulaCatalog:
    catalog_id: str
    version: str
    description: str
    criteria: str
    items: tuple[FormulaCatalogItem, ...]
