import io
import json
import shutil
import sys
import unittest
import uuid
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import factory.continuous_factory as cf
from factory.continuous_factory import run_continuous_factory


@dataclass
class _StubWorkerResult:
    status: str
    message: str
    close_mode: str | None = None
    hallazgo: str | None = None
    moved_to: str | None = None
    modulo_objetivo: str | None = None
    cantera_origen: str | None = None
    ruta_fuente: str | None = None
    unit_id: str | None = None


class _FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def now(self) -> float:
        return self._now

    def sleep(self, seconds: float) -> None:
        self._now += max(0.0, seconds)


class ContinuousFactoryTests(unittest.TestCase):
    def _case_root(self) -> Path:
        base = Path(__file__).resolve().parents[2] / ".tmp" / "continuous_factory_tests"
        base.mkdir(parents=True, exist_ok=True)
        root = base / f"case_{uuid.uuid4().hex}"
        root.mkdir(parents=True, exist_ok=False)
        return root

    def _write_manifest(self, path: Path, canteras: list[str], modulos: list[str]) -> None:
        path.write_text(
            json.dumps({"canteras": canteras, "modulos": modulos}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _write_topology_catalog(self, base_dir: Path) -> None:
        factory_dir = base_dir / "factory"
        factory_dir.mkdir(parents=True, exist_ok=True)
        (factory_dir / "topology_catalog.json").write_text(
            json.dumps(
                {
                    "core_layers": {
                        "clarification": {"target_files": ["app/core/clarification/service.py"]},
                        "reconciliation": {"target_files": ["app/core/reconciliation/service.py"]},
                    },
                    "official_assembly_order": ["clarification", "reconciliation"],
                    "canteras": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_termina_por_presupuesto_temporal(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=20,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertEqual(result["status"], "completed")
            self.assertGreaterEqual(clock.now(), 60.0)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_cantera_inexistente_se_salta(self) -> None:
        root = self._case_root()
        try:
            manifest = root / "manifest.json"
            self._write_manifest(
                manifest,
                [str(root / "no_existe")],
                ["clarification"],
            )
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            errores = result["state"]["errores"]
            self.assertTrue(any("CANTERA_NO_EXISTE" in e for e in errores))
            self.assertEqual(result["status"], "completed")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_error_en_una_unidad_no_tumba_proceso(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification", "reconciliation"])
            clock = _FakeClock()
            calls = {"n": 0}

            def _run_factory_stub(**_: object) -> dict[str, str]:
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RuntimeError("fallo_controlado")
                return {"estado": "in_progress"}

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertGreaterEqual(result["state"]["execution_failures"], 1)
            self.assertEqual(result["status"], "completed")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_fail_fast_when_auditor_env_is_missing(self) -> None:
        root = self._case_root()
        try:
            cantera_a = root / "cantera_a"
            cantera_b = root / "cantera_b"
            cantera_a.mkdir()
            cantera_b.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera_a), str(cantera_b)], ["reconciliation"])
            clock = _FakeClock()
            calls = {"n": 0}

            def _run_factory_stub(**_: object) -> dict[str, str]:
                calls["n"] += 1
                raise RuntimeError("AUDITOR_ENV_MISSING: GOOGLE_CLOUD_PROJECT")

            result = run_continuous_factory(
                minutes=5,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertEqual(calls["n"], 1)
            self.assertEqual(result["state"]["execution_failures"], 1)
            self.assertEqual(result["state"]["current_cycle"], 1)
            self.assertIn("AUDITOR_ENV_MISSING", result["state"]["errores"][0])
            log_content = Path(result["log_path"]).read_text(encoding="utf-8")
            self.assertIn(
                "FAIL_FAST|cycle=1|reason=AUDITOR_ENV_MISSING: GOOGLE_CLOUD_PROJECT",
                log_content,
            )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_crea_log_y_state(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertTrue(Path(result["log_path"]).exists())
            self.assertTrue(Path(result["state_path"]).exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_genera_resumen_final(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            log_content = Path(result["log_path"]).read_text(encoding="utf-8")
            self.assertIn("FINAL_SUMMARY", log_content)
            self.assertRegex(log_content, r"elapsed=\d{2}:\d{2}:\d{2}")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_heartbeat_queda_registrado_con_elapsed_y_remaining(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            log_content = Path(result["log_path"]).read_text(encoding="utf-8")
            self.assertIn("HEARTBEAT", log_content)
            self.assertRegex(log_content, r"elapsed=\d{2}:\d{2}:\d{2}")
            self.assertRegex(log_content, r"remaining=\d{2}:\d{2}:\d{2}")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_logs_worker_status_for_idle_with_message_hallazgo_and_unit_id(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(
                    status="idle",
                    message="NO_HALLAZGOS_DISPONIBLES",
                    hallazgo="factory/hallazgos/in_progress/x.md",
                    unit_id="x:clarification",
                ),
                base_dir=root,
            )

            log_content = Path(result["log_path"]).read_text(encoding="utf-8")
            self.assertIn("WORKER_IDLE|cycle=1", log_content)
            self.assertIn(
                "WORKER_STATUS|cycle=1|status=idle|message=NO_HALLAZGOS_DISPONIBLES",
                log_content,
            )
            self.assertIn("hallazgo=factory/hallazgos/in_progress/x.md", log_content)
            self.assertIn("close_mode=-", log_content)
            self.assertIn("unit_id=x:clarification", log_content)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_respeta_rotacion_basica(self) -> None:
        root = self._case_root()
        try:
            cantera_a = root / "cantera_a"
            cantera_b = root / "cantera_b"
            cantera_a.mkdir()
            cantera_b.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(
                manifest,
                [str(cantera_a), str(cantera_b)],
                ["clarification", "reconciliation"],
            )
            clock = _FakeClock()
            calls: list[tuple[str, str]] = []

            def _run_factory_stub(**kwargs: object) -> dict[str, str]:
                calls.append((str(kwargs["rutas_fuente"][0]), str(kwargs["modulo"])))
                return {"estado": "in_progress"}

            run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            expected = [
                (str(cantera_a), "clarification"),
                (str(cantera_a), "reconciliation"),
                (str(cantera_b), "clarification"),
                (str(cantera_b), "reconciliation"),
            ]
            self.assertEqual(calls, expected)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_no_reprocesa_unidad_en_mismo_ciclo(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera), str(cantera)], ["clarification"])
            clock = _FakeClock()
            calls: list[tuple[str, str]] = []

            def _run_factory_stub(**kwargs: object) -> dict[str, str]:
                calls.append((str(kwargs["rutas_fuente"][0]), str(kwargs["modulo"])))
                return {"estado": "in_progress"}

            run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertEqual(len(calls), 1)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_propagates_auditor_timeout_seconds_to_runner(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()
            captured: dict[str, object] = {}

            def _run_factory_stub(**kwargs: object) -> dict[str, str]:
                captured["auditor_timeout_seconds"] = kwargs.get("auditor_timeout_seconds")
                return {"estado": "in_progress"}

            run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                auditor_timeout_seconds=90,
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertEqual(captured.get("auditor_timeout_seconds"), 90)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_auditor_timeout_seconds_is_none(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()
            captured: dict[str, object] = {}

            def _run_factory_stub(**kwargs: object) -> dict[str, str]:
                captured["auditor_timeout_seconds"] = kwargs.get("auditor_timeout_seconds")
                return {"estado": "in_progress"}

            run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertIsNone(captured.get("auditor_timeout_seconds"))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_main_accepts_auditor_timeout_seconds_cli(self) -> None:
        root = self._case_root()
        try:
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(root / "cantera_a")], ["clarification"])
            captured: dict[str, object] = {}

            def fake_run_continuous_factory(**kwargs: object) -> dict[str, object]:
                captured.update(kwargs)
                return {
                    "status": "completed",
                    "log_path": str(root / "factory" / "logs" / "x.log"),
                    "state_path": str(root / "factory" / "state" / "x.json"),
                    "state": {},
                }

            argv = [
                "continuous_factory.py",
                "--minutes",
                "10",
                "--cycle-seconds",
                "60",
                "--manifest",
                str(manifest),
                "--repo-destino",
                str(root),
                "--auditor-timeout-seconds",
                "120",
            ]

            output = io.StringIO()
            with (
                patch.object(cf, "run_continuous_factory", fake_run_continuous_factory),
                patch.object(sys, "argv", argv),
                redirect_stdout(output),
            ):
                exit_code = cf.main()

            self.assertEqual(exit_code, 0)
            self.assertEqual(captured.get("auditor_timeout_seconds"), 120)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_applies_official_topology_order_to_modulos(self) -> None:
        root = self._case_root()
        try:
            self._write_topology_catalog(root)
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["reconciliation", "clarification"])
            clock = _FakeClock()
            calls: list[str] = []

            def _run_factory_stub(**kwargs: object) -> dict[str, str]:
                calls.append(str(kwargs["modulo"]))
                return {"estado": "in_progress"}

            run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertEqual(calls, ["clarification", "reconciliation"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_fails_closed_when_manifest_has_unknown_layer_with_topology(self) -> None:
        root = self._case_root()
        try:
            self._write_topology_catalog(root)
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification", "unknown_layer"])
            clock = _FakeClock()

            with self.assertRaisesRegex(ValueError, "CAPAS_DESCONOCIDAS_EN_MANIFEST"):
                run_continuous_factory(
                    minutes=1,
                    cycle_seconds=60,
                    manifest_path=manifest,
                    repo_destino=str(root),
                    now_fn=clock.now,
                    sleep_fn=clock.sleep,
                    run_factory_fn=lambda **_: {"estado": "in_progress"},
                    run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                    base_dir=root,
                )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_persists_metrics_breakdown_by_cantera_and_modulo(self) -> None:
        root = self._case_root()
        try:
            cantera_a = root / "cantera_a"
            cantera_b = root / "cantera_b"
            cantera_a.mkdir()
            cantera_b.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(
                manifest,
                [str(cantera_a), str(cantera_b)],
                ["clarification"],
            )
            clock = _FakeClock()
            calls = {"n": 0}

            def _run_factory_stub(**kwargs: object) -> dict[str, str]:
                calls["n"] += 1
                if str(kwargs["rutas_fuente"][0]) == str(cantera_a):
                    return {"estado": "in_progress"}
                return {"estado": "blocked"}

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="done", message="ok"),
                base_dir=root,
            )

            by_cantera = result["state"]["metrics_by_cantera"]
            by_modulo = result["state"]["metrics_by_modulo"]
            self.assertEqual(by_cantera[str(cantera_a)]["generated"], 1)
            self.assertEqual(by_cantera[str(cantera_a)]["moved_to_in_progress"], 1)
            self.assertEqual(by_cantera[str(cantera_b)]["generated"], 1)
            self.assertEqual(by_cantera[str(cantera_b)]["blocked"], 1)
            self.assertEqual(by_modulo["clarification"]["generated"], 2)
            self.assertEqual(by_modulo["_worker"]["done"], 1)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_worker_done_is_imputed_to_real_module_and_not_worker_bucket(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["reconciliation"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(
                    status="done",
                    message="ok",
                    modulo_objetivo="reconciliation",
                    cantera_origen=str(cantera),
                    unit_id="u1:reconciliation",
                ),
                base_dir=root,
            )

            by_cantera = result["state"]["metrics_by_cantera"]
            by_modulo = result["state"]["metrics_by_modulo"]
            self.assertEqual(by_modulo["reconciliation"]["done"], 1)
            self.assertEqual(by_cantera[str(cantera)]["done"], 1)
            self.assertTrue("_worker" not in by_modulo or by_modulo["_worker"]["done"] == 0)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_worker_done_is_imputed_by_cantera_raiz_not_ruta_fuente(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["reconciliation"])
            clock = _FakeClock()
            ruta_fuente = "backend/modules/meli_reconciliation.py"

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(
                    status="done",
                    message="ok",
                    modulo_objetivo="reconciliation",
                    cantera_origen=str(cantera),
                    ruta_fuente=ruta_fuente,
                    unit_id="u3:reconciliation",
                ),
                base_dir=root,
            )

            by_cantera = result["state"]["metrics_by_cantera"]
            self.assertEqual(by_cantera[str(cantera)]["done"], 1)
            self.assertTrue(ruta_fuente not in by_cantera)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_worker_blocked_is_imputed_to_real_module_and_cantera(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["reconciliation"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(
                    status="blocked",
                    message="blocked",
                    modulo_objetivo="reconciliation",
                    cantera_origen=str(cantera),
                    unit_id="u2:reconciliation",
                ),
                base_dir=root,
            )

            by_cantera = result["state"]["metrics_by_cantera"]
            by_modulo = result["state"]["metrics_by_modulo"]
            self.assertEqual(by_modulo["reconciliation"]["blocked"], 1)
            self.assertEqual(by_cantera[str(cantera)]["blocked"], 1)
            self.assertTrue("_worker" not in by_modulo or by_modulo["_worker"]["blocked"] == 0)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_heartbeat_reports_last_real_executed_unit_not_last_manifest_iteration(self) -> None:
        root = self._case_root()
        try:
            cantera_a = root / "cantera_a"
            cantera_b = root / "cantera_b"
            cantera_c = root / "cantera_c"
            cantera_a.mkdir()
            cantera_b.mkdir()
            cantera_c.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(
                manifest,
                [str(cantera_a), str(cantera_b), str(cantera_c)],
                ["reconciliation"],
            )
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                max_hallazgos_per_cycle=1,
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            log_content = Path(result["log_path"]).read_text(encoding="utf-8")
            self.assertIn("HEARTBEAT cycle=1", log_content)
            self.assertIn(f"cantera={cantera_a}", log_content)
            self.assertNotIn(f"cantera={cantera_c}", log_content)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_writes_final_breakdown_to_log(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["clarification"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            log_content = Path(result["log_path"]).read_text(encoding="utf-8")
            state_content = json.loads(Path(result["state_path"]).read_text(encoding="utf-8"))
            self.assertIn("FINAL_BREAKDOWN", log_content)
            self.assertIn("metrics_by_cantera", state_content)
            self.assertIn("metrics_by_modulo", state_content)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_logs_blocked_motivo_from_run_factory(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["reconciliation"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {
                    "estado": "blocked",
                    "motivo": "VALIDACION_BLOCKED: PREGUNTA_ABIERTA",
                },
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            log_content = Path(result["log_path"]).read_text(encoding="utf-8")
            self.assertIn("RUN_FACTORY_OK", log_content)
            self.assertIn("estado=blocked", log_content)
            self.assertIn("motivo=VALIDACION_BLOCKED: PREGUNTA_ABIERTA", log_content)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_suspends_blocked_unit_and_avoids_infinite_reprocessing(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["reconciliation"])
            clock = _FakeClock()
            calls = {"n": 0}

            def _run_factory_stub(**_: object) -> dict[str, str]:
                calls["n"] += 1
                return {"estado": "blocked", "motivo": "VALIDACION_BLOCKED: RUTA_INVALIDA"}

            result = run_continuous_factory(
                minutes=3,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=_run_factory_stub,
                run_worker_fn=lambda: _StubWorkerResult(status="idle", message="idle"),
                base_dir=root,
            )

            self.assertEqual(calls["n"], 1)
            blocked_by_unit = result["state"]["blocked_reasons_by_unit"]
            expected_unit = f"{cantera}::reconciliation"
            self.assertIn(expected_unit, blocked_by_unit)
            self.assertEqual(
                blocked_by_unit[expected_unit]["last_reason"],
                "VALIDACION_BLOCKED: RUTA_INVALIDA",
            )
            self.assertTrue(blocked_by_unit[expected_unit]["suspended"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_registers_worker_block_reason_by_unit(self) -> None:
        root = self._case_root()
        try:
            cantera = root / "cantera_a"
            cantera.mkdir()
            manifest = root / "manifest.json"
            self._write_manifest(manifest, [str(cantera)], ["reconciliation"])
            clock = _FakeClock()

            result = run_continuous_factory(
                minutes=1,
                cycle_seconds=60,
                manifest_path=manifest,
                repo_destino=str(root),
                now_fn=clock.now,
                sleep_fn=clock.sleep,
                run_factory_fn=lambda **_: {"estado": "in_progress"},
                run_worker_fn=lambda: _StubWorkerResult(
                    status="blocked",
                    message="TESTS_FAIL: assertion error",
                    modulo_objetivo="reconciliation",
                    cantera_origen=str(cantera),
                    unit_id="h1:reconciliation",
                ),
                base_dir=root,
            )

            blocked_by_unit = result["state"]["blocked_reasons_by_unit"]
            expected_unit = f"{cantera}::reconciliation"
            self.assertIn(expected_unit, blocked_by_unit)
            self.assertEqual(
                blocked_by_unit[expected_unit]["last_reason"],
                "TESTS_FAIL: assertion error",
            )
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
