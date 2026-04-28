# JAULA OPERATIVA — ORQUESTADOR SMARTPYME

## Regla principal

Este archivo manda sobre cualquier impulso del asistente.

El asistente NO puede:

- escribir en main sin orden literal del usuario;
- crear overlays nuevos sin pedido explícito;
- mezclar diagnóstico, implementación y despliegue;
- dar más de un paso por vez;
- ejecutar migraciones reales sin dry-run validado;
- activar systemd sin repo limpio, config validada y `/estado` funcionando;
- tocar core Python sin TaskSpec explícita;
- tocar secretos, `.env` o archivos locales sensibles;
- inventar estado;
- decir "casi seguro";
- seguir si hay conflicto Git;
- cambiar de estrategia sin declarar `BLOQUEADO`.

## Flujo obligatorio

1. Leer este archivo.
2. Leer `.orquestador/ESTADO_ACTUAL.md`.
3. Dar una sola acción remota o un solo comando.
4. Esperar salida del usuario si la acción requiere ejecución local.
5. No avanzar a otro frente.
6. No reabrir arquitectura salvo orden explícita.

## Estados permitidos

- `BLOQUEADO`
- `DIAGNOSTICO`
- `CONFIGURACION`
- `VALIDACION`
- `DRY_RUN`
- `ACTIVACION_CONTROLADA`
- `OPERATIVO`

## Gate obligatorio antes de cualquier cambio remoto

Antes de cualquier cambio remoto el asistente debe declarar:

- archivo exacto;
- rama exacta;
- si toca `main` o no;
- motivo operativo;
- criterio de reversión.

## Orden literal requerida para tocar main

Solo se puede tocar `main` si el usuario emite una autorización explícita en el chat actual.

Ejemplos válidos:

- `AUTORIZO TOCAR MAIN`
- `Ponelo en GitHub y yo hago pull`
- `Subilo a main`

Sin autorización explícita, solo se puede trabajar en branch separada o limitarse a comandos locales.

## Objetivo actual

Dejar Hermes Gateway operativo con Telegram y control de factoría, sin rediseñar SmartPyme.

## Prohibido

- No reabrir arquitectura.
- No generar documentación lateral.
- No migrar TaskSpecs reales hasta orden humana explícita.
- No activar servicios hasta orden humana explícita.
- No hacer commit automático desde VM.
- No tocar `factory/config/telegram.local.env`.
- No tocar secretos.

## Procedimiento de continuidad entre chats

Al iniciar cualquier chat nuevo sobre SmartPyme Factory, el asistente debe asumir:

1. Leer `.orquestador/JAULA_OPERATIVA.md`.
2. Leer `.orquestador/ESTADO_ACTUAL.md`.
3. Responder solo sobre el próximo paso permitido.
4. No inferir estado no registrado.
5. Si falta evidencia, declarar `BLOQUEADO`.

## Criterio de éxito inmediato

Hermes se considera operativo solo cuando exista evidencia de:

- repo alineado;
- config de Hermes validada;
- token Telegram presente fuera del repo;
- allowlist real configurada;
- comando `/estado` funcionando;
- primer ciclo `dry_run` completado;
- primera TaskSpec P3 ejecutada con evidencia.
