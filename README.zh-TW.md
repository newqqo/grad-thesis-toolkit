# Graduate Thesis Toolkit

這是一套給研究生使用的論文寫作工作流工具，特別適合台灣需要用 Word / DOCX 來回修稿、但又想保留版本控制與 AI 協作紀錄的學生。

它不是某一所學校的正式格式樣板，也不是要取代 LaTeX / Typst / Pandoc。它的目標比較實際：幫「還不知道怎麼開始」的碩士生、碩專班生，搭配 Codex、Claude Code、Gemini CLI、Antigravity 或類似 agent，把論文從 0 整理成可以交給老師看的初稿。

## 適合誰

- 台灣碩士班、碩專班、在職專班學生
- 題目還不穩、章節還沒成形的人
- 老師主要用 Word / PDF 回饋的人
- 想用 AI 幫忙整理、改寫、檢查，但不想讓修改失控的人
- 想讓不同 AI agent 都依同一套論文審查規則工作的人
- 想把正文、產出、文獻、規則、老師意見分開管理的人

## 跟一般論文樣板不同的地方

| 類型 | 強項 | 這個工具補的缺口 |
| --- | --- | --- |
| 台灣 LaTeX 論文樣板 | 格式精準、適合熟悉 LaTeX 的學生 | 從 0 開始寫作與 Word 修稿循環比較不直覺 |
| Word 樣板 | 老師和學校容易接受 | 難追蹤版本、AI 修改、章節規則與一致性 |
| Pandoc / Quarto | 多格式輸出強 | 對完全新手與 Word 審稿場景仍偏工程化 |
| 本工具 | 寫作流程、DOCX 產出、段落 ID、跨 agent 工作流、AI 可稽核 | 不保證符合任何學校格式，需自行套用校方規定 |

## 從 0 開始怎麼用

第一次使用，不要先跑所有指令。先判斷你現在是哪一種狀態：

| 你現在的狀態 | 先做什麼 |
| --- | --- |
| 完全還沒題目 | 讀 [完全還沒題目：先從這裡開始](docs/start-here-zero-topic.zh-TW.md)，先讓 agent 問你問題。 |
| 只有模糊方向 | 讀 [第一次使用分流](docs/first-use-by-stage.md)，再建立文獻地圖。 |
| 已經寫到一半 | 先做引用候選、概念階層、理論承諾檢查，不要全文改寫。 |
| 接近完稿 | 走口試前嚴格審查：概念、引用、結論、DOCX readiness。 |

AI 安全模式：

- 不編文獻。
- 不假裝 DOI 或資料已驗證。
- 不一開始就全文改寫。
- 所有引用先標成未驗證候選。
- 重要判斷必須附原句或章節證據。

第一次打開、不知道從哪開始？用靜態新手導覽：選你現在的狀態，就拿到要貼給 AI 的 prompt、對應文件與可選指令。不上傳、不儲存、不需要伺服器，直接用瀏覽器開啟即可：[docs/onboarding.html](docs/onboarding.html)

想直接「跟著做一遍、看到一樣的輸出」？看這份可執行的完整範例：[完整範例：跟著做一遍](docs/walkthrough-end-to-end.zh-TW.md)

先讀：

1. [第一次使用分流](docs/first-use-by-stage.md)
2. [完全還沒題目：先從這裡開始](docs/start-here-zero-topic.zh-TW.md)
3. [台灣碩專班從 0 開始指南](docs/taiwan-zero-start-guide.md)
4. [從模糊題目到文獻地圖](docs/vague-topic-to-literature-map.md)
5. [AI 研究夥伴 Playbook](docs/research-partner-playbook.md)
6. [大綱匯入流程](docs/outline-intake-workflow.md)
7. [概念階層與理論交付檢查](docs/concept-hierarchy-and-promise-check.md)
8. [Agent adapter strategy](docs/agent-adapter-strategy.md)
9. [台灣碩專班最小樣本](examples/tw-professional-master/README.md)
10. [AI 教學 first-use 範例](examples/ai-teaching-first-use/README.md)
11. [學生首次使用模擬報告](docs/user-simulation-report.md)
12. [12 週初稿衝刺計畫](docs/professional-master-12-week-plan.md)
13. [指導教授回饋循環](docs/advisor-review-workflow.md)
14. [競品調查與後續改進清單](docs/competitor-survey-2026.md)
15. [隱私審查 checklist](docs/privacy-review-checklist.md)

如果你現在只知道一個關鍵字，例如 `PSC`，先不要急著寫第 1 章。先建立文獻地圖工作區：

```powershell
python scripts/init_literature_map.py --topic "PSC" --domain-hint "port state control / maritime safety"
```

這會建立前 30 分鐘 checklist、題目釐清卡、搜尋計畫、seed papers、文獻矩陣、證據 registry、AI 使用紀錄、gap radar 與見老師問題。先把文獻標成候選與未驗證，再決定能不能寫進論文。

再看示例：

- [PSC 文獻地圖示例](docs/psc-literature-map-example.md)
- [AI 教學 first-use 範例](examples/ai-teaching-first-use/README.md)

如果你已經有一份大綱，先不要急著讓 AI 全文改寫。先抓出大綱裡可能需要查證的引用：

```powershell
python scripts/extract_citation_candidates.py --input examples/outline-with-citations.md
```

接著依 [大綱匯入流程](docs/outline-intake-workflow.md) 決定下一步：先查證引用、做結構壓力測試、補文獻地圖，或把其中一節拆成可寫作任務。

如果你已經有第 1-5 章草稿，可以檢查概念位階與理論承諾是否真的交付：

```powershell
python scripts/manuscript_concept_audit.py all --source source/shadow
```

如果你已經接近完稿，請讓 agent 依 [第一次使用分流](docs/first-use-by-stage.md) 的 D 路徑輸出「必修、建議修、可不修、可答辯處理」四類，而不是只看 demo 報告。

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
python scripts/manuscript_concept_audit.py all --source source/shadow
python scripts/check_agent_adapters.py
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/create_thin_template_v2.py
python scripts/thesis_md_pipeline_v2.py render --skip-pdf
```

如果只想快速試跑公開安全 demo：

```powershell
python scripts/run_demo.py
```

想確認環境沒問題，可以跑自動化測試（Windows、macOS、Linux 都可以，不需要安裝 Word）：

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

除了 PDF 匯出（需要 Windows 上的 Word）以外，所有腳本都是純 Python，可跨平台執行；CI 也會在 Linux、macOS、Windows 上驗證。

產出的 DOCX 在：

```text
deliverables/docx/thesis_render_v2_latest.docx
```

這個 DOCX 是 toolkit 產物，不等於學校格式已通過。正式提交前仍要檢查封面、摘要、目錄、頁碼、系所規定與 PDF 匯出。

## 重要提醒

- 這不是學校正式格式保證。
- 這不是代寫工具。
- 不要把真實訪談、個資、未公開研究資料放到公開 repo。
- 若要正式繳交，仍需依學校格式、指導教授要求、系所規定調整。
