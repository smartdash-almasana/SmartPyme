from __future__ import annotations

import os
from pathlib import Path

from factory import hermes_control_cli as control


def test_seleccionar_task_pending(tmp_path, monkeypatch):
    repo = tmp_path / "SmartPyme"
    tasks = repo / "factory/ai_governance/tasks"
    tasks.mkdir(parents=True)
    (tasks / "z_done.yaml").write_text("task_id: z_done\nstatus: validated\n", encoding="utf-8")
    pending = tasks / "a_pending.yaml"
    pending.write_text("task_id: a_pending\nstatus: pending\n", encoding="utf-8")

    assert control.seleccionar_task_pending(repo) == str(pending)


def test_escribir_estado_crea_factory_status(tmp_path):
    repo = tmp_path / "SmartPyme"
    path = control.escribir_estado(repo, "PAUSED", "prueba")

    assert path == repo / "factory/control/FACTORY_STATUS.md"
    texto = path.read_text(encoding="utf-8")
    assert "estado: PAUSED" in texto
    assert "motivo: prueba" in texto


def test_comando_pausar_usa_repo_configurado(tmp_path, monkeypatch):
    repo = tmp_path / "SmartPyme"
    repo.mkdir()
    monkeypatch.setenv("SMARTPYME_REPO", str(repo))

    resultado = control.comando_pausar()

    assert resultado.comando_recibido == "/pausar"
    assert resultado.decision == "OK"
    assert str(repo / "factory/control/FACTORY_STATUS.md") == resultado.evidencia_generada
    assert "PAUSED" in (repo / "factory/control/FACTORY_STATUS.md").read_text(encoding="utf-8")


def test_contiene_estado_bloqueante():
    assert control.contiene_estado_bloqueante("estado: WAITING_AUDIT") == "WAITING_AUDIT"
    assert control.contiene_estado_bloqueante("todo abierto") is None
