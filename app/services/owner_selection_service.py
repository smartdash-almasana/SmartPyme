from __future__ import annotations

from typing import Any

from app.services.operational_taxonomy_service import OperationalTaxonomyService


class OwnerSelectionService:
    def __init__(self, taxonomy_service: OperationalTaxonomyService | None = None) -> None:
        self.taxonomy_service = taxonomy_service or OperationalTaxonomyService()

    def confirm_selection(
        self, candidate_ids: tuple[str, ...], selected_item_id: str
    ) -> dict[str, Any]:
        """
        Registra la selección explícita del dueño sobre una taxonomía candidata.
        """
        item = self.taxonomy_service.get_item(selected_item_id)
        if not item:
            return {"status": "UNKNOWN_SELECTION"}

        if selected_item_id not in candidate_ids:
            return {"status": "SELECTION_NOT_IN_CANDIDATES"}

        return {
            "status": "SELECTION_CONFIRMED",
            "item_id": item["id"],
            "tipo_operativo_confirmado": item["tipo_operativo"],
            "familia_smartpyme": item["familia_smartpyme"],
            "required_data": list(item.get("datos_minimos_a_pedir", [])),
            "possible_pathologies": list(item.get("patologias_probables", [])),
            "suggested_formulas": list(item.get("formulas_utiles", [])),
        }
