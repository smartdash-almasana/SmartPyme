from __future__ import annotations

import subprocess
from pathlib import Path


def get_changed_paths(repo_dir: str | Path = ".") -> list[str]:
    repo_path = Path(repo_dir)
    changed_paths: list[str] = []
    changed_paths.extend(_run_git(["diff", "--name-only"], repo_path))
    changed_paths.extend(_run_git(["diff", "--name-only", "--cached"], repo_path))
    changed_paths.extend(_run_git(["ls-files", "--others", "--exclude-standard"], repo_path))
    return sorted(set(changed_paths))


def get_changed_paths_between(
    base_ref: str,
    head_ref: str = "HEAD",
    repo_dir: str | Path = ".",
) -> list[str]:
    if not base_ref.strip() or not head_ref.strip():
        return []
    return sorted(set(_run_git(["diff", "--name-only", base_ref, head_ref], Path(repo_dir))))


def _run_git(args: list[str], repo_dir: Path) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [
        line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()
    ]
