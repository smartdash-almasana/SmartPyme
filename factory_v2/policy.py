"""Política de seguridad de comandos determinística para factory_v2."""
from typing import Tuple

class CommandPolicyV2:
    """
    Evalúa comandos contra una política de seguridad determinística.
    La política se basa en una allowlist y una blocklist de prefijos de comandos.
    """

    # Comandos considerados seguros para ejecución en el sandbox.
    ALLOWLIST = {"ls", "cat", "echo", "pytest", "python", "pip", "mkdir", "touch", "head", "tail"}

    # Comandos considerados peligrosos o con efectos secundarios no deseados.
    BLOCKLIST = {
        # Modificación destructiva del sistema de archivos
        "rm", "mv", "cp",
        # Control de versiones
        "git",
        # Acceso a la red
        "ssh", "curl", "wget", "ftp", "sftp",
        # Escalada de privilegios
        "sudo", "su",
        # Contenedorización/Virtualización (controlado por el adaptador)
        "docker", "podman",
        # Shells interactivos o ejecución de scripts no controlada
        "bash", "sh", "zsh",
    }

    def evaluate(self, command: str) -> Tuple[bool, str]:
        """
        Evalúa un comando contra la política.

        Retorna (True, "Razón") si está permitido, (False, "Razón") si está bloqueado.
        La lógica es fail-closed: un comando debe estar explícitamente permitido.
        """
        if not command or not command.strip():
            return False, "El comando está vacío y está bloqueado."

        cmd_base = command.strip().split()[0]

        if cmd_base in self.BLOCKLIST:
            return False, f"Comando '{cmd_base}' está en la blocklist y está bloqueado."

        if cmd_base in self.ALLOWLIST:
            return True, f"Comando '{cmd_base}' está en la allowlist y está permitido."

        return False, f"Comando '{cmd_base}' no está en la allowlist y está bloqueado por defecto."
