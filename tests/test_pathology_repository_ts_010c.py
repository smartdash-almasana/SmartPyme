from app.contracts.formula_contract import FormulaInput
from app.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologyStatus,
)
from app.repositories.pathology_repository import PathologyRepository
from app.services.formula_engine_service import FormulaEngineService
from app.services.pathology_engine_service import PathologyEngineService


def _finding(cliente_id="pyme_A"):
    formula_result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=1200, source_refs=["costos:1"]),
        ],
    )
    return PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id=cliente_id,
            formula_result_id="fr1",
            formula_result=formula_result,
        ),
    )


def test_save_and_get_pathology_finding(tmp_path):
    repo = PathologyRepository("pyme_A", tmp_path / "pathologies.db")
    finding = _finding()

    repo.save("pf1", finding)
    loaded = repo.get("pf1")

    assert loaded is not None
    assert loaded.pathology_id == "margen_bruto_negativo"
    assert loaded.status == PathologyStatus.ACTIVE
    assert loaded.source_refs == ["ventas:1", "costos:1"]


def test_list_pathology_findings(tmp_path):
    repo = PathologyRepository("pyme_A", tmp_path / "pathologies.db")
    repo.save("pf1", _finding())

    results = repo.list_findings(pathology_id="margen_bruto_negativo")

    assert len(results) == 1
    assert results[0].status == PathologyStatus.ACTIVE


def test_pathology_finding_isolation(tmp_path):
    db = tmp_path / "pathologies.db"
    repo_a = PathologyRepository("pyme_A", db)
    repo_b = PathologyRepository("pyme_B", db)

    repo_a.save("same-id", _finding("pyme_A"))

    assert repo_a.get("same-id") is not None
    assert repo_b.get("same-id") is None


def test_pathology_repository_blocks_cliente_mismatch(tmp_path):
    repo = PathologyRepository("pyme_A", tmp_path / "pathologies.db")
    finding = _finding("pyme_B")

    try:
        repo.save("bad", finding)
    except ValueError as exc:
        assert "cliente_id mismatch" in str(exc)
    else:
        raise AssertionError("Expected cliente_id mismatch")
