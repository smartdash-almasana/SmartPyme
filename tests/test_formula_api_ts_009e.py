from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.formulas import router, get_formula_db_path, FormulaDbPath
from app.repositories.formula_result_repository import FormulaResultRepository


def create_app(db_formula_results: Path):
    app = FastAPI()

    async def override_formula_db():
        return FormulaDbPath(formula_results=str(db_formula_results))

    app.dependency_overrides[get_formula_db_path] = override_formula_db
    app.include_router(router)
    return app


def test_formula_api_requires_client_header(tmp_path):
    client = TestClient(create_app(tmp_path / "formula_results.db"))

    res = client.post("/formulas/calculate", json={"formula_id": "ganancia_bruta", "inputs": []})

    assert res.status_code == 403


def test_formula_api_calculates_and_persists(tmp_path):
    db = tmp_path / "formula_results.db"
    client = TestClient(create_app(db))

    res = client.post(
        "/formulas/calculate",
        headers={"X-Client-ID": "pyme_A"},
        json={
            "formula_id": "ganancia_bruta",
            "result_id": "api-calc-1",
            "inputs": [
                {"name": "ventas", "value": 1000, "source_refs": ["ventas:1"]},
                {"name": "costos", "value": 650, "source_refs": ["costos:1"]},
            ],
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OK"
    assert data["value"] == 350.0

    repo = FormulaResultRepository("pyme_A", db)
    persisted = repo.get("api-calc-1")
    assert persisted is not None
    assert persisted.value == 350.0


def test_formula_api_isolation(tmp_path):
    db = tmp_path / "formula_results.db"
    client = TestClient(create_app(db))

    client.post(
        "/formulas/calculate",
        headers={"X-Client-ID": "pyme_A"},
        json={
            "formula_id": "ganancia_bruta",
            "result_id": "same-id",
            "inputs": [
                {"name": "ventas", "value": 1000, "source_refs": []},
                {"name": "costos", "value": 650, "source_refs": []},
            ],
        },
    )

    repo_b = FormulaResultRepository("pyme_B", db)
    assert repo_b.get("same-id") is None


def test_formula_api_returns_blocked_status(tmp_path):
    db = tmp_path / "formula_results.db"
    client = TestClient(create_app(db))

    res = client.post(
        "/formulas/calculate",
        headers={"X-Client-ID": "pyme_A"},
        json={
            "formula_id": "margen_bruto",
            "result_id": "blocked-calc",
            "inputs": [
                {"name": "ventas", "value": 0, "source_refs": ["ventas:zero"]},
                {"name": "costos", "value": 650, "source_refs": ["costos:1"]},
            ],
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "BLOCKED"
    assert data["blocking_reason"] == "DIVISION_BY_ZERO: ventas"
