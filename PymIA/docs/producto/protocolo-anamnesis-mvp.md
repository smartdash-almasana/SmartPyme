<!--
FUENTE_ORIGINAL: docs/hermes-producto/PROTOCOLO_ANAMNESIS_MVP.md
ESTADO: copiado_sin_modificaciones
-->

# Protocolo de Anamnesis MVP

## Estado

Documento de diseno para el Laboratorio Inicial PyME.

## Objetivo

La fase de anamnesis convierte el relato inicial del dueno de la PyME en sintomas estructurados, hipotesis iniciales y evidencia requerida.

SmartPyme no procesa documentos a ciegas. Primero escucha, clasifica y define que debe buscar el laboratorio documental.

## Principio

SmartPyme habla como sistema completo. La interfaz conversacional es solo el organo de comunicacion del sistema.

No se debe presentar como un bot separado ni como una entidad autonoma.

## Flujo

```text
Narrativa del dueno
-> sintomas declarados
-> SubjectiveNodes
-> HypothesisNodes v0
-> pedido de evidencia especifica
-> laboratorio documental
-> TruthTensionReport
-> Clarification Gate
-> DDI
-> Snapshot V1
```

## Microfases

### 1. Apertura narrativa

SmartPyme permite que el dueno describa el problema con su propio lenguaje.

Objetivo:

- capturar vocabulario dominante;
- detectar sintomas;
- registrar contradicciones;
- identificar prioridades;
- preservar contexto.

### 2. Clarificacion semiestructurada

SmartPyme reduce ambiguedad con preguntas concretas.

Debe precisar:

- intensidad;
- frecuencia;
- temporalidad;
- impacto operacional;
- causalidad percibida.

### 3. Localizacion de friccion

SmartPyme identifica donde la percepcion del dueno puede colisionar con la realidad documental o matematica.

## Metadata minima de un sintoma

Cada dolor declarado debe transformarse en un registro estructurado con:

- claim literal;
- intensidad;
- temporalidad;
- causalidad percibida;
- impacto operacional;
- area afectada;
- evidencia requerida;
- nivel de confianza inicial.

## Mapeo a hipotesis

Ejemplo:

```text
Entrada: Vendemos mucho pero no queda plata.
```

SmartPyme debe generar:

- SubjectiveNode: incertidumbre de rentabilidad;
- HypothesisNode v0: margen erosionado, fuga operativa o tension de caja;
- evidencia requerida: ventas, costos, lista de precios, caja o extractos.

## Estilo comunicacional

SmartPyme debe mantener autoridad tranquila.

Reglas:

- no usar tono de coaching;
- no validar emociones de forma teatral;
- no prometer diagnosticos sin evidencia;
- pedir precision cuando el lenguaje es vago;
- marcar contradicciones con sobriedad;
- declarar incertidumbre cuando exista.

Ejemplo correcto:

```text
He registrado este sintoma como posible tension de caja o margen. Para distinguirlo necesito ventas, costos y una muestra de movimientos de caja del periodo.
```

## Resultado de la anamnesis

La salida de esta fase no es una respuesta de chat.

La salida es un mapa inicial de incertidumbre:

- sintomas;
- hipotesis;
- preguntas pendientes;
- evidencia requerida;
- tensiones potenciales.

## Criterio de cierre

La fase de anamnesis queda cerrada cuando SmartPyme sabe que evidencia necesita pedir y que hipotesis debe intentar confirmar o refutar en el laboratorio documental.
