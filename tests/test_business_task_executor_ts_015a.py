from pathlib import Path

import pytest

from app.contracts.pathology_contract import PathologyStatus
from app.agents.business_task_executor import (
    AUDIT_VENTA_BAJO_COSTO,
    BusinessTaskExecutor,
)
from app.mcp.tools.owner_status_tool import get_owner_status
from app.repositories.formula_result_repository import FormulaResultRepository
from app.repositories.pathology_repository import PathologyRepository


@pytest.fixture
def executor(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return BusinessTaskExecutor(
        formula_results_db_path=Path("data/formula_results.db"),
        pathologies_db_path=Path("data/pathologies.db"),
    )


def test_audit_venta_bajo_costo_e2e_persists_active_pathology(executor):
    result = executor.execute(
        AUDIT_VENTA_BAJO_COSTO,
        {
            "cliente_id": "pyme_A",
            "ventas": 1000,
            "costos": 1200,
            "source_refs": ["orden:1", "costo:1"],
            "formula_result_id": "fr_venta_bajo_costo_1",
            "pathology_finding_id": "pf_venta_bajo_costo_1",
        },
    )

    assert result["cliente_id"] == "pyme_A"
    assert result["formula_result_id"] == "fr_venta_bajo_costo_1"
    assert result["formula_result"]["formula_id"] == "ganancia_bruta"
    assert result["formula_result"]["value"] == -200.0
    assert result["pathology_finding_id"] == "pf_venta_bajo_costo_1"
    assert result["pathology_finding"]["pathology_id"] == "venta_bajo_costo"
    assert result["pathology_finding"]["status"] == PathologyStatus.ACTIVE.value

    persisted_formula = FormulaResultRepository(
        "pyme_A",
        Path("data/formula_results.db"),
    ).get("fr_venta_bajo_costo_1")
    assert persisted_formula is not None
    assert persisted_formula.value == -200.0

    persisted_finding = PathologyRepository(
        "pyme_A",
        Path("data/pathologies.db"),
    ).get("pf_venta_bajo_costo_1")
    assert persisted_finding is not None
    assert persisted_finding.status == PathologyStatus.ACTIVE

    owner_status = get_owner_status("pyme_A")
    assert owner_status["formula_results_count"] >= 1
    assert owner_status["pathology_findings_count"] >= 1
    assert owner_status["pathology_findings"][0]["pathology_id"] == "venta_bajo_costo"


def test_audit_venta_bajo_costo_isolated_by_cliente_id(executor):
    executor.audit_venta_bajo_costo(
        {
            "cliente_id": "pyme_A",
            "ventas": 1000,
            "costos": 1200,
            "source_refs": ["orden:1"],
            "formula_result_id": "shared_formula_id",
            "pathology_finding_id": "shared_pathology_id",
        }
    )

    formula_repo_b = FormulaResultRepository("pyme_B", Path("data/formula_results.db"))
    pathology_repo_b = PathologyRepository("pyme_B", Path("data/pathologies.db"))

    assert formula_repo_b.get("shared_formula_id") is None
    assert pathology_repo_b.get("shared_pathology_id") is None

    owner_status_b = get_owner_status("pyme_B")
    assert owner_status_b["formula_results_count"] == 0
    assert owner_status_b["pathology_findings_count"] == 0


def test_audit_venta_bajo_costo_rejects_missing_cliente_id(executor):
    with pytest.raises(ValueError, match="cliente_id is required"):
        executor.audit_venta_bajo_costo(
            {"ventas": 1000, "costos": 1200, "source_refs": ["orden:1"]}
        )
