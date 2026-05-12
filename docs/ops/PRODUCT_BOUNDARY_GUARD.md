# Product Boundary Guard

## Propósito

Prevenir la contaminación cruzada del runtime del producto (`PRODUCT_RUNTIME`) con código de factory o experimentos, mientras se reconocen componentes compartidos que son parte operacional del runtime.

## Directorios Protegidos

Los siguientes directorios NO pueden importar módulos prohibidos:

- `app/`
- `core/`
- `services/`
- `models/`

## Clasificación de Imports

### A) FORBIDDEN_DEPENDENCIES (Contaminación)

Desde los directorios protegidos está **prohibido** importar:

- `factory*`
- `factory_v2*`
- `factory_v3*`
- `experiments*`

Estos imports representan contaminación de herramientas de desarrollo/bootstrap y causan fallo en el CI.

### B) TECHNICAL_DEBT_EXCEPTIONS (Deuda Técnica Permitida)

Directorios excluidos explícitamente vía configuración (`config/product_boundary_guard_exceptions.json`):

- `app/mcp/*`

Estos archivos son ignorados por el guard pero se reportan como deuda técnica conocida.

### C) SHARED_RUNTIME_COMPONENTS (Componentes Compartidos del Runtime)

Módulos que son parte operacional del runtime del producto:

- `extraction/*`

**Rationale**: Los módulos `extraction.parse_pdf` y `extraction.split_document` están en el hot path de ingestión documental y son componentes funcionales del producto, no herramientas experimentales. Estos imports se **reportan para observabilidad** pero **NO causan fallo** en el CI.

## Rationale

El código de producción debe mantenerse aislado de:
- Código de generación/factory (usado solo para bootstrap)
- Experimentos (código no consolidado)

Pero puede depender de:
- Componentes compartidos de runtime (ej. `extraction/*` para ingestión documental)

Esta separación garantiza que el runtime del producto sea estable, predecible y libre de dependencias de herramientas de desarrollo, mientras reconoce dependencias operacionales legítimas.

## Excepciones Explícitas

Algunos directorios pueden estar temporalmente excluidos del enforcement mediante el archivo `config/product_boundary_guard_exceptions.json`.

### Excepción actual: `app/mcp/`

El directorio `app/mcp/` está marcado como excepción temporal porque:

1. **Contexto arquitectónico**: MCP (Model Context Protocol) es un componente de integración que requiere acceso a módulos de factory para configuración dinámica.
2. **Estado temporal**: Esta exclusión no implica un boundary estable. Es una medida transitoria mientras se consolida la arquitectura de MCP.
3. **Riesgo controlado**: Las violaciones en este directorio son conocidas y aceptadas conscientemente hasta su refactorización.

### Shared Runtime: `extraction/*`

El módulo `extraction/*` ya no se considera contaminación porque:

1. **Funcionalidad operacional**: `parse_pdf` y `split_document` son parte del pipeline de ingestión documental en producción.
2. **Hot path del producto**: Estos componentes se ejecutan en el flujo principal de procesamiento de documentos.
3. **No es experimental**: A diferencia de factory/experiments, extraction es un componente consolidado del runtime.

**Importante**: Que `extraction/*` sea clasificado como shared runtime no significa que cualquier módulo pueda importarlo indiscriminadamente. Solo se reporta para observabilidad; la decisión arquitectónica de usar estos componentes sigue requiriendo justificación.

### Archivo de excepciones

```json
{
  "allowed_prefixes": [
    "app/mcp/"
  ],
  "shared_runtime_components": [
    "extraction"
  ]
}
```

**Importante**: Agregar nuevas excepciones o shared components requiere revisión arquitectónica explícita. No se deben agregar sin justificación documentada.

## Uso

### Ejecución local

```bash
# Salida normal (resumen legible)
python scripts/guard_product_boundaries.py

# Salida JSON (para integración con CI/CD)
python scripts/guard_product_boundaries.py --json
```

### GitHub Actions

El check se ejecuta automáticamente en cada push y PR a través del workflow `product-boundary-guard.yml`.

## Salida

### Formato normal

Ejemplo de salida en formato legible:

```
============================================================
PRODUCT BOUNDARY GUARD - SUMMARY
============================================================
Total scanned files:          267
Allowed technical debt:       9
Shared runtime dependencies:  2
Forbidden violations:         0
CI status:                    PASS
============================================================

EXCEPTIONS IGNORED (configured in product_boundary_guard_exceptions.json):
--------------------------------------------------
  - app/mcp/__init__.py
  - app/mcp/tools/queue_list_tool.py
  ...
--------------------------------------------------

SHARED RUNTIME DEPENDENCIES (extraction/* - operational runtime components):
--------------------------------------------------
  - /workspace/services/document_ingestion_service.py: from extraction.chunker import ...
  - /workspace/services/document_ingestion_service.py: from extraction.docling_parser import ...
--------------------------------------------------
```

**Interpretación operacional:**
- `Total scanned files`: Cantidad de archivos Python bajo directorios protegidos (`app/`, `core/`, `services/`, `models/`)
- `Allowed technical debt`: Archivos excluidos explícitamente vía configuración (deuda técnica conocida)
- `Shared runtime dependencies`: Imports de componentes compartidos del runtime (ej. `extraction/*`). Se reportan para observabilidad pero NO causan fallo.
- `Forbidden violations`: Imports prohibidos detectados fuera de excepciones (`factory*`, `experiments*`). Requieren atención inmediata y causan fallo en CI.
- `CI status`: `PASS` si no hay violaciones prohibidas, `FAIL` si hay al menos una violación de tipo `FORBIDDEN_DEPENDENCIES`

### Formato JSON

Ejemplo de salida JSON:

```json
{
  "scanned_files": 267,
  "allowed_exceptions_count": 9,
  "shared_runtime_deps_count": 2,
  "violations_count": 0,
  "violations": [],
  "allowed_exceptions": [
    "app/mcp/__init__.py",
    "app/mcp/tools/queue_list_tool.py",
    ...
  ],
  "shared_runtime_deps": [
    "/workspace/services/document_ingestion_service.py: from extraction.chunker import ...",
    "/workspace/services/document_ingestion_service.py: from extraction.docling_parser import ..."
  ],
  "status": "PASS"
}
```

**Campos del JSON:**
- `scanned_files`: Total de archivos Python escaneados
- `allowed_exceptions_count`: Cantidad de archivos excluidos por configuración (technical debt)
- `shared_runtime_deps_count`: Cantidad de imports de componentes compartidos del runtime
- `violations_count`: Cantidad de violaciones prohibidas detectadas (`factory*`, `experiments*`)
- `violations`: Lista detallada de violaciones prohibidas (archivo + import)
- `allowed_exceptions`: Lista de archivos excluidos por configuración
- `shared_runtime_deps`: Lista detallada de imports de componentes compartidos (`extraction/*`)
- `status`: `"PASS"` si no hay violaciones prohibidas, `"FAIL"` si hay al menos una

### Códigos de exit

- Exit code 0: No se detectaron violaciones prohibidas (`status: PASS`)
- Exit code 1: Se detectaron violaciones prohibidas (`status: FAIL`)

Los imports de `shared_runtime_components` (ej. `extraction/*`) NO causan fallo en el CI; solo se reportan para observabilidad.
