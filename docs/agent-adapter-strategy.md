# Agent Adapter Strategy

This project should be understood as an agent-assisted thesis workflow, not as a Python-only tool.

## Why Agent-First

Graduate thesis review involves judgment:

- Is a concept really upper-level, or only a tool?
- Did chapter 4 operate the theory, or only mention it?
- Is a research gap defensible?
- What is the smallest safe revision before meeting an advisor?

These are not good targets for hard-coded Python decisions. They are better handled by an AI agent using source-grounded rules and repeatable evidence reports.

## Why Keep Python

Python remains useful for deterministic work:

- read source files
- extract citation candidates
- generate literature-map templates
- list concept candidates and representative sentences
- create promise-delivery tables
- render placeholder DOCX
- scan for public-safety risks

The intended division is:

| Layer | Responsibility |
| --- | --- |
| Python | collect evidence, produce repeatable reports, reduce hallucination risk |
| Agent skill/command | interpret evidence, ask follow-up questions, make scholarly judgments |
| Human student/advisor | verify sources, approve claims, decide final thesis direction |

## Adapter Design

All platforms should reference the same core:

- `agents/shared/thesis-agent-core.md`
- `agents/shared/command-map.md`

Platform-specific files should stay small:

- Codex: `AGENTS.md` plus `agents/codex/skills/grad-thesis-agent/SKILL.md`
- Antigravity: `.agents/skills/grad-thesis-agent/SKILL.md`
- Claude Code: `CLAUDE.md`, `.claude/commands/thesis/`, `.claude/agents/`
- Gemini CLI: `GEMINI.md`, `.gemini/commands/thesis/`

## Workflow Example

For a concept hierarchy review:

1. Agent reads shared rules.
2. Agent runs `python scripts/manuscript_concept_audit.py all --source source/shadow`.
3. Agent reads the generated reports.
4. Agent checks the manuscript sentences.
5. Agent returns a table with evidence, judgment, and minimum-change revision plan.

For a vague topic:

1. Agent creates a literature-map workspace.
2. Agent treats all literature output as unverified candidates.
3. Agent asks the student to verify seed papers and data access.
4. Agent turns the strongest path into advisor questions and chapter tasks.

## Maintenance Rule

Do not maintain separate logic in each adapter. If a workflow changes, update shared core first, then update platform wrappers only where command syntax changes.
