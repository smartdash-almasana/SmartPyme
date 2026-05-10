from __future__ import annotations

import json
from pathlib import Path

import tools.bem_submit_payload as cli


class _FakeBemClient:
    last_init: dict | None = None
    last_submit: dict | None = None
    response: dict = {"status": "ok"}

    def __init__(self, api_key=None, base_url="https://api.bem.ai") -> None:
        _FakeBemClient.last_init = {"api_key": api_key, "base_url": base_url}

    def submit_payload(self, workflow_id: str, payload: dict):
        _FakeBemClient.last_submit = {"workflow_id": workflow_id, "payload": payload}
        return _FakeBemClient.response


def test_payload_valido(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"tenant_id":"acme","payload":{"evidence_id":"ev-1"}}', encoding="utf-8")
    _FakeBemClient.response = {"accepted": True, "id": "r1"}
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(
        [
            "--workflow-id",
            "demo-workflow",
            "--payload-file",
            str(payload_file),
            "--base-url",
            "https://bem.test",
            "--api-key",
            "key-1",
        ]
    )

    out = capsys.readouterr().out
    assert code == 0
    assert json.loads(out) == {"accepted": True, "id": "r1"}
    assert _FakeBemClient.last_init == {"api_key": "key-1", "base_url": "https://bem.test"}
    assert _FakeBemClient.last_submit is not None
    assert _FakeBemClient.last_submit["workflow_id"] == "demo-workflow"


def test_archivo_inexistente(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(["--workflow-id", "demo", "--payload-file", "no-existe.json"])

    err = capsys.readouterr().err
    assert code == 1
    assert "payload file not found" in err


def test_json_invalido(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(["--workflow-id", "demo", "--payload-file", str(payload_file)])

    err = capsys.readouterr().err
    assert code == 1
    assert "invalid JSON payload file" in err


def test_workflow_vacio(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(["--workflow-id", "   ", "--payload-file", str(payload_file)])

    err = capsys.readouterr().err
    assert code == 2
    assert "workflow_id is required" in err


def test_output_json_esperado(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"a":1}', encoding="utf-8")
    _FakeBemClient.response = {"status": "accepted", "tenant_id": "acme", "evidence_id": "ev-1"}
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(["--workflow-id", "wf", "--payload-file", str(payload_file)])

    out = capsys.readouterr().out
    assert code == 0
    assert json.loads(out) == {"status": "accepted", "tenant_id": "acme", "evidence_id": "ev-1"}
