from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "source" / "shadow"
DEFAULT_RULES = ROOT / "consistency" / "rules"
DEFAULT_REPORT = ROOT / "consistency" / "reports" / "consistency_audit_report.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_terms(canonical_terms: str) -> list[str]:
    terms: list[str] = []
    for line in canonical_terms.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        candidate = stripped[2:].split(";", 1)[0].split(":", 1)[0].strip(" `")
        if candidate:
            terms.append(candidate)
    return terms


def source_text(source: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(source.glob("*.md")))


def audit(source: Path, rules: Path) -> str:
    text = source_text(source)
    canonical = read_text(rules / "canonical_terms.md")
    chapter_contract = read_text(rules / "chapter_contract.md")
    objectives = read_text(rules / "research_objectives_map.md")

    lines = ["# Consistency Audit Report", ""]
    chapter_count = len(
        re.findall(r"^# (Chapter |第\s*[0-9一二三四五六七八九十]+\s*章)", text, flags=re.MULTILINE)
    )
    lines.append(f"- Chapter headings found: {chapter_count}")

    terms = extract_terms(canonical)
    if terms:
        lines.append("- Canonical term coverage:")
        for term in terms:
            lines.append(f"  - `{term}`: {text.count(term)} occurrence(s)")
    else:
        lines.append("- Canonical term coverage: no terms configured")

    lines.append(f"- Chapter contract configured: {'yes' if chapter_contract.strip() else 'no'}")
    lines.append(f"- Research objectives map configured: {'yes' if objectives.strip() else 'no'}")

    placeholders = re.findall(r"\b(TODO|TBD|FIXME)\b", text, flags=re.IGNORECASE)
    lines.append(f"- Placeholder markers: {len(placeholders)}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a generic thesis consistency audit.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--rules", default=str(DEFAULT_RULES))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.exists():
        raise SystemExit(f"Source not found: {args.source}")
    report = Path(args.report).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(audit(source, Path(args.rules).resolve()), encoding="utf-8")
    print(f"wrote {report}")


if __name__ == "__main__":
    main()
