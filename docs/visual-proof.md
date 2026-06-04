# Visual Proof

This page collects public-safe visual evidence for reviewers and new users. All screenshots use placeholder workflow content only.

## Static Onboarding Wizard

The onboarding page is a static guide layer for first-time students. It does not upload files, store content, call a backend, or depend on paid services.

Desktop view:

![Desktop onboarding screenshot](assets/screenshots/onboarding-v0.1.8-desktop.png)

Mobile view:

![Mobile onboarding screenshot](assets/screenshots/onboarding-v0.1.8-mobile.png)

Light-mode accessibility view:

![Light-mode onboarding screenshot](assets/screenshots/onboarding-v0.1.9-light.png)

The screenshots show the "vague direction" student path with:

- first-30-minute outcomes
- safe and unsafe examples for de-identified AI collaboration
- copyable agent prompt
- optional local command
- links to matching repository docs
- keyboard/screen-reader focus landing on the answer panel
- light-mode contrast for safe/unsafe and "do not do this yet" guidance

## Public Demo Outputs

The public demo can be run locally:

```powershell
python scripts/run_demo.py
```

It produces:

- `literature/psc/first-30-minutes.md`
- `literature/psc/evidence-registry.csv`
- `literature/psc/ai-usage-log.md`
- `consistency/reports/citation_candidates.md`
- `consistency/reports/concept_hierarchy_report.md`
- `consistency/reports/promise_delivery_report.md`
- `deliverables/docx/thesis_render_v2_latest.docx`

The v0.1.9 release also includes a public placeholder DOCX artifact:

- [v0.1.9 Onboarding Accessibility](https://github.com/newqqo/grad-thesis-toolkit/releases/tag/v0.1.9)

## Verification

The latest local verification for v0.1.9:

- `python -m pytest -q`: 49 tests passed
- `python scripts/check_public_readiness.py`: passed
- `python scripts/check_agent_adapters.py`: passed
- `python scripts/run_demo.py`: passed
- onboarding browser smoke check: answer-panel focus handoff verified; console clean; light-mode screenshot captured

The repository also runs cross-platform GitHub Actions on Linux, macOS, and Windows.
