# Lean Audit VM Protocol

## Nombre de skill

Lean Audit VM Protocol

## Cuando se activa

Esta skill se activa para tareas de inspección, implementación o validación ejecutadas por Hermes/Gemini en VM o Cloud Shell bajo supervisión de GPT Auditor.

Aplica cuando Hermes/Gemini debe:

- analizar alcance antes de escribir;
- crear o modificar código;
- crear o modificar tests;
- crear o modificar documentación operativa crítica;
- ejecutar validaciones mínimas acotadas;
- reportar evidencia para auditoría externa de GPT.

## Regla central

La VM es la estación de verdad operativa.

Para código de producto o infraestructura viva del repo, GPT no debe escribir directo en GitHub salvo autorización explícita del Owner. GPT redacta la Task Spec, Hermes/Gemini ejecuta en la VM y GPT audita solo el `SUMMARY_DIFF`, los tests ejecutados y los errores si existen.

Toda implementación autorizada debe seguir:

```text
WRITE -> VERIFY -> INSPECT -> TEST -> REPORT
```

No se puede declarar una tarea como `PASS` si falta evidencia física posterior a la escritura o si algún test solicitado falla.

## Modos obligatorios de ejecución

### ANALYSIS_ONLY

Si el Owner, GPT Auditor o la Task Spec pide primero analizar, inspeccionar, reportar alcance, listar archivos, mostrar plan, no escribir todavía, solo revisar, analysis-only, auditoría previa o una instrucción equivalente:

- Hermes/Gemini tiene prohibido escribir, editar, borrar, mover, renombrar o crear archivos.
- Hermes/Gemini solo puede ejecutar comandos de inspección, lectura, búsqueda, baseline y estado.
- Hermes/Gemini debe reportar alcance exacto, archivos candidatos, instanciaciones, riesgos y tests candidatos.
- Hermes/Gemini debe terminar con `VEREDICTO: ANALYSIS_ONLY`.
- Cualquier escritura durante `ANALYSIS_ONLY` invalida el ciclo y debe reportarse como `FAIL` o `BLOCKED`, nunca como `PASS`.

### WRITE_AUTHORIZED

Hermes/Gemini solo puede escribir cuando la Task Spec contiene autorización explícita e inequívoca, por ejemplo:

- `autorizado a escribir`;
- `autorizado a implementar`;
- `aplicar cambio`;
- `modificar archivos`;
- `crear tests`;
- `implementar ahora`;
- otra frase equivalente que autorice escritura sin ambigüedad.

Si la Task Spec no contiene autorización explícita de escritura, Hermes/Gemini debe operar en `ANALYSIS_ONLY`.

La autorización de escritura no habilita cambios fuera de alcance. Solo se pueden tocar las rutas, clases, tests o documentos indicados por la Task Spec.

### STOP_AND_REPORT

Si el Owner o GPT Auditor interrumpe, corrige, dice `stop`, `pará`, `detener`, `no sigas`, `bloqueo`, `cortá`, `esperá`, `reporte`, `no escribas más` o una instrucción equivalente:

- Hermes/Gemini debe detener la ejecución inmediatamente.
- Hermes/Gemini no puede escribir más archivos.
- Hermes/Gemini debe reportar contexto y estado real:

```bash
pwd
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff --name-only
```

El reporte debe terminar con `VEREDICTO: STOP_AND_REPORT` salvo que la Task Spec exija otro formato compatible.

## Roles

- Hermes/Gemini: constructor controlado. Analiza, escribe solo con autorización explícita, verifica, inspecciona, testea y reporta.
- GPT: auditor/director técnico. Revisa `SUMMARY_DIFF`, tests y errores. Emite `PASS`, `RECODE`, `FAIL` o `BLOCKED`.
- Owner: aprueba avance, pega reportes, interrumpe cuando sea necesario y decide cuándo continuar.

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
- la ruta objetivo está fuera del alcance autorizado;
- no existe autorización explícita de escritura.

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
VEREDICTO: PASS | FAIL | BLOCKED | ANALYSIS_ONLY | STOP_AND_REPORT

PWD:
- <pwd real>

BRANCH:
- <branch actual>

HEAD:
- <sha actual>

SUMMARY_DIFF:
- <resumen claro por archivo>

ARCHIVOS_MODIFICADOS:
- <ruta o null>

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

En `ANALYSIS_ONLY`, `ARCHIVOS_MODIFICADOS` debe ser `null` y `SUMMARY_DIFF` debe indicar `sin cambios`.

## Reglas de bloqueo

Hermes/Gemini debe detenerse y reportar `BLOCKED` si ocurre cualquiera de estas condiciones:

- branch incorrecta;
- repo incorrecto;
- working tree sucio antes de empezar;
- ruta fuera de alcance;
- escritura solicitada sin `WRITE_AUTHORIZED` explícito;
- test acotado falla;
- falta evidencia física;
- la Task Spec exige tocar archivos no autorizados;
- hay ambigüedad sobre contrato, ruta o capa arquitectónica;
- se detecta necesidad de refactor global no autorizado;
- se detecta instrucción contradictoria entre análisis previo y escritura.

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

- No escribir directo en GitHub desde GPT para código de producto salvo autorización explícita del Owner.
- No mezclar frentes activos.
- No tocar Polars, DuckDB, conectores, Telegram o factory si la Task Spec es de kernel identity.
- No agregar defaults silenciosos para campos de identidad salvo que la Task Spec lo autorice.
- No declarar `PASS` sin test mínimo y verificación física.
- No escribir durante `ANALYSIS_ONLY`.
- No continuar después de una orden `STOP_AND_REPORT`.

## Resultado válido

Un ciclo Lean Audit se considera cerrado solo cuando:

1. el modo de ejecución fue respetado (`ANALYSIS_ONLY`, `WRITE_AUTHORIZED` o `STOP_AND_REPORT`);
2. si hubo escritura, el archivo fue escrito en la VM;
3. la existencia física fue verificada;
4. el contenido o símbolo relevante fue inspeccionado;
5. el test mínimo pasó cuando correspondía;
6. el reporte respeta el formato obligatorio;
7. GPT Auditor emite `PASS` o el Owner acepta el cierre.
