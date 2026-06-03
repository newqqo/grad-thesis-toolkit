#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

WORKSPACE = Path(__file__).resolve().parents[1]
PACKAGES_DIR = WORKSPACE / "packages"

INCLUDE_PATHS = [
    WORKSPACE / "AGENTS.md",
    WORKSPACE / "README.md",
    WORKSPACE / "USER_GUIDE.md",
    WORKSPACE / "requirements.txt",
    WORKSPACE / "source",
    WORKSPACE / "scripts",
    WORKSPACE / "consistency",
    WORKSPACE / "assets" / "templates",
    WORKSPACE / "assets" / "library" / "README.md",
    WORKSPACE / "assets" / "library" / "entries",
    WORKSPACE / "assets" / "library" / "registry",
    WORKSPACE / "assets" / "library" / "reports",
    WORKSPACE / "assets" / "library" / "inbox" / "README.md",
    WORKSPACE / "assets" / "library" / "inbox" / "pdfs" / "README.md",
    WORKSPACE / "assets" / "library" / "files" / "pdfs" / "README.md",
]

EXCLUDE_PREFIXES = [
    WORKSPACE / ".git",
    WORKSPACE / "archive",
    WORKSPACE / "deliverables",
    WORKSPACE / "packages",
    WORKSPACE / "assets" / "library" / "files" / "pdfs",
    WORKSPACE / "assets" / "library" / "inbox" / "pdfs",
]

ALWAYS_INCLUDE = {
    WORKSPACE / "assets" / "library" / "inbox" / "pdfs" / "README.md",
    WORKSPACE / "assets" / "library" / "files" / "pdfs" / "README.md",
}


def is_excluded(path: Path) -> bool:
    if path in ALWAYS_INCLUDE:
        return False
    return any(prefix == path or prefix in path.parents for prefix in EXCLUDE_PREFIXES)


def collect_files() -> list[Path]:
    files: list[Path] = []
    for target in INCLUDE_PATHS:
        if not target.exists():
            continue
        if target.is_file():
            if not is_excluded(target):
                files.append(target)
            continue
        for path in sorted(target.rglob("*")):
            if not path.is_file():
                continue
            if is_excluded(path):
                continue
            if "__pycache__" in path.parts:
                continue
            if path.suffix in {".pyc", ".pyo"}:
                continue
            files.append(path)
    return sorted(set(files))


def default_output() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return PACKAGES_DIR / f"workspace-core-{stamp}.zip"


def summarize(files: list[Path]) -> dict[str, object]:
    total_bytes = sum(path.stat().st_size for path in files)
    return {
        "workspace": str(WORKSPACE),
        "output_dir": str(PACKAGES_DIR),
        "file_count": len(files),
        "size_mb": round(total_bytes / (1024 * 1024), 2),
    }


def write_zip(output_path: Path, files: list[Path]) -> None:
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED, compresslevel=6) as zf:
        for path in files:
            zf.write(path, arcname=path.relative_to(WORKSPACE))


def main() -> int:
    parser = argparse.ArgumentParser(description="Package the lightweight thesis workspace core for transfer.")
    parser.add_argument("--output", type=Path, help="Zip output path. Defaults to packages/workspace-core-<timestamp>.zip")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be packaged without writing a zip")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the output file if it already exists")
    args = parser.parse_args()

    files = collect_files()
    summary = summarize(files)
    if args.dry_run:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    output_path = (args.output or default_output()).resolve()
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"output already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_zip(output_path, files)
    summary["output"] = str(output_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
