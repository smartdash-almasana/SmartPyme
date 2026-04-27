# HERMES + CODEX + GEMINI GOVERNANCE — SmartPyme Factory

## Estado
CANONICO v1

## Objetivo
Definir la gobernanza multiagente de SmartPyme Factory con Hermes como orquestador, Codex como Builder de codigo y Gemini como Architect/Auditor semantico-documental.

---

## 1. Principio rector

Hermes orquesta. Codex construye. Gemini razona, audita y estructura.

Ningun agente decide solo el cierre de un ciclo.

---

## 2. Roles

### Hermes — Orquestador
Responsabilidades:
- leer tasks, hallazgos pending, roadmap y TECH_SPEC_QUEUE
- elegir una unidad pequena por ciclo
- asignar rol a Codex o Gemini
- exigir evidencia
- bloquear si falta validacion
- consolidar resultado final

No debe:
- escribir logica core directamente
- declarar exito sin evidencia
- depender de memoria conversacional

---

### Codex — Builder tecnico
Responsabilidades:
- modificar codigo
- crear tests
- ejecutar validaciones locales
- producir diff verificable
- generar evidencia tecnica

Uso preferente:
- Python
- scripts
- tests
- schemas
- validadores
- runners

No debe:
- inventar arquitectura de negocio
- cambiar contratos canonicos sin task explicita
- cerrar ciclos sin tests cuando toca codigo

---

### Gemini — Architect / Auditor semantico
Responsabilidades:
- analizar coherencia arquitectonica
- revisar specs
- convertir ideas en documentos tecnicos
- auditar que outputs respeten SmartPyme Core
- detectar deriva conceptual
- proponer priorizacion

Uso preferente:
- documentacion tecnica
- QA semantico
- revision de contratos
- priorizacion de backlog
- analisis de riesgos

No debe:
- tocar codigo core sin builder
- validar su propia propuesta sin evidencia externa
- reemplazar tests deterministas

---

## 3. Flujo canonico por ciclo

```text
TECH_SPEC_QUEUE / TASK / HALLAZGO
        ↓
Hermes selecciona unidad
        ↓
Gemini estructura o audita si hay ambiguedad
        ↓
Codex implementa si hay cambio tecnico
        ↓
Tests + evidencia
        ↓
Gemini puede auditar coherencia final
        ↓
Hermes consolida decision
        ↓
Commit / push si corresponde
```

---

## 4. Matriz de decision

| Tipo de trabajo | Agente primario | Agente secundario |
|---|---|---|
| Codigo Python | Codex | Gemini audita contrato |
| Tests | Codex | Hermes verifica evidencia |
| Specs tecnicas | Gemini | Codex materializa archivo |
| Priorizacion | Gemini | Hermes aplica |
| Refactor | Gemini disena | Codex ejecuta |
| Hallazgos de negocio | Gemini audita semantica | Codex valida schema |
| Runners / systemd / scripts | Codex | Hermes valida ejecucion |

---

## 5. Regla de no deriva

Codex no define negocio.
Gemini no ejecuta codigo critico sin verificacion.
Hermes no inventa estado.

Todo cambio debe terminar en:
- evidencia
- diff
- tests o criterio equivalente
- decision: CORRECTO / BLOCKED / NO_VALIDADO

---

## 6. Integracion con TECH_SPEC_QUEUE

Hermes debe leer `docs/factory/TECH_SPEC_QUEUE.md` en cada ciclo.
Gemini debe convertir ideas nuevas en specs o tasks.
Codex solo implementa tasks ya delimitadas.

---

## 7. Integracion con hallazgos

Todo output de negocio debe respetar:

- `docs/specs/CORE_DATA_CONTRACT_AND_HALLAZGOS.md`
- entidad
- diferencia cuantificada
- comparacion de fuentes
- trazabilidad

---

## 8. Criterios de aceptacion de la gobernanza

- Hermes reconoce Codex y Gemini como agentes distintos.
- Existe ruta documental para specs emergentes.
- Existe task ejecutable para implementacion.
- Existe auditoria semantica separada de la escritura de codigo.
- Ningun ciclo se declara correcto sin evidencia.

---

## 9. Proxima task sugerida

Crear `factory/ai_governance/tasks/hermes_codex_gemini_loop_v1.yaml` para que la factoría implemente lectura de TECH_SPEC_QUEUE y enrutamiento Codex/Gemini por tipo de trabajo.
