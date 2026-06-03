#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception:
    requests = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

WORKSPACE = Path(__file__).resolve().parents[1]
CURRENT = WORKSPACE
LIB = CURRENT / "assets" / "library"
REGISTRY_DIR = LIB / "registry"
ENTRIES_DIR = LIB / "entries"
INBOX_DIR = LIB / "inbox"
INBOX_PDFS_DIR = INBOX_DIR / "pdfs"
FILES_DIR = LIB / "files"
FILES_PDFS_DIR = FILES_DIR / "pdfs"
REPORTS_DIR = LIB / "reports"
SOURCE_SHADOW = CURRENT / "source" / "shadow"
TABLES_DIR = CURRENT / "assets" / "tables"
REFS_SHADOW = SOURCE_SHADOW / "refs.md"
REGISTRY_JSONL = REGISTRY_DIR / "literature_registry.jsonl"
REGISTRY_MANIFEST = REGISTRY_DIR / "literature_registry.json"
DEFAULT_ENCODING = "utf-8"
SCHEMA_VERSION = 4

METADATA_KEYS = [
    "id", "status", "type", "language", "title", "authors", "year", "doi", "url", "apa7",
    "utility_brief", "citation_tokens", "used_in_thesis", "used_in_journal", "thesis_locations",
    "journal_locations", "access_level", "safe_use_scope", "verification_note", "has_fulltext_pdf",
    "source_path", "original_filename", "updated_at",
]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_write_text(path: Path, content: str) -> None:
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(content, encoding=DEFAULT_ENCODING)
    tmp.replace(path)


def safe_console_write(text: str) -> None:
    payload = text if text.endswith("\n") else f"{text}\n"
    try:
        sys.stdout.write(payload)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(payload.encode("utf-8", errors="backslashreplace"))
    sys.stdout.flush()


def ensure_structure() -> None:
    for path in [REGISTRY_DIR, ENTRIES_DIR, INBOX_DIR, INBOX_PDFS_DIR, FILES_DIR, FILES_PDFS_DIR, REPORTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_JSONL.exists():
        REGISTRY_JSONL.write_text("", encoding=DEFAULT_ENCODING)
    if not REGISTRY_MANIFEST.exists():
        write_manifest([])


def slugify(text: str, limit: int = 48) -> str:
    text = (text or "untitled").lower()
    text = re.sub(r"[^\w\s-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"[_\s]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text[:limit].rstrip("-") or "untitled"


def first_author_slug(authors: str) -> str:
    if not authors:
        return "unknown"
    first = authors.split(";")[0].strip()
    if "," in first:
        first = first.split(",")[0].strip()
    return slugify(first, limit=24)


def build_id(title: str, authors: str, year: str) -> str:
    return slugify(f"{first_author_slug(authors)}-{(year or 'nd').strip() or 'nd'}-{slugify(title, limit=32)}", limit=64)


def normalize_list(value: Optional[List[str]]) -> List[str]:
    if not value:
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def author_families(authors: str) -> List[str]:
    raw = (authors or "").strip().rstrip(".")
    if not raw:
        return []
    # Semicolon-separated: "Perepelkin, M.; Knapp, S."
    if ";" in raw:
        parts = [p.strip() for p in raw.split(";") if p.strip()]
    # APA comma-ampersand: "Perepelkin, M., Knapp, S., & de Pooter, M."
    elif ", &" in raw or " & " in raw:
        # Split by " & " first, then by ", " + uppercase-letter pattern
        raw = raw.replace(", &", ";").replace(" &", ";")
        segments = [s.strip() for s in raw.split(";") if s.strip()]
        parts = []
        for seg in segments:
            # Split "Perepelkin, M., Knapp, S." into individual authors
            # Pattern: family, initials pairs separated by ", "
            sub = re.split(r",\s*(?=[A-Z][a-zÀ-ÿ])", seg)
            parts.extend(s.strip() for s in sub if s.strip())
    else:
        parts = [raw]
    families = []
    for part in parts:
        part = part.strip().rstrip(".")
        if not part:
            continue
        if "," in part:
            family = part.split(",", 1)[0].strip()
        else:
            family = part.split()[-1].strip()
        if family:
            families.append(family)
    return families


def default_citation_tokens(authors: str, year: str) -> List[str]:
    families = author_families(authors)
    year = (year or "").strip()
    if not families or not year:
        return []
    tokens: List[str] = []
    if len(families) == 1:
        stem = families[0]
        tokens.extend([f"{stem}，{year}", f"{stem}, {year}", f"{stem}（{year}）", f"{stem} ({year})"])
    elif len(families) == 2:
        stem = f"{families[0]} & {families[1]}"
        tokens.extend([f"{stem}, {year}", f"{stem}（{year}）", f"{stem} ({year})", f"{families[0]} 與 {families[1]}（{year}）"])
    else:
        stem = f"{families[0]} et al."
        tokens.extend([f"{stem}, {year}", f"{stem}（{year}）", f"{stem} ({year})", f"{families[0]} 等人（{year}）"])
    return tokens


def token_set_for_year(authors: str, year: str) -> set[str]:
    tokens = set(default_citation_tokens(authors, year))
    for token in list(tokens):
        tokens.add(token.replace(", ", "，"))
    return tokens


def citation_token_year(token: str, authors: str, base_year: str) -> str:
    families = author_families(authors)
    if not families or not base_year:
        return ""
    if len(families) == 1:
        stems = [families[0]]
    elif len(families) == 2:
        stems = [f"{families[0]} & {families[1]}", f"{families[0]} 與 {families[1]}"]
    else:
        stems = [f"{families[0]} et al.", f"{families[0]} 等人"]
    for stem in stems:
        escaped = re.escape(stem)
        patterns = [
            rf"^{escaped}\s*[，,]\s*({re.escape(base_year)}[a-z]?)$",
            rf"^{escaped}\s*[（(]\s*({re.escape(base_year)}[a-z]?)\s*[）)]$",
        ]
        for pattern in patterns:
            match = re.match(pattern, token)
            if match:
                return match.group(1)
    return ""


def citation_year_for_tokens(entry: Dict[str, Any]) -> str:
    """Prefer APA suffixes (e.g. 2022a) so same-author-year entries do not cross-match."""
    year = str(entry.get("year") or "").strip()
    apa7 = str(entry.get("apa7") or "")
    for pattern in [r"[（(]\s*(\d{4}[a-z])\s*[）)]", r"\b(\d{4}[a-z])\b"]:
        match = re.search(pattern, apa7)
        if match:
            candidate = match.group(1)
            if not year or candidate.startswith(year):
                return candidate
    return year


def default_entry() -> Dict[str, Any]:
    return {
        "id": "", "status": "candidate", "type": "other", "language": "unknown", "title": "",
        "authors": "", "year": "", "doi": "", "url": "", "apa7": "", "utility_brief": "",
        "citation_tokens": [], "used_in_thesis": False, "used_in_journal": False, "thesis_locations": [],
        "journal_locations": [], "access_level": "unverified", "safe_use_scope": "summary-ok",
        "verification_note": "", "has_fulltext_pdf": False, "source_path": "", "original_filename": "",
        "updated_at": now_iso(),
    }


def normalize_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    entry = default_entry()
    entry.update(raw or {})
    citation_year = citation_year_for_tokens(entry)
    base_year = str(entry.get("year") or "").strip()
    manual_tokens = normalize_list(entry.get("citation_tokens"))
    if citation_year and base_year and citation_year != base_year:
        base_defaults = token_set_for_year(entry.get("authors", ""), base_year)
        filtered_tokens = []
        for token in manual_tokens:
            token_year = citation_token_year(token, entry.get("authors", ""), base_year)
            if token in base_defaults:
                continue
            if token_year and token_year != citation_year:
                continue
            filtered_tokens.append(token)
        manual_tokens = filtered_tokens
    entry["citation_tokens"] = merge_unique(
        manual_tokens,
        default_citation_tokens(entry.get("authors", ""), citation_year),
    )
    entry["thesis_locations"] = normalize_list(entry.get("thesis_locations"))
    entry["journal_locations"] = normalize_list(entry.get("journal_locations"))
    entry["used_in_thesis"] = bool(entry.get("used_in_thesis"))
    entry["used_in_journal"] = bool(entry.get("used_in_journal"))
    entry["has_fulltext_pdf"] = bool(entry.get("has_fulltext_pdf"))
    entry["source_path"] = "" if entry.get("source_path") in [None, "null"] else str(entry.get("source_path") or "")
    entry["original_filename"] = str(entry.get("original_filename") or "")
    entry["updated_at"] = entry.get("updated_at") or now_iso()
    return {k: entry.get(k) for k in METADATA_KEYS}


def write_manifest(entries: List[Dict[str, Any]]) -> None:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "registry_format": "jsonl",
        "registry_path": str(REGISTRY_JSONL),
        "entries_count": len(entries),
        "active_count": sum(1 for x in entries if x.get("status") == "active"),
        "used_in_thesis_count": sum(1 for x in entries if x.get("used_in_thesis")),
        "reports": {
            "library_catalog": str(REPORTS_DIR / "library_catalog.md"),
            "pdf_file_map": str(REPORTS_DIR / "pdf_file_map.md"),
            "thesis_bibliography_active": str(REPORTS_DIR / "thesis_bibliography_active.md"),
            "thesis_bibliography_gaps": str(REPORTS_DIR / "thesis_bibliography_gaps.md"),
        },
        "updated_at": now_iso(),
        "note": "Registry source of truth is literature_registry.jsonl. This JSON file is a compact manifest only.",
    }
    atomic_write_text(REGISTRY_MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2))


def load_registry() -> List[Dict[str, Any]]:
    ensure_structure()
    text = REGISTRY_JSONL.read_text(encoding=DEFAULT_ENCODING) if REGISTRY_JSONL.exists() else ""
    if text.strip():
        return [normalize_metadata(json.loads(line)) for line in text.splitlines() if line.strip()]
    if REGISTRY_MANIFEST.exists():
        try:
            data = json.loads(REGISTRY_MANIFEST.read_text(encoding=DEFAULT_ENCODING))
            if isinstance(data, dict) and isinstance(data.get("entries"), list):
                entries = [normalize_metadata(x) for x in data["entries"]]
                write_registry(entries)
                return entries
        except Exception:
            pass
    return []


def write_registry(entries: List[Dict[str, Any]]) -> None:
    cleaned = [normalize_metadata(x) for x in entries]
    cleaned.sort(key=lambda x: ((x.get("authors") or ""), (x.get("year") or ""), (x.get("title") or ""), x["id"]))
    lines = [json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in cleaned]
    atomic_write_text(REGISTRY_JSONL, "\n".join(lines) + ("\n" if lines else ""))
    write_manifest(cleaned)


def parse_entry_sections(path: Path) -> Dict[str, str]:
    sections = {"摘要": "", "對學位論文的幫助": "", "對期刊稿的幫助": "", "驗證註記": "", "備註": ""}
    if not path.exists():
        return sections
    text = path.read_text(encoding=DEFAULT_ENCODING)
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    for idx, match in enumerate(matches):
        title = match.group(1).strip()
        if title not in sections:
            continue
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def entry_path(entry_id: str) -> Path:
    return ENTRIES_DIR / f"{entry_id}.md"


def write_entry(entry: Dict[str, Any], updates: Optional[Dict[str, str]] = None) -> None:
    path = entry_path(entry["id"])
    sections = parse_entry_sections(path)
    for key, value in (updates or {}).items():
        if key in sections:
            sections[key] = (value or "").strip()
    if not sections["驗證註記"]:
        sections["驗證註記"] = (entry.get("verification_note") or "").strip()
    def fmt_locations(items: List[str]) -> List[str]:
        return [f"- {x}" for x in (items or [])] or ["- "]
    lines = [
        f"# {entry.get('title') or entry['id']}", "",
        f"- `id`：{entry['id']}",
        f"- `status`：{entry.get('status') or ''}",
        f"- `type`：{entry.get('type') or ''}",
        f"- `language`：{entry.get('language') or ''}",
        f"- `used_in_thesis`：{str(bool(entry.get('used_in_thesis'))).lower()}",
        f"- `used_in_journal`：{str(bool(entry.get('used_in_journal'))).lower()}",
        f"- `has_fulltext_pdf`：{str(bool(entry.get('has_fulltext_pdf'))).lower()}",
        f"- `access_level`：{entry.get('access_level') or ''}",
        f"- `safe_use_scope`：{entry.get('safe_use_scope') or ''}",
        f"- `apa7`：{entry.get('apa7') or ''}",
        f"- `doi`：{entry.get('doi') or ''}",
        f"- `url`：{entry.get('url') or ''}",
        f"- `source_path`：{entry.get('source_path') or ''}",
        f"- `original_filename`：{entry.get('original_filename') or ''}",
        f"- `utility_brief`：{entry.get('utility_brief') or ''}",
        "", "## 摘要", "", sections["摘要"], "", "## 對學位論文的幫助", "", sections["對學位論文的幫助"], "", "## 對期刊稿的幫助", "", sections["對期刊稿的幫助"], "",
        "## 目前使用位置", "", "- thesis：", *fmt_locations(entry.get("thesis_locations", [])), "- journal：", *fmt_locations(entry.get("journal_locations", [])), "",
        "## 驗證註記", "", sections["驗證註記"], "", "## 備註", "", sections["備註"], "",
    ]
    path.write_text("\n".join(lines), encoding=DEFAULT_ENCODING)


def load_entries_map() -> Dict[str, Dict[str, Any]]:
    return {e["id"]: e for e in load_registry()}


def merge_unique(existing: List[str], new_items: List[str]) -> List[str]:
    merged = list(existing or [])
    for item in new_items or []:
        if item and item not in merged:
            merged.append(item)
    return merged


def render_reports(entries: List[Dict[str, Any]]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    entries = [normalize_metadata(x) for x in entries]
    entries.sort(key=lambda x: ((x.get("authors") or ""), (x.get("year") or ""), (x.get("title") or "")))
    catalog = ["# Library Catalog", "", f"- 更新時間：{now_iso()}", f"- 總筆數：{len(entries)}", "", "| id | 作者 | 年份 | 題名 | status | thesis | pdf | original |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for e in entries:
        catalog.append(f"| `{e['id']}` | {e.get('authors') or ''} | {e.get('year') or ''} | {e.get('title') or ''} | {e.get('status') or ''} | {'Y' if e.get('used_in_thesis') else ''} | {'Y' if e.get('has_fulltext_pdf') else ''} | {e.get('original_filename') or ''} |")
    (REPORTS_DIR / "library_catalog.md").write_text("\n".join(catalog) + "\n", encoding=DEFAULT_ENCODING)

    pdf_map = ["# PDF File Map", "", f"- 更新時間：{now_iso()}", ""]
    mapped = [e for e in entries if e.get("has_fulltext_pdf")]
    if not mapped:
        pdf_map.append("目前沒有已處理 PDF。")
    else:
        pdf_map.extend(["| id | original filename | canonical pdf |", "| --- | --- | --- |"])
        for e in mapped:
            pdf_map.append(
                f"| `{e['id']}` | {e.get('original_filename') or ''} | {Path(e.get('source_path') or '').name if e.get('source_path') else ''} |"
            )
    (REPORTS_DIR / "pdf_file_map.md").write_text("\n".join(pdf_map) + "\n", encoding=DEFAULT_ENCODING)

    used = [e for e in entries if e.get("used_in_thesis")]
    active = ["# Thesis Bibliography Active", "", f"- 更新時間：{now_iso()}", f"- 已在 thesis 使用：{len(used)}", ""]
    for e in used:
        active.extend([f"## {e.get('title') or e['id']}", "", f"- `id`：{e['id']}", f"- `thesis_locations`：{', '.join(e.get('thesis_locations') or [])}", f"- `apa7`：{e.get('apa7') or ''}", ""])
    (REPORTS_DIR / "thesis_bibliography_active.md").write_text("\n".join(active), encoding=DEFAULT_ENCODING)

    gaps = ["# Thesis Bibliography Gaps", "", f"- 更新時間：{now_iso()}", ""]
    found_gap = False
    for e in entries:
        reasons = []
        if e.get("used_in_thesis") and not e.get("apa7"):
            reasons.append("used_in_thesis 但缺 APA7")
        if e.get("used_in_thesis") and not e.get("citation_tokens"):
            reasons.append("used_in_thesis 但缺 citation_tokens")
        if e.get("used_in_thesis") and not e.get("thesis_locations"):
            reasons.append("used_in_thesis 但缺 thesis_locations")
        if e.get("status") == "active" and e.get("access_level") == "unverified":
            reasons.append("active 但 access_level 未驗證")
        if reasons:
            found_gap = True
            gaps.extend([f"## {e.get('title') or e['id']}", "", f"- `id`：{e['id']}", f"- 問題：{'; '.join(reasons)}", ""])
    if not found_gap:
        gaps.append("目前未發現 bibliographic gaps。")
    (REPORTS_DIR / "thesis_bibliography_gaps.md").write_text("\n".join(gaps) + "\n", encoding=DEFAULT_ENCODING)


def save_entries_map(entries_map: Dict[str, Dict[str, Any]]) -> None:
    entries = list(entries_map.values())
    write_registry(entries)
    render_reports(entries)


def upsert_entry(metadata: Dict[str, Any], detail_updates: Optional[Dict[str, str]] = None, touch_entry: bool = True) -> Dict[str, Any]:
    entries = load_entries_map()
    metadata = dict(metadata)
    entry_id = metadata.get("id") or build_id(metadata.get("title", ""), metadata.get("authors", ""), metadata.get("year", ""))
    metadata["id"] = entry_id
    existing = normalize_metadata(entries.get(entry_id, default_entry()))
    for key, value in metadata.items():
        if key in ["citation_tokens", "thesis_locations", "journal_locations"]:
            existing[key] = merge_unique(existing.get(key, []), value or [])
        elif value not in [None, ""]:
            existing[key] = value
    existing["updated_at"] = now_iso()
    entries[entry_id] = normalize_metadata(existing)
    save_entries_map(entries)
    if touch_entry:
        write_entry(entries[entry_id], detail_updates)
    return entries[entry_id]


def extract_doi(text: str) -> Optional[str]:
    match = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b", text or "", flags=re.IGNORECASE)
    return match.group(1).rstrip(".,);]") if match else None


def extract_pdf_preview(pdf_path: Path, max_pages: int = 3) -> Tuple[str, int]:
    if PdfReader is None:
        return "", 0
    try:
        reader = PdfReader(str(pdf_path))
        pages = len(reader.pages)
        parts = []
        for page in reader.pages[:max_pages]:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                parts.append("")
        return "\n".join(parts).strip(), pages
    except Exception:
        return "", 0


def extract_abstract(text: str) -> str:
    match = re.search(r"\bAbstract\b[:\s]*(.+?)(?:\bKeywords?\b|INTRODUCTION|Introduction|\n[A-Z][A-Z\s]{6,}\n)", text or "", flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", match.group(1)).strip()[:1200] if match else ""


def infer_year(text: str, fallback: str = "") -> str:
    candidates = re.findall(r"\b(19\d{2}|20\d{2})\b", text or "")
    return candidates[0] if candidates else fallback


def infer_title_from_filename(path: Path) -> str:
    name = re.sub(r"[_-]+", " ", path.stem)
    return re.sub(r"\s+", " ", name).strip()


def crossref_lookup(doi: str) -> Dict[str, Any]:
    if not requests or not doi:
        return {}
    try:
        resp = requests.get(f"https://api.crossref.org/works/{doi.strip()}", headers={"User-Agent": "thesis-library/1.0 (local script)"}, timeout=20)
        resp.raise_for_status()
        msg = resp.json().get("message", {})
    except Exception:
        return {}
    title_field = msg.get("title")
    if isinstance(title_field, list):
        title = title_field[0] if title_field else ""
    else:
        title = title_field or ""
    authors = []
    for item in msg.get("author", []) or []:
        family = (item.get("family") or "").strip()
        given = (item.get("given") or "").strip()
        if family and given:
            authors.append(f"{family}, {given}")
        elif family or given:
            authors.append(family or given)
    year = ""
    for field in ["published-print", "published-online", "issued"]:
        parts = msg.get(field, {}).get("date-parts") if isinstance(msg.get(field), dict) else None
        if parts and parts[0]:
            year = str(parts[0][0])
            break
    type_map = {"journal-article": "article", "book": "book", "book-chapter": "chapter", "report": "report", "dissertation": "thesis"}
    pub_type = type_map.get(msg.get("type"), "other")
    container_field = msg.get("container-title")
    if isinstance(container_field, list):
        container = container_field[0] if container_field else ""
    else:
        container = container_field or ""
    volume, issue, pages, publisher = msg.get("volume", ""), msg.get("issue", ""), msg.get("page", ""), msg.get("publisher", "")
    abstract = re.sub(r"<[^>]+>", "", msg.get("abstract", "") or "")
    apa7 = ""
    author_text = "; ".join(authors)
    if author_text and year and title:
        if pub_type == "article":
            vol_issue = volume or ""
            if issue:
                vol_issue = f"{vol_issue}({issue})" if vol_issue else f"({issue})"
            tail = ", ".join([x for x in [container, vol_issue, pages] if x])
            apa7 = f"{author_text}. ({year}). {title}. {tail}. https://doi.org/{doi}" if tail else f"{author_text}. ({year}). {title}. https://doi.org/{doi}"
        else:
            tail = container or publisher
            apa7 = f"{author_text}. ({year}). {title}. {tail}. https://doi.org/{doi}" if tail else f"{author_text}. ({year}). {title}. https://doi.org/{doi}"
    return {"title": title, "authors": "; ".join(authors), "year": year, "type": pub_type, "url": f"https://doi.org/{doi}", "apa7": apa7, "abstract": abstract.strip()}


def canonical_pdf_name(entry: Dict[str, Any], original_filename: str = "") -> str:
    return f"{slugify(entry.get('year') or 'nd', 8)}__{first_author_slug(entry.get('authors') or original_filename or 'unknown')}__{slugify(entry.get('title') or Path(original_filename).stem or entry['id'], 28)}.pdf"


def move_pdf_to_canonical(entry: Dict[str, Any], pdf_path: Path) -> Tuple[Path, str]:
    FILES_PDFS_DIR.mkdir(parents=True, exist_ok=True)
    original = pdf_path.name
    target = FILES_PDFS_DIR / canonical_pdf_name(entry, original)
    expected_stem = target.stem
    # Keep already-canonical files stable, including collision suffixes.
    if pdf_path.parent.resolve() == FILES_PDFS_DIR.resolve():
        if pdf_path.stem == expected_stem or pdf_path.stem.startswith(f"{expected_stem}__"):
            return pdf_path, entry.get("original_filename") or original
    if target.exists() and target.resolve() != pdf_path.resolve():
        stem, suffix, counter = target.stem, target.suffix, 2
        while True:
            candidate = FILES_PDFS_DIR / f"{stem}__{counter}{suffix}"
            if not candidate.exists():
                target = candidate
                break
            counter += 1
    if pdf_path.resolve() != target.resolve():
        shutil.move(str(pdf_path), str(target))
    return target, original


def ingest_pdf(pdf_path: Path, status: str = "candidate") -> Optional[Dict[str, Any]]:
    if not pdf_path.exists():
        return None
    preview, page_count = extract_pdf_preview(pdf_path)
    doi = extract_doi(preview or pdf_path.stem) or ""
    cross = crossref_lookup(doi) if doi else {}
    title = cross.get("title") or infer_title_from_filename(pdf_path)
    authors = cross.get("authors") or ""
    year = cross.get("year") or infer_year(preview, "")
    abstract = extract_abstract(preview) or cross.get("abstract", "")
    metadata = {
        "id": build_id(title, authors, year),
        "status": status,
        "type": cross.get("type") or "other",
        "language": "en" if re.search(r"[A-Za-z]", title or "") else "unknown",
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "url": cross.get("url") or (f"https://doi.org/{doi}" if doi else ""),
        "apa7": cross.get("apa7") or "",
        "utility_brief": "",
        "access_level": "fulltext-confirmed" if page_count else "metadata-confirmed",
        "safe_use_scope": "summary-ok",
        "verification_note": " ".join([x for x in [f"PDF 頁數：約 {page_count} 頁。" if page_count else "", f"DOI 候選：{doi}。" if doi else "", "已由 DOI 自動補充 bibliographic metadata。" if cross else "尚未由 DOI 自動補充 bibliographic metadata。"] if x]).strip(),
        "has_fulltext_pdf": True,
        "source_path": "",
        "original_filename": pdf_path.name,
    }
    canonical, original = move_pdf_to_canonical(metadata, pdf_path)
    metadata["source_path"] = str(canonical)
    metadata["original_filename"] = original
    detail = {"摘要": abstract, "對學位論文的幫助": "", "對期刊稿的幫助": "", "驗證註記": metadata["verification_note"], "備註": (preview[:3000] if preview else "").strip()}
    return upsert_entry(metadata, detail_updates=detail, touch_entry=True)


def scan_thesis_for_entry(entry: Dict[str, Any]) -> List[str]:
    if not (SOURCE_SHADOW.exists() or TABLES_DIR.exists()):
        return []
    results = []
    for path in scan_targets():
        page = None
        for idx, line in enumerate(path.read_text(encoding=DEFAULT_ENCODING).splitlines(), start=1):
            marker = re.match(r"^\s*(?:#+\s*)?(p\d+)\s*$", line)
            if marker:
                page = marker.group(1)
                continue
            if line_matches_entry(entry, line):
                if path.parent == TABLES_DIR:
                    loc = f"{path.stem} line {idx}"
                else:
                    loc = f"{path.stem} {page}" if page else path.stem
                if loc not in results:
                    results.append(loc)
    return results


def best_entry_score(entry: Dict[str, Any]) -> Tuple:
    return (1 if entry.get("status") == "active" else 0, 1 if entry.get("used_in_thesis") else 0, 1 if entry.get("has_fulltext_pdf") else 0, len(entry.get("citation_tokens") or []), len(entry.get("thesis_locations") or []), len(entry.get("apa7") or ""))


def merge_entries(base: Dict[str, Any], other: Dict[str, Any]) -> Dict[str, Any]:
    merged = normalize_metadata(base)
    for key in METADATA_KEYS:
        if key in ["citation_tokens", "thesis_locations", "journal_locations"]:
            merged[key] = merge_unique(merged.get(key, []), other.get(key, []))
        elif key in ["used_in_thesis", "used_in_journal", "has_fulltext_pdf"]:
            merged[key] = bool(merged.get(key)) or bool(other.get(key))
        elif not merged.get(key) and other.get(key):
            merged[key] = other.get(key)
    return normalize_metadata(merged)


def scan_targets() -> List[Path]:
    targets: List[Path] = []
    if SOURCE_SHADOW.exists():
        targets.extend(sorted(SOURCE_SHADOW.glob("ch*.md")))
        appendices = SOURCE_SHADOW / "appendices.md"
        if appendices.exists():
            targets.append(appendices)
    if TABLES_DIR.exists():
        for path in sorted(TABLES_DIR.glob("table_*.md")):
            if "archived" in path.parts:
                continue
            targets.append(path)
    return targets


def simplify_scan_text(text: str) -> str:
    text = (text or "").lower()
    replacements = {
        "（": "(",
        "）": ")",
        "，": ",",
        "；": ";",
        "：": ":",
        "　": " ",
        "《": "",
        "》": "",
        "「": "",
        "」": "",
        "`": "",
        "“": "",
        "”": "",
        "‘": "",
        "’": "",
        "—": "",
        "–": "",
        "-": "",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r"\s+", "", text)
    return text


def scan_needles(entry: Dict[str, Any]) -> List[str]:
    needles: List[str] = []
    needles.extend(normalize_list(entry.get("citation_tokens")))
    title = str(entry.get("title", "") or "").strip()
    author = str(entry.get("authors", "") or "").strip()
    for value in [title, entry.get("apa7", "")]:
        value = str(value or "").strip()
        if value:
            needles.append(value)
    if title:
        stripped_title = re.sub(r"^\s*\d{2,4}\s*年(?:度)?", "", title).strip()
        if stripped_title and stripped_title != title and len(stripped_title) >= 4:
            needles.append(stripped_title)
    title_lower = title.lower()
    if author and ("annual report" in title_lower or "年報" in title):
        needles.append(f"{author} 年報")
        needles.append(f"{author} 年度報告")
    return merge_unique([], needles)


def author_year_fragments(entry: Dict[str, Any]) -> List[Tuple[str, str]]:
    fragments: List[Tuple[str, str]] = []
    for token in normalize_list(entry.get("citation_tokens")):
        match = re.match(r"^(?P<author>.+?)[（(,]\s*(?P<year>\d{4}[a-z]?)", token, flags=re.IGNORECASE)
        if not match:
            continue
        author = match.group("author").strip()
        year = match.group("year").strip()
        if not re.search(r"[a-z]$", year, flags=re.IGNORECASE):
            continue
        fragments.append((author, year))
    return fragments


def line_has_exact_author_year(raw_line: str, author: str, year: str) -> bool:
    if not author or not year:
        return False
    escaped_author = re.escape(author)
    escaped_year = re.escape(year)
    patterns = [
        rf"{escaped_author}\s*[，,]\s*{escaped_year}",
        rf"{escaped_author}\s*[，,][^；;）)]*{escaped_year}",
        rf"{escaped_author}\s*[（(][^）)]*{escaped_year}[^）)]*[）)]",
    ]
    return any(re.search(pattern, raw_line, flags=re.IGNORECASE) for pattern in patterns)


def line_matches_entry(entry: Dict[str, Any], line: str) -> bool:
    raw_line = line or ""
    simple_line = simplify_scan_text(raw_line)
    for needle in scan_needles(entry):
        if needle and needle in raw_line:
            return True
        simple_needle = simplify_scan_text(needle)
        if simple_needle and simple_needle in simple_line:
            return True
    for author, year in author_year_fragments(entry):
        if line_has_exact_author_year(raw_line, author, year):
            return True
    return False


def parse_refs_blocks() -> List[Dict[str, str]]:
    if not REFS_SHADOW.exists():
        return []
    text = REFS_SHADOW.read_text(encoding=DEFAULT_ENCODING)
    blocks: List[Dict[str, str]] = []
    current_p = ""
    buffer: List[str] = []

    def flush() -> None:
        nonlocal current_p, buffer
        if not current_p:
            return
        body = "\n".join(buffer).strip()
        if body and body != "參考文獻":
            blocks.append({"p": current_p, "text": body})
        current_p = ""
        buffer = []

    for line in text.splitlines():
        match = re.match(r"^##\s+(p\d+)\s*$", line.strip())
        if match:
            flush()
            current_p = match.group(1)
            continue
        if current_p:
            buffer.append(line)
    flush()
    return blocks


def refs_match_entry(ref_text: str, entry: Dict[str, Any]) -> bool:
    ref_norm = simplify_scan_text(ref_text)
    if not ref_norm:
        return False
    author = str(entry.get("authors", "") or "").strip()
    year = str(entry.get("year", "") or "").strip()
    first_author = author.split(";")[0].strip() if author else ""
    if "," in first_author:
        first_author = first_author.split(",", 1)[0].strip()
    author_norm = simplify_scan_text(first_author)
    year_norm = simplify_scan_text(year)

    def author_year_match() -> bool:
        if author_norm and year_norm:
            return author_norm in ref_norm and year_norm in ref_norm
        if author_norm:
            return author_norm in ref_norm
        return False

    title = str(entry.get("title", "") or "").strip()
    title_variants = [title]
    stripped_title = re.sub(r"^\s*\d{2,4}\s*年(?:度)?", "", title).strip()
    if stripped_title and stripped_title != title:
        title_variants.append(stripped_title)

    apa7_needle = simplify_scan_text(str(entry.get("apa7", "") or ""))
    if apa7_needle and apa7_needle in ref_norm:
        return True

    for variant in title_variants:
        variant = str(variant or "").strip()
        needle = simplify_scan_text(variant)
        if not needle or needle not in ref_norm:
            continue
        # Short generic titles like "Human error" need author/year co-match,
        # otherwise they incorrectly match longer distinct refs.
        if len(needle) < 24 or len(re.findall(r"\w+", variant)) <= 3:
            if author_year_match():
                return True
            continue
        if author_year_match() or len(needle) >= 40:
            return True
    return False


def render_refs_sync_audit(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    refs_blocks = parse_refs_blocks()
    used_entries = [e for e in entries if e.get("used_in_thesis")]
    registry_missing: List[Tuple[Dict[str, Any], List[Dict[str, str]]]] = []
    registry_ambiguous: List[Tuple[Dict[str, Any], List[Dict[str, str]]]] = []
    refs_missing: List[Tuple[Dict[str, str], List[Dict[str, Any]]]] = []
    refs_ambiguous: List[Tuple[Dict[str, str], List[Dict[str, Any]]]] = []

    for entry in used_entries:
        matches = [block for block in refs_blocks if refs_match_entry(block["text"], entry)]
        if not matches:
            registry_missing.append((entry, matches))
        elif len(matches) > 1:
            registry_ambiguous.append((entry, matches))

    for block in refs_blocks:
        matches = [entry for entry in entries if refs_match_entry(block["text"], entry)]
        if not matches:
            refs_missing.append((block, matches))
        elif len(matches) > 1:
            refs_ambiguous.append((block, matches))

    report_lines = [
        "# Refs Sync Audit",
        "",
        f"- 更新時間：{now_iso()}",
        f"- registry used_in_thesis entries：{len(used_entries)}",
        f"- refs blocks：{len(refs_blocks)}",
        "",
        "此報告僅檢查 `registry` 與 `source/shadow/refs.md` 之對位，不處理正文是否引用、APA 正確性或 DOI 真偽。",
        "",
    ]

    report_lines.extend(["## registry used_in_thesis 但 refs 未匹配", ""])
    if registry_missing:
        for entry, _ in registry_missing:
            report_lines.extend(
                [
                    f"### {entry.get('title') or entry['id']}",
                    "",
                    f"- `id`：{entry['id']}",
                    f"- `thesis_locations`：{', '.join(entry.get('thesis_locations') or [])}",
                    f"- `apa7`：{entry.get('apa7') or ''}",
                    "",
                ]
            )
    else:
        report_lines.append("未發現 `used_in_thesis` 但 `refs.md` 無對應條目的項目。")
        report_lines.append("")

    report_lines.extend(["## refs 條目但 registry 無匹配", ""])
    if refs_missing:
        for block, _ in refs_missing:
            snippet = block["text"].splitlines()[0][:180] if block["text"] else ""
            report_lines.extend(
                [
                    f"### {block['p']}",
                    "",
                    f"- 內容：{snippet}",
                    "",
                ]
            )
    else:
        report_lines.append("未發現 `refs.md` 中無 registry 對應的條目。")
        report_lines.append("")

    report_lines.extend(["## 不確定或多重匹配", ""])
    if registry_ambiguous:
        for entry, matches in registry_ambiguous:
            report_lines.extend(
                [
                    f"### registry -> refs 多重匹配：{entry.get('title') or entry['id']}",
                    "",
                    f"- `id`：{entry['id']}",
                    f"- 匹配 p-marker：{', '.join(block['p'] for block in matches)}",
                    "",
                ]
            )
    if refs_ambiguous:
        for block, matches in refs_ambiguous:
            report_lines.extend(
                [
                    f"### refs -> registry 多重匹配：{block['p']}",
                    "",
                    f"- 可能匹配 ids：{', '.join(entry['id'] for entry in matches)}",
                    "",
                ]
            )
    if not registry_ambiguous and not refs_ambiguous:
        report_lines.append("未發現多重匹配。")
        report_lines.append("")

    report_path = REPORTS_DIR / "refs_sync_audit.md"
    report_path.write_text("\n".join(report_lines), encoding=DEFAULT_ENCODING)
    return {
        "report": str(report_path),
        "registry_used_count": len(used_entries),
        "refs_block_count": len(refs_blocks),
        "registry_missing_count": len(registry_missing),
        "refs_missing_count": len(refs_missing),
        "registry_ambiguous_count": len(registry_ambiguous),
        "refs_ambiguous_count": len(refs_ambiguous),
    }


def cmd_init(_: argparse.Namespace) -> int:
    ensure_structure()
    entries = load_registry()
    save_entries_map({e["id"]: e for e in entries})
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    for e in load_registry():
        if args.used_only and not e.get("used_in_thesis"):
            continue
        safe_console_write(f"{e['id']}\t{e.get('status')}\t{e.get('year')}\t{e.get('title')}")
    return 0


def cmd_upsert(args: argparse.Namespace) -> int:
    # --title is required for new entries, optional for updating existing ones
    if not args.title and args.id:
        existing = load_entries_map()
        if args.id not in existing:
            raise SystemExit("--title is required when creating a new entry")
    elif not args.title and not args.id:
        raise SystemExit("--title is required when creating a new entry (no --id provided)")
    metadata = {
        "id": args.id, "status": args.status, "type": args.type, "language": args.language, "title": args.title,
        "authors": args.authors, "year": args.year, "doi": args.doi, "url": args.url, "apa7": args.apa7,
        "utility_brief": args.utility_brief, "citation_tokens": args.citation_token, "used_in_thesis": args.used_in_thesis,
        "used_in_journal": args.used_in_journal, "thesis_locations": args.thesis_location, "journal_locations": args.journal_location,
        "access_level": args.access_level, "safe_use_scope": args.safe_use_scope, "verification_note": args.verification_note,
        "has_fulltext_pdf": args.has_fulltext_pdf, "source_path": args.source_path, "original_filename": args.original_filename,
    }
    detail = {"摘要": args.summary or "", "對學位論文的幫助": args.thesis_help or "", "對期刊稿的幫助": args.journal_help or "", "驗證註記": args.verification_note or "", "備註": args.notes or ""}
    entry = upsert_entry(metadata, detail_updates=detail, touch_entry=args.touch_entry)
    safe_console_write(entry["id"])
    return 0


def cmd_touch_entry(args: argparse.Namespace) -> int:
    entries = load_entries_map()
    if args.id not in entries:
        raise SystemExit(f"entry not found: {args.id}")
    write_entry(entries[args.id])
    return 0


def cmd_set_usage(args: argparse.Namespace) -> int:
    entries = load_entries_map()
    if args.id not in entries:
        raise SystemExit(f"entry not found: {args.id}")
    entry = entries[args.id]
    entry["used_in_thesis"] = args.used_in_thesis
    entry["used_in_journal"] = args.used_in_journal
    entry["thesis_locations"] = merge_unique(entry.get("thesis_locations", []), args.thesis_location)
    entry["journal_locations"] = merge_unique(entry.get("journal_locations", []), args.journal_location)
    entry["updated_at"] = now_iso()
    save_entries_map(entries)
    write_entry(entry)
    return 0


def cmd_scan_thesis(args: argparse.Namespace) -> int:
    entries = load_entries_map()
    if args.id not in entries:
        raise SystemExit(f"entry not found: {args.id}")
    entry = entries[args.id]
    locations = scan_thesis_for_entry(entry)
    entry["used_in_thesis"] = bool(locations)
    entry["thesis_locations"] = locations
    entry["updated_at"] = now_iso()
    save_entries_map(entries)
    write_entry(entry)
    safe_console_write(json.dumps({"id": entry["id"], "used_in_thesis": entry["used_in_thesis"], "thesis_locations": locations}, ensure_ascii=False, indent=2))
    return 0


def cmd_scan_thesis_all(args: argparse.Namespace) -> int:
    entries = load_entries_map()
    updated = []
    for entry_id in sorted(entries):
        entry = entries[entry_id]
        if args.used_only and not entry.get("used_in_thesis"):
            continue
        if args.active_only and entry.get("status") != "active":
            continue
        locations = scan_thesis_for_entry(entry)
        entry["used_in_thesis"] = bool(locations)
        entry["thesis_locations"] = locations
        entry["updated_at"] = now_iso()
        entries[entry_id] = entry
        updated.append(
            {
                "id": entry_id,
                "used_in_thesis": entry["used_in_thesis"],
                "thesis_locations": locations,
            }
        )
    save_entries_map(entries)
    for entry in entries.values():
        write_entry(entry)
    safe_console_write(json.dumps({"updated": updated}, ensure_ascii=False, indent=2))
    return 0


def cmd_ingest_pdf(args: argparse.Namespace) -> int:
    entry = ingest_pdf(Path(args.path))
    if not entry:
        raise SystemExit("pdf not ingested")
    safe_console_write(entry["id"])
    return 0


def cmd_ingest_inbox(_: argparse.Namespace) -> int:
    ingested = []
    for pdf_path in sorted(INBOX_PDFS_DIR.glob("*.pdf")):
        entry = ingest_pdf(pdf_path)
        if entry:
            ingested.append(entry["id"])
    safe_console_write(json.dumps({"ingested": ingested}, ensure_ascii=False, indent=2))
    return 0


def cmd_resolve_doi(args: argparse.Namespace) -> int:
    cross = crossref_lookup(args.doi)
    if not cross:
        raise SystemExit(f"could not resolve DOI: {args.doi}")
    metadata = {
        "id": args.id, "status": args.status or "candidate", "type": cross.get("type") or "other", "language": args.language or "en",
        "title": cross.get("title") or "", "authors": cross.get("authors") or "", "year": cross.get("year") or "", "doi": args.doi,
        "url": cross.get("url") or f"https://doi.org/{args.doi}", "apa7": cross.get("apa7") or "", "utility_brief": args.utility_brief or "",
        "access_level": args.access_level or ("abstract-confirmed" if cross.get("abstract") else "metadata-confirmed"),
        "safe_use_scope": args.safe_use_scope or "summary-ok", "verification_note": args.verification_note or "由 DOI 自動補充 bibliographic metadata。",
        "has_fulltext_pdf": False,
    }
    detail = {"摘要": cross.get("abstract", ""), "對學位論文的幫助": args.thesis_help or "", "對期刊稿的幫助": args.journal_help or "", "驗證註記": metadata["verification_note"], "備註": ""}
    entry = upsert_entry(metadata, detail_updates=detail, touch_entry=args.touch_entry)
    safe_console_write(entry["id"])
    return 0


def cmd_dedupe(_: argparse.Namespace) -> int:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in load_registry():
        key = entry.get("doi") or f"{entry.get('title')}|{entry.get('year')}"
        groups[key].append(entry)
    deduped = []
    for group in groups.values():
        if len(group) == 1:
            deduped.append(group[0])
            continue
        group.sort(key=best_entry_score, reverse=True)
        winner = group[0]
        for other in group[1:]:
            winner = merge_entries(winner, other)
        deduped.append(winner)
    write_registry(deduped)
    for entry in deduped:
        write_entry(entry)
    render_reports(deduped)
    safe_console_write(json.dumps({"entries_after_dedupe": len(deduped)}, ensure_ascii=False, indent=2))
    return 0


def cmd_rename_id(args: argparse.Namespace) -> int:
    old_id = args.old_id
    new_id = args.new_id
    entries = load_registry()
    target = None
    for e in entries:
        if e["id"] == old_id:
            target = e
            break
    if target is None:
        safe_console_write(f"ERROR: id '{old_id}' not found in registry.")
        return 1
    if any(e["id"] == new_id for e in entries):
        safe_console_write(f"ERROR: id '{new_id}' already exists in registry.")
        return 1
    old_entry_path = entry_path(old_id)
    target["id"] = new_id
    target["updated_at"] = now_iso()
    write_registry(entries)
    write_entry(target)
    if old_entry_path.exists():
        old_entry_path.unlink()
    # Rename PDF if exists
    old_source = target.get("source_path") or ""
    if old_source:
        old_pdf = Path(old_source)
        if old_pdf.exists():
            # Keep the same canonical naming but with new id context
            canonical, _ = move_pdf_to_canonical(target, old_pdf)
            target["source_path"] = str(canonical)
            write_registry(entries)
            write_entry(target)
    render_reports(entries)
    safe_console_write(json.dumps({"renamed": old_id, "to": new_id}, ensure_ascii=False, indent=2))
    return 0


def cmd_render_reports(_: argparse.Namespace) -> int:
    render_reports(load_registry())
    return 0


def cmd_audit_refs_sync(_: argparse.Namespace) -> int:
    result = render_refs_sync_audit(load_registry())
    safe_console_write(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def migrate_existing_registry_and_files() -> None:
    entries = load_registry()
    if not entries:
        return
    changed = False
    for entry in entries:
        src = entry.get("source_path") or ""
        if src:
            pdf_path = Path(src)
            if pdf_path.exists():
                canonical, original = move_pdf_to_canonical(entry, pdf_path)
                if str(canonical) != src:
                    entry["source_path"] = str(canonical)
                    entry["original_filename"] = entry.get("original_filename") or original
                    entry["has_fulltext_pdf"] = True
                    changed = True
    if changed:
        write_registry(entries)
    for entry in entries:
        write_entry(entry)
    render_reports(entries)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain thesis literature registry and detail notes.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.set_defaults(func=cmd_init)
    p = sub.add_parser("list"); p.add_argument("--used-only", action="store_true"); p.set_defaults(func=cmd_list)
    p = sub.add_parser("upsert")
    p.add_argument("--id"); p.add_argument("--status", default="candidate"); p.add_argument("--type", default="other"); p.add_argument("--language", default="unknown")
    p.add_argument("--title", default=""); p.add_argument("--authors", default=""); p.add_argument("--year", default=""); p.add_argument("--doi", default=""); p.add_argument("--url", default="")
    p.add_argument("--apa7", default=""); p.add_argument("--utility-brief", default=""); p.add_argument("--citation-token", action="append", default=[])
    p.add_argument("--used-in-thesis", action="store_true"); p.add_argument("--used-in-journal", action="store_true"); p.add_argument("--thesis-location", action="append", default=[]); p.add_argument("--journal-location", action="append", default=[])
    p.add_argument("--access-level", default="unverified"); p.add_argument("--safe-use-scope", default="summary-ok"); p.add_argument("--verification-note", default="")
    p.add_argument("--has-fulltext-pdf", action="store_true"); p.add_argument("--source-path", default=""); p.add_argument("--original-filename", default="")
    p.add_argument("--summary", default=""); p.add_argument("--thesis-help", default=""); p.add_argument("--journal-help", default=""); p.add_argument("--notes", default=""); p.add_argument("--touch-entry", action="store_true")
    p.set_defaults(func=cmd_upsert)
    p = sub.add_parser("touch-entry"); p.add_argument("--id", required=True); p.set_defaults(func=cmd_touch_entry)
    p = sub.add_parser("set-usage"); p.add_argument("--id", required=True); p.add_argument("--used-in-thesis", action="store_true"); p.add_argument("--used-in-journal", action="store_true"); p.add_argument("--thesis-location", action="append", default=[]); p.add_argument("--journal-location", action="append", default=[]); p.set_defaults(func=cmd_set_usage)
    p = sub.add_parser("scan-thesis"); p.add_argument("--id", required=True); p.set_defaults(func=cmd_scan_thesis)
    p = sub.add_parser("scan-thesis-all"); p.add_argument("--used-only", action="store_true"); p.add_argument("--active-only", action="store_true"); p.set_defaults(func=cmd_scan_thesis_all)
    p = sub.add_parser("ingest-pdf"); p.add_argument("path"); p.set_defaults(func=cmd_ingest_pdf)
    p = sub.add_parser("ingest-inbox"); p.set_defaults(func=cmd_ingest_inbox)
    p = sub.add_parser("resolve-doi")
    p.add_argument("--doi", required=True); p.add_argument("--id"); p.add_argument("--status", default="candidate"); p.add_argument("--language", default="en")
    p.add_argument("--utility-brief", default=""); p.add_argument("--thesis-help", default=""); p.add_argument("--journal-help", default=""); p.add_argument("--access-level", default=""); p.add_argument("--safe-use-scope", default=""); p.add_argument("--verification-note", default=""); p.add_argument("--touch-entry", action="store_true")
    p.set_defaults(func=cmd_resolve_doi)
    p = sub.add_parser("dedupe"); p.set_defaults(func=cmd_dedupe)
    p = sub.add_parser("rename-id"); p.add_argument("--old-id", required=True); p.add_argument("--new-id", required=True); p.set_defaults(func=cmd_rename_id)
    p = sub.add_parser("render-reports"); p.set_defaults(func=cmd_render_reports)
    p = sub.add_parser("audit-refs-sync"); p.set_defaults(func=cmd_audit_refs_sync)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_structure()
    migrate_existing_registry_and_files()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
