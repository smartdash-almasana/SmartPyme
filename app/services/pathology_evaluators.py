from collections.abc import Callable

from app.catalog.pathologies import get_pathology_definition, get_pathology_metadata
from app.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologyFinding,
    PathologyStatus,
)

PathologyEvaluator = Callable[[PathologyEvaluationInput], PathologyFinding]


def evaluate_margen_bruto_negativo(payload: PathologyEvaluationInput) -> PathologyFinding:
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


def evaluate_venta_bajo_costo(payload: PathologyEvaluationInput) -> PathologyFinding:
    definition = get_pathology_definition("venta_bajo_costo")
    result = payload.formula_result
    metadata = {"catalog": get_pathology_metadata("venta_bajo_costo")}

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
            explanation=f"La ganancia bruta calculada es {result.value}, lo cual indica venta bajo costo.",
            metadata=metadata,
        )

    return PathologyFinding(
        cliente_id=payload.cliente_id,
        pathology_id=definition.pathology_id,
        formula_result_id=payload.formula_result_id,
        formula_id=result.formula_id,
        status=PathologyStatus.NOT_DETECTED,
        source_refs=result.source_refs,
        explanation="No se detectó venta bajo costo con el resultado calculado.",
        metadata=metadata,
    )


EVALUATOR_REGISTRY: dict[str, PathologyEvaluator] = {
    "margen_bruto_negativo": evaluate_margen_bruto_negativo,
    "venta_bajo_costo": evaluate_venta_bajo_costo,
}


def get_pathology_evaluator(pathology_id: str) -> PathologyEvaluator | None:
    return EVALUATOR_REGISTRY.get(pathology_id)
