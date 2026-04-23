import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import factory.run_codex_worker as rcw
from factory.run_codex_worker import ExecutionResult, run_codex_worker


def _valid_hallazgo_content(
    estado: str = "pending",
    modulo_objetivo: str = "clarification",
    cantera_raiz: str | None = None,
    ruta_fuente: str | None = None,
) -> str:
    cantera_meta = ""
    if cantera_raiz:
        cantera_meta = f"\n- cantera_raiz: {cantera_raiz}"

    rutas_fuente = ""
    if ruta_fuente:
        rutas_fuente = f"\n## RUTAS_FUENTE\n- {ruta_fuente}\n"

    return f"""# HALLAZGO

## META
- id: HZ-test
- estado: {estado}
- modulo_objetivo: {modulo_objetivo}
{cantera_meta}

## OBJETIVO
Objetivo test.
{rutas_fuente}

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- app/core/clarification/service.py

## REGLAS_DE_EJECUCION
- fail-closed

## CRITERIO_DE_CIERRE
- test ok

## PREGUNTA_AL_OWNER
- null
"""


class RunCodexWorkerTests(unittest.TestCase):
    def _local_tmp_root(self) -> Path:
        root = Path(__file__).resolve().parents[2] / ".tmp" / "unittest_run_codex_worker"
        root.mkdir(parents=True, exist_ok=True)
        case_dir = root / f"case_{uuid.uuid4().hex}"
        case_dir.mkdir(parents=True, exist_ok=False)
        return case_dir

    def test_idle_when_no_hallazgos(self) -> None:
        root = self._local_tmp_root()
        try:
            result = run_codex_worker(
                in_progress_dir=root / "in_progress",
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
            )
            self.assertEqual(result.status, "idle")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_fail_closed_when_commit_mode_is_not_disabled(self) -> None:
        root = self._local_tmp_root()
        try:
            result = run_codex_worker(
                in_progress_dir=root / "in_progress",
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                commit_mode="auto_commit",
            )
            self.assertEqual(result.status, "blocked")
            self.assertIn("COMMIT_MODE_NO_IMPLEMENTADO", result.message)
            self.assertEqual(result.close_mode, "unsupported_commit_mode")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_valid_and_executor_success_moves_to_done(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            (in_progress / "a.md").write_text(_valid_hallazgo_content(), encoding="utf-8")

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=lambda _: ExecutionResult(success=True, message="OK", tests_passed=True),
            )

            self.assertEqual(result.status, "done")
            self.assertEqual(result.close_mode, "moved")
            self.assertTrue((root / "done" / "a.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_valid_and_executor_failure_moves_to_blocked(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            (in_progress / "b.md").write_text(_valid_hallazgo_content(), encoding="utf-8")

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=lambda _: ExecutionResult(success=False, message="FAIL", tests_passed=False),
            )

            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.close_mode, "moved")
            self.assertTrue((root / "blocked" / "b.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_skips_hallazgo_with_existing_lock(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            hallazgo = in_progress / "c.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")
            (in_progress / "c.md.lock").write_text("locked", encoding="utf-8")

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
            )

            self.assertEqual(result.status, "idle")
            self.assertTrue(hallazgo.exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_atomic_lock_allows_single_holder_for_same_unit(self) -> None:
        root = self._local_tmp_root()
        first_lock = None
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            hallazgo = in_progress / "lock.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            first_lock = rcw._acquire_lock(hallazgo)
            self.assertIsNotNone(first_lock)
            second_lock = rcw._acquire_lock(hallazgo)
            self.assertIsNone(second_lock)
        finally:
            rcw._release_lock(first_lock)
            shutil.rmtree(root, ignore_errors=True)

    def test_lock_is_released_after_processing(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            hallazgo = in_progress / "d.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=lambda _: ExecutionResult(success=True, message="OK", tests_passed=True),
            )

            self.assertFalse((in_progress / "d.md.lock").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_destination_collision_is_resolved_with_incremental_suffix_and_releases_lock(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            done = root / "done"
            blocked = root / "blocked"
            in_progress.mkdir()
            done.mkdir()
            hallazgo = in_progress / "e.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")
            (done / "e.md").write_text("exists", encoding="utf-8")
            (done / "e-01.md").write_text("exists", encoding="utf-8")

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=done,
                blocked_dir=blocked,
                repo_root=root,
                executor=lambda _: ExecutionResult(success=True, message="OK", tests_passed=True),
            )

            self.assertEqual(result.status, "done")
            self.assertTrue((done / "e-02.md").exists())
            self.assertFalse((in_progress / "e.md.lock").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_processes_only_one_hallazgo_per_run(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            (in_progress / "f1.md").write_text(_valid_hallazgo_content(), encoding="utf-8")
            (in_progress / "f2.md").write_text(_valid_hallazgo_content(), encoding="utf-8")

            run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=lambda _: ExecutionResult(success=True, message="OK", tests_passed=True),
            )

            remaining = list(in_progress.glob("*.md"))
            self.assertEqual(len(remaining), 1)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_picks_oldest_hallazgo(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()

            oldest = in_progress / "old.md"
            newest = in_progress / "new.md"
            oldest.write_text(_valid_hallazgo_content(), encoding="utf-8")
            newest.write_text(_valid_hallazgo_content(), encoding="utf-8")

            old_ts = oldest.stat().st_mtime - 100
            new_ts = newest.stat().st_mtime
            os.utime(oldest, (old_ts, old_ts))
            os.utime(newest, (new_ts, new_ts))

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=lambda _: ExecutionResult(success=True, message="OK", tests_passed=True),
            )

            self.assertIsNotNone(result.hallazgo)
            self.assertTrue(result.hallazgo.endswith("old.md"))
            self.assertTrue((root / "done" / "old.md").exists())
            self.assertTrue((in_progress / "new.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_runs_real_flow_codex_and_pytest(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()

            tests_core = root / "tests" / "core"
            tests_core.mkdir(parents=True, exist_ok=True)
            (tests_core / "test_clarification_service.py").write_text(
                "def test_smoke():\n    assert True\n", encoding="utf-8"
            )
            hallazgo = in_progress / "real.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            captured_calls: list[list[str]] = []

            class _Result:
                def __init__(self, returncode: int = 0, stdout: str = "ok", stderr: str = "") -> None:
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            def _fake_run(cmd, capture_output, text, timeout, cwd, encoding=None, errors=None):
                _ = (capture_output, text, timeout, cwd, encoding, errors)
                captured_calls.append(cmd)
                if Path(cmd[0]).name.lower().startswith("codex"):
                    return _Result(returncode=0, stdout="codex-ok")
                return _Result(returncode=0, stdout="pytest-ok")

            with patch("factory.run_codex_worker.subprocess.run", _fake_run):
                result = run_codex_worker(
                    in_progress_dir=in_progress,
                    done_dir=root / "done",
                    blocked_dir=root / "blocked",
                    repo_root=root,
                )

            self.assertEqual(result.status, "done")
            self.assertTrue((root / "done" / "real.md").exists())
            self.assertTrue(Path(captured_calls[0][0]).name.lower().startswith("codex"))
            self.assertIn("-m", captured_calls[0])
            model_index = captured_calls[0].index("-m")
            self.assertEqual(captured_calls[0][model_index + 1], "gpt-5.4")
            self.assertIn("--full-auto", captured_calls[0])
            self.assertNotIn("-a", captured_calls[0])
            self.assertEqual(captured_calls[1][0], sys.executable)
            self.assertIn("pytest", captured_calls[1])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_uses_env_model_override(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            tests_core = root / "tests" / "core"
            tests_core.mkdir(parents=True, exist_ok=True)
            (tests_core / "test_clarification_service.py").write_text(
                "def test_smoke():\n    assert True\n", encoding="utf-8"
            )
            hallazgo = in_progress / "model-override.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            captured_calls: list[list[str]] = []

            class _Result:
                def __init__(self, returncode: int = 0, stdout: str = "ok", stderr: str = "") -> None:
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            def _fake_run(cmd, capture_output, text, timeout, cwd, encoding=None, errors=None):
                _ = (capture_output, text, timeout, cwd, encoding, errors)
                captured_calls.append(cmd)
                return _Result(returncode=0, stdout="ok")

            with (
                patch.dict(os.environ, {"SMARTPYME_CODEX_MODEL": "gpt-4.1"}, clear=False),
                patch("factory.run_codex_worker.subprocess.run", _fake_run),
            ):
                result = run_codex_worker(
                    in_progress_dir=in_progress,
                    done_dir=root / "done",
                    blocked_dir=root / "blocked",
                    repo_root=root,
                )

            self.assertEqual(result.status, "done")
            self.assertIn("-m", captured_calls[0])
            model_index = captured_calls[0].index("-m")
            self.assertEqual(captured_calls[0][model_index + 1], "gpt-4.1")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_blocks_when_codex_exec_fails(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            tests_core = root / "tests" / "core"
            tests_core.mkdir(parents=True, exist_ok=True)
            (tests_core / "test_clarification_service.py").write_text(
                "def test_smoke():\n    assert True\n", encoding="utf-8"
            )
            hallazgo = in_progress / "fail.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            class _Result:
                def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            def _fake_run(cmd, capture_output, text, timeout, cwd, encoding=None, errors=None):
                _ = (capture_output, text, timeout, cwd, encoding, errors)
                if Path(cmd[0]).name.lower().startswith("codex"):
                    return _Result(returncode=1, stderr="codex exploded")
                return _Result(returncode=0, stdout="pytest-ok")

            with patch("factory.run_codex_worker.subprocess.run", _fake_run):
                result = run_codex_worker(
                    in_progress_dir=in_progress,
                    done_dir=root / "done",
                    blocked_dir=root / "blocked",
                    repo_root=root,
                )

            self.assertEqual(result.status, "blocked")
            self.assertIn("CODEx_EXEC_ERROR", result.message)
            self.assertTrue((root / "blocked" / "fail.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_blocks_with_explicit_message_when_model_is_not_supported(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            tests_core = root / "tests" / "core"
            tests_core.mkdir(parents=True, exist_ok=True)
            (tests_core / "test_clarification_service.py").write_text(
                "def test_smoke():\n    assert True\n", encoding="utf-8"
            )
            hallazgo = in_progress / "model-fail.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            class _Result:
                def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            def _fake_run(cmd, capture_output, text, timeout, cwd, encoding=None, errors=None):
                _ = (cmd, capture_output, text, timeout, cwd, encoding, errors)
                return _Result(
                    returncode=1,
                    stderr="The 'gpt-5.2-codex' model is not supported when using Codex with a ChatGPT account.",
                )

            with patch("factory.run_codex_worker.subprocess.run", _fake_run):
                result = run_codex_worker(
                    in_progress_dir=in_progress,
                    done_dir=root / "done",
                    blocked_dir=root / "blocked",
                    repo_root=root,
                )

            self.assertEqual(result.status, "blocked")
            self.assertIn("CODEX_MODELO_NO_COMPATIBLE", result.message)
            self.assertIn("gpt-5.4", result.message)
            self.assertTrue((root / "blocked" / "model-fail.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_blocks_with_explicit_message_when_codex_missing(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            tests_core = root / "tests" / "core"
            tests_core.mkdir(parents=True, exist_ok=True)
            (tests_core / "test_clarification_service.py").write_text(
                "def test_smoke():\n    assert True\n", encoding="utf-8"
            )
            hallazgo = in_progress / "missing-codex.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            with patch("factory.run_codex_worker.shutil.which", return_value=None):
                result = run_codex_worker(
                    in_progress_dir=in_progress,
                    done_dir=root / "done",
                    blocked_dir=root / "blocked",
                    repo_root=root,
                )

            self.assertEqual(result.status, "blocked")
            self.assertIn("CODEX_BINARIO_NO_ENCONTRADO", result.message)
            self.assertTrue((root / "blocked" / "missing-codex.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_blocks_with_explicit_message_when_codex_times_out(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            tests_core = root / "tests" / "core"
            tests_core.mkdir(parents=True, exist_ok=True)
            (tests_core / "test_clarification_service.py").write_text(
                "def test_smoke():\n    assert True\n", encoding="utf-8"
            )
            hallazgo = in_progress / "timeout-codex.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            def _fake_run(cmd, capture_output, text, timeout, cwd, encoding=None, errors=None):
                _ = (cmd, capture_output, text, timeout, cwd, encoding, errors)
                raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout)

            with patch("factory.run_codex_worker.subprocess.run", _fake_run):
                result = run_codex_worker(
                    in_progress_dir=in_progress,
                    done_dir=root / "done",
                    blocked_dir=root / "blocked",
                    repo_root=root,
                )

            self.assertEqual(result.status, "blocked")
            self.assertIn("CODEX_TIMEOUT", result.message)
            self.assertTrue((root / "blocked" / "timeout-codex.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_blocks_when_no_minimum_tests_available(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            hallazgo = in_progress / "no-tests.md"
            hallazgo.write_text(
                """# HALLAZGO

## META
- id: HZ-test
- estado: pending
- modulo_objetivo: reconciliation

## OBJETIVO
Objetivo test.

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- app/core/reconciliation/service.py

## REGLAS_DE_EJECUCION
- fail-closed

## CRITERIO_DE_CIERRE
- test ok

## PREGUNTA_AL_OWNER
- null
""",
                encoding="utf-8",
            )

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
            )

            self.assertEqual(result.status, "blocked")
            self.assertIn("TESTS_MINIMOS_NO_DEFINIDOS", result.message)
            self.assertTrue((root / "blocked" / "no-tests.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_default_executor_uses_hallazgos_minimum_test_mapping(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            tests_core = root / "tests" / "core"
            tests_core.mkdir(parents=True, exist_ok=True)
            (tests_core / "test_hallazgos_service.py").write_text(
                "def test_smoke():\n    assert True\n", encoding="utf-8"
            )
            hallazgo = in_progress / "hallazgos.md"
            hallazgo.write_text(
                _valid_hallazgo_content(modulo_objetivo="hallazgos"),
                encoding="utf-8",
            )

            captured_calls: list[list[str]] = []

            class _Result:
                def __init__(self, returncode: int = 0, stdout: str = "ok", stderr: str = "") -> None:
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            def _fake_run(cmd, capture_output, text, timeout, cwd, encoding=None, errors=None):
                _ = (capture_output, text, timeout, cwd, encoding, errors)
                captured_calls.append(cmd)
                return _Result(returncode=0, stdout="ok")

            with patch("factory.run_codex_worker.subprocess.run", _fake_run):
                result = run_codex_worker(
                    in_progress_dir=in_progress,
                    done_dir=root / "done",
                    blocked_dir=root / "blocked",
                    repo_root=root,
                )

            self.assertEqual(result.status, "done")
            self.assertEqual(captured_calls[1][0], sys.executable)
            self.assertIn("tests/core/test_hallazgos_service.py", captured_calls[1])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_detect_test_targets_returns_hallazgos_mapping_without_exists_check(self) -> None:
        root = self._local_tmp_root()
        try:
            contract = rcw.HallazgoExecutionContract(
                modulo_objetivo="hallazgos",
                objetivo="Objetivo test.",
                target_paths=["app/core/hallazgos/service.py"],
            )
            targets = rcw._detect_test_targets(contract, root)
            self.assertEqual(targets, ["tests/core/test_hallazgos_service.py"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_worker_result_exposes_modulo_objetivo_cantera_origen_and_unit_id(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            (in_progress / "meta.md").write_text(
                _valid_hallazgo_content(
                    modulo_objetivo="reconciliation",
                    cantera_raiz="E:\\BuenosPasos\\smartcounter",
                    ruta_fuente="backend\\modules\\meli_reconciliation.py",
                ),
                encoding="utf-8",
            )

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=lambda _: ExecutionResult(success=True, message="OK", tests_passed=True),
            )

            self.assertEqual(result.status, "done")
            self.assertEqual(result.modulo_objetivo, "reconciliation")
            self.assertEqual(result.cantera_origen, "E:\\BuenosPasos\\smartcounter")
            self.assertEqual(result.ruta_fuente, "backend\\modules\\meli_reconciliation.py")
            self.assertEqual(result.unit_id, "meta:reconciliation")
            self.assertEqual(result.close_mode, "moved")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_missing_source_during_final_move_returns_done_by_other_worker(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            hallazgo = in_progress / "gone.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            def _executor(path: Path) -> ExecutionResult:
                path.unlink(missing_ok=True)
                return ExecutionResult(success=True, message="OK", tests_passed=True)

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=_executor,
            )

            self.assertEqual(result.status, "done")
            self.assertEqual(result.message, "DONE_BY_OTHER_WORKER")
            self.assertEqual(result.close_mode, "idempotent_missing_source")
            self.assertFalse((in_progress / "gone.md.lock").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_missing_source_during_final_move_returns_blocked_by_other_worker(self) -> None:
        root = self._local_tmp_root()
        try:
            in_progress = root / "in_progress"
            in_progress.mkdir()
            hallazgo = in_progress / "gone-blocked.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            def _executor(path: Path) -> ExecutionResult:
                path.unlink(missing_ok=True)
                return ExecutionResult(success=False, message="FAIL", tests_passed=False)

            result = run_codex_worker(
                in_progress_dir=in_progress,
                done_dir=root / "done",
                blocked_dir=root / "blocked",
                repo_root=root,
                executor=_executor,
            )

            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.message, "BLOCKED_BY_OTHER_WORKER")
            self.assertEqual(result.close_mode, "idempotent_missing_source")
            self.assertFalse((in_progress / "gone-blocked.md.lock").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
