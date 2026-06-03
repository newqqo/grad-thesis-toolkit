---
name: "grad-thesis-agent"
description: "Use when working on graduate thesis workflows: vague topic to literature map, outline intake, citation-candidate review, concept hierarchy, promise-delivery checks, advisor review loops, or DOCX-first thesis editing with privacy guardrails."
---

# Graduate Thesis Agent

Use this skill for agent-assisted thesis work in this repository.

## Load First

Read these shared files before doing substantive review or edits:

- `agents/shared/thesis-agent-core.md`
- `agents/shared/student-stage-router.md`
- `agents/shared/command-map.md`

## Required Behavior

- Use Traditional Chinese for thesis-facing responses.
- Treat Python scripts as evidence-gathering helpers, not as the final reviewer.
- For first-time users, classify the stage before suggesting commands: no topic, vague direction, partial draft, near final, or unclear.
- For concept hierarchy and promise-delivery checks, use only manuscript sentences unless the user explicitly asks for external literature comparison.
- Quote representative chapter or paragraph evidence for every serious judgment.
- Keep private thesis text, private PDFs, personal data, generated reports with local paths, and credentials out of public commits.

## Common Evidence Commands

```powershell
python scripts/init_literature_map.py --topic "<topic>" --domain-hint "<hint>"
python scripts/extract_citation_candidates.py --input <outline-or-draft>
python scripts/manuscript_concept_audit.py all --source <manuscript-or-source-dir>
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/check_public_readiness.py
```

Use `--concept` on `manuscript_concept_audit.py` when the user names specific high-level concepts.
