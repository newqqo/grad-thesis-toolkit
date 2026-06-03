# 從模糊題目到文獻地圖

多數碩士生最痛苦的不是不會排版，而是不知道自己到底要研究什麼。常見起點只有一個模糊詞：

- PSC
- ESG
- AI 教學
- 服務品質
- 職場壓力
- 數位轉型

這些詞不能直接變成論文題目。它們必須先變成文獻地圖。

## 工作流總覽

```text
模糊詞
  -> 題目澄清
  -> 語意搜尋 seed papers
  -> 引用地圖擴張
  -> 文獻矩陣
  -> gap radar
  -> 可研究問題
  -> 第 1-3 章初稿
```

## 建立工作區

```powershell
python scripts/init_literature_map.py --topic "PSC" --domain-hint "port state control / maritime safety"
```

這會建立：

```text
literature/psc/
├── topic-brief.md
├── search-plan.md
├── seed-papers.md
├── literature-matrix.csv
├── gap-radar.md
├── advisor-questions.md
└── ai-prompts.md
```

## 為什麼不能只問 AI「幫我找文獻」

因為 AI 和搜尋工具各有盲點。同一個主題，用不同工具可能找到不同文獻集合。比較穩的做法是：

1. 用語意搜尋找 seed papers。
2. 用引用地圖工具擴張上下游文獻。
3. 用傳統資料庫或 Google Scholar 交叉確認。
4. 把結果放入文獻矩陣。
5. 回到原文驗證，不把 AI 摘要直接寫進論文。

## 文獻矩陣最小欄位

| 欄位 | 用途 |
| --- | --- |
| citation / year | 建立時間脈絡 |
| country_or_region | 找國內外差異 |
| topic_cluster | 分群，而不是堆清單 |
| theory_or_framework | 看理論站在哪裡 |
| method / data_source | 判斷自己能不能做 |
| key_findings | 知道目前做到哪裡 |
| limitations / gap_claim | 找研究缺口 |
| relevance_to_my_thesis | 連回自己的題目 |
| verification_status | 確認是否已看過原文 |

## Gap Radar

常見 gap 類型：

- context gap：國外研究多，台灣情境少。
- method gap：多數研究用統計，你可用訪談/個案補足。
- data gap：舊資料多，新制度或新資料少。
- theory gap：實務研究多，但理論連結弱。
- practice gap：學術模型存在，但現場操作與政策銜接不足。

## 給從 0 開始學生的判斷標準

一個方向適合寫成碩士論文，至少要符合：

- 3 到 5 篇 seed papers 能支撐它不是憑空想像。
- 你能說出目前研究已經知道什麼。
- 你能說出還沒解決什麼。
- 你拿得到資料。
- 你的方法能回答你的問題。
