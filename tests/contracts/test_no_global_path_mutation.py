from __future__ import annotations

from pathlib import Path


ALLOW_TOKEN = "LEGACY_ALLOWED_GLOBAL_PATH_MUTATION"
FORBIDDEN_PATTERNS = (
    ".Path = lambda",
    ".Path = ",
    "Path = lambda",
)
SKIP_DIR_NAMES = {".venv", "__pycache__", ".pytest_cache", "tmp"}


def _should_skip(path: Path) -> bool:
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def test_no_global_path_mutation_in_tests() -> None:
    tests_root = Path("tests")
    violations: list[str] = []

    for file_path in tests_root.rglob("*.py"):
        if _should_skip(file_path):
            continue
        if file_path.resolve() == Path(__file__).resolve():
            continue

        lines = file_path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            if ALLOW_TOKEN in line:
                continue
            if any(pattern in line for pattern in FORBIDDEN_PATTERNS):
                rel = file_path.as_posix()
                violations.append(f"{rel}:{line_no}: {line.strip()}")

    assert not violations, (
        "Detected forbidden global Path mutation patterns in tests:\n"
        + "\n".join(violations)
    )
