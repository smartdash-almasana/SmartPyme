# Write-Verify Implementation Protocol

## Nombre de skill

Write-Verify Implementation Protocol

## Cuando se activa

Esta skill se activa ante cualquier creacion o modificacion de:

- codigo;
- tests;
- Terraform;
- documentacion critica;
- scripts;
- configuracion operativa del repo.

## Regla central

No se puede declarar una implementacion como CORRECTA si no existe evidencia fisica posterior a la escritura. La salida del agente, un diff mental, un plan, un log o una mencion documental no prueban persistencia real en disco.

## Checklist obligatorio

1. WRITE
   - Crear o modificar el archivo real dentro del repo correcto.

2. VERIFY
   - Verificar existencia fisica del archivo con `Test-Path`.
   - Verificar metadata fisica con `Get-Item`.

3. INSPECT
   - Mostrar contenido relevante con `Get-Content -TotalCount N`.
   - O verificar el simbolo creado con `Select-String`.

4. TEST
   - Ejecutar test minimo acotado.
   - No ejecutar suite completa salvo pedido explicito.

5. REPORT
   - Reportar CORRECTO solo si WRITE, VERIFY, INSPECT y TEST pasan.
   - Si no se puede verificar, reportar FALLÓ o INCOMPLETO.

## Comandos PowerShell para verificar archivos

Para cada archivo creado o modificado:

```powershell
Test-Path E:\BuenosPasos\smartbridge\SmartPyme\ruta\archivo.py
Get-Item E:\BuenosPasos\smartbridge\SmartPyme\ruta\archivo.py | Select-Object FullName, Length, LastWriteTime
Get-Content E:\BuenosPasos\smartbridge\SmartPyme\ruta\archivo.py -TotalCount 80
```

Para verificar un simbolo concreto:

```powershell
Select-String -Path E:\BuenosPasos\smartbridge\SmartPyme\ruta\archivo.py -Pattern "NombreDelSimbolo"
```

Para confirmar contexto antes de escribir:

```powershell
Set-Location E:\BuenosPasos\smartbridge\SmartPyme
pwd
git status --short
```

## Plantilla de salida obligatoria

```text
VEREDICTO: CORRECTO | INCOMPLETO | FALLÓ

ARCHIVOS CREADOS / MODIFICADOS
- ruta

VERIFICACION FISICA
- Test-Path: True
- Get-Item: FullName, Length, LastWriteTime
- INSPECT: Get-Content o Select-String con simbolo esperado

TEST MINIMO
- comando:
- resultado:

LIMITES
- que no se toco
```

## Ejemplo de salida correcta

```text
VEREDICTO: CORRECTO

ARCHIVOS CREADOS / MODIFICADOS
- E:\BuenosPasos\smartbridge\SmartPyme\app\repositories\fact_repository.py

VERIFICACION FISICA
- Test-Path: True
- Get-Item: FullName=..., Length=2450, LastWriteTime=...
- Select-String "class FactRepository": encontrado

TEST MINIMO
- pytest tests/core/repositories/test_fact_repository.py -q
- 5 passed
```

## Ejemplo de salida invalida

```text
VEREDICTO: CORRECTO
Se creo FactRepository.
```

Motivo de invalidez:

- No muestra `Test-Path`.
- No muestra `Get-Item`.
- No inspecciona contenido ni simbolo.
- No ejecuta test minimo.
- Confunde afirmacion del agente con archivo persistido.

## Regla de bloqueo

Si no hay verificacion fisica, no avanzar al siguiente paso. El agente debe detenerse y declarar el trabajo como FALLÓ o INCOMPLETO hasta obtener evidencia real del filesystem.
