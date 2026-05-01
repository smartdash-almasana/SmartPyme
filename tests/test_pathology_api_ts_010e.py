from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.pathologies import PathologyDbPaths, get_pathology_db_paths, router
from app.contracts.formula_contract import FormulaInput
from app.agents.formula_calculation_agent import FormulaCalculationAgent


def create_app(formula_db: Path, pathology_db: Path):
    app = FastAPI()

    async def override_pathology_db():
        return PathologyDbPaths(
            formula_results=str(formula_db),
            pathologies=str(pathology_db),
        )

    app.dependency_overrides[get_pathology_db_paths] = override_pathology_db
    app.include_router(router)
    return app


def _seed_negative_margin(cliente_id: str, formula_db: Path, result_id: str = "fr1"):
    FormulaCalculationAgent(cliente_id, formula_db).calculate_and_persist(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=1200, source_refs=["costos:1"]),
        ],
        result_id=result_id,
    )


def test_pathology_audit_requires_header(tmp_path):
    client = TestClient(create_app(tmp_path / "formula.db", tmp_path / "pathologies.db"))

    res = client.post("/pathologies/audit", json={"formula_result_id": "fr1"})

    assert res.status_code == 403


def test_pathology_audit_detects_and_persists(tmp_path):
    formula_db = tmp_path / "formula.db"
    pathology_db = tmp_path / "pathologies.db"
    _seed_negative_margin("pyme_A", formula_db)
    client = TestClient(create_app(formula_db, pathology_db))

    res = client.post(
        "/pathologies/audit",
        headers={"X-Client-ID": "pyme_A"},
        json={"formula_result_id": "fr1", "pathology_finding_id": "pf1"},
    )

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ACTIVE"
    assert data["pathology_id"] == "margen_bruto_negativo"

    get_res = client.get("/pathologies/findings/pf1", headers={"X-Client-ID": "pyme_A"})
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "ACTIVE"


def test_pathology_list_findings(tmp_path):
    formula_db = tmp_path / "formula.db"
    pathology_db = tmp_path / "pathologies.db"
    _seed_negative_margin("pyme_A", formula_db)
    client = TestClient(create_app(formula_db, pathology_db))

    client.post(
        "/pathologies/audit",
        headers={"X-Client-ID": "pyme_A"},
        json={"formula_result_id": "fr1", "pathology_finding_id": "pf1"},
    )

    res = client.get("/pathologies/findings", headers={"X-Client-ID": "pyme_A"})

    assert res.status_code == 200
    assert res.json()["count"] == 1


def test_pathology_cross_client_hidden(tmp_path):
    formula_db = tmp_path / "formula.db"
    pathology_db = tmp_path / "pathologies.db"
    _seed_negative_margin("pyme_A", formula_db)
    client = TestClient(create_app(formula_db, pathology_db))

    client.post(
        "/pathologies/audit",
        headers={"X-Client-ID": "pyme_A"},
        json={"formula_result_id": "fr1", "pathology_finding_id": "pf1"},
    )

    res = client.get("/pathologies/findings/pf1", headers={"X-Client-ID": "pyme_B"})

    assert res.status_code == 404


def test_pathology_audit_missing_formula_result_returns_404(tmp_path):
    client = TestClient(create_app(tmp_path / "formula.db", tmp_path / "pathologies.db"))

    res = client.post(
        "/pathologies/audit",
        headers={"X-Client-ID": "pyme_A"},
        json={"formula_result_id": "missing"},
    )

    assert res.status_code == 404
