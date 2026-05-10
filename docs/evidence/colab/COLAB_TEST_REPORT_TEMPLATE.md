# Colab Test Report — YYYY-MM-DD

## Metadata

- fecha: YYYY-MM-DD HH:MM UTC
- commit: `<hash corto>`
- rama: `product/laboratorio-mvp-vendible`
- python: `3.x.x`
- entorno: Google Colab (efímero)
- clasificacion: **PASS | PARTIAL | FAIL | BLOCKED**

---

## Bloque A — Clone y checkout

Estado: OK | BLOCKED

```
git clone https://github.com/smartdash-almasana/SmartPyme.git
git checkout product/laboratorio-mvp-vendible
```

Resultado:
<!-- pegar salida o "OK sin errores" -->

---

## Bloque B — Instalación

```
pip install -r requirements-bootstrap.txt -q
pip install -r requirements-dev.txt -q
python --version
```

Resultado:
<!-- pegar salida relevante o errores -->

---

## Bloque C — Colección de tests

```
pytest --collect-only -q
```

Estado: OK | PARTIAL | BLOCKED

```
<!-- pegar salida de collect-only -->
```

Errores de colección detectados:
<!-- listar archivos con error de import o mismatch -->

---

## Bloque D — Tests focales

Estado global: PASS | PARTIAL | FAIL

### `tests/contracts/test_operational_case_contract.py`

Estado: PASS | FAIL | SKIP
```
<!-- pegar salida -q --tb=short -->
```

### `tests/repositories/test_operational_case_repository.py`

Estado: PASS | FAIL | SKIP
```
<!-- pegar salida -->
```

### `tests/test_mcp_operational_case_bridge.py`

Estado: PASS | FAIL | SKIP
```
<!-- pegar salida -->
```

### `tests/contracts/test_operational_claims.py`

Estado: PASS | FAIL | SKIP
```
<!-- pegar salida -->
```

### `tests/services/test_operational_interview_engine.py`

Estado: PASS | FAIL | SKIP
```
<!-- pegar salida -->
```

---

## Bloque E — pytest global

```
pytest tests -q --tb=no --ignore=tests/tmp
```

Estado: PASS | PARTIAL | FAIL

```
<!-- pegar resumen final: X passed, Y failed, Z errors -->
```

Fallos detectados:
<!-- listar brevemente los tests que fallaron -->

Clasificación de fallos:
- Regresión nueva (atribuible al cambio actual): <!-- sí/no, cuáles -->
- Deuda preexistente (legacy/factory/tmp): <!-- sí/no, cuáles -->

---

## Clasificación final

**PASS | PARTIAL | FAIL | BLOCKED**

Criterio aplicado:
<!-- explicar brevemente por qué se eligió esta clasificación -->

---

## Métricas

```yaml
commit_hash:
branch:
python_version:
tests_run:
passed:
failed:
collection_errors:
duration_seconds:
classification:
notes:
```

---

## Próximo microciclo recomendado

<!-- completar después de revisar los fallos -->
<!-- un solo microciclo, concreto y accionable -->

---

## Notas adicionales

<!-- observaciones sobre el entorno, dependencias faltantes, paths rotos, etc. -->
