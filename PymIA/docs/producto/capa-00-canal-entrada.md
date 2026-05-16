<!--
FUENTE_ORIGINAL: docs/product/SMARTPYME_CAPA_00_CANAL_ENTRADA_CRUDA.md
ESTADO: copiado_sin_modificaciones
-->

# SmartPyme — Capa 00: Canal y Entrada Cruda

## Estado

DOCUMENTO RECTOR — v1.0  
**Fecha:** Mayo 2026

---

## Regla rectora

```text
Capa 00 recibe entrada cruda.
Capa 00 no interpreta negocio.
Capa 00 no formula hipótesis.
Capa 00 no diagnostica.
Capa 00 registra y entrega.
```

---

## 1. Posición en la arquitectura

```text
Canal externo (Telegram, WhatsApp, web, API, archivo)
  ↓
Capa 00 → RawInboundEvent
  ↓
Capa 01 → InitialCaseAdmission / OwnerDemandCandidate
  ↓
Capa 1.5 → NormalizedEvidencePackage
  ↓
Capa 02 → OperationalCaseCandidate
  ↓
Capa 03 → OperationalCase
```

Capa 00 es la frontera entre el mundo externo y el sistema.

Nada entra al sistema sin pasar por Capa 00.  
Nada sale de Capa 00 sin ser registrado.

---

## 2. Qué hace Capa 00

Capa 00:

- recibe cualquier entrada desde cualquier canal;
- registra el evento de entrada con metadata mínima;
- identifica el canal de origen;
- identifica la fuente (usuario, cliente, sistema externo);
- registra el contenido crudo sin modificarlo;
- asigna un `event_id` único;
- registra el `timestamp` de recepción;
- vincula el evento con un `conversation_id` si existe;
- vincula el evento con un `user_id` o `cliente_id` si está disponible;
- produce un `RawInboundEvent`;
- entrega el evento a Capa 01 para interpretación.

---

## 3. Qué NO hace Capa 00

Capa 00 no:

- interpreta el contenido del mensaje;
- clasifica la intención del dueño;
- detecta síntomas operativos;
- detecta fases clínicas;
- formula hipótesis;
- diagnostica;
- cura datos;
- normaliza entidades;
- resuelve aliases;
- asigna ventanas temporales;
- genera tareas de evidencia;
- toma decisiones;
- autoriza acciones;
- produce `InitialCaseAdmission`;
- produce `OperationalCaseCandidate`;
- produce `OperationalCase`.

---

## 4. Canales soportados

Capa 00 puede recibir entrada desde cualquier canal:

| Canal | Tipo de entrada |
|---|---|
| Telegram | Mensaje de texto, archivo, audio, imagen, documento |
| WhatsApp | Mensaje de texto, archivo, audio, imagen |
| Web / API | JSON, formulario, archivo |
| Email | Texto, adjunto |
| CLI / herramienta interna | Comando, archivo |
| Sistema externo | Webhook, evento, exportación |

El canal no cambia el contrato de Capa 00.  
Siempre produce un `RawInboundEvent`.

---

## 5. Contrato: RawInboundEvent

```text
RawInboundEvent:
  event_id              UUID único del evento
  channel               telegram | whatsapp | web | api | email | cli | otro
  source_type           human | system | file | webhook
  received_at           timestamp ISO UTC de recepción
  conversation_id       ID de conversación si existe (opcional)
  user_id               ID del usuario en el canal (opcional)
  cliente_id            ID del cliente/tenant si está disponible (opcional)
  raw_content_type      text | file | audio | image | document | json | otro
  raw_text              texto crudo del mensaje (si aplica)
  raw_file_ref          referencia al archivo recibido (si aplica)
  raw_file_name         nombre original del archivo (si aplica)
  raw_file_type         extensión o MIME type (si aplica)
  raw_file_size_bytes   tamaño del archivo (si aplica)
  raw_audio_ref         referencia al audio (si aplica)
  raw_image_ref         referencia a la imagen (si aplica)
  metadata              dict con metadata adicional del canal
  processing_status     PENDING | DELIVERED | FAILED
```

---

## 6. Tipos de entrada cruda

### Texto libre

El dueño escribe un mensaje.

```text
"No sé cuánto stock tengo. Paulita tiene un Excel."
```

Capa 00 registra el texto tal como llegó.  
No interpreta.  
No clasifica.

### Archivo

El dueño sube un Excel, PDF, imagen o documento.

```text
stock_mayo_paulita.xlsx
factura_proveedor_003.pdf
foto_estanteria.jpg
```

Capa 00 registra el archivo con su nombre, tipo y referencia de almacenamiento.  
No procesa el contenido.  
No normaliza columnas.

### Audio

El dueño envía un mensaje de voz.

Capa 00 registra la referencia al audio.  
No transcribe.  
No interpreta.

### Imagen

El dueño envía una foto (estantería, cuaderno, pantalla).

Capa 00 registra la referencia a la imagen.  
No extrae texto.  
No interpreta.

---

## 7. Flujo de Capa 00

```text
Entrada externa llega al canal
→ Capa 00 recibe el evento
→ asigna event_id único
→ registra timestamp
→ registra canal y fuente
→ registra contenido crudo sin modificar
→ vincula conversation_id si existe
→ vincula user_id / cliente_id si está disponible
→ produce RawInboundEvent con status PENDING
→ entrega a Capa 01
→ actualiza status a DELIVERED
```

Si la entrega a Capa 01 falla:

```text
→ status = FAILED
→ registra razón del fallo
→ reintenta o alerta según política del canal
```

---

## 8. Relación con Capa 01

Capa 00 entrega el `RawInboundEvent` a Capa 01.

Capa 01 es la que interpreta la intención del dueño.

Capa 00 no sabe qué significa el mensaje.  
Capa 01 sí.

La separación es intencional:

```text
Capa 00 = canal y registro
Capa 01 = interpretación e intención
```

---

## 9. Reglas rectoras

1. Capa 00 no interpreta negocio.
2. Capa 00 no formula hipótesis.
3. Capa 00 no diagnostica.
4. Capa 00 registra y entrega.
5. Todo evento de entrada produce exactamente un `RawInboundEvent`.
6. El contenido crudo no se modifica en Capa 00.
7. El `event_id` es único e inmutable.
8. El `timestamp` de recepción es el momento en que el canal recibió el evento.
9. Si no hay `cliente_id` disponible, el campo queda vacío. Capa 01 lo resuelve.
10. Capa 00 no bloquea la entrada por falta de `cliente_id`.
11. Archivos, audios e imágenes se registran por referencia, no por contenido.
12. La metadata del canal se preserva sin modificar.

---

## 10. Objetos de Capa 00

```text
RawInboundEvent   (único output)
```
