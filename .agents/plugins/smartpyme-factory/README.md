# smartpyme-factory (plugin local)

Plugin local para Codex orientado al flujo SmartPyme Factory.

## Qué incluye
- Skill `factory_audit_execute`: orquesta auditoría y paso a ejecución.
- Skill `hallazgo_gatekeeper`: valida preparación del hallazgo con fail-closed.

## MCP bridge local
El plugin referencia `.mcp.json`, que registra el servidor MCP local:
- comando: `python`
- entrypoint: `E:\BuenosPasos\smartbridge\SmartPyme\factory\mcp_bridge\server.py`
- cwd: `E:\BuenosPasos\smartbridge\SmartPyme`

## Activación desde Codex
1. Mantener este plugin bajo `.agents/plugins/smartpyme-factory`.
2. Verificar que `.agents/plugins/marketplace.json` incluya `smartpyme-factory`.
3. Recargar la sesión de Codex en este repo y activar el plugin local `smartpyme-factory` desde el marketplace local.

## Límites de seguridad
- Solo SmartPyme local.
- Fail-closed en validación de hallazgos.
- No ejecutar si hay dudas abiertas o rutas fuera de política.

## Nota de ajuste fino
Si la versión local de Codex requiere un esquema distinto para `plugin.json` o `.mcp.json`, ajustar solo claves de envoltura manteniendo el mismo contenido funcional (skills + servidor MCP local).
