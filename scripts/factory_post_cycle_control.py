#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CONTRACTS = [
    "docs/specs/CORE_DATA_CONTRACT_AND_HALLAZGOS.md",
    "docs/factory/HERMES_CODEX_GEMINI_GOVERNANCE.md",
    "docs/factory/ANTI_DERIVA_PRIORITY_QA_LOOP.md",
    "docs/factory/TECH_SPEC_QUEUE.md",
    "AGENTS.md",
    "CODEX.md",
    "GEMINI.md",
]

DECISION_EXIT_CODES = {
    "CORRECTO": 0,
    "BLOCKED": 20,
    "NO_VALIDADO": 30,
}


def run(repo: Path, cmd: list[str]) -> str:
    p = subprocess.run(cmd, cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout.strip()


def latest_evidence(repo: Path) -> Path:
    root = repo / "factory" / "evidence"
    root.mkdir(parents=True, exist_ok=True)
    dirs = [p for p in root.iterdir() if p.is_dir()]
    if dirs:
        return max(dirs, key=lambda p: p.stat().st_mtime)
    d = root / ("post_cycle_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_verdict(text: str) -> str | None:
    lines = [line.strip().upper() for line in text.splitlines()]
    for idx, line in enumerate(lines):
        if line == "VEREDICTO":
            for candidate in lines[idx + 1 : idx + 8]:
                if not candidate or candidate.startswith("`"):
                    continue
                if "BLOCKED" in candidate:
                    return "BLOCKED"
                if candidate == "CORRECTO" or candidate.startswith("CORRECTO"):
                    return "CORRECTO"
                if "NO_VALIDADO" in candidate or "NO VALIDADO" in candidate:
                    return "NO_VALIDADO"
                break
    return None


def infer_decision(evidence: Path, returncode: int | None) -> str:
    text = read(evidence / "codex_output.txt") + "\n" + read(evidence / "decision.txt")
    verdict = extract_verdict(text)
    if verdict:
        return verdict

    upper = text.upper()
    if "BLOCKED_REPO" in upper or "BLOCKED_" in upper:
        return "BLOCKED"
    if returncode not in (None, 0):
        return "NO_VALIDADO"
    return "NO_VALIDADO"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--codex-returncode", type=int, default=None)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    evidence = latest_evidence(repo)
    result = infer_decision(evidence, args.codex_returncode)
    now = datetime.now(timezone.utc).isoformat()
    status = run(repo, ["git", "status", "--short"])
    missing = [c for c in CONTRACTS if not (repo / c).exists()]
    anti_status = "PASS" if not missing and result == "CORRECTO" else "WARNING"

    (evidence / "qa_report.md").write_text(
        f"# QA REPORT\n\ncreated_at: {now}\ndecision: {result}\n\n## git status\n```text\n{status or '<clean>'}\n```\n",
        encoding="utf-8",
    )
    (evidence / "anti_deriva_check.md").write_text(
        "# ANTI DERIVA CHECK\n\n"
        f"created_at: {now}\nstatus: {anti_status}\n\n"
        + "\n".join(f"- {c}: {'OK' if (repo / c).exists() else 'MISSING'}" for c in CONTRACTS)
        + "\n",
        encoding="utf-8",
    )
    (evidence / "priority_update.md").write_text(
        f"# PRIORITY UPDATE\n\ncreated_at: {now}\nlast_cycle_result: {result}\n\n"
        "1. core-reconciliacion-v1\n"
        "2. anti-deriva-priority-qa-loop-v1\n"
        "3. modelo canonico de hallazgos\n"
        "4. normalizacion tabular\n",
        encoding="utf-8",
    )
    board = repo / "factory" / "control" / "PRIORITY_BOARD.md"
    board.parent.mkdir(parents=True, exist_ok=True)
    board.write_text(
        f"# PRIORITY BOARD\n\nupdated_at: {now}\nlast_cycle_result: {result}\n\n"
        "1. core-reconciliacion-v1\n"
        "2. anti-deriva-priority-qa-loop-v1\n"
        "3. modelo canonico de hallazgos\n"
        "4. normalizacion tabular\n",
        encoding="utf-8",
    )
    exit_code = DECISION_EXIT_CODES.get(result, 30)
    print(f"POST_CYCLE_CONTROL={evidence}")
    print(f"POST_CYCLE_DECISION={result}")
    print(f"POST_CYCLE_EXIT_CODE={exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
