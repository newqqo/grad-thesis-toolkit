from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
SHADOW_PARAGRAPH_RE = re.compile(r"^(?:#{2,6}|-)\s+\[p(?P<index>\d+)]\s+(?P<text>.*)$")
SHADOW_BLOCK_RE = re.compile(r"^##\s+p(?P<index>\d+)\s*$", re.IGNORECASE)


@dataclass
class ParagraphRecord:
    index: int
    text: str
    order: int = 0


def load_docx_paragraphs(path: Path) -> list[ParagraphRecord]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs: list[ParagraphRecord] = []
    non_empty_index = 0
    for p in root.findall(".//w:body/w:p", NS):
        text = "".join((t.text or "") for t in p.findall(".//w:t", NS)).strip()
        if text:
            non_empty_index += 1
            paragraphs.append(ParagraphRecord(index=non_empty_index, text=text, order=len(paragraphs)))
    return paragraphs


def load_shadow_paragraphs(shadow_dir: Path, config: dict) -> list[ParagraphRecord]:
    paragraphs: list[ParagraphRecord] = []
    seen_indexes: set[int] = set()
    for chapter in config["chapters"]:
        chapter_path = shadow_dir / f"{chapter['id']}.md"
        if not chapter_path.exists():
            raise FileNotFoundError(f"Shadow chapter not found: {chapter_path}")
        lines = chapter_path.read_text(encoding="utf-8").splitlines()
        current_index: int | None = None
        buffer: list[str] = []

        def flush_block() -> None:
            nonlocal current_index, buffer
            if current_index is None:
                return
            text = " ".join(line.strip() for line in buffer if line.strip()).strip()
            if current_index in seen_indexes:
                raise ValueError(f"Duplicate paragraph index in shadow files: p{current_index}")
            seen_indexes.add(current_index)
            paragraphs.append(ParagraphRecord(index=current_index, text=text, order=len(paragraphs)))
            current_index = None
            buffer = []

        in_frontmatter = False
        for raw_line in lines:
            line = raw_line.rstrip()
            stripped = line.strip()
            if stripped == "---":
                if current_index is not None:
                    buffer.append(line)
                    continue
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue

            block_match = SHADOW_BLOCK_RE.match(stripped)
            if block_match:
                flush_block()
                current_index = int(block_match.group("index"))
                continue

            line_match = SHADOW_PARAGRAPH_RE.match(stripped)
            if line_match:
                flush_block()
                index = int(line_match.group("index"))
                text = line_match.group("text")
                if index in seen_indexes:
                    raise ValueError(f"Duplicate paragraph index in shadow files: p{index}")
                seen_indexes.add(index)
                paragraphs.append(ParagraphRecord(index=index, text=text, order=len(paragraphs)))
                continue

            if current_index is not None:
                buffer.append(line)
        flush_block()
    return paragraphs


def load_source_paragraphs(source: Path, config: dict) -> tuple[list[ParagraphRecord], str]:
    if source.is_dir():
        return load_shadow_paragraphs(source, config), source.name
    if source.suffix.lower() == ".docx":
        return load_docx_paragraphs(source), source.name
    raise ValueError(f"Unsupported source: {source}")


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "chunk"


def find_heading_position(paragraphs: list[ParagraphRecord], heading: str) -> int:
    for position, paragraph in enumerate(paragraphs):
        if paragraph.text == heading:
            return position
    raise ValueError(f"Heading not found: {heading}")


def chapter_ranges(paragraphs: list[ParagraphRecord], config: dict) -> list[dict]:
    ranges: list[dict] = []
    for chapter in config["chapters"]:
        start_pos = find_heading_position(paragraphs, chapter["start_heading"])
        try:
            end_heading = chapter["end_heading"]
            end_pos = find_heading_position(paragraphs, end_heading) - 1
        except ValueError:
            end_pos = len(paragraphs) - 1
        chapter_records = paragraphs[start_pos : end_pos + 1]
        ranges.append(
            {
                "id": chapter["id"],
                "label": chapter["label"],
                "start_heading": chapter["start_heading"],
                "start": chapter_records[0].index,
                "end": chapter_records[-1].index,
                "start_pos": start_pos,
                "end_pos": end_pos,
            }
        )
    return ranges


def paragraphs_in_chapter(paragraphs: list[ParagraphRecord], chapter: dict) -> list[ParagraphRecord]:
    return paragraphs[chapter["start_pos"] : chapter["end_pos"] + 1]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def is_candidate_heading(text: str) -> bool:
    return len(text) <= 48 and "。" not in text


def format_record(record: ParagraphRecord) -> str:
    prefix = "##" if is_candidate_heading(record.text) else "-"
    return f"{prefix} [p{record.index}] {record.text}"


def format_records(records: list[ParagraphRecord]) -> list[str]:
    return [format_record(record) for record in records]


def split_records_balanced(records: list[ParagraphRecord], max_size: int) -> list[list[ParagraphRecord]]:
    if not records:
        return []
    if max_size <= 0 or len(records) <= max_size:
        return [records]
    chunk_count = math.ceil(len(records) / max_size)
    base_size = len(records) // chunk_count
    remainder = len(records) % chunk_count
    chunks: list[list[ParagraphRecord]] = []
    cursor = 0
    for chunk_no in range(chunk_count):
        size = base_size + (1 if chunk_no < remainder else 0)
        chunks.append(records[cursor: cursor + size])
        cursor += size
    return chunks


def build_sections(records: list[ParagraphRecord]) -> list[dict]:
    sections: list[dict] = []
    current_records: list[ParagraphRecord] = []
    current_title = ""
    for record in records:
        if current_records and is_candidate_heading(record.text):
            sections.append(
                {
                    "title": current_title,
                    "records": current_records,
                }
            )
            current_records = [record]
            current_title = record.text
            continue
        if not current_records:
            current_records = [record]
            current_title = record.text if is_candidate_heading(record.text) else f"p{record.index}"
        else:
            current_records.append(record)
    if current_records:
        sections.append(
            {
                "title": current_title,
                "records": current_records,
            }
        )
    return sections


def section_titles(group: dict) -> str:
    titles = group.get("titles", [])
    return " / ".join(dict.fromkeys(title for title in titles if title))


def build_focus_chunks(chapter: dict, records: list[ParagraphRecord], chunk_size: int) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    chunk_no = 0
    for section in build_sections(records):
        slices = split_records_balanced(section["records"], chunk_size)
        total_parts = len(slices)
        for part_no, chunk_records in enumerate(slices, start=1):
            chunk_no += 1
            slug = slugify(section["title"])[:24]
            title = f"{chapter['id']}_chunk_{chunk_no:02d}_{slug}"
            lines = [f"# {chapter['label']} / Focus Chunk {chunk_no}", ""]
            lines.append("- Scope: `focus`")
            lines.append(f"- Section: `{section['title']}`")
            if total_parts > 1:
                lines.append(f"- Section part: `{part_no}/{total_parts}`")
            lines.append(f"- Paragraphs: `p{chunk_records[0].index}` to `p{chunk_records[-1].index}`")
            lines.append("")
            lines.extend(format_records(chunk_records))
            chunks.append((title, "\n".join(lines).rstrip() + "\n"))
    return chunks


def build_macro_groups(sections: list[dict], max_size: int) -> list[dict]:
    groups: list[dict] = []
    current_sections: list[dict] = []
    current_count = 0

    def flush_current() -> None:
        nonlocal current_sections, current_count
        if not current_sections:
            return
        groups.append(
            {
                "titles": [section["title"] for section in current_sections],
                "records": [record for section in current_sections for record in section["records"]],
                "part": None,
            }
        )
        current_sections = []
        current_count = 0

    for section in sections:
        section_records = section["records"]
        if max_size > 0 and len(section_records) > max_size:
            flush_current()
            slices = split_records_balanced(section_records, max_size)
            total_parts = len(slices)
            for part_no, chunk_records in enumerate(slices, start=1):
                groups.append(
                    {
                        "titles": [section["title"]],
                        "records": chunk_records,
                        "part": (part_no, total_parts),
                    }
                )
            continue
        if current_sections and max_size > 0 and current_count + len(section_records) > max_size:
            flush_current()
        current_sections.append(section)
        current_count += len(section_records)
    flush_current()
    return groups


def build_macro_chunks(chapter: dict, records: list[ParagraphRecord], chunk_size: int) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    groups = build_macro_groups(build_sections(records), chunk_size)
    for chunk_no, group in enumerate(groups, start=1):
        chunk_records = group["records"]
        title = f"{chapter['id']}_macro_{chunk_no:02d}"
        lines = [f"# {chapter['label']} / Macro Chunk {chunk_no}", ""]
        lines.append("- Scope: `macro`")
        lines.append(f"- Sections: `{section_titles(group)}`")
        if group.get("part"):
            part_no, total_parts = group["part"]
            lines.append(f"- Section part: `{part_no}/{total_parts}`")
        lines.append(f"- Paragraphs: `p{chunk_records[0].index}` to `p{chunk_records[-1].index}`")
        lines.append("")
        lines.extend(format_records(chunk_records))
        chunks.append((title, "\n".join(lines).rstrip() + "\n"))
    return chunks


def build_chapter_packet(chapter: dict, records: list[ParagraphRecord]) -> str:
    lines = [f"# {chapter['label']}", ""]
    lines.append(f"- Range: `{chapter['start']}` to `{chapter['end']}`")
    lines.append(f"- Paragraph count: `{len(records)}`")
    lines.append("")
    lines.append("## Paragraphs")
    lines.extend(format_records(records))
    return "\n".join(lines).rstrip() + "\n"


def objective_context_records(records: list[ParagraphRecord], hit_indexes: list[int], before: int, after: int) -> list[ParagraphRecord]:
    if not hit_indexes:
        return []
    positions = {record.index: pos for pos, record in enumerate(records)}
    selected_indexes: set[int] = set()
    for index in hit_indexes:
        pos = positions.get(index)
        if pos is None:
            continue
        start = max(0, pos - before)
        end = min(len(records), pos + after + 1)
        for record in records[start:end]:
            selected_indexes.add(record.index)
    return [record for record in records if record.index in selected_indexes]


def build_objective_views(paragraphs: list[ParagraphRecord], ranges: list[dict], config: dict) -> list[tuple[str, str]]:
    chapter_records = {
        chapter["id"]: paragraphs_in_chapter(paragraphs, chapter)
        for chapter in ranges
    }
    chapter_meta = {chapter["id"]: chapter for chapter in ranges}
    before = int(config.get("objective_context_before", 1))
    after = int(config.get("objective_context_after", 2))
    packets: list[tuple[str, str]] = []
    for objective in config["research_objectives"]:
        lines = [f"# {objective['label']} / Cross-Chapter Alignment", ""]
        lines.append(f"- Description: `{objective['description']}`")
        lines.append(f"- Context window: `-{before}` / `+{after}` paragraph(s) around each anchor")
        lines.append("")
        for chapter_id in ["ch1", "ch2", "ch3", "ch4", "ch5"]:
            markers = objective["chapter_markers"].get(chapter_id, [])
            records = chapter_records[chapter_id]
            chapter_label = chapter_meta[chapter_id]["label"]
            lines.append(f"## {chapter_label}")
            lines.append(
                "- Markers: " + (", ".join(f"`{marker}`" for marker in markers) if markers else "`-`")
            )
            hits: list[ParagraphRecord] = []
            for marker in markers:
                hits.extend(select_claim_hits(records, marker))
            unique_hits: list[ParagraphRecord] = []
            seen_indexes: set[int] = set()
            for hit in hits:
                if hit.index in seen_indexes:
                    continue
                seen_indexes.add(hit.index)
                unique_hits.append(hit)
            unique_hits.sort(key=lambda item: item.order)
            if not unique_hits:
                lines.append("- Hits: `MISSING`")
                lines.append("")
                continue
            lines.append("- Hits: " + ", ".join(f"`p{hit.index}`" for hit in unique_hits))
            lines.append("")
            lines.extend(format_records(objective_context_records(records, [hit.index for hit in unique_hits], before, after)))
            lines.append("")
        title = f"{objective['id']}_alignment"
        packets.append((title, "\n".join(lines).rstrip() + "\n"))
    return packets


def collect_hits(records: list[ParagraphRecord], term: str) -> list[ParagraphRecord]:
    return [record for record in records if term in record.text]


def select_claim_hits(records: list[ParagraphRecord], marker: str, limit: int = 1) -> list[ParagraphRecord]:
    exact_heading = [record for record in records if record.text == marker and is_candidate_heading(record.text)]
    if exact_heading:
        return exact_heading[:limit]

    exact_any = [record for record in records if record.text == marker]
    if exact_any:
        return exact_any[:limit]

    heading_contains = [record for record in records if marker in record.text and is_candidate_heading(record.text)]
    if heading_contains:
        return heading_contains[:limit]

    contains_any = [record for record in records if marker in record.text]
    return contains_any[:limit]


def chapter_lookup(ranges: list[dict], record: ParagraphRecord) -> str:
    for chapter in ranges:
        if chapter["start_pos"] <= record.order <= chapter["end_pos"]:
            return chapter["id"]
    return "outside"


def build_term_registry(paragraphs: list[ParagraphRecord], ranges: list[dict], config: dict) -> str:
    lines = ["# Term Registry", ""]
    for group_name, group in config["canonical_terms"].items():
        lines.append(f"## {group_name}")
        canonical = group["canonical"]
        all_terms = [canonical] + group.get("alternatives", [])
        for term in all_terms:
            hits = collect_hits(paragraphs, term)
            by_chapter: dict[str, int] = {}
            for hit in hits:
                chapter_id = chapter_lookup(ranges, hit)
                by_chapter[chapter_id] = by_chapter.get(chapter_id, 0) + 1
            dist = ", ".join(f"{k}={v}" for k, v in sorted(by_chapter.items()))
            lines.append(f"- `{term}`: {len(hits)} hit(s)" + (f" [{dist}]" if dist else ""))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_claim_matrix(paragraphs: list[ParagraphRecord], ranges: list[dict], config: dict) -> str:
    chapter_records = {
        chapter["id"]: paragraphs_in_chapter(paragraphs, chapter)
        for chapter in ranges
    }
    lines = ["# Cross-Chapter Claim Matrix", ""]
    lines.append("| Objective | Ch1 framing | Ch2 theory | Ch3 method | Ch4 evidence | Ch5 conclusion |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for objective in config["research_objectives"]:
        row = [objective["label"]]
        for chapter_id in ["ch1", "ch2", "ch3", "ch4", "ch5"]:
            markers = objective["chapter_markers"].get(chapter_id, [])
            refs: list[str] = []
            for marker in markers:
                hits = select_claim_hits(chapter_records[chapter_id], marker)
                refs.extend(f"p{hit.index}" for hit in hits)
            row.append(", ".join(dict.fromkeys(refs)) if refs else "MISSING")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_research_objectives_auto(paragraphs: list[ParagraphRecord], ranges: list[dict], config: dict) -> str:
    chapter_records = {
        chapter["id"]: paragraphs_in_chapter(paragraphs, chapter)
        for chapter in ranges
    }
    chapter_labels = {chapter["id"]: chapter["label"] for chapter in ranges}

    lines = ["# Research Objectives Auto Map", ""]
    lines.append("- Source: machine-generated from `scripts/thesis_mem.py`")
    lines.append("- Preferred objective alignment references: `research_objectives_auto.md` + `claim_matrix.md`")
    lines.append("- `consistency/rules/research_objectives_map.md` is manual reference only and may lag after paragraph-index migrations.")
    lines.append("")

    for objective in config["research_objectives"]:
        lines.append(f"## {objective['label']}")
        lines.append(f"- Description: `{objective['description']}`")
        lines.append("")
        lines.append("| Chapter | Marker(s) | Current hit(s) |")
        lines.append("| --- | --- | --- |")
        for chapter_id in ["ch1", "ch2", "ch3", "ch4", "ch5"]:
            markers = objective["chapter_markers"].get(chapter_id, [])
            refs: list[str] = []
            for marker in markers:
                hits = select_claim_hits(chapter_records[chapter_id], marker)
                refs.extend(f"p{hit.index}" for hit in hits)
            marker_text = "<br>".join(f"`{marker}`" for marker in markers) if markers else "`-`"
            hit_text = ", ".join(dict.fromkeys(refs)) if refs else "MISSING"
            lines.append(f"| {chapter_labels[chapter_id]} | {marker_text} | {hit_text} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_drift_report(paragraphs: list[ParagraphRecord], ranges: list[dict], config: dict, doc_name: str) -> str:
    lines = ["# Thesis Mem Drift Report", ""]
    lines.append(f"- Target: `{doc_name}`")
    lines.append(f"- Paragraphs scanned: `{len(paragraphs)}`")
    lines.append("")

    lines.append("## High-Risk Drift Checks")
    for group_name, group in config["canonical_terms"].items():
        canonical = group["canonical"]
        alternatives = group.get("alternatives", [])
        canonical_hits = collect_hits(paragraphs, canonical)
        alternative_hits = sum(len(collect_hits(paragraphs, term)) for term in alternatives)
        lines.append(
            f"- {group_name}: canonical `{canonical}` = {len(canonical_hits)}, alternatives = {alternative_hits}"
        )
    lines.append("")

    lines.append("## Drift Terms")
    for term in config.get("drift_terms", []):
        hits = collect_hits(paragraphs, term)
        refs = ", ".join(f"p{hit.index}" for hit in hits[:12])
        lines.append(f"- `{term}`: {len(hits)} hit(s)" + (f" at {refs}" if refs else ""))
    lines.append("")

    lines.append("## Chapter Snapshot")
    for chapter in ranges:
        records = paragraphs_in_chapter(paragraphs, chapter)
        lines.append(
            f"- `{chapter['id']}` {chapter['label']}: p{chapter['start']}-p{chapter['end']} / {len(records)} paragraph(s)"
        )
    lines.append("")

    lines.append("## Sample Snippets")
    review_terms = [
        config["canonical_terms"]["core_system_term"]["canonical"],
        *config["canonical_terms"]["core_system_term"].get("alternatives", []),
        *config.get("drift_terms", []),
    ]
    for term in review_terms:
        hits = collect_hits(paragraphs, term)[:5]
        if not hits:
            continue
        lines.append(f"### {term}")
        for hit in hits:
            lines.append(f"- `p{hit.index}` {hit.text[:160]}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_index(paragraphs: list[ParagraphRecord], ranges: list[dict]) -> dict:
    data = {
        "paragraph_count": len(paragraphs),
        "chapters": [],
    }
    for chapter in ranges:
        records = paragraphs_in_chapter(paragraphs, chapter)
        data["chapters"].append(
            {
                "id": chapter["id"],
                "label": chapter["label"],
                "start": chapter["start"],
                "end": chapter["end"],
                "paragraph_count": len(records),
                "section_count": len(build_sections(records)),
            }
        )
    return data


def command_build(source: Path, config_path: Path, outdir: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    paragraphs, source_name = load_source_paragraphs(source, config)
    ranges = chapter_ranges(paragraphs, config)

    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    packets_dir = outdir / "packets"
    reports_dir = outdir / "reports"
    registry_dir = outdir / "registry"
    data_dir = outdir / "data"
    packets_dir.mkdir()
    reports_dir.mkdir()
    registry_dir.mkdir()
    data_dir.mkdir()

    focus_chunk_size = int(config.get("max_paragraphs_per_chunk", 10))
    macro_chunk_size = int(config.get("max_paragraphs_per_macro_chunk", 24))
    for chapter in ranges:
        records = paragraphs_in_chapter(paragraphs, chapter)
        packet = build_chapter_packet(chapter, records)
        write_text(packets_dir / f"{chapter['id']}.md", packet)

        chapter_focus_dir = packets_dir / f"{chapter['id']}_chunks"
        chapter_focus_dir.mkdir()
        for title, body in build_focus_chunks(chapter, records, focus_chunk_size):
            write_text(chapter_focus_dir / f"{title}.md", body)

        chapter_macro_dir = packets_dir / f"{chapter['id']}_macro_chunks"
        chapter_macro_dir.mkdir()
        for title, body in build_macro_chunks(chapter, records, macro_chunk_size):
            write_text(chapter_macro_dir / f"{title}.md", body)

    objective_views_dir = packets_dir / "objective_views"
    objective_views_dir.mkdir()
    for title, body in build_objective_views(paragraphs, ranges, config):
        write_text(objective_views_dir / f"{title}.md", body)

    write_text(registry_dir / "term_registry.md", build_term_registry(paragraphs, ranges, config))
    write_text(registry_dir / "claim_matrix.md", build_claim_matrix(paragraphs, ranges, config))
    write_text(registry_dir / "research_objectives_auto.md", build_research_objectives_auto(paragraphs, ranges, config))
    write_text(reports_dir / "drift_report.md", build_drift_report(paragraphs, ranges, config, source_name))
    write_text(
        outdir / "README.md",
        "\n".join(
            [
                "# Thesis Mem Output",
                "",
                f"- Target: `{source_name}`",
                f"- Config: `{config_path.name}`",
                "",
                "## Directories",
                "- `packets/`: chapter packets, focus chunks, macro chunks, and cross-chapter objective views",
                "- `registry/`: term registry, research objectives auto map, and cross-chapter claim matrix",
                "- `reports/`: drift-focused reports for revision cycles",
                "- `data/`: machine-readable index",
                "",
                "## Packet Layers",
                f"- `ch*_chunks/`: section-aware focus chunks (target <= `{focus_chunk_size}` paragraphs)",
                f"- `ch*_macro_chunks/`: section-aware macro chunks (target <= `{macro_chunk_size}` paragraphs)",
                "- `objective_views/`: cross-chapter alignment packets for each research objective",
                "- `ch*.md`: full-chapter packets for broad review",
                "",
                "## Rebuild",
                f"```powershell\npython scripts/thesis_mem.py build \"{source}\" --config \"{config_path}\" --outdir \"{outdir}\"\n```",
                "",
            ]
        ),
    )
    (data_dir / "index.json").write_text(
        json.dumps(build_index(paragraphs, ranges), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local thesis memory workspace.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build thesis-mem artifacts")
    build_parser.add_argument("source", type=Path, help="Path to the thesis DOCX or shadow markdown directory")
    build_parser.add_argument("--config", type=Path, required=True, help="JSON config path")
    build_parser.add_argument("--outdir", type=Path, required=True, help="Output directory")

    args = parser.parse_args()

    if args.command == "build":
        command_build(args.source, args.config, args.outdir)


if __name__ == "__main__":
    main()
