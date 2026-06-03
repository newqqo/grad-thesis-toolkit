# 學生首次使用模擬報告

這份報告整理四種碩士生第一次使用本系統時可能遇到的情境。模擬結果用來修正 onboarding、agent 分流、文獻流程與完稿審查邊界。

## 模擬使用者

| 使用者類型 | 主要需求 | 最大風險 |
| --- | --- | --- |
| 完全還沒題目 | 需要 agent 先問問題，而不是直接寫論文。 | 一打開 repo 看到 Python/Git 就放棄。 |
| 只有模糊方向 | 只知道 PSC、ESG、AI 教學、數位轉型等關鍵字。 | 跳過種子文獻與 gap logic，直接叫 AI 寫第二章。 |
| 寫到一半 | 有大綱或第 1-3 章，需要診斷。 | 還沒查引用與概念，就要求 AI 全文改寫。 |
| 接近完稿 | 有第 1-5 章，需要口試前審查。 | 把 demo render 誤以為正式提交 readiness。 |

## 主要發現

- README 與繁中 README 需要更明顯的第一次使用分流。
- 完全新手需要不跑 Python、不碰 Git 的入口。
- 題目未釐清前，不應把學生推進 `source/shadow/ch1.md`。
- 文獻地圖模板需要更多繁中說明。
- Codex 與 Antigravity skills 必須明確載入 stage router。
- 寫到一半的學生需要短診斷路徑：引用候選、概念階層、promise-delivery，再做最小修改。
- 快完稿學生需要 formal final-defense review，不是只跑 `run_demo.py`。
- 引用流程要清楚標示：candidate extraction 不等於 source verification。

## 依回饋完成的修正

- 新增 `docs/first-use-by-stage.md`。
- 新增 `docs/start-here-zero-topic.zh-TW.md`。
- 新增 `agents/shared/student-stage-router.md`。
- 新增 Claude 與 Gemini 的 first-use `start` commands。
- 新增 Claude 與 Gemini 的 final-review commands。
- 更新 Codex 與 Antigravity skills，讓它們先讀 stage router。
- 將文獻地圖 workspace 生成內容改成繁中主導。
- 補上 citation candidate extraction 後的查證與 registry sync 說明。
- 補上 final-defense workflow 與 DOCX readiness 警告。

## 產品判斷

Python 應維持在 evidence layer；agent skills/commands 才處理判斷、追問與審查。

| 層次 | 角色 |
| --- | --- |
| Python | 產生檔案、抽候選引用、掃描報告、渲染 DOCX、檢查公開安全。 |
| Agent skill | 分流學生、追問、解讀證據、排序風險、提出最小修改方案。 |
| 學生／指導教授 | 查證來源、核准主張、決定最後研究方向。 |
