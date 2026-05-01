from __future__ import annotations

from factory import hermes_control_cli as control


def test_seleccionar_task_pending(tmp_path):
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


def test_extraer_campo_estado_lee_solo_campo_exacto():
    texto = """# FACTORY STATUS
updated_at: 2026-04-28T12:47:21+00:00
last_cycle_result: AUDIT_GATE_BLOCKING
audit_gate: BLOCKED
last_error: antiguo_bloqueo
estado: OPEN
"""
    assert control.extraer_campo_estado(texto, "estado") == "OPEN"
    assert control.extraer_campo_estado(texto, "status") is None


def test_estado_bloqueante_actual_ignora_bloqueos_historicos(tmp_path):
    repo = tmp_path / "SmartPyme"
    control_dir = repo / "factory/control"
    control_dir.mkdir(parents=True)
    (control_dir / "AUDIT_GATE.md").write_text("status: OPEN\n", encoding="utf-8")
    (control_dir / "FACTORY_STATUS.md").write_text(
        (
            "last_cycle_result: AUDIT_GATE_BLOCKING\n"
            "audit_gate: BLOCKED\n"
            "last_error: antiguo_bloqueo\n"
        ),
        encoding="utf-8",
    )

    assert control.estado_bloqueante_actual(repo) is None


def test_estado_bloqueante_actual_detecta_estado_actual(tmp_path):
    repo = tmp_path / "SmartPyme"
    control_dir = repo / "factory/control"
    control_dir.mkdir(parents=True)
    (control_dir / "AUDIT_GATE.md").write_text("status: OPEN\n", encoding="utf-8")
    (control_dir / "FACTORY_STATUS.md").write_text("estado: PAUSED\n", encoding="utf-8")

    assert control.estado_bloqueante_actual(repo) == "PAUSED"
