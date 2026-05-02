# AI Provider Routing Contract — SmartPyme Factory

**Estado:** CANONICO v1

## Regla Rectora
- **Gemma** lee.
- **Gemini** coordina.
- **Codex** construye.
- **GPT** audita.
- **Owner** decide.

## Tabla de Enrutamiento

| Escenario | Provider | Modelo |
| :--- | :--- | :--- |
| READ_ONLY / documentación | ollama-local | gemma4:e2b |
| ciclo normal Hermes | custom:vertex-gemini | google/gemini-3.1-flash-lite-preview |
| patch crítico | Codex | gpt-5.3-codex |
| auditoría final | GPT | (GPT Director-Auditor) |

## Reglas Operativas
1. **Eficiencia**: No usar Gemini para lectura larga si Gemma alcanza.
2. **Seguridad**: No usar Gemma para patch crítico.
3. **Defaults**: 
   - Prohibido dejar Codex o Gemma como default global en `config.yaml`.
   - `custom:vertex-gemini` es el default operativo.
   - `ollama-local` es fallback y worker barato.
4. **Soberanía**: El Owner tiene la decisión final sobre productos y ejecución.
