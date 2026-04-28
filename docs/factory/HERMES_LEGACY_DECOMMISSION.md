# Hermes Legacy Decommission — SmartPyme

## Objetivo

Eliminar la dependencia operativa de scripts legacy y dejar Hermes Gateway como único canal conversacional.

## Legacy explícitamente prohibido

```text
scripts/telegram_factory_control.py
scripts/hermes_factory_runner.py
```

Estos archivos no deben existir ni ejecutarse en la operación profesional.

## Verificación local

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
find . -path "*/telegram_factory_control.py" -o -path "*/hermes_factory_runner.py"
```

El resultado aceptado es vacío.

## Verificación de procesos

```bash
ps -ef | grep -E "telegram_factory_control|hermes_factory_runner" | grep -v grep || true
```

El resultado aceptado es vacío.

## Remoción local si aparecen

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
git rm -f scripts/telegram_factory_control.py scripts/hermes_factory_runner.py 2>/dev/null || true
rm -f scripts/telegram_factory_control.py scripts/hermes_factory_runner.py
```

## Backup fantasma

Si existe:

```text
/opt/smartpyme-factory/repos/SmartPyme_dirty_backup_20260427_012904
```

no es repo operativo. Debe archivarse fuera del runtime o eliminarse luego de confirmar que `origin/main` contiene el estado válido.

## Criterio de cierre

- No hay procesos legacy.
- No hay archivos legacy en repo operativo.
- No hay polling Telegram fuera de Hermes Gateway.
- Todo control pasa por Hermes Gateway.
