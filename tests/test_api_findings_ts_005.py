from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.findings import router, get_findings_db_path, FindingsDbPath
from app.repositories.finding_repository import FindingRepository
from app.services.findings_service import Finding


def create_app(db: Path):
    app = FastAPI()

    async def override_db():
        return FindingsDbPath(findings=str(db))

    app.dependency_overrides[get_findings_db_path] = override_db
    app.include_router(router)
    return app


def _finding(owner: str):
    return Finding(
        finding_id="same-finding",
        entity_id_a="a",
        entity_id_b="b",
        entity_type="cuit",
        metric="price",
        source_a_value=100,
        source_b_value=200,
        difference=100,
        difference_pct=50,
        severity="CRITICAL",
        suggested_action="Revisar",
        traceable_origin={"owner": owner},
    )


def test_findings_isolated_by_cliente_shared_db(tmp_path):
    db = tmp_path / "findings.db"

    repo_a = FindingRepository("pyme_A", db)
    repo_b = FindingRepository("pyme_B", db)

    repo_a.save(_finding("pyme_A"))
    repo_b.save(_finding("pyme_B"))

    client = TestClient(create_app(db))

    res_a = client.get("/findings", headers={"X-Client-ID": "pyme_A"})
    res_b = client.get("/findings", headers={"X-Client-ID": "pyme_B"})

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    data_a = res_a.json()
    data_b = res_b.json()

    assert data_a["cliente_id"] == "pyme_A"
    assert data_b["cliente_id"] == "pyme_B"

    assert data_a["count"] == 1
    assert data_b["count"] == 1

    f_a = data_a["findings"][0]
    f_b = data_b["findings"][0]

    assert f_a["finding_id"] == f_b["finding_id"] == "same-finding"
    assert f_a["traceable_origin"]["owner"] == "pyme_A"
    assert f_b["traceable_origin"]["owner"] == "pyme_B"
    assert f_a["traceable_origin"]["owner"] != f_b["traceable_origin"]["owner"]
