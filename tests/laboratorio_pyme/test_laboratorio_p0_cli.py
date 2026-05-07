from __future__ import annotations

import json

import pytest

from scripts import laboratorio_p0_cli as cli


class _FakeClientesRepo:
    def __init__(self) -> None:
        self._exists = False

    def exists(self, cliente_id: str) -> bool:
        return self._exists


class _FakeSupabaseClient:
    def __init__(self, clientes_repo: _FakeClientesRepo) -> None:
        self._clientes_repo = clientes_repo
        self.insert_calls = 0

    def table(self, name: str) -> "_FakeSupabaseClient":
        assert name == "clientes"
        return self

    def insert(self, row: dict) -> "_FakeSupabaseClient":
        self.insert_calls += 1
        self._clientes_repo._exists = True
        return self

    def execute(self):
        return type("R", (), {"data": []})()


class _FakeCtx:
    def __init__(self, cliente_id: str) -> None:
        self.cliente_id = cliente_id
        self.clientes = _FakeClientesRepo()


class _FakeCreado:
    def __init__(self) -> None:
        self.cliente_id = "cliente_demo"
        self.case_id = "case-1"
        self.job_id = "job-1"


class _FakeCerrado:
    def __init__(self) -> None:
        self.report_id = "rep-1"


class _FakeAppService:
    crear_calls = 0
    cerrar_calls = 0

    def __init__(self, laboratorio_service, persistence_context) -> None:
        self.ctx = persistence_context

    def crear_caso_persistente(self, **kwargs):
        _FakeAppService.crear_calls += 1
        return _FakeCreado()

    def cerrar_caso_persistente(self, **kwargs):
        _FakeAppService.cerrar_calls += 1
        return _FakeCerrado()


def test_parse_alias_diagnostico_operativo() -> None:
    parsed = cli._parse_laboratorio("diagnostico_operativo")
    assert parsed.value == "analisis_comercial"


def test_run_cli_emite_json_y_llama_flujo(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    ctx = _FakeCtx("cliente_demo")
    fake_supabase = _FakeSupabaseClient(ctx.clientes)

    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "supabase")
    monkeypatch.setenv("SMARTPYME_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SMARTPYME_SUPABASE_KEY", "SECRET_KEY_123")
    monkeypatch.setattr(
        cli.LaboratorioPersistenceContext,
        "from_repository_factory",
        classmethod(lambda cls, **kwargs: ctx),
    )
    monkeypatch.setattr(cli, "_build_supabase_client_from_env", lambda: fake_supabase)
    monkeypatch.setattr(cli, "LaboratorioApplicationService", _FakeAppService)

    exit_code = cli.run_cli(
        [
            "--cliente-id",
            "cliente_demo",
            "--dueno-nombre",
            "Dueño Demo",
            "--laboratorio",
            "diagnostico_operativo",
            "--hallazgo",
            "Primer hallazgo demo",
        ]
    )

    assert exit_code == 0
    assert _FakeAppService.crear_calls == 1
    assert _FakeAppService.cerrar_calls == 1
    assert fake_supabase.insert_calls == 1

    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert data["cliente_id"] == "cliente_demo"
    assert data["case_id"] == "case-1"
    assert data["job_id"] == "job-1"
    assert data["report_id"] == "rep-1"
    assert data["status"] == "closed"
    assert "SECRET_KEY_123" not in out
    assert "SMARTPYME_SUPABASE_KEY" not in out

