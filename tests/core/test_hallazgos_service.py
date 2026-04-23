import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.hallazgos.service import crear_hallazgo

def test_crear_hallazgo():
    hallazgo = crear_hallazgo(id="H-001", descripcion="Test hallazgo")
    assert hallazgo.id == "H-001"
    assert hallazgo.descripcion == "Test hallazgo"
