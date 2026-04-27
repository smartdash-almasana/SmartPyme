#!/usr/bin/env bash
set -euo pipefail

REPO="/opt/smartpyme-factory/repos/SmartPyme"
SERVICE="smartpyme-telegram-control.service"
UNIT_PATH="/etc/systemd/system/${SERVICE}"

if [ ! -d "$REPO" ]; then
  echo "Repo no encontrado en $REPO" >&2
  exit 1
fi

sudo bash -lc "cat > ${UNIT_PATH} <<'EOF'
[Unit]
Description=SmartPyme Telegram Control (polling)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=neoalmasana
WorkingDirectory=${REPO}
EnvironmentFile=/opt/smartpyme-factory/.env.telegram
ExecStart=/usr/bin/python3 ${REPO}/scripts/telegram_factory_control.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE}
sudo systemctl restart ${SERVICE}
sudo systemctl status ${SERVICE} --no-pager

echo "Servicio ${SERVICE} instalado y corriendo."
