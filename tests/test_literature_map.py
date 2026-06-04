from __future__ import annotations

import argparse
import csv

import init_literature_map as ilm


def build_tmp(tmp_path, topic: str = "PSC"):
    args = argparse.Namespace(
        topic=topic,
        domain_hint="port state control / maritime safety",
        slug="psc",
        output_root=str(tmp_path),
        overwrite=True,
    )
    return ilm.build(args)


def test_literature_map_includes_traceability_artifacts(tmp_path):
    target = build_tmp(tmp_path)
    expected = {
        "topic-brief.md",
        "first-30-minutes.md",
        "search-plan.md",
        "seed-papers.md",
        "literature-matrix.csv",
        "evidence-registry.csv",
        "ai-usage-log.md",
        "gap-radar.md",
        "advisor-questions.md",
        "ai-prompts.md",
    }
    assert expected <= {path.name for path in target.iterdir()}


def test_evidence_registry_has_verification_columns(tmp_path):
    target = build_tmp(tmp_path)
    with (target / "evidence-registry.csv").open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames is not None
        for column in (
            "source_id",
            "doi_or_url",
            "database_or_tool",
            "search_date",
            "verification_status",
            "evidence_location",
            "supporting_quote_or_note",
            "matrix_fields_supported",
        ):
            assert column in reader.fieldnames
        rows = list(reader)
    assert rows[0]["source_id"] == "S001"
    assert rows[0]["verification_status"] == "unverified"


def test_first_30_minutes_is_public_safe_and_actionable(tmp_path):
    target = build_tmp(tmp_path, topic="AI teaching")
    text = (target / "first-30-minutes.md").read_text(encoding="utf-8")
    assert "AI teaching" in text
    assert "0-5 分鐘" in text
    assert "10-20 分鐘" in text
    assert "不貼私人訪談逐字稿" in text
    assert "evidence-registry.csv" in text


def test_ai_usage_log_records_human_verification(tmp_path):
    target = build_tmp(tmp_path)
    text = (target / "ai-usage-log.md").read_text(encoding="utf-8")
    assert "Human verification" in text
    assert "rejected AI outputs" in text
    assert "Treat literature suggestions as candidates" in text
