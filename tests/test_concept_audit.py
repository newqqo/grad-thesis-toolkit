"""Tests for the manuscript concept-audit primitives.

The concept-hierarchy and promise-delivery reports are only trustworthy if the
underlying sentence/term extraction is stable, so these cover the pure helpers.
"""

from __future__ import annotations

import manuscript_concept_audit as mca


def test_split_sentences_breaks_on_cjk_punctuation():
    parts = mca.split_sentences("數位轉型是趨勢。服務流程需要治理框架。")
    assert len(parts) == 2
    assert parts[0].endswith("。")


def test_split_sentences_skips_headings_and_tables():
    assert mca.split_sentences("## p001 標題") == []
    assert mca.split_sentences("| 欄位 | 值 |") == []


def test_clean_term_strips_punctuation_and_noise():
    assert mca.clean_term("（數位轉型）") == "數位轉型"


def test_extract_terms_picks_up_acronyms():
    terms = mca.extract_terms_from_sentence("本研究採用 PSC 作為分析單位。")
    assert "PSC" in terms


def test_infer_level_returns_known_label():
    label = mca.infer_level("工單系統", "工單系統是操作層的工具與指標。")
    assert label in {"upper", "middle", "lower", "mixed", "unclassified"}
