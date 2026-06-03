# Agent Adapters

This repository is designed to be used with AI agents, not only as a Python toolkit.

## Architecture

```text
shared rules
  -> platform adapters
  -> evidence scripts
  -> manuscript-facing review
```

- Shared rules live in `agents/shared/`.
- First-use routing lives in `agents/shared/student-stage-router.md`.
- Platform adapters live in root agent files and platform-specific folders.
- Python scripts collect evidence and produce repeatable reports.
- The agent interprets those reports with scholarly judgment.

## Platform Files

| Platform | Files |
| --- | --- |
| Codex | `AGENTS.md`, `agents/codex/skills/grad-thesis-agent/SKILL.md` |
| Antigravity | `.agents/skills/grad-thesis-agent/SKILL.md` |
| Claude Code | `CLAUDE.md`, `.claude/commands/thesis/*.md`, `.claude/agents/thesis-reviewer.md` |
| Gemini CLI | `GEMINI.md`, `.gemini/commands/thesis/*.toml` |

## First-Use Routing

Use the `start` command or shared router before selecting a workflow:

- Claude: `/thesis:start`
- Gemini: thesis `start` custom command
- Codex/Antigravity: use the `grad-thesis-agent` skill and read `agents/shared/student-stage-router.md`

## Near-Final Review

Use the final-review command when the student already has a full or near-full draft:

- Claude: `/thesis:final-review`
- Gemini: thesis `final-review` custom command
- Codex/Antigravity: use the `grad-thesis-agent` skill, then run the final defense review row in `agents/shared/command-map.md`

The human-facing result should be grouped as `必修`, `建議修`, `可不修`, and `可答辯處理`. Do not describe the generated DOCX as school-format compliant unless the user's institutional template has been checked separately.

## What Belongs In Skills Or Agent Commands

- vague topic to literature-map guidance
- outline intake and citation-risk menu
- concept hierarchy review
- theoretical promise-delivery review
- advisor-facing next steps
- near-final oral-defense risk classification
- scholarly pressure testing
- source-grounded rewrite planning

## What Belongs In Python

- extracting citation candidates
- generating literature-map workspace files
- scanning manuscript concept candidates
- producing chapter promise-delivery report tables
- rendering placeholder DOCX
- checking public-readiness risks
- running repeatable CI smoke tests

## Shared Rule

When adding a new workflow, update `agents/shared/thesis-agent-core.md` first. Then add only the platform-specific trigger or command wrapper.
