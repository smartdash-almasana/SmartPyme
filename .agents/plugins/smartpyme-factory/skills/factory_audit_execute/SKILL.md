# Factory Audit Execute

## Propósito
Ejecutar el flujo operativo de SmartPyme Factory sobre hallazgos: auditoría, validación de preparación y entrega a ejecución local posterior.

## Cuándo usarlo
- Cuando existe un hallazgo `.md` en `factory/hallazgos/pending`.
- Cuando se necesita correr el flujo `audit_only` o `execute_ready` con `factory/run_factory.py`.
- Cuando se debe respetar el hallazgo como contrato de trabajo.

## Cuándo no usarlo
- Cuando no hay hallazgo pendiente.
- Cuando el objetivo exige cambios fuera de SmartPyme.
- Cuando hay dudas abiertas del owner sin resolver.

## Input esperado
- Modo de ejecución: `audit_only` o `execute_ready`.
- Módulo objetivo.
- Una o más rutas fuente (`--rutas-fuente`).
- Ruta del repo destino: `E:\BuenosPasos\smartbridge\SmartPyme`.
- Opcional: `--model` para auditor Gemini.

## Output esperado
- Estado explícito del hallazgo: `pending`, `in_progress`, `blocked` o `done`.
- Ruta final del archivo de hallazgo movido.
- Motivo explícito de bloqueo si aplica.

## Reglas obligatorias
- Respetar fail-closed.
- No ejecutar cambios fuera de SmartPyme.
- Usar el hallazgo como contrato de alcance.
- No continuar si hay pregunta abierta en `PREGUNTA_AL_OWNER`.
- No permitir rutas `src\...` o rutas fuera del repo.

## Criterio de bloqueo
- Faltan secciones obligatorias del hallazgo.
- Hay pregunta abierta o más de una interpretación razonable.
- Las rutas de portado están fuera de SmartPyme o contienen `src`.
- No hay hallazgo nuevo generado por auditor.

## Ejemplo mínimo
```powershell
python factory\run_factory.py --modo execute_ready --modulo clarification --rutas-fuente "E:\BuenosPasos\smartbridge\app\services\clarification_service.py" "E:\BuenosPasos\smartbridge\app\services\inbox_service.py" --repo-destino "E:\BuenosPasos\smartbridge\SmartPyme" --model "gemini-2.5-pro"
```
