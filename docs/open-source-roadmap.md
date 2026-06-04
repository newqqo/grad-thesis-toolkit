# Open Source Roadmap

This roadmap describes the work needed to make the Graduate Thesis Workflow Toolkit credible as a public open-source project. It uses generic placeholders only and should be updated as maintainers make publication decisions.

## Phase 1: Public Scope

- Define the toolkit audience, supported workflows, and non-goals.
- Keep the Taiwan zero-start/professional master's student use case visible in public docs.
- Keep the vague-topic-to-literature-map workflow central to the student journey.
- Keep citation verification and source traceability as explicit AI-use guardrails.
- Keep concept hierarchy and promise-delivery checks tied to manuscript evidence.
- Keep agent adapters thin and tied to the shared core rules.
- Keep the static onboarding wizard as a guide layer only: no upload, backend, external credentials, paid-service dependency, or private thesis intake.
- Replace private examples with generic fixtures and placeholder documents.
- Confirm that scripts, docs, and templates do not rely on local absolute paths.
- Keep the root license current and consistent with `CITATION.cff`.
- Document what generated outputs should and should not be committed.

## Phase 2: Trust and Safety

- Maintain the privacy review checklist for new examples and demo materials.
- Document expected handling for private research content.
- Add safe/unsafe AI paste examples and de-identification prompts for thesis excerpts. Current status: present in `docs/onboarding.html`.
- Add an AI usage log template for agent-assisted writing and literature work. Current status: generated in each new literature-map workspace.
- Add security reporting instructions with a real maintainer contact.
- Confirm dependency files are current and do not include unnecessary packages.
- Add a lightweight release checklist for tagged versions.

## Phase 3: Contributor Readiness

- Publish contribution guidelines and issue templates. Current status: issue templates are present.
- Add a small public demo that runs on placeholder content. Current status: `python scripts/run_demo.py` renders public-safe placeholder content.
- Maintain the static onboarding wizard and add first-30-minute checklists for each student stage. Current status: present in `docs/onboarding.html`; vague-topic workspaces also generate `first-30-minutes.md`.
- Add Traditional Chinese examples for topic framing, chapter planning, and advisor feedback.
- Add outline-intake examples that show when to verify citations before rewriting.
- Add more concept-audit examples for qualitative, quantitative, and mixed-method theses.
- Expand topic examples beyond the current PSC and professional-master mini samples. Current status: v0.1.5 adds an AI teaching first-use sample.
- Add usage notes from students or advisors using different agents. Current status: v0.1.5 includes simulated first-use feedback; real user feedback remains needed.
- Document setup, verification, and troubleshooting steps.
- Define maintainer review expectations for pull requests.
- Add a citation file and basic project metadata.

## Phase 4: Reproducibility

- Provide a minimal sample project with placeholder inputs and expected outputs.
- Provide a Taiwan professional master's starter pack with no private school forms or personal data.
- Provide screenshots or a short screen recording of the literature-map and DOCX-render demo.
- Add a source/evidence registry that can track DOI or URL, database/tool, search date, verification status, and supporting quote/page/paragraph. Current status: generated in each new literature-map workspace.
- Add a sample advisor-feedback loop with placeholder comments, paragraph IDs, before/after revision, and post-revision checks.
- Document any required runtime assumptions.
- Add automated checks for formatting, generated artifacts, and privacy-sensitive strings where practical.
- Keep generated deliverables separate from reusable source material.
- Capture known limitations and planned improvements.

## Publication Gate

Before publishing, maintainers should confirm:

- [ ] The repository contains no private writing, data, credentials, or personal identifiers.
- [ ] All examples are placeholders or approved public samples.
- [ ] Public documentation explains setup, usage, contribution, security, and citation.
- [ ] The license is present and documented.
- [ ] The demo workflow can be completed in a clean environment.
- [ ] At least one public release includes a placeholder DOCX artifact and documented zero-start workflow.
- [ ] A public first-use page explains what students can do without external credentials, paid services, uploads, or private text exposure.
- [x] A competitor survey and backlog explain why the project targets workflow orchestration rather than official formatting or live literature search.
