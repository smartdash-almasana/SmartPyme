# DeepSeek Audit Bridge

Objetivo: usar DeepSeek local para lectura larga y auditoria, sin pasarlo por Telegram.

Ruteo:
- Gemini Vertex: chat rapido y builder de codigo.
- DeepSeek local: auditor, lector largo y revisor de diffs.
- Gemma local: fallback conversacional o runtime local si se decide explicitamente.

Salida obligatoria por tarea:
- factory/evidence/deepseek_audit/<task_id>/audit_report.md
- factory/evidence/deepseek_audit/<task_id>/verdict.txt
- factory/evidence/deepseek_audit/<task_id>/files_reviewed.txt

verdict.txt acepta solo:
- PASS
- PARTIAL
- BLOCKED

Reglas:
- DeepSeek no edita codigo critico.
- DeepSeek no reemplaza a Gemini como builder.
- DeepSeek escribe evidencia auditable en archivos.
- GPT o Hermes leen esos archivos y definen el proximo paso.

Flujo:
TaskSpec -> DeepSeek audita -> escribe evidencia -> GPT/Hermes lee -> Owner decide.
