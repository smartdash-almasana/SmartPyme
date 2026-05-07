"""Selector de proveedor de persistencia para SmartPyme P0.

Proveedor por defecto: sqlite (legacy, sin cambios de comportamiento).
Proveedor alternativo: supabase (declarado, no implementado en P0 Step 1).

Uso:
    from app.repositories.persistence_provider import get_provider, PersistenceProvider

    provider = get_provider()          # → PersistenceProvider.SQLITE (default)
    provider = get_provider("sqlite")  # → PersistenceProvider.SQLITE
    provider = get_provider("supabase") # → PersistenceProvider.SUPABASE

Fail-closed:
    get_provider("invalid") → ValueError con mensaje claro.
    validate_supabase_env() → ValueError si faltan variables de entorno
    cuando provider=supabase.

Variables de entorno:
    SMARTPYME_PERSISTENCE_PROVIDER=sqlite|supabase  (default: sqlite)
    SMARTPYME_SUPABASE_URL                          (requerida si provider=supabase)
    SMARTPYME_SUPABASE_KEY                          (requerida si provider=supabase)
    SMARTPYME_SUPABASE_SCHEMA                       (opcional, default: public)
"""
from __future__ import annotations

import os
from enum import Enum

_ENV_PROVIDER = "SMARTPYME_PERSISTENCE_PROVIDER"
_ENV_SUPABASE_URL = "SMARTPYME_SUPABASE_URL"
_ENV_SUPABASE_KEY = "SMARTPYME_SUPABASE_KEY"
_ENV_SUPABASE_SCHEMA = "SMARTPYME_SUPABASE_SCHEMA"

_DEFAULT_PROVIDER = "sqlite"
_SUPPORTED_PROVIDERS = frozenset({"sqlite", "supabase"})


class PersistenceProvider(str, Enum):
    """Proveedores de persistencia soportados en SmartPyme P0."""

    SQLITE = "sqlite"
    SUPABASE = "supabase"


def get_provider(provider: str | None = None) -> PersistenceProvider:
    """Resuelve el proveedor de persistencia activo.

    Orden de resolución:
    1. Argumento explícito `provider` (si se provee).
    2. Variable de entorno `SMARTPYME_PERSISTENCE_PROVIDER`.
    3. Default: `sqlite`.

    Args:
        provider: Nombre del proveedor. Si es None, se lee del entorno.

    Returns:
        PersistenceProvider correspondiente.

    Raises:
        ValueError: Si el proveedor no es uno de los soportados (fail-closed).
    """
    resolved = provider or os.environ.get(_ENV_PROVIDER, _DEFAULT_PROVIDER)
    normalized = resolved.strip().lower()

    if normalized not in _SUPPORTED_PROVIDERS:
        raise ValueError(
            f"PERSISTENCE_PROVIDER_INVALID: '{resolved}' no es un proveedor soportado. "
            f"Valores permitidos: {sorted(_SUPPORTED_PROVIDERS)}"
        )

    return PersistenceProvider(normalized)


def validate_supabase_env() -> None:
    """Valida que las variables de entorno requeridas para Supabase estén presentes.

    Solo debe llamarse cuando provider=supabase. Fail-closed si faltan variables.

    Raises:
        ValueError: Si `SMARTPYME_SUPABASE_URL` o `SMARTPYME_SUPABASE_KEY` no están definidas.
    """
    missing = []
    if not os.environ.get(_ENV_SUPABASE_URL, "").strip():
        missing.append(_ENV_SUPABASE_URL)
    if not os.environ.get(_ENV_SUPABASE_KEY, "").strip():
        missing.append(_ENV_SUPABASE_KEY)

    if missing:
        raise ValueError(
            f"BLOCKED_ENVIRONMENT_CONTRACT_MISSING: variables requeridas para "
            f"provider=supabase no definidas: {missing}"
        )
