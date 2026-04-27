# TELEGRAM DAILY REPORT DELIVERY

Estado: CANONICO v1

Objetivo: enviar el cierre diario de SmartPyme Factory por Telegram en formato Markdown o texto plano.

Base tecnica: Hermes ya incluye adaptador Telegram. SmartPyme no debe reinventar mensajeria si puede delegar el envio a Hermes.

Flujo:
1. generar daily report local
2. leer daily_summary.md
3. convertir a texto compatible con Telegram
4. enviar al chat_id configurado
5. registrar delivery_status.md

Variables requeridas:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

Formato recomendado:
- mensaje corto de resumen en Markdown
- si el reporte excede limite, enviar TXT/MD como archivo o dividir en bloques

Fallback:
- si falta token o chat_id, registrar DELIVERY_BLOCKED_TELEGRAM_CONFIG
- no bloquear el loop productivo por fallo de envio

Output obligatorio:
- factory/daily_reports/YYYY-MM-DD/delivery_status.md

Criterios de aceptacion:
- se detecta daily_summary.md
- se envia mensaje o archivo por Telegram
- se registra estado SENT o BLOCKED
- no se exponen secretos en logs
