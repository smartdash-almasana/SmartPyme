# Taxonomía Arquitectónica del Repositorio

**Fecha:** 2026-05-12  
**Estado:** Consolidado basado en evidencia operativa real  
**Rama:** `product/laboratorio-mvp-vendible`

---

## 1. Dominios Canónicos

El repositorio se estructura en seis dominios arquitectónicos diferenciados por propósito y restricciones de acoplamiento:

| Dominio | Propósito | Restricciones |
|---------|-----------|---------------|
| **PRODUCT_RUNTIME** | Código operacional del producto en producción | No puede importar de FACTORY ni AI_RESEARCH |
| **FACTORY_RUNTIME** | Scaffolding, generación de código, blueprints | Aislado; su salida alimenta PRODUCT pero no se mezcla |
| **CONTROL_PLANE** | Herramientas de gestión, MCP, orquestación externa | Requiere visibilidad transversal; excepción controlada |
| **SHARED_RUNTIME_COMPONENTS** | Componentes utilitarios usados por múltiples dominios | Estables, auditados, sin dependencias experimentales |
| **AI_RESEARCH_LAYER** | Experimentación, prototipos, integración de modelos | Aislado; no contamina runtime productivo |
| **DOCUMENTATION_VAULT** | ADRs, auditorías, registros históricos | Solo lectura; referencia arquitectónica |

---

## 2. Mapeo Actual del Repositorio

### PRODUCT_RUNTIME
```
app/                    # Aplicación principal (excepto app/mcp/)
core/                   # Núcleo de lógica de negocio
services/               # Servicios operacionales
models/                 # Modelos de datos del producto
```

### FACTORY_RUNTIME
```
factory*/               # Factoría V2 activa
factory_v2*/            # Blueprints LangGraph low-cost
factory_v3*/            # Freeze Factory V3 + ADRs SmartGraph
factory/ts-*            # Rutas históricas de factoría
```

### CONTROL_PLANE
```
app/mcp/                # Servidores MCP para herramientas externas
scripts/                # Scripts de governance y operación
config/                 # Configuraciones de guard y excepciones
```

### SHARED_RUNTIME_COMPONENTS
```
extraction/             # parse_pdf, split_document (ingestión operacional)
```

### AI_RESEARCH_LAYER
```
experiments/            # Prototipos no integrados al runtime
factory/ts-021-*        # Soft interpretation consumer (no integrado)
factory/ts-023-*        # AI intake orchestrator (no integrado)
```

### DOCUMENTATION_VAULT
```
docs/                   # ADRs, documentación operativa
export/auditoria-total  # Vault histórico de contratos
```

---

## 3. Clasificación de Dependencias

El boundary guard clasifica las dependencias cruzadas en tres categorías:

### A) Forbidden Dependencies (Contaminación Prohibida)
**Origen:** `factory*`, `factory_v2*`, `factory_v3*`, `experiments*`  
**Destino:** `app/`, `core/`, `services/`, `models/`  
**Acción:** Bloqueo en CI, exit code 1.

*Rationale:* La factoría y experimentación son fases temporales. Su código no debe permear el runtime productivo.

### B) Technical Debt Exceptions (Deuda Técnica Explícita)
**Origen:** `app/mcp/*`  
**Destino:** Cualquier dominio (requiere visibilidad transversal)  
**Acción:** Permitido con registro en `config/product_boundary_guard_exceptions.json`.

*Rationale:* MCP es CONTROL_PLANE y requiere acceso a múltiples dominios para exponer herramientas. Es deuda arquitectónica consciente, no contaminación accidental.

### C) Shared Runtime Dependencies (Componentes Compartidos Operacionales)
**Origen:** `extraction/*`  
**Destino:** `services/`, `app/`  
**Acción:** Permitido sin restricción; considerado parte del runtime.

*Rationale:* `extraction/parse_pdf` y `extraction/split_document` están en el hot path de ingestión documental del producto. Son componentes estables, no experimentales.

---

## 4. Caso Especial: MCP (Model Context Protocol)

### ¿Por qué MCP es CONTROL_PLANE?

MCP (`app/mcp/`) implementa servidores de contexto para herramientas externas (IDEs, asistentes AI, sistemas de observabilidad). Su función es **exponer** capacidades del sistema, no consumirlas como lógica de negocio.

### ¿Por qué está acoplado?

Para exponer herramientas, MCP necesita:
- Acceder a modelos (`models/`) para describir esquemas
- Invocar servicios (`services/`) para ejecutar acciones
- Leer configuración (`core/`) para contextualizar respuestas

Este acoplamiento es **intrínseco al patrón MCP**: un servidor que no puede ver el sistema que expone es inútil.

### ¿Por qué NO es simple contaminación?

1. **Direccionalidad:** MCP no modifica la lógica de PRODUCT_RUNTIME; solo la expone.
2. **Transparencia:** Las excepciones están declaradas explícitamente en configuración.
3. **Auditoría:** El boundary guard reporta cada archivo MCP ignorado como "allowed technical debt".
4. **Temporalidad:** Se reconoce como deuda hasta definir arquitectura de CONTROL_PLANE separada.

**No tratar MCP como contaminación accidental evita:**
- Falsos positivos en CI que ocultan violaciones reales
- Refactors prematuros sin criterio arquitectónico
- Pérdida de trazabilidad sobre deuda técnica consciente

---

## 5. Shared Runtime: extraction/*

### Evidencia Operacional

Los módulos `extraction/parse_pdf.py` y `extraction/split_document.py`:
- Son invocados en el hot path de ingestión documental
- No contienen experimentación ni código de investigación
- Tienen APIs estables usadas por `services/document_ingestion_service.py`
- Son requeridos para funcionamiento productivo del MVP

### Decisión de Clasificación

`extraction/*` se clasifica como **SHARED_RUNTIME_COMPONENTS**, no como AI_RESEARCH_LAYER.

**Implicaciones:**
- ✅ Permitido importar desde `app/`, `services/`, `core/`
- ✅ No cuenta como violación del boundary guard
- ✅ Sujeto a mismas restricciones de estabilidad que PRODUCT_RUNTIME
- ❌ No debe introducir dependencias experimentales nuevas

### Límite Claro

Si en el futuro se agrega código experimental a `extraction/`:
1. Debe aislarse en submódulos separados (ej. `extraction/experimental/`)
2. El boundary guard deberá actualizarse para bloquear imports desde esos submódulos
3. Los componentes operacionales deben permanecer en `extraction/` raíz

---

## 6. Política Actual de Boundaries

### Principios Rectores

1. **No nuevas contaminaciones:** Prohibido agregar imports desde factory/experiments hacia runtime productivo.
2. **Deuda explícita:** Toda excepción debe estar documentada en `config/product_boundary_guard_exceptions.json`.
3. **Boundaries auditables:** El script `guard_product_boundaries.py` debe ejecutarse en cada PR y push.
4. **Runtime protegido:** PRODUCT_RUNTIME mantiene integridad mediante bloqueo automático en CI.

### Estado del Sistema

| Categoría | Count | Estado |
|-----------|-------|--------|
| Forbidden violations | 0 | ✅ Clean |
| Technical debt (MCP) | 9 archivos | ⚠️ Explicito |
| Shared runtime (extraction) | 2 módulos | ✅ Operacional |

### Próximos Pasos (No Implementados)

Esta taxonomía **no prescribe** movimientos de código ni refactors futuros. Solo documenta el estado actual consolidado tras el ciclo de descubrimiento del boundary guard.

Cualquier evolución arquitectónica (separar CONTROL_PLANE, mover extraction, etc.) requerirá:
- ADR nuevo en `docs/architecture/`
- Plan de migración explícito
- Aprobación de governance

---

## Referencias Cruzadas

- Boundary Guard Script: `scripts/guard_product_boundaries.py`
- Configuración de Excepciones: `config/product_boundary_guard_exceptions.json`
- Documentación Operativa: `docs/ops/PRODUCT_BOUNDARY_GUARD.md`
- Workflow CI: `.github/workflows/product-boundary-guard.yml`
