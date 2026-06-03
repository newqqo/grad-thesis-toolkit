# Graduate Thesis Toolkit

[![Render smoke test](https://github.com/newqqo/grad-thesis-toolkit/actions/workflows/render-smoke.yml/badge.svg)](https://github.com/newqqo/grad-thesis-toolkit/actions/workflows/render-smoke.yml)

A clean, reusable workspace for writing, checking, rendering, and packaging a graduate thesis from Markdown source into DOCX/PDF deliverables.

This repository is a public-template candidate. It intentionally contains workflow code and placeholder content only. Personal thesis text, research data, generated deliverables, and private literature PDFs should stay outside the public repository.

## Why This Exists

Most strong thesis repositories are LaTeX, Typst, Pandoc, Quarto, or university-specific templates. This project has a narrower goal: help graduate students who must eventually submit or revise in Microsoft Word, while still keeping the thesis source in plain text and giving AI assistants stable rules for safe editing.

The differentiator is not typography alone. It is the workflow around a thesis:

- stable paragraph IDs for precise edits and review notes
- Markdown chapter sources that can be versioned with Git
- DOCX-first rendering for Word-centered departments
- local consistency rules for terms, chapter responsibilities, and writing boundaries
- style scans for weak academic phrasing and process placeholders
- public-safety defaults that keep private drafts, PDFs, and generated files out of git

## What This Toolkit Is For

- Keep thesis chapters in `source/shadow/*.md`.
- Render a thesis DOCX from a thin Word template.
- Export PDF through Microsoft Word automation on Windows.
- Run consistency and style checks before submission.
- Keep literature notes and source files organized without committing private PDFs.
- Give AI coding assistants a stable workspace structure for thesis editing tasks.

## Compared With Existing Thesis Templates

| Project type | Strength | Gap this toolkit targets |
| --- | --- | --- |
| LaTeX university templates | Best for exact institutional typography and math-heavy theses | Harder for Word-centered review cycles |
| Pandoc/Quarto templates | Excellent multi-format rendering | Often depends on LaTeX/Pandoc stack and generic document flow |
| Typst templates | Fast modern PDF workflow | Less useful when the final revision loop happens in Word |
| Word-only templates | Familiar for students and committees | Weak source control, auditability, and AI-safe editing boundaries |

This toolkit is strongest when the student wants Git/Markdown discipline but cannot avoid DOCX deliverables.

## What Is Not Included

- No real thesis chapters.
- No unpublished paper drafts.
- No raw research data.
- No generated DOCX/PDF submission files.
- No private literature PDFs.
- No personal committee, school, or author metadata.

## Workspace Layout

```text
grad-thesis-toolkit/
├── source/
│   ├── shadow/          # Markdown chapters, controlled by the user
│   ├── layout/          # Rendering/layout directives
│   └── front_matter/    # Optional front matter source files
├── scripts/             # Build, render, audit, and packaging scripts
├── consistency/
│   ├── rules/           # Style, term, and chapter-contract guardrails
│   └── reports/         # Generated audit reports
├── assets/
│   ├── templates/docx/  # Generated or provided DOCX templates
│   ├── library/         # Literature registry placeholders
│   ├── figures/         # Generated figures
│   └── tables/          # Generated tables
└── deliverables/
    ├── docx/            # Generated DOCX files
    └── pdf/             # Generated PDF files
```

## Project Docs

- [Demo guide](docs/demo.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Open-source roadmap](docs/open-source-roadmap.md)
- [OSS readiness notes](docs/oss-readiness.md)
- [Codex for OSS application draft](docs/application-draft.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Citation metadata](CITATION.cff)
- [Changelog](CHANGELOG.md)

## Quick Start

1. Create a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Generate the thin DOCX template.

```powershell
python scripts/create_thin_template_v2.py
```

3. Edit placeholder chapters under `source/shadow/`.

4. Render a DOCX.

```powershell
python scripts/thesis_md_pipeline_v2.py render --skip-pdf
```

5. Run style or consistency checks.

```powershell
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/check_public_readiness.py
```

## Core Commands

```powershell
# Create or refresh the DOCX template
python scripts/create_thin_template_v2.py

# Render a body-only DOCX from placeholder chapters
python scripts/thesis_md_pipeline_v2.py render --skip-pdf

# Render with PDF export on Windows with Microsoft Word installed
python scripts/thesis_md_pipeline_v2.py render

# Check style and consistency reports
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py

# Check whether the public template has obvious private-content risks
python scripts/check_public_readiness.py
```

## Supported Outputs And Limits

Supported now:

- body-only DOCX rendering from placeholder Markdown chapters
- generated thin DOCX template
- public-readiness scan for obvious private-content risks
- style and consistency reports
- GitHub Actions smoke test for placeholder DOCX rendering

Known limits:

- PDF export depends on Microsoft Word automation on Windows.
- The public template does not include private school front matter files.
- Citation rendering is not a full reference-management replacement.
- This is a workflow toolkit, not an official university thesis format.
- Screenshots and release artifacts should be added only after public review.

## AI-Assisted Editing Model

The `source/shadow` format uses stable paragraph markers such as `## p001`. This makes AI-assisted editing less ambiguous:

- ask for edits by chapter and paragraph ID
- keep generated DOCX/PDF files separate from source
- use `consistency/rules` as the durable instruction layer
- run scans before treating a draft as ready

The toolkit is designed to make AI help auditable, not invisible.

## What The CI Smoke Test Proves

The render smoke test checks that a clean checkout can:

1. install Python dependencies,
2. pass the public-readiness scan,
3. run style and consistency audits,
4. render the placeholder DOCX.

It does not prove that a user's customized thesis satisfies any university format requirement.

## Public Release Checklist

- Confirm the MIT license is the intended public license.
- Mark the repository as a GitHub template.
- Add screenshots or a short demo using placeholder content.
- Confirm no real thesis text, private data, or generated submission files are present.
- Confirm all examples use generic names and dummy research topics.
- Add repository topics such as `thesis`, `markdown`, `docx`, `academic-writing`, `graduate-school`, and `research-workflow`.
- Create a first release after the render smoke test passes.
