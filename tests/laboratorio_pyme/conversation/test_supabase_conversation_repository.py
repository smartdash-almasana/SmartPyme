from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from app.laboratorio_pyme.conversation.serialization import conversation_state_to_dict
from app.laboratorio_pyme.conversation.state import FaseConversacion, crear_estado_inicial
from app.laboratorio_pyme.conversation.supabase_repository import (
    SupabaseConversationRepository,
)


@dataclass
class _FakeResponse:
    data: Any


class _FakeQuery:
    def __init__(self, client: "_FakeSupabaseClient") -> None:
        self._client = client
        self._filters: dict[str, Any] = {}
        self._limit: int | None = None
        self._upsert_payload: dict[str, Any] | None = None

    def select(self, _fields: str) -> "_FakeQuery":
        return self

    def eq(self, field: str, value: Any) -> "_FakeQuery":
        self._filters[field] = value
        return self

    def limit(self, value: int) -> "_FakeQuery":
        self._limit = value
        return self

    def upsert(self, payload: dict[str, Any], on_conflict: str) -> "_FakeQuery":
        self._client.last_upsert_on_conflict = on_conflict
        self._upsert_payload = dict(payload)
        return self

    def execute(self) -> _FakeResponse:
        if self._upsert_payload is not None:
            cliente_id = self._upsert_payload["cliente_id"]
            self._client.rows[cliente_id] = dict(self._upsert_payload)
            self._client.last_upsert_payload = dict(self._upsert_payload)
            return _FakeResponse(data=[dict(self._upsert_payload)])

        cliente_id = self._filters.get("cliente_id")
        row = self._client.rows.get(cliente_id)
        if row is None:
            return _FakeResponse(data=[])

        data = [dict(row)]
        if self._limit is not None:
            data = data[: self._limit]
        return _FakeResponse(data=data)


class _FakeSupabaseClient:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, Any]] = {}
        self.last_upsert_payload: dict[str, Any] | None = None
        self.last_upsert_on_conflict: str | None = None

    def table(self, _name: str) -> _FakeQuery:
        return _FakeQuery(self)


def test_get_active_session_devuelve_none_si_no_existe() -> None:
    client = _FakeSupabaseClient()
    repo = SupabaseConversationRepository(client)

    assert repo.get_active_session("cliente_inexistente") is None


def test_get_or_create_crea_sesion_y_persiste_snapshot() -> None:
    client = _FakeSupabaseClient()
    repo = SupabaseConversationRepository(client)

    state = repo.get_or_create_active_session("cliente_nuevo")

    assert state.cliente_id == "cliente_nuevo"
    assert "cliente_nuevo" in client.rows
    row = client.rows["cliente_nuevo"]
    assert row["fase"] == FaseConversacion.ANAMNESIS_GENERAL.value
    assert row["state_snapshot"]["cliente_id"] == "cliente_nuevo"


def test_get_or_create_reutiliza_sesion_existente() -> None:
    client = _FakeSupabaseClient()
    base = crear_estado_inicial("cliente_reutiliza")
    base.dolor_principal = "vendo mucho pero no queda plata"
    client.rows["cliente_reutiliza"] = {
        "cliente_id": "cliente_reutiliza",
        "fase": base.fase.value,
        "dolor_principal": base.dolor_principal,
        "dimension_foco": base.dimension_foco,
        "ultima_pregunta": base.ultima_pregunta,
        "state_snapshot": conversation_state_to_dict(base),
    }
    repo = SupabaseConversationRepository(client)

    state = repo.get_or_create_active_session("cliente_reutiliza")

    assert state.dolor_principal == "vendo mucho pero no queda plata"


def test_save_active_session_sincroniza_columnas_espejo_y_snapshot() -> None:
    client = _FakeSupabaseClient()
    repo = SupabaseConversationRepository(client)
    state = crear_estado_inicial("cliente_save")
    state.fase = FaseConversacion.RECOLECCION_EVIDENCIA
    state.dolor_principal = "falta caja"
    state.dimension_foco = "dinero"
    state.ultima_pregunta = "Cuanto debes cobrar esta semana?"

    repo.save_active_session(state)

    assert client.last_upsert_on_conflict == "cliente_id"
    assert client.last_upsert_payload is not None
    payload = client.last_upsert_payload
    assert payload["cliente_id"] == "cliente_save"
    assert payload["fase"] == FaseConversacion.RECOLECCION_EVIDENCIA.value
    assert payload["dolor_principal"] == "falta caja"
    assert payload["dimension_foco"] == "dinero"
    assert payload["ultima_pregunta"] == "Cuanto debes cobrar esta semana?"
    assert payload["state_snapshot"]["cliente_id"] == "cliente_save"


def test_fail_closed_cliente_id_vacio_en_get_active_session() -> None:
    client = _FakeSupabaseClient()
    repo = SupabaseConversationRepository(client)

    with pytest.raises(ValueError):
        repo.get_active_session("   ")


def test_fail_closed_cliente_id_vacio_en_get_or_create() -> None:
    client = _FakeSupabaseClient()
    repo = SupabaseConversationRepository(client)

    with pytest.raises(ValueError):
        repo.get_or_create_active_session("")


def test_fail_closed_cliente_id_vacio_en_save() -> None:
    client = _FakeSupabaseClient()
    repo = SupabaseConversationRepository(client)
    state = crear_estado_inicial("cliente_original")
    state.cliente_id = " \t "

    with pytest.raises(ValueError):
        repo.save_active_session(state)
