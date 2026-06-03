"""Shared pytest fixtures and import path setup.

The toolkit ships flat scripts under ``scripts/`` rather than an installed
package, so tests add that directory to ``sys.path`` to import them directly.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

for candidate in (ROOT, SCRIPTS):
    text = str(candidate)
    if text not in sys.path:
        sys.path.insert(0, text)
