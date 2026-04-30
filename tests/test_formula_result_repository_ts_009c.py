from app.contracts.formula_contract import FormulaInput, FormulaStatus
from app.repositories.formula_result_repository import FormulaResultRepository
from app.services.formula_engine_service import FormulaEngineService


def _result():
    return FormulaEngineService().calculate(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=600, source_refs=["costos:1"]),
        ],
    )


def test_save_and_get_formula_result(tmp_path):
    repo = FormulaResultRepository("pyme_A", tmp_path / "formula_results.db")
    result = _result()

    repo.save("r1", result)
    loaded = repo.get("r1")

    assert loaded is not None
    assert loaded.formula_id == "ganancia_bruta"
    assert loaded.status == FormulaStatus.OK
    assert loaded.value == 400.0
    assert loaded.source_refs == ["ventas:1", "costos:1"]


def test_list_formula_results(tmp_path):
    repo = FormulaResultRepository("pyme_A", tmp_path / "formula_results.db")

    repo.save("r1", _result())

    results = repo.list_results("ganancia_bruta")

    assert len(results) == 1
    assert results[0].formula_id == "ganancia_bruta"


def test_formula_result_isolation(tmp_path):
    db = tmp_path / "formula_results.db"
    repo_a = FormulaResultRepository("pyme_A", db)
    repo_b = FormulaResultRepository("pyme_B", db)

    repo_a.save("same-id", _result())

    assert repo_a.get("same-id") is not None
    assert repo_b.get("same-id") is None
