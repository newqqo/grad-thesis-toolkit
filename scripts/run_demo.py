from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    printable = " ".join(args)
    print(f"\n$ {printable}")
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    python = sys.executable
    steps = [
        [python, "scripts/check_public_readiness.py"],
        [
            python,
            "scripts/init_literature_map.py",
            "--topic",
            "PSC",
            "--domain-hint",
            "port state control / maritime safety",
            "--overwrite",
        ],
        [
            python,
            "scripts/extract_citation_candidates.py",
            "--input",
            "examples/outline-with-citations.md",
            "--output",
            "consistency/reports/citation_candidates.md",
        ],
        [python, "scripts/thesis_style_scan.py", "scan"],
        [python, "scripts/thesis_consistency_audit.py"],
        [python, "scripts/create_thin_template_v2.py"],
        [python, "scripts/thesis_md_pipeline_v2.py", "render", "--skip-pdf"],
    ]
    for step in steps:
        run(step)
    print("\nDemo complete.")
    print("- Literature map: literature/psc/")
    print("- Citation candidate report: consistency/reports/citation_candidates.md")
    print("- DOCX output: deliverables/docx/thesis_render_v2_latest.docx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
