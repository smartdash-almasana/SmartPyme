from __future__ import annotations

from typing import Any

from app.services.operational_taxonomy_service import OperationalTaxonomyService


class ContextValidationService:
    def __init__(self, taxonomy_service: OperationalTaxonomyService | None = None) -> None:
        self.taxonomy_service = taxonomy_service or OperationalTaxonomyService()

    def validate(self, item_id: str, provided_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Evalúa si hay contexto suficiente para confirmar una taxonomía operativa.
        """
        item = self.taxonomy_service.get_item(item_id)
        if not item:
            return {
                "status": "UNKNOWN_TAXONOMY",
                "item_id": item_id,
                "tipo_operativo": None,
                "missing_data": [],
                "questions": [],
                "possible_pathologies": [],
                "suggested_formulas": [],
            }

        provided = provided_data or {}
        required_data = item.get("datos_minimos_a_pedir", [])
        
        missing_data = [field for field in required_data if field not in provided]
        
        if missing_data:
            status = "NEEDS_MORE_CONTEXT"
            questions = list(item.get("preguntas_al_dueno", []))
        else:
            status = "CONTEXT_READY"
            questions = []

        return {
            "status": status,
            "item_id": item["id"],
            "tipo_operativo": item["tipo_operativo"],
            "missing_data": missing_data,
            "questions": questions,
            "possible_pathologies": list(item.get("patologias_probables", [])),
            "suggested_formulas": list(item.get("formulas_utiles", [])),
        }
