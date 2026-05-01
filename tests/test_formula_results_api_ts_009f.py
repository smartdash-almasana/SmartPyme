from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.formulas import FormulaDbPath, get_formula_db_path, router


def create_app(db_formula_results: Path):
    app = FastAPI()

    async def override_formula_db():
        return FormulaDbPath(formula_results=str(db_formula_results))

    app.dependency_overrides[get_formula_db_path] = override_formula_db
    app.include_router(router)
    return app


def _calculate(client: TestClient, result_id: str, cliente_id: str = "pyme_A"):
    return client.post(
        "/formulas/calculate",
        headers={"X-Client-ID": cliente_id},
        json={
            "formula_id": "ganancia_bruta",
            "result_id": result_id,
            "inputs": [
                {"name": "ventas", "value": 1000, "source_refs": ["ventas:1"]},
                {"name": "costos", "value": 650, "source_refs": ["costos:1"]},
            ],
        },
    )


def test_list_formula_results_requires_header(tmp_path):
    client = TestClient(create_app(tmp_path / "formula_results.db"))

    res = client.get("/formulas/results")

    assert res.status_code == 403


def test_list_formula_results(tmp_path):
    client = TestClient(create_app(tmp_path / "formula_results.db"))
    _calculate(client, "r1")

    res = client.get("/formulas/results", headers={"X-Client-ID": "pyme_A"})

    assert res.status_code == 200
    data = res.json()
    assert data["cliente_id"] == "pyme_A"
    assert data["count"] == 1
    assert data["results"][0]["formula_id"] == "ganancia_bruta"


def test_get_formula_result(tmp_path):
    client = TestClient(create_app(tmp_path / "formula_results.db"))
    _calculate(client, "r1")

    res = client.get("/formulas/results/r1", headers={"X-Client-ID": "pyme_A"})

    assert res.status_code == 200
    data = res.json()
    assert data["value"] == 350.0
    assert data["source_refs"] == ["ventas:1", "costos:1"]


def test_formula_result_cross_client_hidden(tmp_path):
    client = TestClient(create_app(tmp_path / "formula_results.db"))
    _calculate(client, "shared-id", cliente_id="pyme_A")

    res = client.get("/formulas/results/shared-id", headers={"X-Client-ID": "pyme_B"})

    assert res.status_code == 404
