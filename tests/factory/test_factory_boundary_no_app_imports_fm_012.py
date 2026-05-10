from pathlib import Path

FORBIDDEN_IMPORTS = (
    "from app.",
    "import app.",
)

# Directorios excluidos del boundary check.
# factory/adapters/app_bridge/ es el adapter explícito hacia el runtime de SmartPyme app.
# Es el único punto de acoplamiento permitido por diseño: core desacoplado, adapter acoplado.
EXCLUDED_DIRS = {
    "app_bridge",
}


def test_decoupled_factory_package_does_not_import_smartpyme_app_runtime():
    factory_root = Path("factory")
    checked_files = [
        path
        for path in factory_root.rglob("*.py")
        if "__pycache__" not in path.parts
        and not any(part in EXCLUDED_DIRS for part in path.parts)
    ]

    assert checked_files, "factory package python files must exist"

    violations = []
    for path in checked_files:
        content = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_IMPORTS:
            if forbidden in content:
                violations.append(f"{path}: contains {forbidden}")

    assert violations == []
