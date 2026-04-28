from __future__ import annotations

import json
import os
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

BUTTONS = {
    "GO": "/run",
    "STOP": "/stop",
    "FIX": "/retry",
    "STATUS": "/status",
    "TASKS": "/tasks",
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
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "▶ Seguir", "callback_data": "GO"},
                    {"text": "⏸️ Pausar", "callback_data": "STOP"},
                ],
                [
                    {"text": "🔁 Corregir", "callback_data": "FIX"},
                    {"text": "📊 Estado", "callback_data": "STATUS"},
                ],
                [
                    {"text": "🧭 En curso", "callback_data": "TASKS"},
                ],
            ]
        }
    )


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
        f"updated_by: telegram_control\n"
        f"previous_status: {previous}\n"
        f"reason: {reason}\n",
        encoding="utf-8",
    )


def status_text() -> str:
    lines = ["SmartPyme Factory", f"gate: {gate_status()}"]
    if STATUS.exists():
        text = STATUS.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if line.startswith(("updated_at:", "last_cycle_result:", "audit_gate:", "last_error:")):
                lines.append(line)
    return "\n".join(lines)


def _read_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if value in {">", "|", ">-", "|-"}:
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                if lines[i].strip():
                    block.append(lines[i].strip())
                i += 1
            data[key] = " ".join(block).strip()
            continue
        data[key] = value
        i += 1
    return data


def _pick(data: dict[str, str], *keys: str, default: str = "no informado") -> str:
    for key in keys:
        value = data.get(key, "").strip()
        if value:
            return value
    return default


def tasks_text() -> str:
    if not TASKS_DIR.exists():
        return "No encuentro la carpeta de tareas de la factoría."

    tasks = []
    for path in sorted(TASKS_DIR.glob("*.yaml")):
        data = _read_simple_yaml(path)
        status = data.get("status", "").lower()
        if status in {"pending", "in_progress"}:
            tasks.append((path, data))

    if not tasks:
        return "No hay tareas pendientes o en ejecución."

    lines = ["🧭 Qué está preparado o en curso", ""]
    for idx, (path, data) in enumerate(tasks[:5], start=1):
        title = _pick(data, "title", "task_id", default=path.stem)
        status = _pick(data, "status")
        objective = _pick(data, "objective", "product_frame", default="sin descripción")
        product = _pick(data, "product_frame", "product_goal", "product_final_target", default="SmartPyme Factory")
        agents = _pick(data, "agents", default="Hermes coordina; Gemini analiza; Codex valida cuando corresponde")
        lines.extend(
            [
                f"{idx}. {title}",
                f"Estado: {status}",
                f"Para qué sirve: {product[:280]}",
                f"Qué se hace: {objective[:420]}",
                f"Agentes: {agents[:220]}",
                f"Trazabilidad: {path.relative_to(REPO)}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def handle_command(text: str) -> str:
    cmd = text.strip().split()[0].lower() if text.strip() else ""
    if cmd in {"/run", "/start", "/approve", "/go", "/seguir"}:
        write_gate("APPROVED", cmd)
        return "OK: aprobado. La factoría puede ejecutar el próximo ciclo."
    if cmd in {"/stop", "/block", "/kill", "/frenar", "/pausar"}:
        write_gate("BLOCKED", cmd)
        return "OK: pausado. La factoría queda frenada."
    if cmd in {"/retry", "/reject", "/fix", "/reprocesar", "/corregir"}:
        write_gate("REJECTED", cmd)
        return "OK: rechazado. El runner reabrirá la última tarea para corregirla."
    if cmd in {"/status", "/state", "/s", "/estado"}:
        return status_text()
    if cmd in {"/tasks", "/tareas", "/encurso", "/en_curso"}:
        return tasks_text()
    if cmd in {"/help", "help", "/panel"}:
        return "SmartPyme Control\n\nUsá los botones o comandos: /go, /pausar, /corregir, /estado, /tareas"
    return "Comando no reconocido. Usá los botones o /panel."


def handle_callback(data: str) -> str:
    command = BUTTONS.get(data, "")
    if not command:
        return "Botón no reconocido."
    return handle_command(command)


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
            chat = message.get("chat") or {}
            chat_id = str(chat.get("id", ""))
            if chat_id != allowed_chat_id():
                continue
            answer_callback(callback.get("id", ""))
            reply = handle_callback(callback.get("data", ""))
            send(reply)
            continue

        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = str(chat.get("id", ""))
        text = message.get("text", "")
        if chat_id != allowed_chat_id():
            continue
        reply = handle_command(text)
        send(reply)


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
