import io
import shutil
import sys
import time
import unittest
import uuid
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import factory.run_factory as rf


def _valid_hallazgo_content() -> str:
    return """# HALLAZGO

## META
- id: HZ-test
- estado: pending

## OBJETIVO
Objetivo de prueba.

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


class RunFactoryTests(unittest.TestCase):
    def _case_root(self) -> Path:
        base = Path(__file__).resolve().parents[2] / ".tmp" / "run_factory_tests"
        base.mkdir(parents=True, exist_ok=True)
        root = base / f"case_{uuid.uuid4().hex}"
        root.mkdir(parents=True, exist_ok=False)
        return root

    def _write_topology_catalog(self, root: Path) -> None:
        factory_dir = root / "factory"
        factory_dir.mkdir(parents=True, exist_ok=True)
        (factory_dir / "topology_catalog.json").write_text(
            """{
  "core_layers": {
    "clarification": {
      "target_files": ["app/core/clarification/service.py"]
    },
    "reconciliation": {
      "target_files": ["app/core/reconciliation/service.py"]
    }
  },
  "official_assembly_order": ["clarification", "reconciliation"],
  "canteras": [
    {
      "name": "allowed",
      "path_prefix": "E:/allowed",
      "possible_layers": ["clarification"]
    }
  ]
}""",
            encoding="utf-8",
        )

    def test_run_auditor_supports_model_and_multiple_rutas(self) -> None:
        root = self._case_root()
        try:
            auditor = root / "gemini_slice_auditor.py"
            auditor.write_text("print('ok')", encoding="utf-8")
            captured: dict[str, object] = {}

            class FakeResult:
                returncode = 0
                stderr = ""

            def fake_run(cmd, capture_output, text, timeout, encoding=None, errors=None):
                captured["encoding"] = encoding
                captured["errors"] = errors
                captured["cmd"] = cmd
                captured["timeout"] = timeout
                return FakeResult()

            with (
                patch.dict(rf.os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}, clear=False),
                patch.object(rf, "AUDITOR_PATH", auditor),
                patch.object(rf.subprocess, "run", fake_run),
            ):
                rf.run_auditor(
                    modulo="clarification",
                    rutas_fuente=["E:\\a.py", "E:\\b.py"],
                    repo_destino="E:\\BuenosPasos\\smartbridge\\SmartPyme",
                    model="gemini-2.5-pro",
                    timeout_seconds=123,
                )

            cmd = captured["cmd"]
            self.assertIn("--rutas-fuente", cmd)
            rutas_index = cmd.index("--rutas-fuente")
            self.assertEqual(cmd[rutas_index + 1 : rutas_index + 3], ["E:\\a.py", "E:\\b.py"])
            self.assertIn("--model", cmd)
            model_index = cmd.index("--model")
            self.assertEqual(cmd[model_index + 1], "gemini-2.5-pro")
            self.assertEqual(captured.get("timeout"), 123)
            self.assertEqual(captured.get("encoding"), "utf-8")
            self.assertEqual(captured.get("errors"), "replace")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_auditor_timeout_produces_explicit_error(self) -> None:
        root = self._case_root()
        try:
            auditor = root / "gemini_slice_auditor.py"
            auditor.write_text("print('ok')", encoding="utf-8")

            def fake_run(cmd, capture_output, text, timeout, encoding=None, errors=None):
                _ = (cmd, capture_output, text, timeout, encoding, errors)
                raise rf.subprocess.TimeoutExpired(cmd=["python"], timeout=timeout)

            with (
                patch.dict(rf.os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}, clear=False),
                patch.object(rf, "AUDITOR_PATH", auditor),
                patch.object(rf.subprocess, "run", fake_run),
            ):
                with self.assertRaisesRegex(RuntimeError, "AUDITOR_TIMEOUT"):
                    rf.run_auditor(
                        modulo="clarification",
                        rutas_fuente=["E:\\a.py"],
                        repo_destino="E:\\BuenosPasos\\smartbridge\\SmartPyme",
                        timeout_seconds=1,
                    )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_auditor_fails_fast_when_google_cloud_project_is_missing(self) -> None:
        root = self._case_root()
        try:
            auditor = root / "gemini_slice_auditor.py"
            auditor.write_text("print('ok')", encoding="utf-8")

            with (
                patch.dict(rf.os.environ, {}, clear=True),
                patch.object(rf, "AUDITOR_PATH", auditor),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "AUDITOR_ENV_MISSING: GOOGLE_CLOUD_PROJECT",
                ):
                    rf.run_auditor(
                        modulo="clarification",
                        rutas_fuente=["E:\\a.py"],
                        repo_destino="E:\\BuenosPasos\\smartbridge\\SmartPyme",
                    )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_move_hallazgo_resolves_collision_with_incremental_suffix(self) -> None:
        root = self._case_root()
        try:
            source = root / "pending" / "h1.md"
            target_dir = root / "blocked"
            target_dir.mkdir(parents=True)
            source.parent.mkdir(parents=True)
            source.write_text("x", encoding="utf-8")
            (target_dir / "h1.md").write_text("exists", encoding="utf-8")
            (target_dir / "h1-01.md").write_text("exists", encoding="utf-8")

            moved = rf.move_hallazgo(source, target_dir)
            self.assertEqual(moved.name, "h1-02.md")
            self.assertTrue((target_dir / "h1-02.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_detects_new_hallazgo_not_old(self) -> None:
        root = self._case_root()
        try:
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True)

            old_hallazgo = pending / "old.md"
            old_hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")
            time.sleep(0.01)

            def fake_auditor(modulo, rutas_fuente, repo_destino, model, timeout_seconds):
                _ = (modulo, rutas_fuente, repo_destino, model, timeout_seconds)
                new_hallazgo = pending / "new.md"
                new_hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            result = rf.run_factory(
                modo="execute_ready",
                modulo="clarification",
                rutas_fuente=["E:\\BuenosPasos\\smartbridge\\app\\services\\clarification_service.py"],
                repo_destino=str(root),
                pending_dir=pending,
                in_progress_dir=in_progress,
                blocked_dir=blocked,
                done_dir=done,
                repo_root=root,
                auditor_runner=fake_auditor,
            )

            self.assertEqual(result["estado"], "in_progress")
            self.assertEqual(Path(result["archivo"]).name, "new.md")
            self.assertTrue(old_hallazgo.exists())
            self.assertTrue((in_progress / "new.md").exists())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_main_supports_model_and_multiple_rutas(self) -> None:
        root = self._case_root()
        try:
            captured: dict[str, object] = {}

            def fake_run_factory(**kwargs):
                captured.update(kwargs)
                return {"estado": "pending", "archivo": "x.md", "motivo": "AUDIT_ONLY"}

            argv = [
                "run_factory.py",
                "--modo",
                "audit_only",
                "--modulo",
                "clarification",
                "--rutas-fuente",
                "E:\\r1.py",
                "E:\\r2.py",
                "--repo-destino",
                str(root),
                "--model",
                "gemini-2.5-flash",
                "--auditor-timeout-seconds",
                "77",
            ]

            output = io.StringIO()
            with (
                patch.object(rf, "run_factory", fake_run_factory),
                patch.object(sys, "argv", argv),
                redirect_stdout(output),
            ):
                exit_code = rf.main()

            self.assertEqual(exit_code, 0)
            self.assertEqual(captured["rutas_fuente"], ["E:\\r1.py", "E:\\r2.py"])
            self.assertEqual(captured["model"], "gemini-2.5-flash")
            self.assertEqual(captured["auditor_timeout_seconds"], 77)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_preserves_rutas_fuente_list(self) -> None:
        root = self._case_root()
        try:
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True)
            captured: dict[str, object] = {}

            def fake_auditor(modulo, rutas_fuente, repo_destino, model, timeout_seconds):
                captured["modulo"] = modulo
                captured["rutas_fuente"] = rutas_fuente
                captured["repo_destino"] = repo_destino
                captured["model"] = model
                captured["timeout_seconds"] = timeout_seconds
                (pending / "new.md").write_text(_valid_hallazgo_content(), encoding="utf-8")

            rutas = ["E:\\fuente_a.py", "E:\\fuente_b.py"]
            rf.run_factory(
                modo="execute_ready",
                modulo="clarification",
                rutas_fuente=rutas,
                repo_destino=str(root),
                model="gemini-2.5-pro",
                pending_dir=pending,
                in_progress_dir=in_progress,
                blocked_dir=blocked,
                done_dir=done,
                repo_root=root,
                auditor_runner=fake_auditor,
            )

            self.assertEqual(captured["rutas_fuente"], rutas)
            self.assertEqual(captured["model"], "gemini-2.5-pro")
            self.assertIsNone(captured["timeout_seconds"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_propagates_auditor_timeout_seconds(self) -> None:
        root = self._case_root()
        try:
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True)
            captured: dict[str, object] = {}

            def fake_auditor(modulo, rutas_fuente, repo_destino, model, timeout_seconds):
                captured["timeout_seconds"] = timeout_seconds
                (pending / "new.md").write_text(_valid_hallazgo_content(), encoding="utf-8")

            rf.run_factory(
                modo="execute_ready",
                modulo="clarification",
                rutas_fuente=["E:\\fuente_a.py"],
                repo_destino=str(root),
                pending_dir=pending,
                in_progress_dir=in_progress,
                blocked_dir=blocked,
                done_dir=done,
                repo_root=root,
                auditor_timeout_seconds=45,
                auditor_runner=fake_auditor,
            )

            self.assertEqual(captured["timeout_seconds"], 45)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_blocks_unknown_layer_when_topology_catalog_exists(self) -> None:
        root = self._case_root()
        try:
            self._write_topology_catalog(root)
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(ValueError, "CAPA_OBJETIVO_INVALIDA"):
                rf.run_factory(
                    modo="execute_ready",
                    modulo="validation",
                    rutas_fuente=["E:\\allowed\\repo"],
                    repo_destino=str(root),
                    pending_dir=pending,
                    in_progress_dir=in_progress,
                    blocked_dir=blocked,
                    done_dir=done,
                    repo_root=root,
                    auditor_runner=lambda *_: None,
                )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_blocks_cantera_not_allowed_for_layer(self) -> None:
        root = self._case_root()
        try:
            self._write_topology_catalog(root)
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(ValueError, "CANTERA_NO_HABILITADA_PARA_CAPA"):
                rf.run_factory(
                    modo="execute_ready",
                    modulo="clarification",
                    rutas_fuente=["E:\\forbidden\\repo"],
                    repo_destino=str(root),
                    pending_dir=pending,
                    in_progress_dir=in_progress,
                    blocked_dir=blocked,
                    done_dir=done,
                    repo_root=root,
                    auditor_runner=lambda *_: None,
                )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_process_pending_moves_valid_invalid_and_done(self) -> None:
        root = self._case_root()
        try:
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True)

            valid = pending / "valid.md"
            valid.write_text(_valid_hallazgo_content(), encoding="utf-8")

            invalid = pending / "invalid.md"
            invalid.write_text(
                """# HALLAZGO
## META
- id: HZ-invalid
## OBJETIVO
x
## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- src/core/bad.py
## REGLAS_DE_EJECUCION
- fail-closed
## CRITERIO_DE_CIERRE
- ok
## PREGUNTA_AL_OWNER
- null
""",
                encoding="utf-8",
            )

            done_file = pending / "done.md"
            done_file.write_text(
                _valid_hallazgo_content().replace("- estado: pending", "- estado: done"),
                encoding="utf-8",
            )

            summary = rf.process_pending_hallazgos(
                pending_dir=pending,
                in_progress_dir=in_progress,
                blocked_dir=blocked,
                done_dir=done,
                repo_root=root,
            )

            self.assertEqual(summary["total"], 3)
            self.assertEqual(summary["processed"], 3)
            self.assertEqual(len(summary["moved_to_in_progress"]), 1)
            self.assertEqual(len(summary["moved_to_done"]), 1)
            self.assertEqual(len(summary["moved_to_blocked"]), 1)
            self.assertTrue((in_progress / "valid.md").exists())
            self.assertTrue((done / "done.md").exists())
            self.assertTrue((blocked / "invalid.md").exists())
            self.assertFalse(list(pending.glob("*.md")))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_main_requires_modulo_and_rutas_for_execute_ready(self) -> None:
        root = self._case_root()
        try:
            argv = [
                "run_factory.py",
                "--modo",
                "execute_ready",
                "--repo-destino",
                str(root),
            ]

            output = io.StringIO()
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                exit_code = rf.main()

            out = output.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("MODULO_REQUERIDO", out)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_validate_hallazgo_accepts_target_path_with_backticks(self) -> None:
        root = self._case_root()
        try:
            hallazgo = root / "hallazgo.md"
            hallazgo.write_text(
                """# HALLAZGO

## META
- id: HZ-bt
- estado: pending

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- `app\\core\\reconciliation\\models.py`

## REGLAS_DE_EJECUCION
- fail-closed

## CRITERIO_DE_CIERRE
- ok

## PREGUNTA_AL_OWNER
- null
""",
                encoding="utf-8",
            )

            is_valid, reason = rf.validate_hallazgo(hallazgo, repo_root=root)
            self.assertTrue(is_valid)
            self.assertEqual(reason, "VALIDACION_OK")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_validate_hallazgo_requires_cantera_raiz_when_flag_enabled(self) -> None:
        root = self._case_root()
        try:
            hallazgo = root / "hallazgo_no_cantera.md"
            hallazgo.write_text(_valid_hallazgo_content(), encoding="utf-8")

            is_valid, reason = rf.validate_hallazgo(
                hallazgo,
                repo_root=root,
                require_cantera_raiz=True,
            )
            self.assertFalse(is_valid)
            self.assertIn("CANTERA_RAIZ_FALTANTE", reason)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_validate_hallazgo_accepts_simple_markdown_link_wrapper(self) -> None:
        root = self._case_root()
        try:
            hallazgo = root / "hallazgo_link.md"
            hallazgo.write_text(
                """# HALLAZGO

## META
- id: HZ-link
- estado: pending

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- [models](app/core/reconciliation/models.py)

## REGLAS_DE_EJECUCION
- fail-closed

## CRITERIO_DE_CIERRE
- ok

## PREGUNTA_AL_OWNER
- null
""",
                encoding="utf-8",
            )

            is_valid, reason = rf.validate_hallazgo(hallazgo, repo_root=root)
            self.assertTrue(is_valid)
            self.assertEqual(reason, "VALIDACION_OK")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_prefixes_blocked_reason_for_validation_failures(self) -> None:
        root = self._case_root()
        try:
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True, exist_ok=True)
            def fake_auditor(*_: object) -> None:
                (pending / "blocked.md").write_text(
                    """# HALLAZGO
## META
- id: HZ-blocked
- estado: pending
- modulo_objetivo: reconciliation
## OBJETIVO
objetivo
## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- app/core/reconciliation/service.py
## REGLAS_DE_EJECUCION
- fail-closed
## CRITERIO_DE_CIERRE
- ok
## PREGUNTA_AL_OWNER
- ¿falta decision?
""",
                    encoding="utf-8",
                )

            result = rf.run_factory(
                modo="execute_ready",
                modulo="reconciliation",
                rutas_fuente=["E:\\allowed\\repo"],
                repo_destino=str(root),
                pending_dir=pending,
                in_progress_dir=in_progress,
                blocked_dir=blocked,
                done_dir=done,
                repo_root=root,
                auditor_runner=fake_auditor,
            )

            self.assertEqual(result["estado"], "blocked")
            self.assertIn("VALIDACION_BLOCKED:", result["motivo"])
            self.assertIn("PREGUNTA_ABIERTA", result["motivo"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_fail_closed_when_commit_mode_is_not_disabled(self) -> None:
        root = self._case_root()
        try:
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(ValueError, "COMMIT_MODE_NO_IMPLEMENTADO"):
                rf.run_factory(
                    modo="execute_ready",
                    modulo="clarification",
                    rutas_fuente=["E:\\allowed\\repo"],
                    repo_destino=str(root),
                    commit_mode="auto_commit",
                    pending_dir=pending,
                    in_progress_dir=in_progress,
                    blocked_dir=blocked,
                    done_dir=done,
                    repo_root=root,
                    auditor_runner=lambda *_: None,
                )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_factory_execute_ready_blocks_if_cantera_raiz_cannot_be_written(self) -> None:
        root = self._case_root()
        try:
            pending = root / "hallazgos" / "pending"
            in_progress = root / "hallazgos" / "in_progress"
            blocked = root / "hallazgos" / "blocked"
            done = root / "hallazgos" / "done"
            pending.mkdir(parents=True, exist_ok=True)

            def fake_auditor(*_: object) -> None:
                (pending / "no-cantera.md").write_text(_valid_hallazgo_content(), encoding="utf-8")

            with patch.object(rf, "_upsert_meta_field", side_effect=lambda content, *_: content):
                result = rf.run_factory(
                    modo="execute_ready",
                    modulo="clarification",
                    rutas_fuente=["E:\\allowed\\repo"],
                    repo_destino=str(root),
                    pending_dir=pending,
                    in_progress_dir=in_progress,
                    blocked_dir=blocked,
                    done_dir=done,
                    repo_root=root,
                    auditor_runner=fake_auditor,
                )

            self.assertEqual(result["estado"], "blocked")
            self.assertIn("VALIDACION_BLOCKED:", result["motivo"])
            self.assertIn("CANTERA_RAIZ_FALTANTE", result["motivo"])
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
