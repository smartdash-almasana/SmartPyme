PLAN
objetivo: implementar/verificar motor minimo de reconciliacion entre dos CSV con salida de hallazgos por entidad.
archivos_permitidos: app/core/reconciliation/models.py app/core/reconciliation/service.py tests/core/test_reconciliation_csv.py factory/evidence/core-reconciliacion-v1/*
archivos_prohibidos: resto del repo; sin refactor global; sin cambios de control factory en esta unidad.
criterio_cierre: detectar diferencia numerica entre fuentes CSV y emitir Hallazgo estructurado con entidad, delta y evidencia comparativa.
tests_esperados: pytest focal, pytest relacionado de reconciliacion/hallazgos, py_compile/compileall y Ruff si esta disponible.

WRITE
app/core/reconciliation/service.py expone reconcile_csv_sources con lectura deterministica de dos CSV, normalizacion numerica y transformacion a Hallazgo.
tests/core/test_reconciliation_csv.py valida diferencia numerica por entidad y evidencia estructurada.
app/core/reconciliation/models.py mantiene ReconciliationRow sin dependencia runtime externa no declarada.
No se usa polars porque no esta instalado ni declarado en pyproject.toml.

VERIFY
ver pwd.txt, git_status.txt, ls_files.txt e inspect_*.txt.

RUN
.venv/bin/python -m pytest tests/core/test_reconciliation_csv.py -q
.venv/bin/python -m pytest tests/core/test_reconciliation.py tests/core/test_reconciliation_csv.py tests/core/test_hallazgos_service.py -q
.venv/bin/python -m py_compile app/core/reconciliation/models.py app/core/reconciliation/service.py tests/core/test_reconciliation_csv.py
python3 -m compileall app/core/reconciliation app/core/hallazgos tests/core/test_reconciliation_csv.py -q
.venv/bin/python manual reconcile_csv_sources smoke
.venv/bin/python -m ruff check app/core/reconciliation/models.py app/core/reconciliation/service.py tests/core/test_reconciliation_csv.py

DECISION
BLOCKED: pytest focal y tests relacionados pasan en .venv, py_compile/compileall pasan y el smoke deterministico emite un Hallazgo correcto. Ruff no esta instalado en python3 ni en .venv, por lo que no se declara CORRECTO segun AGENTS.md.
