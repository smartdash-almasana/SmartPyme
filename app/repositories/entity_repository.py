from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from app.contracts.entity_contract import Entity


def _default_db_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "entities.db"


def _get_db_path() -> Path:
    raw_path = os.getenv("SMARTPYME_ENTITIES_DB")
    return Path(raw_path) if raw_path else _default_db_path()


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_entities_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                cliente_id TEXT NOT NULL DEFAULT 'sistema',
                entity_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                attributes_json TEXT NOT NULL,
                linked_canonical_rows_json TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                errors_json TEXT NOT NULL,
                PRIMARY KEY (cliente_id, entity_id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_entities_cliente_id
            ON entities(cliente_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_entities_cliente_id_entity_type
            ON entities(cliente_id, entity_type)
            """
        )


class EntityRepository:
    def __init__(self, cliente_id: str, db_path: str | Path | None = None) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required for EntityRepository isolation")

        self.cliente_id = cliente_id
        self.db_path = Path(db_path) if db_path is not None else _get_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self) -> None:
        previous_env = os.environ.get("SMARTPYME_ENTITIES_DB")
        os.environ["SMARTPYME_ENTITIES_DB"] = str(self.db_path)
        try:
            init_entities_db()
        finally:
            if previous_env is None:
                os.environ.pop("SMARTPYME_ENTITIES_DB", None)
            else:
                os.environ["SMARTPYME_ENTITIES_DB"] = previous_env

    def save(self, entity: Entity) -> None:
        attributes_json = json.dumps(entity.attributes, ensure_ascii=False, sort_keys=True)
        linked_canonical_rows_json = json.dumps(entity.linked_canonical_rows, ensure_ascii=False)
        errors_json = json.dumps(entity.errors, ensure_ascii=False)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO entities (
                    cliente_id,
                    entity_id,
                    entity_type,
                    attributes_json,
                    linked_canonical_rows_json,
                    validation_status,
                    errors_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cliente_id, entity_id) DO UPDATE SET
                    entity_type = excluded.entity_type,
                    attributes_json = excluded.attributes_json,
                    linked_canonical_rows_json = excluded.linked_canonical_rows_json,
                    validation_status = excluded.validation_status,
                    errors_json = excluded.errors_json
                """,
                (
                    self.cliente_id,
                    entity.entity_id,
                    entity.entity_type,
                    attributes_json,
                    linked_canonical_rows_json,
                    entity.validation_status,
                    errors_json,
                ),
            )

    def save_batch(self, entities: list[Entity]) -> None:
        for entity in entities:
            self.save(entity)

    def find_by_attribute(self, entity_type: str, attribute: str, value: Any) -> Entity | None:
        query = f"""
            SELECT
                entity_id,
                entity_type,
                attributes_json,
                linked_canonical_rows_json,
                validation_status,
                errors_json
            FROM entities
            WHERE cliente_id = ?
              AND entity_type = ?
              AND json_extract(attributes_json, '$.{attribute}') = ?
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(query, (self.cliente_id, entity_type, value)).fetchone()

        return _row_to_entity(row) if row else None

    def list_entities(self, entity_type: str | None = None) -> list[Entity]:
        query = """
            SELECT
                entity_id,
                entity_type,
                attributes_json,
                linked_canonical_rows_json,
                validation_status,
                errors_json
            FROM entities
            WHERE cliente_id = ?
              AND (? IS NULL OR entity_type = ?)
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (self.cliente_id, entity_type, entity_type)).fetchall()
        return [_row_to_entity(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _row_to_entity(row: sqlite3.Row) -> Entity:
    return Entity(
        entity_id=row["entity_id"],
        entity_type=row["entity_type"],
        attributes=json.loads(row["attributes_json"]),
        linked_canonical_rows=json.loads(row["linked_canonical_rows_json"]),
        validation_status=row["validation_status"],
        errors=json.loads(row["errors_json"]),
    )
