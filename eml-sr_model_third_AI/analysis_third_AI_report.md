# eml-sr_model_third_AI 結果レポート

**日付**: 2026/06/30  
**ブランチ**: `20260630_create_model_third`  
**方針**: 案 A（R 前処理 + `glmnet` LOOCV → Python `eml-sr_model_first_AI`）

---

## 1. 概要

GEO **GSE310779** Series Matrix から、原著 `CheetahClock_age_sex.Rmd` に沿って **R** で前処理・線形 Elastic Net LOOCV を実行し、その出力を用いて **EML 記号回帰**（多変量・リンク関数）を実施した。

---

## 2. 前処理（`preprocess_clock.R`）

| 項目 | 設定・結果 |
|:---|:---|
| 入力 | `age_cheetah/GSE310779_series_matrix.txt` |
| 学習コホート | liver + blood（**52** サンプル） |
| 皮膚 | **5** サンプル（`data/skin_samples.csv`、学習から除外） |
| QC | `WGCNA::goodSamplesGenes` + 階層クラスタリング（`h=30`） |
| 外れ値除去 | **4** サンプル（GSM9308714, GSM9308742, GSM9308744, GSM9308745） |
| 著者 SID リスト | GEO supplementary に未検出 → クラスタリングのみ適用 |
| 残サンプル数 | **48** |
| バッチ補正 | `sva::ComBat`（batch = Study: SDZWA / MammCon 相当） |
| 年齢変換 | ASM = 2, k = 0.2（Rmd と同一） |

### 原著との差分（限界）

- **MCDB 血液データ**は GEO に含まれず、原著 RDS も未同梱のため未使用。
- 外れ値 ID（`ET0394TOX...`）は GEO ファイル名と突合できず、クラスタリングベースの除去のみ。

---

## 3. 線形 Elastic Net ベースライン（LOOCV）

| 指標 | 値 |
|:---|:---:|
| 最適 \(\lambda\) | 0.555 |
| 非ゼロ CpG 数 | **42** |
| LOOCV Pearson \(r\)（暦年齢 vs 逆 ASM 予測） | **0.758** |
| LOOCV MAE（年） | **1.88** |

原著報告（\(r \approx 0.97\), MAE \(\approx 0.86\)）には届いていないが、簡易 Python 前処理（80/20 ホールドアウト \(R^2 \approx 0.5\) 台）よりは LOOCV \(r\) が改善している。残差の主因は **MCDB 血液未含有・サンプル構成の差** と考えられる。

---

## 4. 多変量 EML-SR（`train_eml_sr.py`）

| 設定 | 値 |
|:---|:---|
| エンジン | `eml-sr_model_first_AI` |
| 入力 CpG | glmnet \|coef\| **上位 15** |
| `max_complexity` | 10 |
| `beam_width` | 500（`config.py` で変更可） |

### パレート上位（訓練データ・`age_trans` スケール）

| Rank | 複雑度 | Train MSE | Train \(r\) | 数式 |
|:---:|:---:|:---:|:---:|:---|
| 1 | 3 | 5.56 | 0.686 | \(\frac{v_{6}}{v_{12}}\) |
| 2 | 2 | 8.53 | 0.723 | \(e^{v_{4}}\) |

- CpG 対応: `results/eml_sr_results.txt` 参照（例: \(v_6\) = cg16046465, \(v_{12}\) = cg04226429）。
- 線形 EN LOOCV（\(r=0.76\) on 暦年齢）と比較すると、**訓練上の `age_trans` フィットは EN に劣る**一方、低複雡度の解釈可能な式が得られた。
- 厳密 LOOCV 再探索は計算コストのため未実施（全データ探索 → 訓練指標で評価）。

---

## 5. リンク関数のシンボリック回帰（`train_link_sr.py`）

固定 ASM との比較（Task A）および EN 線形スコアへのリンク（Task B）を実施。

| Task | 目的 | 最良式（複雑度 2） | MSE | \(r\) |
|:---|:---|:---|:---:|:---:|
| A | Age → `age_trans`（ASM 再現） | \(\sqrt{\text{Age}}\) | 2.50 | 0.991 |
| B | Age → EN スコア | \(\sqrt{\text{Age}}\) | 0.517 | 0.944 |

- 固定 ASM の参照 MSE（再計算 vs 保存 `age_trans`）≈ **0**（数値的に一致）。
- SR は **平方根**を最良としたが、ASM の区分対数・線形構造は再現できていない（\(r\) は高いが MSE は ASM より大きい）。リンク探索の候補としては \(\sqrt{x}\) が簡潔な近似であることが示された。

---

## 6. 考察

1. **R 前処理**により、論文と同種のツールチェーン（WGCNA, ComBat, glmnet）でベースラインを確立できた。
2. LOOCV \(r \approx 0.76\) は簡易 Python パイプラインより改善するが、**\(r \approx 0.97\) 再現には MCDB データ等が必要**。
3. **eml-sr** は 15 CpG・複雑度 2–3 の短い式を発見；線形 EN を上回る暦年齢 LOOCV までは本 Run では未検証。
4. **リンク SR** は ASM そのものより \(\sqrt{\text{Age}}\) を選んだが、生物学的 ASM との一致は今後の制約付き探索（区分関数・単調性）が有用。

---

## 7. 再現手順

```powershell
cd eml-sr_model_third_AI
Rscript install_r_packages.R      # 初回のみ
Rscript preprocess_clock.R
python train_eml_sr.py
python train_link_sr.py
# または
python run_pipeline.py
```

パラメータ変更: `config.py` の `N_CPG_FOR_SR`, `BEAM_WIDTH`, `MAX_COMPLEXITY`。

---

## 8. 出力ファイル一覧

| パス | 内容 |
|:---|:---|
| `data/clock_samples.csv` | メタデータ + `age_trans` |
| `data/beta_combat.csv` | ComBat 後 β |
| `data/selected_cpgs.csv` | glmnet 係数 |
| `data/baseline_loocv.csv` | EN LOOCV 予測 |
| `data/baseline_summary.csv` | 要約指標 |
| `results/eml_sr_results.txt` | 多変量 SR |
| `results/link_sr_results.txt` | リンク SR |
