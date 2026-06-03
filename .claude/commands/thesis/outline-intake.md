---
description: Intake a thesis outline or proposal and identify safe next steps.
argument-hint: <outline path>
allowed-tools: Read, Glob, Grep, Bash(python scripts/extract_citation_candidates.py:*)
---

Read `agents/shared/thesis-agent-core.md` and `agents/shared/command-map.md`.

Task:

1. Read the outline or draft path from `$ARGUMENTS`.
2. Run `python scripts/extract_citation_candidates.py --input <path> --output consistency/reports/citation_candidates.md`.
3. Read `consistency/reports/citation_candidates.md`.
4. Return a Traditional Chinese intake menu: citation verification, logic/structure pressure test, structural completeness, literature-map expansion, concept alignment, or targeted rewrite.
5. If citation candidates exist, recommend verification before heavy rewriting.
