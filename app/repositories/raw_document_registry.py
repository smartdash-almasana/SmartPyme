from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _default_db_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "raw_documents.db"


def _get_db_path() -> Path:
    raw_path = os.getenv("SMARTPYME_RAW_DOCUMENTS_DB")
    return Path(raw_path) if raw_path else _default_db_path()


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_raw_documents_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_documents (
                raw_document_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_hash_sha256 TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT,
                job_id TEXT,
                plan_id TEXT,
                source_id TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_documents_file_hash_sha256
            ON raw_documents(file_hash_sha256)
            """
        )


def compute_file_sha256(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"raw_document_file_not_found: {file_path}")

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def register_raw_document(
    file_path: str,
    job_id: str | None = None,
    plan_id: str | None = None,
    source_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    init_raw_documents_db()

    path = Path(file_path).resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"raw_document_file_not_found: {file_path}")

    file_hash = compute_file_sha256(str(path))
    existing = get_raw_document_by_hash(file_hash)
    if existing is not None:
        return existing

    raw_document_id = f"raw_{file_hash[:16]}"
    metadata_json = json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)
    created_at = datetime.now(UTC).isoformat()
    mime_type = mimetypes.guess_type(path.name)[0]

    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO raw_documents (
                    raw_document_id,
                    file_path,
                    filename,
                    file_hash_sha256,
                    size_bytes,
                    mime_type,
                    job_id,
                    plan_id,
                    source_id,
                    metadata_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    raw_document_id,
                    str(path),
                    path.name,
                    file_hash,
                    path.stat().st_size,
                    mime_type,
                    job_id,
                    plan_id,
                    source_id,
                    metadata_json,
                    created_at,
                ),
            )
    except sqlite3.IntegrityError:
        existing_after_race = get_raw_document_by_hash(file_hash)
        if existing_after_race is not None:
            return existing_after_race
        raise

    stored = get_raw_document(raw_document_id)
    if stored is None:
        raise RuntimeError(f"raw_document_not_persisted: {raw_document_id}")
    return stored


def get_raw_document(raw_document_id: str) -> dict[str, Any] | None:
    init_raw_documents_db()
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT
                raw_document_id,
                file_path,
                filename,
                file_hash_sha256,
                size_bytes,
                mime_type,
                job_id,
                plan_id,
                source_id,
                metadata_json,
                created_at
            FROM raw_documents
            WHERE raw_document_id = ?
            """,
            (raw_document_id,),
        ).fetchone()
    return _row_to_dict(row)


def get_raw_document_by_hash(file_hash_sha256: str) -> dict[str, Any] | None:
    init_raw_documents_db()
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT
                raw_document_id,
                file_path,
                filename,
                file_hash_sha256,
                size_bytes,
                mime_type,
                job_id,
                plan_id,
                source_id,
                metadata_json,
                created_at
            FROM raw_documents
            WHERE file_hash_sha256 = ?
            """,
            (file_hash_sha256,),
        ).fetchone()
    return _row_to_dict(row)


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None

    data = dict(row)
    metadata_json = data.pop("metadata_json", None)
    try:
        data["metadata"] = json.loads(metadata_json) if metadata_json else {}
    except json.JSONDecodeError:
        data["metadata"] = {}
    return data
