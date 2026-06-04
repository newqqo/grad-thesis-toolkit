"""Regression tests for committed public-safe sample outputs.

The sample outputs are useful only if they remain reproducible from the bundled
placeholder inputs, so these tests compare generated report text with the
committed references under ``docs/sample-outputs``.
"""

from __future__ import annotations

from pathlib import Path

import extract_citation_candidates as ecc
import manuscript_concept_audit as mca

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "docs" / "sample-outputs"


def _read_sample(name: str) -> str:
    return (SAMPLES / name).read_text(encoding="utf-8")


def test_citation_candidate_sample_output_is_current():
    source = ROOT / "examples" / "outline-with-citations.md"
    report = ecc.render_markdown(ecc.collect_candidates(ecc.read_input(source)), source)
    assert report == _read_sample("citation-candidates.md")


def test_concept_tree_sample_output_is_current():
    source = ROOT / "examples" / "concept-drift-sample.md"
    sentences = mca.read_sentences(source)
    report = mca.render_concept_tree(sentences, mca.collect_occurrences(sentences))
    assert report == _read_sample("concept-tree.md")


def test_promise_delivery_sample_output_is_current():
    source = ROOT / "examples" / "concept-drift-sample.md"
    concepts = ["數位轉型", "服務流程治理框架", "顧客回應機制"]
    sentences = mca.read_sentences(source)
    report = mca.render_promise_delivery(sentences, mca.collect_occurrences(sentences, concepts), concepts)
    assert report == _read_sample("promise-delivery.md")
