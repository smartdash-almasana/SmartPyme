# MCP Tools Contract — SmartPyme Bridge

## Transporte canónico

SmartPyme Bridge opera por `stdio`.

Hermes Gateway lanza el bridge como subproceso local:

```yaml
mcp:
  servers:
    smartpyme:
      transport: "stdio"
      command: "/home/neoalmasana/smartpyme-factory/repos/SmartPyme/.venv/bin/python"
      args:
        - "/home/neoalmasana/smartpyme-factory/repos/SmartPyme/mcp_smartpyme_bridge.py"
```

No existe endpoint HTTP `localhost:8080/mcp` para el bridge vigente.

## Reglas

- Hermes invoca tools MCP; no importa core Python directamente.
- El bridge no decide flujo de factoría.
- El bridge no saltea validaciones humanas.
- Toda respuesta debe indicar si viene de backend real o de fallback explícito.

## Tools esperadas

- `create_job`
- `get_job_status`
- `list_pending_validations`
- `resolve_clarification`
- `save_clarification`
- `get_evidence`
- `ingest_document`

## Validación

```bash
grep -n "mcp.run" mcp_smartpyme_bridge.py
```
