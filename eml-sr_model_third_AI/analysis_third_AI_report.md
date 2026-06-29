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

年齢変換（ASM）は Rmd と同様、性成熟年齢 ASM = 2、定数 k = 0.2 として

$$
g(x) = log((x+k)/(ASM+k))  when  x < ASM,  g(x) = (x-ASM)/(ASM+k)  when  x >= ASM
$$

を各サンプルの暦年齢 $x$ に適用し、変換年齢 `age_trans` = $g(x)$ とした。

### 原著との差分（限界）

- **MCDB 血液データ**は GEO に含まれず、原著 RDS も未同梱のため未使用。
- 外れ値 ID（`ET0394TOX...`）は GEO ファイル名と突合できず、クラスタリングベースの除去のみ。

---

## 3. 線形 Elastic Net ベースライン（LOOCV）

| 指標 | 値 |
|:---|:---:|
| 最適 $lambda$ | 0.555 |
| 非ゼロ CpG 数 | **42** |
| LOOCV Pearson $r$（暦年齢 vs 逆 ASM 予測） | **0.758** |
| LOOCV MAE（年） | **1.88** |

原著報告（$r \approx 0.97$, MAE $\approx 0.86$）には届いていないが、簡易 Python 前処理（80/20 ホールドアウト $R^2 \approx 0.5$ 台）よりは LOOCV $r$ が改善している。残差の主因は **MCDB 血液未含有・サンプル構成の差** と考えられる。

---

## 4. 多変量 EML-SR（`train_eml_sr.py`）

| 設定 | 値 |
|:---|:---|
| エンジン | `eml-sr_model_first_AI` |
| 入力 CpG | glmnet \|coef\| **上位 15** |
| `max_complexity` | 10 |
| `beam_width` | 500（`config.py` で変更可） |

### パレート上位（訓練データ・`age_trans` スケール）

| Rank | 複雑度 | Train MSE | Train $r$ | 数式 |
|:---:|:---:|:---:|:---:|:---|
| 1 | 3 | 5.56 | 0.686 | $v_6 / v_{12}$ |
| 2 | 2 | 8.53 | 0.723 | $e^{v_4}$ |

- CpG 対応: `results/eml_sr_results.txt` 参照（例: $v_6$ = cg16046465, $v_{12}$ = cg04226429）。
- 線形 EN LOOCV（暦年齢上 $r = 0.76$）と比較すると、**訓練上の `age_trans` フィットは EN に劣る**一方、低複雑度の解釈可能な式が得られた。
- 厳密 LOOCV 再探索は計算コストのため未実施（全データ探索 → 訓練指標で評価）。

---

## 5. リンク関数のシンボリック回帰（`train_link_g_sr.py`）

### 5.1 モデル定義

§3–§4 では CpG から ASM 変換年齢 `age_trans` を直接予測した。§5 では **GLM のリンク関数** $g$ を、メチル化の線形予測子 $\eta$ と `age_trans` の関係として推定する。

$$
E(\texttt{age\_trans}) = g^{-1}(\eta), \qquad
\eta = \beta_0 + \sum_{j=1}^{p} \beta_j \,\mathrm{CpG}_j
$$

探索目標は全データ上で

$$
g(\texttt{age\_trans}) \approx \eta
$$

となる $g$ を `eml-sr_model_first_AI` で求めることである。ASM による区分対数変換（§2）とは別概念である。

| 設定 | 値 |
|:---|:---|
| $\eta$ の推定 | `ElasticNetCV`（15 CpG、§4 と同一の上位 15） |
| SR 入力 | 単変量 $v_0 = \texttt{age\_trans}$ |
| SR 出力 | $\eta$ |
| `max_complexity` / `beam_width` | 10 / 500（`config.py`） |

### 5.2 LOOCV の設計と限界

承諾済み方針に従い、LOOCV では **各 fold ごとに $\eta$（Elastic Net）を再学習**し、暦年齢は $g^{-1}(\hat\eta)$ → ASM 逆変換で得る。

**限界（本 Run）**: リンク $g$ は **全データで一度 SR 探索した式を固定**し、fold 間で再探索しない。したがって LOOCV は「$\eta$ の汎化」と「固定 $g$ による逆写像」の評価であり、$g$ 自体の厳密な交差検証ではない。

### 5.3 全データ上のリンク推定

| リンク | Train link MSE | Train link $r$ | 複雑度 | 備考 |
|:---|:---:|:---:|:---:|:---|
| Identity ($g(y)=y$) | 0.517 | 0.971 | 1 | $\eta$ が `age_trans` の EN 予測のため近似的に最良 |
| SR 最良（有限 MSE） | 0.517 | 0.971 | 1 | $g(v_0)=v_0$（identity と一致） |

複雑度 8–9 の候補（例: $\sin(\sin v_0)+v_0+\arccos(e^{v_0})$）は `age_trans` の定義域で **NaN** となり除外した。本データでは **非線形 $g$ は恒等リンクを上回らなかった**。

### 5.4 LOOCV（暦年齢、15 CpG）

| モデル | LOOCV $r$ | LOOCV MAE（年） |
|:---|:---:|:---:|
| Identity link（$\hat{\texttt{age\_trans}}=\hat\eta$） | **0.946** | **0.93** |
| SR link（$g(v_0)=v_0$ 固定） | 0.949 | 0.92 |
| §3 参照: glmnet 42 CpG | 0.758 | 1.88 |

- Identity と SR link（$g=v_0$）は LOOCV 上ほぼ同等（SR 側は数値逆写像のグリッド探索による微小差）。
- §3 ベースライン（42 CpG・`glmnet` LOOCV）より **15 CpG + identity link** の方が高い $r$ を示したが、**CpG 数・CV 実装（R `glmnet` vs Python `ElasticNetCV`）が異なる**ため、単純な優劣比較ではない（§3 は変数選択込みの 42 CpG、§5 は |coef| 上位 15 固定）。

### 5.5 小括

非線形リンク $g$ の SR 探索は実施したが、有効域内で **恒等リンクが最良**であった。LOOCV は $\eta$ の再学習のみ fold 内で行い、$g$ は全データ固定——この限界は上記のとおりである。

---

## 6. 考察

1. **R 前処理**により、論文と同種のツールチェーン（WGCNA, ComBat, glmnet）でベースラインを確立できた。
2. LOOCV $r \approx 0.76$ は簡易 Python パイプラインより改善するが、**$r \approx 0.97$ 再現には MCDB データ等が必要**。
3. **eml-sr** は 15 CpG・複雑度 2–3 の短い式を発見；線形 EN を上回る暦年齢 LOOCV までは本 Run では未検証。
4. **リンク SR（§5）** では $g(\texttt{age\_trans})\approx\eta$ を探索したが、有効な非線形 $g$ は得られず **恒等リンク**が最良。LOOCV（15 CpG・$\eta$ 再学習・$g$ 全データ固定）では $r\approx 0.95$、MAE $\approx 0.93$ 年。

---

## 7. 再現手順

```powershell
cd eml-sr_model_third_AI
Rscript install_r_packages.R      # 初回のみ
Rscript preprocess_clock.R
python train_eml_sr.py
python train_link_g_sr.py
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
| `data/linear_predictor.csv` | $\eta$ と `age_trans`（全サンプル） |
| `results/eml_sr_results.txt` | 多変量 SR |
| `results/link_g_sr_results.txt` | リンク $g$ の SR |
| `results/link_g_loocv.csv` | §5 LOOCV 予測 |
| `results/link_g_summary.csv` | Identity / SR link / §3 比較 |
