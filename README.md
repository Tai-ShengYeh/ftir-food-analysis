# 紅外光譜 FTIR × 食品分析教學包

> 以**即溶咖啡 Arabica vs Robusta** 鑑別為案例，示範 FTIR 光譜的 **PCA** 與 **PLS-DA** 分析。
> 內含 Python 完整流程、Orange 視覺化工作流、兩支教學影片與互動式網頁教材。

🔗 **線上教材（GitHub Pages）**：<https://tai-shengyeh.github.io/ftir-food-analysis/>

## 🔗 同主題搭配課程（咖啡真偽鑑別）

同樣以「咖啡」為案例、不同分析角度，可串成一條教學線：

| 課程 | 技術 / 方法 | 課程頁 |
|------|------------|--------|
| **FTIR（本課）** | 中紅外 MIR + PCA + PLS-DA | — |
| 咖啡化學成分 | 12 種成分 + PCA + GMM 集群 | [↗](https://tai-shengyeh.github.io/coffee_pgmm_R_code/coffee_pgmm.html) |
| Benchtop NMR | 桌上型 NMR + PCA + PLS + PLS-DA（16-OMC 摻假）| [↗](https://tai-shengyeh.github.io/benchtop-nmr-coffee/teaching.html) |
| GC 氣相層析 | GC 層析 + PCA + PLS-DA | [↗](https://tai-shengyeh.github.io/coffee-gc-analysis/teaching.html) |

🏠 課程總入口：<https://tai-shengyeh.github.io/>

---

## 這個專案在做什麼

用一組公開的即溶咖啡中紅外光譜（MIR-DRIFT FTIR），帶學習者走一遍光譜化學計量學的標準流程：

1. **看光譜** — 原始譜圖 + SNV 散射校正後的譜圖，依品種上色
2. **PCA**（非監督）— 看樣本在主成分空間自然分群，找出貢獻波段
3. **PLS-DA**（監督）— 建立 Arabica / Robusta 判別模型，交叉驗證評估
4. **交叉印證** — 用直接量測的化學成分資料再跑一次，確認光譜判別波段對應到真實化學差異

### 主要結果

| 分析 | 重點數字 |
|------|----------|
| 資料 | 56 支即溶咖啡 × 286 波數（810–1911 cm⁻¹），Arabica 29 / Robusta 27 |
| PCA | PC1 44.5% + PC2 23.1%，前 4 個 PC 累積 82.6%；PC1 主導波段 ≈ 1714 / 1710 / 1706 cm⁻¹ |
| PLS-DA | 最佳 2 個潛在變量，**留組交叉驗證準確率 100%**（兩品種 recall 皆 100%）；判別波段 ≈ 1007 / 957 / 1011 / 903 cm⁻¹ |

---

## 資料來源

Instant-coffee MIR-DRIFT FTIR 光譜（Briandet et al.），公開資料集
**Mendeley Data `frrv2yd9rg`**（`FTIR_Spectra_instant_coffee.csv`）。
56 支冷凍乾燥即溶咖啡，286 個波數（810–1911 cm⁻¹），標註 Arabica / Robusta。

---

## 目錄結構

```
ftir-food-analysis/
├── data/                       # 資料集與分析輸出指標
│   ├── coffee_ftir.csv         #   原始（轉置）光譜 CSV
│   ├── coffee_ftir_clean.csv   #   整理後：sample_id, variety, 286 波數欄
│   ├── coffee_orange.tab       #   Orange 用的 .tab 格式
│   ├── pgmm_coffee.csv         #   交叉印證用的化學成分資料
│   ├── wavenumbers.npy         #   波數軸
│   └── metrics_*.txt           #   各步驟輸出的關鍵數字
├── python/                     # Python 分析流程
│   ├── ftir_utils.py           #   載入 / SNV 前處理 / 繪圖樣式
│   ├── 01_explore.py           #   原始 + SNV 譜圖
│   ├── 02_pca.py               #   PCA（碎石圖 / 得分 / 載荷）
│   ├── 03_plsda.py             #   PLS-DA（得分 / 交叉驗證 / 混淆矩陣 / 係數）
│   ├── 04_composition_compare.py   # 化學成分交叉印證
│   └── figures/                #   產出的圖（ft01–ft09, ftc01–02）
├── orange/                     # Orange Data Mining 工作流
│   ├── coffee_ftir_workflow.ows
│   └── ORANGE_GUIDE.md         #   無程式操作教學
├── videos/                     # 兩支教學影片（PCA / PLS-DA）
│   ├── DESIGN.md               #   視覺規範
│   ├── pca/   (final.mp4 + 製作腳本)
│   └── plsda/ (final.mp4 + 製作腳本)
├── teaching.html               # 互動式網頁教材
└── index.html                  # 導向 teaching.html
```

---

## 快速開始（Python）

需求：Python 3.9+，套件 `numpy pandas matplotlib scikit-learn scipy`

```bash
pip install numpy pandas matplotlib scikit-learn scipy

cd python
python 01_explore.py            # 譜圖
python 02_pca.py                # PCA
python 03_plsda.py              # PLS-DA
python 04_composition_compare.py  # 化學成分交叉印證
```

首次執行 `ftir_utils.load()` 會自動把原始 CSV 解析成 `coffee_ftir_clean.csv`、
`wavenumbers.npy` 與 Orange 用的 `coffee_orange.tab`。圖檔輸出到 `python/figures/`。

> 前處理採 **SNV（Standard Normal Variate）** 逐譜散射校正——這是 IR / DRIFT 光譜的標準做法。

## 不寫程式：用 Orange

打開 `orange/coffee_ftir_workflow.ows`，載入 `data/coffee_orange.tab`，
依 `orange/ORANGE_GUIDE.md` 一步步操作即可完成同樣的 PCA / PLS-DA 分析。

## 教學影片 / 網頁

- 兩支教學影片在 `videos/pca/final.mp4` 與 `videos/plsda/final.mp4`
- 互動網頁教材：開 `teaching.html`，或直接看線上版
  <https://tai-shengyeh.github.io/ftir-food-analysis/>

---

## 授權與引用

資料集為公開資料（Mendeley Data `frrv2yd9rg`），引用請註明原作者 Briandet et al.。
本教學包之程式碼與教材供教學使用。
