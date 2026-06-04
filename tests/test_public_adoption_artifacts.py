from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_visual_proof_screenshots_exist():
    screenshots = ROOT / "docs" / "assets" / "screenshots"
    expected = [
        screenshots / "onboarding-v0.1.8-desktop.png",
        screenshots / "onboarding-v0.1.8-mobile.png",
    ]
    for path in expected:
        assert path.exists(), f"missing visual proof screenshot: {path.name}"
        assert path.stat().st_size > 10_000, f"screenshot appears too small: {path.name}"


def test_visual_proof_doc_links_to_release_and_screenshots():
    text = (ROOT / "docs" / "visual-proof.md").read_text(encoding="utf-8")
    assert "assets/screenshots/onboarding-v0.1.8-desktop.png" in text
    assert "assets/screenshots/onboarding-v0.1.8-mobile.png" in text
    assert "releases/tag/v0.1.8" in text
    assert "45 tests passed" in text


def test_student_workflow_issue_template_is_public_safe():
    path = ROOT / ".github" / "ISSUE_TEMPLATE" / "student_workflow_request.md"
    text = path.read_text(encoding="utf-8")
    assert "Student workflow request" in text
    assert "Do not include private thesis text" in text
    assert "No topic yet" in text
    assert "Vague direction or keyword" in text
    assert "Near-final draft" in text
    assert "unverified until checked" in text
