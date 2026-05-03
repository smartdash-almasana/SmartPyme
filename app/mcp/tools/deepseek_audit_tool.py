from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "factory" / "evidence" / "deepseek_audit"
DEFAULT_MODEL = "gemma4:e2b"


def _safe_relative_path(raw_path: str) -> Path:
    candidate = (REPO_ROOT / raw_path).resolve()
    if not str(candidate).startswith(str(REPO_ROOT.resolve())):
        raise ValueError(f"path_outside_repo: {raw_path}")
    if not candidate.exists():
        raise FileNotFoundError(f"file_not_found: {raw_path}")
    if not candidate.is_file():
        raise ValueError(f"not_a_file: {raw_path}")
    return candidate


def _audit_dir(task_id: str, output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    safe_task_id = "".join(ch for ch in task_id if ch.isalnum() or ch in "-_")
    if not safe_task_id:
        raise ValueError("invalid_task_id")
    return output_root / safe_task_id


def run_deepseek_audit(
    task_id: str,
    files: list[str],
    objective: str,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = 900,
) -> dict[str, Any]:
    """Run a local DeepSeek audit and persist the result as factory evidence."""
    target_dir = _audit_dir(task_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    resolved_files = [_safe_relative_path(path) for path in files]
    files_reviewed = [str(path.relative_to(REPO_ROOT)) for path in resolved_files]

    prompt_parts = [
        "Audita los siguientes archivos del repo SmartPyme.",
        "Responde en castellano operativo.",
        "No propongas editar codigo directamente.",
        "Devuelve secciones: TASK_ID, OBJETIVO, ARCHIVOS_REVISADOS, HALLAZGOS, RIESGOS, RECOMENDACION, VEREDICTO.",
        "VEREDICTO debe ser PASS, PARTIAL o BLOCKED.",
        f"TASK_ID: {task_id}",
        f"OBJETIVO: {objective}",
    ]

    for path in resolved_files:
        rel = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")
        prompt_parts.append(f"\n--- FILE: {rel} ---\n{text[:50000]}")

    prompt = "\n".join(prompt_parts)

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        cwd=str(REPO_ROOT),
        check=False,
    )

    audit_text = result.stdout.strip()
    stderr_text = result.stderr.strip()

    if result.returncode != 0:
        verdict = "BLOCKED"
        audit_text = audit_text or f"DeepSeek audit failed: {stderr_text}"
    else:
        upper = audit_text.upper()
        if "VEREDICTO: PASS" in upper or "\nPASS\n" in upper:
            verdict = "PASS"
        elif "VEREDICTO: BLOCKED" in upper or "\nBLOCKED\n" in upper:
            verdict = "BLOCKED"
        else:
            verdict = "PARTIAL"

    (target_dir / "audit_report.md").write_text(audit_text + "\n", encoding="utf-8")
    (target_dir / "verdict.txt").write_text(verdict + "\n", encoding="utf-8")
    (target_dir / "files_reviewed.txt").write_text("\n".join(files_reviewed) + "\n", encoding="utf-8")

    return {
        "status": "AUDIT_COMPLETED" if result.returncode == 0 else "AUDIT_BLOCKED",
        "source": "deepseek_local",
        "task_id": task_id,
        "model": model,
        "verdict": verdict,
        "output_dir": str(target_dir.relative_to(REPO_ROOT)),
        "audit_report": str((target_dir / "audit_report.md").relative_to(REPO_ROOT)),
        "verdict_file": str((target_dir / "verdict.txt").relative_to(REPO_ROOT)),
        "files_reviewed_file": str((target_dir / "files_reviewed.txt").relative_to(REPO_ROOT)),
        "files_reviewed": files_reviewed,
    }
