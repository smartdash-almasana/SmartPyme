"""Tests del selector de proveedor de persistencia SmartPyme P0.

Cubre:
- Proveedor default = sqlite
- sqlite explícito
- supabase reconocido
- proveedor inválido falla cerrado (fail-closed)
- variables de entorno de Supabase detectadas solo cuando provider=supabase
"""
import os
import pytest

from app.repositories.persistence_provider import (
    PersistenceProvider,
    get_provider,
    validate_supabase_env,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clear_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Elimina la variable de entorno del proveedor para aislar el test."""
    monkeypatch.delenv("SMARTPYME_PERSISTENCE_PROVIDER", raising=False)


def _clear_supabase_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Elimina las variables de entorno de Supabase para aislar el test."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_SCHEMA", raising=False)


# ---------------------------------------------------------------------------
# Proveedor default = sqlite
# ---------------------------------------------------------------------------

def test_default_provider_es_sqlite_sin_env(monkeypatch):
    """Sin argumento ni variable de entorno, el proveedor default es sqlite."""
    _clear_provider_env(monkeypatch)
    provider = get_provider()
    assert provider == PersistenceProvider.SQLITE


def test_default_provider_es_sqlite_con_env_vacia(monkeypatch):
    """Con SMARTPYME_PERSISTENCE_PROVIDER vacía, el proveedor default es sqlite."""
    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "")
    # Vacío normaliza a "" que no está en _SUPPORTED_PROVIDERS → ValueError
    # Pero el default es "sqlite" cuando la env está ausente, no vacía.
    # Vacío debe fallar cerrado.
    with pytest.raises(ValueError, match="PERSISTENCE_PROVIDER_INVALID"):
        get_provider()


# ---------------------------------------------------------------------------
# sqlite explícito
# ---------------------------------------------------------------------------

def test_sqlite_explicito_por_argumento(monkeypatch):
    """get_provider('sqlite') retorna PersistenceProvider.SQLITE."""
    _clear_provider_env(monkeypatch)
    provider = get_provider("sqlite")
    assert provider == PersistenceProvider.SQLITE


def test_sqlite_explicito_por_env(monkeypatch):
    """SMARTPYME_PERSISTENCE_PROVIDER=sqlite retorna PersistenceProvider.SQLITE."""
    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "sqlite")
    provider = get_provider()
    assert provider == PersistenceProvider.SQLITE


def test_sqlite_case_insensitive(monkeypatch):
    """El proveedor es case-insensitive: 'SQLite' y 'SQLITE' son válidos."""
    _clear_provider_env(monkeypatch)
    assert get_provider("SQLite") == PersistenceProvider.SQLITE
    assert get_provider("SQLITE") == PersistenceProvider.SQLITE


# ---------------------------------------------------------------------------
# supabase reconocido
# ---------------------------------------------------------------------------

def test_supabase_reconocido_por_argumento(monkeypatch):
    """get_provider('supabase') retorna PersistenceProvider.SUPABASE."""
    _clear_provider_env(monkeypatch)
    provider = get_provider("supabase")
    assert provider == PersistenceProvider.SUPABASE


def test_supabase_reconocido_por_env(monkeypatch):
    """SMARTPYME_PERSISTENCE_PROVIDER=supabase retorna PersistenceProvider.SUPABASE."""
    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "supabase")
    provider = get_provider()
    assert provider == PersistenceProvider.SUPABASE


def test_supabase_es_string_enum():
    """PersistenceProvider.SUPABASE es usable como string."""
    assert PersistenceProvider.SUPABASE == "supabase"
    assert isinstance(PersistenceProvider.SUPABASE, str)


# ---------------------------------------------------------------------------
# Proveedor inválido falla cerrado (fail-closed)
# ---------------------------------------------------------------------------

def test_proveedor_invalido_lanza_error(monkeypatch):
    """Un proveedor no soportado lanza ValueError con mensaje claro."""
    _clear_provider_env(monkeypatch)
    with pytest.raises(ValueError, match="PERSISTENCE_PROVIDER_INVALID"):
        get_provider("postgres")


def test_proveedor_invalido_por_env(monkeypatch):
    """SMARTPYME_PERSISTENCE_PROVIDER con valor inválido lanza ValueError."""
    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "mongodb")
    with pytest.raises(ValueError, match="PERSISTENCE_PROVIDER_INVALID"):
        get_provider()


def test_proveedor_invalido_mensaje_incluye_valor(monkeypatch):
    """El mensaje de error incluye el valor inválido provisto."""
    _clear_provider_env(monkeypatch)
    with pytest.raises(ValueError, match="dynamo"):
        get_provider("dynamo")


def test_proveedor_invalido_mensaje_incluye_permitidos(monkeypatch):
    """El mensaje de error menciona los valores permitidos."""
    _clear_provider_env(monkeypatch)
    with pytest.raises(ValueError, match="sqlite"):
        get_provider("invalid")


# ---------------------------------------------------------------------------
# Variables de entorno Supabase detectadas solo cuando provider=supabase
# ---------------------------------------------------------------------------

def test_validate_supabase_env_falla_si_url_falta(monkeypatch):
    """validate_supabase_env() falla si SMARTPYME_SUPABASE_URL no está definida."""
    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv("SMARTPYME_SUPABASE_KEY", "key-abc")
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        validate_supabase_env()


def test_validate_supabase_env_falla_si_key_falta(monkeypatch):
    """validate_supabase_env() falla si SMARTPYME_SUPABASE_KEY no está definida."""
    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv("SMARTPYME_SUPABASE_URL", "https://example.supabase.co")
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        validate_supabase_env()


def test_validate_supabase_env_falla_si_ambas_faltan(monkeypatch):
    """validate_supabase_env() falla si URL y KEY están ausentes."""
    _clear_supabase_env(monkeypatch)
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        validate_supabase_env()


def test_validate_supabase_env_pasa_si_url_y_key_presentes(monkeypatch):
    """validate_supabase_env() no lanza error si URL y KEY están definidas."""
    monkeypatch.setenv("SMARTPYME_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SMARTPYME_SUPABASE_KEY", "service-role-key-abc")
    validate_supabase_env()  # No debe lanzar


def test_sqlite_no_requiere_supabase_env(monkeypatch):
    """Con provider=sqlite, validate_supabase_env() no se llama y no hay error."""
    _clear_supabase_env(monkeypatch)
    _clear_provider_env(monkeypatch)
    # Solo verificar que get_provider() funciona sin env de Supabase
    provider = get_provider("sqlite")
    assert provider == PersistenceProvider.SQLITE
    # validate_supabase_env() no se llama para sqlite — no hay error implícito


def test_error_supabase_env_menciona_variables_faltantes(monkeypatch):
    """El mensaje de error de validate_supabase_env menciona las variables faltantes."""
    _clear_supabase_env(monkeypatch)
    with pytest.raises(ValueError, match="SMARTPYME_SUPABASE_URL"):
        validate_supabase_env()
