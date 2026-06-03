---
description: Run a strict near-final thesis review before oral defense or submission.
argument-hint: [source path]
allowed-tools: Read, Glob, Grep, Bash(python scripts/manuscript_concept_audit.py:*), Bash(python scripts/thesis_style_scan.py:*), Bash(python scripts/thesis_consistency_audit.py:*), Bash(python scripts/check_public_readiness.py:*)
---

Read:

- `agents/shared/thesis-agent-core.md`
- `agents/shared/student-stage-router.md`
- `agents/shared/command-map.md`

Task:

1. Treat `$ARGUMENTS` as the manuscript source; default to `source/shadow`.
2. Run `python scripts/manuscript_concept_audit.py all --source <source>`.
3. Run `python scripts/thesis_style_scan.py scan`.
4. Run `python scripts/thesis_consistency_audit.py`.
5. Run `python scripts/check_public_readiness.py`.
6. Read the generated reports under `consistency/reports/`.
7. Return a Traditional Chinese oral-defense risk review with four buckets:
   - 必修：會造成研究問題、理論承諾、實證操作、結論回收、引用或公開安全風險。
   - 建議修：會降低說服力，但不一定阻止口試。
   - 可不修：屬於表達或格式偏好。
   - 可答辯處理：可在口試中用限制、範圍或補充說明處理。
8. Quote manuscript evidence or report lines for every mandatory finding.
9. Do not claim DOCX or school-format compliance unless a school template has been checked separately.
