# Lean Audit VM Protocol

## Nombre de skill

Lean Audit VM Protocol

## Cuando se activa

Esta skill se activa para tareas de implementación ejecutadas por Hermes/Gemini en VM o Cloud Shell bajo supervisión de GPT Auditor.

Aplica cuando Hermes/Gemini debe:

- crear o modificar código;
- crear o modificar tests;
- crear o modificar documentación operativa crítica;
- ejecutar validaciones mínimas acotadas;
- reportar evidencia para auditoría externa de GPT.

## Regla central

La VM es la estación de verdad.

Para código de producto o infraestructura viva del repo, GPT no debe escribir directo en GitHub. GPT redacta la Task Spec, Hermes/Gemini ejecuta en la VM y GPT audita solo el `SUMMARY_DIFF`, los tests ejecutados y los errores si existen.

Toda implementación debe seguir:

```text
WRITE -> VERIFY -> INSPECT -> TEST -> REPORT
```

No se puede declarar una tarea como `PASS` si falta evidencia física posterior a la escritura.

## Roles

- Hermes/Gemini: constructor. Escribe, verifica, inspecciona, testea y reporta.
- GPT: auditor. Revisa `SUMMARY_DIFF`, tests y errores. Emite `PASS`, `RECODE` o `BLOCKED`.
- Owner: aprueba avance, pega reportes y decide cuando continuar.

## Baseline obligatorio antes de escribir

Antes de cualquier cambio, Hermes/Gemini debe confirmar contexto real:

```bash
pwd
git remote -v
git branch --show-current
git rev-parse HEAD
git status --short
```

La tarea queda bloqueada si:

- la rama no coincide con la Task Spec;
- el repo no es el esperado;
- `git status --short` muestra cambios no explicados;
- la ruta objetivo está fuera del alcance autorizado.

## Verificación física obligatoria en Linux / Cloud Shell

Para cada archivo creado o modificado:

```bash
test -f ruta/archivo
stat ruta/archivo
sed -n '1,160p' ruta/archivo
```

Para verificar un símbolo concreto:

```bash
grep -R "SIMBOLO" ruta/archivo
```

Si el archivo es largo, se permite inspeccionar rangos relevantes:

```bash
sed -n '1,120p' ruta/archivo
sed -n '120,240p' ruta/archivo
```

## Test mínimo obligatorio

Ejecutar solo tests acotados al cambio:

```bash
PYTHONPATH=. pytest <tests_acotados> -q
```

No ejecutar suite completa salvo pedido explícito del Owner o del Auditor.

## Formato de reporte obligatorio

Toda salida de Hermes/Gemini debe usar este formato:

```text
VEREDICTO: PASS | FAIL | BLOCKED

BRANCH:
- <branch actual>

HEAD:
- <sha actual>

SUMMARY_DIFF:
- <resumen claro por archivo>

ARCHIVOS_MODIFICADOS:
- <ruta>

VERIFICACION_FISICA:
- test -f: <resultado>
- stat: <Full path, Size, Modify>
- inspect: <sed/grep usado y símbolo confirmado>

TESTS:
- comando:
- resultado:

LIMITES:
- rutas no tocadas
- decisiones explícitamente fuera de alcance

NEXT_RECOMMENDED_STEP:
- <siguiente acción o null>
```

## Reglas de bloqueo

Hermes/Gemini debe detenerse y reportar `BLOCKED` si ocurre cualquiera de estas condiciones:

- branch incorrecta;
- repo incorrecto;
- working tree sucio antes de empezar;
- ruta fuera de alcance;
- test acotado falla;
- falta evidencia física;
- la Task Spec exige tocar archivos no autorizados;
- hay ambigüedad sobre contrato, ruta o capa arquitectónica;
- se detecta necesidad de refactor global no autorizado.

## Regla de economía de tokens

No pegar archivos completos a GPT salvo pedido explícito.

El reporte para GPT debe incluir solo:

- `SUMMARY_DIFF`;
- rutas modificadas;
- tests ejecutados;
- errores completos si existen;
- dudas o bloqueos concretos.

GPT no necesita releer el repo completo para auditar un ciclo acotado.

## Prohibiciones

- No escribir directo en GitHub desde GPT para código de producto.
- No mezclar frentes activos.
- No tocar Polars, DuckDB, conectores, Telegram o factory si la Task Spec es de kernel identity.
- No agregar defaults silenciosos para campos de identidad salvo que la Task Spec lo autorice.
- No declarar `PASS` sin test mínimo y verificación física.

## Resultado válido

Un ciclo Lean Audit se considera cerrado solo cuando:

1. el archivo fue escrito en la VM;
2. la existencia física fue verificada;
3. el contenido o símbolo relevante fue inspeccionado;
4. el test mínimo pasó;
5. el reporte respeta el formato obligatorio;
6. GPT Auditor emite `PASS` o el Owner acepta el cierre.
