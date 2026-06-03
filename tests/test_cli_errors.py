"""Tests that the CLIs fail friendly, not with a traceback.

A student who mistypes a path should get a clear one-line message and a
non-zero exit code, never a Python stack trace and never a misleading
"wrote report" success over a path that does not exist.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "args, needle",
    [
        (("scripts/extract_citation_candidates.py", "--input", "no_such_file.md"), "not found"),
        (("scripts/manuscript_concept_audit.py", "all", "--source", "no_such_dir"), "not found"),
        (("scripts/thesis_style_scan.py", "scan", "--source", "no_such_dir"), "not found"),
        (("scripts/thesis_consistency_audit.py", "--source", "no_such_dir"), "not found"),
    ],
)
def test_missing_source_fails_friendly(args, needle):
    result = _run(*args)
    assert result.returncode != 0, "a missing path must exit non-zero"
    combined = (result.stdout + result.stderr).lower()
    assert needle in combined, combined
    assert "traceback" not in combined, "should not dump a Python traceback"


def test_empty_source_warns_but_succeeds(tmp_path: Path):
    """An existing-but-empty source is a warning, not a crash."""
    (tmp_path / "ch1.md").write_text("# heading only\n", encoding="utf-8")
    out = tmp_path / "report.md"
    result = _run(
        "scripts/manuscript_concept_audit.py",
        "concept-tree",
        "--source",
        str(tmp_path),
        "--output",
        str(out),
    )
    assert result.returncode == 0, result.stderr
    assert "warning" in result.stderr.lower()
    assert out.exists()
