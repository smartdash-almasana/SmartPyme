from __future__ import annotations

from typing import Any

from app.catalogs.operational_conditions_catalog import OPERATIONAL_CONDITIONS_CATALOG
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

    def validate_operational_conditions(
        self,
        skill_id: str,
        variables: dict[str, Any] | None = None,
        evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Valida las condiciones operativas determinísticas para una skill específica.
        """
        conditions = OPERATIONAL_CONDITIONS_CATALOG.get(skill_id)
        if not conditions:
            return {
                "status": "UNKNOWN_SKILL",
                "skill_id": skill_id,
                "missing_variables": [],
                "missing_evidence": [],
            }

        vars_provided = variables or {}
        ev_provided = evidence or []

        if not isinstance(vars_provided, dict) or not isinstance(ev_provided, list):
            return {
                "status": "CONDITIONS_INVALID",
                "skill_id": skill_id,
                "reason": "INVALID_INPUT_TYPES",
            }

        missing_vars = [v for v in conditions.required_variables if v not in vars_provided]
        missing_ev = [e for e in conditions.required_evidence if e not in ev_provided]

        if missing_vars or missing_ev:
            return {
                "status": "CONDITIONS_MISSING",
                "skill_id": skill_id,
                "missing_variables": missing_vars,
                "missing_evidence": missing_ev,
            }

        return {
            "status": "CONDITIONS_OK",
            "skill_id": skill_id,
        }
