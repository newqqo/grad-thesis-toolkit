---
description: Route a first-time thesis user to the right workflow by current stage.
argument-hint: [student situation]
allowed-tools: Read, Glob, Grep, Bash
---

Read:

- `agents/shared/thesis-agent-core.md`
- `agents/shared/student-stage-router.md`
- `agents/shared/command-map.md`

Task:

1. Use `$ARGUMENTS` as the student's current situation.
2. Classify the student as: no topic, vague direction, partial draft, near final, or unclear.
3. If unclear, ask only the three questions from `student-stage-router.md`.
4. If clear, return the first workflow, exact next agent action, and optional evidence command.
5. Do not ask the student to run every command at once.

