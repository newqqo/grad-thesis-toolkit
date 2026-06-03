"""End-to-end smoke test for the placeholder DOCX render.

The render path uses ``python-docx`` only (no Word/COM automation), so it must
succeed on Linux, macOS, and Windows. This guards the claim that a reviewer can
clone the repository on any platform and produce a deliverable.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_thin_template_then_render(tmp_path: Path):
    template = _run("scripts/create_thin_template_v2.py")
    assert template.returncode == 0, template.stderr

    render = _run("scripts/thesis_md_pipeline_v2.py", "render", "--skip-pdf")
    assert render.returncode == 0, render.stderr

    out = ROOT / "deliverables" / "docx" / "thesis_render_v2_latest.docx"
    assert out.exists(), "expected a rendered placeholder DOCX"
    assert out.stat().st_size > 0
