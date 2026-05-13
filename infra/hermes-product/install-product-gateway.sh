#!/usr/bin/env bash
set -euo pipefail

SMARTPYME_REPO="${SMARTPYME_REPO:-/opt/smartpyme-factory/repos/SmartPyme}"
PRODUCT_HOME="${HERMES_PRODUCT_HOME:-/home/neoalmasana/.hermes-smartpyme-product}"
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"
UNIT_NAME="hermes-smartpyme-product.service"

mkdir -p "$PRODUCT_HOME"/logs "$PRODUCT_HOME"/sessions "$PRODUCT_HOME"/cron "$PRODUCT_HOME"/memories
mkdir -p "$USER_SYSTEMD_DIR"

chmod +x "$SMARTPYME_REPO/infra/hermes-product/run-hermes-product-gateway.sh"
cp "$SMARTPYME_REPO/infra/hermes-product/$UNIT_NAME" "$USER_SYSTEMD_DIR/$UNIT_NAME"

systemctl --user daemon-reload
systemctl --user enable "$UNIT_NAME"

echo "Installed $UNIT_NAME"
echo "Product Hermes home: $PRODUCT_HOME"
echo "Start with: systemctl --user start $UNIT_NAME"
