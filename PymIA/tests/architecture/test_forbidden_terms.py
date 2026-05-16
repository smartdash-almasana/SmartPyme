"""
contamination guard
"""
from pathlib import Path
from .policy import get_project_root, iter_python_files, scan_file_for_terms

FORBIDDEN_TERMS = [
    "create_job",
    "authorization",
    "decision_type",
    "workflow",
    "orchestration"
]

# Excepciones para prohibiciones explicitas (en docs o docstrings/tests)
ALLOW_PATTERNS = [
    "forbidden",
    "no incluye",
    "no recibe",
    "no devuelve",
    " no debe",
    " no se",
    "ni ",
    "sin ",
    "ausencia",
    "ningún",
    "ningun",
    "boundary",
    "intenta",
    "- create_job",
    "crear workflows",
    "escalar a orchestration",
    '"workflow",',
    '"authorization",',
    '"orchestration",',
    '"create_job",',
    '"decision_type",',
    "'workflow',",
    "'authorization',",
    "'orchestration',",
    "'create_job',",
    "'decision_type',"
]

def test_no_forbidden_terms_in_code():
    root = get_project_root()
    
    dirs_to_scan = [root / "pymia", root / "tests"]
    
    files_to_scan = []
    for d in dirs_to_scan:
        if d.exists():
            files_to_scan.extend(iter_python_files(d))
            
    violations = []
    for fpath in files_to_scan:
        # Exceptions: architecture tests
        if "architecture" in fpath.parts and ("policy.py" in fpath.name or "test_forbidden_terms.py" in fpath.name or "test_forbidden_imports.py" in fpath.name or "__init__.py" in fpath.name):
            continue
            
        findings = scan_file_for_terms(fpath, FORBIDDEN_TERMS, ALLOW_PATTERNS)
        for lineno, term, context in findings:
            violations.append(f"{fpath.relative_to(root)}:{lineno} -> {term} (context: {context})")
            
    assert not violations, "Found forbidden terms in code:\n" + "\n".join(violations)
