from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from factory.run_factory import validate_hallazgo

BASE_DIR = Path(__file__).resolve().parents[1]
HALLAZGOS_DIR = BASE_DIR / "factory" / "hallazgos"
IN_PROGRESS_DIR = HALLAZGOS_DIR / "in_progress"
DONE_DIR = HALLAZGOS_DIR / "done"
BLOCKED_DIR = HALLAZGOS_DIR / "blocked"
MINIMUM_TESTS_BY_MODULE: dict[str, list[str]] = {
    "hallazgos": ["tests/core/test_hallazgos_service.py"],
}


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    message: str
    tests_passed: bool


@dataclass(frozen=True)
class WorkerResult:
    status: str
    message: str
    close_mode: str | None = None
    hallazgo: str | None = None
    moved_to: str | None = None
    modulo_objetivo: str | None = None
    cantera_origen: str | None = None
    ruta_fuente: str | None = None
    unit_id: str | None = None


@dataclass(frozen=True)
class HallazgoExecutionContract:
    modulo_objetivo: str
    objetivo: str
    target_paths: list[str]


def _ensure_dirs(*dirs: Path) -> None:
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)


def _lock_path(hallazgo_path: Path) -> Path:
    return hallazgo_path.with_suffix(f"{hallazgo_path.suffix}.lock")


def _acquire_lock(hallazgo_path: Path) -> Path | None:
    lock = _lock_path(hallazgo_path)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(str(lock), flags)
    except FileExistsError:
        return None
    os.close(fd)
    return lock


def _release_lock(lock_path: Path | None) -> None:
    if lock_path and lock_path.exists():
        lock_path.unlink()


def _resolve_unique_destination(destination_dir: Path, original_name: str) -> Path:
    base_candidate = destination_dir / original_name
    if not base_candidate.exists():
        return base_candidate

    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    index = 1
    while True:
        candidate = destination_dir / f"{stem}-{index:02d}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _move_no_overwrite(source: Path, destination_dir: Path) -> Path | None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    original_name = source.name
    while True:
        destination = _resolve_unique_destination(destination_dir, original_name)
        try:
            source.rename(destination)
            return destination
        except FileExistsError:
            # fallback defensivo ante carrera de colision al momento del rename
            continue
        except FileNotFoundError:
            # source desaparecio entre lock/ejecucion/cierre; tratar como idempotente
            return None


def _select_oldest_unlocked(in_progress_dir: Path) -> Path | None:
    hallazgos = sorted(
        [p for p in in_progress_dir.glob("*.md") if p.is_file()],
        key=lambda path: path.stat().st_mtime,
    )
    for hallazgo in hallazgos:
        if not _lock_path(hallazgo).exists():
            return hallazgo
    return None


def _extract_section_lines(content: str, section_title: str) -> list[str]:
    lines = content.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == section_title:
            start_index = index + 1
            break
    if start_index is None:
        return []

    collected: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return collected


def _extract_modulo_objetivo(content: str) -> str | None:
    for line in content.splitlines():
        stripped = line.strip().lower()
        if stripped.startswith("- modulo_objetivo:"):
            value = stripped.replace("- modulo_objetivo:", "", 1).strip()
            return value or None
    return None


def _extract_meta_value(content: str, field_name: str) -> str | None:
    prefix = f"- {field_name}:"
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(prefix.lower()):
            value = stripped[len(prefix) :].strip()
            return value or None
    return None


def _extract_target_paths(content: str) -> list[str]:
    proposal_lines = _extract_section_lines(content, "## PROPUESTA_DE_PORTADO")
    targets: list[str] = []
    for line in proposal_lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        candidate = stripped[2:].strip()
        if candidate:
            targets.append(candidate.replace("\\", "/"))
    return targets


def _extract_ruta_fuente(content: str) -> str | None:
    source_lines = _extract_section_lines(content, "## RUTAS_FUENTE")
    for line in source_lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            candidate = stripped[2:].strip()
            if candidate:
                return candidate
    return None


def _build_unit_metadata(
    hallazgo_path: Path,
) -> tuple[str | None, str | None, str | None, str | None]:
    content = hallazgo_path.read_text(encoding="utf-8")
    modulo_objetivo = _extract_modulo_objetivo(content)
    cantera_raiz = _extract_meta_value(content, "cantera_raiz")
    ruta_fuente = _extract_ruta_fuente(content)
    cantera_origen = cantera_raiz or ruta_fuente
    if modulo_objetivo:
        unit_id = f"{hallazgo_path.stem}:{modulo_objetivo}"
    else:
        unit_id = hallazgo_path.stem
    return modulo_objetivo, cantera_origen, ruta_fuente, unit_id


def _parse_hallazgo_contract(hallazgo_path: Path) -> HallazgoExecutionContract:
    content = hallazgo_path.read_text(encoding="utf-8")
    modulo = _extract_modulo_objetivo(content)
    if not modulo:
        raise ValueError("CONTRATO_INVALIDO: falta modulo_objetivo en hallazgo.")

    objetivo_lines = [
        line.strip()
        for line in _extract_section_lines(content, "## OBJETIVO")
        if line.strip()
    ]
    objetivo = " ".join(objetivo_lines).strip()
    if not objetivo:
        raise ValueError("CONTRATO_INVALIDO: falta objetivo operativo en hallazgo.")

    target_paths = _extract_target_paths(content)
    if not target_paths:
        raise ValueError("CONTRATO_INVALIDO: no hay rutas en PROPUESTA_DE_PORTADO.")

    return HallazgoExecutionContract(
        modulo_objetivo=modulo,
        objetivo=objetivo,
        target_paths=target_paths,
    )


def _detect_test_targets(contract: HallazgoExecutionContract, repo_root: Path) -> list[str]:
    explicit_tests: list[str] = []
    for raw_path in contract.target_paths:
        normalized = raw_path.replace("\\", "/")
        if not normalized.lower().startswith("tests/"):
            continue
        test_path = repo_root / Path(normalized)
        if test_path.exists():
            explicit_tests.append(normalized)

    if explicit_tests:
        return sorted(set(explicit_tests))

    module_key = contract.modulo_objetivo.lower()
    module_mapped_tests = MINIMUM_TESTS_BY_MODULE.get(module_key, [])
    if module_mapped_tests:
        return list(dict.fromkeys(module_mapped_tests))

    fallback_candidates = [
        f"tests/core/test_{contract.modulo_objetivo}_service.py",
        f"tests/core/test_{contract.modulo_objetivo}.py",
    ]
    detected: list[str] = []
    for candidate in fallback_candidates:
        if (repo_root / Path(candidate)).exists():
            detected.append(candidate)
    return detected


def _run_codex_exec(
    repo_root: Path,
    contract: HallazgoExecutionContract,
    hallazgo_path: Path,
) -> tuple[bool, str]:
    codex_bin = _resolve_codex_executable()
    if codex_bin is None:
        return False, "CODEX_BINARIO_NO_ENCONTRADO: instalar Codex CLI o agregarlo al PATH."

    timeout_seconds = int(os.environ.get("SMARTPYME_CODEX_EXEC_TIMEOUT_SECONDS", "600"))
    codex_model = os.environ.get("SMARTPYME_CODEX_MODEL", "gpt-5.4")
    prompt = (
        "Ejecuta este hallazgo en modo fail-closed y alcance minimo. "
        f"Modulo objetivo: {contract.modulo_objetivo}. "
        f"Objetivo: {contract.objetivo}. "
        f"Archivos autorizados: {', '.join(contract.target_paths)}. "
        "No tocar otras capas. "
        f"Hallazgo: {hallazgo_path}."
    )
    command = [
        codex_bin,
        "exec",
        "-C",
        str(repo_root),
        "-m",
        codex_model,
        "--full-auto",
    ]
    command.append(prompt)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            cwd=str(repo_root),
        )
    except FileNotFoundError:
        return False, "CODEX_BINARIO_NO_ENCONTRADO: instalar Codex CLI o agregarlo al PATH."
    except subprocess.TimeoutExpired:
        return False, f"CODEX_TIMEOUT: supero {timeout_seconds}s ejecutando codex."
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr or stdout or "codex exec sin detalle"
        if "not supported when using Codex with a ChatGPT account" in detail:
            return False, f"CODEX_MODELO_NO_COMPATIBLE: {codex_model}"
        return False, f"CODEx_EXEC_ERROR: {detail}"
    return True, "CODEx_EXEC_OK"


def _resolve_codex_executable() -> str | None:
    candidates = (
        "codex",
        "codex.cmd",
        "codex.exe",
        "codex.ps1",
    )
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _run_minimum_tests(repo_root: Path, test_targets: list[str]) -> tuple[bool, str]:
    timeout_seconds = int(os.environ.get("SMARTPYME_WORKER_PYTEST_TIMEOUT_SECONDS", "300"))
    base_temp = repo_root / ".tmp" / "pytest_codex_worker"
    base_temp.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        *test_targets,
        "-q",
        "--basetemp",
        str(base_temp),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        cwd=str(repo_root),
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr or stdout or "pytest sin detalle"
        return False, f"TESTS_FAIL: {detail}"
    return True, "TESTS_OK"


def _build_real_executor(repo_root: Path) -> Callable[[Path], ExecutionResult]:
    def _executor(hallazgo_path: Path) -> ExecutionResult:
        try:
            contract = _parse_hallazgo_contract(hallazgo_path)
        except Exception as exc:
            return ExecutionResult(
                success=False,
                message=f"CONTRATO_INVALIDO: {exc}",
                tests_passed=False,
            )

        test_targets = _detect_test_targets(contract, repo_root)
        if not test_targets:
            return ExecutionResult(
                success=False,
                message=(
                    "TESTS_MINIMOS_NO_DEFINIDOS: no hay tests objetivos para "
                    f"modulo {contract.modulo_objetivo}."
                ),
                tests_passed=False,
            )

        executed, exec_message = _run_codex_exec(repo_root, contract, hallazgo_path)
        if not executed:
            return ExecutionResult(success=False, message=exec_message, tests_passed=False)

        tests_ok, tests_message = _run_minimum_tests(repo_root, test_targets)
        if not tests_ok:
            return ExecutionResult(success=False, message=tests_message, tests_passed=False)

        return ExecutionResult(
            success=True,
            message=f"{exec_message}; {tests_message}; tests={','.join(test_targets)}",
            tests_passed=True,
        )

    return _executor


def run_codex_worker(
    *,
    in_progress_dir: Path = IN_PROGRESS_DIR,
    done_dir: Path = DONE_DIR,
    blocked_dir: Path = BLOCKED_DIR,
    repo_root: Path = BASE_DIR,
    executor: Callable[[Path], ExecutionResult] | None = None,
    commit_mode: str = "disabled",
) -> WorkerResult:
    if commit_mode != "disabled":
        return WorkerResult(
            status="blocked",
            message="COMMIT_MODE_NO_IMPLEMENTADO: solo se permite commit_mode=disabled por ahora.",
            close_mode="unsupported_commit_mode",
        )

    _ensure_dirs(in_progress_dir, done_dir, blocked_dir)
    active_executor = executor or _build_real_executor(repo_root)

    hallazgo = _select_oldest_unlocked(in_progress_dir)
    if hallazgo is None:
        return WorkerResult(status="idle", message="NO_HALLAZGOS_DISPONIBLES", close_mode=None)

    lock_path = _acquire_lock(hallazgo)
    if lock_path is None:
        return WorkerResult(status="idle", message="HALLAZGO_BLOQUEADO_POR_LOCK", close_mode=None)

    try:
        modulo_objetivo, cantera_origen, ruta_fuente, unit_id = _build_unit_metadata(hallazgo)
        is_valid, reason = validate_hallazgo(hallazgo, repo_root=repo_root)
        if not is_valid:
            moved = _move_no_overwrite(hallazgo, blocked_dir)
            if moved is None:
                return WorkerResult(
                    status="idle",
                    message=(
                        "HALLAZGO_NO_ENCONTRADO_EN_CIERRE: posiblemente ya fue "
                        "procesado por otra corrida."
                    ),
                    close_mode="idempotent_missing_source",
                    hallazgo=str(hallazgo),
                    moved_to=None,
                    modulo_objetivo=modulo_objetivo,
                    cantera_origen=cantera_origen,
                    ruta_fuente=ruta_fuente,
                    unit_id=unit_id,
                )
            return WorkerResult(
                status="blocked",
                message=reason,
                close_mode="moved",
                hallazgo=str(hallazgo),
                moved_to=str(moved),
                modulo_objetivo=modulo_objetivo,
                cantera_origen=cantera_origen,
                ruta_fuente=ruta_fuente,
                unit_id=unit_id,
            )

        execution = active_executor(hallazgo)
        target_dir = done_dir if (execution.success and execution.tests_passed) else blocked_dir
        target_status = "done" if target_dir == done_dir else "blocked"

        moved = _move_no_overwrite(hallazgo, target_dir)
        if moved is None:
            return WorkerResult(
                status=target_status,
                message=(
                    "DONE_BY_OTHER_WORKER"
                    if target_status == "done"
                    else "BLOCKED_BY_OTHER_WORKER"
                ),
                close_mode="idempotent_missing_source",
                hallazgo=str(hallazgo),
                moved_to=None,
                modulo_objetivo=modulo_objetivo,
                cantera_origen=cantera_origen,
                ruta_fuente=ruta_fuente,
                unit_id=unit_id,
            )
        return WorkerResult(
            status=target_status,
            message=execution.message,
            close_mode="moved",
            hallazgo=str(hallazgo),
            moved_to=str(moved),
            modulo_objetivo=modulo_objetivo,
            cantera_origen=cantera_origen,
            ruta_fuente=ruta_fuente,
            unit_id=unit_id,
        )
    finally:
        _release_lock(lock_path)


def main() -> int:
    result = run_codex_worker()
    print(f"status={result.status}")
    print(f"message={result.message}")
    if result.close_mode:
        print(f"close_mode={result.close_mode}")
    if result.hallazgo:
        print(f"hallazgo={result.hallazgo}")
    if result.moved_to:
        print(f"moved_to={result.moved_to}")
    if result.modulo_objetivo:
        print(f"modulo_objetivo={result.modulo_objetivo}")
    if result.cantera_origen:
        print(f"cantera_origen={result.cantera_origen}")
    if result.ruta_fuente:
        print(f"ruta_fuente={result.ruta_fuente}")
    if result.unit_id:
        print(f"unit_id={result.unit_id}")
    return 0 if result.status in {"idle", "done"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
