# Product Boundary Guard

## Propósito

Prevenir la contaminación cruzada del runtime del producto (`PRODUCT_RUNTIME`) con código de factory, experimentos o extracción.

## Directorios Protegidos

Los siguientes directorios NO pueden importar módulos prohibidos:

- `app/`
- `core/`
- `services/`
- `models/`

## Imports Prohibidos

Desde los directorios protegidos está prohibido importar:

- `factory*`
- `factory_v2*`
- `factory_v3*`
- `experiments*`
- `extraction*`

## Rationale

El código de producción debe mantenerse aislado de:
- Código de generación/factory (usado solo para bootstrap)
- Experimentos (código no consolidado)
- Módulos de extracción (herramientas auxiliares)

Esta separación garantiza que el runtime del producto sea estable, predecible y libre de dependencias de herramientas de desarrollo.

## Excepciones Explícitas

Algunos directorios pueden estar temporalmente excluidos del enforcement mediante el archivo `config/product_boundary_guard_exceptions.json`.

### Excepción actual: `app/mcp/`

El directorio `app/mcp/` está marcado como excepción temporal porque:

1. **Contexto arquitectónico**: MCP (Model Context Protocol) es un componente de integración que requiere acceso a módulos de factory para configuración dinámica.
2. **Estado temporal**: Esta exclusión no implica un boundary estable. Es una medida transitoria mientras se consolida la arquitectura de MCP.
3. **Riesgo controlado**: Las violaciones en este directorio son conocidas y aceptadas conscientemente hasta su refactorización.

### Archivo de excepciones

```json
{
  "allowed_prefixes": [
    "app/mcp/"
  ]
}
```

**Importante**: Agregar nuevas excepciones requiere revisión arquitectónica explícita. No se deben agregar más excepciones sin justificación documentada.

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
Total scanned files:       267
Allowed technical debt:    9
Forbidden violations:      2
CI status:                 FAIL
============================================================

EXCEPTIONS IGNORED (configured in product_boundary_guard_exceptions.json):
--------------------------------------------------
  - app/mcp/__init__.py
  - app/mcp/tools/queue_list_tool.py
  ...
--------------------------------------------------

PRODUCT BOUNDARY VIOLATIONS DETECTED:
--------------------------------------------------
/workspace/services/document_ingestion_service.py: from extraction.chunker import ...
/workspace/services/document_ingestion_service.py: from extraction.docling_parser import ...
--------------------------------------------------
```

**Interpretación operacional:**
- `Total scanned files`: Cantidad de archivos Python bajo directorios protegidos (`app/`, `core/`, `services/`, `models/`)
- `Allowed technical debt`: Archivos excluidos explícitamente vía configuración (deuda técnica conocida)
- `Forbidden violations`: Imports prohibidos detectados fuera de excepciones (requieren atención)
- `CI status`: `PASS` si no hay violaciones, `FAIL` si hay al menos una violación

### Formato JSON

Ejemplo de salida JSON:

```json
{
  "scanned_files": 267,
  "allowed_exceptions_count": 9,
  "violations_count": 2,
  "violations": [
    "/workspace/services/document_ingestion_service.py: from extraction.chunker import ...",
    "/workspace/services/document_ingestion_service.py: from extraction.docling_parser import ..."
  ],
  "allowed_exceptions": [
    "app/mcp/__init__.py",
    "app/mcp/tools/queue_list_tool.py",
    ...
  ],
  "status": "FAIL"
}
```

**Campos del JSON:**
- `scanned_files`: Total de archivos Python escaneados
- `allowed_exceptions_count`: Cantidad de archivos excluidos por configuración
- `violations_count`: Cantidad de violaciones detectadas
- `violations`: Lista detallada de violaciones (archivo + import)
- `allowed_exceptions`: Lista de archivos excluidos
- `status`: `"PASS"` o `"FAIL"` según resultado

### Códigos de exit

- Exit code 0: No se detectaron violaciones (`status: PASS`)
- Exit code 1: Se detectaron violaciones (`status: FAIL`)
