from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "literature"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "topic"


def write_once(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def topic_brief(topic: str, domain_hint: str) -> str:
    return f"""# 題目釐清卡 Topic Brief

## 原始關鍵字

{topic}

## 領域提示

{domain_hint or "尚未指定。"}

## 五句話釐清

1. 我對這個題目有興趣，因為：
2. 我觀察到的實務問題是：
3. 受到影響的人、組織或系統是：
4. 我可能取得的資料或證據是：
5. 我這篇論文可能回答的問題是：

## 題目收斂表

| 層次 | 暫定答案 |
| --- | --- |
| 原始關鍵字 | {topic} |
| 實務脈絡 | |
| 學術領域 | |
| 核心概念 | |
| 可能結果變項或分析對象 | |
| 可能方法 | |
| 可取得資料來源 | |

## 見老師前檢查

- 這個題目是否太大？
- 是否真的有資料來源？
- 這是可研究的論文問題，還只是工作抱怨？
- 這個題目最難寫的是哪一章？
"""


def search_plan(topic: str) -> str:
    return f"""# 文獻搜尋計畫 Search Plan

## 目標

把模糊關鍵字 `{topic}` 變成可以跟指導教授討論的文獻地圖。

## Step 1: 先找種子文獻 Seed Papers

不要只用一個工具。建議至少用 2-3 種搜尋來源互相補盲點。

可用來源：

- Google Scholar / 學校圖書館資料庫
- Elicit 或其他語意搜尋工具
- SciSpace 或其他論文閱讀工具
- Scopus / Web of Science，如果學校有訂閱

起始搜尋語：

- `{topic} literature review`
- `{topic} systematic review`
- `{topic} research gap`
- `{topic} determinants`
- `{topic} trend`
- `{topic} Taiwan`
- `{topic} Asia`

## Step 2: 記錄種子文獻

挑 5-10 篇看起來像核心起點的文獻。先不要相信 AI 摘要，先把它們記到 `seed-papers.md`。

## Step 3: 引文擴張 Citation Expansion

如果可以，至少用一個引用地圖工具：

- Litmaps
- ResearchRabbit
- Connected Papers

擴張目標：

- 較早的基礎文獻
- 引用種子文獻的新文獻
- 綜述型文獻
- 使用不同方法的文獻
- 台灣或鄰近脈絡的文獻

## Step 4: 建立文獻矩陣

填寫 `literature-matrix.csv`。最低限度要能回答這些欄位：

- citation：引用資訊
- year：年份
- country_or_region：國家或區域
- topic_cluster：研究群集
- theory_or_framework：理論或框架
- method：方法
- data_source：資料來源
- key_findings：主要發現
- limitations：限制
- gap_claim：作者宣稱的缺口
- relevance_to_my_thesis：跟我論文的關係
- verification_status：是否已對照原文

同時填寫 `evidence-registry.csv`。每一篇要進入矩陣的文獻，都需要留下 DOI/URL、搜尋來源、搜尋日期、查證狀態，以及支撐哪個矩陣欄位。

## Step 5: 缺口雷達 Gap Radar

用 `gap-radar.md` 分類可能缺口：

- 脈絡缺口 context gap
- 方法缺口 method gap
- 資料缺口 data gap
- 理論缺口 theory gap
- 實務落地缺口 practical implementation gap
- 台灣或在地化缺口 Taiwan/localization gap

## 安全規則

AI 可以幫忙搜尋、分類與摘要，但任何要寫進論文的主張，都必須回到原文查證。

每一次使用 AI 協助文獻搜尋、分類或改寫，都先記到 `ai-usage-log.md`。
"""


def seed_papers() -> str:
    return """# 種子文獻 Seed Papers

在這裡放 5-10 篇作為起點的文獻。

| 狀態 | 引用資訊 | 為何適合作為種子 | 來源連結 | 已對照原文？ |
| --- | --- | --- | --- | --- |
| candidate | | | | no |

## 判斷提醒

- 種子文獻不是「有提到關鍵字」就算。
- 優先選綜述文獻、高引用文獻、近年文獻，以及能定義主要爭論的文獻。
- 如果兩個 AI 或搜尋工具結果完全不重疊，先保留兩組，再比較差異原因。
"""


def literature_matrix() -> str:
    return (
        "citation,year,country_or_region,topic_cluster,theory_or_framework,method,"
        "data_source,key_findings,limitations,gap_claim,relevance_to_my_thesis,"
        "verification_status,notes\n"
    )


def evidence_registry() -> str:
    return (
        "source_id,citation_or_title,doi_or_url,database_or_tool,search_query,"
        "search_date,screening_status,verification_status,evidence_location,"
        "supporting_quote_or_note,matrix_fields_supported,human_verified_by,notes\n"
        "S001,,,,,,candidate,unverified,,,,,\n"
    )


def ai_usage_log() -> str:
    return """# AI 使用紀錄 AI Usage Log

Use this log when an AI agent helps with topic framing, literature mapping, outline repair, or chapter revision. It is a disclosure aid, not proof that the output is correct.

| Date | Agent/tool | Task | Input scope | Private text removed? | Output used? | Human verification | Disclosure note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | | | de-identified summary / outline / short excerpt | yes/no | accepted / revised / rejected | pending / checked against source / advisor reviewed | |

## Rules

- Do not paste private interview transcripts, personal identifiers, school-only forms, or unpublished full chapters into public tools.
- Treat literature suggestions as candidates until the original source is checked.
- Record rejected AI outputs too when they influenced your next step.
- Keep the final academic judgment with the student and advisor.
"""


def first_30_minutes(topic: str) -> str:
    return f"""# 前 30 分鐘 Checklist

題目或關鍵字：{topic}

This checklist gives a first-time student a concrete first session. It does not require external credentials, paid services, uploads, or private thesis text.

## 0-5 分鐘：安全邊界

- [ ] 只使用去識別化摘要、公開資料、章節大綱或短段落。
- [ ] 不貼私人訪談逐字稿、個資、真實公司內部資料、未公開完整章節。
- [ ] 在 `ai-usage-log.md` 開一筆紀錄。

## 5-10 分鐘：釐清自己真正能做什麼

- [ ] 填 `topic-brief.md` 的五句話釐清。
- [ ] 寫下可取得資料來源，而不是只寫想研究的概念。
- [ ] 標出目前最不確定的一件事。

## 10-20 分鐘：建立可查證的文獻入口

- [ ] 依 `search-plan.md` 產生 3-5 組搜尋語。
- [ ] 找 3 篇可能的 seed papers，先放進 `seed-papers.md`。
- [ ] 每篇都同步登錄到 `evidence-registry.csv`，狀態先標 `candidate` / `unverified`。

## 20-30 分鐘：準備見老師

- [ ] 在 `gap-radar.md` 寫下 1-2 個可能缺口。
- [ ] 在 `advisor-questions.md` 寫下 3 個要問老師的問題。
- [ ] 決定下一次工作只做一件事：查證文獻、補資料來源、縮小題目，或寫一頁初步大綱。
"""


def gap_radar(topic: str) -> str:
    return f"""# 缺口雷達 Gap Radar

題目：{topic}

## 目前研究群集

| 群集 | 代表文獻 | 這個群集已知道什麼 | 還沒解決什麼 |
| --- | --- | --- | --- |
| | | | |

## 缺口類型

| 缺口類型 | 文獻證據 | 可能論文角度 |
| --- | --- | --- |
| 脈絡缺口 | | |
| 台灣／在地缺口 | | |
| 方法缺口 | | |
| 資料缺口 | | |
| 理論缺口 | | |
| 實務落地缺口 | | |

## 我可以站的位置

1. 我可以把既有研究延伸到台灣或特定場域，方式是：
2. 我可以比較不同方法，方式是：
3. 我可以使用不同資料來源，方式是：
4. 我可以把學術文獻和實務問題接起來，方式是：
5. 我應避免的方向是，因為它太大或資料不可得：

## 候選研究問題

| 候選問題 | 為何可研究 | 需要資料 | 風險 |
| --- | --- | --- | --- |
| | | | |
"""


def advisor_questions(topic: str) -> str:
    return f"""# 指導教授討論問題 Advisor Questions

在跟指導教授討論 `{topic}` 前，先填這一頁。

## 我目前知道什麼

- 我的原始題目是：
- 目前最重要的種子文獻是：
- 我看到的主要研究群集是：
- 最有可能的缺口是：

## 需要老師幫忙判斷

1. 這個題目是否適合碩士論文？
2. 哪個方向太大或太淺？
3. 系上可接受的方法是什麼？
4. 哪種資料來源才有足夠可信度？
5. 哪一群文獻必須先讀？

## 會議後記錄

跟老師討論後，填寫：

- 通過方向：
- 暫時排除方向：
- 接下來要讀的 3 篇文獻：
- 接下來要確認的資料來源：
- 接下來要寫的章節或段落：
"""


def ai_prompts(topic: str) -> str:
    return f"""# AI 提示詞 AI Prompts

可把這些提示詞交給 AI 助手。所有輸出都要回到原文查證。

## 釐清題目

```text
我目前只知道想研究「{topic}」。請先問我 10 個釐清問題，再提出 5 個較窄的碩士論文方向。每個方向請說明需要資料、可能方法、最大風險，以及見老師前要準備什麼。
```

## 建立搜尋語

```text
請為「{topic}」建立英文與繁體中文搜尋語，分成：綜述文獻、近年趨勢、研究方法、台灣／在地脈絡、研究缺口。請提供 Boolean query 版本。
```

## 分類文獻

```text
請根據這份文獻矩陣，把文獻分成研究群集。每個群集請整理：已知結論、常用方法、仍存在的缺口。不要捏造不存在的文獻。
```

## 挑戰缺口

```text
請扮演嚴格的指導教授。根據這份 gap radar，指出哪個缺口太模糊、哪個缺口適合碩士論文，以及我必須蒐集哪些資料才能站得住腳。
```
"""


def build(args: argparse.Namespace) -> Path:
    topic = args.topic.strip()
    slug = args.slug.strip() if args.slug else slugify(topic)
    target = Path(args.output_root).resolve() / slug
    overwrite = bool(args.overwrite)

    write_once(target / "topic-brief.md", topic_brief(topic, args.domain_hint), overwrite)
    write_once(target / "search-plan.md", search_plan(topic), overwrite)
    write_once(target / "seed-papers.md", seed_papers(), overwrite)
    write_once(target / "literature-matrix.csv", literature_matrix(), overwrite)
    write_once(target / "evidence-registry.csv", evidence_registry(), overwrite)
    write_once(target / "ai-usage-log.md", ai_usage_log(), overwrite)
    write_once(target / "first-30-minutes.md", first_30_minutes(topic), overwrite)
    write_once(target / "gap-radar.md", gap_radar(topic), overwrite)
    write_once(target / "advisor-questions.md", advisor_questions(topic), overwrite)
    write_once(target / "ai-prompts.md", ai_prompts(topic), overwrite)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a literature-map workspace for a vague thesis topic.")
    parser.add_argument("--topic", required=True, help="Raw topic keyword or phrase, e.g. PSC")
    parser.add_argument("--domain-hint", default="", help="Optional domain hint, e.g. maritime safety")
    parser.add_argument("--slug", default="", help="Optional output folder name")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    target = build(args)
    print(f"created literature map workspace: {target}")


if __name__ == "__main__":
    main()
