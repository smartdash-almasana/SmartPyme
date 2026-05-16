"""
contamination guard
"""
from pathlib import Path
from .policy import get_project_root, iter_python_files, extract_imports

FORBIDDEN_IMPORT_PREFIXES = [
    "app.",
    "factory",
    "factory_v2",
    "factory_v3",
    "mcp",
    "orchestration",
    "jobs",
    "workflows"
]

def test_no_forbidden_imports():
    root = get_project_root()
    pymia_dir = root / "pymia"
    
    python_files = iter_python_files(pymia_dir)
    
    violations = []
    for fpath in python_files:
        imports = extract_imports(fpath)
        for lineno, imp in imports:
            for prefix in FORBIDDEN_IMPORT_PREFIXES:
                if imp == prefix or imp.startswith(f"{prefix}."):
                    violations.append(f"{fpath.relative_to(root)}:{lineno} -> {imp}")
                    
    assert not violations, "Found forbidden imports:\n" + "\n".join(violations)
