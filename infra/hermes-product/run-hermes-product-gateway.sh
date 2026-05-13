#!/usr/bin/env bash
set -euo pipefail

export HERMES_HOME="${HERMES_PRODUCT_HOME:-/home/neoalmasana/.hermes-smartpyme-product}"
export SMARTPYME_REPO="${SMARTPYME_REPO:-/opt/smartpyme-factory/repos/SmartPyme}"
export PYTHONPATH="$SMARTPYME_REPO${PYTHONPATH:+:$PYTHONPATH}"

SMARTPYME_BRIDGE="$SMARTPYME_REPO/mcp_smartpyme_bridge.py"
SMARTPYME_PYTHON="$SMARTPYME_REPO/.venv/bin/python"
HERMES_CONFIG="$HERMES_HOME/config.yaml"
OVERLAY_PATH="$SMARTPYME_REPO/infra/hermes-product/product-config-overlay.yaml"

mkdir -p "$HERMES_HOME"/logs "$HERMES_HOME"/sessions "$HERMES_HOME"/cron "$HERMES_HOME"/memories

if [[ ! -f "$SMARTPYME_BRIDGE" ]]; then
  echo "ERROR: SmartPyme MCP bridge not found: $SMARTPYME_BRIDGE" >&2
  exit 78
fi

if [[ ! -x "$SMARTPYME_PYTHON" ]]; then
  echo "ERROR: SmartPyme Python venv not executable: $SMARTPYME_PYTHON" >&2
  exit 78
fi

# Ensure MCP dependencies are installed in the bridge venv
echo "[smartpyme] Ensuring MCP dependencies in $SMARTPYME_PYTHON..."
"$SMARTPYME_PYTHON" -m pip install -q mcp fastmcp 2>/dev/null || {
  echo "WARNING: pip install failed, attempting ensurepip..."
  "$SMARTPYME_PYTHON" -m ensurepip --upgrade 2>/dev/null
  "$SMARTPYME_PYTHON" -m pip install -q mcp fastmcp
}

# Bootstrap product config from overlay
if [[ -f "$OVERLAY_PATH" ]]; then
  echo "[smartpyme] Bootstrapping product config..."
  SMARTPYME_REPO="$SMARTPYME_REPO" HERMES_PRODUCT_HOME="$HERMES_HOME" \
    "$SMARTPYME_PYTHON" "$SMARTPYME_REPO/infra/hermes-product/bootstrap-product-home.py"
fi

# Reconcile stale sandbox paths in generated config
if [[ -f "$HERMES_CONFIG" ]]; then
  sed -i "s#/workspace/mcp_smartpyme_bridge.py#$SMARTPYME_BRIDGE#g" "$HERMES_CONFIG"
  sed -i "s#\(^[[:space:]]*command:[[:space:]]*\)\"\?python3\"?#\1\"$SMARTPYME_PYTHON\"#g" "$HERMES_CONFIG"
fi

echo "[smartpyme] Starting Hermes Product Gateway..."
cd /opt/smartpyme-factory/repos/hermes-agent
exec /opt/smartpyme-factory/repos/hermes-agent/.venv/bin/hermes gateway run --replace
