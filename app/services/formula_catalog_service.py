from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.contracts.catalog_contract import FormulaCatalog, FormulaCatalogItem, FormulaVariable

_DEFAULT_FORMULA_CATALOG_PATH = (
    Path(__file__).resolve().parents[1] / "catalogs" / "formulas_smartpyme_v0.json"
)
_REQUIRED_TOP_LEVEL_FIELDS = {"catalog_id", "version", "description", "criteria", "items"}
_REQUIRED_ITEM_FIELDS = {
    "id",
    "nombre",
    "dominio",
    "descripcion_operativa",
    "formula",
    "variables_requeridas",
    "datos_minimos_a_pedir",
    "sirve_para_detectar",
    "patologias_asociadas",
    "tipos_de_negocio_aplicables",
    "frecuencia_recomendada",
    "salida_esperada",
    "accion_sugerida_si_alerta",
    "criticidad",
    "complejidad",
}
_REQUIRED_VARIABLE_FIELDS = {"nombre", "descripcion", "tipo"}
_LIST_FIELDS = {
    "variables_requeridas",
    "datos_minimos_a_pedir",
    "sirve_para_detectar",
    "patologias_asociadas",
    "tipos_de_negocio_aplicables",
}


class FormulaCatalogService:
    def __init__(self, catalog_path: str | Path | None = None) -> None:
        self.catalog_path = Path(catalog_path) if catalog_path else _DEFAULT_FORMULA_CATALOG_PATH
        self.catalog = self._load_catalog(self.catalog_path)
        self._items_by_id = {item.id: item for item in self.catalog.items}

    def list_domains(self) -> list[str]:
        return sorted({item.dominio for item in self.catalog.items})

    def list_items(self) -> list[FormulaCatalogItem]:
        return list(self.catalog.items)

    def list_by_domain(self, domain: str) -> list[FormulaCatalogItem]:
        return [item for item in self.catalog.items if item.dominio == domain]

    def list_by_pathology(self, pathology_id: str) -> list[FormulaCatalogItem]:
        return [
            item
            for item in self.catalog.items
            if pathology_id in item.patologias_asociadas
        ]

    def list_by_criticality(self, criticality: str) -> list[FormulaCatalogItem]:
        return [item for item in self.catalog.items if item.criticidad == criticality]

    def get_item(self, item_id: str) -> FormulaCatalogItem | None:
        return self._items_by_id.get(item_id)

    def get_minimum_data(self, item_id: str) -> tuple[str, ...]:
        item = self.get_item(item_id)
        return item.datos_minimos_a_pedir if item else ()

    def get_pathologies(self, item_id: str) -> tuple[str, ...]:
        item = self.get_item(item_id)
        return item.patologias_asociadas if item else ()

    def _load_catalog(self, catalog_path: Path) -> FormulaCatalog:
        if not catalog_path.exists():
            raise FileNotFoundError(f"Formula catalog file not found: {catalog_path}")

        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
        self._validate_catalog_payload(raw)

        return FormulaCatalog(
            catalog_id=raw["catalog_id"],
            version=raw["version"],
            description=raw["description"],
            criteria=raw["criteria"],
            items=tuple(self._build_item(item) for item in raw["items"]),
        )

    def _validate_catalog_payload(self, raw: dict[str, Any]) -> None:
        missing = _REQUIRED_TOP_LEVEL_FIELDS - set(raw)
        if missing:
            raise ValueError(f"Formula catalog missing required fields: {sorted(missing)}")
        if not isinstance(raw["items"], list) or not raw["items"]:
            raise ValueError("Formula catalog items must be a non-empty list")

        seen_ids: set[str] = set()
        for item in raw["items"]:
            self._validate_item_payload(item)
            if item["id"] in seen_ids:
                raise ValueError(f"Duplicated formula catalog item id: {item['id']}")
            seen_ids.add(item["id"])

    def _validate_item_payload(self, item: dict[str, Any]) -> None:
        missing = _REQUIRED_ITEM_FIELDS - set(item)
        if missing:
            raise ValueError(f"Formula catalog item missing required fields: {sorted(missing)}")
        for field in _LIST_FIELDS:
            if not isinstance(item[field], list) or not item[field]:
                raise ValueError(f"Formula catalog item field must be a non-empty list: {field}")
        for variable in item["variables_requeridas"]:
            missing_variable_fields = _REQUIRED_VARIABLE_FIELDS - set(variable)
            if missing_variable_fields:
                raise ValueError(
                    "Formula variable missing required fields: "
                    f"{sorted(missing_variable_fields)}"
                )

    def _build_item(self, item: dict[str, Any]) -> FormulaCatalogItem:
        return FormulaCatalogItem(
            id=item["id"],
            nombre=item["nombre"],
            dominio=item["dominio"],
            descripcion_operativa=item["descripcion_operativa"],
            formula=item["formula"],
            variables_requeridas=tuple(
                FormulaVariable(
                    nombre=variable["nombre"],
                    descripcion=variable["descripcion"],
                    tipo=variable["tipo"],
                )
                for variable in item["variables_requeridas"]
            ),
            datos_minimos_a_pedir=tuple(item["datos_minimos_a_pedir"]),
            sirve_para_detectar=tuple(item["sirve_para_detectar"]),
            patologias_asociadas=tuple(item["patologias_asociadas"]),
            tipos_de_negocio_aplicables=tuple(item["tipos_de_negocio_aplicables"]),
            frecuencia_recomendada=item["frecuencia_recomendada"],
            salida_esperada=item["salida_esperada"],
            accion_sugerida_si_alerta=item["accion_sugerida_si_alerta"],
            criticidad=item["criticidad"],
            complejidad=item["complejidad"],
        )
