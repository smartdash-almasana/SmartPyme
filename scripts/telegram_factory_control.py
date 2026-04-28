from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "factory" / "control" / "AUDIT_GATE.md"
STATUS = REPO / "factory" / "control" / "FACTORY_STATUS.md"
OFFSET_FILE = REPO / "factory" / "control" / ".telegram_control_offset"
TASKS_DIR = REPO / "factory" / "ai_governance" / "tasks"
TRIGGER = REPO / "scripts" / "telegram_trigger_cycle.py"
LOCK = REPO / "factory" / "control" / ".telegram_cycle_lock"

BUTTONS = {
    "SEGUIR": "/seguir",
    "PAUSAR": "/pausar",
    "CORREGIR": "/corregir",
    "ESTADO": "/estado",
    "TAREAS": "/tareas",
}


def env(name: str) -> str:
    return os.getenv(name, "").strip()


def token() -> str:
    value = env("TELEGRAM_BOT_TOKEN")
    if not value:
        raise RuntimeError("missing TELEGRAM_BOT_TOKEN")
    return value


def allowed_chat_id() -> str:
    value = env("TELEGRAM_CHAT_ID")
    if not value:
        raise RuntimeError("missing TELEGRAM_CHAT_ID")
    return value


def api(method: str, payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.telegram.org/bot" + token() + "/" + method,
        data=data,
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read().decode("utf-8"))


def control_keyboard() -> str:
    return json.dumps({"inline_keyboard": [
        [{"text": "▶ Seguir", "callback_data": "SEGUIR"}, {"text": "⏸️ Pausar", "callback_data": "PAUSAR"}],
        [{"text": "🔁 Corregir", "callback_data": "CORREGIR"}, {"text": "📊 Estado", "callback_data": "ESTADO"}],
        [{"text": "🧭 Tareas", "callback_data": "TAREAS"}],
    ]})


def send(text: str, buttons: bool = True) -> None:
    payload = {"chat_id": allowed_chat_id(), "text": text[:3900]}
    if buttons:
        payload["reply_markup"] = control_keyboard()
    api("sendMessage", payload)


def answer_callback(callback_id: str) -> None:
    api("answerCallbackQuery", {"callback_query_id": callback_id})


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_offset() -> int:
    try:
        return int(OFFSET_FILE.read_text().strip())
    except Exception:
        return 0


def write_offset(value: int) -> None:
    OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(str(value), encoding="utf-8")


def _read_status_file() -> dict[str, str]:
    data: dict[str, str] = {}
    if not STATUS.exists():
        return data
    for line in STATUS.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def gate_status() -> str:
    if not GATE.exists():
        return "APPROVED"
    for line in GATE.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip().upper()
    return "UNKNOWN"


def write_gate(status: str, reason: str) -> None:
    GATE.parent.mkdir(parents=True, exist_ok=True)
    previous = gate_status()
    GATE.write_text(
        "# AUDIT GATE\n\n"
        f"status: {status}\n"
        f"updated_at: {now()}\n"
        "updated_by: telegram_control\n"
        f"previous_status: {previous}\n"
        f"reason: {reason}\n",
        encoding="utf-8",
    )


def trigger_cycle() -> str:
    if LOCK.exists():
        return "Ya hay un ciclo en ejecución. No disparo otro para evitar iteración repetida."
    if not TRIGGER.exists():
        return "No encuentro scripts/telegram_trigger_cycle.py. No puedo disparar el ciclo."
    subprocess.Popen([sys.executable, str(TRIGGER)], cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return "OK: ciclo solicitado. Hará pull de GitHub y ejecutará una sola vuelta de Hermes."


def status_text() -> str:
    data = _read_status_file()
    gate = gate_status()
    return "\n".join([
        "📊 Estado de SmartPyme Factory", "",
        f"Decisión actual: {gate}",
        f"Último resultado: {data.get('last_cycle_result', 'no informado')}",
        f"Última actualización: {data.get('updated_at', 'no informada')}",
        f"Detalle para GPT: {data.get('last_error', 'sin detalle')}", "",
        "Botones:",
        "- ▶ Seguir: hacer pull y ejecutar una vuelta.",
        "- ⏸️ Pausar: mantener detenido.",
        "- 🔁 Corregir: reabrir la última tarea.",
        "- 🧭 Tareas: ver tareas activas.",
    ])


def _read_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def tasks_text() -> str:
    if not TASKS_DIR.exists():
        return "No encuentro la carpeta de tareas de la factoría."
    tasks = []
    for path in sorted(TASKS_DIR.glob("*.yaml")):
        data = _read_simple_yaml(path)
        if data.get("status", "").lower() in {"pending", "in_progress"}:
            tasks.append((path, data))
    if not tasks:
        return "No hay tareas pendientes o en ejecución."
    lines = ["🧭 Tareas preparadas o en curso", ""]
    for idx, (path, data) in enumerate(tasks[:5], start=1):
        lines.extend([
            f"{idx}. {data.get('task_id', path.stem)}",
            f"Estado: {data.get('status', 'no informado')}",
            f"Trazabilidad: {path.relative_to(REPO)}", "",
        ])
    return "\n".join(lines).strip()


def handle_command(text: str) -> str:
    cmd = text.strip().split()[0].lower() if text.strip() else ""
    if cmd in {"/seguir", "/run", "/go"}:
        return trigger_cycle()
    if cmd in {"/pausar", "/stop"}:
        write_gate("BLOCKED", cmd)
        return "OK: pausado. La factoría queda frenada."
    if cmd in {"/corregir", "/retry"}:
        write_gate("REJECTED", cmd)
        return "OK: rechazado. El runner reabrirá la última tarea para corregirla."
    if cmd in {"/estado", "/status"}:
        return status_text()
    if cmd in {"/tareas", "/tasks"}:
        return tasks_text()
    if cmd in {"/help", "help", "/panel"}:
        return "SmartPyme Control\n\nUsá: /seguir, /pausar, /corregir, /estado, /tareas"
    return "Comando no reconocido. Usá /panel."


def handle_callback(data: str) -> str:
    return handle_command(BUTTONS.get(data, "")) if data in BUTTONS else "Botón no reconocido."


def poll_once() -> None:
    offset = read_offset()
    payload = {"timeout": 25, "allowed_updates": json.dumps(["message", "callback_query"])}
    if offset:
        payload["offset"] = offset
    result = api("getUpdates", payload)
    for update in result.get("result", []):
        write_offset(int(update["update_id"]) + 1)
        callback = update.get("callback_query")
        if callback:
            message = callback.get("message") or {}
            chat_id = str((message.get("chat") or {}).get("id", ""))
            if chat_id != allowed_chat_id():
                continue
            answer_callback(callback.get("id", ""))
            send(handle_callback(callback.get("data", "")))
            continue
        message = update.get("message") or {}
        chat_id = str((message.get("chat") or {}).get("id", ""))
        if chat_id != allowed_chat_id():
            continue
        send(handle_command(message.get("text", "")))


def main() -> None:
    send("SmartPyme Control activo. Usá los botones.")
    while True:
        try:
            poll_once()
        except Exception as exc:
            print(f"TELEGRAM_CONTROL_ERROR {type(exc).__name__}: {exc}", flush=True)
            time.sleep(10)


if __name__ == "__main__":
    main()
