from __future__ import annotations

from typing import Any

FACTORY_COMMANDS: list[dict[str, str]] = [
    {
        "command": "/factory_health",
        "purpose": (
            "Resumen compacto de salud: cola, último reporte, bloqueos, "
            "path_errors y changed_paths."
        ),
        "phase": "diagnóstico",
    },
    {
        "command": "/status_factory",
        "purpose": "Estado de cola y próxima tarea pendiente.",
        "phase": "diagnóstico",
    },
    {"command": "/tasks_pending", "purpose": "Lista tareas pendientes.", "phase": "diagnóstico"},
    {"command": "/blocked", "purpose": "Lista tareas bloqueadas.", "phase": "diagnóstico"},
    {"command": "/run_one", "purpose": "Ejecuta una TaskSpec pendiente.", "phase": "ejecución"},
    {
        "command": "/run_batch <n>",
        "purpose": "Ejecuta hasta n TaskSpecs pendientes.",
        "phase": "ejecución",
    },
    {
        "command": "/retry_blocked <task_id>",
        "purpose": "Devuelve una tarea bloqueada a pending.",
        "phase": "recuperación",
    },
    {
        "command": "/task <task_id>",
        "purpose": "Inspecciona una tarea específica.",
        "phase": "inspección",
    },
    {
        "command": "/evidence <task_id>",
        "purpose": "Lee evidencia registrada para una tarea.",
        "phase": "inspección",
    },
    {
        "command": "/diff <task_id>",
        "purpose": "Muestra changed_paths asociados a una tarea.",
        "phase": "inspección",
    },
    {
        "command": "/last_report",
        "purpose": "Devuelve el último run report con markdown truncado.",
        "phase": "reportes",
    },
    {
        "command": "/run_report_summary",
        "purpose": "Resumen compacto del último run report.",
        "phase": "reportes",
    },
    {
        "command": "/failed_paths",
        "purpose": "Lista path_errors del último reporte agrupados por tarea.",
        "phase": "reportes",
    },
    {
        "command": "/report <report_id>",
        "purpose": "Devuelve un reporte específico.",
        "phase": "reportes",
    },
    {"command": "/templates", "purpose": "Lista templates disponibles.", "phase": "encolado"},
    {
        "command": "/enqueue_template <template> <objetivo>",
        "purpose": "Encola una TaskSpec desde template.",
        "phase": "encolado",
    },
    {
        "command": "/enqueue_dev <objetivo>",
        "purpose": "Atajo para encolar una tarea de cambio de código.",
        "phase": "encolado",
    },
    {"command": "/factory_help", "purpose": "Muestra esta ayuda operativa.", "phase": "ayuda"},
]

RECOMMENDED_FLOW = [
    "/factory_health",
    "/failed_paths si hay path_errors",
    "/diff <task_id> si necesitás ver archivos tocados",
    "/run_one o /run_batch <n> para avanzar",
    "/factory_health para verificar cierre",
]


def build_factory_help_payload() -> dict[str, Any]:
    return {
        "commands_count": len(FACTORY_COMMANDS),
        "commands": [dict(command) for command in FACTORY_COMMANDS],
        "recommended_flow": list(RECOMMENDED_FLOW),
    }


def format_factory_help_message(payload: dict[str, Any]) -> str:
    commands = ", ".join(command["command"] for command in payload["commands"])
    flow = " -> ".join(payload["recommended_flow"])
    return (
        f"Factory help: {payload['commands_count']} comandos. "
        f"Flujo recomendado: {flow}. Comandos: {commands}."
    )
