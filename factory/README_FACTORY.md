# Factory Runner SmartPyme

Runner local para orquestar el flujo: auditoria Gemini -> validacion local -> movimiento de estado del hallazgo.

## Alcance
- No invoca Codex desde el script.
- Opera solo sobre `factory/hallazgos/`.
- Fail-closed: ante error o inconsistencia, bloquea.

## Modos
- `audit_only`: ejecuta auditor y deja el hallazgo en `pending`.
- `execute_ready`: ejecuta auditor, valida hallazgo y mueve:
  - `pending -> in_progress` si valida.
  - `pending -> blocked` si falla validacion.
  - `pending -> done` si en META viene `estado: done`.
- `process_pending`: procesa en lote los hallazgos ya existentes en `pending`:
  - `pending -> in_progress` si valida.
  - `pending -> blocked` si falla validacion.
  - `pending -> done` si en META viene `estado: done`.

## Validaciones fail-closed
- Requiere secciones: `# HALLAZGO`, `## META`, `## OBJETIVO`, `## PROPUESTA_DE_PORTADO`, `## REGLAS_DE_EJECUCION`, `## CRITERIO_DE_CIERRE`.
- Bloquea si hay pregunta abierta en `## PREGUNTA_AL_OWNER`.
- Bloquea rutas destino con `src\` o `src/`.
- Bloquea rutas fuera del repo SmartPyme.
- Solo permite rutas bajo `app/`, `tests/` o `factory/`.

## Uso real
```powershell
python factory\run_factory.py --modo audit_only --modulo clarification --rutas-fuente "E:\BuenosPasos\smartbridge\app\services\clarification_service.py" "E:\BuenosPasos\smartcounter\app\services\entity_resolution_service.py" --repo-destino "E:\BuenosPasos\smartbridge\SmartPyme"
```

```powershell
python factory\run_factory.py --modo execute_ready --modulo reconciliation --rutas-fuente "E:\BuenosPasos\smartbridge\app\services\reconciliation\matcher.py" "E:\BuenosPasos\smartbridge\app\services\reconciliation\diff.py" --repo-destino "E:\BuenosPasos\smartbridge\SmartPyme" --model "gemini-2.5-pro"
```

```powershell
python factory\run_factory.py --modo process_pending --repo-destino "E:\BuenosPasos\smartbridge\SmartPyme"
```
