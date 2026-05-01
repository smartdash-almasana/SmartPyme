from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HallazgoStore:
    repo_root: Path

    @property
    def hallazgos_dir(self) -> Path:
        return self.repo_root / "factory" / "hallazgos"

    @property
    def pending_dir(self) -> Path:
        return self.hallazgos_dir / "pending"

    @property
    def in_progress_dir(self) -> Path:
        return self.hallazgos_dir / "in_progress"

    @property
    def done_dir(self) -> Path:
        return self.hallazgos_dir / "done"

    @property
    def blocked_dir(self) -> Path:
        return self.hallazgos_dir / "blocked"

    def ensure_dirs(self) -> None:
        for directory in (
            self.pending_dir,
            self.in_progress_dir,
            self.done_dir,
            self.blocked_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def list_pending(self) -> list[Path]:
        self.ensure_dirs()
        return sorted(p for p in self.pending_dir.glob("*.md") if p.is_file())

    def read_hallazgo(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def move_to_in_progress(self, path: Path) -> Path:
        return self._move_no_overwrite(path, self.in_progress_dir)

    def move_to_done(self, path: Path) -> Path:
        return self._move_no_overwrite(path, self.done_dir)

    def move_to_blocked(self, path: Path, reason: str | None = None) -> Path:
        target = self._move_no_overwrite(path, self.blocked_dir)
        if reason:
            reason_path = target.with_suffix(target.suffix + ".reason.txt")
            reason_path.write_text(reason, encoding="utf-8")
        return target

    def _move_no_overwrite(self, source: Path, destination_dir: Path) -> Path:
        self.ensure_dirs()
        if not source.exists():
            raise FileNotFoundError(str(source))
        destination_dir.mkdir(parents=True, exist_ok=True)
        target = _resolve_unique_destination(destination_dir, source.name)
        source.rename(target)
        return target


def _resolve_unique_destination(destination_dir: Path, original_name: str) -> Path:
    candidate = destination_dir / original_name
    if not candidate.exists():
        return candidate

    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    counter = 1
    while True:
        candidate = destination_dir / f"{stem}-{counter:02d}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def list_pending(repo_root: str | Path = ".") -> list[Path]:
    return HallazgoStore(Path(repo_root)).list_pending()


def read_hallazgo(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def move_to_in_progress(path: str | Path, repo_root: str | Path = ".") -> Path:
    return HallazgoStore(Path(repo_root)).move_to_in_progress(Path(path))


def move_to_done(path: str | Path, repo_root: str | Path = ".") -> Path:
    return HallazgoStore(Path(repo_root)).move_to_done(Path(path))


def move_to_blocked(
    path: str | Path,
    reason: str | None = None,
    repo_root: str | Path = ".",
) -> Path:
    return HallazgoStore(Path(repo_root)).move_to_blocked(Path(path), reason=reason)
