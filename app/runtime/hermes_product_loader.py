from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

HERMES_PRODUCT_CONFIG_ENV_VAR = "HERMES_PRODUCT_CONFIG_PATH"


class HermesProductConfigError(Exception):
    """Custom exception for configuration loading errors."""


def load_product_config() -> dict[str, Any]:
    """
    Carga la configuración de Hermes Producto desde la ruta especificada
    en la variable de entorno HERMES_PRODUCT_CONFIG_ENV_VAR.

    Levanta HermesProductConfigError si la variable no está definida o
    el archivo no existe.
    """
    config_path_str = os.getenv(HERMES_PRODUCT_CONFIG_ENV_VAR)
    if not config_path_str:
        raise HermesProductConfigError(
            f"La variable de entorno {HERMES_PRODUCT_CONFIG_ENV_VAR} no está definida."
        )

    config_path = Path(config_path_str)
    if not config_path.is_file():
        raise HermesProductConfigError(f"El archivo de configuración no existe en: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise HermesProductConfigError(
                f"Error al parsear el archivo YAML de configuración: {config_path}"
            ) from exc
