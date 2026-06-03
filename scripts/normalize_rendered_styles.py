from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document


def normalize_docx(path: Path, output: Path | None = None) -> Path:
    doc = Document(path)
    for paragraph in doc.paragraphs:
        if paragraph.style and paragraph.style.name.startswith("Heading"):
            paragraph.paragraph_format.keep_with_next = True
        for run in paragraph.runs:
            if run.font.name is None:
                run.font.name = "Times New Roman"
    target = output or path
    doc.save(target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply generic post-render DOCX style normalization.")
    parser.add_argument("docx", help="Input DOCX path")
    parser.add_argument("--output", help="Optional output DOCX path")
    args = parser.parse_args()

    output = Path(args.output).resolve() if args.output else None
    written = normalize_docx(Path(args.docx).resolve(), output)
    print(f"wrote {written}")


if __name__ == "__main__":
    main()

