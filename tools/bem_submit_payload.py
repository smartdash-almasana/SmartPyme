from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from app.services.bem_client import BemClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Submit payload JSON to BEM workflow.")
    parser.add_argument("--workflow-id", required=True, help="BEM workflow id")
    parser.add_argument("--payload-file", required=True, help="Path to payload JSON file")
    parser.add_argument("--base-url", default="https://api.bem.ai", help="BEM base URL")
    parser.add_argument("--api-key", default=None, help="BEM API key")
    return parser


def _load_payload(path_value: str) -> dict[str, Any]:
    path = Path(path_value)
    if not path.exists() or not path.is_file():
        raise ValueError(f"payload file not found: {path}")

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read payload file: {path}") from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON payload file: {path}") from exc

    if not isinstance(data, dict) or not data:
        raise ValueError("payload JSON must be a non-empty object")
    return data


def run(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    workflow_id = args.workflow_id.strip() if isinstance(args.workflow_id, str) else ""
    if not workflow_id:
        print("workflow_id is required", file=sys.stderr)
        return 2

    try:
        payload = _load_payload(args.payload_file)
        client = BemClient(api_key=args.api_key, base_url=args.base_url)
        response = client.submit_payload(workflow_id=workflow_id, payload=payload)
    except (ValueError, TypeError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
