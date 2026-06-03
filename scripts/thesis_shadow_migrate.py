#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE / "scripts") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "scripts"))

from thesis_shadow import MANIFEST_NAME, rewrite_paragraph_text, write_docx_xml, xml_paragraphs  # noqa: E402


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


BLOCK_PREFIX = "<!-- Edit only the text under each p-marker. Do not change p-numbers. -->"
DEFAULT_TEMPLATE_DOCX = WORKSPACE / "assets" / "templates" / "docx" / "thesis_template.docx"
DEFAULT_P_STYLE_OVERRIDES = WORKSPACE / "consistency" / "rules" / "p_style_overrides.json"


@dataclass
class ShadowRecord:
    chapter_id: str
    chapter_label: str
    source_indexes: list[int]
    text: str
    original_index: int | None = None
    new_index: int | None = None


@dataclass
class DocxRecord:
    source_indexes: list[int]
    text: str
    element: Any


def load_manifest(shadow_dir: Path) -> dict[str, Any]:
    manifest_path = shadow_dir / MANIFEST_NAME
    if not manifest_path.exists():
        raise FileNotFoundError(f"Shadow manifest not found: {manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def parse_shadow_file(chapter_path: Path) -> list[tuple[int, str]]:
    records: list[tuple[int, str]] = []
    current_index: int | None = None
    buffer: list[str] = []
    in_frontmatter = False

    def flush() -> None:
        nonlocal current_index, buffer
        if current_index is None:
            return
        text = "\n".join(buffer).strip()
        records.append((current_index, text))
        current_index = None
        buffer = []

    for raw_line in chapter_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped == "---" and current_index is None:
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped.startswith("# ") or stripped == BLOCK_PREFIX:
            continue
        if stripped.startswith("## p") and stripped[4:].isdigit():
            flush()
            current_index = int(stripped[4:])
            continue
        if current_index is not None:
            buffer.append(line)
    flush()
    return records


def load_shadow_records(shadow_dir: Path, manifest: dict[str, Any]) -> list[ShadowRecord]:
    records: list[ShadowRecord] = []
    seen: set[int] = set()
    for chapter in manifest["chapters"]:
        chapter_id = chapter["id"]
        chapter_label = chapter["label"]
        chapter_path = shadow_dir / f"{chapter_id}.md"
        chapter_records = parse_shadow_file(chapter_path)
        for index, text in chapter_records:
            if index in seen:
                raise ValueError(f"Duplicate p marker in shadow source: p{index}")
            seen.add(index)
            records.append(
                ShadowRecord(
                    chapter_id=chapter_id,
                    chapter_label=chapter_label,
                    source_indexes=[index],
                    text=text,
                    original_index=index,
                )
            )
    return sorted(records, key=lambda item: item.original_index or -1)


def clone_record(record: ShadowRecord, *, text: str | None = None, source_indexes: list[int] | None = None) -> ShadowRecord:
    return ShadowRecord(
        chapter_id=record.chapter_id,
        chapter_label=record.chapter_label,
        source_indexes=list(record.source_indexes if source_indexes is None else source_indexes),
        text=record.text if text is None else text,
        original_index=record.original_index,
    )


def normalize_new_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        raise ValueError("Inserted or rewritten shadow text cannot be empty.")
    return normalized


def locate_record(records: list[ShadowRecord], target: int, match: str | None = None) -> int:
    positions = [idx for idx, record in enumerate(records) if target in record.source_indexes]
    if not positions:
        raise ValueError(f"Target p{target} not found in current migration state.")
    if len(positions) == 1:
        return positions[0]
    if match == "first":
        return positions[0]
    if match == "last":
        return positions[-1]
    raise ValueError(
        f"Target p{target} became ambiguous after a prior split/merge. "
        "Add \"match\": \"first\" or \"match\": \"last\" in the plan."
    )


def locate_docx_record(records: list[DocxRecord], target: int, match: str | None = None) -> int:
    positions = [idx for idx, record in enumerate(records) if target in record.source_indexes]
    if not positions:
        raise ValueError(f"Target p{target} not found in DOCX migration state.")
    if len(positions) == 1:
        return positions[0]
    if match == "first":
        return positions[0]
    if match == "last":
        return positions[-1]
    raise ValueError(
        f"Target p{target} became ambiguous in DOCX migration state. "
        "Add \"match\": \"first\" or \"match\": \"last\" in the plan."
    )


def split_text(text: str, op: dict[str, Any]) -> tuple[str, str]:
    delimiter = op.get("delimiter")
    regex = op.get("regex")
    keep = op.get("keep_delimiter", "second")
    if bool(delimiter) == bool(regex):
        raise ValueError("split operation requires exactly one of: delimiter or regex")

    if delimiter:
        start = text.find(delimiter)
        if start < 0:
            raise ValueError(f'Split delimiter not found: "{delimiter}"')
        end = start + len(delimiter)
    else:
        import re

        match = re.search(str(regex), text, flags=re.MULTILINE)
        if not match:
            raise ValueError(f'Split regex not found: "{regex}"')
        start, end = match.span()

    if keep == "first":
        left = text[:end].rstrip()
        right = text[end:].lstrip()
    elif keep == "second":
        left = text[:start].rstrip()
        right = text[start:].lstrip()
    elif keep == "both":
        left = text[:end].rstrip()
        right = text[start:].lstrip()
    elif keep == "drop":
        left = text[:start].rstrip()
        right = text[end:].lstrip()
    else:
        raise ValueError('keep_delimiter must be one of: "first", "second", "both", "drop"')

    if not left or not right:
        raise ValueError("Split would create an empty paragraph. Adjust delimiter or keep_delimiter.")
    return left, right


def load_docx_records(docx_path: Path) -> tuple[Any, Any, list[DocxRecord]]:
    tree, xml_records = xml_paragraphs(docx_path)
    root = tree.getroot()
    body = root.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body")
    if body is None:
        raise ValueError(f"Unable to locate document body in {docx_path}")
    records = [
        DocxRecord(source_indexes=[index], text=text, element=element)
        for index, element, text in xml_records
    ]
    return tree, body, records


def clone_docx_paragraph(record: DocxRecord, text: str | None = None) -> Any:
    cloned = copy.deepcopy(record.element)
    rewrite_paragraph_text(cloned, (text if text is not None else record.text) or record.text)
    return cloned


def insert_body_element(body: Any, reference: Any, new_element: Any, *, before: bool) -> None:
    siblings = list(body)
    position = siblings.index(reference)
    body.insert(position if before else position + 1, new_element)


def apply_docx_operation(records: list[DocxRecord], body: Any, op: dict[str, Any]) -> None:
    op_type = op["op"]
    target = int(op["target"]) if "target" in op else None
    match = op.get("match")

    if op_type == "insert_after":
        pos = locate_docx_record(records, target, match)
        base = records[pos]
        inserted_text = normalize_new_text(op["text"])
        cloned = clone_docx_paragraph(base, inserted_text)
        insert_body_element(body, base.element, cloned, before=False)
        records.insert(pos + 1, DocxRecord(source_indexes=[], text=inserted_text, element=cloned))
        return

    if op_type == "insert_before":
        pos = locate_docx_record(records, target, match)
        base = records[pos]
        inserted_text = normalize_new_text(op["text"])
        cloned = clone_docx_paragraph(base, inserted_text)
        insert_body_element(body, base.element, cloned, before=True)
        records.insert(pos, DocxRecord(source_indexes=[], text=inserted_text, element=cloned))
        return

    if op_type == "delete":
        pos = locate_docx_record(records, target, match)
        body.remove(records[pos].element)
        records.pop(pos)
        return

    if op_type == "split":
        pos = locate_docx_record(records, target, match)
        current = records[pos]
        try:
            _, right_text = split_text(current.text, op)
        except Exception:
            right_text = current.text
        cloned = clone_docx_paragraph(current, right_text)
        insert_body_element(body, current.element, cloned, before=False)
        records[pos:pos + 1] = [
            DocxRecord(source_indexes=list(current.source_indexes), text=current.text, element=current.element),
            DocxRecord(source_indexes=list(current.source_indexes), text=right_text, element=cloned),
        ]
        return

    if op_type == "merge_with_next":
        pos = locate_docx_record(records, target, match)
        if pos + 1 >= len(records):
            raise ValueError(f"Cannot merge p{target} with next DOCX paragraph; already at end.")
        nxt = records[pos + 1]
        current = records[pos]
        body.remove(nxt.element)
        records[pos:pos + 2] = [
            DocxRecord(
                source_indexes=current.source_indexes + nxt.source_indexes,
                text=current.text,
                element=current.element,
            )
        ]
        return

    raise ValueError(f"Unsupported DOCX operation: {op_type}")


def apply_operation(records: list[ShadowRecord], op: dict[str, Any]) -> None:
    op_type = op["op"]
    target = int(op["target"]) if "target" in op else None
    match = op.get("match")

    if op_type == "insert_after":
        pos = locate_record(records, target, match)
        base = records[pos]
        records.insert(
            pos + 1,
            ShadowRecord(
                chapter_id=base.chapter_id,
                chapter_label=base.chapter_label,
                source_indexes=[],
                text=normalize_new_text(op["text"]),
            ),
        )
        return

    if op_type == "insert_before":
        pos = locate_record(records, target, match)
        base = records[pos]
        records.insert(
            pos,
            ShadowRecord(
                chapter_id=base.chapter_id,
                chapter_label=base.chapter_label,
                source_indexes=[],
                text=normalize_new_text(op["text"]),
            ),
        )
        return

    if op_type == "delete":
        pos = locate_record(records, target, match)
        records.pop(pos)
        return

    if op_type == "split":
        pos = locate_record(records, target, match)
        current = records[pos]
        left, right = split_text(current.text, op)
        records[pos:pos + 1] = [
            clone_record(current, text=left),
            clone_record(current, text=right),
        ]
        return

    if op_type == "merge_with_next":
        pos = locate_record(records, target, match)
        if pos + 1 >= len(records):
            raise ValueError(f"Cannot merge p{target} with next paragraph; already at end of shadow.")
        current = records[pos]
        nxt = records[pos + 1]
        if current.chapter_id != nxt.chapter_id:
            raise ValueError(
                f"Cannot merge across chapter boundary: {current.chapter_id} -> {nxt.chapter_id}"
            )
        joiner = op.get("joiner", " ")
        merged = clone_record(
            current,
            text=current.text.rstrip() + joiner + nxt.text.lstrip(),
            source_indexes=current.source_indexes + nxt.source_indexes,
        )
        records[pos:pos + 2] = [merged]
        return

    raise ValueError(f"Unsupported operation: {op_type}")


def renumber_records(records: list[ShadowRecord], manifest: dict[str, Any]) -> tuple[list[ShadowRecord], list[dict[str, Any]]]:
    renumbered: list[ShadowRecord] = []
    next_index = manifest["chapters"][0]["start"]
    for record in records:
        clone = clone_record(record)
        clone.new_index = next_index
        renumbered.append(clone)
        next_index += 1

    chapter_ranges: list[dict[str, Any]] = []
    for chapter in manifest["chapters"]:
        chapter_records = [record for record in renumbered if record.chapter_id == chapter["id"]]
        if not chapter_records:
            raise ValueError(f"Chapter {chapter['id']} would become empty after migration.")
        chapter_ranges.append(
            {
                "id": chapter["id"],
                "label": chapter["label"],
                "start": chapter_records[0].new_index,
                "end": chapter_records[-1].new_index,
                "paragraph_count": len(chapter_records),
            }
        )
    return renumbered, chapter_ranges


def build_mapping(renumbered: list[ShadowRecord], original_indexes: list[int]) -> dict[str, Any]:
    old_to_new = {index: [] for index in original_indexes}
    new_to_old: dict[int, list[int]] = {}
    inserted_new: list[int] = []
    merged_new: list[int] = []

    for record in renumbered:
        assert record.new_index is not None
        new_to_old[record.new_index] = list(record.source_indexes)
        if not record.source_indexes:
            inserted_new.append(record.new_index)
        if len(record.source_indexes) > 1:
            merged_new.append(record.new_index)
        for old_index in record.source_indexes:
            old_to_new.setdefault(old_index, []).append(record.new_index)

    deleted_old = [index for index, targets in old_to_new.items() if not targets]
    split_old = {index: targets for index, targets in old_to_new.items() if len(targets) > 1}
    renumbered_old = {
        index: targets[0]
        for index, targets in old_to_new.items()
        if len(targets) == 1 and targets[0] != index
    }
    unchanged_old = [index for index, targets in old_to_new.items() if targets == [index]]

    return {
        "old_to_new": old_to_new,
        "new_to_old": {str(key): value for key, value in new_to_old.items()},
        "deleted_old": deleted_old,
        "split_old": split_old,
        "merged_new": merged_new,
        "inserted_new": inserted_new,
        "renumbered_old": renumbered_old,
        "unchanged_old_count": len(unchanged_old),
    }


def format_migration_report(
    *,
    shadow_dir: Path,
    plan: dict[str, Any],
    manifest: dict[str, Any],
    chapter_ranges: list[dict[str, Any]],
    mapping: dict[str, Any],
) -> str:
    old_count = manifest["paragraph_count"]
    new_count = sum(item["paragraph_count"] for item in chapter_ranges)
    lines = [
        f"# Shadow Migration Report",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Shadow dir: `{shadow_dir}`",
        f"- Description: `{plan.get('description', '')}`",
        f"- Paragraph count: `{old_count}` -> `{new_count}`",
        f"- Operations: `{len(plan.get('operations', []))}`",
        "",
        "## Counts",
        "",
        f"- Unchanged old indexes: `{mapping['unchanged_old_count']}`",
        f"- Renumbered old indexes: `{len(mapping['renumbered_old'])}`",
        f"- Deleted old indexes: `{len(mapping['deleted_old'])}`",
        f"- Split old indexes: `{len(mapping['split_old'])}`",
        f"- Inserted new indexes: `{len(mapping['inserted_new'])}`",
        f"- Merged new indexes: `{len(mapping['merged_new'])}`",
        "",
        "## Chapter Ranges",
        "",
    ]
    for chapter in chapter_ranges:
        lines.append(
            f"- `{chapter['id']}`: `p{chapter['start']}`–`p{chapter['end']}` "
            f"(`{chapter['paragraph_count']}` paragraphs)"
        )

    if mapping["renumbered_old"]:
        lines.extend(["", "## Renumbered", ""])
        for item in compress_renumber_ranges(mapping["renumbered_old"]):
            lines.append(f"- {item}")

    if mapping["deleted_old"]:
        lines.extend(["", "## Deleted", ""])
        for old_index in mapping["deleted_old"]:
            lines.append(f"- `p{old_index}`")

    if mapping["split_old"]:
        lines.extend(["", "## Split", ""])
        for old_index, new_indexes in sorted(mapping["split_old"].items()):
            formatted = ", ".join(f"`p{item}`" for item in new_indexes)
            lines.append(f"- `p{old_index}` -> {formatted}")

    if mapping["inserted_new"]:
        lines.extend(["", "## Inserted", ""])
        for new_index in mapping["inserted_new"]:
            lines.append(f"- `p{new_index}` (new paragraph)")

    if mapping["merged_new"]:
        lines.extend(["", "## Merged", ""])
        for new_index in mapping["merged_new"]:
            old_indexes = mapping["new_to_old"][str(new_index)]
            formatted = ", ".join(f"`p{item}`" for item in old_indexes)
            lines.append(f"- `p{new_index}` <- {formatted}")

    return "\n".join(lines).rstrip() + "\n"


def compress_renumber_ranges(renumbered_old: dict[int, int]) -> list[str]:
    items = sorted(renumbered_old.items())
    if not items:
        return []

    def render(start_old: int, start_new: int, end_old: int, end_new: int) -> str:
        if start_old == end_old:
            return f"`p{start_old}` -> `p{start_new}`"
        return f"`p{start_old}`–`p{end_old}` -> `p{start_new}`–`p{end_new}`"

    rendered: list[str] = []
    start_old, start_new = items[0]
    prev_old, prev_new = items[0]

    for old_index, new_index in items[1:]:
        same_delta = (new_index - old_index) == (prev_new - prev_old)
        consecutive = old_index == prev_old + 1 and new_index == prev_new + 1
        if same_delta and consecutive:
            prev_old, prev_new = old_index, new_index
            continue
        rendered.append(render(start_old, start_new, prev_old, prev_new))
        start_old, start_new = old_index, new_index
        prev_old, prev_new = old_index, new_index

    rendered.append(render(start_old, start_new, prev_old, prev_new))
    return rendered


def render_chapter(chapter: dict[str, Any], source_docx_name: str, records: list[ShadowRecord]) -> str:
    lines = [
        "---",
        f'chapter_id: "{chapter["id"]}"',
        f'chapter_label: "{chapter["label"]}"',
        f'source_docx: "{source_docx_name}"',
        f"range_start: {chapter['start']}",
        f"range_end: {chapter['end']}",
        f"paragraph_count: {chapter['paragraph_count']}",
        "---",
        "",
        BLOCK_PREFIX,
        "",
        f"# {chapter['label']}",
        "",
    ]
    for record in records:
        if record.new_index is None:
            raise ValueError("Attempted to render chapter before assigning new indexes.")
        lines.append(f"## p{record.new_index}")
        lines.append(record.text.strip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_shadow_dir(
    shadow_dir: Path,
    manifest: dict[str, Any],
    renumbered: list[ShadowRecord],
    chapter_ranges: list[dict[str, Any]],
) -> None:
    source_docx_name = Path(manifest["source_docx"]).name
    for chapter in chapter_ranges:
        chapter_records = [record for record in renumbered if record.chapter_id == chapter["id"]]
        chapter_path = shadow_dir / f"{chapter['id']}.md"
        chapter_path.write_text(
            render_chapter(chapter, source_docx_name, chapter_records),
            encoding="utf-8",
        )

    new_manifest = dict(manifest)
    new_manifest["paragraph_count"] = len(renumbered)
    new_manifest["chapters"] = [
        {
            "id": chapter["id"],
            "label": chapter["label"],
            "start": chapter["start"],
            "end": chapter["end"],
        }
        for chapter in chapter_ranges
    ]
    new_manifest["generated_at"] = datetime.now().isoformat(timespec="seconds")
    (shadow_dir / MANIFEST_NAME).write_text(
        json.dumps(new_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def backup_shadow_dir(shadow_dir: Path, backup_root: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / stamp
    backup_dir.mkdir(parents=True, exist_ok=False)
    shutil.copytree(shadow_dir, backup_dir / "shadow")
    return backup_dir


def backup_docx_targets(docx_targets: list[Path], backup_dir: Path) -> None:
    if not docx_targets:
        return
    docx_backup_dir = backup_dir / "docx"
    docx_backup_dir.mkdir(parents=True, exist_ok=True)
    for target in docx_targets:
        if target.exists():
            shutil.copy2(target, docx_backup_dir / target.name)


def sync_docx_targets(plan: dict[str, Any], docx_targets: list[Path]) -> list[Path]:
    updated: list[Path] = []
    for target in docx_targets:
        if not target.exists():
            continue
        tree, body, records = load_docx_records(target)
        for op in plan["operations"]:
            apply_docx_operation(records, body, op)
        write_docx_xml(target, tree)
        updated.append(target)
    return updated


def run_sidecar_refresh(shadow_dir: Path, manifest: dict[str, Any], backup_dir: Path) -> None:
    config_path = Path(manifest["config_path"])
    commands = [
        [
            sys.executable,
            str(WORKSPACE / "scripts" / "thesis_mem.py"),
            "build",
            str(shadow_dir),
            "--config",
            str(config_path),
            "--outdir",
            str(WORKSPACE / "consistency" / "exports" / "thesis_mem"),
        ],
        [
            sys.executable,
            str(WORKSPACE / "scripts" / "thesis_library.py"),
            "scan-thesis-all",
            "--active-only",
        ],
    ]
    logs: list[str] = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            check=True,
        )
        logs.append("$ " + " ".join(command))
        if completed.stdout.strip():
            logs.append(completed.stdout.rstrip())
        if completed.stderr.strip():
            logs.append(completed.stderr.rstrip())
        logs.append("")
    (backup_dir / "post_refresh.log").write_text("\n".join(logs).rstrip() + "\n", encoding="utf-8")


def remap_p_style_overrides(overrides_path: Path, mapping: dict[str, Any], backup_dir: Path) -> dict[str, int]:
    if not overrides_path.exists():
        return {"updated": 0, "section_break_updated": 0, "pending": 0}

    payload = json.loads(overrides_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"updated": 0, "section_break_updated": 0, "pending": 0}

    raw_styles = payload.get("styles", {})
    if not isinstance(raw_styles, dict):
        return {"updated": 0, "section_break_updated": 0, "pending": 0}

    raw_section_break_before = payload.get("section_break_before", {})
    if not isinstance(raw_section_break_before, dict):
        raw_section_break_before = {}

    old_to_new_raw = mapping.get("old_to_new", {})
    old_to_new: dict[int, list[int]] = {}
    for old_index_text, new_indexes in old_to_new_raw.items():
        try:
            old_index = int(str(old_index_text))
        except ValueError:
            continue
        if isinstance(new_indexes, list):
            old_to_new[old_index] = [int(item) for item in new_indexes]

    remapped: dict[int, str] = {}
    remapped_section_break_before: dict[int, str] = {}
    pending: list[dict[str, Any]] = []

    for old_key, style_name in raw_styles.items():
        try:
            old_index = int(str(old_key))
        except ValueError:
            pending.append(
                {
                    "type": "invalid_key",
                    "scope": "styles",
                    "old_p": old_key,
                    "reason": "style key is not an integer p marker",
                }
            )
            continue

        targets = old_to_new.get(old_index, [])
        if len(targets) == 1:
            target = targets[0]
            previous = remapped.get(target)
            if previous is None or previous == style_name:
                remapped[target] = style_name
            else:
                pending.append(
                    {
                        "type": "conflict",
                        "scope": "styles",
                        "new_p": target,
                        "styles": [previous, style_name],
                        "old_p_candidates": [k for k, v in raw_styles.items() if str(v) in {previous, style_name}],
                    }
                )
        elif len(targets) == 0:
            pending.append(
                {
                    "type": "deleted",
                    "scope": "styles",
                    "old_p": old_index,
                    "style": style_name,
                    "reason": "original paragraph was deleted",
                }
            )
        else:
            pending.append(
                {
                    "type": "split",
                    "scope": "styles",
                    "old_p": old_index,
                    "new_p_candidates": targets,
                    "style": style_name,
                    "reason": "original paragraph split into multiple new p markers",
                }
            )

    for old_key, raw_orientation in raw_section_break_before.items():
        try:
            old_index = int(str(old_key))
        except ValueError:
            pending.append(
                {
                    "type": "invalid_key",
                    "scope": "section_break_before",
                    "old_p": old_key,
                    "reason": "section_break_before key is not an integer p marker",
                }
            )
            continue

        orientation = str(raw_orientation).strip().lower()
        if orientation not in {"portrait", "landscape"}:
            orientation = "portrait"

        targets = old_to_new.get(old_index, [])
        if len(targets) == 1:
            target = targets[0]
            previous = remapped_section_break_before.get(target)
            if previous is None or previous == orientation:
                remapped_section_break_before[target] = orientation
            else:
                pending.append(
                    {
                        "type": "conflict",
                        "scope": "section_break_before",
                        "new_p": target,
                        "orientations": [previous, orientation],
                    }
                )
        elif len(targets) == 0:
            pending.append(
                {
                    "type": "deleted",
                    "scope": "section_break_before",
                    "old_p": old_index,
                    "orientation": orientation,
                    "reason": "original paragraph was deleted",
                }
            )
        else:
            pending.append(
                {
                    "type": "split",
                    "scope": "section_break_before",
                    "old_p": old_index,
                    "new_p_candidates": targets,
                    "orientation": orientation,
                    "reason": "original paragraph split into multiple new p markers",
                }
            )

    sorted_styles = {
        str(key): remapped[key]
        for key in sorted(remapped)
    }
    sorted_section_break_before = {
        str(key): remapped_section_break_before[key]
        for key in sorted(remapped_section_break_before)
    }
    payload["styles"] = sorted_styles
    payload["section_break_before"] = sorted_section_break_before
    payload["pending_resolutions"] = pending
    payload["last_remap"] = datetime.now().isoformat(timespec="seconds")

    backup_copy = backup_dir / overrides_path.name
    backup_copy.write_text(overrides_path.read_text(encoding="utf-8"), encoding="utf-8")
    overrides_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "updated": len(sorted_styles),
        "section_break_updated": len(sorted_section_break_before),
        "pending": len(pending),
    }


def load_plan(path: Path) -> dict[str, Any]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or "operations" not in plan:
        raise ValueError("Migration plan must be a JSON object containing an operations array.")
    if not isinstance(plan["operations"], list) or not plan["operations"]:
        raise ValueError("Migration plan operations must be a non-empty array.")
    return plan


def preview_or_apply(
    *,
    shadow_dir: Path,
    plan_path: Path,
    apply: bool,
    refresh_sidecars: bool,
    backup_root: Path,
    docx_targets: list[Path],
    p_style_overrides: Path,
) -> None:
    manifest = load_manifest(shadow_dir)
    original_records = load_shadow_records(shadow_dir, manifest)
    working_records = [clone_record(record) for record in original_records]
    plan = load_plan(plan_path)

    for op in plan["operations"]:
        apply_operation(working_records, op)

    renumbered, chapter_ranges = renumber_records(working_records, manifest)
    mapping = build_mapping(renumbered, [record.original_index for record in original_records if record.original_index is not None])
    report = format_migration_report(
        shadow_dir=shadow_dir,
        plan=plan,
        manifest=manifest,
        chapter_ranges=chapter_ranges,
        mapping=mapping,
    )

    if not apply:
        if docx_targets:
            print("DOCX targets to sync:")
            for target in docx_targets:
                print(f"- {target}")
            print("")
        print(report)
        return

    backup_dir = backup_shadow_dir(shadow_dir, backup_root)
    (backup_dir / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (backup_dir / "migration_map.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    backup_docx_targets(docx_targets, backup_dir)

    updated_docx = sync_docx_targets(plan, docx_targets)
    write_shadow_dir(shadow_dir, manifest, renumbered, chapter_ranges)
    (backup_dir / "migration_report.md").write_text(report, encoding="utf-8")
    override_stats = remap_p_style_overrides(p_style_overrides, mapping, backup_dir)

    if refresh_sidecars:
        run_sidecar_refresh(shadow_dir, manifest, backup_dir)

    print(f"Applied migration. Backup: {backup_dir}")
    if updated_docx:
        print("Updated DOCX structure:")
        for target in updated_docx:
            print(f"- {target}")
    if p_style_overrides.exists():
        print(
            "Updated p-style overrides: "
            f"{p_style_overrides} "
            f"(active={override_stats['updated']}, section_break={override_stats['section_break_updated']}, pending={override_stats['pending']})"
        )
    print(report)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely migrate shadow p markers after insert/delete/split/merge operations."
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--shadow",
        type=Path,
        default=WORKSPACE / "source" / "shadow",
        help="Shadow directory to migrate (default: source/shadow).",
    )
    common.add_argument(
        "--backup-root",
        type=Path,
        default=WORKSPACE / "archive" / "backups" / "shadow_migrations",
        help="Backup root for applied migrations.",
    )
    common.add_argument(
        "--docx-target",
        type=Path,
        action="append",
        default=None,
        help="DOCX file whose paragraph skeleton should be migrated together with shadow. Can be used multiple times.",
    )
    common.add_argument(
        "--p-style-overrides",
        type=Path,
        default=DEFAULT_P_STYLE_OVERRIDES,
        help="JSON file containing p-to-style overrides to remap after apply.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    preview = subparsers.add_parser(
        "preview",
        parents=[common],
        help="Preview a migration plan without writing files.",
    )
    preview.add_argument("--plan", type=Path, required=True, help="JSON migration plan.")

    apply = subparsers.add_parser(
        "apply",
        parents=[common],
        help="Apply a migration plan to source/shadow.",
    )
    apply.add_argument("--plan", type=Path, required=True, help="JSON migration plan.")
    apply.add_argument(
        "--no-refresh-sidecars",
        action="store_true",
        help="Skip thesis_mem rebuild and thesis-library scan after applying the migration.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "preview":
        preview_or_apply(
            shadow_dir=args.shadow.resolve(),
            plan_path=args.plan.resolve(),
            apply=False,
            refresh_sidecars=False,
            backup_root=args.backup_root.resolve(),
            docx_targets=[path.resolve() for path in (args.docx_target or [DEFAULT_TEMPLATE_DOCX])],
            p_style_overrides=args.p_style_overrides.resolve(),
        )
        return

    if args.command == "apply":
        preview_or_apply(
            shadow_dir=args.shadow.resolve(),
            plan_path=args.plan.resolve(),
            apply=True,
            refresh_sidecars=not args.no_refresh_sidecars,
            backup_root=args.backup_root.resolve(),
            docx_targets=[path.resolve() for path in (args.docx_target or [DEFAULT_TEMPLATE_DOCX])],
            p_style_overrides=args.p_style_overrides.resolve(),
        )
        return

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
