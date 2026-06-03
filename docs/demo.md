# Demo Guide

This demo uses the placeholder thesis already included in `source/shadow`. It does not require private documents, unpublished research details, credentials, or institution-specific files.

## Demo Goal

Show how a user can organize a sample graduate writing project, run workflow checks, and render a DOCX output using neutral placeholder material.

## Prerequisites

- Python 3.11 or newer
- Dependencies from `requirements.txt`
- Microsoft Word is only required for PDF export, not for the body-only DOCX demo

## Run The Demo

To run the whole public-safe demo in one command:

```powershell
python scripts/run_demo.py
```

Or run the two parts manually.

### A. Zero-Start Research Workflow

```powershell
python scripts/init_literature_map.py --topic "PSC" --domain-hint "port state control / maritime safety" --overwrite
python scripts/extract_citation_candidates.py --input examples/outline-with-citations.md --output consistency/reports/citation_candidates.md
python scripts/manuscript_concept_audit.py all --source examples/concept-drift-sample.md --concept 數位轉型 --concept 服務流程治理框架 --concept 顧客回應機制
```

Expected output:

- `literature/psc/topic-brief.md`
- `literature/psc/search-plan.md`
- `literature/psc/seed-papers.md`
- `literature/psc/literature-matrix.csv`
- `literature/psc/gap-radar.md`
- `literature/psc/advisor-questions.md`
- `literature/psc/ai-prompts.md`
- `consistency/reports/citation_candidates.md` (generated report, ignored by git)
- `consistency/reports/concept_hierarchy_report.md` (generated report, ignored by git)
- `consistency/reports/promise_delivery_report.md` (generated report, ignored by git)

This part demonstrates how a student moves from a vague keyword to a structured literature-map workspace, treats outline citations as unverified candidates, and checks whether manuscript concepts remain consistent across chapters.

### B. DOCX Render Workflow

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

python scripts/check_public_readiness.py
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/create_thin_template_v2.py
python scripts/thesis_md_pipeline_v2.py render --skip-pdf
```

Expected output:

- `assets/templates/docx/thesis_template_thin.docx`
- `deliverables/docx/thesis_render_v2_latest.docx`
- `consistency/reports/style_scan_report.md`
- `consistency/reports/consistency_audit_report.md`

## Demo Script

Use this structure for a short recorded or live walkthrough:

- "This repository demonstrates a reusable graduate thesis workflow toolkit."
- "The demo uses placeholder content only."
- "A student can start from a vague keyword, create a literature-map workspace, and identify what must be verified before writing."
- "A student can run concept hierarchy and promise-delivery checks before asking an advisor to review a draft."
- "Markdown chapters use stable paragraph IDs so AI edits can be requested and reviewed precisely."
- "Source material, generated deliverables, documentation, and temporary files are separated."
- "The workflow renders a DOCX output without committing private generated files."
- "Before publishing or contributing, users run a public-readiness scan."

## Verification Checklist

- [ ] The demo runs in a clean environment.
- [ ] All example content is generic.
- [ ] Outputs are easy to distinguish from source files.
- [ ] Generated files that should not be committed are ignored or documented.
- [ ] The demo does not require private credentials or local-only paths.

## Known Gaps

- The public demo currently renders body-only DOCX output.
- PDF export depends on Microsoft Word automation on Windows.
- Screenshots should be added after the first public release is reviewed.
