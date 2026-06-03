from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from thesis_render_v2 import load_layout_rules, load_shadow_chapters


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = ROOT / "scripts"
DEFAULT_SHADOW = ROOT / "source" / "shadow"
DEFAULT_LAYOUT = ROOT / "source" / "layout" / "thesis_v2_layout.md"
DEFAULT_TEMPLATE = ROOT / "assets" / "templates" / "docx" / "thesis_template_thin.docx"
DEFAULT_FRONT_MATTER_SOURCE = ROOT / "source" / "front_matter" / "front_matter_source.docx"
DEFAULT_OUTPUT = ROOT / "deliverables" / "docx" / "thesis_render_v2_latest.docx"
DEFAULT_PDF_OUTPUT = ROOT / "deliverables" / "pdf" / "thesis_render_v2_latest.pdf"
TMP_DOCS_DIR = ROOT / "tmp" / "docs"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def build_managed_assets(layout: Path, refresh_assets: bool = False) -> None:
    for rule in load_layout_rules(layout):
        if rule.kind != "build-image" or rule.script is None or rule.path is None:
            continue
        if not refresh_assets and rule.path.exists():
            continue
        run([sys.executable, str(rule.script)])


def cmd_audit_layout(args: argparse.Namespace) -> None:
    layout = Path(args.layout).resolve()
    shadow = Path(args.shadow).resolve()
    errors: list[str] = []
    shadow_texts: list[str] = []
    for chapter in load_shadow_chapters(shadow):
        shadow_texts.append(chapter.label)
        shadow_texts.extend(paragraph.text for paragraph in chapter.paragraphs)
    for rule in load_layout_rules(layout):
        if not any(rule.match.search(text.strip()) for text in shadow_texts if text.strip()):
            errors.append(f"rule matches no source text: {rule.kind} / {rule.match.pattern}")
        if rule.kind == "build-image":
            if rule.script is None or not rule.script.exists():
                errors.append(f"missing build script: {rule.script}")
            if rule.path is None:
                errors.append("build-image rule missing output path")
        if rule.kind == "image":
            if rule.path is None:
                errors.append("image rule missing path")
        if rule.kind in {"image", "build-image"} and rule.path is not None and not rule.path.exists():
            errors.append(f"missing asset: {rule.path}")

    if errors:
        raise SystemExit("layout audit failed:\n- " + "\n- ".join(errors))
    print("layout audit ok")


def cmd_render(args: argparse.Namespace) -> None:
    shadow = Path(args.shadow).resolve()
    layout = Path(args.layout).resolve()
    template = Path(args.template).resolve()
    front_matter_source = Path(args.front_matter_source).resolve()
    output = Path(args.output).resolve()
    pdf_output = Path(args.pdf_output).resolve()
    should_merge_front_matter = (not args.skip_front_matter_merge) and front_matter_source.exists()
    body_output = output if not should_merge_front_matter else (TMP_DOCS_DIR / f"{output.stem}_body.docx")

    if not args.skip_asset_build:
        build_managed_assets(layout, refresh_assets=args.refresh_assets)

    if not template.exists() or args.refresh_template:
        run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / "create_thin_template_v2.py"),
                "--output",
                str(template),
            ]
        )

    run(
        [
            sys.executable,
                str(SCRIPTS_ROOT / "thesis_render_v2.py"),
                "--shadow",
                str(shadow),
                "--layout",
                str(layout),
                "--template",
                str(template),
                "--output",
                str(body_output),
            ]
        )

    if should_merge_front_matter:
        run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / "merge_front_matter_v2.py"),
                "--front-source",
                str(front_matter_source),
                "--body-source",
                str(body_output),
                "--output",
                str(output),
            ]
        )

        run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / "normalize_page_layout.py"),
                "--docx",
                str(output),
            ]
        )

        run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / "repair_v2_imported_styles.py"),
                "--docx",
                str(output),
            ]
        )

        if not args.skip_word_update:
            run(
                [
                    sys.executable,
                    str(SCRIPTS_ROOT / "thesis_word_update.py"),
                    "update-fields",
                    "--docx",
                    str(output),
                    "--mode",
                    "toc-only",
                ]
            )
            run(
                [
                    sys.executable,
                    str(SCRIPTS_ROOT / "repair_v2_imported_styles.py"),
                    "--docx",
                    str(output),
                ]
            )

            run(
                [
                    sys.executable,
                    str(SCRIPTS_ROOT / "normalize_page_layout.py"),
                    "--docx",
                    str(output),
                ]
            )
    elif not args.skip_front_matter_merge:
        print(f"front matter source not found, wrote body-only DOCX: {output}")

    if not args.skip_pdf:
        run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / "thesis_pdf.py"),
                "export",
                "--docx",
                str(output),
                "--output",
                str(pdf_output),
            ]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Thin-template thesis render pipeline (v2).")
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render")
    render.add_argument("--shadow", default=str(DEFAULT_SHADOW))
    render.add_argument("--layout", default=str(DEFAULT_LAYOUT))
    render.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    render.add_argument("--front-matter-source", default=str(DEFAULT_FRONT_MATTER_SOURCE))
    render.add_argument("--output", default=str(DEFAULT_OUTPUT))
    render.add_argument("--pdf-output", default=str(DEFAULT_PDF_OUTPUT))
    render.add_argument("--refresh-template", action="store_true")
    render.add_argument("--refresh-assets", action="store_true")
    render.add_argument("--skip-asset-build", action="store_true")
    render.add_argument("--skip-front-matter-merge", action="store_true")
    render.add_argument("--skip-word-update", action="store_true")
    render.add_argument("--skip-pdf", action="store_true")
    render.set_defaults(func=cmd_render)

    audit = sub.add_parser("audit-layout")
    audit.add_argument("--layout", default=str(DEFAULT_LAYOUT))
    audit.add_argument("--shadow", default=str(DEFAULT_SHADOW))
    audit.set_defaults(func=cmd_audit_layout)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
