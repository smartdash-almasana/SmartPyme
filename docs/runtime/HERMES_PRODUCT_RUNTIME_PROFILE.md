# Hermes Product Runtime Profile

Fecha: 2026-05-12
Estado: perfil mínimo real + bootstrap fail-closed

## Propósito

Hermes Producto es la capa conversacional de bajo privilegio para SmartPyme.
No es Hermes Factoría, no audita código, no ejecuta herramientas de repositorio y no toma decisiones soberanas.

Ruta objetivo:

```text
Telegram producto
→ HermesProductAdapter
→ Hermes Producto Runtime
→ herramientas readonly/controladas
→ kernel determinístico SmartPyme
→ findings/reportes/evidencia
→ respuesta grounded
```

Regla rectora:

```text
Hermes conversa/orquesta.
SmartPyme decide.
```

## Configuración real

Archivo canónico:

```text
config/hermes_product.yaml
```

Variable soportada:

```text
HERMES_PRODUCT_CONFIG_PATH=config/hermes_product.yaml
```

El adapter carga esta configuración al habilitar `ENABLE_LLM_ASSISTANT=true` y prepara un runtime scaffold fail-closed.

## Runtime profile

- `profile`: `hermes_product_runtime`
- `runtime.kind`: `product_conversational`
- `runtime.mode`: `fail_closed_scaffold`
- `model.default`: `gemma-4`
- `model.temperature`: `0.1`
- `runtime.timeout_seconds`: `8`
- `fallback.required`: `true`

## Grounding obligatorio

Hermes Producto solo puede responder a partir de:

- `summary`
- `findings`
- `operational_report`

No puede inventar:

- montos;
- entidades;
- archivos;
- causas;
- diagnósticos;
- resultados no producidos por SmartPyme.

Si falta evidencia suficiente, debe fallar cerrado o pedir evidencia mínima.

## Tools permitidas

Whitelist readonly:

- `owner_status_read`
- `findings_read`
- `operational_report_read`
- `curated_evidence_read`

Estas herramientas representan lectura de estado, hallazgos, reportes y evidencia ya curada. No escriben, no ejecutan, no modifican repositorio ni alteran evidencia.

## Tools prohibidas

Prohibidas explícitamente:

- `filesystem`
- `shell`
- `git`
- `factory_control`
- `business_task_executor`
- `code_execution`
- `network_write`
- `database_write`
- `destructive_actions`

## Boundaries confirmados por diseño

Hermes Producto no debe importar ni usar:

- `factory/*`
- `app.mcp.tools.factory_control_tool`
- `app.agents.business_task_executor`
- filesystem tools
- git tools
- shell tools

Nota: `TelegramAdapter` aún conserva comandos legacy de factoría para otros flujos. Ese legacy no pertenece al flujo conversacional de Hermes Producto y queda fuera de este ciclo.

## Bootstrap mínimo actual

`HermesProductAdapter` ahora:

1. Respeta `ENABLE_LLM_ASSISTANT`.
2. Si está deshabilitado, retorna `None`.
3. Si está habilitado y no se inyecta runtime, intenta cargar `HERMES_PRODUCT_CONFIG_PATH`.
4. Crea `HermesProductRuntimeScaffold` con la configuración real.
5. El scaffold no ejecuta LLM real todavía.
6. Ante falta de config, error de runtime, respuesta vacía o payload inválido, retorna `None` para activar fallback determinístico.

## Estado no implementado todavía

Todavía no existe:

- ejecución LLM real;
- tool execution real;
- enforcement externo de sandbox;
- memoria persistente compleja;
- graph runtime;
- agentes autónomos;
- auto-remediation.

Este perfil deja el contrato real preparado sin mezclar Producto con Factoría.
