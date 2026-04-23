# Continuous Factory Supervisor

## Qué hace
- Ejecuta un loop local por una ventana temporal (`--minutes`).
- Rota por canteras y módulos definidos en `factory/canteras_manifest.json`.
- Llama `run_factory` en `execute_ready`.
- Llama `run_codex_worker` para drenar `in_progress`.
- Emite heartbeat visible por ciclo (con `elapsed` y `remaining` en `HH:MM:SS`).
- Emite resumen parcial cada 15 minutos.
- Escribe log y estado en disco.
- Tolera fallos por cantera/unidad y continúa el ciclo.
- Cierra limpio al terminar el presupuesto temporal con resumen final en consola y log.

## Radio Inicial Reducido (calidad > volumen)
- Canteras iniciales:
  - `E:\BuenosPasos\smartcounter`
  - `E:\BuenosPasos\smartexcel\poc-agente-pyme`
  - `E:\BuenosPasos\smartseller-v2`
- Módulos iniciales:
  - `clarification`
  - `reconciliation`
- Estrategia: reducir amplitud de exploración para subir precisión de hallazgos ejecutables y bajar el porcentaje de `blocked` por rutas inválidas o alcance difuso.

## Qué no hace
- No usa threads.
- No usa servicios de background.
- No usa watchers.
- No invoca Codex externo ni LLMs desde este script.
- No ejecuta shell arbitrario.

## CLI recomendado (paquete)
```powershell
$env:PYTHONPATH="."
python -m factory.continuous_factory `
  --minutes 180 `
  --cycle-seconds 60 `
  --manifest factory\canteras_manifest.json `
  --repo-destino E:\BuenosPasos\smartbridge\SmartPyme `
  --model gemini-2.5-pro `
  --auditor-timeout-seconds 120 `
  --max-hallazgos-per-cycle 10 `
  --max-executions-per-cycle 10
```

Parámetros:
- `--minutes`: ventana total de ejecución.
- `--cycle-seconds`: pausa entre ciclos.
- `--manifest`: manifiesto de canteras y módulos.
- `--repo-destino`: repo SmartPyme destino.
- `--model` (opcional): se pasa a `run_factory`.
- `--auditor-timeout-seconds` (opcional): timeout fail-closed propagado al auditor en `run_factory`.
- `--max-hallazgos-per-cycle` (opcional): límite de unidades auditadas por ciclo.
- `--max-executions-per-cycle` (opcional): límite de drenado de worker por ciclo.

## Archivos runtime
- `factory/logs/continuous_factory_<timestamp>.log`
- `factory/state/continuous_factory_state_<timestamp>.json`

## Tests
```powershell
python -m unittest -v tests.factory.test_continuous_factory
```

## Piloto 10 minutos
```powershell
$env:PYTHONPATH="."
$env:GEMINI_MODEL="gemini-2.5-pro"
python -m factory.continuous_factory --minutes 10 --cycle-seconds 60 --manifest factory\canteras_manifest.json --repo-destino E:\BuenosPasos\smartbridge\SmartPyme --model gemini-2.5-pro --auditor-timeout-seconds 120 --max-hallazgos-per-cycle 6 --max-executions-per-cycle 6
```

## Corrida 180 minutos
```powershell
$env:PYTHONPATH="."
$env:GEMINI_MODEL="gemini-2.5-pro"
python -m factory.continuous_factory --minutes 180 --cycle-seconds 60 --manifest factory\canteras_manifest.json --repo-destino E:\BuenosPasos\smartbridge\SmartPyme --model gemini-2.5-pro --auditor-timeout-seconds 180 --max-hallazgos-per-cycle 10 --max-executions-per-cycle 10
```
