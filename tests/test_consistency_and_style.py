"""Tests for the consistency audit and style scan helpers."""

from __future__ import annotations

from pathlib import Path

import thesis_consistency_audit as tca
import thesis_style_scan as tss


def test_extract_terms_reads_bullet_list():
    canonical = "\n".join(
        [
            "# Canonical Terms",
            "",
            "- 數位轉型; digital transformation",
            "- 服務流程治理框架: service-process governance",
            "not a bullet line",
            "- PSC",
        ]
    )
    terms = tca.extract_terms(canonical)
    assert terms == ["數位轉型", "服務流程治理框架", "PSC"]


def test_style_scan_flags_weak_phrase(tmp_path: Path):
    target = tmp_path / "ch.md"
    # The style guard watches for process placeholders / weak academic phrasing.
    target.write_text("TODO 補上分析。\n眾所周知這很重要。\n", encoding="utf-8")
    findings = tss.scan_file(target)
    assert findings, "expected the style scan to flag at least one weak phrase"


def test_style_scan_clean_file_has_no_findings(tmp_path: Path):
    target = tmp_path / "ch.md"
    target.write_text("本章描述研究方法與資料來源。\n", encoding="utf-8")
    assert tss.scan_file(target) == []
