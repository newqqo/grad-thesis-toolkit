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

## What Belongs In Skills Or Agent Commands

- vague topic to literature-map guidance
- outline intake and citation-risk menu
- concept hierarchy review
- theoretical promise-delivery review
- advisor-facing next steps
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
