from pathlib import Path


FORBIDDEN_IMPORTS = (
    "from app.",
    "import app.",
)


def test_decoupled_factory_package_does_not_import_smartpyme_app_runtime():
    factory_root = Path("factory")
    checked_files = [
        path
        for path in factory_root.rglob("*.py")
        if "__pycache__" not in path.parts
    ]

    assert checked_files, "factory package python files must exist"

    violations = []
    for path in checked_files:
        content = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_IMPORTS:
            if forbidden in content:
                violations.append(f"{path}: contains {forbidden}")

    assert violations == []
