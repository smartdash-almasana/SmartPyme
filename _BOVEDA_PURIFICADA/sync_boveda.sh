#!/bin/bash
set -e

# Script de sincronización controlada de _BOVEDA_PURIFICADA hacia repo SME OS
# Uso: ejecutar desde la raíz del repo destino

SRC="_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL"
DEST="."

# Sincroniza SOLO contratos e infraestructura, sin tocar código de producto
rsync -av --progress \
  --exclude "PRODUCTO_SMARTPYME/schema_maestro.py" \
  --exclude "*.log" \
  --exclude "*.tmp" \
  --exclude "__pycache__/" \
  --ignore-existing \
  "$SRC/" "$DEST/"

# Mensaje final
echo "Sincronización completada (modo seguro)."
echo "Revisar manualmente antes de mergear en main."
