from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


MAX_RECENT_FILES = 5
MAX_SECTION_CHARS = 4000


@dataclass(frozen=True)
class RecentFile:
    path: Path
    modified_at: str


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_optional_text(path: Path, max_chars: int = MAX_SECTION_CHARS) -> str:
    if not path.is_file():
        return f"NO_ENCONTRADO: {path.as_posix()}"

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) <= max_chars:
        return text or "(archivo vacio)"
    return f"{text[:max_chars].rstrip()}\n... [TRUNCADO]"


def _recent_files(root: Path, limit: int = MAX_RECENT_FILES) -> list[RecentFile]:
    if not root.is_dir():
        return []

    files = [path for path in root.rglob("*") if path.is_file()]
    files.sort(key=lambda path: (path.stat().st_mtime, path.as_posix()), reverse=True)

    recent: list[RecentFile] = []
    for path in files[:limit]:
        modified_at = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        recent.append(
            RecentFile(
                path=path,
                modified_at=modified_at.replace(microsecond=0).isoformat(),
            )
        )
    return recent


def _format_recent_files(repo_root: Path, title: str, root: Path) -> str:
    recent = _recent_files(root)
    lines = [f"## {title}"]
    if not recent:
        lines.append(f"NO_ENCONTRADO_O_VACIO: {root.relative_to(repo_root).as_posix()}")
        return "\n".join(lines)

    for item in recent:
        lines.append(f"- {item.modified_at} {item.path.relative_to(repo_root).as_posix()}")
    return "\n".join(lines)


def _run_git(repo_root: Path, args: list[str]) -> str:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return f"ERROR git {' '.join(args)}: {output or f'codigo {result.returncode}'}"
    return output or "(sin salida)"


def build_audit_context(repo_root: Path) -> str:
    repo_root = repo_root.resolve()
    control = repo_root / "factory" / "control"

    sections = [
        "# SMARTPYME AUDIT CONTEXT BUNDLE",
        f"generated_at: {_utc_timestamp()}",
        f"repo_root: {repo_root.as_posix()}",
        "",
        "## GATE_ACTUAL",
        _read_optional_text(control / "AUDIT_GATE.md"),
        "",
        "## ESTADO_FACTORY",
        _read_optional_text(control / "FACTORY_STATUS.md"),
        "",
        "## ULTIMA_TAREA",
        _read_optional_text(control / "NEXT_CYCLE.md"),
        "",
        _format_recent_files(repo_root, "EVIDENCIA_RECIENTE", repo_root / "factory" / "evidence"),
        "",
        _format_recent_files(repo_root, "BUGS_RECIENTES", repo_root / "factory" / "bugs"),
        "",
        "## GIT_STATUS_SHORT",
        _run_git(repo_root, ["status", "--short"]),
        "",
        "## GIT_LOG_ONELINE_5",
        _run_git(repo_root, ["log", "--oneline", "-5"]),
        "",
    ]
    return "\n".join(sections)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera un contexto tecnico compacto para auditoria humana SmartPyme."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Ruta de salida. Si se omite, imprime el bundle por stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = build_audit_context(Path.cwd())

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(context, encoding="utf-8")
        return 0

    print(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
