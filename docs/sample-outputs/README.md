# Sample Outputs

These are real reports produced by the toolkit from **public placeholder
input only**. They let you see what each workflow produces without cloning or
running anything, and they double as a regression reference (the same commands
in CI regenerate identical content on Linux, macOS, and Windows).

| Report | Produced by | From |
| --- | --- | --- |
| [citation-candidates.md](citation-candidates.md) | `scripts/extract_citation_candidates.py` | [examples/outline-with-citations.md](../../examples/outline-with-citations.md) |
| [concept-tree.md](concept-tree.md) | `scripts/manuscript_concept_audit.py concept-tree` | [examples/concept-drift-sample.md](../../examples/concept-drift-sample.md) |
| [promise-delivery.md](promise-delivery.md) | `scripts/manuscript_concept_audit.py promise-delivery` | [examples/concept-drift-sample.md](../../examples/concept-drift-sample.md) |

## Regenerate

```powershell
python scripts/extract_citation_candidates.py --input examples/outline-with-citations.md --output docs/sample-outputs/citation-candidates.md
python scripts/manuscript_concept_audit.py concept-tree --source examples/concept-drift-sample.md --output docs/sample-outputs/concept-tree.md
python scripts/manuscript_concept_audit.py promise-delivery --source examples/concept-drift-sample.md --concept "數位轉型" --concept "服務流程治理框架" --concept "顧客回應機制" --output docs/sample-outputs/promise-delivery.md
```

All three reports are intentionally cautious: citations are marked
`unverified`, and the concept reports separate evidence (quoted source
sentences) from interpretation. The toolkit surfaces candidates and gaps; the
student and advisor make the scholarly judgement.
