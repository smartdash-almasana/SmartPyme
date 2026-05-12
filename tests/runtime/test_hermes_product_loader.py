from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.runtime.hermes_product_loader import (
    HERMES_PRODUCT_CONFIG_ENV_VAR,
    HermesProductConfigError,
    load_product_config,
)


def test_load_product_config_success(monkeypatch, tmp_path: Path):
    """Verifica que la configuración se carga correctamente desde un archivo YAML válido."""
    config_content = {"model": "gemma-4", "tools": ["tool1"]}
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_content))

    monkeypatch.setenv(HERMES_PRODUCT_CONFIG_ENV_VAR, str(config_file))

    config = load_product_config()
    assert config == config_content


def test_load_product_config_raises_error_when_var_not_set(monkeypatch):
    """Verifica que se lanza una excepción si la variable de entorno no está definida."""
    monkeypatch.delenv(HERMES_PRODUCT_CONFIG_ENV_VAR, raising=False)

    with pytest.raises(HermesProductConfigError, match="no está definida"):
        load_product_config()


def test_load_product_config_raises_error_when_file_not_found(monkeypatch):
    """Verifica que se lanza una excepción si el archivo de config no existe."""
    monkeypatch.setenv(HERMES_PRODUCT_CONFIG_ENV_VAR, "/path/to/nonexistent/file.yaml")

    with pytest.raises(HermesProductConfigError, match="no existe en"):
        load_product_config()


def test_load_product_config_raises_error_on_invalid_yaml(monkeypatch, tmp_path: Path):
    """Verifica que se lanza una excepción si el archivo YAML es inválido."""
    config_file = tmp_path / "invalid.yaml"
    # An unclosed bracket is invalid YAML
    config_file.write_text("model: gemma-4\ntools: [tool1,")

    monkeypatch.setenv(HERMES_PRODUCT_CONFIG_ENV_VAR, str(config_file))

    with pytest.raises(HermesProductConfigError, match="Error al parsear"):
        load_product_config()
        load_product_config()
