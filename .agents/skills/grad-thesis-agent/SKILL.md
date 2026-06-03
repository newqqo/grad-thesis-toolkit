---
name: "grad-thesis-agent"
description: "Use for graduate thesis workflows: topic narrowing, literature mapping, outline intake, citation-candidate review, concept hierarchy, theoretical promise-delivery checks, advisor review loops, and DOCX-first thesis editing."
---

# Graduate Thesis Agent

This is the workspace skill adapter for agent environments that support `.agents/skills`.

## Shared Context

Before substantive review, read:

- `agents/shared/thesis-agent-core.md`
- `agents/shared/student-stage-router.md`
- `agents/shared/command-map.md`

## Operating Rules

- Use Traditional Chinese for thesis-facing responses.
- For first-time users, classify the stage before suggesting commands: no topic, vague direction, partial draft, near final, or unclear.
- Do not treat AI output as verified scholarship.
- Use repository scripts to collect evidence, then make a clearly reasoned judgment from manuscript text.
- Do not invent citations, DOI values, findings, datasets, or advisor feedback.
- For concept hierarchy and promise-delivery tasks, quote manuscript sentences and keep external theory out unless requested.
- Run public-readiness checks before any public-facing commit.

## Evidence Commands

```powershell
python scripts/run_demo.py
python scripts/init_literature_map.py --topic "<topic>" --domain-hint "<hint>"
python scripts/extract_citation_candidates.py --input <outline-or-draft>
python scripts/manuscript_concept_audit.py all --source <manuscript-or-source-dir>
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/check_public_readiness.py
```
