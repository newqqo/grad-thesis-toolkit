# Agent Command Map

Use this map to keep platform-specific adapters aligned.

| Workflow | Evidence command | Human-facing result |
| --- | --- | --- |
| Public-safe demo | `python scripts/run_demo.py` | Runs literature map, citation candidates, concept audits, style audit, consistency audit, and DOCX render. |
| Vague topic | `python scripts/init_literature_map.py --topic "<topic>" --domain-hint "<hint>"` | Creates topic brief, search plan, seed papers, matrix, gap radar, advisor questions, and AI prompts. |
| Outline intake | `python scripts/extract_citation_candidates.py --input <outline>` | Lists citation-like strings as unverified candidates. |
| Concept hierarchy | `python scripts/manuscript_concept_audit.py concept-tree --source <manuscript>` | Candidate concept tree with representative sentences and drift signals. |
| Promise-delivery | `python scripts/manuscript_concept_audit.py promise-delivery --source <manuscript> --concept <term>` | Chapter 1/2/4/5 consistency table. |
| Final defense review | `python scripts/manuscript_concept_audit.py all --source <manuscript>` plus `python scripts/thesis_style_scan.py scan`, `python scripts/thesis_consistency_audit.py`, and `python scripts/check_public_readiness.py` | Strict near-final review grouped as mandatory fixes, recommended fixes, optional polish, and oral-defense handling. |
| Style scan | `python scripts/thesis_style_scan.py scan` | Generic style watch report. |
| Consistency audit | `python scripts/thesis_consistency_audit.py` | Canonical term and chapter-contract report. |
| Public readiness | `python scripts/check_public_readiness.py` | Scans for obvious private-content risks. |
| Render DOCX | `python scripts/thesis_md_pipeline_v2.py render --skip-pdf` | Writes placeholder DOCX output. |
