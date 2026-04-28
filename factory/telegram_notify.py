from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTROL = REPO / "factory" / "control"
GATE_FILE = CONTROL / "AUDIT_GATE.md"
STATUS_FILE = CONTROL / "FACTORY_STATUS.md"
EVIDENCE_DIR = REPO / "factory" / "evidence"


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _read_kv_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def _git(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        return (result.stdout or result.stderr).strip()
    except Exception as exc:
        return f"git no disponible: {type(exc).__name__}"


def _last_evidence_name() -> str:
    if not EVIDENCE_DIR.exists():
        return "sin evidencia encontrada"
    dirs = [p for p in EVIDENCE_DIR.iterdir() if p.is_dir()]
    if not dirs:
        return "sin evidencia encontrada"
    latest = max(dirs, key=lambda p: p.stat().st_mtime)
    return latest.name


def _infer_product_area(task: str, evidence: str) -> str:
    text = f"{task} {evidence}".lower()
    if "telegram" in text:
        return "control Telegram / experiencia del owner"
    if "priority" in text or "prioridad" in text:
        return "orquestacion de tareas / priorizacion"
    if "contract" in text or "doc" in text or "alignment" in text:
        return "gobernanza documental / contrato de factoria"
    if "reconciliacion" in text or "reconciliation" in text:
        return "core de reconciliacion / hallazgos"
    if "audit" in text:
        return "auditoria y evidencia"
    return "factoria SmartPyme"


def _audit_card() -> str:
    gate = _read_kv_file(GATE_FILE)
    status = _read_kv_file(STATUS_FILE)
    last_task = gate.get("last_task", "no informado")
    last_result = status.get("last_cycle_result", "no informado")
    last_error = status.get("last_error", "none")
    evidence = _last_evidence_name()
    area = _infer_product_area(last_task, evidence)
    git_status = _git(["status", "--short"])
    last_commit = _git(["log", "--oneline", "-1"])
    changed = "no" if not git_status else "si"

    if last_result in {"WAITING_AUDIT", "CYCLE_OK", "RUNNING"} and last_error in {"none", "cycle closed", ""}:
        interpretation = "El ciclo anterior parece cerrado sin error critico reportado por la factoria."
        suggested = "Sugerencia: toca Ver estado si queres revisar evidencia; toca Aprobar y seguir si ya confias en el ultimo ciclo."
    elif "FAIL" in last_result or last_error not in {"none", "cycle closed", ""}:
        interpretation = "El ciclo anterior reporta problema o error pendiente."
        suggested = "Sugerencia: toca Ver estado o Pausar. No apruebes sin revisar evidencia."
    else:
        interpretation = "No hay suficiente informacion resumida para recomendar aprobar."
        suggested = "Sugerencia: toca Ver estado antes de decidir."

    return (
        "Resumen del ciclo que estas auditando:\n"
        f"- Area de producto: {area}\n"
        f"- Ultima tarea: {last_task}\n"
        f"- Resultado anterior: {last_result}\n"
        f"- Evidencia reciente: {evidence}\n"
        f"- Codigo pendiente sin guardar: {changed}\n"
        f"- Ultimo commit: {last_commit or 'no informado'}\n\n"
        f"Lectura: {interpretation}\n"
        f"{suggested}"
    )


def _reserved_for_gpt(status: str, details: str = "") -> str:
    gate = _read_kv_file(GATE_FILE)
    status_file = _read_kv_file(STATUS_FILE)
    lines = [
        f"estado={status.strip().upper()}",
        f"gate={gate.get('status', 'UNKNOWN')}",
        f"last_task={gate.get('last_task', 'none')}",
        f"last_cycle_result={status_file.get('last_cycle_result', 'unknown')}",
        f"last_error={status_file.get('last_error', 'unknown')}",
    ]
    if details.strip():
        lines.extend(line.strip() for line in details.splitlines() if line.strip())
    return "\n\nReservado a GPT:\n" + "\n".join(f"- {line}" for line in lines[:12])


def _decision_keyboard() -> str:
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "✅ Aprobar y seguir", "callback_data": "GO"},
                    {"text": "🔁 Rechazar y corregir", "callback_data": "FIX"},
                ],
                [
                    {"text": "⏸️ Pausar", "callback_data": "STOP"},
                    {"text": "📊 Ver estado", "callback_data": "STATUS"},
                ],
            ]
        }
    )


def _needs_decision_buttons(status_key: str) -> bool:
    return status_key in {"AUDIT_BLOCKED", "CYCLE_OK", "CYCLE_FAIL", "AUTO_PUSH_OK"}


def format_cycle_message(status: str, details: str = "") -> str:
    status_key = status.strip().upper()

    if status_key == "CYCLE_START":
        text = (
            "SmartPyme Factory esta activa.\n\n"
            "Estoy verificando si corresponde trabajar en una nueva mejora del producto. "
            "Esto es solo un chequeo: todavia no se modifico codigo."
        )
    elif status_key == "AUDIT_BLOCKED":
        text = (
            "SmartPyme Factory esta pausada para que decidas con control.\n\n"
            f"{_audit_card()}\n\n"
            "Botones disponibles:\n"
            "✅ Aprobar y seguir: aceptar el ultimo ciclo y permitir la proxima mejora.\n"
            "🔁 Rechazar y corregir: reabrir la ultima tarea para correccion.\n"
            "⏸️ Pausar: no ejecutar nada por ahora.\n"
            "📊 Ver estado: pedir mas informacion antes de decidir.\n\n"
            "Seguridad: no se ejecuto ninguna tarea nueva mientras esperabas decidir."
        )
    elif status_key == "TASK_DISPATCH":
        text = (
            "SmartPyme Factory empezo una tarea aprobada.\n\n"
            f"Area probable: {_infer_product_area(details, details)}.\n"
            "No tenes que responder ahora; espera el cierre del ciclo."
        )
    elif status_key == "TASK_DONE":
        text = (
            "SmartPyme Factory termino una tarea.\n\n"
            "Ahora falta revisar evidencia del cambio antes de permitir otra mejora."
        )
    elif status_key == "CYCLE_OK":
        text = (
            "SmartPyme Factory termino el ciclo sin errores reportados.\n\n"
            f"{_audit_card()}\n\n"
            "Usa los botones para aprobar, corregir, pausar o revisar estado."
        )
    elif status_key == "CYCLE_FAIL":
        text = (
            "SmartPyme Factory encontro un problema durante el ciclo.\n\n"
            f"{_audit_card()}\n\n"
            "Recomendacion: Ver estado o Pausar. No aprobar sin revisar evidencia."
        )
    elif status_key == "AUTO_PUSH_OK":
        text = (
            "SmartPyme Factory guardo cambios en el repo.\n\n"
            f"{_audit_card()}\n\n"
            "Hay un commit nuevo para auditar antes de permitir otra mejora."
        )
    elif status_key == "NO_TASK":
        text = (
            "SmartPyme Factory no encontro tareas pendientes.\n\n"
            "El sistema esta activo, pero no tiene una mejora de producto lista para ejecutar."
        )
    else:
        text = (
            "SmartPyme Factory envio una actualizacion.\n\n"
            "La parte reservada a GPT contiene el detalle tecnico para interpretar el evento."
        )

    return text + _reserved_for_gpt(status_key, details)


def send_telegram_message(text: str, reply_markup: str | None = None) -> bool:
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_NOTIFY_SKIPPED missing env")
        return False

    payload = {
        "chat_id": chat_id,
        "text": text[:3900],
        "disable_web_page_preview": "true",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    data = urllib.parse.urlencode(payload).encode("utf-8")

    req = urllib.request.Request(
        "https://api.telegram.org/bot" + token + "/sendMessage",
        data=data,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"TELEGRAM_NOTIFY_STATUS {resp.status}")
            return 200 <= resp.status < 300
    except Exception as exc:
        print(f"TELEGRAM_NOTIFY_FAILED {type(exc).__name__}: {exc}")
        return False


def notify_cycle_result(status: str, details: str = "") -> bool:
    status_key = status.strip().upper()
    buttons = _decision_keyboard() if _needs_decision_buttons(status_key) else None
    return send_telegram_message(format_cycle_message(status, details), buttons)
