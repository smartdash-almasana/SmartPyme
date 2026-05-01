from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_audit_context.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_audit_context", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_context_tolerates_missing_control_and_recent_dirs(tmp_path, monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_run_git", lambda repo_root, args: "git-ok")

    context = module.build_audit_context(tmp_path)

    assert "## GATE_ACTUAL" in context
    assert "NO_ENCONTRADO: " in context
    assert "factory/control/AUDIT_GATE.md" in context
    assert "## ESTADO_FACTORY" in context
    assert "factory/control/FACTORY_STATUS.md" in context
    assert "## ULTIMA_TAREA" in context
    assert "factory/control/NEXT_CYCLE.md" in context
    assert "NO_ENCONTRADO_O_VACIO: factory/evidence" in context
    assert "NO_ENCONTRADO_O_VACIO: factory/bugs" in context
    assert context.count("git-ok") == 2


def test_recent_evidence_and_bugs_are_limited_to_five(tmp_path, monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_run_git", lambda repo_root, args: "git-ok")

    evidence = tmp_path / "factory" / "evidence"
    bugs = tmp_path / "factory" / "bugs"
    evidence.mkdir(parents=True)
    bugs.mkdir(parents=True)
    for index in range(7):
        (evidence / f"evidence-{index}.txt").write_text(str(index), encoding="utf-8")
        (bugs / f"bug-{index}.md").write_text(str(index), encoding="utf-8")

    context = module.build_audit_context(tmp_path)

    assert context.count("factory/evidence/evidence-") == 5
    assert context.count("factory/bugs/bug-") == 5


def test_context_does_not_write_files_without_output(tmp_path, monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_run_git", lambda repo_root, args: "git-ok")

    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    context = module.build_audit_context(tmp_path)
    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    assert context.startswith("# SMARTPYME AUDIT CONTEXT BUNDLE")
    assert after == before


def test_main_writes_only_requested_output(tmp_path, monkeypatch):
    module = _load_module()
    output = tmp_path / "out" / "audit.txt"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "_run_git", lambda repo_root, args: "git-ok")
    monkeypatch.setattr(module, "parse_args", lambda: type("Args", (), {"output": output})())

    result = module.main()

    assert result == 0
    assert output.is_file()
    assert output.read_text(encoding="utf-8").startswith("# SMARTPYME AUDIT CONTEXT BUNDLE")
    written = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert written == ["out", "out/audit.txt"]
