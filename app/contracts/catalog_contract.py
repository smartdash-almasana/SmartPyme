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
