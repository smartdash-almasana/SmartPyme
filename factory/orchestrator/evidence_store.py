from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvidenceStore:
    repo_root: Path

    @property
    def evidence_root(self) -> Path:
        return self.repo_root / "factory" / "evidence"

    def evidence_dir(self, hallazgo_id: str) -> Path:
        safe_id = _safe_hallazgo_id(hallazgo_id)
        directory = self.evidence_root / safe_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def write_builder_report(self, hallazgo_id: str, content: str) -> Path:
        return self.write_text(hallazgo_id, "builder_report.md", content)

    def write_auditor_report(self, hallazgo_id: str, content: str) -> Path:
        return self.write_text(hallazgo_id, "auditor_report.md", content)

    def write_status(self, hallazgo_id: str, data: dict[str, Any]) -> Path:
        path = self.evidence_dir(hallazgo_id) / "status.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return path

    def write_text(self, hallazgo_id: str, filename: str, content: str) -> Path:
        path = self.evidence_dir(hallazgo_id) / filename
        path.write_text(content, encoding="utf-8")
        return path


def _safe_hallazgo_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in value.strip())
    return cleaned or "unknown-hallazgo"


def write_builder_report(hallazgo_id: str, content: str, repo_root: str | Path = ".") -> Path:
    return EvidenceStore(Path(repo_root)).write_builder_report(hallazgo_id, content)


def write_auditor_report(hallazgo_id: str, content: str, repo_root: str | Path = ".") -> Path:
    return EvidenceStore(Path(repo_root)).write_auditor_report(hallazgo_id, content)


def write_status(hallazgo_id: str, data: dict[str, Any], repo_root: str | Path = ".") -> Path:
    return EvidenceStore(Path(repo_root)).write_status(hallazgo_id, data)


def write_text(hallazgo_id: str, filename: str, content: str, repo_root: str | Path = ".") -> Path:
    return EvidenceStore(Path(repo_root)).write_text(hallazgo_id, filename, content)
