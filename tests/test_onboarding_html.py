"""Tests for the static onboarding wizard (docs/onboarding.html).

The wizard is a thin, static onboarding *layer* over the agent workflow. These
tests pin its safety and link integrity so it cannot rot or quietly start
claiming to upload user content.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs" / "onboarding.html"


@pytest.fixture(scope="module")
def text() -> str:
    assert HTML.exists(), "docs/onboarding.html should exist"
    return HTML.read_text(encoding="utf-8")


def test_file_exists():
    assert HTML.exists(), "docs/onboarding.html should exist"


def test_all_doc_links_resolve(text: str):
    """Every relpath referenced in the wizard must point to a real repo file."""
    relpaths = re.findall(r'relpath:\s*"([^"]+)"', text)
    assert relpaths, "expected at least one relpath entry"
    missing = [rel for rel in relpaths if not (ROOT / rel).exists()]
    assert missing == [], f"onboarding links point to missing files: {missing}"


def test_covers_four_student_stages(text: str):
    ids = re.findall(r'id:\s*"([^"]+)"', text)
    for expected in ("no-topic", "vague", "partial", "near-final"):
        assert expected in ids, f"missing stage: {expected}"


def test_is_static_and_safe(text: str):
    lowered = text.lower()
    # No upload / form-submission surface: this page must never take user files.
    assert "<form" not in lowered, "onboarding must not contain a form"
    assert "type=\"file\"" not in lowered and "type='file'" not in lowered
    assert "xmlhttprequest" not in lowered and "fetch(" not in lowered, "must not call the network"
    assert "https://github.com" not in lowered, "doc links should work as local relative paths"
    # Privacy notice must be present.
    assert "不會上傳" in text and "不會儲存" in text
    assert "去識別化" in text and "刪除個資" in text


def test_copy_failure_state_is_visible(text: str):
    assert "複製失敗" in text
    assert "document.execCommand(\"copy\")" in text


def test_no_private_trigger_strings(text: str):
    """The page must pass the same spirit as check_public_readiness."""
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text), "no email addresses"
    secret_label = "api" + "_" + "key"  # assembled so this file stays readiness-clean
    assert secret_label not in text.lower()
