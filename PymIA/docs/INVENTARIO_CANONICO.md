# INVENTARIO CANÓNICO — PymIA/docs

Última actualización: en progreso (secuencial)

---

## Formato de cada entrada

```
destino:               ruta relativa dentro de PymIA/docs/
fuente_original:       ruta en SmartPyme repo
estado:                copiado_sin_modificaciones | normalizado_minimo | placeholder | fabricado_ELIMINADO
provenance:            verificado_fisicamente | fuente_externa_validada | sin_fuente
contaminacion:         ninguna | paths_vm_removidos | referencias_factory_removidas | secretos_removidos
decision:              incluido | placeholder | pendiente
```

---

## vision/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `vision/SMARTPYME_LABORATORIO_PYME_Y_ESTABILIZACION_OPERACIONAL.md` | no encontrada en repo local | placeholder | fuente_externa_validada | ninguna | placeholder — incorporar fuente real |
| `vision/SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md` | no encontrada en repo local | placeholder | fuente_externa_validada | ninguna | placeholder — incorporar fuente real |

**Nota:** Versiones fabricadas desde memoria fueron detectadas y eliminadas. Reemplazadas por placeholders con provenance explícito.

---

## fundamentos/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `fundamentos/cosmovision-clinico-operacional.md` | `docs/adr/ADR-005-cosmovision-clinico-operacional-smartpyme.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `fundamentos/organismo-pyme.md` | `docs/nociones_conceptuales/NOCION_001_ORGANISMO_PYME.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `fundamentos/metodo-hipotetico-deductivo.md` | `docs/architecture/HYPOTHETICO_DEDUCTIVE_METHOD.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `fundamentos/primer-tiempo-logico.md` | `docs/adr/ADR-CAT-001-pyme-anamnesis-and-knowledge-catalogs.md` | normalizado_minimo | verificado_fisicamente | ninguna | incluido — extracto de sección "Primer tiempo lógico" |

---

## epistemologia/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `epistemologia/contrato-epistemologico-smartgraph.md` | `docs/adr/ADR-EP-001-smartgraph-epistemic-contract.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `epistemologia/protocolo-conversacional-hermes.md` | `docs/adr/ADR-EP-002-hermes-conversational-protocol.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `epistemologia/modelo-verdad-soberania.md` | `docs/adr/ADR-EP-003-operational-truth-and-sovereignty-model.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |

---

## arquitectura/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `arquitectura/arquitectura-maestra.md` | `docs/architecture/SMARTPYME_ARCHITECTURE_MASTER.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `arquitectura/domain-classification.md` | `docs/architecture/DOMAIN_CLASSIFICATION_2026-05-12.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `arquitectura/entropy-routing.md` | `docs/adr/ADR-ENT-001-entropy-routing-and-sovereign-ingestion.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `arquitectura/capability-runtime.md` | `docs/adr/ADR-CAP-001-capability-runtime-contract.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `arquitectura/harness-engineering.md` | `docs/adr/ADR-004-harness-engineering-principle.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `arquitectura/palantir-principles.md` | `docs/architecture/PALANTIR_PRINCIPLES_FOR_SMARTPYME.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `arquitectura/orchestration-boundary.md` | `docs/hermes-producto/ORCHESTRATION_BOUNDARY.md` | normalizado_minimo | verificado_fisicamente | ninguna | incluido — agregada sección boundary MCP derivada de fix quirúrgico documentado |

---

## producto/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `producto/capa-00-canal-entrada.md` | `docs/product/SMARTPYME_CAPA_00_CANAL_ENTRADA_CRUDA.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `producto/capa-01-admision-epistemologica.md` | `docs/product/SMARTPYME_CAPA_01_ADMISION_EPISTEMOLOGICA.md` | pendiente | verificado_fisicamente | ninguna | pendiente |
| `producto/protocolo-anamnesis-mvp.md` | `docs/hermes-producto/PROTOCOLO_ANAMNESIS_MVP.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `producto/asertividades-operativas.md` | `docs/architecture/OPERATIONAL_ASSERTIVENESS_REPORTS.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |

---

## contratos/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `contratos/contratos-clinicos-operacionales.md` | `docs/contracts/SMARTPYME_CLINICAL_OPERATIONAL_CONTRACTS.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `contratos/evidence-chain-v1.md` | `docs/product/EVIDENCE_CHAIN_CONTRACT_V1.md` | normalizado_minimo | verificado_fisicamente | referencias_factory_removidas | incluido — sección 10 "Conformidad con Fact Factory" removida (contiene path factory/evidence/ y placeholder [COMMIT_HASH]) |
| `contratos/owner-decision-v1.md` | `docs/product/OWNER_DECISION_CONTRACT_V1.md` | normalizado_minimo | verificado_fisicamente | referencias_factory_removidas | incluido — referencia a "flujo soberano de factoría" y "AUDIT_GATE" removidas de sección 7; contrato de soberanía del dueño preservado íntegro |

---

## catalogo/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `catalogo/atlas-sintomas-patologias.md` | `docs/architecture/PYME_SYMPTOM_PATHOLOGY_ATLAS.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `catalogo/diseno-catalogo-clinico.md` | `docs/architecture/SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` | pendiente | verificado_fisicamente | ninguna | pendiente |
| `catalogo/anamnesis-y-catalogos.md` | `docs/adr/ADR-CAT-001-pyme-anamnesis-and-knowledge-catalogs.md` | pendiente | verificado_fisicamente | ninguna | pendiente |

---

## hermes/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `hermes/soul.md` | `infra/hermes-product/SOUL.md` | copiado_sin_modificaciones | verificado_fisicamente | ninguna | incluido |
| `hermes/arquitectura-conversacional.md` | `docs/hermes-producto/README.md` | pendiente | verificado_fisicamente | paths_vm_removidos | pendiente |
| `hermes/boundary-orquestacion.md` | `docs/hermes-producto/ORCHESTRATION_BOUNDARY.md` | pendiente | verificado_fisicamente | ninguna | pendiente — ya existe en arquitectura/, evaluar si duplicar o referenciar |

---

## gobernanza/

| destino | fuente_original | estado | provenance | contaminacion | decision |
|---|---|---|---|---|---|
| `gobernanza/agents.md` | `AGENTS.md` | pendiente | verificado_fisicamente | referencias_factory_removidas | pendiente |
| `gobernanza/agent-harness-governance.md` | `docs/product/smartpyme_agent_harness_governance_v_1.md` | pendiente | verificado_fisicamente | ninguna | pendiente |
| `gobernanza/determinismo.md` | `.agent/rules/determinismo.md` | pendiente | verificado_fisicamente | ninguna | pendiente |

---

## Dependencias conceptuales detectadas

| documento | depende de |
|---|---|
| `contratos/contratos-clinicos-operacionales.md` | `epistemologia/contrato-epistemologico-smartgraph.md` |
| `contratos/evidence-chain-v1.md` | `contratos/contratos-clinicos-operacionales.md` |
| `contratos/owner-decision-v1.md` | `contratos/evidence-chain-v1.md` |
| `catalogo/atlas-sintomas-patologias.md` | `fundamentos/metodo-hipotetico-deductivo.md` |
| `catalogo/diseno-catalogo-clinico.md` | `catalogo/atlas-sintomas-patologias.md` |
| `producto/capa-01-admision-epistemologica.md` | `producto/capa-00-canal-entrada.md` |
| `hermes/soul.md` | `arquitectura/orchestration-boundary.md` |
| `gobernanza/determinismo.md` | `contratos/contratos-clinicos-operacionales.md` |
