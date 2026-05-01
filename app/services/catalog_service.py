from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.contracts.catalog_contract import Catalog, CatalogItem

_DEFAULT_CATALOG_PATH = (
    Path(__file__).resolve().parents[1] / "catalogs" / "patologias_pyme_v0.json"
)
_REQUIRED_TOP_LEVEL_FIELDS = {"catalog_id", "version", "description", "criteria", "items"}
_REQUIRED_ITEM_FIELDS = {
    "id",
    "domain",
    "name",
    "description",
    "symptoms",
    "anamnesis_signals",
    "minimum_data",
    "associated_formulas",
    "impact",
}
_LIST_FIELDS = {
    "symptoms",
    "anamnesis_signals",
    "minimum_data",
    "associated_formulas",
    "impact",
}


class CatalogService:
    def __init__(self, catalog_path: str | Path | None = None) -> None:
        self.catalog_path = Path(catalog_path) if catalog_path else _DEFAULT_CATALOG_PATH
        self.catalog = self._load_catalog(self.catalog_path)
        self._items_by_id = {item.id: item for item in self.catalog.items}

    def list_domains(self) -> list[str]:
        return sorted({item.domain for item in self.catalog.items})

    def list_items(self) -> list[CatalogItem]:
        return list(self.catalog.items)

    def list_by_domain(self, domain: str) -> list[CatalogItem]:
        return [item for item in self.catalog.items if item.domain == domain]

    def get_item(self, item_id: str) -> CatalogItem | None:
        return self._items_by_id.get(item_id)

    def get_minimum_data(self, item_id: str) -> tuple[str, ...]:
        item = self.get_item(item_id)
        return item.minimum_data if item else ()

    def get_associated_formulas(self, item_id: str) -> tuple[str, ...]:
        item = self.get_item(item_id)
        return item.associated_formulas if item else ()

    def _load_catalog(self, catalog_path: Path) -> Catalog:
        if not catalog_path.exists():
            raise FileNotFoundError(f"Catalog file not found: {catalog_path}")

        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
        self._validate_catalog_payload(raw)

        return Catalog(
            catalog_id=raw["catalog_id"],
            version=raw["version"],
            description=raw["description"],
            criteria=raw["criteria"],
            items=tuple(self._build_item(item) for item in raw["items"]),
        )

    def _validate_catalog_payload(self, raw: dict[str, Any]) -> None:
        missing = _REQUIRED_TOP_LEVEL_FIELDS - set(raw)
        if missing:
            raise ValueError(f"Catalog missing required fields: {sorted(missing)}")
        if not isinstance(raw["items"], list) or not raw["items"]:
            raise ValueError("Catalog items must be a non-empty list")

        seen_ids: set[str] = set()
        for item in raw["items"]:
            self._validate_item_payload(item)
            if item["id"] in seen_ids:
                raise ValueError(f"Duplicated catalog item id: {item['id']}")
            seen_ids.add(item["id"])

    def _validate_item_payload(self, item: dict[str, Any]) -> None:
        missing = _REQUIRED_ITEM_FIELDS - set(item)
        if missing:
            raise ValueError(f"Catalog item missing required fields: {sorted(missing)}")
        for field in _LIST_FIELDS:
            if not isinstance(item[field], list) or not item[field]:
                raise ValueError(f"Catalog item field must be a non-empty list: {field}")

    def _build_item(self, item: dict[str, Any]) -> CatalogItem:
        return CatalogItem(
            id=item["id"],
            domain=item["domain"],
            name=item["name"],
            description=item["description"],
            symptoms=tuple(item["symptoms"]),
            anamnesis_signals=tuple(item["anamnesis_signals"]),
            minimum_data=tuple(item["minimum_data"]),
            associated_formulas=tuple(item["associated_formulas"]),
            impact=tuple(item["impact"]),
        )
