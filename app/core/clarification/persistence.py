import os
import sqlite3
from pathlib import Path

from app.core.clarification.models import ClarificationRecord, ClarificationRequest

DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "clarifications.db"


def _get_db_path() -> Path:
    raw_path = os.getenv("SMARTPYME_CLARIFICATIONS_DB")
    if raw_path:
        return Path(raw_path)
    return DEFAULT_DB_PATH


def _get_connection() -> sqlite3.Connection:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_clarifications_db() -> None:
    with _get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS clarifications (
                clarification_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                value_a TEXT NOT NULL,
                value_b TEXT NOT NULL,
                reason TEXT NOT NULL,
                blocking INTEGER NOT NULL,
                status TEXT NOT NULL,
                resolution TEXT
            )
            """
        )


def save_clarification(request: ClarificationRequest) -> None:
    init_clarifications_db()
    try:
        with _get_connection() as connection:
            connection.execute(
                """
                INSERT INTO clarifications (
                    clarification_id,
                    entity_type,
                    value_a,
                    value_b,
                    reason,
                    blocking,
                    status,
                    resolution
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.clarification_id,
                    request.entity_type,
                    request.value_a,
                    request.value_b,
                    request.reason,
                    1 if request.blocking else 0,
                    "pending",
                    None,
                ),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(
            f"CLARIFICATION_ID_DUPLICADO: {request.clarification_id}"
        ) from error


def list_pending_clarifications() -> list[ClarificationRecord]:
    init_clarifications_db()
    with _get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                clarification_id,
                entity_type,
                value_a,
                value_b,
                reason,
                blocking,
                status,
                resolution
            FROM clarifications
            WHERE status = 'pending'
            ORDER BY rowid ASC
            """
        ).fetchall()

    return [
        ClarificationRecord(
            clarification_id=row[0],
            entity_type=row[1],
            value_a=row[2],
            value_b=row[3],
            reason=row[4],
            blocking=bool(row[5]),
            status=row[6],
            resolution=row[7],
        )
        for row in rows
    ]


def resolve_clarification(clarification_id: str, resolution: str) -> bool:
    if not resolution.strip():
        raise ValueError("RESOLUTION_INVALIDA: la resolucion no puede estar vacia.")

    init_clarifications_db()
    with _get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE clarifications
            SET status = 'resolved', resolution = ?
            WHERE clarification_id = ? AND status = 'pending'
            """,
            (resolution, clarification_id),
        )
        return cursor.rowcount > 0


def has_blocking_pending_clarifications() -> bool:
    init_clarifications_db()
    with _get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(1)
            FROM clarifications
            WHERE status = 'pending' AND blocking = 1
            """
        ).fetchone()

    pending_count = int(row[0]) if row is not None else 0
    return pending_count > 0
