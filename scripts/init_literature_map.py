from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "literature"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "topic"


def write_once(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def topic_brief(topic: str, domain_hint: str) -> str:
    return f"""# Topic Brief

## Raw Topic

{topic}

## Domain Hint

{domain_hint or "Not specified yet."}

## Five-Sentence Clarification

1. I am interested in this topic because:
2. The practical problem I observe is:
3. The people, organizations, or systems affected are:
4. The evidence or data I might be able to access are:
5. The thesis-level question I might answer is:

## Topic Narrowing

| Layer | Working Answer |
| --- | --- |
| Broad keyword | {topic} |
| Practical context | |
| Academic field | |
| Main concept | |
| Possible outcome variable | |
| Possible method | |
| Feasible data source | |

## Advisor Check

- Is this topic too broad?
- Is there a real data source?
- Is this a thesis question, or only a work complaint?
- Which chapter would this topic be hardest to write?
"""


def search_plan(topic: str) -> str:
    return f"""# Search Plan

## Goal

Turn the vague topic `{topic}` into a defensible literature map.

## Step 1: Semantic Search For Seed Papers

Use 2-3 tools or databases, not just one.

Suggested options:

- Google Scholar / university library database
- Elicit or another semantic-search tool
- SciSpace or another paper-reading tool
- Scopus / Web of Science if your school provides access

Starter query patterns:

- `{topic} literature review`
- `{topic} systematic review`
- `{topic} research gap`
- `{topic} determinants`
- `{topic} trend`
- `{topic} Taiwan`
- `{topic} Asia`

## Step 2: Record Seed Papers

Pick 5-10 papers that look central. Do not trust AI summaries yet. Record them in `seed-papers.md`.

## Step 3: Citation Expansion

Use at least one citation-map tool when possible:

- Litmaps
- ResearchRabbit
- Connected Papers

Expansion targets:

- older foundational papers
- newer papers citing the seed papers
- review papers
- papers using different methods
- papers from Taiwan or nearby contexts

## Step 4: Matrix Extraction

Fill `literature-matrix.csv`. The minimum useful columns are:

- citation
- year
- country_or_region
- topic_cluster
- theory_or_framework
- method
- data_source
- key_findings
- limitations
- gap_claim
- relevance_to_my_thesis
- verification_status

## Step 5: Gap Radar

Use `gap-radar.md` to classify gaps:

- context gap
- method gap
- data gap
- theory gap
- practical implementation gap
- Taiwan/localization gap

## Rule

AI can help search, sort, and summarize. The student must verify claims against source text before writing them into the thesis.
"""


def seed_papers() -> str:
    return """# Seed Papers

Add 5-10 seed papers here.

| Status | Citation | Why It Is A Seed | Source Link | Verified Source Text? |
| --- | --- | --- | --- | --- |
| candidate | | | | no |

## Notes

- A seed paper is not just a paper that mentions the keyword.
- Prefer review papers, highly cited papers, recent papers, and papers that define the main debate.
- If two AI/search tools return zero overlap, keep both sets and compare why.
"""


def literature_matrix() -> str:
    return (
        "citation,year,country_or_region,topic_cluster,theory_or_framework,method,"
        "data_source,key_findings,limitations,gap_claim,relevance_to_my_thesis,"
        "verification_status,notes\n"
    )


def gap_radar(topic: str) -> str:
    return f"""# Gap Radar

Topic: {topic}

## Current Research Clusters

| Cluster | Representative Papers | What This Cluster Already Knows | What It Does Not Solve |
| --- | --- | --- | --- |
| | | | |

## Gap Types

| Gap Type | Evidence From Literature | Possible Thesis Angle |
| --- | --- | --- |
| Context gap | | |
| Taiwan/local gap | | |
| Method gap | | |
| Data gap | | |
| Theory gap | | |
| Practice gap | | |

## Candidate Research Positions

1. I can extend existing research to a Taiwan context by:
2. I can compare methods by:
3. I can use a different data source by:
4. I can connect academic literature to practice by:
5. I should avoid this direction because it is too broad:

## Final Research Question Candidates

| Candidate | Why It Is Researchable | Required Data | Risk |
| --- | --- | --- | --- |
| | | | |
"""


def advisor_questions(topic: str) -> str:
    return f"""# Advisor Questions

Use this before meeting your advisor about `{topic}`.

## What I Know

- My broad topic is:
- The strongest seed papers so far are:
- The main clusters I see are:
- The most promising gap is:

## What I Need The Advisor To Decide

1. Is this topic suitable for a master's thesis?
2. Which direction is too broad or too shallow?
3. What method would be acceptable in this department?
4. What data source would be credible enough?
5. Which literature cluster must be read first?

## Meeting Output

After the meeting, write:

- approved direction:
- rejected directions:
- next 3 papers to read:
- next data source to verify:
- next draft section to write:
"""


def ai_prompts(topic: str) -> str:
    return f"""# AI Prompts

Use these prompts with an AI assistant. Always verify output against original sources.

## Clarify The Topic

```text
I only know I want to study "{topic}". Ask me 10 clarification questions, then propose 5 narrower master's thesis topics. For each topic, explain required data, likely method, and risk.
```

## Build Search Queries

```text
Create search queries for "{topic}" using English and Traditional Chinese terms. Separate queries into: broad review, recent trend, method, Taiwan/local context, and research gap. Include Boolean query variants.
```

## Classify Literature

```text
Given this literature matrix, group papers into research clusters. For each cluster, summarize what is already known, what methods dominate, and what gap remains. Do not invent papers.
```

## Challenge The Gap

```text
Act as a strict thesis advisor. Based on this gap radar, tell me which proposed gap is too vague, which one is feasible for a master's thesis, and what data I must collect to defend it.
```
"""


def build(args: argparse.Namespace) -> Path:
    topic = args.topic.strip()
    slug = args.slug.strip() if args.slug else slugify(topic)
    target = Path(args.output_root).resolve() / slug
    overwrite = bool(args.overwrite)

    write_once(target / "topic-brief.md", topic_brief(topic, args.domain_hint), overwrite)
    write_once(target / "search-plan.md", search_plan(topic), overwrite)
    write_once(target / "seed-papers.md", seed_papers(), overwrite)
    write_once(target / "literature-matrix.csv", literature_matrix(), overwrite)
    write_once(target / "gap-radar.md", gap_radar(topic), overwrite)
    write_once(target / "advisor-questions.md", advisor_questions(topic), overwrite)
    write_once(target / "ai-prompts.md", ai_prompts(topic), overwrite)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a literature-map workspace for a vague thesis topic.")
    parser.add_argument("--topic", required=True, help="Raw topic keyword or phrase, e.g. PSC")
    parser.add_argument("--domain-hint", default="", help="Optional domain hint, e.g. maritime safety")
    parser.add_argument("--slug", default="", help="Optional output folder name")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    target = build(args)
    print(f"created literature map workspace: {target}")


if __name__ == "__main__":
    main()
