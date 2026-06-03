# Troubleshooting

## `python` Uses The Wrong Interpreter

Create and activate a local virtual environment before installing dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## DOCX Template Is Missing

Regenerate the thin template.

```powershell
python scripts/create_thin_template_v2.py
```

## Front Matter Source Is Missing

The public demo intentionally does not include private school front matter DOCX files. The render pipeline falls back to body-only DOCX output when `source/front_matter/front_matter_source.docx` is absent.

## PDF Export Fails

PDF export uses Microsoft Word automation and is expected to work only on Windows machines with Word installed. For CI and public demos, use:

```powershell
python scripts/thesis_md_pipeline_v2.py render --skip-pdf
```

## Public Readiness Check Fails

Read the reported file and line number. Remove private paths, credentials, personal identifiers, or unpublished content. If the finding is a false positive, narrow the sample text rather than weakening the check globally.

## Generated Files Appear In Git

Generated deliverables belong under `deliverables/`, reports under `consistency/reports/`, and temporary files under `tmp/`. These are ignored or treated as generated outputs.

