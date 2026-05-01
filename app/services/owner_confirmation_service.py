from __future__ import annotations

from typing import Any

from app.services.context_validation_service import ContextValidationService
from app.services.operational_taxonomy_service import OperationalTaxonomyService


class OwnerConfirmationService:
    def __init__(
        self,
        taxonomy_service: OperationalTaxonomyService | None = None,
        validation_service: ContextValidationService | None = None,
    ) -> None:
        self.taxonomy_service = taxonomy_service or OperationalTaxonomyService()
        self.validation_service = validation_service or ContextValidationService(
            taxonomy_service=self.taxonomy_service
        )

    def build_confirmation(
        self, candidate_ids: tuple[str, ...], provided_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Prepara una propuesta de confirmación para el dueño a partir de candidatos taxonómicos.
        """
        if not candidate_ids:
            return {"status": "NO_CANDIDATES", "candidates": []}

        candidates = []
        for item_id in candidate_ids:
            item = self.taxonomy_service.get_item(item_id)
            if not item:
                continue

            validation = self.validation_service.validate(item_id, provided_data)
            
            candidates.append({
                "item_id": item["id"],
                "tipo_operativo": item["tipo_operativo"],
                "familia_smartpyme": item["familia_smartpyme"],
                "confirmation_question": f"¿Tu negocio se parece más a: {item['tipo_operativo']}?",
                "missing_data": validation["missing_data"],
                "required_questions": validation["questions"],
                "possible_pathologies": validation["possible_pathologies"],
                "suggested_formulas": validation["suggested_formulas"],
            })

        if not candidates:
            return {"status": "NO_VALID_CANDIDATES", "candidates": []}

        return {
            "status": "OWNER_CONFIRMATION_REQUIRED",
            "candidates": candidates,
        }
