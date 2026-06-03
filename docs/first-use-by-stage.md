# First Use By Student Stage

本系統應先判斷學生目前在哪個階段，而不是一開始就要求學生跑一串指令。

## 先選你的狀態

| 狀態 | 你可能會說 | 第一個目標 | 建議入口 |
| --- | --- | --- | --- |
| A. 還沒有題目 | 我不知道要寫什麼，只知道要開始準備論文。 | 從生活/工作經驗找 3-5 個可研究方向。 | Agent first-use router |
| B. 有模糊方向 | 我想做 PSC、ESG、AI 教學、數位轉型，但不知道怎麼變題目。 | 建立文獻地圖、gap radar、老師問題清單。 | Literature map |
| C. 寫到一半 | 我有第 1-3 章或部分第 4 章，怕概念和文獻亂掉。 | 抓引用候選、概念漂移、章節承諾落差。 | Outline intake + concept audit |
| D. 快完稿 | 我有第 1-5 章，想做口試前嚴格檢查。 | 找出理論承諾落空、引用風險、結論超寫、格式/公開風險。 | Final defense review |

## A. 還沒有題目

可以直接對 agent 說：

```text
我還沒有論文題目。請先不要幫我寫論文，也不要直接給我題目清單。
請先問我 8-10 個問題，從我的工作經驗、可取得資料、老師偏好、時間限制，整理出 3-5 個可研究方向。
每個方向請列出：可能研究問題、需要的文獻關鍵字、可能資料、方法難度、最大風險、下一步。
```

Agent 應做：

- 問問題，不急著寫章節。
- 把生活/工作問題轉成可能研究方向。
- 標明哪些方向資料不可得或太大。
- 建議先建立文獻地圖。

## B. 有模糊方向

可以直接對 agent 說：

```text
我目前只知道想做「<你的關鍵字>」。請幫我建立文獻地圖工作區，不要直接寫文獻回顧。
請把它拆成研究群集、seed paper 搜尋語、可能 gap、可取得資料、適合方法、老師會問的問題。
```

建議 evidence command：

```powershell
python scripts/init_literature_map.py --topic "<你的關鍵字>" --domain-hint "<領域提示>"
```

## C. 寫到一半

可以直接對 agent 說：

```text
我已經有部分草稿。請先不要全文改寫。
請先做引用候選檢查、概念階層樹、理論承諾與實際交付一致性檢查。
請所有判斷都附原句，最後只給最小修改成本方案。
```

建議 evidence commands：

```powershell
python scripts/extract_citation_candidates.py --input <你的大綱或草稿>
python scripts/manuscript_concept_audit.py all --source source/shadow
```

## D. 快完稿

可以直接對 agent 說：

```text
我已接近完稿。請用口試前嚴格審查角度檢查，不要幫我美化文字。
請檢查：第 1 章承諾、第 2 章支撐、第 4 章操作、第 5 章回收、引用風險、概念漂移、結論是否超出證據。
請列出必修、建議修、可不修、可答辯處理四類。
```

建議 evidence commands：

```powershell
python scripts/manuscript_concept_audit.py all --source source/shadow
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/check_public_readiness.py
```

## Skill Or Python

| 工作 | 比較適合 |
| --- | --- |
| 判斷學生目前階段 | Agent skill |
| 問澄清問題 | Agent skill |
| 產生研究方向與老師問題 | Agent skill |
| 抽引用候選 | Python |
| 抽概念候選與原句 | Python |
| 判斷概念是否落空 | Agent skill + Python report |
| 決定最小修改方案 | Agent skill |
| 渲染 DOCX | Python |
| 公開安全掃描 | Python |
