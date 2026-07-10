# eml-sr_model_fifth_AI

論文と同一構成の学習データ（**SDZWA 肝臓 + MCDB チーター血液 14**, $n=52$）で、Elastic Net・**eml-sr_fable**・PySR を比較するパイプライン。

入力データは `data/age_cheetah/`（gitignore 済み）:

| ファイル | 内容 |
|:---|:---|
| `GSE310779_series_matrix.txt` | SDZWA チーター（肝・血・皮） |
| `GSE223748_datBetaNormalized.csv` | MCDB 全 β（抽出元） |
| `cheetah_mamconsortium_betas.csv` | MCDB チーター血液 14（`extract_mcdb_cheetah.py` で生成） |
| `mcdb_cheetah_blood_meta.csv` | MCDB 14 の年齢・性別メタデータ |

## 手法

| Step | スクリプト | 手法 |
|:---:|:---|:---|
| R | `replicate_paper_enet.R` | 論文データ整形 + glmnet LOOCV |
| 0 | `step0_baseline_enet.py` | Step 0 指標の Python 再集計 |
| 1 | `step1_eml_sr_fable.py` | **eml-sr_fable** 記号回帰（上位 20 CpG） |
| 2 | `step2_pysr.py` | PySR（上位 20 CpG、オプション） |

## eml-sr_fable ビルド

```powershell
cd ..\eml-sr_fable
maturin develop --release --features python,full-math
```

詳細: `eml-sr_fable/manual_eml-sr_fable.md`

## 実行

```powershell
cd eml-sr_model_fifth_AI
python verify_data.py
python run_pipeline.py
```

MCDB 抽出のみ:

```powershell
python extract_mcdb_cheetah.py
```

PySR を除く:

```powershell
python run_pipeline.py r 0 1 compare
```

## 依存

- R: `glmnet`, `WGCNA`, `sva`（`install_r_packages.R`）
- `eml-sr_fable`: `maturin develop --release --features python,full-math`
- PySR（Step 2）: Julia 要

`config.py` の `RSCRIPT` を環境に合わせる。
