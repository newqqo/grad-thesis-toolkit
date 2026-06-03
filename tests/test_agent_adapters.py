"""Tests for the cross-agent adapter checker.

The cross-agent story (Codex, Claude, Gemini, Antigravity) is a core selling
point, so the structural invariants that keep those adapters in sync are
worth pinning down.
"""

from __future__ import annotations

import check_agent_adapters as caa


def test_frontmatter_detection():
    assert caa.has_frontmatter("---\nname: x\ndescription: y\n---\nbody")
    assert not caa.has_frontmatter("# just a heading\n")


def test_required_files_present():
    """Every declared adapter file must exist in the repository."""
    assert caa.check_required_files() == []


def test_skill_frontmatter_valid():
    assert caa.check_skill_frontmatter() == []


def test_gemini_toml_commands_valid():
    assert caa.check_toml_commands() == []


def test_shared_core_has_required_terms():
    assert caa.check_shared_core() == []


def test_main_returns_zero():
    assert caa.main() == 0
