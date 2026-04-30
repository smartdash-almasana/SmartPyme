import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.repositories.finding_repository import FindingRepository
from app.services.findings_service import Finding

TEST_CLIENTE_ID = "test_cliente"


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[2] / "fixtures" / "tmp_finding_repository"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"findings-{uuid.uuid4().hex[:8]}.db"


def _repo() -> FindingRepository:
    return FindingRepository(TEST_CLIENTE_ID, _db_path())


def _finding(
    finding_id: str = "finding-1",
    *,
    entity_type: str = "cuit",
    severity: str = "ALTO",
    difference: float = 100.0,
    difference_pct: float = 10.0,
    traceable_origin: dict | None = None,
) -> Finding:
    return Finding(
        finding_id=finding_id,
        entity_id_a="ent-a",
        entity_id_b="ent-b",
        entity_type=entity_type,
        metric="price",
        source_a_value=1000.0,
        source_b_value=1100.0,
        difference=difference,
        difference_pct=difference_pct,
        severity=severity,
        suggested_action="Revisión recomendada",
        traceable_origin=traceable_origin or {"key": "value"},
    )


def test_finding_repository_save_and_list():
    repo = _repo()
    repo.save(_finding("f-1"))

    results = repo.list_findings()

    assert len(results) == 1
    f = results[0]
    assert f.finding_id == "f-1"
    assert f.entity_type == "cuit"
    assert f.severity == "ALTO"


def test_finding_repository_save_batch():
    repo = _repo()
    repo.save_batch([
        _finding("f-1", entity_type="cuit"),
        _finding("f-2", entity_type="invoice"),
        _finding("f-3", entity_type="cuit"),
    ])

    all_findings = repo.list_findings()
    assert len(all_findings) == 3

    cuit_findings = repo.list_findings(entity_type="cuit")
    assert len(cuit_findings) == 2

    invoice_findings = repo.list_findings(entity_type="invoice")
    assert len(invoice_findings) == 1


def test_finding_repository_idempotent_by_finding_id_per_cliente():
    repo = _repo()
    repo.save(_finding("f-1", severity="ALTO"))
    repo.save(_finding("f-1", severity="CRITICO"))

    results = repo.list_findings()
    assert len(results) == 1
    assert results[0].severity == "CRITICO"


def test_finding_repository_preserves_fields():
    repo = _repo()
    origin = {"comparison_result": {"entity_id_a": "a", "value": 42}}
    repo.save(_finding(
        "f-1",
        severity="MEDIO",
        difference=50.0,
        difference_pct=7.5,
        traceable_origin=origin,
    ))

    results = repo.list_findings()
    assert len(results) == 1
    f = results[0]
    assert f.severity == "MEDIO"
    assert f.difference == 50.0
    assert f.difference_pct == 7.5
    assert f.traceable_origin == origin


def test_finding_repository_list_empty_returns_empty_list():
    repo = _repo()
    assert repo.list_findings() == []


def test_finding_repository_isolated_by_cliente_shared_db():
    db = _db_path()
    repo_a = FindingRepository("pyme_A", db)
    repo_b = FindingRepository("pyme_B", db)

    repo_a.save(_finding("same-finding", severity="ALTO", traceable_origin={"owner": "pyme_A"}))
    repo_b.save(_finding("same-finding", severity="CRITICO", traceable_origin={"owner": "pyme_B"}))

    findings_a = repo_a.list_findings()
    findings_b = repo_b.list_findings()

    assert len(findings_a) == 1
    assert len(findings_b) == 1
    assert findings_a[0].finding_id == findings_b[0].finding_id == "same-finding"
    assert findings_a[0].severity == "ALTO"
    assert findings_b[0].severity == "CRITICO"
    assert findings_a[0].traceable_origin["owner"] == "pyme_A"
    assert findings_b[0].traceable_origin["owner"] == "pyme_B"
