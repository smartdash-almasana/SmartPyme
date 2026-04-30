import subprocess
from pathlib import Path

from factory.core.git_diff_detector import get_changed_paths, get_changed_paths_between


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init")
    _git(repo, "config", "user.name", "FM Test")
    _git(repo, "config", "user.email", "fm-test@example.com")


def _commit_all(repo: Path, message: str) -> str:
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def test_repo_without_git_returns_empty_list(tmp_path):
    (tmp_path / "file.txt").write_text("x", encoding="utf-8")

    assert get_changed_paths(tmp_path) == []
    assert get_changed_paths_between("HEAD~1", "HEAD", tmp_path) == []


def test_git_repo_without_changes_returns_empty_list(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("base", encoding="utf-8")
    _commit_all(tmp_path, "base")

    assert get_changed_paths(tmp_path) == []


def test_unstaged_file_is_detected(tmp_path):
    _init_repo(tmp_path)
    file_path = tmp_path / "tracked.txt"
    file_path.write_text("base", encoding="utf-8")
    _commit_all(tmp_path, "base")

    file_path.write_text("changed", encoding="utf-8")

    assert get_changed_paths(tmp_path) == ["tracked.txt"]


def test_staged_file_is_detected(tmp_path):
    _init_repo(tmp_path)
    file_path = tmp_path / "tracked.txt"
    file_path.write_text("base", encoding="utf-8")
    _commit_all(tmp_path, "base")

    file_path.write_text("changed", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")

    assert get_changed_paths(tmp_path) == ["tracked.txt"]


def test_untracked_file_is_detected(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "tracked.txt").write_text("base", encoding="utf-8")
    _commit_all(tmp_path, "base")

    (tmp_path / "new_file.txt").write_text("new", encoding="utf-8")

    assert get_changed_paths(tmp_path) == ["new_file.txt"]


def test_changed_paths_between_refs_detects_changed_file(tmp_path):
    _init_repo(tmp_path)
    file_path = tmp_path / "tracked.txt"
    file_path.write_text("base", encoding="utf-8")
    base_ref = _commit_all(tmp_path, "base")

    file_path.write_text("changed", encoding="utf-8")
    head_ref = _commit_all(tmp_path, "changed")

    assert get_changed_paths_between(base_ref, head_ref, tmp_path) == ["tracked.txt"]
