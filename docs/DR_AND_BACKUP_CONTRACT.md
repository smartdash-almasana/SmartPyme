# DR and Backup Contract — SmartPyme Factory

## Alcance

SQLite y evidencia local.

## Política mínima

- Backup SQLite con `.backup` antes de operaciones destructivas.
- Retención inicial: 30 días.
- Restore manual verificado antes de producción.

## Bases conocidas

- `data/jobs.db`
- `data/clarifications.db`
- `data/processed_updates.db`
- `/home/neoalmasana/.hermes/memory_short.db`
- `/home/neoalmasana/.hermes/memory_long.db`

## Regla

No activar systemd productivo sin política de backup operativa.
