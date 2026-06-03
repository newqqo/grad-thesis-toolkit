"""Tests for the citation-candidate extractor.

These lock in the detection behaviour the outline-intake workflow depends on:
the extractor must surface citation-like strings as *candidates* without
inventing or verifying anything.
"""

from __future__ import annotations

import extract_citation_candidates as ecc


def kinds(text: str) -> set[str]:
    return {item["kind"] for item in ecc.collect_candidates(text)}


def test_detects_english_author_year():
    candidates = ecc.collect_candidates("Porter (1980) defined competitive strategy.")
    assert any(c["kind"] == "author-year" and "1980" in c["candidate"] for c in candidates)


def test_detects_doi():
    candidates = ecc.collect_candidates("See https://doi.org/10.1016/j.marpol.2020.103889 for detail.")
    assert any(c["kind"] == "doi" for c in candidates)


def test_detects_chinese_author_year():
    candidates = ecc.collect_candidates("林某某（2019）指出數位轉型的困難。")
    assert any(c["kind"] == "zh-author-year" and "2019" in c["candidate"] for c in candidates)


def test_no_false_positive_on_plain_prose():
    assert ecc.collect_candidates("這一段沒有任何引用，只是普通敘述。") == []


def test_candidates_are_deduplicated():
    text = "Porter (1980). Porter (1980)."  # same kind + string + line collapses
    one_line = ecc.collect_candidates(text)
    # Two on the same line are distinct matches but identical -> dedup keeps one.
    assert sum(1 for c in one_line if c["candidate"] == "Porter (1980)") == 1


def test_report_marks_everything_unverified():
    report = ecc.render_markdown(ecc.collect_candidates("Porter (1980)."), source=ecc.ROOT / "x.md")
    assert "unverified" in report
    assert "does not verify" in report
