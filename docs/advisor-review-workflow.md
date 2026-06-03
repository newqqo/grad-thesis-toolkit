# 指導教授回饋循環

這份文件說明如何用本工具管理老師回饋，避免每次修稿都變成「找不到哪裡改過」。

## 基本原則

- 正文主控來源是 `source/shadow`，不是 Word 檔。
- Word / PDF 是交付與審閱用輸出。
- 老師意見要回到段落 ID，例如 `ch2 p104`。
- 每次交稿都附上「本次修改摘要」與「需要老師判斷的問題」。

## 建議流程

1. 修改 `source/shadow`。
2. 執行檢查：

```powershell
python scripts/thesis_style_scan.py scan
python scripts/thesis_consistency_audit.py
python scripts/thesis_md_pipeline_v2.py render --skip-pdf
```

3. 交付 `deliverables/docx/thesis_render_v2_latest.docx`。
4. 將老師意見整理成段落層級清單。
5. 下一輪只針對清單修正，不順手大改其他章。

## 給老師的交稿摘要範本

```text
老師您好，這次交付的是第 X 版初稿。

本次主要修改：
1. ch1 p001-p003：收斂研究動機與問題意識。
2. ch2 p101-p105：補上核心概念與文獻分類。
3. ch3 p201-p204：確認研究方法與資料來源。

想請老師協助判斷：
1. 研究問題是否仍然太大？
2. 第 3 章的方法是否足以回答研究問題？
3. 第 2 章文獻分類是否缺重要方向？
```

## AI 協作注意事項

適合交給 AI：

- 檢查段落是否偏離章節功能。
- 將口語草稿改成學術語氣。
- 找出研究目的、方法、結論是否不一致。
- 產生交稿摘要。

不適合交給 AI：

- 創造不存在的訪談資料。
- 杜撰文獻。
- 代替老師決定研究設計。
- 在沒有資料支持下補第 4 章結果。

