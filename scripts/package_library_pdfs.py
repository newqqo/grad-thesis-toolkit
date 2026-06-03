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


def collect_files(include_inbox: bool) -> list[Path]:
    files: list[Path] = []
    roots = [WORKSPACE / "assets" / "library" / "files" / "pdfs"]
    if include_inbox:
        roots.append(WORKSPACE / "assets" / "library" / "inbox" / "pdfs")
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.pdf")):
            if path.is_file():
                files.append(path)
    return sorted(set(files))


def default_output() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return PACKAGES_DIR / f"library-pdfs-{stamp}.zip"


def summarize(files: list[Path], include_inbox: bool) -> dict[str, object]:
    total_bytes = sum(path.stat().st_size for path in files)
    return {
        "workspace": str(WORKSPACE),
        "include_inbox": include_inbox,
        "file_count": len(files),
        "size_mb": round(total_bytes / (1024 * 1024), 2),
    }


def write_zip(output_path: Path, files: list[Path]) -> None:
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED, compresslevel=6) as zf:
        for path in files:
            zf.write(path, arcname=path.relative_to(WORKSPACE))


def main() -> int:
    parser = argparse.ArgumentParser(description="Package thesis library PDFs for transfer.")
    parser.add_argument("--output", type=Path, help="Zip output path. Defaults to packages/library-pdfs-<timestamp>.zip")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be packaged without writing a zip")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the output file if it already exists")
    parser.add_argument("--include-inbox", action="store_true", help="Also include assets/library/inbox/pdfs/*.pdf")
    args = parser.parse_args()

    files = collect_files(include_inbox=args.include_inbox)
    summary = summarize(files, include_inbox=args.include_inbox)
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
