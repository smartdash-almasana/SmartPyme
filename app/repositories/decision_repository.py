from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.contracts.decision_record import DecisionRecord


class DecisionRepository:
    def __init__(self, cliente_id: str, db_path: str | Path):
        self.cliente_id = cliente_id
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS decision_records (
                    cliente_id TEXT,
                    decision_id TEXT,
                    timestamp TEXT,
                    tipo_decision TEXT,
                    mensaje_original TEXT,
                    propuesta TEXT,
                    accion TEXT,
                    overrides TEXT,
                    job_id TEXT,
                    PRIMARY KEY (cliente_id, decision_id)
                )
                """
            )

    def create(self, record: DecisionRecord) -> None:
        if record.cliente_id != self.cliente_id:
            raise ValueError(f"Violacion de aislamiento: {record.cliente_id} != {self.cliente_id}")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO decision_records (
                    cliente_id, decision_id, timestamp, tipo_decision,
                    mensaje_original, propuesta, accion, overrides, job_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.cliente_id,
                    record.decision_id,
                    record.timestamp,
                    record.tipo_decision,
                    record.mensaje_original,
                    json.dumps(record.propuesta, ensure_ascii=False),
                    record.accion,
                    json.dumps(record.overrides, ensure_ascii=False) if record.overrides is not None else None,
                    record.job_id,
                ),
            )

    def get(self, decision_id: str) -> DecisionRecord | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM decision_records WHERE cliente_id = ? AND decision_id = ?",
                (self.cliente_id, decision_id),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
        return None

    def list_by_cliente(self) -> list[DecisionRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM decision_records WHERE cliente_id = ?", (self.cliente_id,)
            )
            return [self._row_to_record(row) for row in cursor.fetchall()]

    def _row_to_record(self, row: sqlite3.Row) -> DecisionRecord:
        return DecisionRecord(
            cliente_id=row["cliente_id"],
            decision_id=row["decision_id"],
            timestamp=row["timestamp"],
            tipo_decision=row["tipo_decision"],
            mensaje_original=row["mensaje_original"],
            propuesta=json.loads(row["propuesta"]),
            accion=row["accion"],
            overrides=json.loads(row["overrides"]) if row["overrides"] is not None else None,
            job_id=row["job_id"],
        )
