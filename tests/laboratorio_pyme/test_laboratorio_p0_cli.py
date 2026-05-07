from __future__ import annotations

import json

from app.laboratorio_pyme.p0_runner import LaboratorioP0Result
from scripts import laboratorio_p0_cli as cli


def test_parse_alias_diagnostico_operativo() -> None:
    parsed = cli._parse_laboratorio_arg("diagnostico_operativo")
    assert parsed == "diagnostico_operativo"


def test_run_cli_emite_json_y_llama_runner(monkeypatch, capsys) -> None:
    called = {"count": 0}

    def _fake_runner(**kwargs):
        called["count"] += 1
        return LaboratorioP0Result(
            cliente_id="cliente_demo",
            case_id="case-1",
            job_id="job-1",
            report_id="rep-1",
            status="closed",
        )

    monkeypatch.setattr(cli, "run_laboratorio_p0", _fake_runner)
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
    assert called["count"] == 1

    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert data == {
        "cliente_id": "cliente_demo",
        "case_id": "case-1",
        "job_id": "job-1",
        "report_id": "rep-1",
        "status": "closed",
    }

