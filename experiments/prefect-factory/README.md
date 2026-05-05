# SmartPyme Prefect Factory

Scaffold experimental de factoría deterministic-first.

## Jerarquía

```text
Prefect = runtime durable del workflow
Pydantic = contratos estrictos
Pydantic AI = agentes tipados futuros
Hermes = HITL / fail-closed approval gateway
Docker = sandbox obligatorio
GitHub = fuente de verdad
```

## Alcance HITO_001

Este hito solo crea el esqueleto base:

```text
factory_prefect/contracts/messages.py
factory_prefect/contracts/ledgers.py
factory_prefect/flows/software_factory_flow.py
```

No conecta LLM, no ejecuta Docker, no toca Hermes, no toca GCP y no modifica runtime productivo.
