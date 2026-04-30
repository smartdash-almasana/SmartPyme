from app.catalog.pathologies import get_pathology_definition, get_pathology_metadata
from app.contracts.formula_contract import FormulaStatus
from app.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologyFinding,
    PathologyStatus,
)
from app.services.pathology_evaluators import get_pathology_evaluator


class PathologyEngineService:
    def evaluate(self, pathology_id: str, payload: PathologyEvaluationInput) -> PathologyFinding:
        definition = get_pathology_definition(pathology_id)
        if definition is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=payload.formula_result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=payload.formula_result.source_refs,
                explanation="Patología no soportada por el catálogo.",
                metadata={"blocking_reason": "PATHOLOGY_NOT_SUPPORTED"},
            )

        result = payload.formula_result
        catalog_metadata = get_pathology_metadata(pathology_id)

        if result.status == FormulaStatus.BLOCKED:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="No se puede evaluar la patología porque la fórmula está bloqueada.",
                metadata={"blocking_reason": result.blocking_reason, "catalog": catalog_metadata},
            )

        if result.formula_id != definition.formula_id:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="La fórmula calculada no coincide con la patología solicitada.",
                metadata={"expected_formula_id": definition.formula_id, "catalog": catalog_metadata},
            )

        evaluator = get_pathology_evaluator(pathology_id)
        if evaluator is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="Patología sin evaluador implementado.",
                metadata={"blocking_reason": "PATHOLOGY_NOT_IMPLEMENTED", "catalog": catalog_metadata},
            )

        return evaluator(payload)
