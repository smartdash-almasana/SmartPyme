# REPO BRANCH SANITIZATION — 2026-05-12

## Estado inicial

Existían aliases y ramas mergeadas históricas.

`product/laboratorio-mvp-vendible` fue confirmado como rama activa del producto.

`main` quedó como trunk histórico/freeze de transición Factory V3.

Se detectaron ramas con valor ADR/histórico y ramas AI-layer no integradas.

---

## Acciones ejecutadas

### Ramas locales eliminadas

- `factory/ts-006-jobs-sovereign-persistence`
- `main`
- `feat/excel-diagnostic-flow`
- `factory/v3-a2a-adk-scaffold` (solo local)

### Ramas remotas eliminadas

- `factory/ts-001-entity-sovereignty`
- `factory/ts-002-identity-propagation`
- `factory/ts-004-no-leak-global`
- `factory/ts-005-sovereign-query-endpoints`
- `factory/ts-006-jobs-sovereign-persistence`
- `remediacion-veredictos-cliente-id`
- `reset/from-hito-009`
- `factory/ts-001-router-e2e`

---

## Estado consolidado

### Producto activo

- `product/laboratorio-mvp-vendible`

### Factoría activa preservada

- `factory/v2-blueprint-langgraph-lowcost`
- `factory/v3-a2a-adk-scaffold`

### AI Layer histórico preservado

- `factory/ts-016-019-ai-layer-on-ts-006`
- `factory/ts-021-soft-interpretation-consumer`
- `factory/ts-023-ai-intake-orchestrator`

### ADR / documentación preservada

- `docs/*`
- `export/auditoria-total`
- `chore/hermes-professional-config`

---

## Hallazgos arquitectónicos

El repositorio convergió desde:

- factoría soberana,
- runtime multiagente,
- AI layer experimental,

hacia **producto clínico-operacional vendible**.

`product/laboratorio-mvp-vendible` contiene actualmente:

- Telegram runtime
- BEM integration
- curated evidence
- diagnostic engine
- SmartGraph boundary
- clinical operational contracts
- artifact reporting

`main` quedó como freeze histórico de Factory V3 + ADRs SmartGraph.

---

## Riesgos preservados deliberadamente

No se eliminaron ramas con:

- código AI no integrado
- ADRs únicos
- genealogía operacional
- contracts históricos
- freeze V3
- experimentación LangGraph

---

## Resultado

Repositorio saneado sin pérdida de trazabilidad crítica.

Producto y factoría quedaron conceptualmente separados sin fragmentar físicamente el monorepo.

---

## Índice de ramas preservadas

| Rama | Familia | Motivo de preservación | Acción futura recomendada |
|------|---------|------------------------|---------------------------|
| `product/laboratorio-mvp-vendible` | producto | Producto activo | Mantener como rama principal de desarrollo |
| `main` | trunk | Freeze histórico Factory V3 + ADRs SmartGraph | Preservar como referencia histórica |
| `factory/v2-blueprint-langgraph-lowcost` | factoría | Factoría V2 activa | Mantener para referencia de blueprint |
| `factory/v3-a2a-adk-scaffold` | factoría | Freeze Factory V3 | Preservar como scaffold de referencia |
| `factory/v21-bootstrap` | factoría | Overlay histórico | Preservar como referencia de bootstrap |
| `factory/ts-016-019-ai-layer-on-ts-006` | ai-layer | AI layer histórico consolidado | Preservar como referencia arquitectónica |
| `factory/ts-021-soft-interpretation-consumer` | ai-layer | AI layer no integrado | Preservar para posible integración futura |
| `factory/ts-023-ai-intake-orchestrator` | ai-layer | AI orchestrator no integrado | Preservar para posible integración futura |
| `factory/ts-016` | ai-layer | Rama histórica parcial del AI layer | Preservar como genealogía técnica |
| `factory/ts-017` | ai-layer | Rama histórica parcial del AI layer | Preservar como genealogía técnica |
| `factory/ts-018` | ai-layer | Rama histórica parcial del AI layer | Preservar como genealogía técnica |
| `factory/ts-019` | ai-layer | Rama histórica parcial del AI layer | Preservar como genealogía técnica |
| `docs/*` | documentación | ADR/documentación | Preservar como registro de decisiones |
| `export/auditoria-total` | vault | Vault histórico de contratos | Preservar como auditoría histórica |
| `chore/hermes-professional-config` | configuración | Configuración histórica Hermes | Preservar como referencia de config |
| `builder/ts-001-entity-sovereignty` | builder | Builder histórico entity sovereignty | Preservar como referencia de soberanía |
