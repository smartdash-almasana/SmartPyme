from __future__ import annotations

import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from factory.mcp_bridge.tools import register_tools

CLIENT_NAME = os.getenv("MCP_CLIENT_ID") or os.getenv("MCP_CLIENT", "unknown")
LOG_PATH = REPO_ROOT / "factory" / "logs" / "mcp_bridge.log.jsonl"

mcp = FastMCP("SmartPyme-Bridge")

register_tools(
    mcp,
    repo_root=REPO_ROOT,
    client_name=CLIENT_NAME,
    log_path=LOG_PATH,
)


if __name__ == "__main__":
    mcp.run()
