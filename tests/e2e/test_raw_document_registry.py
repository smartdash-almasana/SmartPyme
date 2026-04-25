import hashlib
import sqlite3
import uuid
from pathlib import Path

from app.repositories.raw_document_registry import (
    compute_file_sha256,
    get_raw_document,
    get_raw_document_by_hash,
    register_raw_document,
)


def test_raw_document_registry_hashes_and_deduplicates(monkeypatch):
    run_id = uuid.uuid4().hex[:8]
    fixture_dir = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_raw_document_registry"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    db_path = fixture_dir / f"raw-documents-{run_id}.db"
    file_path = fixture_dir / f"raw-document-{run_id}.txt"
    file_path.write_text("documento raw para validacion\n", encoding="utf-8")

    monkeypatch.setenv("SMARTPYME_RAW_DOCUMENTS_DB", str(db_path))

    expected_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
    computed_hash = compute_file_sha256(str(file_path))

    first = register_raw_document(
        str(file_path),
        job_id="job-raw-test",
        plan_id="plan-raw-test",
        source_id="source-raw-test",
        metadata={"doc_type": "fixture"},
    )
    second = register_raw_document(
        str(file_path),
        job_id="job-other",
        plan_id="plan-other",
        source_id="source-other",
        metadata={"doc_type": "ignored_duplicate"},
    )
    by_hash = get_raw_document_by_hash(expected_hash)
    by_id = get_raw_document(first["raw_document_id"])

    assert computed_hash == expected_hash
    assert first["raw_document_id"] == second["raw_document_id"]
    assert first["file_hash_sha256"] == expected_hash
    assert first["raw_document_id"].startswith("raw_")
    assert by_hash is not None
    assert by_hash["raw_document_id"] == first["raw_document_id"]
    assert by_id is not None
    assert by_id["metadata"] == {"doc_type": "fixture"}

    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM raw_documents WHERE file_hash_sha256 = ?",
            (expected_hash,),
        ).fetchone()[0]
    assert count == 1
