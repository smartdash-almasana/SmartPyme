#!/usr/bin/env bash
set -euo pipefail

REPO="/home/neoalmasana/smartpyme-factory/repos/SmartPyme"
HERMES_HOME="/home/neoalmasana/.hermes"
HERMES_VENV="$HERMES_HOME/venv"

cd "$REPO"

python3 -m pip install --user -r requirements-bootstrap.txt

mkdir -p factory/ai_governance/{contracts,schemas,evidence,tasks,skills}
mkdir -p factory/control data docs/factory hermes infra/systemd

if [[ ! -f "$HERMES_HOME/.env" ]]; then
  echo "ERROR: falta $HERMES_HOME/.env"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$HERMES_HOME/.env"
set +a

: "${SMARTPYME_ENV:=dry_run}"
: "${TELEGRAM_BOT_TOKEN:?falta TELEGRAM_BOT_TOKEN en $HERMES_HOME/.env}"
: "${TELEGRAM_OWNER_CHAT_ID:?falta TELEGRAM_OWNER_CHAT_ID en $HERMES_HOME/.env}"

if [[ ! -f factory/ai_governance/telegram_allowlist.yaml ]]; then
  echo "ERROR: falta factory/ai_governance/telegram_allowlist.yaml"
  echo "Crear desde factory/ai_governance/telegram_allowlist.yaml.example con user_id real."
  exit 1
fi

if ! command -v envsubst >/dev/null 2>&1; then
  echo "ERROR: falta envsubst"
  exit 1
fi

envsubst < hermes/config.template.yaml.example > "$HERMES_HOME/config.yaml"

if [[ -x "$HERMES_VENV/bin/pip" ]]; then
  "$HERMES_VENV/bin/pip" install -e "$REPO"
else
  echo "WARNING: no existe $HERMES_VENV/bin/pip; no se instala editable en Hermes venv"
fi

python3 scripts/migrate_taskspecs_v1_to_v2.py --dry-run
python3 -m pytest tests/factory/test_telegram_escape.py tests/e2e/test_factory_dry_run.py -q

echo "Bootstrap dry-run completado. No se inició systemd."
