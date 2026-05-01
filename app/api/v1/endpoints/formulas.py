from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_active_client
from app.contracts.formula_contract import FormulaInput, FormulaResult
from app.agents.formula_calculation_agent import FormulaCalculationAgent
from app.repositories.formula_result_repository import FormulaResultRepository

router = APIRouter()


class FormulaDbPath(BaseModel):
    formula_results: str


class FormulaCalculationRequest(BaseModel):
    formula_id: str
    inputs: list[FormulaInput]
    result_id: str | None = None


async def get_formula_db_path() -> FormulaDbPath:
    return FormulaDbPath(formula_results="data/formula_results.db")


def serialize_formula_result(result: FormulaResult) -> dict:
    return result.model_dump(mode="json")


@router.post("/formulas/calculate")
async def calculate_formula_endpoint(
    payload: FormulaCalculationRequest,
    cliente_id: str = Depends(get_active_client),
    db_path: FormulaDbPath = Depends(get_formula_db_path),
):
    agent = FormulaCalculationAgent(cliente_id, Path(db_path.formula_results))
    result = agent.calculate_and_persist(
        formula_id=payload.formula_id,
        inputs=payload.inputs,
        result_id=payload.result_id,
    )
    return serialize_formula_result(result)


@router.get("/formulas/results")
async def list_formula_results(
    formula_id: str | None = None,
    cliente_id: str = Depends(get_active_client),
    db_path: FormulaDbPath = Depends(get_formula_db_path),
):
    repo = FormulaResultRepository(cliente_id, Path(db_path.formula_results))
    results = repo.list_results(formula_id=formula_id)

    return {
        "cliente_id": cliente_id,
        "count": len(results),
        "results": [serialize_formula_result(result) for result in results],
    }


@router.get("/formulas/results/{result_id}")
async def get_formula_result(
    result_id: str,
    cliente_id: str = Depends(get_active_client),
    db_path: FormulaDbPath = Depends(get_formula_db_path),
):
    repo = FormulaResultRepository(cliente_id, Path(db_path.formula_results))
    result = repo.get(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Formula result not found")

    return serialize_formula_result(result)
