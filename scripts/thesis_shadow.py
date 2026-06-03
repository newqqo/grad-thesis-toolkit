from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from thesis_mem import NS, ParagraphRecord, chapter_ranges, load_docx_paragraphs, load_shadow_paragraphs


ET.register_namespace("w", NS["w"])
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
MANIFEST_NAME = "shadow_manifest.json"
WORD_NAMESPACE_DECLS = {
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
    "cx1": "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex",
    "cx2": "http://schemas.microsoft.com/office/drawing/2015/10/21/chartex",
    "cx3": "http://schemas.microsoft.com/office/drawing/2016/5/9/chartex",
    "cx4": "http://schemas.microsoft.com/office/drawing/2016/5/10/chartex",
    "cx5": "http://schemas.microsoft.com/office/drawing/2016/5/11/chartex",
    "cx6": "http://schemas.microsoft.com/office/drawing/2016/5/12/chartex",
    "cx7": "http://schemas.microsoft.com/office/drawing/2016/5/13/chartex",
    "cx8": "http://schemas.microsoft.com/office/drawing/2016/5/14/chartex",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "aink": "http://schemas.microsoft.com/office/drawing/2016/ink",
    "am3d": "http://schemas.microsoft.com/office/drawing/2017/model3d",
    "o": "urn:schemas-microsoft-com:office:office",
    "oel": "http://schemas.microsoft.com/office/2019/extlst",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
    "w16du": "http://schemas.microsoft.com/office/word/2023/wordml/word16du",
    "w16sdtdh": "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash",
    "w16sdtfl": "http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}
TEXT_CONTAINER_TAGS = {
    f"{{{NS['w']}}}r",
    f"{{{NS['w']}}}hyperlink",
    f"{{{NS['w']}}}smartTag",
    f"{{{NS['w']}}}sdt",
    f"{{{NS['w']}}}customXml",
    f"{{{NS['w']}}}fldSimple",
}
for prefix, uri in WORD_NAMESPACE_DECLS.items():
    ET.register_namespace(prefix, uri)


def read_config(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_shadow_chapter(docx: Path, chapter: dict, records: list[ParagraphRecord]) -> str:
    lines = [
        "---",
        f'chapter_id: "{chapter["id"]}"',
        f'chapter_label: "{chapter["label"]}"',
        f'source_docx: "{docx.name}"',
        f"range_start: {chapter['start']}",
        f"range_end: {chapter['end']}",
        f"paragraph_count: {len(records)}",
        "---",
        "",
        "<!-- Edit only the text under each p-marker. Do not change p-numbers. -->",
        "",
        f"# {chapter['label']}",
        "",
    ]
    for record in records:
        lines.append(f"## p{record.index}")
        lines.append(record.text)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_manifest(docx: Path, config_path: Path, ranges: list[dict], paragraph_count: int) -> dict:
    return {
        "source_docx": str(docx.resolve()),
        "config_path": str(config_path.resolve()),
        "paragraph_count": paragraph_count,
        "chapters": [
            {
                "id": chapter["id"],
                "label": chapter["label"],
                "start": chapter["start"],
                "end": chapter["end"],
            }
            for chapter in ranges
        ],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def resolve_config(shadow_dir: Path, config_arg: Path | None) -> Path:
    if config_arg is not None:
        return config_arg
    manifest_path = shadow_dir / MANIFEST_NAME
    if not manifest_path.exists():
        raise FileNotFoundError(f"Config not provided and manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return Path(manifest["config_path"])


def docx_chapter_records(docx: Path, config: dict) -> tuple[list[ParagraphRecord], list[dict]]:
    paragraphs = load_docx_paragraphs(docx)
    ranges = chapter_ranges(paragraphs, config)
    selected: list[ParagraphRecord] = []
    for chapter in ranges:
        selected.extend(
            record for record in paragraphs if chapter["start"] <= record.index <= chapter["end"]
        )
    return selected, ranges


def paragraph_xml_text(p: ET.Element) -> str:
    return "".join((t.text or "") for t in p.findall(".//w:t", NS)).strip()


def _container_has_non_text_payload(node: ET.Element) -> bool:
    return (
        node.find('.//w:drawing', NS) is not None
        or node.find('.//w:pict', NS) is not None
        or node.find('.//w:object', NS) is not None
        or node.find('.//w:footnoteReference', NS) is not None
        or node.find('.//w:endnoteReference', NS) is not None
    )


def rewrite_paragraph_text(p: ET.Element, new_text: str) -> None:
    if not new_text.strip():
        raise ValueError("Shadow paragraphs cannot be empty.")

    children = list(p)
    text_children = [
        child for child in children
        if child.tag in TEXT_CONTAINER_TAGS and not _container_has_non_text_payload(child)
    ]
    if text_children:
        insert_at = list(p).index(text_children[0])
        for child in text_children:
            p.remove(child)
    else:
        insert_at = 1 if children and children[0].tag == f"{{{NS['w']}}}pPr" else 0

    run = ET.Element(f"{{{NS['w']}}}r")
    text = ET.SubElement(run, f"{{{NS['w']}}}t")
    if new_text[:1].isspace() or new_text[-1:].isspace():
        text.set(XML_SPACE, "preserve")
    text.text = new_text
    p.insert(insert_at, run)


def xml_paragraphs(path: Path) -> tuple[ET.ElementTree, list[tuple[int, ET.Element, str]]]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    non_empty = 0
    paragraphs: list[tuple[int, ET.Element, str]] = []
    for p in root.findall(".//w:body/w:p", NS):
        text = paragraph_xml_text(p)
        if text:
            non_empty += 1
            paragraphs.append((non_empty, p, text))
    return ET.ElementTree(root), paragraphs


def ensure_document_root_namespaces(xml_text: str) -> str:
    match = re.search(r"<w:document\b[^>]*>", xml_text, flags=re.S)
    if not match:
        return xml_text
    start_tag = match.group(0)
    missing = []
    for prefix, uri in WORD_NAMESPACE_DECLS.items():
        if f"xmlns:{prefix}=" not in start_tag:
            missing.append(f'xmlns:{prefix}="{uri}"')
    if not missing:
        return xml_text
    replacement = start_tag[:-1] + " " + " ".join(missing) + ">"
    return xml_text.replace(start_tag, replacement, 1)


def write_docx_xml(docx_path: Path, tree: ET.ElementTree) -> None:
    root = tree.getroot()
    xml_text = ET.tostring(root, encoding="unicode", xml_declaration=True)
    xml_text = ensure_document_root_namespaces(xml_text)
    xml_bytes = xml_text.encode("utf-8")
    with zipfile.ZipFile(docx_path, "r") as zin:
        fd, temp_name = tempfile.mkstemp(suffix=".docx", prefix="shadow-sync-", dir=str(docx_path.parent))
        try:
            import os
            os.close(fd)
        except OSError:
            pass
        Path(temp_name).unlink(missing_ok=True)
        temp_path = Path(temp_name)
        try:
            with zipfile.ZipFile(temp_path, "w") as zout:
                for item in zin.infolist():
                    if item.filename == "word/document.xml":
                        zout.writestr(item, xml_bytes)
                    else:
                        zout.writestr(item, zin.read(item.filename))
            shutil.move(str(temp_path), str(docx_path))
        finally:
            if temp_path.exists():
                temp_path.unlink()


def compare_shadow_to_docx(shadow_records: list[ParagraphRecord], docx_records: list[ParagraphRecord]) -> tuple[list[int], list[int], list[int]]:
    shadow_map = {record.index: record.text for record in shadow_records}
    docx_map = {record.index: record.text for record in docx_records}

    missing_in_shadow = sorted(set(docx_map) - set(shadow_map))
    extra_in_shadow = sorted(set(shadow_map) - set(docx_map))
    changed = sorted(index for index in set(shadow_map) & set(docx_map) if shadow_map[index] != docx_map[index])
    return missing_in_shadow, extra_in_shadow, changed


def command_export(docx: Path, config_path: Path, outdir: Path) -> None:
    config = read_config(config_path)
    paragraphs, ranges = docx_chapter_records(docx, config)

    outdir.mkdir(parents=True, exist_ok=True)
    for chapter in ranges:
        records = [record for record in paragraphs if chapter["start"] <= record.index <= chapter["end"]]
        write_text(outdir / f"{chapter['id']}.md", render_shadow_chapter(docx, chapter, records))

    manifest = build_manifest(docx, config_path, ranges, len(paragraphs))
    write_text(outdir / MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def command_status(shadow_dir: Path, docx: Path, config_path: Path | None) -> None:
    config = read_config(resolve_config(shadow_dir, config_path))
    shadow_records = load_shadow_paragraphs(shadow_dir, config)
    docx_records, _ = docx_chapter_records(docx, config)
    missing_in_shadow, extra_in_shadow, changed = compare_shadow_to_docx(shadow_records, docx_records)

    print(f"shadow_paragraphs={len(shadow_records)}")
    print(f"docx_paragraphs={len(docx_records)}")
    print(f"missing_in_shadow={len(missing_in_shadow)}")
    print(f"extra_in_shadow={len(extra_in_shadow)}")
    print(f"changed={len(changed)}")
    if changed:
        print("changed_refs=" + ", ".join(f"p{index}" for index in changed[:30]))
    if missing_in_shadow:
        print("missing_refs=" + ", ".join(f"p{index}" for index in missing_in_shadow[:30]))
    if extra_in_shadow:
        print("extra_refs=" + ", ".join(f"p{index}" for index in extra_in_shadow[:30]))


def command_apply(shadow_dir: Path, docx: Path, config_path: Path | None, backup_dir: Path | None) -> None:
    config = read_config(resolve_config(shadow_dir, config_path))
    shadow_records = load_shadow_paragraphs(shadow_dir, config)
    docx_records, ranges = docx_chapter_records(docx, config)
    missing_in_shadow, extra_in_shadow, changed = compare_shadow_to_docx(shadow_records, docx_records)

    if missing_in_shadow or extra_in_shadow:
        raise ValueError(
            "Shadow/docx paragraph indexes differ. "
            f"missing_in_shadow={len(missing_in_shadow)}, extra_in_shadow={len(extra_in_shadow)}"
        )

    shadow_map = {record.index: record.text for record in shadow_records}
    if any(not text.strip() for text in shadow_map.values()):
        raise ValueError("Shadow files contain empty paragraph text. Aborting apply.")

    if backup_dir is not None:
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{docx.stem}_{timestamp}{docx.suffix}"
        shutil.copy2(docx, backup_path)
        print(f"backup={backup_path}")

    tree, xml_records = xml_paragraphs(docx)
    changed_count = 0
    valid_indexes = {record.index for record in docx_records}
    for index, element, current_text in xml_records:
        if index not in valid_indexes:
            continue
        new_text = shadow_map[index]
        if current_text != new_text:
            rewrite_paragraph_text(element, new_text)
            changed_count += 1

    write_docx_xml(docx, tree)
    print(f"changed={changed_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage shadow markdown files for thesis drafting.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export DOCX to chapter-based shadow markdown")
    export_parser.add_argument("docx", type=Path, help="Path to the thesis DOCX")
    export_parser.add_argument("--config", type=Path, required=True, help="JSON config path")
    export_parser.add_argument("--outdir", type=Path, required=True, help="Shadow markdown output directory")

    status_parser = subparsers.add_parser("status", help="Compare shadow markdown against DOCX")
    status_parser.add_argument("shadow_dir", type=Path, help="Shadow markdown directory")
    status_parser.add_argument("docx", type=Path, help="Path to the thesis DOCX")
    status_parser.add_argument("--config", type=Path, default=None, help="Optional JSON config path")

    apply_parser = subparsers.add_parser("apply", help="Apply shadow markdown changes back to DOCX")
    apply_parser.add_argument("shadow_dir", type=Path, help="Shadow markdown directory")
    apply_parser.add_argument("docx", type=Path, help="Path to the thesis DOCX")
    apply_parser.add_argument("--config", type=Path, default=None, help="Optional JSON config path")
    apply_parser.add_argument("--backup-dir", type=Path, default=None, help="Optional backup directory")

    args = parser.parse_args()

    if args.command == "export":
        command_export(args.docx, args.config, args.outdir)
    elif args.command == "status":
        command_status(args.shadow_dir, args.docx, args.config)
    elif args.command == "apply":
        command_apply(args.shadow_dir, args.docx, args.config, args.backup_dir)


if __name__ == "__main__":
    main()
