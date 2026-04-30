#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

BROKEN_SERVER_NAME = "smartpyme_bridge"
BROKEN_PATH_FRAGMENT = "/home/neoalmasana/SmartPyme/mcp_smartpyme_bridge.py"


def main() -> int:
    config_path = Path(os.environ.get("HERMES_CONFIG_PATH", "~/.hermes/config.yaml")).expanduser()
    if not config_path.exists():
        raise SystemExit(f"ERROR_MISSING_HERMES_CONFIG: {config_path}")

    data = yaml.safe_load(config_path.read_text(encoding="utf-8", errors="replace")) or {}
    if not isinstance(data, dict):
        raise SystemExit("ERROR_INVALID_HERMES_CONFIG")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = config_path.with_name(f"{config_path.name}.bak.disable-smartpyme-mcp-{stamp}")
    shutil.copy2(config_path, backup)

    changed_paths: list[str] = []
    disabled_entries: list[str] = []

    _remove_named_server(data, ["mcp", "servers"], changed_paths, disabled_entries)
    _remove_named_server(data, ["mcp_servers"], changed_paths, disabled_entries)
    _remove_named_server(data, ["tools", "mcp", "servers"], changed_paths, disabled_entries)
    _remove_named_server(data, ["toolsets", "mcp", "servers"], changed_paths, disabled_entries)

    # Fallback recursive cleanup: remove any dict key named smartpyme_bridge, and
    # remove list entries that explicitly reference the old broken script path.
    recursive_changed = _recursive_remove_broken_mcp(data, path="root", disabled_entries=disabled_entries)
    changed_paths.extend(recursive_changed)

    if changed_paths:
        config_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print("SMARTPYME_MCP_BRIDGE_DISABLE_DONE")
    print(f"config={config_path}")
    print(f"backup={backup}")
    print(f"changed={bool(changed_paths)}")
    print("changed_paths:")
    for item in changed_paths:
        print(f"- {item}")
    print("disabled_entries:")
    for item in disabled_entries:
        print(f"- {item}")
    return 0


def _remove_named_server(
    data: dict[str, Any],
    path: list[str],
    changed_paths: list[str],
    disabled_entries: list[str],
) -> None:
    parent: Any = data
    for key in path[:-1]:
        if not isinstance(parent, dict) or key not in parent:
            return
        parent = parent[key]
    final_key = path[-1]
    if not isinstance(parent, dict) or final_key not in parent:
        return
    servers = parent[final_key]
    if isinstance(servers, dict) and BROKEN_SERVER_NAME in servers:
        disabled_entries.append(f"{'.'.join(path)}.{BROKEN_SERVER_NAME}")
        del servers[BROKEN_SERVER_NAME]
        changed_paths.append(".".join(path))


def _recursive_remove_broken_mcp(node: Any, path: str, disabled_entries: list[str]) -> list[str]:
    changed: list[str] = []
    if isinstance(node, dict):
        if BROKEN_SERVER_NAME in node:
            disabled_entries.append(f"{path}.{BROKEN_SERVER_NAME}")
            del node[BROKEN_SERVER_NAME]
            changed.append(path)
        for key, value in list(node.items()):
            child_path = f"{path}.{key}"
            child_changes = _recursive_remove_broken_mcp(value, child_path, disabled_entries)
            changed.extend(child_changes)
    elif isinstance(node, list):
        kept = []
        removed = False
        for index, item in enumerate(node):
            if _references_broken_bridge(item):
                disabled_entries.append(f"{path}[{index}]")
                removed = True
                continue
            child_changes = _recursive_remove_broken_mcp(item, f"{path}[{index}]", disabled_entries)
            changed.extend(child_changes)
            kept.append(item)
        if removed:
            node[:] = kept
            changed.append(path)
    return changed


def _references_broken_bridge(item: Any) -> bool:
    text = yaml.safe_dump(item, allow_unicode=True, sort_keys=False) if not isinstance(item, str) else item
    return BROKEN_SERVER_NAME in text or BROKEN_PATH_FRAGMENT in text


if __name__ == "__main__":
    raise SystemExit(main())
