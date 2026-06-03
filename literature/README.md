# Literature Map Workspaces

This folder is for topic-specific literature map workspaces.

Create a workspace from a vague topic:

```powershell
python scripts/init_literature_map.py --topic "PSC" --domain-hint "port state control / maritime safety"
```

Each generated workspace contains:

- `topic-brief.md`
- `search-plan.md`
- `seed-papers.md`
- `literature-matrix.csv`
- `gap-radar.md`
- `advisor-questions.md`
- `ai-prompts.md`

Use these files to move from a vague keyword to a researchable thesis direction.
