"""Política determinística mínima para validar code/test_code en factory_v2."""

from __future__ import annotations

import re


class CodePolicyV2:
    """Evalúa contenido Python antes de construir el wrapper de Docker.

    Esta política es intencionalmente conservadora. No reemplaza un sandbox real,
    pero agrega una barrera previa contra IO, red, procesos y ejecución dinámica.
    """

    BLOCKED_PATTERNS: tuple[tuple[str, str], ...] = (
        (r"\bimport\s+os\b", "IMPORT_OS_BLOCKED"),
        (r"\bfrom\s+os\s+import\b", "IMPORT_OS_BLOCKED"),
        (r"\bimport\s+subprocess\b", "SUBPROCESS_BLOCKED"),
        (r"\bfrom\s+subprocess\s+import\b", "SUBPROCESS_BLOCKED"),
        (r"\bsocket\b", "SOCKET_BLOCKED"),
        (r"\brequests\b", "REQUESTS_BLOCKED"),
        (r"\burllib\b", "URLLIB_BLOCKED"),
        (r"\bopen\s*\(", "OPEN_BLOCKED"),
        (r"\bpathlib\.Path\s*\(", "PATHLIB_PATH_BLOCKED"),
        (r"\bshutil\b", "SHUTIL_BLOCKED"),
        (r"\beval\s*\(", "EVAL_BLOCKED"),
        (r"\bexec\s*\(", "EXEC_BLOCKED"),
        (r"__import__\s*\(", "DYNAMIC_IMPORT_BLOCKED"),
    )

    def evaluate(self, code: str, test_code: str) -> tuple[bool, list[str]]:
        """Evalúa code y test_code.

        Retorna:
            (True, []) si el contenido está permitido.
            (False, reasons) si se detectan patrones bloqueados.

        Regla fail-closed mínima:
            `code` vacío o solo whitespace queda bloqueado.
        """
        if not code or not code.strip():
            return False, ["CODE_EMPTY_BLOCKED"]

        combined = f"{code}\n{test_code or ''}"
        reasons: list[str] = []

        for pattern, reason in self.BLOCKED_PATTERNS:
            if re.search(pattern, combined):
                reasons.append(reason)

        if reasons:
            return False, reasons

        return True, []
