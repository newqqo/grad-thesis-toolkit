# Competitor Survey And Improvement Backlog 2026

This report summarizes a four-perspective survey of related tools and repositories:

- Taiwan thesis templates, school resources, and graduate-student writing support
- GitHub thesis template and reproducible publishing repositories
- AI literature-review, citation-map, and systematic-review tools
- Static onboarding and first-use UX patterns for non-technical users

## Short Verdict

This project is useful for Taiwan master's students if it is positioned as a thesis workflow operating system, not as another thesis format template and not as a replacement for Elicit, Rayyan, Litmaps, or similar literature-review platforms.

The defensible niche is:

> Help zero-start and professional master's students move from vague topic, advisor feedback, and scattered notes into a traceable, DOCX-first, AI-assisted thesis workflow.

The biggest opportunity is the stage before formatting: students often do not know what they are researching yet, cannot turn a keyword into a literature map, and do not know how to ask an AI agent for help without leaking private text or accepting fake citations.

## Competitive Landscape

| Area | Examples | What they do well | Gap this toolkit can target |
| --- | --- | --- | --- |
| Taiwan thesis templates | [TW_Thesis_Template](https://github.com/sppmg/TW_Thesis_Template), [NTU-Thesis-LaTeX-Template](https://github.com/Hsins/NTU-Thesis-LaTeX-Template) | School-aware LaTeX/Word templates, local formatting context, sample structure | They mainly help after a topic and manuscript direction exist. They do not manage AI-assisted topic discovery, advisor-feedback loops, or evidence traceability. |
| International thesis publishing templates | [pandoc-thesis](https://github.com/cagix/pandoc-thesis), [phd_thesis_markdown](https://github.com/tompollard/phd_thesis_markdown), [academic-pandoc-template](https://github.com/maehr/academic-pandoc-template), [quarto-thesis](https://github.com/nmfs-opensci/quarto-thesis), [thesisdown](https://github.com/ismayc/thesisdown), [oxforddown](https://github.com/ulyngs/oxforddown), [thesis-template-typst](https://github.com/ls1intum/thesis-template-typst), [Dissertate](https://github.com/suchow/Dissertate) | Reproducible writing stacks, strong typography, sample output, automated rendering | Often assume the student can already write in a technical stack and knows the research shape. Less focused on Taiwan Word/PDF advisor review. |
| AI literature-review tools | [Elicit](https://elicit.com/welcome), [SciSpace](https://scispace.com/), [Consensus](https://consensus.app/home/features/research-agent/), [Rayyan](https://help.rayyan.ai/hc/en-us/articles/22697630697617-2-Getting-Started-with-Rayyan-A-Quick-Start-Guide), [ASReview](https://asreview.nl/), [EPPI-Reviewer](https://eppi.ioe.ac.uk/cms/Default.aspx?tabid=3396), [revtools](https://search.r-project.org/CRAN/refmans/revtools/html/revtools.html), [ReviewAid](https://reviewaid.github.io/) | Paper search, screening, extraction, systematic-review workflow, deduplication, AI prioritization | They are stronger than this toolkit at literature discovery. This toolkit should integrate with their outputs, not compete as a live search engine. |
| Citation-map tools | [ResearchRabbit](https://www.researchrabbit.ai/features), [Connected Papers](https://www.connectedpapers.com/index.html), [Litmaps](https://www.litmaps.com/features), [Open Knowledge Maps](https://openknowledgemaps.org/) | Citation networks, visual maps, seed-paper expansion, monitoring new work | They do not turn the map into chapter tasks, Word deliverables, advisor questions, and AI-safe revision rules. |
| Static onboarding patterns | [First Contributions](https://github.com/firstcontributions/first-contributions), [Vite guide](https://vite.dev/guide/), [Docusaurus deployment](https://docusaurus.io/docs/deployment), [JupyterLite GitHub Pages guide](https://jupyterlite.readthedocs.io/en/stable/quickstart/deploy.html) | Clear first action, minimal setup, visible examples, user-friendly paths | This project can improve by making the first 30 minutes concrete for non-technical thesis users. |

## What Competitors Do Better

1. Visual proof: many template projects show screenshots, sample PDFs, or rendered output. This repository still needs stronger visual evidence.
2. Format confidence: Taiwan LaTeX templates can point to school-aware formats. This project must avoid claiming official compliance, but should still document front-matter adapter patterns.
3. Literature discovery: tools such as Elicit, Rayyan, Litmaps, ResearchRabbit, Connected Papers, ASReview, and Open Knowledge Maps are better at search, screening, citation graphs, and extraction.
4. First-click clarity: beginner-facing projects often show one exact first action and one visible result. This repository has improved with `docs/onboarding.html`, first-30-minute checklists, and committed screenshots; a short video walkthrough would still help.
5. Adoption proof: mature projects have visible users, stars, forks, institutional links, or testimonials. This repository currently has simulated first-use feedback, not real student feedback.

## What This Project Can Defend

1. Topic uncertainty support: it routes no-topic, vague-direction, partial-draft, and near-final students differently.
2. Taiwan professional master's context: it acknowledges limited time, work-based topics, and Word/PDF advisor feedback.
3. DOCX-first traceability: stable paragraph IDs and render checks support a Word-centered review cycle without losing source control.
4. Cross-agent operation: Codex, Claude Code, Gemini CLI, Antigravity, and similar agents can follow shared rules instead of one Python-only path.
5. Privacy-first public examples: onboarding and demos avoid uploads, private thesis text, external credentials, and paid-service assumptions.
6. Evidence discipline: citation candidates, source/evidence registry, AI usage log, concept hierarchy checks, and theoretical promise-delivery checks reduce fake citations and unsupported high-level claims.

## Improvement Backlog

### P0: Keep The Boundary Clear

- Keep `docs/onboarding.html` static: no upload, no account, no backend, no external credentials, no network request.
- Add stronger safe/unsafe paste examples so students know how to de-identify thesis text before asking an AI agent for help. Current status: added to `docs/onboarding.html`.
- Avoid all claims of official school-format compliance.
- Avoid claiming that the repository can perform live literature search better than dedicated tools.

### P1: Highest-Value Improvements

1. Add a "first 30 minutes" checklist for each student stage:
   - no topic yet
   - vague keyword
   - partial outline or chapter
   - near-final draft
   Current status: added to the onboarding page; vague-topic workspaces also include `first-30-minutes.md`.
2. Add visual proof:
   - screenshot of the onboarding page
   - screenshot of the generated literature-map workspace
   - screenshot or sample image of the rendered placeholder DOCX
   Current status: onboarding desktop/mobile screenshots are committed under `docs/assets/screenshots/`; a short video or DOCX render visual is still useful.
3. Add an AI usage log and disclosure template:
   - date
   - tool or agent
   - input scope
   - whether private text was removed
   - output used or rejected
   - human verification status
   Current status: generated as `ai-usage-log.md` by `scripts/init_literature_map.py`.
4. Add a source/evidence registry:
   - DOI or URL
   - database or tool used
   - search date
   - verification status
   - evidence quote/page/paragraph
   - matrix fields supported by the source
   Current status: generated as `evidence-registry.csv` by `scripts/init_literature_map.py`.
5. Add a sample advisor-feedback loop:
   - public placeholder Word/PDF comments
   - mapped paragraph IDs
   - AI revision request
   - before/after paragraph
   - consistency checks after revision

### P2: Useful But Larger

1. Import and deduplicate RIS, BibTeX, or Zotero exports into a literature matrix.
2. Generate a simple static citation-map edge list from known seed papers and exported references.
3. Provide school-front-matter adapter documentation using placeholders only.
4. Add a GitHub template action that renders the placeholder DOCX on first use.
5. Add discipline-neutral examples beyond PSC and AI teaching, especially management, education, health administration, and engineering management.

## Student-Value Hypotheses

The project is likely helpful if a student can complete these actions without understanding the whole repository:

| Student stage | Useful first outcome | Evidence needed |
| --- | --- | --- |
| No topic yet | A short advisor-discussion memo with possible research directions and method choices | Simulated and real first-use feedback |
| Vague keyword | A seed-paper plan, search strategy, literature matrix, and gap radar | Example topic workspace and source registry |
| Partial draft | Citation-candidate list, concept drift report, and chapter-level repair plan | Placeholder outline and manuscript audit outputs |
| Near-final draft | Oral-defense risk list split into mandatory fixes, recommended fixes, optional polish, and defensible answers | Near-final review example using placeholder chapters |

## Application Implication

For an open-source support application, the best argument is not "we have a complete thesis-writing AI." The stronger argument is:

> Existing public tools are strong at formatting or literature discovery. This repository covers the missing workflow layer for Taiwan students who need agent-assisted topic formation, source discipline, DOCX review loops, and privacy-safe thesis operations.

This remains a new project with limited adoption evidence. The next proof should come from screenshots, a short demo, and feedback from real Taiwan graduate students or advisors.
