from app.catalog.pathologies import get_pathology_definition, get_pathology_metadata
from app.contracts.formula_contract import FormulaStatus
from app.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologyFinding,
    PathologyStatus,
)


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

        if pathology_id == "margen_bruto_negativo":
            return self._evaluate_margen_bruto_negativo(payload)

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

    def _evaluate_margen_bruto_negativo(self, payload: PathologyEvaluationInput) -> PathologyFinding:
        definition = get_pathology_definition("margen_bruto_negativo")
        result = payload.formula_result
        metadata = {"catalog": get_pathology_metadata("margen_bruto_negativo")}

        if result.value is not None and result.value < 0:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=definition.pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.ACTIVE,
                severity=definition.severity,
                suggested_action=definition.suggested_action,
                source_refs=result.source_refs,
                explanation=f"El margen bruto calculado es {result.value}, lo cual indica pérdida.",
                metadata=metadata,
            )

        return PathologyFinding(
            cliente_id=payload.cliente_id,
            pathology_id=definition.pathology_id,
            formula_result_id=payload.formula_result_id,
            formula_id=result.formula_id,
            status=PathologyStatus.NOT_DETECTED,
            source_refs=result.source_refs,
            explanation="No se detectó la patología con el resultado calculado.",
            metadata=metadata,
        )
