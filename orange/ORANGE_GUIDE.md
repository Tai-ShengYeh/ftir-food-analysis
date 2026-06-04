# Orange Data Mining 實作指南 — 紅外光譜食品分析（PCA + 品種鑑別）

> 給課堂用的「不寫程式」版本。學生用拖拉式 widget，重現 Python 影片裡的 PCA 與 PLS-DA 結果。
> 資料：`../data/coffee_orange.tab`（56 支即溶咖啡 × 286 個 FTIR 波數 + variety 品種標籤）。
> 一鍵開檔：`coffee_ftir_workflow.ows`（已含 7 個 widget、6 條連線）。
> Orange 版本：3.36+（PCA、Logistic Regression、Confusion Matrix 皆為內建）。

---

## Part 0 ｜ 安裝 Orange

1. 到 <https://orangedatamining.com/download> 下載安裝（Windows / macOS 皆可，含 Python）。
2. 開啟 Orange，看到空白 canvas、左側 widget 工具列即安裝成功。
3. 本指南用到的 widget 都是內建：**Data ▸ File / Data Table**、**Unsupervised ▸ PCA**、
   **Visualize ▸ Scatter Plot**、**Model ▸ Logistic Regression**、**Evaluate ▸ Test and Score / Confusion Matrix**。

---

## Part 1 ｜ 認識資料

`coffee_orange.tab` 欄位（已標好角色，直接可用）：

| 欄位 | 數量 | 角色 (role) | 說明 |
|------|------|------------|------|
| `sample_id` | 1 | **meta** | 樣本編號（不參與分析） |
| 286 個波數欄 (`w810`…`w1911`) | 286 | **feature** | FTIR 吸收值 → PCA / 分類的輸入 |
| `variety` | 1 | **target (class)** | 品種（Arabica / Robusta）→ 分類目標 |

> 資料來源：Mendeley Data **frrv2yd9rg**（Briandet et al. Instant-coffee MIR-DRIFT FTIR，56 支凍乾咖啡，公開資料）。

---

## Part 2 ｜ 開啟現成工作流程

`File ▸ Open` 選 `coffee_ftir_workflow.ows`。會看到兩條分支：

```
                 ┌──────────────┐
         ┌──────▶│  Data Table  │   檢視原始 FTIR 光譜矩陣
         │       └──────────────┘
         │       ┌──────┐  Transformed Data   ┌──────────────────────┐
         │  ┌───▶│ PCA  │────────────────────▶│ Scatter Plot 分數圖   │  ← PCA 分支（探索）
 ┌───────┴──┐│   └──────┘                      └──────────────────────┘
 │  File    ├┤
 │coffee_   ││
 │orange.tab│└──▶ ┌───────────────────┐ Data  ┌───────────────┐ Eval  ┌─────────────────┐
 └──────────┘     │ Test and Score    │◀──────│               │──────▶│ Confusion Matrix│
                  │ (5-fold CV)       │       └───────────────┘  Res  └─────────────────┘
                  └───────────────────┘            ▲ Learner
                                             ┌─────┴──────────────┐
                                             │ Logistic Regression│   ← 分類分支（監督）
                                             └────────────────────┘
```

**第一步永遠是設定 File widget**：雙擊 `File` → 右下 `Browse` 選 `../data/coffee_orange.tab` → 按 `Apply`。
（`.tab` 檔已標好角色：`variety` = target（class）、`sample_id` = meta、其餘 286 個維持 feature。）

> 中文路徑載入失敗時，把 `coffee_orange.tab` 複製到純英文路徑再 Browse。

---

## Part 3 ｜ PCA 分支（對應第一支影片）

**目標**：把 286 個波數壓成 2–3 個主成分，看咖啡是否依品種自動排列。

| # | 動作 | Widget 設定 | 應觀察到 |
|---|------|------------|---------|
| 1 | 拉 **File** | 載入 `coffee_orange.tab` | 56 instances、286 features |
| 2 | 接 **Data Table** | （File→Data Table） | 看到原始 FTIR 吸收值表格 |
| 3 | 接 **PCA** | 視窗內勾 **Normalize variables**（= autoscale），看變異解釋曲線 | PC1 ≈ 44.5%，前 2 個累積 ≈ 67.6% |
| 4 | 接 **Scatter Plot** | PCA 的 **Transformed Data** → Scatter Plot | 下一步上色 |
| 5 | 設定 Scatter Plot | Axis x = **PC1**、y = **PC2**、**Color = variety** | Arabica（teal）一側、Robusta（coral）另一側，主要沿 PC2 分開 |

**教學提問**：
- PCA 有沒有用到品種標籤？（沒有，它是非監督；卻仍依品種聚集 → 結構自己浮現）
- 把 Color 改成某個波數欄（如 `w1007`、`w1714`），觀察梯度分布。
- PC1 佔 44.5%，比質譜的 22% 高很多，為什麼？（FTIR 相鄰波數高度相關，資訊更集中）

> 影片的 Python 版先做 SNV；Orange 只勾 Normalize（autoscale），結果略有不同，
> 但「兩品種依 PC2 自動分群」的結論一致。想更貼近 Python，可在 File 與 PCA 之間插一個 **Preprocess** widget。

---

## Part 4 ｜ 分類分支（對應第二支影片的 PLS-DA）

**目標**：用 FTIR 光譜建立一個能分辨 **Arabica vs Robusta** 的分類器，並誠實驗證。

> **關於 PLS-DA**：影片用的 PLS-DA = 在 0/1 類別標籤上做 PLS 回歸。Orange 內建的 **PLS** widget
> 只做數值回歸，因此這裡改用 **Logistic Regression**——同樣是「監督式線性鑑別」，能直接輸出
> 混淆矩陣與準確率，教學概念與 PLS-DA 完全相通（都在找一條最能分開兩類的方向）。
>
> **本資料已只有 Arabica / Robusta 兩類，無需 Select Rows**，比質譜課更簡潔。

| # | 動作 | Widget 設定 | 應觀察到 |
|---|------|------------|---------|
| 1 | 接 **Logistic Regression** | （Model 類別）預設即可；Regularization 可留預設 | 產生 Learner |
| 2 | 接 **Test and Score** | File 的 **Data** → Test&Score 的 **Data**；Logistic 的 **Learner** → Test&Score。選 **Cross validation, 5 folds** | **CA（準確率）≈ 0.98–1.00**（對應影片 5 折 CV 結果） |
| 3 | 接 **Confusion Matrix** | Test&Score 的 **Evaluation Results** → Confusion Matrix | 對角線幾乎全中：29 Arabica / 27 Robusta 互不混淆 |

**重現影片的「過度擬合」教學（選做）**：
- 調整 Logistic 的 Regularization C 值（越大越複雜），看 Test&Score 的 CA：
  本題兩品種差異大，模型很快就接近完美，**加更多複雜度沒有幫助**。
- 教學結論：用交叉驗證挑「夠用」的複雜度，不是越複雜越好（呼應影片 ft07）。

**看是哪些波段在分類**（呼應影片 ft09，鑑別係數）：
- 接 **Rank**（Data 類別）到 File 的 Data，依 information gain / ANOVA 排序，
  排前面的常是 **1007 / 957 / 903 cm⁻¹** 附近的波數欄——對應醣類 C–O 伸縮振動區，和影片的 PLS-DA 回歸係數一致。

---

## Part 5 ｜ 和 Python / 影片對照

| 概念 | 影片 / Python 圖 | Orange widget |
|------|-----------------|---------------|
| FTIR 光譜（原始） | ft01 | File → Data Table |
| 主成分數量 | ft03 scree | PCA 視窗內的變異曲線 |
| 分數圖（依品種上色） | ft04 | PCA → Scatter Plot（Color=variety） |
| 監督式分類 | ft06 / ft08 | Logistic Regression + Test&Score + Confusion Matrix |
| 選複雜度 / 過度擬合 | ft07 | 調模型複雜度 + Test&Score 的 CA |
| 哪些波段在分類 | ft09 | Rank widget（information gain / ANOVA） |

學生先看影片建立直覺、看 Python 看「怎麼算」、最後用 Orange 親手「拉一遍」，三層遞進。

---

## Part 6 ｜ 疑難排解

| 現象 | 原因 / 修法 |
|------|------------|
| Logistic / Test&Score 灰掉沒反應 | File 沒把 `variety` 設成 target；確認 .tab 第三列 flags 中 variety 欄為 `class` |
| 開 .ows 後 File 紅框 | File 還沒指定檔案：雙擊 File 重新 Browse 到 `coffee_orange.tab` |
| Scatter Plot 沒有 PC1/PC2 選項 | 確認連的是 PCA 的 **Transformed Data**（不是原始 Data） |
| Confusion Matrix 空白 | 確認 Test&Score 跑完且選了 Cross validation；連的是 **Evaluation Results** |
| CA 和 Python 略不同 | 隨機折數所致，量級一致即可（兩品種都接近 100%） |
| 中文路徑載入失敗 | 把 `coffee_orange.tab` 複製到純英文路徑再 Browse |
| PCA 結果和 Python 不同 | Orange 只做 autoscale，Python 先做 SNV 再 mean-center；品種分群方向一致即可 |
