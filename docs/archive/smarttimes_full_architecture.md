# SMARTTIMES / SMARTPYME — ARQUITECTURA COMPLETA (FACTORÍA READY)

## 1. PROPÓSITO

Sistema operativo para PyMEs que:
- Reconstruye la realidad del negocio desde datos caóticos
- Detecta inconsistencias
- Genera hallazgos accionables
- Orquesta decisiones con humano en el loop

---

## 2. PIPELINE CORE

Ingesta → Normalización → Entity Resolution ↔ Clarification  
→ Orquestación → Comparación → Hallazgos → Comunicación → Acción

Referencia: smartcounter_informe_analitico.docx

---

## 3. CAPAS COMPLETAS DEL SISTEMA

### 3.1 Source Connectors
- Excel, PDF, WhatsApp, Email, APIs

### 3.2 OCR / Extraction Layer
- OCR
- parsing de tablas
- lectura documental

### 3.3 Core Pipeline
- ingestion
- normalization
- classification
- entities
- clarification
- reconciliation
- validation
- hallazgos
- communication
- actions

### 3.4 Orchestration Layer
- state machine
- jobs
- bloqueos (AWAITING_VALIDATION)
- eventos

### 3.5 MCP Layer
- Data MCP
- Context MCP
- Action MCP
- AI MCP
- Tool Registry

### 3.6 Module Layer
- módulos horizontales
- módulos verticales
- registry
- contracts

### 3.7 Knowledge Layer
- catálogo de patologías
- catálogo de comunicación
- catálogo de reglas
- catálogo de skills

### 3.8 Memory Layer
- entities
- facts
- relations
- findings
- clarifications
- decisions humanas

### 3.9 User Layer
- HermesBot
- Telegram
- WhatsApp
- email

### 3.10 System Growth Layer
- detección de oportunidades
- expansión automática de módulos

---

## 4. CATÁLOGO DE PATOLOGÍAS (EJEMPLOS)

- stock inconsistente
- ventas sin factura
- pagos sin imputación
- duplicación de proveedores
- subtotales en inventario
- familias de artículos fragmentadas

---

## 5. CATÁLOGO DE COMUNICACIÓN

Cada mensaje debe responder:
- qué pasa
- con quién
- cuánto
- qué hacer

---

## 6. MCP + TOOL REGISTRY

Campos obligatorios:
- tool_name
- capabilities
- cost_level
- latency
- reliability
- input_schema
- output_schema

---

## 7. MODELO DE EJECUCIÓN

Core = cerebro  
MCP = sistema nervioso  
n8n = ejecutor  

Referencia: smartcounter_orchestration_state_machine.pdf

---

## 8. LEYES DEL SISTEMA

- no alucinación
- humano en el loop
- trazabilidad total
- persistencia de decisiones
- consistencia sobre velocidad

Referencia: smartcounter_consistency_validation_framework.pdf

---

## 9. FACTORÍA (VERTEX READY)

Agentes:

- director
- arquitecto
- constructor
- auditor
- QA
- integrador

Pipeline de fabricación:

objetivo → contrato → código → test → auditoría → integración → veredicto

---

## 10. RESPUESTA CRÍTICA

¿Vertex puede usar esto?

SÍ, pero solo si:

- este archivo está en repo accesible
- se carga como contexto (prompt base o memoria)
- se usa como fuente de verdad en Agent Engine

Vertex NO “ve chats”.
Vertex SOLO usa:
- archivos
- prompts
- contextos explícitos

---

## 11. CONCLUSIÓN

Esto ya es arquitectura de producto final + arquitectura de factoría.

No es MVP.
Es sistema operativo completo listo para ser fabricado por agentes.
