from __future__ import annotations

import json
from pathlib import Path

import tools.bem_submit_payload as cli


class _FakeBemClient:
    last_init: dict | None = None
    last_submit: dict | None = None
    last_submit_file: dict | None = None
    response: dict = {"status": "ok"}

    def __init__(self, api_key=None, base_url="https://api.bem.ai") -> None:
        _FakeBemClient.last_init = {"api_key": api_key, "base_url": base_url}

    def submit_payload(self, workflow_id: str, payload: dict):
        _FakeBemClient.last_submit = {"workflow_id": workflow_id, "payload": payload}
        return _FakeBemClient.response

    def submit_file(self, workflow_id: str, file_path: str | Path, call_reference_id: str | None = None):
        _FakeBemClient.last_submit_file = {
            "workflow_id": workflow_id,
            "file_path": str(file_path),
            "call_reference_id": call_reference_id,
        }
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


def test_file_valido_llama_submit_file(tmp_path: Path, monkeypatch, capsys) -> None:
    file_path = tmp_path / "ventas.xlsx"
    file_path.write_bytes(b"fake")
    _FakeBemClient.response = {"accepted": True, "id": "r-file"}
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(
        [
            "--workflow-id",
            "demo-workflow",
            "--file",
            str(file_path),
            "--api-key",
            "key-1",
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert json.loads(out) == {"accepted": True, "id": "r-file"}
    assert _FakeBemClient.last_submit_file is not None
    assert _FakeBemClient.last_submit_file["workflow_id"] == "demo-workflow"
    assert _FakeBemClient.last_submit_file["file_path"] == str(file_path)


def test_call_reference_id_llega_a_submit_file(tmp_path: Path, monkeypatch, capsys) -> None:
    file_path = tmp_path / "ventas.xlsx"
    file_path.write_bytes(b"fake")
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(
        [
            "--workflow-id",
            "demo-workflow",
            "--file",
            str(file_path),
            "--call-reference-id",
            "smartpyme-real-file-cli-001",
            "--api-key",
            "key-1",
        ]
    )
    assert code == 0
    assert _FakeBemClient.last_submit_file is not None
    assert _FakeBemClient.last_submit_file["call_reference_id"] == "smartpyme-real-file-cli-001"


def test_archivo_inexistente(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(
        ["--workflow-id", "demo", "--payload-file", "no-existe.json", "--api-key", "key-1"]
    )

    err = capsys.readouterr().err
    assert code == 1
    assert "payload file not found" in err


def test_falla_si_no_hay_input(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)
    code = cli.run(["--workflow-id", "wf", "--api-key", "k"])
    err = capsys.readouterr().err
    assert code == 2
    assert "one input is required" in err


def test_falla_si_hay_ambos_inputs(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"a":1}', encoding="utf-8")
    file_path = tmp_path / "ventas.xlsx"
    file_path.write_bytes(b"fake")
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)
    code = cli.run(
        [
            "--workflow-id",
            "wf",
            "--payload-file",
            str(payload_file),
            "--file",
            str(file_path),
            "--api-key",
            "k",
        ]
    )
    err = capsys.readouterr().err
    assert code == 2
    assert "only one input is allowed" in err


def test_json_invalido(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(
        ["--workflow-id", "demo", "--payload-file", str(payload_file), "--api-key", "key-1"]
    )

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

    code = cli.run(["--workflow-id", "wf", "--payload-file", str(payload_file), "--api-key", "k"])

    out = capsys.readouterr().out
    assert code == 0
    assert json.loads(out) == {"status": "accepted", "tenant_id": "acme", "evidence_id": "ev-1"}


def test_workflow_desde_env_local(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"a":1}', encoding="utf-8")
    (tmp_path / ".env.local").write_text(
        "BEM_WORKFLOW_ID=wf-local\nBEM_API_KEY=key-local\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BEM_WORKFLOW_ID", raising=False)
    monkeypatch.delenv("BEM_API_KEY", raising=False)
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(["--payload-file", str(payload_file)])

    assert code == 0
    assert _FakeBemClient.last_init == {"api_key": "key-local", "base_url": "https://api.bem.ai"}
    assert _FakeBemClient.last_submit is not None
    assert _FakeBemClient.last_submit["workflow_id"] == "wf-local"


def test_precedencia_cli_sobre_env_y_env_local(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"a":1}', encoding="utf-8")
    (tmp_path / ".env.local").write_text(
        "BEM_WORKFLOW_ID=wf-local\nBEM_API_KEY=key-local\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BEM_WORKFLOW_ID", "wf-env")
    monkeypatch.setenv("BEM_API_KEY", "key-env")
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(
        [
            "--workflow-id",
            "wf-cli",
            "--payload-file",
            str(payload_file),
            "--api-key",
            "key-cli",
        ]
    )

    assert code == 0
    assert _FakeBemClient.last_init == {"api_key": "key-cli", "base_url": "https://api.bem.ai"}
    assert _FakeBemClient.last_submit is not None
    assert _FakeBemClient.last_submit["workflow_id"] == "wf-cli"


def test_falla_si_falta_api_key(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"a":1}', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BEM_API_KEY", raising=False)
    monkeypatch.delenv("BEM_WORKFLOW_ID", raising=False)
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)

    code = cli.run(["--workflow-id", "wf", "--payload-file", str(payload_file)])
    err = capsys.readouterr().err
    assert code == 2
    assert "api_key is required" in err


def test_no_imprime_api_key_en_error(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr(cli, "BemClient", _FakeBemClient)
    code = cli.run(["--workflow-id", "wf", "--payload-file", str(payload_file), "--api-key", "SECRET123"])
    err = capsys.readouterr().err
    assert code == 1
    assert "SECRET123" not in err
