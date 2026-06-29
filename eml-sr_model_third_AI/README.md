# eml-sr_model_third_AI

論文準拠のチーター時計パイプライン（**案 A**: R 前処理 + Python 記号回帰）です。

## 概要

1. **`preprocess_clock.R`** — GEO GSE310779 から WGCNA QC・ComBat・ASM・`glmnet` LOOCV
2. **`train_eml_sr.py`** — `eml-sr_model_first_AI` で CpG → `age_trans` の多変量記号回帰
3. **`train_link_g_sr.py`** — GLM リンク $g$ を SR で探索（$g(\texttt{age\_trans}) \approx \eta$、$\eta$ は 15 CpG の Elastic Net）

## 依存関係

### R（前処理）

```text
glmnet, sva, WGCNA
```

初回のみ:

```powershell
& "C:\Program Files\R\R-4.4.2\bin\Rscript.exe" install_r_packages.R
```

### Python（記号回帰）

```powershell
pip install -r requirements.txt
cd ..\eml-sr_model_first_AI
maturin develop --release
```

`config.py` で `RSCRIPT` パス・`BEAM_WIDTH`・`N_CPG_FOR_SR` 等を変更できます。

## 実行

```powershell
cd eml-sr_model_third_AI
python run_pipeline.py          # 全部
python run_pipeline.py r        # R 前処理のみ
python run_pipeline.py eml link # SR のみ（data/ がある場合）
```

## 出力

| パス | 内容 |
|:---|:---|
| `data/clock_samples.csv` | メタデータ + `age_trans` |
| `data/beta_combat.csv` | ComBat 後 β |
| `data/selected_cpgs.csv` | glmnet 非ゼロ CpG |
| `data/baseline_loocv.csv` | 線形 EN LOOCV（§3） |
| `data/linear_predictor.csv` | §5 用 $\eta$ と `age_trans` |
| `results/eml_sr_results.txt` | 多変量 SR 結果 |
| `results/link_g_sr_results.txt` | リンク $g$ の SR 結果 |
| `results/link_g_loocv.csv` | §5 LOOCV 暦年齢予測 |
| `results/link_g_summary.csv` | Identity / SR link / §3 比較 |

詳細は `WORK_PLAN.md`、`WORK_PLAN_section5.md`、`analysis_third_AI_report.md` を参照。
