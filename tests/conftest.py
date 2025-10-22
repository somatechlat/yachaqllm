"""Pytest conftest to ensure the repository root is on sys.path for test imports."""
from __future__ import annotations

import sys
from pathlib import Path

# Insert the repository root so tests can import the `rag` package directly.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
