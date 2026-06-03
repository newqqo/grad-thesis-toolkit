# Codex Adapter

Codex can use this repository through two layers:

1. Root `AGENTS.md` for repository-level behavior.
2. `agents/codex/skills/grad-thesis-agent/SKILL.md` as a reusable skill template.

To install the skill into a Codex environment, copy the `grad-thesis-agent` folder into the local Codex skills directory, then start a new Codex thread in this repository.

The skill should trigger for first-use student-stage routing, thesis review, concept hierarchy, promise-delivery checks, outline intake, literature maps, near-final oral-defense review, advisor review, and DOCX-first thesis editing.
