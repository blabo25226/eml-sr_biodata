# eml-sr_model_fifth_AI

論文と同一構成の学習データ（**SDZWA 肝臓 + MCDB チーター血液 14**）で、Elastic Net・EML-SR・PySR を比較するパイプライン。

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
| 0 | `step0_baseline_enet.py` | R `glmnet` Elastic Net + 厳密 LOOCV（論文再現） |
| 1 | `step1_eml_sr.py` | EML-SR（上位 20 CpG） |
| 2 | `step2_pysr.py` | PySR（上位 20 CpG） |

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
- `eml-sr_model_first_AI`: `maturin develop --features python`
- PySR（Step 2）: Julia 要

`config.py` の `RSCRIPT` を環境に合わせる。
