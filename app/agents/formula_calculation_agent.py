from pathlib import Path
from uuid import uuid4

from app.contracts.formula_contract import FormulaInput, FormulaResult
from app.repositories.formula_result_repository import FormulaResultRepository
from app.services.formula_engine_service import FormulaEngineService


class FormulaCalculationAgent:
    def __init__(self, cliente_id: str, db_path: str | Path):
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required for FormulaCalculationAgent")

        self.cliente_id = cliente_id
        self.engine = FormulaEngineService()
        self.repository = FormulaResultRepository(cliente_id, db_path)

    def calculate_and_persist(
        self,
        formula_id: str,
        inputs: list[FormulaInput],
        result_id: str | None = None,
    ) -> FormulaResult:
        result_id = result_id or str(uuid4())
        result = self.engine.calculate(formula_id, inputs)
        self.repository.save(result_id, result)
        result.metadata["result_id"] = result_id
        result.metadata["cliente_id"] = self.cliente_id
        self.repository.save(result_id, result)
        return result
