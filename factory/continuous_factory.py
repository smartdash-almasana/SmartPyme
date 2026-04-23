from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from factory.run_codex_worker import WorkerResult, run_codex_worker
from factory.run_factory import run_factory
from factory.topology_catalog import load_topology_catalog

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = BASE_DIR / "factory" / "canteras_manifest.json"
LOGS_DIR = BASE_DIR / "factory" / "logs"
STATE_DIR = BASE_DIR / "factory" / "state"
SUMMARY_INTERVAL_SECONDS = 15 * 60


def _new_metrics() -> dict[str, int]:
    return {
        "generated": 0,
        "moved_to_in_progress": 0,
        "done": 0,
        "blocked": 0,
        "execution_failures": 0,
        "idle_loops": 0,
    }


def _bump_metrics(container: dict[str, dict[str, int]], key: str, field: str, amount: int = 1) -> None:
    bucket = container.setdefault(key, _new_metrics())
    bucket[field] += amount


def _iso_now(ts: float) -> str:
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _timestamp_for_files(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y%m%d-%H%M%S")


def _format_hhmmss(seconds: float) -> str:
    total = max(0, int(seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _append_log(log_path: Path, message: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} | {message}\n")


def _save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _register_blocked_unit(
    state: dict[str, Any],
    *,
    unit_id: str,
    reason: str,
) -> None:
    blocked_registry = state.setdefault("blocked_reasons_by_unit", {})
    previous = blocked_registry.get(unit_id, {})
    blocked_count = int(previous.get("blocked_count", 0)) + 1
    blocked_registry[unit_id] = {
        "blocked_count": blocked_count,
        "last_reason": reason,
        "suspended": True,
    }


def _is_unit_suspended(state: dict[str, Any], unit_id: str) -> bool:
    blocked_registry = state.get("blocked_reasons_by_unit", {})
    unit_info = blocked_registry.get(unit_id, {})
    return bool(unit_info.get("suspended", False))


def _load_manifest(manifest_path: Path) -> dict[str, list[str]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    canteras = data.get("canteras", [])
    modulos = data.get("modulos", [])
    if not isinstance(canteras, list) or not all(isinstance(x, str) for x in canteras):
        raise ValueError("MANIFEST_INVALIDO: 'canteras' debe ser list[str].")
    if not isinstance(modulos, list) or not all(isinstance(x, str) for x in modulos):
        raise ValueError("MANIFEST_INVALIDO: 'modulos' debe ser list[str].")
    if not modulos:
        raise ValueError("MANIFEST_INVALIDO: 'modulos' no puede ser vacio.")
    return {"canteras": canteras, "modulos": modulos}


def _apply_topology_order(modulos: list[str], topology_manifest_path: Path) -> list[str]:
    catalog = load_topology_catalog(topology_manifest_path.parent / "factory" / "topology_catalog.json")
    if catalog is None:
        return modulos

    unknown = [modulo for modulo in modulos if not catalog.is_known_layer(modulo)]
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise ValueError(f"CAPAS_DESCONOCIDAS_EN_MANIFEST: {joined}")

    official = [layer for layer in catalog.official_assembly_order if layer in modulos]
    remaining = [layer for layer in modulos if layer not in official]
    return official + remaining


def run_continuous_factory(
    *,
    minutes: int,
    cycle_seconds: int,
    manifest_path: Path,
    repo_destino: str,
    model: str | None = None,
    commit_mode: str = "disabled",
    auditor_timeout_seconds: int | None = None,
    max_hallazgos_per_cycle: int | None = None,
    max_executions_per_cycle: int | None = None,
    now_fn: Callable[[], float] = time.time,
    sleep_fn: Callable[[float], None] = time.sleep,
    run_factory_fn: Callable[..., dict[str, str]] = run_factory,
    run_worker_fn: Callable[[], WorkerResult] | None = None,
    base_dir: Path = BASE_DIR,
) -> dict[str, Any]:
    if minutes <= 0:
        raise ValueError("ARGUMENTO_INVALIDO: --minutes debe ser mayor a 0.")
    if cycle_seconds <= 0:
        raise ValueError("ARGUMENTO_INVALIDO: --cycle-seconds debe ser mayor a 0.")
    if max_hallazgos_per_cycle is not None and max_hallazgos_per_cycle <= 0:
        raise ValueError("ARGUMENTO_INVALIDO: --max-hallazgos-per-cycle debe ser mayor a 0.")
    if max_executions_per_cycle is not None and max_executions_per_cycle <= 0:
        raise ValueError("ARGUMENTO_INVALIDO: --max-executions-per-cycle debe ser mayor a 0.")

    manifest = _load_manifest(manifest_path)
    manifest["modulos"] = _apply_topology_order(manifest["modulos"], manifest_path)
    start_ts = now_fn()
    end_ts = start_ts + (minutes * 60)
    ts_name = _timestamp_for_files(start_ts)

    logs_dir = base_dir / "factory" / "logs"
    state_dir = base_dir / "factory" / "state"
    logs_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / f"continuous_factory_{ts_name}.log"
    state_path = state_dir / f"continuous_factory_state_{ts_name}.json"

    state: dict[str, Any] = {
        "start_time": _iso_now(start_ts),
        "planned_end_time": _iso_now(end_ts),
        "current_cycle": 0,
        "canteras_visitadas": [],
        "modulos_procesados": [],
        "generated": 0,
        "moved_to_in_progress": 0,
        "done": 0,
        "blocked": 0,
        "execution_failures": 0,
        "idle_loops": 0,
        "metrics_by_cantera": {},
        "metrics_by_modulo": {},
        "blocked_reasons_by_unit": {},
        "commit_mode": commit_mode,
        "errores": [],
    }
    _save_state(state_path, state)
    _append_log(log_path, "SUPERVISOR_START")

    last_summary_ts = start_ts
    execution_budget = max_executions_per_cycle if max_executions_per_cycle is not None else 1
    last_cantera = "-"
    last_modulo = "-"

    while now_fn() < end_ts:
        state["current_cycle"] += 1
        cycle_id = state["current_cycle"]
        cycle_hallazgos = 0
        cycle_activity = False
        processed_units: set[str] = set()
        fail_fast_reason: str | None = None

        for cantera in manifest["canteras"]:
            if cantera not in state["canteras_visitadas"]:
                state["canteras_visitadas"].append(cantera)

            cantera_path = Path(cantera)
            if not cantera_path.exists():
                err = f"CANTERA_NO_EXISTE|cycle={cycle_id}|cantera={cantera}"
                state["errores"].append(err)
                _append_log(log_path, err)
                continue

            for modulo in manifest["modulos"]:
                if modulo not in state["modulos_procesados"]:
                    state["modulos_procesados"].append(modulo)

                unit_id = f"{cantera}::{modulo}"
                if unit_id in processed_units:
                    _append_log(log_path, f"UNIT_DUPLICADA_SALTADA|cycle={cycle_id}|unit={unit_id}")
                    continue
                processed_units.add(unit_id)

                if _is_unit_suspended(state, unit_id):
                    _append_log(log_path, f"UNIT_SUSPENDIDA_SALTADA|cycle={cycle_id}|unit={unit_id}")
                    continue

                if max_hallazgos_per_cycle is not None and cycle_hallazgos >= max_hallazgos_per_cycle:
                    _append_log(log_path, f"HALLAZGO_BUDGET_ALCANZADO|cycle={cycle_id}")
                    break

                try:
                    result = run_factory_fn(
                        modo="execute_ready",
                        modulo=modulo,
                        rutas_fuente=[cantera],
                        repo_destino=repo_destino,
                        model=model,
                        commit_mode=commit_mode,
                        auditor_timeout_seconds=auditor_timeout_seconds,
                    )
                    state["generated"] += 1
                    last_cantera = cantera
                    last_modulo = modulo
                    _bump_metrics(state["metrics_by_cantera"], cantera, "generated")
                    _bump_metrics(state["metrics_by_modulo"], modulo, "generated")
                    cycle_hallazgos += 1
                    cycle_activity = True

                    estado = result.get("estado", "unknown")
                    motivo = result.get("motivo", "-")
                    if estado == "in_progress":
                        state["moved_to_in_progress"] += 1
                        _bump_metrics(state["metrics_by_cantera"], cantera, "moved_to_in_progress")
                        _bump_metrics(state["metrics_by_modulo"], modulo, "moved_to_in_progress")
                    elif estado == "done":
                        state["done"] += 1
                        _bump_metrics(state["metrics_by_cantera"], cantera, "done")
                        _bump_metrics(state["metrics_by_modulo"], modulo, "done")
                    elif estado == "blocked":
                        state["blocked"] += 1
                        _bump_metrics(state["metrics_by_cantera"], cantera, "blocked")
                        _bump_metrics(state["metrics_by_modulo"], modulo, "blocked")
                        _register_blocked_unit(
                            state,
                            unit_id=unit_id,
                            reason=motivo,
                        )

                    _append_log(
                        log_path,
                        (
                            f"RUN_FACTORY_OK|cycle={cycle_id}|cantera={cantera}|modulo={modulo}|"
                            f"estado={estado}|motivo={motivo}"
                        ),
                    )
                except Exception as exc:  # fail-closed por unidad, no por loop global
                    state["execution_failures"] += 1
                    _bump_metrics(state["metrics_by_cantera"], cantera, "execution_failures")
                    _bump_metrics(state["metrics_by_modulo"], modulo, "execution_failures")
                    err = f"RUN_FACTORY_ERROR|cycle={cycle_id}|cantera={cantera}|modulo={modulo}|error={exc}"
                    state["errores"].append(err)
                    _append_log(log_path, err)
                    if "AUDITOR_ENV_MISSING" in str(exc):
                        fail_fast_reason = str(exc)
                        break

            if fail_fast_reason:
                break

        if fail_fast_reason:
            _append_log(log_path, f"FAIL_FAST|cycle={cycle_id}|reason={fail_fast_reason}")
            _save_state(state_path, state)
            break

        worker_runs = 0
        while worker_runs < execution_budget:
            worker_runs += 1
            try:
                if run_worker_fn is None:
                    worker_result = run_codex_worker(commit_mode=commit_mode)
                else:
                    worker_result = run_worker_fn()
                modulo_metric = worker_result.modulo_objetivo or "_worker"
                cantera_metric = worker_result.cantera_origen
                if worker_result.status == "done":
                    state["done"] += 1
                    _bump_metrics(state["metrics_by_modulo"], modulo_metric, "done")
                    if cantera_metric:
                        _bump_metrics(state["metrics_by_cantera"], cantera_metric, "done")
                    cycle_activity = True
                elif worker_result.status == "blocked":
                    state["blocked"] += 1
                    _bump_metrics(state["metrics_by_modulo"], modulo_metric, "blocked")
                    if cantera_metric:
                        _bump_metrics(state["metrics_by_cantera"], cantera_metric, "blocked")
                    if cantera_metric and worker_result.modulo_objetivo:
                        blocked_unit = f"{cantera_metric}::{worker_result.modulo_objetivo}"
                    else:
                        blocked_unit = worker_result.unit_id or "_worker_unknown"
                    _register_blocked_unit(
                        state,
                        unit_id=blocked_unit,
                        reason=worker_result.message,
                    )
                    cycle_activity = True
                elif worker_result.status == "idle":
                    _append_log(log_path, f"WORKER_IDLE|cycle={cycle_id}")

                _append_log(
                    log_path,
                    (
                        f"WORKER_STATUS|cycle={cycle_id}|status={worker_result.status}|"
                        f"message={worker_result.message}|hallazgo={worker_result.hallazgo or '-'}|"
                        f"modulo={worker_result.modulo_objetivo or '-'}|"
                        f"cantera={worker_result.cantera_origen or '-'}|"
                        f"ruta_fuente={getattr(worker_result, 'ruta_fuente', None) or '-'}|"
                        f"close_mode={getattr(worker_result, 'close_mode', None) or '-'}|"
                        f"unit_id={worker_result.unit_id or '-'}"
                    ),
                )
                if worker_result.status == "idle":
                    break
            except Exception as exc:  # fail-closed por unidad, no por loop global
                state["execution_failures"] += 1
                _bump_metrics(state["metrics_by_modulo"], "_worker", "execution_failures")
                err = f"RUN_WORKER_ERROR|cycle={cycle_id}|error={exc}"
                state["errores"].append(err)
                _append_log(log_path, err)
                break

        if not cycle_activity:
            state["idle_loops"] += 1
            _bump_metrics(state["metrics_by_modulo"], "_global", "idle_loops")

        _save_state(state_path, state)

        now_ts = now_fn()
        elapsed_hhmmss = _format_hhmmss(now_ts - start_ts)
        remaining_hhmmss = _format_hhmmss(end_ts - now_ts)
        heartbeat = (
            f"[{_iso_now(now_ts)}] HEARTBEAT"
            f" cycle={cycle_id}"
            f" elapsed={elapsed_hhmmss}"
            f" remaining={remaining_hhmmss}"
            f" cantera={last_cantera}"
            f" modulo={last_modulo}"
            f" generated={state['generated']}"
            f" moved_to_in_progress={state['moved_to_in_progress']}"
            f" done={state['done']}"
            f" blocked={state['blocked']}"
            f" execution_failures={state['execution_failures']}"
            f" idle_loops={state['idle_loops']}"
        )
        print(heartbeat)
        _append_log(log_path, heartbeat)

        if (now_ts - last_summary_ts) >= SUMMARY_INTERVAL_SECONDS:
            summary_15m = (
                f"[{_iso_now(now_ts)}] SUMMARY_15M"
                f" cycle={cycle_id}"
                f" generated={state['generated']}"
                f" moved_to_in_progress={state['moved_to_in_progress']}"
                f" done={state['done']}"
                f" blocked={state['blocked']}"
                f" execution_failures={state['execution_failures']}"
                f" idle_loops={state['idle_loops']}"
            )
            print(summary_15m)
            _append_log(log_path, summary_15m)
            last_summary_ts = now_ts

        remaining = end_ts - now_fn()
        if remaining <= 0:
            break
        sleep_fn(min(float(cycle_seconds), remaining))

    end_real_ts = now_fn()
    final_elapsed = _format_hhmmss(end_real_ts - start_ts)
    final_summary = (
        f"[{_iso_now(end_real_ts)}] FINAL_SUMMARY"
        f" total_cycles={state['current_cycle']}"
        f" total_generated={state['generated']}"
        f" total_moved_to_in_progress={state['moved_to_in_progress']}"
        f" total_done={state['done']}"
        f" total_blocked={state['blocked']}"
        f" total_execution_failures={state['execution_failures']}"
        f" total_idle_loops={state['idle_loops']}"
        f" elapsed={final_elapsed}"
        f" remaining=00:00:00"
    )
    print(final_summary)
    _append_log(
        log_path,
        (
            final_summary
        ),
    )
    cantera_breakdown = json.dumps(state["metrics_by_cantera"], ensure_ascii=False, sort_keys=True)
    modulo_breakdown = json.dumps(state["metrics_by_modulo"], ensure_ascii=False, sort_keys=True)
    final_breakdown = (
        f"[{_iso_now(end_real_ts)}] FINAL_BREAKDOWN"
        f" by_cantera={cantera_breakdown}"
        f" by_modulo={modulo_breakdown}"
    )
    print(final_breakdown)
    _append_log(log_path, final_breakdown)
    _save_state(state_path, state)

    return {
        "status": "completed",
        "log_path": str(log_path),
        "state_path": str(state_path),
        "state": state,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Supervisor continuo local de SmartPyme Factory")
    parser.add_argument("--minutes", type=int, default=180)
    parser.add_argument("--cycle-seconds", type=int, default=60)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repo-destino", required=True)
    parser.add_argument("--model", required=False, default=None)
    parser.add_argument("--commit-mode", required=False, default="disabled")
    parser.add_argument("--auditor-timeout-seconds", type=int, required=False, default=None)
    parser.add_argument("--max-hallazgos-per-cycle", type=int, required=False, default=None)
    parser.add_argument("--max-executions-per-cycle", type=int, required=False, default=None)
    args = parser.parse_args()

    try:
        result = run_continuous_factory(
            minutes=args.minutes,
            cycle_seconds=args.cycle_seconds,
            manifest_path=args.manifest,
            repo_destino=args.repo_destino,
            model=args.model,
            commit_mode=args.commit_mode,
            auditor_timeout_seconds=args.auditor_timeout_seconds,
            max_hallazgos_per_cycle=args.max_hallazgos_per_cycle,
            max_executions_per_cycle=args.max_executions_per_cycle,
        )
    except Exception as exc:
        print(str(exc))
        return 1

    print("status=completed")
    print(f"log_path={result['log_path']}")
    print(f"state_path={result['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
