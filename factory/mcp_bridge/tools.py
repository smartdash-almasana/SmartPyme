from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Callable


ALLOWED_HALLAZGO_STATES = {"pending", "in_progress", "done", "blocked"}


def register_tools(
    mcp,
    *,
    repo_root: Path,
    client_name: str,
    log_path: Path,
) -> None:
    """Register SmartPyme local tools in a FastMCP server."""

    repo_root = repo_root.resolve()
    log_path = log_path.resolve()
    logger = logging.getLogger("SmartPyme-Bridge-Audit")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    def _log(event: dict) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _trace(tool_name: str) -> Callable:
        def decorator(fn: Callable) -> Callable:
            @wraps(fn)
            def wrapper(*args, **kwargs):
                started = time.perf_counter()
                utc_ts = datetime.now(timezone.utc).isoformat()
                ok = True
                error = None
                safe_params = json.dumps(kwargs, ensure_ascii=False, default=str)
                logger.info("[%s] CALLING TOOL: %s | PARAMS: %s", client_name, tool_name, safe_params)
                try:
                    result = fn(*args, **kwargs)
                    return result
                except Exception as exc:  # fail-closed logging
                    ok = False
                    error = str(exc)
                    logger.error("[%s] ERROR in %s: %s", client_name, tool_name, error)
                    raise
                finally:
                    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
                    if ok:
                        logger.info("[%s] SUCCESS: %s | ELAPSED_MS: %s", client_name, tool_name, elapsed_ms)
                    _log(
                        {
                            "ts": utc_ts,
                            "client": client_name,
                            "tool": tool_name,
                            "ok": ok,
                            "elapsed_ms": elapsed_ms,
                            "error": error,
                        }
                    )

            return wrapper

        return decorator

    def _safe_path(raw_path: str) -> Path:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (repo_root / candidate).resolve()
        else:
            candidate = candidate.resolve()
        try:
            candidate.relative_to(repo_root)
        except ValueError as exc:
            raise ValueError(f"PATH_FORBIDDEN: {raw_path}") from exc
        return candidate

    def _hallazgos_base() -> Path:
        return repo_root / "factory" / "hallazgos"

    def _find_hallazgo_file(hallazgo_id: str) -> Path:
        if not hallazgo_id or not hallazgo_id.strip():
            raise ValueError("HALLAZGO_ID_INVALIDO")
        base = _hallazgos_base()
        for state in ALLOWED_HALLAZGO_STATES:
            state_dir = base / state
            if not state_dir.exists():
                continue
            for file_path in state_dir.glob("*.md"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                except OSError:
                    continue
                marker = f"- id: {hallazgo_id}"
                if marker in content:
                    return file_path
        raise FileNotFoundError(f"HALLAZGO_NO_ENCONTRADO: {hallazgo_id}")

    @mcp.tool()
    @_trace("read_file")
    def read_file(path: str) -> str:
        """Lee un archivo dentro de SmartPyme."""
        safe = _safe_path(path)
        if not safe.exists() or not safe.is_file():
            raise FileNotFoundError(f"FILE_NOT_FOUND: {path}")
        return safe.read_text(encoding="utf-8")

    @mcp.tool()
    @_trace("list_files")
    def list_files(directory: str = ".") -> list[str]:
        """Lista archivos y carpetas dentro de SmartPyme."""
        safe_dir = _safe_path(directory)
        if not safe_dir.exists() or not safe_dir.is_dir():
            raise FileNotFoundError(f"DIRECTORY_NOT_FOUND: {directory}")
        return sorted([entry.name for entry in safe_dir.iterdir()])

    @mcp.tool()
    @_trace("git_status")
    def git_status() -> str:
        """Devuelve git status --short del repo SmartPyme."""
        out = subprocess.check_output(["git", "status", "--short"], cwd=repo_root)
        return out.decode("utf-8", errors="replace")

    @mcp.tool()
    @_trace("run_tests")
    def run_tests(test_target: str = "") -> str:
        """Ejecuta pytest en SmartPyme. Si test_target se informa, ejecuta solo ese target."""
        command = ["pytest", "-q"]
        if test_target and test_target.strip():
            command.append(test_target.strip())
        try:
            out = subprocess.check_output(command, cwd=repo_root, stderr=subprocess.STDOUT)
            return out.decode("utf-8", errors="replace")
        except subprocess.CalledProcessError as exc:
            return exc.output.decode("utf-8", errors="replace")

    @mcp.tool()
    @_trace("move_hallazgo_state")
    def move_hallazgo_state(hallazgo_id: str, new_state: str) -> str:
        """Mueve un hallazgo entre pending/in_progress/done/blocked usando su id interno."""
        state = (new_state or "").strip().lower()
        if state not in ALLOWED_HALLAZGO_STATES:
            raise ValueError(f"STATE_INVALIDO: {new_state}")

        source_file = _find_hallazgo_file(hallazgo_id)
        destination_dir = _hallazgos_base() / state
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination_file = destination_dir / source_file.name

        if destination_file.exists():
            raise FileExistsError(f"DESTINO_YA_EXISTE: {destination_file}")

        shutil.move(str(source_file), str(destination_file))
        return f"Hallazgo {hallazgo_id} movido a {state}: {destination_file}"


__all__ = ["register_tools"]
