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

`app/factory/**` es nombre incorrecto legacy. Debe migrar a `app/orchestrator/**`.

## Regla crítica

`app/**` no debe importar `factory/**`.

## Estado detectado

Hay contaminación arquitectónica detectada en:

- `app/factory/agent_loop/multiagent_task_loop.py`
- `app/adapters/factory_superowner_telegram_adapter.py`

Estado: `BOUNDARY_NOT_CLEAN`

## Decisión

No borrar `factory/**`.

No seguir agregando lógica bajo `app/factory/**`.

Preparar migración controlada:

`app/factory/** -> app/orchestrator/**`

## Comandos útiles

Ir al repo producto:

`cd /opt/smartpyme-factory/repos/SmartPyme`

Ir al repo Hermes:

`cd /opt/smartpyme-factory/repos/hermes-agent`

Ver estado:

`git status --short`

Buscar contaminación:

`grep -R --exclude-dir='__pycache__' "from factory\|import factory" app -n || true`
