# Student Stage Router

Use this before choosing a thesis workflow. Do not assume the student knows which tool or command to run.

## Route By Current State

| Stage | Student signal | Agent first action | Evidence command |
| --- | --- | --- | --- |
| No topic | "I don't know what to write", "I only need to start" | Ask 8-10 clarification questions and identify possible research directions. | none yet |
| Vague direction | "I want to do PSC/ESG/AI teaching/digital transformation" | Create literature-map workspace and explain seed-paper/gap workflow. | `python scripts/init_literature_map.py --topic "<topic>" --domain-hint "<hint>"` |
| Partial draft | "I have an outline/chapter draft", "I wrote chapters 1-3" | Run citation candidate and concept-audit checks before rewriting. | `python scripts/extract_citation_candidates.py --input <path>` and `python scripts/manuscript_concept_audit.py all --source <source>` |
| Near final | "I am close to oral defense/submission", "I have chapters 1-5" | Run strict final review: promise-delivery, consistency, style, public readiness, and optional DOCX render. | `python scripts/manuscript_concept_audit.py all --source <source>`, `python scripts/thesis_style_scan.py scan`, `python scripts/thesis_consistency_audit.py`, `python scripts/check_public_readiness.py` |

## Required First Response

If the user's stage is unclear, ask only these three questions:

1. 你現在是：還沒題目、有模糊方向、寫到一半、還是快完稿？
2. 你目前有什麼材料：關鍵字、大綱、章節草稿、文獻清單、或完整第 1-5 章？
3. 這次最想得到什麼：找方向、見老師前整理、修章節、還是口試前審查？

## Stage-Specific Rules

### No Topic

- Do not generate a fake thesis title immediately.
- Ask about work experience, data access, advisor preference, time limit, and acceptable methods.
- Return 3-5 possible directions with risk and next action.

### Vague Direction

- Do not write chapter 2 directly.
- Build seed-paper search logic, literature clusters, gap radar, and advisor questions.
- Mark all paper suggestions as unverified candidates.

### Partial Draft

- Do not rewrite the whole draft first.
- Extract citation candidates.
- Run concept hierarchy and promise-delivery checks.
- Return minimum-change fixes.

### Near Final

- Be strict and evidence-grounded.
- Focus on what can still fail in oral defense: unsupported concepts, unoperated frameworks, conclusion overclaims, citation risk, and privacy/public-readiness.
- Separate mandatory fixes from optional polish.
