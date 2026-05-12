#!/usr/bin/env python3
"""
Guard script to detect forbidden imports in PRODUCT_RUNTIME areas.

Forbidden import patterns:
- factory*
- factory_v2*
- factory_v3*
- experiments*
- extraction*

Protected directories:
- app/
- core/
- services/
- models/

Exceptions are loaded from config/product_boundary_guard_exceptions.json
"""

import ast
import json
import os
import sys
from pathlib import Path

# Directories to protect (relative to repo root)
PROTECTED_DIRS = ["app", "core", "services", "models"]

# Forbidden import prefixes
FORBIDDEN_PATTERNS = [
    "factory",
    "factory_v2",
    "factory_v3",
    "experiments",
    "extraction",
]


def load_exceptions(repo_root: Path) -> list[str]:
    """Load allowed path prefixes from exceptions config file."""
    exceptions_file = repo_root / "config" / "product_boundary_guard_exceptions.json"
    if not exceptions_file.exists():
        return []
    
    try:
        with open(exceptions_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("allowed_prefixes", [])
    except Exception:
        return []


def is_protected_path(file_path: Path, repo_root: Path) -> bool:
    """Check if file is under a protected directory."""
    try:
        rel_path = file_path.relative_to(repo_root)
        parts = rel_path.parts
        if len(parts) == 0:
            return False
        return parts[0] in PROTECTED_DIRS
    except ValueError:
        return False


def is_exception_path(file_path: Path, repo_root: Path, allowed_prefixes: list[str]) -> bool:
    """Check if file path matches any allowed exception prefix."""
    try:
        rel_path = file_path.relative_to(repo_root)
        rel_path_str = str(rel_path)
        for prefix in allowed_prefixes:
            if rel_path_str.startswith(prefix):
                return True
    except ValueError:
        pass
    return False


def check_imports(file_path: Path, repo_root: Path) -> list[str]:
    """Check a Python file for forbidden imports."""
    violations = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return violations
    
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return violations
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                for pattern in FORBIDDEN_PATTERNS:
                    if module_name == pattern or module_name.startswith(pattern + "."):
                        violations.append(f"{file_path}: import {module_name}")
                        break
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            for pattern in FORBIDDEN_PATTERNS:
                if module_name == pattern or module_name.startswith(pattern + "."):
                    violations.append(f"{file_path}: from {module_name} import ...")
                    break
    
    return violations


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    # Load exceptions
    allowed_prefixes = load_exceptions(repo_root)
    
    violations = []
    ignored_exceptions = []
    
    # Find all Python files in protected directories
    for protected_dir in PROTECTED_DIRS:
        dir_path = repo_root / protected_dir
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob("*.py"):
            if not is_protected_path(py_file, repo_root):
                continue
            
            # Check if this file is an exception
            if is_exception_path(py_file, repo_root, allowed_prefixes):
                ignored_exceptions.append(str(py_file.relative_to(repo_root)))
                continue
            
            file_violations = check_imports(py_file, repo_root)
            violations.extend(file_violations)
    
    # Print ignored exceptions info
    if ignored_exceptions:
        print("EXCEPTIONS IGNORED (configured in product_boundary_guard_exceptions.json):")
        print("-" * 50)
        for exc in ignored_exceptions:
            print(f"  - {exc}")
        print("-" * 50)
        print()
    
    if violations:
        print("PRODUCT BOUNDARY VIOLATIONS DETECTED:")
        print("=" * 50)
        for v in violations:
            print(v)
        print("=" * 50)
        print(f"Total violations: {len(violations)}")
        sys.exit(1)
    else:
        print("No product boundary violations detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
