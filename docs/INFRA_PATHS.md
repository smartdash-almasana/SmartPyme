# INFRA_PATHS.md — Fuente Única de Verdad de Infraestructura SmartPyme

Este archivo es la referencia obligatoria para todas las operaciones agénticas sobre rutas, infraestructura y configuración en el entorno de SmartPyme.

Este archivo debe leerse antes de cualquier TaskSpec que toque Hermes, MCP, providers, configs, rutas, VM, Cloud Shell o ejecución remota.

## 1. RUTAS REALES VM — HERMES RUNTIME

- **Configuración Principal**: `/home/neoalmasana/.hermes/config.yaml`
- **Variables de Entorno**: `/home/neoalmasana/.hermes/.env`
- **Proceso Hermes Gateway**: El gateway se gestiona vía el proceso identificado por `/home/neoalmasana/.hermes/gateway.pid`.

**Verificación Física**:
Para confirmar la existencia de estas rutas, usar:
```bash
ls -l /home/neoalmasana/.hermes/config.yaml
ls -l /home/neoalmasana/.hermes/.env
ps -p $(cat /home/neoalmasana/.hermes/gateway.pid)
```

## 2. RUTAS REPO FACTORÍA

- **Root del Repositorio**: `/opt/smartpyme-factory/repos/SmartPyme`
- **Directorio de Evidencia**: `/opt/smartpyme-factory/repos/SmartPyme/factory/evidence/`
- **Catálogos de Código**: `/opt/smartpyme-factory/repos/SmartPyme/app/catalogs/`

## 3. DIFERENCIAS CLAVE

- **Entorno**: Cloud Shell no es el mismo entorno que la VM runtime (`/opt/smartpyme-factory/...`).
- **Configuración**: El `config.yaml` activo es el de `/home/neoalmasana/.hermes/`. Los archivos con extensión `.bak` u otras nomenclaturas son respaldos y no deben considerarse activos.
- **Validación**: La presencia de un archivo de configuración no garantiza su validez ni que sea el archivo en uso. Siempre verificar mediante `readlink` o inspección de procesos si hay duda sobre la resolución de paths.

## 4. REGLA OBLIGATORIA PARA AGENTES

Nunca asumir rutas.
Siempre verificar con pwd / ls / readlink antes de ejecutar.
Si existe duda sobre path activo, responder BLOCKED_PATH_UNCERTAINTY.

## 5. UBICACIÓN DE PROVIDERS

- Los proveedores externos se definen exclusivamente en `/home/neoalmasana/.hermes/config.yaml`.
- Las llaves de API (API keys) residen en `/home/neoalmasana/.hermes/.env`.
- **Prohibiciones**:
    - Prohibido commitear archivos de configuración que contengan secretos.
    - Prohibido escribir llaves de API (secrets) en documentación.
