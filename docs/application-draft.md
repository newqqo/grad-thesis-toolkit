# Codex For Open Source Application Draft

This draft is written for a public open-source support application. Replace repository URL and maintainer details after the public repository is created.

## Project Name

Graduate Thesis Workflow Toolkit

## Short Description

A DOCX-first graduate thesis workflow toolkit for Taiwan students, especially professional master's students starting from zero. It helps students move from a vague keyword to a literature map, then to research questions, Markdown chapters, Word deliverables, consistency checks, and AI-auditable revisions.

## Problem

Graduate students often work across Markdown notes, Word drafts, advisor feedback, reference files, generated figures, and final DOCX/PDF deliverables. Existing open templates are strong in LaTeX, Typst, Pandoc, and Quarto, but many students still need a Word-centered workflow because their department, advisor, or committee reviews in DOCX.

The missing layer is not only formatting. Students need a repeatable workspace that separates source from generated files, prevents accidental publication of private material, and makes AI edits traceable instead of opaque.

For Taiwan professional master's students, the starting problem is often earlier than formatting: turning work experience into a researchable topic, building chapter structure, keeping advisor feedback organized, and producing a reviewable Word draft while working full time.

Many students begin with only a vague keyword, such as PSC, ESG, AI teaching, or digital transformation. They need a guided way to find seed papers, map research clusters, identify domestic/international gaps, and decide where they can stand academically.

## Proposed Solution

This toolkit provides a public, placeholder-first thesis workspace with:

- Markdown chapter source under stable paragraph IDs
- DOCX rendering through a generated thin Word template
- consistency rules for chapter responsibilities, canonical terms, and writing style
- Traditional Chinese onboarding for Taiwan zero-start and professional master's workflows
- a vague-topic-to-literature-map initializer that creates a topic brief, search plan, seed-paper list, literature matrix, gap radar, advisor questions, and AI prompts
- an outline intake workflow that extracts citation candidates before structural rewriting, so students can verify evidence before expanding claims
- a reusable AI research partner playbook and Traditional Chinese prompt template for guided menus, pressure tests, literature mapping, and chapter-level writing tasks
- advisor-review workflow guidance for Word/PDF feedback loops
- style and public-readiness checks
- GitHub Actions smoke testing for placeholder DOCX rendering
- contribution and security rules that discourage private thesis text, credentials, and personal data from entering the public repo

## Public Scope

- reusable workflow templates for graduate research writing
- Taiwan-focused zero-start writing guides in Traditional Chinese
- literature mapping workflow for students who only have a keyword
- outline intake and citation-candidate extraction for students who already have a partial plan
- prompt templates that keep AI assistance skeptical, source-aware, and advisor-reviewable
- a public-safe Taiwan professional master's mini sample that demonstrates topic narrowing, matrix setup, gap radar, advisor feedback tracking, and chapter tasks
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

The repository is a public candidate at version 0.1.2. The core placeholder workflow runs locally and in CI: public readiness check, style scan, consistency audit, DOCX template generation, DOCX rendering, literature-map initialization, and outline citation-candidate extraction. The next maturity step is collecting feedback from Taiwan students and adding a stronger sample project with screenshots.

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
- Current release: 0.1.2 literature map and research partner workflow
- Public demo: `python scripts/run_demo.py`
