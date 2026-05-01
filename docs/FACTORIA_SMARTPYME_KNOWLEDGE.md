# FACTORIA SMARTPYME — KNOWLEDGE BASE

## 1. Proposito del Sistema

SmartPyme es un motor deterministico de auditoria y reconciliacion de datos.

No es un chatbot.
No es un CRM.

Es:

```text
Sistema de comparacion, validacion y generacion de hallazgos
sobre datos distribuidos (Excel, PDFs, WhatsApp, APIs, etc.)
```

## 2. Principios Fundamentales

### 2.1 Soberania por cliente

```text
cliente_id es obligatorio en TODAS las entidades
```

Reglas:

- nunca inferir cliente_id
- nunca usar defaults silenciosos
- nunca mezclar datos entre clientes
- lectura cruzada = NULL, comportamiento tipo 404

### 2.2 Contratos primero

Orden obligatorio:

```text
1. contracts
2. repository / DB
3. services
4. pipeline
5. tests
```

Nunca al reves.

### 2.3 Hallazgos como output

Todo resultado debe ser:

```text
Entidad + diferencia cuantificada + comparacion explicita
```

Ejemplo:

```text
Factura A vs Excel:
- Producto: X
- Diferencia: $120
- Fuente: PDF vs Excel
```

## 3. Arquitectura General

```text
Pipeline:
Document -> Evidence -> Facts -> Canonical -> Entities -> Comparison -> Findings
```

Capas:

1. Contracts: dataclasses puras.
2. Repositories: persistencia SQLite multi-tenant.
3. Services: logica deterministica.
4. Pipeline: orquestacion.

## 4. Modelo de Datos Core

### 4.1 Nivel Documento

- RawDocument
- DocumentRecord

### 4.2 Nivel Evidencia

- EvidenceChunk
- RetrievalResult

### 4.3 Nivel Facts

- ExtractedFactCandidate

### 4.4 Nivel Canonical

- CanonicalRowCandidate

## 5. Estado Actual del Desarrollo

```text
TS_008A  DONE  cliente_id en documentos
TS_008B  DONE  cliente_id en evidencia
TS_008C1 DONE  cliente_id en facts end-to-end
TS_008C2 DONE  cliente_id en canonical, validado en scope acotado
```

## 6. Multi-Tenancy

```text
cliente_id SIEMPRE:
- en contratos
- en DB
- en servicios
- en pipeline
```

DB:

```sql
PRIMARY KEY (cliente_id, id)
```

## 7. Pipeline Operativo

```text
Pipeline(cliente_id)
  -> FactExtractionService
  -> CanonicalizationService
  -> EntityResolutionService
  -> ComparisonService
  -> FindingsService
```

Regla: el cliente_id se propaga desde contratos y objetos del dominio. No se infiere desde metadata.

## 8. Gobernanza Hermes

Hermes es el orquestador de la factoria. No debe depender de instrucciones sueltas de chat.

Archivos de control esperados:

```text
factory/control/NEXT_CYCLE.md
factory/ai_governance/tasks/*.yaml
factory/evidence/<task_id>/
```

Modos:

### ANALYSIS_ONLY

- solo lectura
- sin escribir archivos
- salida con alcance, riesgo y plan minimo

### WRITE_AUTHORIZED

- escritura solo dentro del alcance autorizado
- una unidad por ciclo
- tests acotados
- evidencia obligatoria

### STOP_AND_REPORT

- cortar ejecucion
- reportar estado, bloqueo y siguiente paso minimo

## 9. Skill Principal

```text
lean_audit_vm_protocol
```

Reglas:

- no escribir sin autorizacion
- reportar alcance antes de implementar
- evitar cambios masivos
- no validar trabajo propio sin evidencia reproducible

## 10. Problemas Detectados y Soluciones

### Hermes borra archivos

Solucion:

- bloquear comandos destructivos en config
- usar checkpoints
- registrar diff antes de cierre

### Truncamiento de archivos

Solucion:

- evitar reescrituras completas cuando sea posible
- preferir cambios incrementales
- inspeccionar diff antes de commit

### Perdida de contexto

Solucion:

- usar docs versionados como fuente de verdad
- proteger ultimos ciclos relevantes
- no usar memoria conversacional como estado operativo

## 11. DB Strategy

SQLite por ahora:

```text
facts.db
canonical.db
entities.db
findings.db
```

Migraciones:

- no automaticas por ahora
- cambios de esquema se validan con DBs temporales de tests
- cada repositorio multi-tenant debe usar clave compuesta o filtro explicito por cliente_id

## 12. Integraciones Futuras

### Telegram

- owner controla sistema
- inputs y outputs operativos

### Notion PARKED

- exportacion de reportes
- requiere identidad y trazabilidad cerradas

## 13. Filosofia de Diseno

```text
Core deterministico en Python
IA solo para construir y auditar el sistema
```

Prohibido:

- logica critica en LLM
- decisiones sin trazabilidad
- defaults silenciosos de cliente_id

## 14. Roadmap inmediato

```text
TS_008C2 DONE  cliente_id en canonical
TS_008C3       validacion pipeline facts -> canonical -> entity resolution
TS_009         Hermes task loop soberano
TS_010         Hermes ejecuta ciclo real con evidencia
TS_011         comparison engine robusto
TS_012         hallazgos accionables
```

## 15. Regla de oro

```text
Si no podes rastrear cliente_id, el sistema esta mal disenado.
```

## 16. Prompt base de continuidad

```text
Trabajar en rama:
factory/ts-006-jobs-sovereign-persistence

Modo:
- un paso por vez
- sin teoria
- sin cambios fuera de alcance
- contrato primero
- evidencia obligatoria

Objetivo actual:
continuar ciclo Hermes/Factory desde TaskSpec versionada.
```

## 17. Estado mental del sistema

```text
De script a sistema industrial multi-tenant.
```

## 18. Uso de este archivo

- Fuente base de continuidad para GPT, Hermes, Gemini y Codex.
- Referencia para crear TaskSpecs.
- No reemplaza tests ni evidencia.
- No habilita cambios fuera de alcance.
