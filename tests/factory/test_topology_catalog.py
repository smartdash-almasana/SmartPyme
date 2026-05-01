import json
import shutil
import unittest
import uuid
from pathlib import Path

from factory.topology_catalog import load_topology_catalog


class TopologyCatalogTests(unittest.TestCase):
    def _case_root(self) -> Path:
        base = Path(__file__).resolve().parents[2] / ".tmp" / "topology_catalog_tests"
        base.mkdir(parents=True, exist_ok=True)
        root = base / f"case_{uuid.uuid4().hex}"
        root.mkdir(parents=True, exist_ok=False)
        return root

    def test_load_and_validate_cantera_layer_mapping(self) -> None:
        root = self._case_root()
        try:
            catalog_path = root / "factory" / "topology_catalog.json"
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            catalog_path.write_text(
                json.dumps(
                    {
                        "core_layers": {
                            "clarification": {
                                "target_files": [
                                    "app/core/clarification/service.py"
                                ]
                            }
                        },
                        "official_assembly_order": ["clarification"],
                        "canteras": [
                            {
                                "name": "smartcounter",
                                "path_prefix": "E:/BuenosPasos/smartcounter",
                                "possible_layers": ["clarification"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            catalog = load_topology_catalog(catalog_path)
            assert catalog is not None
            self.assertTrue(catalog.is_known_layer("clarification"))
            self.assertTrue(
                catalog.can_excavate(
                    "E:\\BuenosPasos\\smartcounter\\backend",
                    "clarification",
                )
            )
            self.assertFalse(catalog.can_excavate("E:\\BuenosPasos\\smartexcel", "clarification"))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_allowed_target_paths_for_layer_is_normalized(self) -> None:
        root = self._case_root()
        try:
            catalog_path = root / "factory" / "topology_catalog.json"
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            catalog_path.write_text(
                json.dumps(
                    {
                        "core_layers": {
                            "reconciliation": {
                                "target_files": [
                                    "app\\core\\reconciliation\\models.py",
                                    "tests/core/test_reconciliation_service.py",
                                ]
                            }
                        },
                        "official_assembly_order": ["reconciliation"],
                        "canteras": [],
                    }
                ),
                encoding="utf-8",
            )

            catalog = load_topology_catalog(catalog_path)
            assert catalog is not None
            allowed = catalog.allowed_target_paths_for_layer("reconciliation")
            self.assertIn("app/core/reconciliation/models.py", allowed)
            self.assertIn("tests/core/test_reconciliation_service.py", allowed)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
