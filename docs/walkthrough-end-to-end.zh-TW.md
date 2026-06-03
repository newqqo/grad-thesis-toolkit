# 完整範例：跟著做一遍（用內建公開資料）

這份文件把散在各處的工作流接成「一條可實際執行」的路徑。每個步驟都用 repo 內建的**公開占位資料**，你可以照著貼指令、看到一樣的輸出，再對照「這代表什麼、下一步該做什麼」。

> 這不是代寫。工具只負責「抓候選、找缺口、做檢查」，學術判斷由你和指導教授決定。

跟著做之前，先確認環境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

非 Windows（macOS / Linux）也可以，只是 PDF 匯出那一步需要 Windows + Word；其餘全部跨平台。

---

## 階段 1：只有一個關鍵字 → 文獻地圖

情境：你只知道想做「PSC（港口國管制）」，還不知道能切什麼題目。

```powershell
python scripts/init_literature_map.py --topic "PSC" --domain-hint "port state control / maritime safety"
```

會在 `literature/psc/` 產生一個工作區：

| 檔案 | 你要填什麼 |
| --- | --- |
| `topic-brief.md` | 你的初步動機、可能的資料來源、為什麼值得做 |
| `search-plan.md` | 中英文檢索詞、資料庫、納入/排除條件 |
| `seed-papers.md` | 3–5 篇種子論文（先填你已知的，其餘標未驗證） |
| `literature-matrix.csv` | 逐篇整理：研究問題、方法、資料、結論、缺口 |
| `gap-radar.md` | 國內外研究還沒做的、可切入的空隙 |
| `advisor-questions.md` | 見老師前要問的問題 |
| `ai-prompts.md` | 給 AI 當研究夥伴的提示，全部要求標「未驗證候選」 |

**下一步決策**：填完 matrix 後，看 `gap-radar.md`，挑 1–2 個你「有資料、做得到、老師可能接受」的方向，再進階段 2。

> 提醒：你自己建立的題目工作區（例如 `literature/我的題目/`）預設不會進 git，避免不小心把私人研究筆記推上公開倉庫。只有內建的 `psc` 範例會被追蹤。

---

## 階段 2：已有大綱 → 先抓引用候選，不要急著全文改寫

情境：你已經有一份含引用的大綱。先別讓 AI 重寫，先確認哪些引用需要查證。

```powershell
python scripts/extract_citation_candidates.py --input examples/outline-with-citations.md
```

輸出長這樣（完整版見 [docs/sample-outputs/citation-candidates.md](sample-outputs/citation-candidates.md)）：每一筆都標成 `unverified`，分成 `author-year`、`doi`、`zh-author-year`、`title-year`。

**怎麼讀 / 下一步**：

- 每一筆都先當「**還沒驗證**」。逐筆用 DOI、標題、作者、年份、資料庫核對原始文獻。
- 確認為真，才寫進論文；查不到或對不上的，標記存疑，不要擴張論述。
- 全部核完後，再決定是否做結構壓力測試、補文獻地圖，或把某一節拆成寫作任務。

順序原則：**先驗證證據，再擴張主張**。

---

## 階段 3：寫到一半 → 概念位階與「承諾是否兌現」檢查

情境：你已經有第 1–5 章草稿，想知道第 1 章丟出的大概念，後面有沒有真的接住。

先看概念樹（詞彙位階、是否漂移）：

```powershell
python scripts/manuscript_concept_audit.py concept-tree --source examples/concept-drift-sample.md
```

再看「承諾 vs 交付」（第 1 章提出 → 第 2 章支撐 → 第 4 章操作 → 第 5 章回收）：

```powershell
python scripts/manuscript_concept_audit.py promise-delivery --source examples/concept-drift-sample.md --concept "數位轉型" --concept "服務流程治理框架" --concept "顧客回應機制"
```

用內建範例，你會看到（完整版見 [docs/sample-outputs/promise-delivery.md](sample-outputs/promise-delivery.md)）：

| 概念 | 判斷 | 為什麼 |
| --- | --- | --- |
| 數位轉型 | **一致** | 第 1 章當場域、第 2 章定義、第 4 章操作、第 5 章回收都有句子 |
| 服務流程治理框架 | **部分落空** | 第 4 章找不到「操作語言」（措施／工具／指標／資料／分析單位） |
| 顧客回應機制 | **部分落空** | 同上：被提到，但沒有被真正操作 |

**怎麼讀 / 怎麼用最小改動修**：

- 「部分落空」通常不是要你刪概念，而是兩條路二選一：
  1. **降階**：把它從「框架／場域」降成「分析單位／工具」，讓承諾與實作對齊；或
  2. **補操作**：在第 4 章補上它的具體措施、指標、資料或程序，把承諾接住。
- 表格只是「掃描器的提示」，不是定論。每一列都要回原文人工確認，再決定改法。

這一步最能擋下口試常見的致命傷：第 1 章講了大理論，第 4 章卻沒真的做。

---

## 階段 4：接近完稿 → 嚴格檢查，分「必修 / 可選」

```powershell
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/check_public_readiness.py
```

- **style scan**：抓 `TODO`/`TBD` 這類流程佔位字，與 `clearly`、`obviously`、`generally` 這類沒證據的強調語。
- **consistency audit**：檢查術語是否一致、章節責任是否照「章節契約」。
- **public readiness**：掃 email、本機路徑、疑似金鑰等不該公開的內容（提交公開前必跑）。

**分類原則**：把結果分成「必修（會在口試被打）／建議修／可不修／可在口試現場用說明處理」，不要全部一視同仁。

---

## 產出 Word 初稿

```powershell
python scripts/create_thin_template_v2.py
python scripts/thesis_md_pipeline_v2.py render --skip-pdf
```

DOCX 會輸出在 `deliverables/docx/thesis_render_v2_latest.docx`。在 Windows 且裝了 Word，可去掉 `--skip-pdf` 一併匯出 PDF。

> 這份 DOCX 是工具產物，**不等於**學校格式已通過。正式繳交前仍要自行套用封面、摘要、目錄、頁碼與系所規定。

---

## 一次跑完（公開安全 demo）

想一口氣看完整條流程：

```powershell
python scripts/run_demo.py
```

它會依序跑公開檢查、文獻地圖、引用候選、概念稽核、風格與一致性、DOCX 產出，全部用占位資料，不碰你的私人內容。

---

## 對照：你現在在哪一站？

| 你的狀態 | 從哪個階段開始 |
| --- | --- |
| 還沒題目 | 先讀 [從 0 開始：還沒有題目](start-here-zero-topic.zh-TW.md)，讓 agent 先訪談你 |
| 只有關鍵字 | 階段 1 |
| 有大綱 | 階段 2 |
| 寫到一半 | 階段 3 |
| 接近完稿 | 階段 4 |
