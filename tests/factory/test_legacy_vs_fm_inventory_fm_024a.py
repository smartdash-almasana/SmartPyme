from pathlib import Path

INVENTORY_PATH = Path("docs/factory_legacy_vs_fm_inventory.md")


def test_legacy_vs_fm_inventory_document_exists_and_names_active_fm_paths():
    assert INVENTORY_PATH.exists()
    content = INVENTORY_PATH.read_text(encoding="utf-8")

    assert "FM_024A — Legacy Factory Inventory" in content
    assert "FM factory nueva — ACTIVA" in content
    assert "LEGACY factory — DEPRECATED PARA EL PLANO SUPEROWNER" in content
    assert "factory/core/task_spec.py" in content
    assert "factory/core/task_spec_store.py" in content
    assert "factory/core/task_spec_runner.py" in content
    assert "factory/core/run_report.py" in content
    assert "factory/core/task_spec_templates.py" in content
    assert "factory/adapters/telegram_superowner_adapter.py" in content


def test_legacy_vs_fm_inventory_names_legacy_paths_as_deprecated():
    content = INVENTORY_PATH.read_text(encoding="utf-8")

    assert "factory/run_factory.py" in content
    assert "factory/continuous_factory.py" in content
    assert "factory/run_codex_worker.py" in content
    assert "factory/hallazgos/" in content
    assert "No usar como fuente de verdad para nuevos ciclos FM" in content


def test_legacy_vs_fm_inventory_defines_no_mix_rules():
    content = INVENTORY_PATH.read_text(encoding="utf-8")

    assert "Reglas de no mezcla" in content
    assert "`factory/core/*` no debe importar desde `app/*`" in content
    assert "TaskSpecStore" in content
    assert "TaskSpecRunner" in content
    assert "tests/factory/test_*_fm_*.py" in content
    assert "factory/evidence/taskspecs/run_reports/" in content


def test_legacy_vs_fm_inventory_declares_branch_and_audit_scope():
    content = INVENTORY_PATH.read_text(encoding="utf-8")

    assert "Branch activa: factory/ts-006-jobs-sovereign-persistence" in content
    assert "Una auditoría de la factoría nueva debe comprobar como mínimo" in content
    assert "tests/factory/test_enqueue_template_fm_023.py" in content
