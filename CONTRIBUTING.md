# Contributing

Thank you for considering a contribution to the Graduate Thesis Workflow Toolkit. This project is intended to become a reusable, public workflow toolkit for graduate research writing, review, and reproducibility. Contributions should keep the repository generic, privacy-conscious, and useful across disciplines.

## Contribution Principles

- Keep examples generic and reusable.
- Do not add private documents, unpublished research text, personal identifiers, institution-specific material, or sensitive data.
- Prefer small, focused changes that are easy to review.
- Document assumptions when adding workflow behavior or templates.
- Keep public-facing language neutral and beginner-friendly.

## Before Opening a Pull Request

1. Review the current documentation and confirm your change fits the public toolkit scope.
2. Use placeholder content for examples unless a public sample has been explicitly approved.
3. Run the relevant local checks for the files you changed.
4. Remove generated files, caches, temporary outputs, and local paths unless they are intentionally part of the contribution.
5. Confirm the change does not include private research data or personal information.
6. Use the [privacy review checklist](docs/privacy-review-checklist.md) before adding examples, demo files, or release assets.

## Running The Tests

The toolkit ships a `pytest` suite that covers the privacy scan, citation
extraction, agent-adapter integrity, concept-audit primitives, and an
end-to-end DOCX render. Run it on any platform (no Microsoft Word required):

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

CI runs the same suite on Linux and Windows, plus a workflow smoke test on
Linux, macOS, and Windows. Please keep the suite green and add a test when you
change script behaviour.

## Pull Request Checklist

- [ ] The change has a clear public-purpose description.
- [ ] Documentation has been updated when behavior or workflow expectations changed.
- [ ] Examples use placeholder or public sample content only.
- [ ] No private files, local absolute paths, credentials, or identifiers were added.
- [ ] The relevant local checks were run, or the reason they were not run is stated.

## Issues

Use issues for bug reports, documentation gaps, reproducible workflow problems, and feature proposals. Include enough context for maintainers to reproduce or evaluate the request, but do not include private writing samples, unpublished research details, or sensitive project files.

## Code of Conduct

This repository expects respectful, constructive collaboration. Comments and reviews should focus on the technical, documentation, or workflow concern being discussed. Harassment, personal attacks, and disclosure of private information are not acceptable.

## Maintainer Notes

Before accepting contributions, maintainers should verify that the change strengthens the project as a reusable open-source toolkit and does not depend on private context. Changes that require project-specific data should be redesigned around placeholders, fixtures, or documented extension points.
