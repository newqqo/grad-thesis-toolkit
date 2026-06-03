# Concept Hierarchy And Promise-Delivery Checks

這份流程補上兩種高標準論文審查能力：

1. 核心概念階層樹。
2. 理論承諾與實際交付一致性檢查。

兩者都遵守同一個原則：先讀文稿本身，不先帶入外部學理定義，也不替文稿補不存在的理論。

## 先用工具抓原文證據

自動掃描 `source/shadow`：

```powershell
python scripts/manuscript_concept_audit.py all --source source/shadow
```

用公開範例試跑：

```powershell
python scripts/manuscript_concept_audit.py all --source examples/concept-drift-sample.md
```

如果你已經知道要檢查哪些核心概念，可以明確指定：

```powershell
python scripts/manuscript_concept_audit.py all --source examples/concept-drift-sample.md --concept 數位轉型 --concept 服務流程治理框架 --concept 顧客回應機制
```

產出：

- `consistency/reports/concept_hierarchy_report.md`
- `consistency/reports/promise_delivery_report.md`

## 能力 1: 核心概念階層樹

使用這段 prompt 搭配報告與完整文稿：

```text
請完整讀取我的文稿。不要帶入外部知識，也不要先用一般學理定義判斷；請僅憑我文稿中的實際論述，幫我萃取並建立一棵「核心概念階層樹」，區分上位場域、中位分析單位、下位具體工具／措施／操作概念。

請列出：
1. 每個層級我實際使用了哪些名詞。
2. 每個判定所依據的代表性原句。
3. 哪些名詞在全文中使用穩定。
4. 哪些名詞在不同章節出現位階漂移、語意擴張或互相替換。
5. 若同一層次被不同名詞指稱，請明確指出衝突點與所在章節。
6. 最後提出一套「最小修改成本」的概念統一方案，說明哪些詞應保留為核心主軸，哪些詞應作為次層或操作性用語。
```

## 能力 2: Theoretical Promise vs. Delivery Check

使用這段 prompt 搭配報告與完整文稿：

```text
請以高標準學術審查方式，對本文進行「理論承諾與實際交付一致性檢查（Theoretical Promise vs. Delivery Check）」。

請依序檢查：
1. 第一章提出了哪些高位階概念、理論標籤或分析框架？
2. 第二章是否有足夠文獻回顧與概念界定支撐這些概念？
3. 第四章的實證材料是否有真正操作這些概念，而非僅止於提及或裝飾性引用？
4. 第五章的結論是否建立在前文已被分析與證成的內容上？

請列成表格，欄位包含：
- 概念名稱
- 第一章如何提出
- 第二章是否有支撐
- 第四章是否有操作
- 第五章是否有合理回收
- 判定：一致／部分落空／明顯落空
- 建議：保留、降階、改寫、刪除

請務必附上對應章節中的原句或關鍵語句作為判斷依據，不要只給抽象評論。
```

## 判讀方式

- `concept_hierarchy_report.md` 是候選概念與原文證據，不是最後裁判。
- `promise_delivery_report.md` 用章節出現與操作語境做初步判定，嚴格審查時仍要人工確認。
- 如果報告太吵，先從自動報告挑出 5 到 12 個真正核心概念，再用 `--concept` 重跑。
- 如果第四章只有提到概念名稱，但沒有資料、指標、個案、訪談、表格、流程或操作措施，應判為「部分落空」或「明顯落空」。
