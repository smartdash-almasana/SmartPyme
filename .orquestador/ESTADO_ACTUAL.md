# ESTADO ACTUAL — SMARTPYME FACTORY

## Fecha

2026-04-28

## Repo VM

`/home/neoalmasana/smartpyme-factory/repos/SmartPyme`

## GitHub

`smartdash-almasana/SmartPyme`

## Último commit limpio conocido en VM antes del bootstrap remoto

`b0da6cd9c3c34267306227c89a00540cd1932176`

## Situación actual registrada

- La VM tenía cambios locales antes de los commits remotos nuevos.
- `main` remoto fue modificado con archivos de bootstrap v2.1.
- No se activó systemd.
- No se migraron TaskSpecs con `--execute`.
- No se tocó core Python.
- No se tocó `mcp_smartpyme_bridge.py`.
- Fase 0A fue ejecutada localmente y produjo `fase0a_report.md`.
- El migrador TaskSpec validó `21 valid, 0 errors` en dry-run local.

## Archivos locales sensibles detectados

No borrar ni pisar:

- `factory/config/telegram.local.env`
- `factory/install_hermes_telegram_control.py`

## Commits remotos agregados por bootstrap v2.1

- `a43e852` — `factory: add bootstrap requirements`
- `f33faad` — `factory: add canonical verdict enum`
- `75c3a3d` — `factory: add v2.1 schemas and telegram escape`
- `57e0d77` — `orquestador: add operational cage`

## Estado de seguridad

No se debe activar ningún servicio hasta validar:

- repo local alineado;
- config real de Hermes;
- token Telegram fuera del repo;
- allowlist real;
- `/estado` funcionando;
- `dry_run` completo.

## Próxima decisión operativa

La acción siguiente debe ser una sola de estas:

A. Conservar `main` remoto y alinear la VM con cuidado.
B. Revertir los commits de bootstrap remoto y rehacer por branch/PR.

## Regla inmediata

No avanzar a activación ni migración real hasta que el estado local de la VM esté reconciliado.
