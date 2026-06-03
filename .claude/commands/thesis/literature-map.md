---
description: Turn a vague thesis keyword into a literature-map workspace.
argument-hint: <topic> [domain hint]
allowed-tools: Read, Glob, Grep, Bash(python scripts/init_literature_map.py:*)
---

Read `agents/shared/thesis-agent-core.md` and `agents/shared/command-map.md`.

Task:

1. Use `$ARGUMENTS` as the topic and optional domain hint.
2. Run `python scripts/init_literature_map.py --topic "<topic>" --domain-hint "<hint>"`.
3. Read the generated workspace under `literature/<slug>/`.
4. Return a Traditional Chinese advisor-facing summary: possible research clusters, seed-paper search strategy, likely data, method fit, gap radar, and next advisor questions.
5. Mark all literature claims as unverified candidates until source text is checked.
