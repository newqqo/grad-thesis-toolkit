# Outline Intake Workflow

這份流程用於處理學生上傳的大綱、研究計畫或初稿。

## 目標

把一份可能很模糊的大綱轉成可處理的下一步：

- 先抓疑似引用。
- 再檢查研究結構。
- 再決定要查證、補文獻地圖、壓力測試或改寫。

## Step 1: Extract Citation Candidates

如果大綱是 Markdown、文字檔或 DOCX：

```powershell
python scripts/extract_citation_candidates.py --input path/to/outline.docx --output consistency/reports/citation_candidates.md
```

這只會抓疑似引用，不會驗證真偽。

## Citation Verification Gate

`extract_citation_candidates.py` 只做「候選擷取」。它不能證明文獻存在，也不能證明作者、年份、標題、期刊、DOI 或頁碼正確。

建議把引用分成四種狀態：

| 狀態 | 意義 | 可以做什麼 |
| --- | --- | --- |
| candidate | 文稿中看起來像引用 | 暫時列入查證清單 |
| registered | 已放進本地 literature registry | 可追蹤使用位置，但仍不等於真實驗證 |
| source-checked | 已對照原文或可信資料庫 | 可進入文獻回顧草稿 |
| rejected | 找不到、年份不符、標題不符或來源不可靠 | 刪除或改寫相關論述 |

如果使用本地文獻登錄功能，可以接著跑：

```powershell
python scripts/thesis_library.py scan-thesis-all
python scripts/thesis_library.py audit-refs-sync
python scripts/thesis_library.py render-reports
```

這些命令可以檢查 `source/shadow/refs.md` 與 registry 的同步狀態，但仍不是 DOI 或資料庫真偽查證。真正查證應至少比對 DOI、標題、作者、年份、出版來源，以及文稿中使用的主張是否能被原文支持。

## Step 2: Select A Review Mode

如果有疑似引用：

1. 先做文獻查證。
2. 再做結構壓力測試。
3. 最後才改寫章節。

如果沒有疑似引用：

1. 先做結構完整性檢查。
2. 再建立文獻地圖。
3. 然後回到研究問題與方法。

## Step 3: Structural Checklist

| Item | Check |
| --- | --- |
| Research problem | 是否能用一句話說清楚？ |
| Research question | 是否可回答、可驗證、範圍合理？ |
| Literature gap | 是否不是自己想像，而是文獻支持？ |
| Method | 是否能回答研究問題？ |
| Data | 是否拿得到？ |
| Contribution | 是否回應 gap？ |
| Limitations | 是否誠實揭露？ |

## Step 4: Advisor-Facing Summary

每次處理完大綱，應產出：

```text
本次大綱狀態：
- 已確認的研究方向：
- 仍模糊的部分：
- 需要查證的引用：
- 需要補的文獻群集：
- 建議下一步：
```
