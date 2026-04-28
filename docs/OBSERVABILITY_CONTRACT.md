# Observability Contract — SmartPyme Factory

## Log schema mínimo

```json
{
  "timestamp": "ISO-8601",
  "event_id": "string",
  "trace_id": "string",
  "cliente_id": "string",
  "severity": "INFO|WARN|ERROR",
  "event": "string",
  "message": "string",
  "metadata": {}
}
```

## Reglas

- No loggear tokens.
- No loggear secretos.
- No ocultar errores de herramientas.
- Evidencia de ciclo en `factory/ai_governance/evidence/`.

## Destino inicial

stdout JSON o archivos de evidencia; journald solo cuando se active servicio real.
