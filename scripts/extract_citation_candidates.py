from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
AUTHOR_YEAR_RE = re.compile(
    r"\b([A-Z][A-Za-z'\-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'\-]+|(?:\s+et\s+al\.)?)?)\s*"
    r"[\(\[]\s*((?:19|20)\d{2}[a-z]?)\s*[\)\]]"
)
ZH_AUTHOR_YEAR_RE = re.compile(r"([\u4e00-\u9fff]{2,6})(?:等|、[\u4e00-\u9fff]{2,6})?[（(]((?:19|20)\d{2})[）)]")
BRACKET_YEAR_RE = re.compile(r"「([^」]{4,160})」\s*[（(]((?:19|20)\d{2})[）)]")


def read_input(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        from docx import Document

        doc = Document(path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    raise SystemExit(f"Unsupported input file type: {path.suffix}")


def line_context(text: str, start: int) -> tuple[int, str]:
    line_no = text.count("\n", 0, start) + 1
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", start)
    if line_end == -1:
        line_end = len(text)
    return line_no, text[line_start:line_end].strip()


def collect_candidates(text: str) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    patterns = [
        ("doi", DOI_RE),
        ("author-year", AUTHOR_YEAR_RE),
        ("zh-author-year", ZH_AUTHOR_YEAR_RE),
        ("title-year", BRACKET_YEAR_RE),
    ]
    for kind, regex in patterns:
        for match in regex.finditer(text):
            raw = match.group(0).strip()
            line_no, context = line_context(text, match.start())
            key = (kind, raw.lower(), str(line_no))
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                {
                    "kind": kind,
                    "candidate": raw,
                    "line": str(line_no),
                    "context": context,
                }
            )
    return sorted(candidates, key=lambda item: int(item["line"]))


def render_markdown(candidates: list[dict[str, str]], source: Path) -> str:
    try:
        # Use POSIX separators so reports are identical across Linux/macOS/Windows.
        display_source = source.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        display_source = source.name
    lines = [
        "# Citation Candidate Report",
        "",
        f"Source: `{display_source}`",
        "",
        "This report identifies possible citations. It does not verify that the references are real.",
        "",
        "| Status | Type | Candidate | Line | Context |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for item in candidates:
        candidate = item["candidate"].replace("|", "\\|")
        context = item["context"].replace("|", "\\|")
        lines.append(f"| unverified | {item['kind']} | {candidate} | {item['line']} | {context} |")
    if not candidates:
        lines.append("| none | none | No citation candidates found. |  |  |")
    lines.extend(
        [
            "",
            "## Recommended Next Step",
            "",
            "Verify each candidate by DOI, title, author, year, and source database before writing it into the thesis.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract possible citation strings from an outline or draft.")
    parser.add_argument("--input", required=True, help="Input .md, .txt, or .docx file")
    parser.add_argument("--output", default="", help="Output markdown report path")
    args = parser.parse_args()

    source = Path(args.input).resolve()
    if not source.exists():
        raise SystemExit(f"Input file not found: {args.input}")
    text = read_input(source)
    candidates = collect_candidates(text)
    report = render_markdown(candidates, source)

    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(f"wrote {output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
