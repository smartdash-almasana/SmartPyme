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
python scripts/guard_product_boundaries.py
```

### GitHub Actions

El check se ejecuta automáticamente en cada push y PR a través del workflow `product-boundary-guard.yml`.

## Salida

- Exit code 0: No se detectaron violaciones
- Exit code 1: Se detectaron violaciones (se listan en stdout)
