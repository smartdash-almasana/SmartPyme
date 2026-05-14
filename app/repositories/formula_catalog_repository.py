from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.contracts.formula_catalog import FormulaCatalogEntry, TenantFormulaOverride


class FormulaCatalogRepository:
    """SQLite repository for formula_catalog and tenant_formula_overrides."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS formula_catalog (
                    formula_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    required_inputs_json TEXT NOT NULL,
                    accepted_sources_json TEXT NOT NULL,
                    assumptions_json TEXT NOT NULL,
                    unit TEXT,
                    period TEXT,
                    when_not_to_use TEXT,
                    confidence REAL NOT NULL,
                    allows_tenant_override INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant_formula_overrides (
                    cliente_id TEXT NOT NULL,
                    formula_id TEXT NOT NULL,
                    override_id TEXT NOT NULL,
                    overridden_inputs_json TEXT,
                    assumptions_json TEXT,
                    unit TEXT,
                    period TEXT,
                    when_not_to_use TEXT,
                    confidence REAL NOT NULL,
                    approved_by TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    PRIMARY KEY (cliente_id, formula_id, override_id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tenant_formula_overrides_cliente_formula
                ON tenant_formula_overrides(cliente_id, formula_id)
                """
            )

    def save_formula(self, formula: FormulaCatalogEntry) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO formula_catalog (
                    formula_id, name, description, required_inputs_json,
                    accepted_sources_json, assumptions_json, unit, period,
                    when_not_to_use, confidence, allows_tenant_override,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(formula_id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    required_inputs_json = excluded.required_inputs_json,
                    accepted_sources_json = excluded.accepted_sources_json,
                    assumptions_json = excluded.assumptions_json,
                    unit = excluded.unit,
                    period = excluded.period,
                    when_not_to_use = excluded.when_not_to_use,
                    confidence = excluded.confidence,
                    allows_tenant_override = excluded.allows_tenant_override,
                    metadata_json = excluded.metadata_json
                """,
                (
                    formula.formula_id,
                    formula.name,
                    formula.description,
                    json.dumps(formula.required_inputs, ensure_ascii=False),
                    json.dumps(formula.accepted_sources, ensure_ascii=False),
                    json.dumps(formula.assumptions, ensure_ascii=False),
                    formula.unit,
                    formula.period,
                    formula.when_not_to_use,
                    formula.confidence,
                    1 if formula.allows_tenant_override else 0,
                    json.dumps(formula.metadata, ensure_ascii=False, sort_keys=True),
                ),
            )

    def get_formula(self, formula_id: str) -> FormulaCatalogEntry | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT * FROM formula_catalog
                WHERE formula_id = ?
                """,
                (formula_id,),
            ).fetchone()
        return _row_to_formula(row) if row else None

    def list_formulas(self) -> list[FormulaCatalogEntry]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM formula_catalog
                ORDER BY formula_id
                """
            ).fetchall()
        return [_row_to_formula(row) for row in rows]

    def save_override(self, override: TenantFormulaOverride) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tenant_formula_overrides (
                    cliente_id, formula_id, override_id, overridden_inputs_json,
                    assumptions_json, unit, period, when_not_to_use, confidence,
                    approved_by, reason, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cliente_id, formula_id, override_id) DO UPDATE SET
                    overridden_inputs_json = excluded.overridden_inputs_json,
                    assumptions_json = excluded.assumptions_json,
                    unit = excluded.unit,
                    period = excluded.period,
                    when_not_to_use = excluded.when_not_to_use,
                    confidence = excluded.confidence,
                    approved_by = excluded.approved_by,
                    reason = excluded.reason,
                    metadata_json = excluded.metadata_json
                """,
                (
                    override.cliente_id,
                    override.formula_id,
                    override.override_id,
                    _json_or_none(override.overridden_inputs),
                    _json_or_none(override.assumptions),
                    override.unit,
                    override.period,
                    override.when_not_to_use,
                    override.confidence,
                    override.approved_by,
                    override.reason,
                    json.dumps(override.metadata, ensure_ascii=False, sort_keys=True),
                ),
            )

    def list_overrides(self, *, cliente_id: str, formula_id: str | None = None) -> list[TenantFormulaOverride]:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required")

        query = """
            SELECT * FROM tenant_formula_overrides
            WHERE cliente_id = ?
              AND (? IS NULL OR formula_id = ?)
            ORDER BY formula_id, override_id
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (cliente_id, formula_id, formula_id)).fetchall()
        return [_row_to_override(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _json_or_none(value: list[str] | None) -> str | None:
    return json.dumps(value, ensure_ascii=False) if value is not None else None


def _json_loads_or_none(value: str | None) -> list[str] | None:
    return json.loads(value) if value is not None else None


def _row_to_formula(row: sqlite3.Row) -> FormulaCatalogEntry:
    return FormulaCatalogEntry(
        formula_id=row["formula_id"],
        name=row["name"],
        description=row["description"],
        required_inputs=json.loads(row["required_inputs_json"]),
        accepted_sources=json.loads(row["accepted_sources_json"]),
        assumptions=json.loads(row["assumptions_json"]),
        unit=row["unit"],
        period=row["period"],
        when_not_to_use=row["when_not_to_use"],
        confidence=float(row["confidence"]),
        allows_tenant_override=bool(row["allows_tenant_override"]),
        metadata=json.loads(row["metadata_json"]),
    )


def _row_to_override(row: sqlite3.Row) -> TenantFormulaOverride:
    return TenantFormulaOverride(
        cliente_id=row["cliente_id"],
        formula_id=row["formula_id"],
        override_id=row["override_id"],
        overridden_inputs=_json_loads_or_none(row["overridden_inputs_json"]),
        assumptions=_json_loads_or_none(row["assumptions_json"]),
        unit=row["unit"],
        period=row["period"],
        when_not_to_use=row["when_not_to_use"],
        confidence=float(row["confidence"]),
        approved_by=row["approved_by"],
        reason=row["reason"],
        metadata=json.loads(row["metadata_json"]),
    )
