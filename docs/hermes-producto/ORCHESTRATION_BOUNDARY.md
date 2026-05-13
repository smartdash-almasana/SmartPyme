# Hermes Producto — Boundary de Orquestación

## Estado

Documento complementario canónico de `docs/hermes-producto/README.md`.

## Regla obligatoria

Hermes Producto / Hermes SmartPyme es obligatorio en el flujo conversacional del producto.

Telegram es solamente canal de entrada y salida.

BEM, Curated Evidence y SmartPyme Kernel son capacidades internas orquestadas por Hermes Producto.

## Flujo correcto

```text
Telegram
→ Hermes Producto
→ AI Layer
→ Pydantic
→ BEM / Curated Evidence, si corresponde
→ SmartPyme Kernel
→ Hallazgos
→ Hermes Producto
→ Telegram
```

## Flujo incorrecto

```text
Telegram → BEM
Telegram → SmartPyme Kernel
Telegram → Diagnóstico
```

Cualquier documento que permita leer esos atajos queda reemplazado por esta frontera.

## Criterio

Si Hermes Producto no está en el camino, el flujo no pertenece a la arquitectura oficial de SmartPyme Producto.
