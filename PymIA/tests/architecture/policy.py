"""
contamination guard
Helper library for structural architectural tests.
"""
import ast
import os
from pathlib import Path
from typing import List, Tuple

def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent

def iter_python_files(directory: Path) -> List[Path]:
    files = []
    if not directory.exists():
        return files
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(Path(root) / filename)
    return files

def extract_imports(file_path: Path) -> List[Tuple[int, str]]:
    """Returns a list of (line_number, imported_module_name)."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return []
            
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imports.append((node.lineno, f"{node.module}.{alias.name}"))
    return imports

def scan_file_for_terms(file_path: Path, forbidden_terms: List[str], allow_patterns: List[str] = None) -> List[Tuple[int, str, str]]:
    """Returns lines and terms found in the file, ignoring lines matching allow_patterns."""
    findings = []
    if allow_patterns is None:
        allow_patterns = []
        
    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            lower_line = line.lower()
            
            # Si la lnea contiene un patrn permitido, es una "prohibicin explcita" y la omitimos
            if any(p.lower() in lower_line for p in allow_patterns):
                continue
                
            for term in forbidden_terms:
                if term.lower() in lower_line:
                    findings.append((idx + 1, term, line.strip()))
    return findings
