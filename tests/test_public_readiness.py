"""Tests for the public-readiness scanner.

This is the privacy guardrail that runs before public commits, so its
detections (and its own clean pass over the repository) must stay reliable.

The trigger strings below are assembled at runtime from fragments so that this
test file does not itself contain literal private-looking content -- that keeps
the repository's own readiness scan clean.
"""

from __future__ import annotations

from pathlib import Path

import check_public_readiness as cpr


def _write(tmp_path: Path, name: str, body: str) -> Path:
    target = tmp_path / name
    target.write_text(body, encoding="utf-8")
    return target


def test_flags_email_address(tmp_path: Path):
    email = "student" + "@" + "example" + ".com"
    _write(tmp_path, "note.md", f"Contact me at {email} please.")
    assert cpr.scan(tmp_path, cpr.DEFAULT_BLOCKLIST), "an email address should be flagged"


def test_flags_windows_user_path(tmp_path: Path):
    path = "C:" + "\\Users\\" + "alice\\thesis"
    _write(tmp_path, "note.md", f"Saved under {path}")
    assert cpr.scan(tmp_path, cpr.DEFAULT_BLOCKLIST)


def test_flags_api_key_token(tmp_path: Path):
    label = "api" + "_" + "key"
    _write(tmp_path, "config.md", f"{label} = do-not-commit")
    assert cpr.scan(tmp_path, cpr.DEFAULT_BLOCKLIST)


def test_clean_content_passes(tmp_path: Path):
    _write(tmp_path, "ok.md", "這是一段安全的占位內容，沒有私人資訊。")
    assert cpr.scan(tmp_path, cpr.DEFAULT_BLOCKLIST) == []


def test_repository_itself_is_clean():
    """The committed repository must pass its own privacy scan."""
    findings = cpr.scan(cpr.ROOT, cpr.DEFAULT_BLOCKLIST)
    assert findings == [], f"repository tripped the readiness scan: {findings[:3]}"
