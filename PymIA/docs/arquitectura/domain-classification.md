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
```

### DOCUMENTATION_VAULT
```
docs/                   # ADRs, documentación operativa
```

---

## 3. Clasificación de Dependencias

### A) Forbidden Dependencies (Contaminación Prohibida)
**Origen:** `factory*`, `experiments*`
**Destino:** `app/`, `core/`, `services/`, `models/`
**Acción:** Bloqueo en CI, exit code 1.

### B) Technical Debt Exceptions (Deuda Técnica Explícita)
**Origen:** `app/mcp/*`
**Destino:** Cualquier dominio (requiere visibilidad transversal)
**Acción:** Permitido con registro explícito.

### C) Shared Runtime Dependencies (Componentes Compartidos Operacionales)
**Origen:** `extraction/*`
**Destino:** `services/`, `app/`
**Acción:** Permitido sin restricción.

---

## 4. Principios Rectores

1. **No nuevas contaminaciones:** Prohibido agregar imports desde factory/experiments hacia runtime productivo.
2. **Deuda explícita:** Toda excepción debe estar documentada.
3. **Boundaries auditables:** El script `guard_product_boundaries.py` debe ejecutarse en cada PR y push.
4. **Runtime protegido:** PRODUCT_RUNTIME mantiene integridad mediante bloqueo automático en CI.
