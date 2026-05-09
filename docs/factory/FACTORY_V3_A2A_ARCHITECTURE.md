# FACTORY V3 — Arquitectura A2A + Google ADK

## Separación fundamental

FACTORÍA != PRODUCTO.

### Producto SmartPyme
- diagnóstico operacional PyME
- tenant_id
- EvidenceRecord
- Finding
- OutputReport
- recepción del caos PyME

### Factoría SmartPyme
- construcción multiagente
- generación de código
- revisión
- sandbox
- artifacts persistentes
- HITL
- PR workflows

## Stack rector

### Google ADK
Runtime/capa agente.

Responsabilidades:
- workflow agents
- sequential agents
- tools
- artifacts
- sessions/state
- evaluation
- interoperabilidad A2A/MCP

No gobierna:
- memoria soberana
- tenant core
- políticas SmartPyme
- persistencia clínica del producto

### A2A
Contrato de comunicación agente-agente.

Regla:
ningún agente comparte memoria implícita.

Toda comunicación ocurre mediante:
- YAML
- JSON
- Markdown
- artifacts persistentes

### MCP
Frontera herramienta/recurso.

MCP conecta:
- GitHub
- Drive
- Supabase
- Docker
- filesystem
- APIs

### Prefect
Secuenciador durable.

Prefect NO pasa variables en memoria.

Prefect:
- dispara agentes
- monitorea estados
- persiste task lifecycle
- reinicia workflows

### Hermes
HITL/autorización.

Ningún merge crítico ocurre sin aprobación.

### Docker Sandbox
Toda ejecución:
- aislada
- efímera
- auditada
- reproducible

## Artifact Ledger

Directorio conceptual:

artifacts/
ledgers/
agent_cards/
tasks/
findings/
reports/

Artifacts son APIs internas persistentes.

## Agentes iniciales

- planner_agent
- architect_agent
- coder_agent
- reviewer_agent
- security_agent
- documentation_agent
- release_agent
- hermes_gateway_agent

## Flujo

planner_agent
→ genera PlanArtifact YAML

architect_agent
→ refina arquitectura

coder_agent
→ lee artifacts previos
→ genera CodeArtifact

reviewer_agent
→ revisa artifacts

security_agent
→ verifica policies

hermes_gateway_agent
→ aprobación humana

release_agent
→ genera PR/report

## Reglas soberanas

- ningún agente ejecuta fuera sandbox
- ningún merge sin HITL
- ningún artifact sin lineage
- ningún task sin tenant_id
- ningún diagnóstico sin evidencia
- ningún agente depende de memoria implícita

## Veredicto arquitectónico

A2A pertenece a FACTORÍA.

No al core clínico del producto.
