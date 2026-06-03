# Graduate Thesis Toolkit

這是一套給研究生使用的論文寫作工作流工具，特別適合台灣需要用 Word / DOCX 來回修稿、但又想保留版本控制與 AI 協作紀錄的學生。

它不是某一所學校的正式格式樣板，也不是要取代 LaTeX / Typst / Pandoc。它的目標比較實際：幫「還不知道怎麼開始」的碩士生、碩專班生，把論文從 0 整理成可以交給老師看的初稿。

## 適合誰

- 台灣碩士班、碩專班、在職專班學生
- 題目還不穩、章節還沒成形的人
- 老師主要用 Word / PDF 回饋的人
- 想用 AI 幫忙整理、改寫、檢查，但不想讓修改失控的人
- 想把正文、產出、文獻、規則、老師意見分開管理的人

## 跟一般論文樣板不同的地方

| 類型 | 強項 | 這個工具補的缺口 |
| --- | --- | --- |
| 台灣 LaTeX 論文樣板 | 格式精準、適合熟悉 LaTeX 的學生 | 從 0 開始寫作與 Word 修稿循環比較不直覺 |
| Word 樣板 | 老師和學校容易接受 | 難追蹤版本、AI 修改、章節規則與一致性 |
| Pandoc / Quarto | 多格式輸出強 | 對完全新手與 Word 審稿場景仍偏工程化 |
| 本工具 | 寫作流程、DOCX 產出、段落 ID、AI 可稽核 | 不保證符合任何學校格式，需自行套用校方規定 |

## 從 0 開始怎麼用

先讀：

1. [台灣碩專班從 0 開始指南](docs/taiwan-zero-start-guide.md)
2. [從模糊題目到文獻地圖](docs/vague-topic-to-literature-map.md)
3. [AI 研究夥伴 Playbook](docs/research-partner-playbook.md)
4. [大綱匯入流程](docs/outline-intake-workflow.md)
5. [台灣碩專班最小樣本](examples/tw-professional-master/README.md)
6. [12 週初稿衝刺計畫](docs/professional-master-12-week-plan.md)
7. [指導教授回饋循環](docs/advisor-review-workflow.md)
8. [隱私審查 checklist](docs/privacy-review-checklist.md)

如果你現在只知道一個關鍵字，例如 `PSC`，先不要急著寫第 1 章。先建立文獻地圖工作區：

```powershell
python scripts/init_literature_map.py --topic "PSC" --domain-hint "port state control / maritime safety"
```

再看示例：

- [PSC 文獻地圖示例](docs/psc-literature-map-example.md)

如果你已經有一份大綱，先不要急著讓 AI 全文改寫。先抓出大綱裡可能需要查證的引用：

```powershell
python scripts/extract_citation_candidates.py --input examples/outline-with-citations.md
```

接著依 [大綱匯入流程](docs/outline-intake-workflow.md) 決定下一步：先查證引用、做結構壓力測試、補文獻地圖，或把其中一節拆成可寫作任務。

然後修改：

- `source/shadow/ch1.md`: 緒論
- `source/shadow/ch2.md`: 文獻回顧
- `source/shadow/ch3.md`: 研究方法
- `source/shadow/ch4.md`: 研究結果與分析
- `source/shadow/ch5.md`: 結論與建議

每個段落都有 `## p001` 這種穩定段落 ID。跟 AI 或老師討論時，可以直接說「請改 ch1 p002」，避免整章被亂改。

## 基本指令

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

python scripts/check_public_readiness.py
python scripts/init_literature_map.py --topic "PSC" --domain-hint "port state control / maritime safety"
python scripts/extract_citation_candidates.py --input examples/outline-with-citations.md
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/create_thin_template_v2.py
python scripts/thesis_md_pipeline_v2.py render --skip-pdf
```

如果只想快速試跑公開安全 demo：

```powershell
python scripts/run_demo.py
```

產出的 DOCX 在：

```text
deliverables/docx/thesis_render_v2_latest.docx
```

## 重要提醒

- 這不是學校正式格式保證。
- 這不是代寫工具。
- 不要把真實訪談、個資、未公開研究資料放到公開 repo。
- 若要正式繳交，仍需依學校格式、指導教授要求、系所規定調整。
