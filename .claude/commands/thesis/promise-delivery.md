---
description: Check whether chapter 1 theoretical promises are supported, operated, and recovered.
argument-hint: [source path] [--concept term]
allowed-tools: Read, Glob, Grep, Bash(python scripts/manuscript_concept_audit.py:*)
---

Read `agents/shared/thesis-agent-core.md`, `agents/shared/student-stage-router.md`, and `agents/shared/command-map.md`.

Task:

1. Run `python scripts/manuscript_concept_audit.py promise-delivery --source <source>` using `$ARGUMENTS`; default source is `source/shadow`.
2. Read `consistency/reports/promise_delivery_report.md`.
3. Produce a high-standard Traditional Chinese review table with: concept name, chapter 1 promise, chapter 2 support, chapter 4 operation, chapter 5 recovery, judgment, and recommendation.
4. Quote representative manuscript sentences. Do not give abstract comments without chapter evidence.
