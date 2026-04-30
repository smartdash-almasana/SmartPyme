# SmartPyme Baseline Report — TS_013 Telegram Interface

## Veredicto

**TS_013_TELEGRAM_BASELINE_READY**

La rama `factory/ts-006-jobs-sovereign-persistence` consolida la primera baseline funcional de interfaz Telegram/Hermes para SmartPyme.

El objetivo de TS_013 fue abrir un puente social controlado hacia el Kernel sin introducir dependencia directa de `python-telegram-bot`, manteniendo el adaptador puro, testeable y soberano por `cliente_id`.

---

## Estado validado

### TS_013A — Identity Service

Estado: **CERRADO**

Componente:

- `app/services/identity_service.py`

Responsabilidad:

- crear tokens de onboarding
- vincular `telegram_user_id` con `cliente_id`
- impedir reutilización de token usado
- consultar autorización de usuario Telegram

Garantías:

- usuario sin vínculo no accede al estado de SmartPyme
- token inválido no autoriza
- token usado no se reutiliza
- usuario existente puede revincularse con nuevo token
- identidad soberana: `cliente_id`, nunca `tenant_id`

---

### TS_013B — Telegram Command Adapter

Estado: **CERRADO**

Componente:

- `app/adapters/telegram_adapter.py`

Responsabilidad:

- recibir `update_dict` estilo Telegram
- procesar `/vincular <token>`
- procesar `/status`
- bloquear usuarios no vinculados
- devolver respuestas determinísticas testeables

Garantías:

- no depende de librerías externas de Telegram
- update sin `telegram_user_id` devuelve `security_error`
- `/status` usa `get_owner_status(cliente_id)`
- ningún comando distinto de `/vincular` se procesa sin vínculo previo

---

### TS_013C — Telegram Document Intake Adapter

Estado: **CERRADO**

Componente extendido:

- `app/adapters/telegram_adapter.py`

Responsabilidad:

- detectar documentos enviados por Telegram
- validar extensión permitida
- encolar tarea en factoría mediante `enqueue_factory_task`

Formatos aceptados:

- `.pdf`
- `.xlsx`
- `.csv`

Garantías:

- usuario no vinculado no puede enviar documentos a la factoría
- formatos no soportados son rechazados
- documento aceptado genera tarea con `cliente_id`
- no descarga archivos todavía
- no interpreta documentos todavía
- solo realiza validación ligera y encolado

---

## Smoke validado

Comando ejecutado:

```bash
PYTHONPATH=. pytest \
  tests/test_identity_service_ts_013a.py \
  tests/test_telegram_adapter_ts_013b.py \
  tests/test_telegram_document_intake_ts_013c.py
```

Resultado:

```text
12 passed
```

---

## Reglas arquitectónicas preservadas

- `cliente_id` siempre obligatorio para acceso a datos de negocio
- no usar `tenant_id`
- zero trust por defecto
- `/vincular <token>` es el único mecanismo de onboarding Telegram
- Telegram no es fuente de verdad contable
- la verdad de negocio sigue en SmartPyme DB
- la memoria conversacional no reemplaza evidencia documental
- el adaptador Telegram es puro y testeable sin servidores externos

---

## Alcance deliberadamente excluido

No se implementó en TS_013:

- descarga real de archivos desde Telegram Bot API
- webhook HTTP público
- envío real de mensajes por `sendMessage`
- inline keyboards
- retry de jobs bloqueados
- storage persistente de archivos
- parsing real de documentos

Estas piezas quedan para una fase posterior sobre una baseline ya segura.

---

## Próxima fase recomendada

### TS_014 — Telegram Runtime Adapter

Objetivo:

Conectar el adaptador puro con infraestructura real de Telegram sin romper el contrato testeado.

Alcance sugerido:

1. endpoint webhook HTTP
2. validación de secret/token de webhook
3. descarga de archivos permitidos
4. storage temporal o persistente
5. encolado de tarea con referencia real de archivo
6. respuesta real vía Telegram Bot API

Criterio de cierre:

Un documento enviado por un usuario vinculado debe llegar a la cola de factoría con evidencia trazable y respuesta confirmada en Telegram.

---

## Estado final

**TS_013 FINALIZADA**

La interfaz Telegram queda congelada como baseline lógica. La próxima acción recomendada es congelar la rama o preparar PR/merge controlado.
