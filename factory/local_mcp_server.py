import os
import sys

from mcp.server.fastmcp import FastMCP

# Creamos el servidor. 
# Importante: No imprimas NADA en este archivo fuera de los logs de MCP.
mcp = FastMCP("SmartPyme-Local")

@mcp.tool()
def verificar_entorno() -> str:
    """Verifica la ruta actual y el entorno."""
    return f"Estoy en: {os.getcwd()} | Python: {sys.version}"

@mcp.tool()
def crear_carpetas_arquitectura() -> str:
    """Crea las carpetas base del proyecto SmartPyme."""
    capas = ["core", "extraction", "knowledge", "mcp", "memory", 
             "modules", "orchestration", "source_connectors", 
             "system_growth", "user_layer"]
    for c in capas:
        os.makedirs(f"app/{c}", exist_ok=True)
        with open(f"app/{c}/__init__.py", "a"): pass
    return "Arquitectura SmartPyme desplegada localmente."

if __name__ == "__main__":
    # mcp.run() usa stdio por defecto, que es lo que espera Antigravity localmente.
    mcp.run()