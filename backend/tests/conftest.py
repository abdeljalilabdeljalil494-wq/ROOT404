"""Ensure `app` is importable regardless of where pytest is launched from.

`backend/pytest.ini` (pythonpath = .) already covers `pytest` runs from
backend/; this fallback covers `pytest backend/tests` / `python -m pytest
backend/tests` from the repository root, on Linux, macOS and Windows.
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
