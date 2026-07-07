from __future__ import annotations

import ast
from pathlib import Path


def test_backend_sources_parse_with_python_311_grammar() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    python_files = [
        path
        for path in backend_root.rglob("*.py")
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]

    for path in python_files:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path), feature_version=(3, 11))
