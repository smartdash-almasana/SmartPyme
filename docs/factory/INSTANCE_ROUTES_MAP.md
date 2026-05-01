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
`app/factory/**` es nombre incorrecto legacy. Debe migrar a `app/orchestrator/**` (o `app/agents/` según corresponda).

## Reglas críticas

1. `app/**` no debe importar `factory/**` (top-level).
2. Ningún código nuevo debe escribirse bajo `app/factory/**`.
3. `factory/**` queda reservado exclusivamente a Hermes/dev system.

## Inventario app/factory/

Subcarpetas detectadas y clasificación:

- `app/factory/orchestrator/` -> **ORCHESTRATOR_RUNTIME**
- `app/factory/router/` -> **ORCHESTRATOR_RUNTIME**
- `app/factory/chain/` -> **ORCHESTRATOR_RUNTIME**
- `app/factory/skills/` -> **ORCHESTRATOR_RUNTIME**
- `app/factory/multiagent/` -> **ORCHESTRATOR_RUNTIME**
- `app/factory/agents/` -> **PRODUCT_RUNTIME** (Destino futuro: `app/agents/`)
- `app/factory/agent_loop/` -> **CONTAMINATED_BOUNDARY** (Requiere aislamiento)

## Estado de contaminación

Estado: `BOUNDARY_NOT_CLEAN`

Contaminación arquitectónica detectada (imports runtime desde `app/` a `factory/` top-level):
- `app/factory/agent_loop/multiagent_task_loop.py`
- `app/adapters/factory_superowner_telegram_adapter.py`

## Plan de migración controlada

Se ejecutará en batches seguros:

- **Batch 1:** `app/factory/orchestrator/` -> `app/orchestrator/`
- **Batch 2:** `app/factory/router/`, `chain/`, `skills/`, `multiagent/` -> `app/orchestrator/`
- **Batch 3:** `app/factory/agents/` -> `app/agents/`
- **Batch 4:** `app/factory/agent_loop/` (Aislar imports a `factory/` y migrar a `app/orchestrator/boundary/` o equivalente).

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

Buscar contaminación:
`grep -R --exclude-dir='__pycache__' "from factory\|import factory" app -n || true`

Diagnóstico provider Hermes:
`python3 scripts/hermes_provider_doctor.py`
