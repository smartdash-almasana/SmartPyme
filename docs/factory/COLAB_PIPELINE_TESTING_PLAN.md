# Plan de aprovechamiento de Google Colab para pruebas de Factoría y SmartPyme

## Estado

Documento operativo de laboratorio.

Este documento define cómo usar Google Colab como entorno gratuito, efímero y externo para probar pipelines de SmartPyme y de la factoría sin contaminar la PC local ni mezclar validaciones de producto con deuda histórica del repositorio.

Colab no es producción.
Colab no es fuente de verdad.
Colab es laboratorio de reproducibilidad.

---

## 1. Objetivo

Aprovechar sesiones gratuitas de Google Colab para validar y optimizar diariamente:

- instalación limpia del repo;
- colección de tests;
- tests focales de SmartPyme producto;
- tests de factoría;
- runners offline;
- contratos;
- evidencia;
- tiempos de ejecución;
- reproducibilidad fuera del entorno local;
- fallos por paths locales, permisos o archivos temporales colados.

El objetivo no es desarrollar dentro de Colab como IDE principal, sino responder una pregunta concreta:

```text
¿El repo corre limpio y reproducible en un entorno externo efímero?
```

---

## 2. Principio operativo

El flujo base será:

```text
GitHub repo
→ clone limpio en Colab
→ instalación reproducible
→ colección de tests
→ tests focales
→ tests de pipeline
→ captura de evidencia
→ reporte diario
→ decisión humana
```

Regla central:

```text
Si algo solo funciona en la PC local, todavía no está suficientemente estabilizado.
```

---

## 3. Responsabilidad de Colab dentro del sistema

| Capa | Rol |
|---|---|
| Local / Codex | Construcción rápida de código y microcortes. |
| Hermes | Coordinación HITL, control desde teléfono, despacho de tareas. |
| GitHub | Fuente de verdad del código. |
| Colab | Laboratorio externo de reproducibilidad y pruebas limpias. |
| Factoría | Industrialización gobernada cuando el patrón ya es estable. |

---

## 4. Qué sí probar en Colab

### 4.1 Instalación limpia

Validar que el repo puede arrancar desde cero:

```bash
git clone https://github.com/smartdash-almasana/SmartPyme.git
cd SmartPyme
git checkout product/laboratorio-mvp-vendible
python --version
pip install -r requirements.txt
```

Objetivo:

- detectar dependencias faltantes;
- detectar imports rotos;
- detectar acoplamientos al entorno local;
- detectar paths absolutos;
- detectar archivos temporales colados;
- detectar errores por permisos.

---

### 4.2 Colección de tests

Antes de correr todo:

```bash
pytest --collect-only -q
```

Objetivo:

- detectar errores de import;
- detectar tests duplicados;
- detectar conflictos de nombres;
- detectar carpetas temporales mal ubicadas;
- detectar módulos legacy rotos;
- detectar archivos que no deberían estar bajo `tests/`.

Regla:

```text
Si collect-only falla, no se interpreta pytest global como señal de producto.
Primero se sanea colección o se aíslan tests focales.
```

---

### 4.3 Tests focales de SmartPyme producto

Prioridad actual:

```bash
pytest tests/contracts/test_operational_claims.py -q
pytest tests/services/test_operational_interview_engine.py -q
```

Objetivo:

- validar `OperationalClaim`;
- validar `ClaimCatalogEntry`;
- validar `MockClaimExtractor`;
- validar `OperationalInterviewEngine`;
- validar flujo offline mensaje operativo → claim;
- mantener el lifecycle inicial sin evidencia real todavía.

Restricciones:

```text
sin LLM
sin SmartGraph automático
sin EvidenceStore real
sin factory
sin UI
```

---

### 4.4 Tests de factory_v2

Cuando el entorno esté instalado:

```bash
pytest tests/factory_v2 -q
```

Objetivo:

- validar contratos de factoría;
- validar evidence records;
- validar sandbox fake;
- validar policies;
- validar runners;
- validar integración mínima de LangGraph si la dependencia está disponible.

Regla:

```text
Factory_v2 se valida separado de producto SmartPyme.
No mezclar fallos de factory con claims operacionales.
```

---

### 4.5 Tests globales controlados

Solo después de colección limpia:

```bash
pytest tests -q
```

Objetivo:

- medir salud general del repo;
- detectar regresiones reales;
- separar fallos nuevos de deuda histórica.

Si falla por colección preexistente, clasificar como:

```text
PARTIAL
```

No como FAIL del microciclo de producto.

---

## 5. Qué no usar en Colab todavía

No usar Colab para:

- producción;
- credenciales sensibles permanentes;
- Supabase real;
- EvidenceStore real;
- SmartGraph automático sobre datos reales;
- LLM con claves pegadas en notebook;
- workflows autónomos largos;
- merges;
- pushes automáticos sin revisión;
- ejecución de factory con permisos amplios.

Regla:

```text
Colab puede validar, medir y reportar.
No debe convertirse en operador autónomo del repo.
```

---

## 6. Uso recomendado de una sesión diaria

### Bloque A — Sanidad inicial

Duración estimada: 30 a 60 minutos.

```bash
git status
python --version
pip freeze
pytest --collect-only -q
```

Salida esperada:

- colección limpia; o
- lista explícita de errores de colección.

---

### Bloque B — Producto SmartPyme

Duración estimada: 1 a 2 horas.

```bash
pytest tests/contracts/test_operational_claims.py -q
pytest tests/services/test_operational_interview_engine.py -q
```

Objetivo:

- validar flujo claims operacionales;
- cerrar integración offline mínima;
- evitar ruido de factory legacy.

---

### Bloque C — Factoría

Duración estimada: 2 a 3 horas.

```bash
pytest tests/factory_v2 -q
```

Objetivo:

- comprobar que la línea industrial sigue estable;
- medir reproducibilidad fuera de la PC local;
- detectar dependencia faltante o entorno insuficiente.

---

### Bloque D — Benchmark básico

Duración estimada: 1 hora.

Medir tiempos:

```bash
time pytest tests/contracts/test_operational_claims.py -q
time pytest tests/services/test_operational_interview_engine.py -q
time pytest tests/factory_v2 -q
```

Registrar:

- duración de instalación;
- duración de colección;
- duración de tests focales;
- duración de tests de factoría;
- consumo aproximado de RAM si aplica;
- errores recurrentes.

---

### Bloque E — Evidencia diaria

Duración estimada: 15 minutos.

Crear reporte en:

```text
docs/evidence/colab/YYYY-MM-DD-colab-pipeline-report.md
```

Plantilla:

```text
fecha:
commit:
rama:
python:
entorno:
tests ejecutados:
resultado:
fallos:
causa probable:
clasificación: PASS | PARTIAL | FAIL | BLOCKED
próximo microciclo:
```

---

## 7. Métricas mínimas

Cada corrida Colab debe dejar como mínimo:

```yaml
commit_hash:
branch:
python_version:
pip_freeze_hash:
tests_run:
passed:
failed:
collection_errors:
duration_seconds:
classification:
notes:
```

---

## 8. Política de clasificación

### PASS

```text
Los tests focales pasan y no hay errores atribuibles al cambio.
```

### PARTIAL

```text
El flujo nuevo pasa, pero pytest global falla por deuda preexistente o colección externa al cambio.
```

### FAIL

```text
El flujo nuevo falla directamente.
```

### BLOCKED

```text
No se pudo instalar, clonar, autenticar, ejecutar o completar por límite del entorno.
```

---

## 9. Aplicación al estado actual

Estado informado:

```text
pytest tests/contracts/test_operational_claims.py -q -> PASS
pytest tests -q -> FAIL por errores de colección preexistentes
```

Errores reportados:

```text
tests/factory/test_agent_min.py import error: factory.agent_min
tests/factory/test_agent_min_runtime.py module not found: factory.agent_min.agent
import file mismatch en test_orchestrator.py
import file mismatch en test_skill_registry.py
tests/tmp/pytest_create_job permission denied
```

Lectura correcta:

```text
No hay evidencia suficiente para declarar fallido el flujo nuevo.
El estado correcto es PARTIAL hasta ejecutar el test focal de services.
```

Próximo comando focal:

```bash
pytest tests/services/test_operational_interview_engine.py -q
```

Si pasa:

```text
Cerrar integración mínima offline como PASS focal.
```

Luego abrir microciclo separado:

```text
saneamiento de colección pytest global
```

---

## 10. Separación obligatoria de señales

No mezclar:

```text
claims operacionales
≠ factory legacy
≠ tests temporales
≠ permisos locales
≠ integración LLM
≠ SmartGraph
```

Cada frente debe tener sus propios tests focales y su propia evidencia.

---

## 11. Notebook mínimo recomendado

Un notebook Colab operativo debería tener celdas para:

1. clonar repo;
2. checkout de rama;
3. instalar dependencias;
4. imprimir versión Python;
5. correr `pytest --collect-only -q`;
6. correr tests focales de producto;
7. correr tests de factory_v2;
8. guardar reporte Markdown;
9. mostrar resumen final.

No debe guardar claves en texto plano.
No debe hacer push automático.

---

## 12. Regla final

```text
Local/Codex construye.
Hermes coordina.
Colab valida en limpio.
GitHub conserva verdad.
Factoría industrializa cuando el patrón ya está claro.
```

El valor de Colab no es reemplazar a la factoría.
El valor de Colab es probar si la factoría y SmartPyme sobreviven fuera del entorno cómodo local.
