#!/usr/bin/env bash
set -euo pipefail

export HERMES_HOME="${HERMES_PRODUCT_HOME:-/home/neoalmasana/.hermes-smartpyme-product}"
export SMARTPYME_REPO="${SMARTPYME_REPO:-/opt/smartpyme-factory/repos/SmartPyme}"

mkdir -p "$HERMES_HOME"/logs "$HERMES_HOME"/sessions "$HERMES_HOME"/cron "$HERMES_HOME"/memories

cd /opt/smartpyme-factory/repos/hermes-agent
exec /opt/smartpyme-factory/repos/hermes-agent/.venv/bin/hermes gateway run --replace
