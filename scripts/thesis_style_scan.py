from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "source" / "shadow"
DEFAULT_REPORT = ROOT / "consistency" / "reports" / "style_scan_report.md"


WATCH_PATTERNS = {
    "vague claims": [
        r"\bmay be\b",
        r"\bpossibly\b",
        r"\bseems\b",
        r"\bgenerally\b",
    ],
    "unsupported emphasis": [
        r"\bvery important\b",
        r"\bobviously\b",
        r"\bclearly\b",
    ],
    "process placeholders": [
        r"\bTODO\b",
        r"\bTBD\b",
        r"\bFIXME\b",
    ],
}


def iter_markdown_files(source: Path) -> list[Path]:
    return sorted(path for path in source.glob("*.md") if path.is_file())


def scan_file(path: Path) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        for label, patterns in WATCH_PATTERNS.items():
            if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in patterns):
                hits.append((label, line_no, line.strip()))
    return hits


def build_report(source: Path) -> str:
    lines = ["# Style Scan Report", ""]
    total = 0
    for path in iter_markdown_files(source):
        hits = scan_file(path)
        if not hits:
            continue
        rel = path.relative_to(ROOT)
        lines.extend([f"## {rel}", ""])
        for label, line_no, line in hits:
            total += 1
            preview = line[:180]
            lines.append(f"- `{label}` at line {line_no}: {preview}")
        lines.append("")
    if total == 0:
        lines.append("No style watch items found.")
    else:
        lines.insert(2, f"Total watch items: {total}")
        lines.insert(3, "")
    return "\n".join(lines).rstrip() + "\n"


def cmd_scan(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    report = Path(args.report).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(build_report(source), encoding="utf-8")
    print(f"wrote {report}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan thesis Markdown files for generic style watch items.")
    sub = parser.add_subparsers(dest="cmd")
    scan = sub.add_parser("scan")
    scan.add_argument("--source", default=str(DEFAULT_SOURCE))
    scan.add_argument("--report", default=str(DEFAULT_REPORT))
    scan.set_defaults(func=cmd_scan)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()

