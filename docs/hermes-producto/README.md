# Hermes Producto — Arquitectura Conversacional y Orquestacional Canónica

## Estado

Documento canónico vigente para Hermes Producto / Hermes SmartPyme.

Este documento reemplaza descripciones parciales, experimentales o ambiguas de la capa conversacional y orquestacional de Hermes Producto.

## Principio rector

```text
La IA interpreta.
Pydantic valida.
El kernel determinístico decide.
El dueño confirma.
```

Hermes Producto no es un cerebro soberano de negocio. Hermes Producto es la capa conversacional y orquestacional que conecta al dueño con SmartPyme mediante contratos verificables.

## Flujo oficial

```text
Telegram dueño
→ Hermes Producto / Hermes SmartPyme
→ AI Layer oficial
→ Validación Pydantic
→ SmartPyme Kernel
→ BEM / Curated Evidence
→ Diagnóstico determinístico
→ Hallazgos accionables
→ Telegram dueño
```

## Responsabilidades de Hermes Producto

Hermes Producto puede:

- recibir mensajes del dueño por Telegram;
- interpretar intención operacional;
- solicitar aclaraciones cuando falta contexto;
- orquestar llamadas hacia contratos SmartPyme;
- activar carga documental;
- activar BEM cuando corresponda;
- consumir evidencia curada;
- redactar respuestas comprensibles para el dueño;
- preservar trazabilidad conversacional.

Hermes Producto no puede:

- inventar evidencia;
- decidir hallazgos finales sin kernel;
- modificar verdad operacional fuera de contratos;
- reemplazar BEM;
- reemplazar curated evidence;
- reemplazar diagnóstico determinístico;
- operar con wrappers o proxies no documentados;
- depender de runtimes artesanales.

## AI Layer oficial

La capa AI oficial es una frontera Soft Core.

Debe vivir bajo:

```text
app/ai/
```

Responsabilidad:

```text
interpretación contextual blanda
```

Contrato esperado:

```text
OwnerMessageInterpretation
SoftInterpretationResult
```

La AI Layer puede extraer:

- intención;
- entidades;
- variables;
- evidencia mencionada;
- dudas;
- confianza.

La AI Layer no persiste, no decide negocio y no emite hallazgos finales.

## Kernel SmartPyme

SmartPyme Kernel conserva la soberanía determinística.

Responsabilidades:

- reglas operacionales;
- reconciliación;
- comparación;
- diagnóstico;
- persistencia;
- curated evidence;
- hallazgos accionables;
- trazabilidad.

El kernel no conversa. El kernel decide.

## BEM y Curated Evidence

BEM procesa documentos cuando el flujo lo requiere.

Flujo documental oficial:

```text
Telegram documento
→ Hermes Producto
→ carga controlada
→ BEM
→ Curated Evidence
→ Kernel diagnóstico
→ Hallazgos
→ Telegram
```

## Configuración oficial requerida

Debe existir una única configuración operativa para Hermes Producto.

Debe declarar:

- provider permitido;
- modelo permitido;
- límites de streaming;
- tool/contracts permitidos;
- política de fallback;
- observabilidad;
- timeouts;
- Telegram runtime;
- BEM integration;
- curated evidence integration.

Cualquier configuración duplicada, implícita o artesanal debe marcarse como `DEPRECATED` o eliminarse.

## Componentes actualmente bajo revisión

Los siguientes componentes existen, pero quedan clasificados como pendientes de canonización:

```text
app/adapters/hermes_product_adapter.py
app/runtime/hermes_product_loader.py
app/runtime/hermes_vertex_gemma_client.py
```

Estado:

```text
PENDING_CANONICAL_REVIEW
```

No se consideran oficiales hasta que cumplan este documento.

## Prohibiciones explícitas

Queda prohibido:

```text
runtime artesanal
proxy ambiguo
wrapper no documentado
modelo configurado fuera del contrato oficial
servicio paralelo no canónico
mezcla de responsabilidades
```

## Documentación vigente relacionada

Documentación vigente permitida:

```text
docs/hermes-producto/README.md
docs/architecture/ai_layer.md
docs/technical/ts_016_019_ai_layer.md
```

Documentos anteriores deben ser revisados y marcados como:

```text
SUPERSEDED_BY docs/hermes-producto/README.md
```

## Criterio de cierre

Hermes Producto queda validado solo cuando exista evidencia de:

```text
Telegram → Hermes Producto → AI Layer → BEM / Curated Evidence → Kernel → Hallazgos → Telegram
```

con configuración única, sin runtime artesanal y sin servicios ambiguos.
