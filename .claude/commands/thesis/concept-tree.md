---
description: Build a source-grounded thesis concept hierarchy tree.
argument-hint: [source path] [--concept term]
allowed-tools: Read, Glob, Grep, Bash(python scripts/manuscript_concept_audit.py:*)
---

Read `agents/shared/thesis-agent-core.md`, `agents/shared/student-stage-router.md`, and `agents/shared/command-map.md`.

Task:

1. Run `python scripts/manuscript_concept_audit.py concept-tree --source <source>` using `$ARGUMENTS`; default source is `source/shadow`.
2. Read `consistency/reports/concept_hierarchy_report.md`.
3. Produce a Traditional Chinese review that lists upper-level fields, mid-level analysis units, lower-level tools/measures/operations, representative sentences, stable terms, drifted terms, naming conflicts, and a minimum-change unification plan.
4. Use only manuscript text as evidence unless the user explicitly asks for external theory.
