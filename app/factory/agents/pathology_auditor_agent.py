from pathlib import Path

from app.contracts.pathology_contract import PathologyEvaluationInput, PathologyFinding
from app.repositories.formula_result_repository import FormulaResultRepository
from app.repositories.pathology_repository import PathologyRepository
from app.services.pathology_engine_service import PathologyEngineService


class PathologyAuditorAgent:
    def __init__(
        self,
        cliente_id: str,
        formula_results_db_path: str | Path,
        pathologies_db_path: str | Path,
    ) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required for PathologyAuditorAgent")

        self.cliente_id = cliente_id
        self.formula_results = FormulaResultRepository(cliente_id, formula_results_db_path)
        self.pathologies = PathologyRepository(cliente_id, pathologies_db_path)
        self.engine = PathologyEngineService()

    def audit_formula_result(
        self,
        formula_result_id: str,
        pathology_id: str = "margen_bruto_negativo",
        pathology_finding_id: str | None = None,
    ) -> PathologyFinding | None:
        formula_result = self.formula_results.get(formula_result_id)
        if formula_result is None:
            return None

        finding = self.engine.evaluate(
            pathology_id,
            PathologyEvaluationInput(
                cliente_id=self.cliente_id,
                formula_result_id=formula_result_id,
                formula_result=formula_result,
            ),
        )

        pathology_finding_id = pathology_finding_id or f"{pathology_id}:{formula_result_id}"
        self.pathologies.save(pathology_finding_id, finding)
        return finding
