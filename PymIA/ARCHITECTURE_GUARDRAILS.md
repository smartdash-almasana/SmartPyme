# PymIA Architecture Guardrails

Este documento fija los invariantes arquitectónicos para evitar la contaminación de PymIA.

## 1. SOURCE_OF_TRUTH_HIERARCHY

* código físico en PymIA
* tests verdes
* documentos físicos en PymIA/docs
* documentos externos validados con provenance
* memoria conversacional solo como pista, nunca como fuente

## 2. PROHIBICIONES ABSOLUTAS

* create_job
* workflow orchestration
* authorization flow
* decision_type
* factory imports
* app.* imports
* MCP legacy
* runtime Hermes duplicado
* LLM obligatorio en core

## 3. HERMES_BOUNDARY

* Hermes conversa
* PymIA computa
* Hermes no decide verdad operacional
* Hermes no crea jobs en admisión inicial
* Hermes entra solo por `HermesAdapter`
* `HermesAdapter` entra solo por `ClinicalConversationalPort`

## 4. DOCUMENTATION_POLICY

* no inventar documentos ausentes
* diferenciar fuente física vs fuente externa
* placeholders con provenance
* no reconstruir desde memoria

## 5. TEST_POLICY

* todo boundary nuevo debe tener tests
* tests deben verificar ausencia de contaminación
* caso canónico obligatorio:
  “vendo mucho pero no sé si gano plata”

## 6. ACCEPTANCE_CRITERIA

* pytest -q verde
* cero imports prohibidos
* demo offline funcionando
* ningún output menciona job/workflow/authorization/orchestration
