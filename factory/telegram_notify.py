from __future__ import annotations

import json
import os
import re
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


def _read_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
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
        if value in {">", "|", "|-", ">-"}:
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


def _task_path(last_task: str) -> Path | None:
    if not last_task or last_task in {"none", "no informado"}:
        return None
    candidate = (REPO / last_task).resolve()
    try:
        candidate.relative_to(REPO)
    except ValueError:
        return None
    return candidate if candidate.exists() else None


def _pick(data: dict[str, str], *keys: str, default: str = "dato no informado") -> str:
    for key in keys:
        value = data.get(key, "").strip()
        if value:
            return value
    return default


def _infer_product_area(task: str, evidence: str, task_data: dict[str, str]) -> str:
    declared = _pick(task_data, "product_area", "area", "module", "modulo", "layer", "capa", default="")
    if declared:
        return declared
    text = f"{task} {evidence} {_pick(task_data, 'objective', default='')}".lower()
    if "telegram" in text:
        return "control Telegram / experiencia del owner"
    if "ocr" in text or "remito" in text or "ticket" in text:
        return "ingesta documental / OCR"
    if "polars" in text or "polar" in text:
        return "procesamiento tabular / Polars"
    if "priority" in text or "prioridad" in text:
        return "orquestacion de tareas / priorizacion"
    if "contract" in text or "doc" in text or "alignment" in text:
        return "gobernanza documental / contrato de factoria"
    if "reconciliacion" in text or "reconciliation" in text:
        return "core de reconciliacion / hallazgos"
    if "audit" in text:
        return "auditoria y evidencia"
    return "dato no informado en la tarea"


def _progress_label(event_status: str, gate: dict[str, str], task_data: dict[str, str]) -> str:
    explicit = _pick(task_data, "progress_pct", "roadmap_progress_pct", "avance_pct", default="")
    if explicit:
        return f"{explicit}% informado por la tarea"

    code = gate.get("last_returncode", "").strip()
    task_status = task_data.get("status", "").strip().lower()
    event_status = event_status.upper()

    if event_status == "CYCLE_START":
        return "0% — chequeo inicial; no hubo cambios"
    if event_status == "TASK_DISPATCH":
        return "25% — tarea tomada por la factoria"
    if event_status == "TASK_DONE":
        return "75% — tarea marcada como terminada; falta cierre y auditoria"
    if event_status in {"CYCLE_OK", "AUTO_PUSH_OK"}:
        return "100% — ciclo finalizado sin error reportado"
    if event_status == "CYCLE_FAIL":
        return "fallido — ciclo con error; requiere revision"
    if event_status == "AUDIT_BLOCKED" and code == "0" and task_status == "done":
        return "100% — ultimo ciclo finalizado con exito; esperando auditoria humana"
    if event_status == "AUDIT_BLOCKED" and code and code != "0":
        return "fallido — ultimo ciclo cerro con error; esperando decision humana"
    if event_status == "AUDIT_BLOCKED":
        return "en pausa — no hay dato suficiente del porcentaje del ultimo ciclo"
    return "dato no informado"


def _audit_card(event_status: str) -> str:
    gate = _read_kv_file(GATE_FILE)
    status = _read_kv_file(STATUS_FILE)
    last_task = gate.get("last_task", "no informado")
    task_file = _task_path(last_task)
    task_data = _read_simple_yaml(task_file) if task_file else {}

    last_result = status.get("last_cycle_result", "no informado")
    last_error = status.get("last_error", "none")
    evidence = _last_evidence_name()
    area = _infer_product_area(last_task, evidence, task_data)
    git_status = _git(["status", "--short"])
    last_commit = _git(["log", "--oneline", "-1"])
    changed = "no" if not git_status else "si"

    objective = _pick(task_data, "product_goal", "business_goal", "objective", default="dato no informado en la tarea")
    product_outcome = _pick(
        task_data,
        "product_outcome",
        "expected_product_outcome",
        "resultado_producto",
        "impacto_producto",
        default="dato no informado en la tarea",
    )
    roadmap_ref = _pick(
        task_data,
        "roadmap_ref",
        "roadmap_step",
        "roadmap",
        "fase",
        default="dato no informado en la tarea",
    )
    progress = _progress_label(event_status, gate, task_data)

    if "fallido" in progress or "FAIL" in last_result or last_error not in {"none", "cycle closed", ""}:
        decision = "No aprobar sin revisar. Usar Ver estado o Rechazar y corregir."
    elif progress.startswith("100%"):
        decision = "Se puede aprobar si la evidencia coincide con el objetivo declarado."
    else:
        decision = "Usar Ver estado antes de aprobar."

    return (
        "Tarjeta de auditoria del producto:\n"
        f"- Capa/modulo: {area}\n"
        f"- Tarea: {last_task}\n"
        f"- Objetivo del ciclo: {objective}\n"
        f"- Resultado esperado en producto: {product_outcome}\n"
        f"- Avance: {progress}\n"
        f"- Roadmap/trazabilidad: {roadmap_ref}\n"
        f"- Evidencia: {evidence}\n"
        f"- Resultado tecnico: {last_result}\n"
        f"- Codigo pendiente sin guardar: {changed}\n"
        f"- Ultimo commit: {last_commit or 'no informado'}\n\n"
        f"Decision sugerida: {decision}"
    )


def _reserved_for_gpt(status: str, details: str = "") -> str:
    gate = _read_kv_file(GATE_FILE)
    status_file = _read_kv_file(STATUS_FILE)
    lines = [
        f"estado={status.strip().upper()}",
        f"gate={gate.get('status', 'UNKNOWN')}",
        f"last_task={gate.get('last_task', 'none')}",
        f"last_returncode={gate.get('last_returncode', 'unknown')}",
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
            "SmartPyme Factory esta pausada para auditoria del producto.\n\n"
            f"{_audit_card(status_key)}\n\n"
            "Botones:\n"
            "✅ Aprobar y seguir: aceptar el ciclo si la evidencia coincide con el objetivo.\n"
            "🔁 Rechazar y corregir: reabrir la tarea si el resultado no cumple.\n"
            "⏸️ Pausar: no ejecutar nada por ahora.\n"
            "📊 Ver estado: pedir mas informacion antes de decidir."
        )
    elif status_key == "TASK_DISPATCH":
        text = (
            "SmartPyme Factory empezo una tarea aprobada.\n\n"
            f"{_audit_card(status_key)}\n\n"
            "No tenes que responder ahora; espera el cierre del ciclo."
        )
    elif status_key == "TASK_DONE":
        text = (
            "SmartPyme Factory termino una tarea.\n\n"
            f"{_audit_card(status_key)}\n\n"
            "Falta cierre del ciclo y auditoria humana."
        )
    elif status_key == "CYCLE_OK":
        text = (
            "SmartPyme Factory termino el ciclo sin errores reportados.\n\n"
            f"{_audit_card(status_key)}\n\n"
            "Usa los botones para aprobar, corregir, pausar o revisar estado."
        )
    elif status_key == "CYCLE_FAIL":
        text = (
            "SmartPyme Factory encontro un problema durante el ciclo.\n\n"
            f"{_audit_card(status_key)}\n\n"
            "Recomendacion: Ver estado o Pausar. No aprobar sin revisar evidencia."
        )
    elif status_key == "AUTO_PUSH_OK":
        text = (
            "SmartPyme Factory guardo cambios en el repo.\n\n"
            f"{_audit_card(status_key)}\n\n"
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
