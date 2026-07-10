# eml-sr_model_fifth_AI — 論文 Elastic Net 再現結果

**日付**: 2026/07/10  
**スクリプト**: `replicate_paper_enet.R`（原著 `CheetahClock_age_sex.Rmd` 準拠）

---

## 1. 学習コホート（論文と一致）

| 項目 | 本 Run | 論文 |
|:---|:---:|:---:|
| SDZWA 肝臓 | **38** | 38 |
| MCDB チーター血液 | **14** | 14 |
| 合計 | **52** | 52 |

**外れ値除去**（肝臓のみ）:
- WGCNA 階層クラスタリング $h=30$ の単独クラスター: **4** サンプル
- 新生仔（stillborn）: GEO タイトル `0.0y 1/2/3` に対応する GSM9308716, 8720, 8721 の **3** サンプル

---

## 2. Elastic Net 設定（論文と同じ）

- ComBat（`batch = study`: SDZWA / MammCon）
- ASM 年齢変換（ASM = 2, $k = 0.2$）
- `cv.glmnet`（`alpha = 0.5`, `nfolds = n`）で $\lambda_{\min}$ 選択
- 非ゼロ CpG: **52**（論文と一致）

---

## 3. LOOCV 結果

原著 Rmd の LOOCV 手順（各 fold で学習した $n$ 個のモデルのうち、**全サンプルへの in-sample MSE が最小**のモデルを選び、その予測を報告）と、一般的な **標準 LOOCV**（各点を held-out 予測）の両方を計算した。

| 評価手順 | LOOCV $r$（暦年齢） | MAE（年） | $\sqrt{\mathrm{median}(\mathrm{error}^2)}$ |
|:---|:---:|:---:|:---:|
| **論文 Rmd 手順** | **0.983** | **0.65** | 0.65 |
| 標準 LOOCV | 0.696 | 2.09 | 2.09 |
| **論文報告値** | **~0.97** | **~0.86** | — |

**結論**: 論文と同じデータ構成・同じ Rmd の LOOCV 定義であれば、**$r$ は論文以上、MAE は論文より良好**（0.65 年）。論文表記の MAE は Rmd 上 `sqrt(median(error^2))` であり、厳密な $\mathrm{median}(|\mathrm{error}|)$ とは異なる。

標準 LOOCV は $r \approx 0.70$ と低く、論文図の「LOOCV」は上記 Rmd 手順に対応していると解釈するのが妥当。

---

## 4. 再現コマンド

```powershell
cd eml-sr_model_fifth_AI
Rscript replicate_paper_enet.R
```

出力: `data/paper_replication_summary.csv`, `data/paper_replication_loocv.csv`

---

## 5. 注意（EML-SR 前のベースライン）

記号回帰との比較には、**標準 LOOCV** を使うか、論文 Rmd 手順を明示するかを事前に決める必要がある。本プロジェクトの `step0_baseline_enet.py` は `baseline_loocv.csv`（標準 LOOCV）を読むため、論文図との直接比較には `paper_replication_loocv.csv` の `pred_age_paper` 列を用いること。
