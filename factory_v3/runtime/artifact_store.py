from __future__ import annotations

from pathlib import Path


class ArtifactStore:
    def __init__(self, root_path: str = "factory_v3/runtime/artifacts"):
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, relative_path: str) -> Path:
        clean_relative = relative_path.lstrip("/")
        resolved = (self.root_path / clean_relative).resolve()

        if self.root_path.resolve() not in resolved.parents and resolved != self.root_path.resolve():
            raise ValueError("artifact path escapes artifact store root")

        return resolved

    def write_text(self, relative_path: str, content: str) -> Path:
        target = self.resolve_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def read_text(self, relative_path: str) -> str:
        target = self.resolve_path(relative_path)
        return target.read_text(encoding="utf-8")

    def exists(self, relative_path: str) -> bool:
        target = self.resolve_path(relative_path)
        return target.exists()

    def delete(self, relative_path: str) -> None:
        target = self.resolve_path(relative_path)

        if target.exists():
            target.unlink()
