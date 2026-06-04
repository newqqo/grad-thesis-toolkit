# 文獻搜尋計畫 Search Plan

## 目標

把模糊關鍵字 `PSC` 變成可以跟指導教授討論的文獻地圖。

## Step 1: 先找種子文獻 Seed Papers

不要只用一個工具。建議至少用 2-3 種搜尋來源互相補盲點。

可用來源：

- Google Scholar / 學校圖書館資料庫
- Elicit 或其他語意搜尋工具
- SciSpace 或其他論文閱讀工具
- Scopus / Web of Science，如果學校有訂閱

起始搜尋語：

- `PSC literature review`
- `PSC systematic review`
- `PSC research gap`
- `PSC determinants`
- `PSC trend`
- `PSC Taiwan`
- `PSC Asia`

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
