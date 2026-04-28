# core-reconciliacion-v1 - Codex Builder validation

## PLAN
- objetivo: validar primer motor deterministico de reconciliacion CSV contra CSV.
- archivos permitidos: `app/core/reconciliation/models.py`, `app/core/reconciliation/service.py`, `tests/core/test_reconciliation_csv.py`, evidencia bajo `factory/evidence/core-reconciliacion-v1/`.
- archivos prohibidos: integraciones externas, Telegram, reporting, systemd, refactor global.
- criterio de cierre: detectar diferencia numerica por entidad y devolver hallazgo estructurado con test focalizado.
- tests esperados: pytest focalizado de reconciliacion y Ruff si esta disponible en el entorno.

## WRITE
- No se modifico codigo en esta intervencion.
- Se registro esta evidencia fisica nueva.

## VERIFY
Comandos ejecutados:

```bash
pwd
git status --short
test -f app/core/reconciliation/service.py; ls -la app/core/reconciliation/service.py
test -f app/core/reconciliation/models.py; ls -la app/core/reconciliation/models.py
test -f tests/core/test_reconciliation_csv.py; ls -la tests/core/test_reconciliation_csv.py
grep -R "def reconcile_csv_sources\|class SimpleReconciliationFinding\|test_reconcile_csv_sources_returns_hallazgo" -n app/core/reconciliation tests/core/test_reconciliation_csv.py
```

Salida relevante:

```text
/opt/smartpyme-factory/repos/SmartPyme
-rw-r--r-- 1 neoalmasana neoalmasana 60132 Apr 27 19:47 app/core/reconciliation/service.py
-rw-r--r-- 1 neoalmasana neoalmasana 8478 Apr 27 19:56 app/core/reconciliation/models.py
-rw-r--r-- 1 neoalmasana neoalmasana 1150 Apr 27 19:21 tests/core/test_reconciliation_csv.py
app/core/reconciliation/models.py:285:class SimpleReconciliationFinding:
app/core/reconciliation/service.py:524:def reconcile_csv_sources(
tests/core/test_reconciliation_csv.py:9:def test_reconcile_csv_sources_returns_hallazgo_for_numeric_difference(tmp_path):
```

## INSPECT
Contenido relevante inspeccionado:
- `app/core/reconciliation/service.py`: `reconcile_csv_sources` lee 2 CSV, normaliza campos numericos deterministas, llama `reconcile_records` y transforma a `Hallazgo`.
- `tests/core/test_reconciliation_csv.py`: crea 2 CSV temporales y valida un hallazgo para `o-1` con `diferencia_cuantificada == 25.5`.

## RUN
Comandos ejecutados:

```bash
python3 -m pytest tests/core/test_reconciliation_csv.py tests/core/test_reconciliation.py tests/core/test_reconciliation_service.py -q
ruff check app/core/reconciliation/models.py app/core/reconciliation/service.py tests/core/test_reconciliation_csv.py tests/core/test_reconciliation.py tests/core/test_reconciliation_service.py
./.venv/bin/pytest tests/core/test_reconciliation_csv.py tests/core/test_reconciliation.py tests/core/test_reconciliation_service.py -q
./.venv/bin/python -m compileall app/core/reconciliation tests/core/test_reconciliation_csv.py
```

Salida relevante:

```text
/usr/bin/python3: No module named pytest
/bin/bash: line 1: ruff: command not found
........................................................................ [ 90%]
........                                                                 [100%]
Listing 'app/core/reconciliation'...
```

## DECISION
BLOCKED

Motivo: los tests focalizados pasan en `.venv`, pero Ruff no esta disponible en el entorno global ni en `.venv/bin`, por lo que no se puede declarar cierre `CORRECTO` bajo AGENTS/CODEX.
