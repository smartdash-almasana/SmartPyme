# core-reconciliacion-v1

Objetivo: implementar primer motor deterministico de reconciliacion entre dos fuentes CSV.

PLAN:
- Objetivo: leer dos CSV, comparar por entidad y emitir diferencias estructuradas como `Hallazgo`.
- Archivos permitidos: `app/core/reconciliation/service.py`, `app/core/reconciliation/__init__.py`, `tests/core/test_reconciliation_csv.py`, `factory/evidence/core-reconciliacion-v1/*`.
- Archivos prohibidos/no tocados por esta unidad: integraciones externas, reporting, systemd y refactors globales.
- Criterio de cierre: diferencia numerica detectada por entidad, salida tipo hallazgo, test focal validado.
- Tests esperados: `python3 -m pytest tests/core/test_reconciliation_csv.py -q` y `python3 -m ruff check ...`.

WRITE:
- Se agrego entrada publica `reconcile_csv_sources`.
- Se agregaron helpers deterministas para lectura CSV y normalizacion numerica.
- Se agrego test focal para una diferencia numerica por entidad.

VERIFY/RUN:
- La existencia fisica fue verificada en `verification.txt`.
- `compileall` paso.
- `pytest` y `ruff` no estan disponibles en el entorno.
- El import del core falla por dependencia existente faltante: `pydantic`.

DECISION:
- `BLOCKED` por contrato/entorno de dependencias faltante.
