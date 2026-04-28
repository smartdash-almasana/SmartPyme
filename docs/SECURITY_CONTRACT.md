# Security Contract — SmartPyme Factory

## Principios

- Secretos fuera del repo.
- Autorización por identidad del usuario Telegram.
- Fail-closed ante incertidumbre.
- Ningún agente ejecuta acciones destructivas sin gate humano.

## Archivos sensibles

No versionar ni sobrescribir:

- `factory/config/telegram.local.env`
- `.env`
- `/home/neoalmasana/.hermes/.env`

## Roles

- `owner`: todos los comandos.
- `moderator`: `/estado`, `/actualizar`.
- `auditor`: solo lectura.

## Auditoría

Registrar actor, comando, fecha, resultado y evidencia cuando exista.

## Rotación

Tokens externos deben rotarse fuera del repo. El repo solo contiene `.example`.
