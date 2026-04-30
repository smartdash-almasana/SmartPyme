from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_active_client
from app.contracts.formula_contract import FormulaInput
from app.factory.agents.formula_calculation_agent import FormulaCalculationAgent

router = APIRouter()


class FormulaDbPath(BaseModel):
    formula_results: str


class FormulaCalculationRequest(BaseModel):
    formula_id: str
    inputs: list[FormulaInput]
    result_id: str | None = None


async def get_formula_db_path() -> FormulaDbPath:
    return FormulaDbPath(formula_results="data/formula_results.db")


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
    return result.model_dump(mode="json")
