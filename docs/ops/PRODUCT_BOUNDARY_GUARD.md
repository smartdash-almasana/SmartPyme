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
