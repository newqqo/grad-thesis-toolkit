from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "source" / "shadow"
DEFAULT_REPORT_DIR = ROOT / "consistency" / "reports"

CHAPTER_NUMBER_MAP = {
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
    "十": "10",
}

TERM_SUFFIXES = [
    "場域",
    "脈絡",
    "理論",
    "框架",
    "模型",
    "概念",
    "主軸",
    "構面",
    "面向",
    "單位",
    "因素",
    "機制",
    "關係",
    "變數",
    "流程",
    "策略",
    "方法",
    "工具",
    "措施",
    "指標",
    "資料",
    "系統",
    "平台",
    "作法",
    "程序",
]

UPPER_MARKERS = {"場域", "脈絡", "理論", "框架", "主軸", "高位階", "整體", "宏觀", "制度", "治理"}
MIDDLE_MARKERS = {"分析單位", "構面", "面向", "因素", "機制", "關係", "變數", "流程", "模型"}
LOWER_MARKERS = {"工具", "措施", "操作", "指標", "資料", "系統", "平台", "作法", "程序", "步驟", "問項", "SOP"}
STOP_TERMS = {
    "本研究",
    "本文",
    "本論文",
    "研究問題",
    "研究目的",
    "研究方法",
    "文獻回顧",
    "結論建議",
    "流程",
    "上位研究場域",
    "主要分析單位",
    "主要操作措施",
    "具體工具",
    "研究場域",
    "研究場域的理論",
    "單一資訊工具",
    "清楚的操作措施",
}
PREFIX_NOISE = [
    "本研究以",
    "本研究將",
    "本研究",
    "本文以",
    "本文將",
    "本文",
    "請先寫下",
    "請明確寫出",
    "請整理",
    "請說明",
    "說明",
    "整理",
    "建立",
    "探討",
    "分析",
    "導入",
]
CLAUSE_NOISE = [
    "便難以支撐",
    "既有研究常將",
    "有時將",
    "將",
    "支撐",
    "指出",
    "提出",
    "回收",
    "導入",
    "因此",
    "並以",
    "在",
]
BACKTRACK_STOPS = [
    "則可被",
    "作為",
    "視為",
    "稱為",
    "需要",
    "界定",
    "使用",
    "提出",
    "回收",
    "指出",
    "缺乏",
    "降低",
    "探討",
    "關注",
    "整理",
    "並以",
    "因此",
    "而非",
    "本研究以",
    "本文以",
    "以",
    "將",
    "把",
    "與",
    "和",
    "、",
]


@dataclass(frozen=True)
class SentenceRecord:
    chapter: str
    source: str
    line: int
    text: str


@dataclass
class Occurrence:
    term: str
    level: str
    sentence: SentenceRecord


def read_plain_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        from docx import Document

        doc = Document(path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    raise SystemExit(f"Unsupported file type: {path.suffix}")


def normalize_chapter(raw: str, fallback: str) -> str:
    text = raw.strip()
    if match := re.search(r"ch\s*([1-9][0-9]?)", text, flags=re.IGNORECASE):
        return f"ch{match.group(1)}"
    if match := re.search(r"chapter\s*([1-9][0-9]?)", text, flags=re.IGNORECASE):
        return f"ch{match.group(1)}"
    if match := re.search(r"第\s*([0-9一二三四五六七八九十]+)\s*章", text):
        value = match.group(1)
        return f"ch{CHAPTER_NUMBER_MAP.get(value, value)}"
    return fallback


def file_chapter(path: Path) -> str:
    if match := re.search(r"ch([1-9][0-9]?)", path.stem, flags=re.IGNORECASE):
        return f"ch{match.group(1)}"
    return path.stem


def iter_source_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    files = []
    for path in sorted(source.glob("*.md")):
        if path.name in {"refs.md", "shadow_manifest.json"}:
            continue
        files.append(path)
    return files


def split_sentences(line: str) -> list[str]:
    line = re.sub(r"\s+", " ", line).strip()
    if not line or line.startswith("|") or line.startswith("```"):
        return []
    if re.match(r"^#{1,6}\s+", line):
        return []
    return [item.strip() for item in re.findall(r"[^。！？!?；;\n]+[。！？!?；;]?", line) if item.strip()]


def read_sentences(source: Path) -> list[SentenceRecord]:
    records: list[SentenceRecord] = []
    for path in iter_source_files(source):
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name
        current_chapter = file_chapter(path)
        text = read_plain_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if re.match(r"^#{1,2}\s+", line):
                current_chapter = normalize_chapter(line, current_chapter)
                continue
            for sentence in split_sentences(line):
                records.append(
                    SentenceRecord(
                        chapter=current_chapter,
                        source=str(rel),
                        line=line_no,
                        text=sentence,
                    )
                )
    return records


def clean_term(term: str) -> str:
    term = term.strip(" ，,。；;：:、()（）[]「」『』`")
    for prefix in PREFIX_NOISE:
        if term.startswith(prefix) and len(term) > len(prefix) + 1:
            term = term[len(prefix) :]
    for marker in CLAUSE_NOISE:
        if marker in term and not term.endswith(marker):
            term = term.split(marker)[-1]
    return term.strip(" ，,。；;：:、()（）[]「」『』`")


def concept_before_predicate(sentence: str) -> set[str]:
    terms: set[str] = set()
    patterns = [
        r"([\u4e00-\u9fffA-Za-z0-9]{2,12})作為",
        r"([\u4e00-\u9fffA-Za-z0-9]{2,12})視為",
        r"將([\u4e00-\u9fffA-Za-z0-9]{2,12})稱為",
        r"將([\u4e00-\u9fffA-Za-z0-9]{2,12})視為",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, sentence):
            term = clean_term(match.group(1))
            if 2 <= len(term) <= 12 and term not in STOP_TERMS:
                terms.add(term)
    return terms


def suffix_terms(sentence: str, suffix: str) -> set[str]:
    terms: set[str] = set()
    for match in re.finditer(re.escape(suffix), sentence):
        start = match.start()
        prefix_window = sentence[max(0, start - 14) : start]
        for stop in BACKTRACK_STOPS:
            prefix_window = prefix_window.replace(stop, "|")
        prefix = re.split(r"[|，,。；;：:\s()（）\[\]「」『』]+", prefix_window)[-1]
        term = clean_term(prefix + suffix)
        if 2 <= len(term) <= 14 and term not in STOP_TERMS:
            terms.add(term)
    return terms


def extract_terms_from_sentence(sentence: str) -> set[str]:
    terms: set[str] = set()
    terms.update(concept_before_predicate(sentence))
    for suffix in TERM_SUFFIXES:
        terms.update(suffix_terms(sentence, suffix))
    for match in re.finditer(r"\b[A-Z]{2,}\b", sentence):
        term = match.group(0)
        if term not in {"TODO", "TBD", "FIXME"}:
            terms.add(term)
    return terms


def infer_level(term: str, sentence: str) -> str:
    scores = Counter()
    combined = f"{term} {sentence}"
    for marker in UPPER_MARKERS:
        if marker in combined:
            scores["upper"] += 1
    for marker in MIDDLE_MARKERS:
        if marker in combined:
            scores["middle"] += 1
    for marker in LOWER_MARKERS:
        if marker in combined:
            scores["lower"] += 1
    if not scores:
        return "unclassified"
    ordered = scores.most_common()
    if len(ordered) > 1 and ordered[0][1] == ordered[1][1]:
        return "mixed"
    return ordered[0][0]


def collect_occurrences(sentences: list[SentenceRecord], forced_terms: list[str] | None = None) -> list[Occurrence]:
    terms_filter = {term.strip() for term in forced_terms or [] if term.strip()}
    occurrences: list[Occurrence] = []
    for sentence in sentences:
        terms = set(terms_filter) if terms_filter else extract_terms_from_sentence(sentence.text)
        for term in terms:
            if term and term in sentence.text:
                occurrences.append(Occurrence(term, infer_level(term, sentence.text), sentence))
    return occurrences


def representative(occurrences: list[Occurrence]) -> str:
    if not occurrences:
        return "not found"
    occ = occurrences[0]
    return f"{occ.sentence.chapter} `{occ.sentence.text}`"


def chapters_for(occurrences: list[Occurrence]) -> str:
    chapters = sorted({occ.sentence.chapter for occ in occurrences})
    return ", ".join(chapters) if chapters else "-"


def level_label(level: str) -> str:
    return {
        "upper": "上位場域/高位概念",
        "middle": "中位分析單位",
        "lower": "下位工具/措施/操作概念",
        "mixed": "混合/需人工判定",
        "unclassified": "未分類候選",
    }.get(level, level)


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def group_occurrences(occurrences: list[Occurrence]) -> dict[str, list[Occurrence]]:
    grouped: dict[str, list[Occurrence]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[occurrence.term].append(occurrence)
    return dict(sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])))


def primary_level(occurrences: list[Occurrence]) -> str:
    counts = Counter(occ.level for occ in occurrences)
    return counts.most_common(1)[0][0] if counts else "unclassified"


def term_root(term: str) -> str:
    zh = re.findall(r"[\u4e00-\u9fff]+", term)
    if zh:
        value = zh[0]
        return value[: min(4, max(2, len(value) - 2))]
    return term.split()[0].lower()


def render_concept_tree(sentences: list[SentenceRecord], occurrences: list[Occurrence]) -> str:
    grouped = group_occurrences(occurrences)
    lines = [
        "# Core Concept Hierarchy Audit",
        "",
        "This report uses only the submitted manuscript text. It extracts candidate terms and representative sentences; final conceptual classification still requires human or advisor review.",
        "",
        f"- Sentences scanned: {len(sentences)}",
        f"- Candidate terms found: {len(grouped)}",
        "",
        "## Candidate Concept Tree",
        "",
    ]

    by_level: dict[str, list[tuple[str, list[Occurrence]]]] = defaultdict(list)
    for term, items in grouped.items():
        by_level[primary_level(items)].append((term, items))

    for level in ["upper", "middle", "lower", "mixed", "unclassified"]:
        items = by_level.get(level, [])
        if not items:
            continue
        lines.extend([f"### {level_label(level)}", "", "| Term | Count | Chapters | Representative sentence |", "| --- | ---: | --- | --- |"])
        for term, term_occurrences in items:
            lines.append(
                f"| {escape_cell(term)} | {len(term_occurrences)} | {chapters_for(term_occurrences)} | {escape_cell(representative(term_occurrences))} |"
            )
        lines.append("")

    stable = []
    drift = []
    singletons = []
    for term, items in grouped.items():
        levels = {item.level for item in items}
        if len(items) == 1:
            singletons.append((term, items))
        elif len(levels) == 1:
            stable.append((term, items))
        else:
            drift.append((term, items))

    lines.extend(["## Term Stability", "", "| Term | Status | Evidence |", "| --- | --- | --- |"])
    for term, items in stable[:30]:
        lines.append(f"| {escape_cell(term)} | stable | {escape_cell(chapters_for(items))}; {escape_cell(representative(items))} |")
    for term, items in drift[:30]:
        levels = ", ".join(sorted(level_label(level) for level in {item.level for item in items}))
        lines.append(f"| {escape_cell(term)} | possible rank drift | {escape_cell(levels)}; {escape_cell(representative(items))} |")
    for term, items in singletons[:20]:
        lines.append(f"| {escape_cell(term)} | insufficient evidence | {escape_cell(representative(items))} |")
    lines.append("")

    roots: dict[str, list[str]] = defaultdict(list)
    for term in grouped:
        roots[term_root(term)].append(term)
    conflicts = {root: terms for root, terms in roots.items() if len(set(terms)) > 1}
    lines.extend(["## Possible Same-Level Naming Conflicts", ""])
    if conflicts:
        lines.extend(["| Term family | Terms | Conflict point |", "| --- | --- | --- |"])
        for root, terms in sorted(conflicts.items()):
            unique_terms = sorted(set(terms))
            evidence = "; ".join(f"{term}: {chapters_for(grouped[term])}" for term in unique_terms)
            lines.append(f"| {escape_cell(root)} | {escape_cell(', '.join(unique_terms))} | {escape_cell(evidence)} |")
    else:
        lines.append("No obvious same-family naming conflicts were detected by the heuristic scanner.")
    lines.append("")

    lines.extend(["## Minimum-Change Unification Plan", ""])
    if not grouped:
        lines.append("No candidate concept terms were found. Add explicit concept terms to chapter 1 and rerun the audit.")
    else:
        core_terms = [
            term for term, items in grouped.items() if primary_level(items) in {"upper", "middle"} and len(items) >= 2
        ][:5]
        operational_terms = [term for term, items in grouped.items() if primary_level(items) == "lower"][:8]
        drift_terms = [term for term, _ in drift[:8]]
        lines.append("- Keep as core axis: " + (", ".join(core_terms) if core_terms else "none detected; choose from chapter 1 manually."))
        lines.append("- Treat as lower-level or operational vocabulary: " + (", ".join(operational_terms) if operational_terms else "none detected."))
        lines.append("- Review or rename because of possible rank drift: " + (", ".join(drift_terms) if drift_terms else "none detected."))
        lines.append("- Edit with minimum cost: keep the highest-level term in chapter 1 and chapter 5, then demote tool, measure, and process terms to chapter 3 or chapter 4 operation language.")
    return "\n".join(lines).rstrip() + "\n"


def chapter_occurrences(grouped: dict[str, list[Occurrence]], term: str, chapter: str) -> list[Occurrence]:
    return [occ for occ in grouped.get(term, []) if occ.sentence.chapter == chapter]


def chapter_any(grouped: dict[str, list[Occurrence]], term: str, chapter: str) -> list[Occurrence]:
    return [occ for occ in grouped.get(term, []) if occ.sentence.chapter.startswith(chapter)]


def has_operational_context(occurrences: list[Occurrence]) -> bool:
    return any(occ.level in {"middle", "lower", "mixed"} for occ in occurrences)


def status_with_evidence(items: list[Occurrence], needed: str) -> str:
    if not items:
        return "not found"
    marker = "yes"
    if needed == "operation" and not has_operational_context(items):
        marker = "mentioned only"
    return f"{marker}: {representative(items)}"


def judge_promise_delivery(ch2: list[Occurrence], ch4: list[Occurrence], ch5: list[Occurrence]) -> tuple[str, str]:
    supported = bool(ch2)
    operated = bool(ch4) and has_operational_context(ch4)
    recovered = bool(ch5)
    if supported and operated and recovered:
        return "一致", "保留"
    if not supported and not operated:
        return "明顯落空", "刪除或降階"
    if not operated:
        return "部分落空", "降階"
    if not supported:
        return "部分落空", "改寫"
    if not recovered:
        return "部分落空", "第五章回收"
    return "部分落空", "改寫"


def render_promise_delivery(sentences: list[SentenceRecord], occurrences: list[Occurrence], forced_terms: list[str] | None = None) -> str:
    grouped = group_occurrences(occurrences)
    if forced_terms:
        concepts = [term for term in forced_terms if term in grouped]
    else:
        ch1_terms = []
        for term, items in grouped.items():
            if chapter_any(grouped, term, "ch1") and primary_level(items) in {"upper", "middle", "mixed"}:
                ch1_terms.append((term, len(chapter_any(grouped, term, "ch1")), len(items)))
        concepts = [term for term, _, _ in sorted(ch1_terms, key=lambda item: (-item[1], -item[2], item[0]))[:20]]

    lines = [
        "# Theoretical Promise vs. Delivery Check",
        "",
        "This report checks whether concepts introduced in chapter 1 are supported in chapter 2, operated in chapter 4, and recovered in chapter 5. It uses only manuscript sentences as evidence.",
        "",
        f"- Sentences scanned: {len(sentences)}",
        f"- Chapter-1 concepts checked: {len(concepts)}",
        "",
        "| Concept | Chapter 1 promise | Chapter 2 support | Chapter 4 operation | Chapter 5 recovery | Judgment | Recommendation |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not concepts:
        lines.append("| none | No chapter 1 concept candidates found. |  |  |  | 明顯落空 | Add explicit concepts or pass `--concept`. |")
        return "\n".join(lines).rstrip() + "\n"

    for term in concepts:
        ch1 = chapter_any(grouped, term, "ch1")
        ch2 = chapter_any(grouped, term, "ch2")
        ch4 = chapter_any(grouped, term, "ch4")
        ch5 = chapter_any(grouped, term, "ch5")
        judgment, recommendation = judge_promise_delivery(ch2, ch4, ch5)
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(term),
                    escape_cell(status_with_evidence(ch1, "promise")),
                    escape_cell(status_with_evidence(ch2, "support")),
                    escape_cell(status_with_evidence(ch4, "operation")),
                    escape_cell(status_with_evidence(ch5, "recovery")),
                    judgment,
                    recommendation,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Reading Rule",
            "",
            "- `mentioned only` in chapter 4 means the term appears, but the scanner did not find nearby operation language such as measures, tools, indicators, data, systems, procedures, or analysis units.",
            "- A strict reviewer should verify the table manually and revise any row where the evidence sentence is only decorative.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path}")


def build_context(args: argparse.Namespace) -> tuple[list[SentenceRecord], list[Occurrence]]:
    source = Path(args.source).resolve()
    sentences = read_sentences(source)
    occurrences = collect_occurrences(sentences, getattr(args, "concept", None))
    return sentences, occurrences


def cmd_concept_tree(args: argparse.Namespace) -> None:
    sentences, occurrences = build_context(args)
    write_report(Path(args.output).resolve(), render_concept_tree(sentences, occurrences))


def cmd_promise_delivery(args: argparse.Namespace) -> None:
    sentences, occurrences = build_context(args)
    write_report(Path(args.output).resolve(), render_promise_delivery(sentences, occurrences, args.concept))


def cmd_all(args: argparse.Namespace) -> None:
    sentences, occurrences = build_context(args)
    output_dir = Path(args.output_dir).resolve()
    write_report(output_dir / "concept_hierarchy_report.md", render_concept_tree(sentences, occurrences))
    write_report(output_dir / "promise_delivery_report.md", render_promise_delivery(sentences, occurrences, args.concept))


def add_shared(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="Input directory or .md/.txt/.docx manuscript")
    parser.add_argument("--concept", action="append", default=[], help="Force a concept term to audit; repeatable")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit manuscript concept hierarchy and promise-delivery consistency.")
    sub = parser.add_subparsers(dest="cmd")

    concept_tree = sub.add_parser("concept-tree")
    add_shared(concept_tree)
    concept_tree.add_argument("--output", default=str(DEFAULT_REPORT_DIR / "concept_hierarchy_report.md"))
    concept_tree.set_defaults(func=cmd_concept_tree)

    promise_delivery = sub.add_parser("promise-delivery")
    add_shared(promise_delivery)
    promise_delivery.add_argument("--output", default=str(DEFAULT_REPORT_DIR / "promise_delivery_report.md"))
    promise_delivery.set_defaults(func=cmd_promise_delivery)

    all_cmd = sub.add_parser("all")
    add_shared(all_cmd)
    all_cmd.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR))
    all_cmd.set_defaults(func=cmd_all)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
