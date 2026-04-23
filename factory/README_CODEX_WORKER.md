# Codex Worker (Local)

## Qué hace
- Toma un único hallazgo por corrida desde `factory/hallazgos/in_progress`.
- Selecciona el más antiguo sin lock.
- Crea lock local (`.md.lock`) antes de procesar.
- Revalida el hallazgo (fail-closed).
- Ejecuta implementación real con `codex exec` usando el contrato del hallazgo.
- Corre tests mínimos del módulo (`pytest`) antes de cerrar estado.
- Cierra estado:
  - éxito + tests_passed -> `done`
  - cualquier falla -> `blocked`
- Libera lock siempre, incluso con excepción.

## Qué no hace
- No simula cierre exitoso.
- No corre shell arbitrario.
- No procesa más de un hallazgo por corrida.

## Contrato del executor
El worker recibe una función:
- `executor(hallazgo_path: Path) -> ExecutionResult`

`ExecutionResult`:
- `success: bool`
- `message: str`
- `tests_passed: bool`

Si no se inyecta `executor`, usa el ejecutor real por defecto:
1. parsea `modulo_objetivo`, `objetivo` y rutas destino del hallazgo
2. ejecuta `codex exec` con alcance fail-closed
3. corre `pytest` mínimo del módulo
4. solo cierra en `done` si ambos pasos salen bien

## Cómo correr tests
```powershell
python -m unittest -v tests.factory.test_run_codex_worker
```

## Cómo ejecutar una corrida local
```powershell
python factory\run_codex_worker.py
```
