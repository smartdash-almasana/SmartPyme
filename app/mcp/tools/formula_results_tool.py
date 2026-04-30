from pathlib import Path

from app.contracts.formula_contract import FormulaResult, FormulaStatus
from app.repositories.formula_result_repository import FormulaResultRepository


def get_formula_results(cliente_id: str, formula_id: str | None = None) -> list[dict]:
    repo = FormulaResultRepository(cliente_id, Path("data/formula_results.db"))
    results = repo.list_results(formula_id=formula_id)
    return [_serialize_result(result) for result in results]


def get_formula_result(cliente_id: str, result_id: str) -> dict | None:
    repo = FormulaResultRepository(cliente_id, Path("data/formula_results.db"))
    result = repo.get(result_id)
    if result is None:
        return None
    return _serialize_result(result)


def interpret_formula_result(result: dict) -> str:
    formula_id = result.get("formula_id", "formula")
    status = result.get("status")
    value = result.get("value")
    blocking_reason = result.get("blocking_reason")
    source_refs = result.get("source_refs", [])

    if status == FormulaStatus.BLOCKED.value or status == "BLOCKED":
        return (
            f"No pude calcular {formula_id}. "
            f"Motivo: {blocking_reason}. "
            f"Fuentes revisadas: {len(source_refs)}."
        )

    return (
        f"Resultado calculado para {formula_id}: {value}. "
        f"Fuentes usadas: {len(source_refs)}."
    )


def get_formula_status_for_owner(cliente_id: str, formula_id: str | None = None) -> dict:
    results = get_formula_results(cliente_id, formula_id=formula_id)
    messages = [interpret_formula_result(result) for result in results]
    return {
        "cliente_id": cliente_id,
        "count": len(results),
        "results": results,
        "messages": messages,
    }


def _serialize_result(result: FormulaResult) -> dict:
    return result.model_dump(mode="json")
