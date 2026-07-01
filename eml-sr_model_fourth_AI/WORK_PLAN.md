# eml-sr_model_fourth_AI 作業計画書

**ブランチ**: `20260701_create_model_fourth_AI`  
**作成日**: 2026/07/01  
**ステータス**: 実装済み（パイプライン実行・レポート更新は進行中）  
**編集対象**: `eml-sr_model_fourth_AI/` および `daily_report.md`（`MEb/` は非改変、`git push` は指示があるまで行わない）

---

## 1. 目的

`eml-sr_model_third_AI` の結果（リンク関数のシンボリック回帰は恒等リンクが最良で打ち切り）を踏まえ、チーター GSE310779（同一前処理パイプライン）において **CpG → 変換年齢 `age_trans`** の予測モデルを **5 手法**で横並び比較する。

| Step | 手法 | 入力 |
|:---:|:---|:---|
| **0** | Elastic Net 線形回帰（論文再現ベースライン） | 全 CpG（`glmnet` 変数選択込み） |
| **1** | EML-SR（`eml-sr_model_first_AI`） | EN 上位 **20** CpG |
| **2** | PySR（遺伝的プログラミング） | 同上 |
| **3** | ニューラルシンボリック回帰（EQL スタイル PyTorch） | 同上 |
| **4** | Sparse Simple Index Model (SIM) | 同上 |

**third からの変更点**

- リンク関数 $g$ の探索は **廃止**（`nextplan.md`）
- SR 系は **20 CpG 固定**
- 全 Step（0〜4）で **MSE・$R^2$ を必須**（既存の Pearson $r$、MAE 等と併記）
- Step 1〜4 では **惜しかった候補式を上位 10 件固定**で出力

---

## 2. 参照元と既知の制約

### 2.1 参照コード・レポート

| 参照 | 役割 |
|:---|:---|
| `eml-sr_model_third_AI/analysis_third_AI_report.md` | third の数値結果・限界・再現手順 |
| `eml-sr_model_third_AI/preprocess_clock.R` | 前処理のコピー元（WGCNA, ComBat, ASM, `glmnet` LOOCV） |
| `age_cheetah/CheetahClock_age_sex.Rmd` | 原著手順 |
| `age_cheetah/GSE310779_series_matrix.txt` | 入力データ |
| `eml-sr_model_first_AI/` | EML-SR エンジン |
| `nextplan.md` | fourth フェーズの方針 |

### 2.2 GEO 単体では完全再現できない点（レポートに明記）

原著 Rmd は **内部 RDS** と **MCDB 血液データ** を使用するが、リポジトリに無い（third §2 と同様）。

| 項目 | 原著 | 本計画（GEO ベース） |
|:---|:---|:---|
| 時計学習サンプル | 肝臓 + MCDB 血液 | GEO 内の liver + blood のみ |
| LOOCV $r$ | 論文値 $\approx 0.97$ | third では $\approx 0.76$；**相対比較が主目的** |

---

## 3. 承諾済み設計判断（§9 確認事項）

| # | 項目 | 決定 |
|:---:|:---|:---|
| 1 | CpG 数 | **20**（`selected_cpgs.csv` の \|coef\| 上位） |
| 2 | 惜しかった式 | **パレート／候補リストから上位 10 件固定** |
| 3 | Step 3 実装 | **EQL スタイル PyTorch**（L1 スパース → 式簡約） |
| 4 | LOOCV（Step 1〜4） | **構造固定 LOOCV**（全データで構造探索 → fold ごとに held-out 評価） |
| 5 | 前処理 | `preprocess_clock.R` を **fourth にコピー**し、`data/` を独立生成 |

---

## 4. 成果物一覧

### 4.1 コード（`eml-sr_model_fourth_AI/`）

```
eml-sr_model_fourth_AI/
├── WORK_PLAN.md                 # 本計画書
├── README.md                    # 実行手順・依存関係
├── requirements.txt             # Python 依存
├── config.py                    # N_CPG=20, 各手法ハイパーパラメータ
├── preprocess_clock.R           # third からコピー
├── run_pipeline.py              # Step 0→4 を順実行
├── metrics.py                   # MSE, R², r, MAE（共通）
├── utils.py                     # 式評価, ASM 逆変換
├── step0_baseline_enet.py       # R 出力の集約・指標拡張
├── step1_eml_sr.py
├── step2_pysr.py
├── step3_neural_sr.py           # EQL スタイル
├── step4_sparse_sim.py
├── compare_results.py           # 全手法比較表
├── data/                        # 生成物（.gitignore）
└── results/
    ├── comparison_summary.csv
    ├── step{0-4}_*
    └── analysis_fourth_AI_report.md
```

### 4.2 レポート

| ファイル | 内容 |
|:---|:---|
| `daily_report.md` | 作業ログ（日付・実施内容） |
| `eml-sr_model_fourth_AI/analysis_fourth_AI_report.md` | 手法・数値結果・考察（実行後） |

---

## 5. 評価指標の統一

### 5.1 予測対象

- **主スケール**: `age_trans`（原著 `glmnet` と同じ）
- **補助スケール**: ASM 逆変換後の **暦年齢**（解釈用）

年齢変換（ASM）は Rmd と同様、性成熟年齢 ASM = 2、定数 $k = 0.2$ として

$$
g(x) = \log\frac{x+k}{\mathrm{ASM}+k} \quad (x < \mathrm{ASM}), \qquad
g(x) = \frac{x-\mathrm{ASM}}{\mathrm{ASM}+k} \quad (x \geq \mathrm{ASM})
$$

### 5.2 必須指標（Step 0〜4 共通）

| 指標 | `age_trans` 上 | 暦年齢上（逆変換後） |
|:---|:---:|:---:|
| MSE | ✓ | ✓ |
| $R^2$ | ✓ | ✓ |
| Pearson $r$ | ✓ | ✓ |
| MAE | ✓ | ✓（年） |

$R^2$ は LOOCV 予測に対する out-of-sample 値（`sklearn.metrics.r2_score` 相当）。

### 5.3 交差検証方針

| Step | LOOCV | 備考 |
|:---:|:---:|:---|
| **0** | **厳密 LOOCV** | R `glmnet`（`preprocess_clock.R`） |
| **1〜4** | **構造固定 LOOCV** | 全データで式／モデル構造を探索し、各 fold で held-out 評価 |

Step 1〜4 の LOOCV 限界（構造の再探索なし）は `analysis_fourth_AI_report.md` に明記する。

### 5.4 惜しかった式（Step 1〜4）

- 各手法の候補リストから **MSE 昇順（またはパレート順）で上位 10 件**を固定出力
- 最良式は Rank 1 として別途 `comparison_summary.csv` に反映

---

## 6. 各 Step の実装方針

### Step 0: Elastic Net 線形回帰

- `preprocess_clock.R` が出力する `baseline_loocv.csv`, `baseline_summary.csv` を読み込み
- Python 側で **MSE・$R^2$ を追加計算**し `results/step0_baseline.csv` に保存
- 非ゼロ CpG 数・$\lambda$ を併記

### Step 1: EML-SR（first_AI）

- 入力: `selected_cpgs.csv` の |coef| **上位 20**
- `find_candidates` でパレート候補取得
- 出力: 最良式 + **惜しかった式 Top 10**（複雑度, Train/LOOCV MSE, $R^2$, $r$, 数式）
- ハイパーパラメータ: `MAX_COMPLEXITY=10`, `BEAM_WIDTH=500`（`config.py` で変更可）

### Step 2: PySR

- ライブラリ: [PySR](https://github.com/MilesCranmer/PySR)（Julia バックエンド要インストール）
- 演算子: `+`, `-`, `*`, `/`, `exp`, `log`, `sin`, `cos` 等
- `equations.csv` から **最良 + 上位 10 件**を抽出・指標計算

### Step 3: ニューラルシンボリック回帰（EQL）

- 1 隠れ層 + `sin` / `exp` / `identity` 活性化、**L1 スパース**
- スパース化後の重み・活性化の組み合わせを **sympy で簡約**し疑似式として記録
- Train / LOOCV 指標を Step 1〜2 と同形式で出力

### Step 4: Sparse Simple Index Model

$$
\text{age\_trans} \approx g(\eta), \quad \eta = \sum_{j=1}^{20} \beta_j \,\mathrm{CpG}_j
$$

- **Sparse $\beta$**: `ElasticNet` または `Lasso`
- **$g$**: 単変量スプライン（`SplineTransformer` + 線形）または低次多項式 CV
- 非ゼロ $\beta_j$、$g$ の形式、MSE / $R^2$ / LOOCV を出力

---

## 7. 比較・レポート

### 7.1 `compare_results.py`

全 Step の LOOCV 指標を 1 表にまとめる:

```
results/comparison_summary.csv
  method, n_features, formula_or_model,
  loocv_mse_trans, loocv_r2_trans, loocv_r_trans, loocv_mae_trans,
  loocv_mse_age, loocv_r2_age, loocv_r_age, loocv_mae_age
```

### 7.2 `analysis_fourth_AI_report.md`

- third からの変更理由（リンク SR 打ち切り）
- 各手法の最良式・惜しかった候補 Top 10
- MSE / $R^2$ / $r$ / MAE の比較表
- 生物学的・統計的考察ドラフト

---

## 8. 依存関係

### Python（`requirements.txt` 予定）

```
numpy>=1.24
pandas>=2.0
scikit-learn>=1.3
matplotlib>=3.7
pysr              # Step 2
torch             # Step 3
sympy             # 式簡約
```

### R（`install_r_packages.R` 予定）

`glmnet`, `WGCNA`, `sva`（third と同様）

### 外部

- `eml-sr_model_first_AI`（maturin build 済み wheel）
- PySR: Julia 1.x + `SymbolicRegression.jl`（README に手順記載）

---

## 9. 実装順序（承諾後）

| 順 | タスク | 成果物 |
|:---:|:---|:---|
| 1 | スケルトン + `config` + `metrics` + R 前処理コピー | ディレクトリ骨格 |
| 2 | Step 0（ベースライン指標拡張） | `step0_baseline.csv` |
| 3 | Step 1（EML-SR + Top 10 + LOOCV） | `step1_eml_sr_*` |
| 4 | Step 4（Sparse SIM） | `step4_sim_*` |
| 5 | Step 2（PySR） | `step2_pysr_*` |
| 6 | Step 3（Neural SR / EQL） | `step3_neural_sr_*` |
| 7 | `compare_results.py` + レポート | 比較表・考察 |

Step 4 を Step 2 より先にする理由: sklearn のみで動き、パイプライン検証が早い。

---

## 10. 想定リスクと対応

| リスク | 対応 |
|:---|:---|
| PySR / Julia 未インストール | README に手順記載；Step 2 はオプション実行可能に |
| Neural SR が簡潔な式を抽出できない | スパース重み + 活性化の組み合わせを疑似式として報告 |
| 48 サンプル・20 変数で過学習 | LOOCV 必須、複雑度ペナルティ、SIM で次元削減 |
| 計算時間 | PySR の `niterations` を `config.py` で抑制 |

---

## 11. 再現手順（実装完了後の想定）

```powershell
cd eml-sr_model_fourth_AI
Rscript install_r_packages.R      # 初回のみ
Rscript preprocess_clock.R
python step0_baseline_enet.py
python step1_eml_sr.py
python step4_sparse_sim.py
python step2_pysr.py              # Julia 要
python step3_neural_sr.py
python compare_results.py
# または
python run_pipeline.py
```

---

## 12. Git

- フェーズ完了ごとに `git add` + `git commit`（**push はユーザー指示まで行わない**）
- コミット例: `feat(fourth_AI): add WORK_PLAN and skeleton`, `feat(fourth_AI): step0 baseline metrics`, 等
