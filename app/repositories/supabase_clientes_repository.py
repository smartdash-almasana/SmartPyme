"""Adapter Supabase para clientes — SmartPyme P0.

Implementa ClientePort usando un cliente Supabase inyectable.
El cliente real es `supabase.Client` (librería supabase-py).
En tests se inyecta un FakeSupabaseClient sin red.

CONTRACT_BRIDGE:
    No existe una entidad de dominio `Cliente` en app/contracts.
    Este adapter devuelve `dict | None` normalizado desde la fila de Supabase.
    El dict normalizado incluye las claves del schema draft:
        cliente_id, nombre, status, metadata, created_at, updated_at.
    Si en el futuro se crea un dataclass Cliente, el adapter puede adaptarse
    sin cambiar la firma pública de ClientePort.

Reglas:
    - Constructor NO requiere cliente_id (este repo consulta clientes por parámetro).
    - get(cliente_id) y exists(cliente_id) fallan cerrado si cliente_id está vacío.
    - Si no se inyecta cliente explícito, se valida el entorno Supabase.
    - No introduce tenant_id ni owner_id como aislamiento primario.
    - No modifica repositorios SQLite legacy.
    - No hace dual-write.

Tabla Supabase esperada: clientes
    cliente_id      TEXT PRIMARY KEY
    nombre          TEXT
    status          TEXT NOT NULL DEFAULT 'active'
    metadata        JSONB
    created_at      TIMESTAMPTZ
    updated_at      TIMESTAMPTZ
"""
from __future__ import annotations

from typing import Any

from app.repositories.persistence_provider import validate_supabase_env

_TABLE = "clientes"


class SupabaseClientesRepository:
    """Adapter Supabase para clientes. Implementa ClientePort.

    Args:
        supabase_client: Cliente Supabase inyectable. Si es None, se valida
            el entorno (SMARTPYME_SUPABASE_URL / SMARTPYME_SUPABASE_KEY) y se
            construye el cliente real. En tests, inyectar un FakeSupabaseClient.
    """

    def __init__(self, supabase_client: Any | None = None) -> None:
        if supabase_client is None:
            # Sin cliente inyectado → validar entorno y construir cliente real.
            validate_supabase_env()
            self._client = self._build_real_client()
        else:
            self._client = supabase_client

    # ------------------------------------------------------------------
    # ClientePort interface
    # ------------------------------------------------------------------

    def get(self, cliente_id: str) -> dict[str, Any] | None:
        """Recupera un cliente por cliente_id.

        Args:
            cliente_id: Identificador único del cliente. Obligatorio.

        Returns:
            Dict normalizado con los campos del cliente, o None si no existe.

        Raises:
            ValueError: Si cliente_id está vacío (fail-closed).
        """
        self._require_cliente_id(cliente_id)

        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", cliente_id)
            .execute()
        )

        rows = response.data
        if not rows:
            return None

        return self._normalize_row(rows[0])

    def exists(self, cliente_id: str) -> bool:
        """Verifica si un cliente existe en el catálogo.

        Args:
            cliente_id: Identificador único del cliente. Obligatorio.

        Returns:
            True si el cliente existe, False en caso contrario.

        Raises:
            ValueError: Si cliente_id está vacío (fail-closed).
        """
        self._require_cliente_id(cliente_id)
        return self.get(cliente_id) is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_cliente_id(cliente_id: str) -> None:
        """Fail-closed si cliente_id está vacío o solo espacios."""
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required")

    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        """Normaliza una fila de Supabase al dict canónico de cliente P0.

        Claves garantizadas en el resultado:
            cliente_id, nombre, status, metadata, created_at, updated_at.
        """
        return {
            "cliente_id": row["cliente_id"],
            "nombre": row.get("nombre"),
            "status": row.get("status", "active"),
            "metadata": row.get("metadata") or {},
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    @staticmethod
    def _build_real_client() -> Any:
        """Construye el cliente Supabase real usando variables de entorno.

        Solo se llama cuando no se inyecta un cliente explícito y el entorno
        ya fue validado por validate_supabase_env().

        Raises:
            ImportError: Si la librería supabase-py no está instalada.
        """
        import os

        try:
            from supabase import create_client  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "BLOCKED_MISSING_DEPENDENCY: la librería 'supabase' no está instalada. "
                "Instalar con: pip install supabase"
            ) from exc

        url = os.environ["SMARTPYME_SUPABASE_URL"]
        key = os.environ["SMARTPYME_SUPABASE_KEY"]
        return create_client(url, key)
