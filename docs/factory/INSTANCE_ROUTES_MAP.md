# INSTANCE_ROUTES_MAP — SmartPyme / Hermes

## Rutas canónicas

SmartPyme producto:
`/opt/smartpyme-factory/repos/SmartPyme`

Hermes externo:
`/opt/smartpyme-factory/repos/hermes-agent`

Runtime local Hermes:
`/home/neoalmasana/.hermes`

Docker workspace:
`/workspace`

## Separación obligatoria

`factory/**` es la factoría externa / Hermes dev system.

`app/**` es el runtime producto SmartPyme.

`app/factory/**` fue eliminado. No debe volver a crearse.

## Reglas críticas

1. `app/**` no debe importar `factory/**` como lógica de producto.
2. Ningún código nuevo debe escribirse bajo `app/factory/**`.
3. `factory/**` queda reservado exclusivamente a Hermes/dev system.
4. Única excepción permitida: `app/mcp/tools/factory_control_tool.py` puede importar `factory.adapters.app_bridge/**` como puente explícito de control MCP hacia la factoría externa.

## Estado final de migración runtime

Estado: `BOUNDARY_CLEAN_WITH_EXPLICIT_MCP_BRIDGE`

Resultado confirmado:

- `app/factory/` eliminado.
- `app/orchestrator/` soberano.
- `app/agents/` soberano.
- `factory/adapters/app_bridge/` centraliza el puente explícito hacia la factoría externa.
- `app/mcp/tools/factory_control_tool.py` es el único punto de contacto permitido desde `app/**` hacia `factory/**`.

## Migración ejecutada

Batches completados:

- **Batch 1:** `app/factory/orchestrator/` -> `app/orchestrator/`
- **Batch 2:** `app/factory/router/`, `chain/`, `skills/`, `multiagent/` -> `app/orchestrator/`
- **Batch 3:** `app/factory/agents/` -> `app/agents/`
- **Batch 4:** `app/factory/agent_loop/` aislado en `factory/adapters/app_bridge/agent_loop/` y eliminado de `app/factory/`.
- **Batch 5:** motor soberano `agent_loop/models.py` y `agent_loop/service.py` movido a `app/orchestrator/agent_loop/`.

## Estructura vigente

Producto SmartPyme:

```text
app/api/**
app/core/**
app/services/**
app/repositories/**
app/adapters/**
app/mcp/**
app/orchestrator/**
app/agents/**
```

Factoría externa / Hermes dev system:

```text
factory/**
```

Puente permitido:

```text
factory/adapters/app_bridge/**
```

Uso permitido desde `app/**`:

```text
app/mcp/tools/factory_control_tool.py -> factory.adapters.app_bridge/**
```

Todo otro import desde `app/**` hacia `factory/**` debe considerarse contaminación arquitectónica.

## Validación final registrada

Última validación reportada:

```text
app/factory: eliminado
app/orchestrator: sin dependencia de factory/**
app/agents: sin dependencia de factory/**
pytest tests/factory/test_agent_loop.py \
  tests/factory/test_multiagent_min.py \
  tests/factory/test_skill_router.py \
  tests/factory/test_skill_registry.py \
  tests/factory/test_skill_chain.py \
  tests/factory/test_orchestrator.py -q
36 passed
```

Import `factory/**` restante en `app/**`:

```text
app/mcp/tools/factory_control_tool.py
```

Estado: excepción aceptada como puente explícito de control.

## Estado provider Hermes

Estado operativo validado desde la VM:

- Codex: archivos de auth presentes, pero no usar como provider principal ahora.
- Gemini OAuth CLI / Code Assist: NO usar con Hermes por warning de política de Google para software de terceros.
- Gemini API key: operativo. Test liviano respondió `OK`.
- Gemini/Vertex: configuración local detectable por `GOOGLE_CLOUD_PROJECT` y ADC; queda como alternativa con créditos GCP.
- DeepSeek/OpenRouter: pendiente configurar API key.

Provider recomendado actual:
`gemini` vía Google AI Studio API key.

Regla operativa:
Antes de loops largos, probar siempre:
`hermes "Responde solo con OK si estás disponible."`
Evitar loops agresivos sin rate control.

## Comandos útiles

Ir al repo producto:
`cd /opt/smartpyme-factory/repos/SmartPyme`

Ir al repo Hermes:
`cd /opt/smartpyme-factory/repos/hermes-agent`

Ver estado:
`git status --short`

Buscar imports legacy eliminados:
`grep -R --exclude-dir='__pycache__' "app.factory" app tests scripts -n || true`

Buscar imports `factory/**` en runtime:
`grep -R --exclude-dir='__pycache__' "from factory\|import factory" app -n || true`

Diagnóstico provider Hermes:
`python3 scripts/hermes_provider_doctor.py`
