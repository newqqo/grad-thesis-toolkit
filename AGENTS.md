# Agent Instructions

This repository is an agent-assisted thesis workflow toolkit. Before thesis review or editing work, read:

- `agents/shared/thesis-agent-core.md`
- `agents/shared/student-stage-router.md`
- `agents/shared/command-map.md`

Key rules:

- Use Traditional Chinese for thesis-facing responses unless asked otherwise.
- For first-time users, route by stage before suggesting tools: no topic, vague direction, partial draft, near final, or unclear.
- Treat Python scripts as evidence and repeatability tools, not as replacements for scholarly judgment.
- For concept hierarchy and promise-delivery checks, use manuscript text only and quote representative sentences.
- Never invent citations, DOI values, data, advisor comments, or findings.
- Do not commit private thesis text, personal data, unpublished drafts, private PDFs, generated reports with local paths, or credentials.
- Run `python scripts/check_public_readiness.py` before public-facing changes.
