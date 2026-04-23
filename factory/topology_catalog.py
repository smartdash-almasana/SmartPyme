from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY_CATALOG_PATH = BASE_DIR / "factory" / "topology_catalog.json"


@dataclass(frozen=True, slots=True)
class TopologyCatalog:
    path: Path
    data: dict[str, object]

    @property
    def layers(self) -> set[str]:
        core_layers = self.data.get("core_layers", {})
        if not isinstance(core_layers, dict):
            return set()
        return {str(key) for key in core_layers.keys()}

    @property
    def official_assembly_order(self) -> list[str]:
        value = self.data.get("official_assembly_order", [])
        if not isinstance(value, list):
            return []
        return [str(item) for item in value]

    def is_known_layer(self, layer: str) -> bool:
        return layer in self.layers

    def allowed_target_paths_for_layer(self, layer: str) -> set[str]:
        core_layers = self.data.get("core_layers", {})
        if not isinstance(core_layers, dict):
            return set()
        layer_data = core_layers.get(layer, {})
        if not isinstance(layer_data, dict):
            return set()
        target_files = layer_data.get("target_files", [])
        if not isinstance(target_files, list):
            return set()
        return {str(item).replace("\\", "/").lower() for item in target_files if isinstance(item, str)}

    def can_excavate(self, cantera_path: str, layer: str) -> bool:
        normalized = cantera_path.replace("\\", "/").lower()
        canteras = self.data.get("canteras", [])
        if not isinstance(canteras, list):
            return False
        for cantera in canteras:
            if not isinstance(cantera, dict):
                continue
            prefix = str(cantera.get("path_prefix", "")).replace("\\", "/").lower().rstrip("/")
            if not prefix:
                continue
            if normalized.startswith(prefix):
                possible_layers = cantera.get("possible_layers", [])
                if not isinstance(possible_layers, list):
                    return False
                return layer in {str(item) for item in possible_layers}
        return False


def load_topology_catalog(
    path: Path = DEFAULT_TOPOLOGY_CATALOG_PATH,
) -> TopologyCatalog | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"TOPOLOGY_INVALIDA: estructura raiz invalida en {path}")
    return TopologyCatalog(path=path, data=data)
