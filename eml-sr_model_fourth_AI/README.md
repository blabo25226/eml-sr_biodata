# eml-sr_model_fourth_AI

チーター GSE310779 データに対し、Elastic Net ベースラインと 4 種の記号回帰／指数モデルを **MSE・$R^2$・$r$・MAE** で比較するパイプライン。

詳細は [WORK_PLAN.md](WORK_PLAN.md) を参照。

## 手法一覧

| Step | スクリプト | 手法 |
|:---:|:---|:---|
| 0 | `step0_baseline_enet.py` | R `glmnet` Elastic Net + LOOCV |
| 1 | `step1_eml_sr.py` | EML-SR（`eml-sr_model_first_AI`） |
| 2 | `step2_pysr.py` | PySR（遺伝的プログラミング） |
| 3 | `step3_neural_sr.py` | EQL スタイルニューラル SR（PyTorch） |
| 4 | `step4_sparse_sim.py` | Sparse Simple Index Model |

Step 1–4 は glmnet \|coef\| **上位 20 CpG** を入力とする。惜しかった候補は **上位 10 件**を出力。

## 依存関係

### Python

```powershell
cd eml-sr_model_fourth_AI
pip install -r requirements.txt
```

`eml-sr_model_first_AI` は事前にビルドが必要:

```powershell
cd ..\eml-sr_model_first_AI
maturin develop --features python
```

### R

```powershell
Rscript install_r_packages.R
```

`config.py` の `RSCRIPT` を環境の R パスに合わせる。

### PySR（Step 2、オプション）

[PySR](https://github.com/MilesCranmer/PySR) は Julia が必要。未インストール時は Step 2 をスキップして続行できる。

```powershell
pip install pysr
python -c "import pysr; pysr.install()"
```

## 実行

```powershell
cd eml-sr_model_fourth_AI
python run_pipeline.py              # 全 Step
python run_pipeline.py r 0 1 4 3 compare   # PySR を除く例
python run_pipeline.py 2            # PySR のみ
```

個別実行:

```powershell
Rscript preprocess_clock.R
python step0_baseline_enet.py
python step1_eml_sr.py
python step4_sparse_sim.py
python step2_pysr.py
python step3_neural_sr.py
python compare_results.py
```

## 出力

| パス | 内容 |
|:---|:---|
| `data/` | 前処理 CSV（ComBat β、LOOCV 予測など） |
| `results/step0_baseline.csv` | EN ベースライン指標 |
| `results/step1_eml_sr_candidates.csv` | EML-SR 上位 10 候補 |
| `results/step2_pysr_candidates.csv` | PySR 上位 10 候補 |
| `results/step3_neural_sr_summary.csv` | EQL 結果 |
| `results/step4_sim_summary.csv` | Sparse SIM 結果 |
| `results/comparison_summary.csv` | 全手法 LOOCV 比較 |

## LOOCV の注意

- Step 0: R による厳密 LOOCV
- Step 1–4: **構造固定 LOOCV**（全データで構造探索後、同一式で各サンプルを評価）。$g$ や式の fold 内再探索は行わない。

## ブランチ

`20260701_create_model_fourth_AI`
