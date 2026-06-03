# Codex For Open Source Application Draft

This draft is written for a public open-source support application. Replace repository URL and maintainer details after the public repository is created.

## Project Name

Graduate Thesis Workflow Toolkit

## Short Description

A DOCX-first graduate thesis workflow toolkit for Taiwan students, especially professional master's students starting from zero. It lets students write thesis chapters in plain Markdown, render Word deliverables, run consistency checks, and keep AI-assisted revisions auditable through stable paragraph IDs and reusable rules.

## Problem

Graduate students often work across Markdown notes, Word drafts, advisor feedback, reference files, generated figures, and final DOCX/PDF deliverables. Existing open templates are strong in LaTeX, Typst, Pandoc, and Quarto, but many students still need a Word-centered workflow because their department, advisor, or committee reviews in DOCX.

The missing layer is not only formatting. Students need a repeatable workspace that separates source from generated files, prevents accidental publication of private material, and makes AI edits traceable instead of opaque.

For Taiwan professional master's students, the starting problem is often earlier than formatting: turning work experience into a researchable topic, building chapter structure, keeping advisor feedback organized, and producing a reviewable Word draft while working full time.

## Proposed Solution

This toolkit provides a public, placeholder-first thesis workspace with:

- Markdown chapter source under stable paragraph IDs
- DOCX rendering through a generated thin Word template
- consistency rules for chapter responsibilities, canonical terms, and writing style
- Traditional Chinese onboarding for Taiwan zero-start and professional master's workflows
- advisor-review workflow guidance for Word/PDF feedback loops
- style and public-readiness checks
- GitHub Actions smoke testing for placeholder DOCX rendering
- contribution and security rules that discourage private thesis text, credentials, and personal data from entering the public repo

## Public Scope

- reusable workflow templates for graduate research writing
- Taiwan-focused zero-start writing guides in Traditional Chinese
- placeholder examples that demonstrate structure without private content
- documentation for setup, contribution, security, citation, and troubleshooting
- reproducibility checks for local scripts and generated outputs
- a public demo path that can render a placeholder thesis DOCX

## Non-Goals

- Hosting private thesis drafts or unpublished research data.
- Replacing institutional review, advisor feedback, or disciplinary methods.
- Providing discipline-specific claims, datasets, or analysis results.
- Storing credentials, personally identifying information, or confidential documents.

## Intended Users

- Taiwan graduate and professional master's students who need a reusable thesis workflow structure.
- Students starting from topic uncertainty rather than from an existing LaTeX template.
- Advisors or lab groups preparing generic onboarding material.
- Maintainers evaluating workflow automation for academic writing projects.
- Open-source contributors improving documentation, templates, and reproducibility checks.

## Project Maturity

The repository is a public candidate at version 0.1.0. The core placeholder workflow runs locally and in CI: public readiness check, style scan, consistency audit, DOCX template generation, and DOCX rendering. The next maturity step is collecting feedback from Taiwan students and adding a stronger sample project with screenshots.

## Risks and Mitigations

- Risk: Private content is accidentally added.
  Mitigation: Use placeholder fixtures, contribution checks, and explicit privacy review steps.

- Risk: Workflow examples are too project-specific.
  Mitigation: Keep examples discipline-neutral and document extension points.

- Risk: Users misinterpret templates as institutional requirements.
  Mitigation: State that templates are examples and should be adapted to local requirements.

## Success Criteria

- a new user can understand the repository purpose within a few minutes
- the demo workflow runs using placeholder content only
- contributors have clear expectations for safe, public changes
- the repository has documented contribution, security, citation, troubleshooting, and roadmap materials
- CI verifies the placeholder DOCX render on every pull request

## Placeholder Submission Details

- Repository URL: `https://github.com/newqqo/grad-thesis-toolkit`
- License: MIT
- Current release: 0.1.0 public candidate
- Public demo: `python scripts/thesis_md_pipeline_v2.py render --skip-pdf`
