# Changelog

## 0.1.6 - Tests And Cross-Platform Reproducibility

- Added a `pytest` test suite under `tests/` covering citation-candidate extraction, the public-readiness privacy scan, agent-adapter integrity, concept-audit primitives, consistency/style helpers, and an end-to-end DOCX render smoke test.
- Added `requirements-dev.txt` and `pytest.ini` so contributors and agents can run `python -m pytest` with one setup step.
- Expanded the CI workflow from a single Windows job to a matrix: unit tests on Linux and Windows, plus a workflow smoke test on Linux, macOS, and Windows. This proves the placeholder render works without Microsoft Word/COM on any platform.
- Documented the cross-platform support boundary: the Markdown-to-DOCX render path is pure Python (`python-docx`); only optional PDF export needs Word on Windows.
- Added a contributor "run the tests" path so Codex and other agents have a verifiable maintenance loop.
- Added committed, public-safe sample outputs under `docs/sample-outputs/` (citation candidates, concept tree, promise-delivery) so reviewers can see what the toolkit produces without running it.
- Made generated report source paths POSIX-style so reports are byte-identical across Linux, macOS, and Windows.

## 0.1.5 - First-Use Student Routing Refinements

- Added first-use student-stage routing for no-topic, vague-direction, partial-draft, and near-final thesis users.
- Added zero-topic onboarding and a first-use simulation report based on four simulated student journeys.
- Added Claude and Gemini final-review commands for near-final oral-defense risk review.
- Updated Codex and Antigravity skill adapters to load the student-stage router before substantive work.
- Improved literature-map templates with Traditional Chinese-first wording for Taiwan students.
- Added a non-PSC AI teaching first-use sample to show the workflow beyond maritime topics.
- Clarified citation-candidate extraction, literature registry sync, report output paths, and DOCX format limitations.

## 0.1.4 - Cross-Agent Thesis Workflow Adapters

- Added shared agent workflow core and command map.
- Added root agent context files for Codex, Claude Code, and Gemini-style project memory.
- Added Codex skill template and Antigravity workspace skill adapter.
- Added Claude Code thesis commands and thesis-reviewer subagent template.
- Added Gemini CLI thesis command templates.
- Added agent adapter strategy documentation and adapter validation script.
- Added agent adapter validation to the one-command demo and CI smoke test.

## 0.1.3 - Concept Hierarchy And Promise-Delivery Checks

- Added manuscript concept audit script for concept hierarchy and theoretical promise-delivery checks.
- Added source-grounded reports for term stability, rank drift, naming conflicts, chapter support, chapter operation, and chapter recovery.
- Added concept drift sample manuscript for public-safe demonstrations.
- Added documentation and research-partner prompt rules for concept hierarchy and promise-delivery review modes.
- Added the concept audit workflow to the one-command demo and CI smoke test.

## 0.1.2 - Literature Map And Research Partner Workflow

- Added vague-topic-to-literature-map workflow for students who only have a keyword.
- Added literature map initializer script and topic workspace templates.
- Added PSC literature map example.
- Added AI research partner playbook and Traditional Chinese prompt template.
- Added outline intake workflow for turning partial outlines into advisor-ready next steps.
- Added citation-candidate extraction utility for Markdown, text, and DOCX outlines.

## 0.1.1 - Taiwan Student Workflow

- Added Traditional Chinese README entrypoint.
- Added Taiwan zero-start writing guide for graduate and professional master's students.
- Added 12-week professional master's first-draft plan.
- Added advisor-review workflow for Word/PDF feedback loops.
- Added competitive positioning notes against LaTeX, Pandoc, Typst, and Word-only templates.
- Updated default placeholder thesis chapters to Traditional Chinese.

## 0.1.0 - Public Candidate

- Added placeholder-only thesis source structure.
- Added DOCX thin-template generation.
- Added body-only DOCX rendering for public demos without private front matter.
- Added style scan, consistency audit, and public-readiness checks.
- Added GitHub Actions render smoke test.
- Added contribution, citation, security, roadmap, and issue-template files.
- Added Traditional Chinese onboarding, Taiwan zero-start guidance, professional master's 12-week plan, advisor-review workflow, and competitive positioning notes.
