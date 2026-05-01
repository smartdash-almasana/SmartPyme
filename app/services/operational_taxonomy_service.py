from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DEFAULT_TAXONOMY_PATH = (
    Path(__file__).resolve().parents[1]
    / "catalogs"
    / "taxonomia_operativa_pyme_argentina_v0.json"
)
_REQUIRED_TOP_LEVEL_FIELDS = {"catalog_id", "version", "description", "criteria", "items"}
_REQUIRED_ITEM_FIELDS = {
    "id",
    "actividad_oficial_referencia",
    "familia_smartpyme",
    "tipo_operativo",
    "derivada_operativa",
    "ejemplos_argentinos",
    "modelo_ingresos",
    "intensidad",
    "senales_anamnesis",
    "preguntas_al_dueno",
    "datos_minimos_a_pedir",
    "patologias_probables",
    "formulas_utiles",
    "buenas_practicas_asociadas",
}
_VALID_INTENSITY_VALUES = {"baja", "media", "alta"}
_VALID_CONFIDENCE_VALUES = {"baja", "media", "alta"}
_LIST_FIELDS = {
    "ejemplos_argentinos",
    "senales_anamnesis",
    "preguntas_al_dueno",
    "datos_minimos_a_pedir",
    "patologias_probables",
    "formulas_utiles",
    "buenas_practicas_asociadas",
}


class OperationalTaxonomyService:
    def __init__(self, catalog_path: str | Path | None = None) -> None:
        self.catalog_path = Path(catalog_path) if catalog_path else _DEFAULT_TAXONOMY_PATH
        self.catalog = self._load_catalog(self.catalog_path)
        self.items = tuple(self.catalog["items"])
        self._items_by_id = {item["id"]: item for item in self.items}

    def list_items(self) -> list[dict[str, Any]]:
        return list(self.items)

    def list_families(self) -> list[str]:
        return sorted({item["familia_smartpyme"] for item in self.items})

    def list_by_family(self, family: str) -> list[dict[str, Any]]:
        return [item for item in self.items if item["familia_smartpyme"] == family]

    def get_item(self, item_id: str) -> dict[str, Any] | None:
        return self._items_by_id.get(item_id)

    def get_questions(self, item_id: str) -> tuple[str, ...]:
        item = self.get_item(item_id)
        if not item:
            return ()
        return tuple(item["preguntas_al_dueno"])

    def get_minimum_data(self, item_id: str) -> tuple[str, ...]:
        item = self.get_item(item_id)
        if not item:
            return ()
        return tuple(item["datos_minimos_a_pedir"])

    def _load_catalog(self, catalog_path: Path) -> dict[str, Any]:
        if not catalog_path.exists():
            raise FileNotFoundError(f"Operational taxonomy file not found: {catalog_path}")

        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
        self._validate_catalog(raw)
        return raw

    def _validate_catalog(self, raw: dict[str, Any]) -> None:
        missing = _REQUIRED_TOP_LEVEL_FIELDS - set(raw)
        if missing:
            raise ValueError(f"Operational taxonomy missing fields: {sorted(missing)}")
        if raw["catalog_id"] != "taxonomia_operativa_pyme_argentina_v0":
            raise ValueError("Unexpected operational taxonomy catalog_id")
        if not isinstance(raw["items"], list) or not raw["items"]:
            raise ValueError("Operational taxonomy items must be a non-empty list")

        seen_ids: set[str] = set()
        for item in raw["items"]:
            self._validate_item(item)
            if item["id"] in seen_ids:
                raise ValueError(f"Duplicated operational taxonomy item id: {item['id']}")
            seen_ids.add(item["id"])

    def _validate_item(self, item: dict[str, Any]) -> None:
        missing = _REQUIRED_ITEM_FIELDS - set(item)
        if missing:
            raise ValueError(f"Operational taxonomy item missing fields: {sorted(missing)}")

        for field in _LIST_FIELDS:
            if not isinstance(item[field], list) or not item[field]:
                raise ValueError(f"Operational taxonomy field must be a non-empty list: {field}")

        intensity = item["intensidad"]
        if set(intensity) != {"stock", "personal", "tiempo", "documentacion"}:
            raise ValueError("Operational taxonomy intensity has invalid keys")
        invalid_intensity_values = set(intensity.values()) - _VALID_INTENSITY_VALUES
        if invalid_intensity_values:
            raise ValueError(
                "Operational taxonomy intensity has invalid values: "
                f"{sorted(invalid_intensity_values)}"
            )

        official_reference = item["actividad_oficial_referencia"]
        confidence = official_reference.get("confianza_mapeo_oficial")
        if confidence not in _VALID_CONFIDENCE_VALUES:
            raise ValueError("Invalid official mapping confidence")
        if official_reference.get("validacion_requerida") is not True:
            raise ValueError("Operational taxonomy official reference must require validation")
