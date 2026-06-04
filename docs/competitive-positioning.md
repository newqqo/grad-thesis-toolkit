# Competitive Positioning

For the detailed 2026 survey across Taiwan thesis resources, GitHub thesis templates, AI literature-review tools, citation-map tools, and onboarding patterns, see [Competitor Survey And Improvement Backlog 2026](competitor-survey-2026.md).

## Short Answer

This repository is not competitive as a pure thesis format template. Taiwan already has stronger LaTeX-oriented thesis templates and school-specific formats.

It becomes competitive when positioned as a thesis workflow operating system for students who:

- start from topic uncertainty,
- need to produce Word/DOCX drafts,
- receive advisor feedback in Word or PDF,
- want AI assistance without losing traceability,
- need privacy guardrails before publishing or collaborating.

The most defensible gap is the stage before formatting: a student may only have a vague keyword, no stable research question, no literature map, and no safe way to ask an AI agent for help.

## Existing Strengths In The Ecosystem

Taiwan and international thesis repositories tend to be strong in these areas:

- exact LaTeX typography and university formatting,
- Overleaf-friendly workflows,
- release downloads,
- sample PDFs,
- school-specific front matter,
- citation and table/figure automation.

Examples include Taiwan-focused LaTeX templates such as `sppmg/TW_Thesis_Template`, NTU/NYCU/NCKU templates, and international Markdown/Pandoc/Typst projects.

## Patterns Worth Learning From

- `sppmg/TW_Thesis_Template`: strong Taiwan onboarding, multi-school awareness, and explicit user guidance.
- `Hsins/NTU-Thesis-LaTeX-Template` and `coldwufish/NYCU-thesis-template`: clear local thesis-format context and examples.
- `cagix/pandoc-thesis`: reproducible Markdown-to-output workflow with automation.
- Literature-review matrix and systematic-review tools: structured matrices, source verification gates, and exportable artifacts.

This project should borrow the onboarding and reproducibility patterns, not the claim of official formatting compliance.

It should also integrate with literature-review and citation-map tools rather than claim to replace them. Tools such as Elicit, Rayyan, ASReview, Litmaps, ResearchRabbit, Connected Papers, and Open Knowledge Maps are stronger at search, screening, extraction, and citation-network exploration. This repository should turn those outputs into chapter tasks, source registries, advisor questions, and DOCX review loops.

## Gap This Project Targets

Many Taiwan professional master's students do not begin with LaTeX or a reproducible publishing stack. They begin with:

- a practical work problem,
- limited weekly writing time,
- uncertainty about research method,
- advisor feedback through Word/PDF,
- pressure to turn experience into a structured thesis.

This project targets that beginning stage.

## Competitive Claims We Can Defend

- DOCX-first workflow instead of LaTeX-first formatting.
- Traditional Chinese onboarding for Taiwan students.
- Stable paragraph IDs for precise AI and advisor feedback.
- Explicit privacy/public-readiness checks.
- CI smoke test that proves the placeholder thesis can render.
- Literature-map workspace generation from a vague keyword.
- Citation-candidate extraction before outline rewriting.
- Concept hierarchy and promise-delivery checks grounded in manuscript sentences.
- Research-partner prompt/playbook that requires verification and advisor-facing next steps.
- Cross-agent adapters that turn the workflow into reusable agent behavior rather than Python-only scripts.
- Template repository and release artifact for quick adoption.
- Static onboarding wizard that stays offline, requires no upload, and does not assume API keys or paid services.

## Claims We Should Avoid

- Do not claim official university format compliance.
- Do not claim to replace LaTeX thesis templates.
- Do not claim to replace dedicated literature-search, citation-map, or systematic-review platforms.
- Do not claim AI can write a valid thesis from zero.
- Do not claim suitability for all disciplines.

## Next Improvements

1. Add screenshots of the placeholder DOCX output.
2. Add a sample `老師回饋清單` fixture.
3. Add a small `examples/tw-professional-master` sample project.
4. Add school-front-matter adapter documentation without committing private school forms.
5. Add a short video or GIF demo of edit -> check -> render.
6. Collect feedback from at least 3 Taiwan graduate students or advisors.
7. Add source/evidence registry and AI usage log templates for traceable literature work.
8. Add a first-30-minute checklist for each student stage in the onboarding page.
