# Privacy Review Checklist

Use this checklist before committing examples, demo files, release assets, or generated reports.

## Do Not Commit

- real thesis chapters or unpublished paper drafts
- private literature PDFs
- interview transcripts, survey responses, meeting notes, or raw data
- student, advisor, school, employer, vessel, patient, customer, or participant identifiers
- credentials, API keys, access tokens, passwords, cookies, or local config files
- local absolute paths from a personal user directory
- generated reports that contain private file paths or private document titles
- institution-specific forms unless they are public and redistribution is allowed

## Public-Safe Examples

Good examples use:

- placeholder student and advisor names
- fictional or generic topics
- unverified citation placeholders clearly marked as `candidate` or `unverified`
- public URLs only when redistribution is acceptable
- generated DOCX outputs that contain placeholder content only

## Required Checks

Run:

```powershell
python scripts/check_public_readiness.py
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
```

For outline or literature examples, also run:

```powershell
python scripts/extract_citation_candidates.py --input examples/outline-with-citations.md
```

## Reviewer Questions

1. Could this example reveal a real student, advisor, employer, school process, dataset, or unpublished research direction?
2. Does any generated file contain a local path?
3. Are all citation-like claims either verified or marked as unverified candidates?
4. Would a contributor understand that this toolkit is not an official school format?
5. Can the example be reused by another student without knowing the original private project?
