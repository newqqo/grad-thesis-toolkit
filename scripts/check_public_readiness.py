from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BLOCKLIST = [
    r"C:\\Users\\[^\\]+",
    r"C:\\\\Users\\\\[^\\]+",
    r"/Users/[^/]+",
    r"\\/Users\\/[^\\/]+",
    r"C:\\Code",
    r"C:\\\\Code",
    r"C:/Code",
    r"thesis-workspace",
    r"Date of Birth",
    r"contact number",
    r"passport",
    r"\bphone\b",
    r"\b(contact|home|mailing)[_-]?\s*address\b",
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
    r"\bapi[_-]?key\b",
    r"\bsecret\b",
    r"\b(access|refresh|auth)[_-]?token\b",
    r"\bpassword\b",
]

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "deliverables",
    "tmp",
    "packages",
}

SKIP_SUFFIXES = {
    ".docx",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pyc",
}


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.name == "check_public_readiness.py":
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        files.append(path)
    return sorted(files)


def scan(root: Path, patterns: list[str]) -> list[tuple[Path, int, str, str]]:
    compiled = [(pattern, re.compile(pattern, flags=re.IGNORECASE)) for pattern in patterns]
    findings: list[tuple[Path, int, str, str]] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for label, regex in compiled:
                if regex.search(line):
                    findings.append((path, line_no, label, line.strip()[:180]))
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan the template for obvious private-content risks.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--extra-pattern", action="append", default=[])
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = scan(root, DEFAULT_BLOCKLIST + list(args.extra_pattern))
    if findings:
        print("Public readiness check failed:")
        for path, line_no, pattern, preview in findings:
            print(f"- {path.relative_to(root)}:{line_no} matched `{pattern}`: {preview}")
        raise SystemExit(1)
    print("Public readiness check passed.")


if __name__ == "__main__":
    main()
