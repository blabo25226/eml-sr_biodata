# eml-sr_model_third_AI 作業計画書

**ブランチ**: `20260630_create_model_third`  
**作成日**: 2026/06/30  
**編集対象**: `eml-sr_model_third_AI/` および `daily_report.md` のみ（`git push` 禁止、`git add` / `git commit` 可）

---

## 1. 目的

チーター GSE310779（GEO Series Matrix）を出発点に、原著 `age_cheetah/CheetahClock_age_sex.Rmd` に準じた前処理を **R** で実装し、その上で

1. **線形 Elastic Net + LOOCV**（論文ベースライン再現）
2. **`eml-sr_model_first_AI` による多変量シンボリック回帰**（CpG → 変換年齢）
3. **GLM リンク関数のシンボリック回帰**（実年齢 → 変換年齢 \(g(\text{Age})\) の探索）

を同一評価枠組み（LOOCV）で比較する。

---

## 2. 参照元と既知の制約

### 2.1 参照コード

| 参照 | 役割 |
|:---|:---|
| `age_cheetah/CheetahClock_age_sex.Rmd` | 前処理・ComBat・ASM・`cv.glmnet`・LOOCV の手順 |
| `age_cheetah/data_souorce.md` | GEO は全 CpG・全サンプル・外れ値未除去である旨 |
| `age_cheetah/GSE310779_series_matrix.txt` | 入力データ（SeSaMe 正規化済み β、57 サンプル） |
| `eml-sr_model_first_AI/` | 記号回帰エンジン（`find_candidates`, `fit`, `predict`） |
| `eml-sr_age_cheetah_AI/preprocess.py` | GEO 読み込み・ASM の既存実装（簡易版） |

### 2.2 GEO 単体では完全再現できない点（計画に明記する）

原著 Rmd は **内部 RDS**（`beta_sesame_shifted.RDS` 等）と **MCDB 血液データ**（`cheetah_mamconsortium_betas.csv`）を使用する。これらはリポジトリに無い。

| 項目 | 原著 | 本計画（GEO ベース） |
|:---|:---|:---|
| メチル化 β | SeSaMe RDS（2 submission 結合） | GEO Series Matrix（既に SeSaMe 処理済みと記載） |
| 時計学習サンプル | 肝臓 + MCDB 血液 | **GEO 内の liver + blood のみ**（skin は検証用として別枠） |
| 外れ値 ID | 著者 SID（例: `ET0394TOX00092`） | **Rmd 記載リストを GEO メタデータと突合**して除去；突合不能 ID はログに記録 |
| バッチ | `cheetah_info_clock$study`（SDZWA / MammCon） | **GEO から推定**（抽出プロトコル Qiagen vs Monarch、idat ファイル名プレフィックス等） |
| LOOCV \(r\) | 論文値 \(r \approx 0.97\) | **完全一致は保証しない**；再現度をレポートで報告 |

上記は `analysis_third_AI_report.md` の「限界」節に必ず記載する。

---

## 3. 成果物一覧

### 3.1 コード（`eml-sr_model_third_AI/`）

```
eml-sr_model_third_AI/
├── WORK_PLAN.md                 # 本計画書
├── README.md                    # 実行手順・依存関係
├── requirements.txt             # Python 依存
├── config.py                    # パス・ハイパーパラメータ（一元管理・後から変更容易）
│                                #   N_CP_G_FOR_SR=15, BEAM_WIDTH=500, MAX_COMPLEXITY=10 等
├── geo_io.py                    # GEO Series Matrix 読み込み・メタデータ構築
├── preprocessing.py             # 外れ値除去・ComBat・ASM・保存
├── baseline_enet.py             # glmnet 相当の Elastic Net + LOOCV
├── train_eml_sr.py              # first_AI 多変量 SR（CpG → age_trans）
├── train_link_sr.py             # first_AI 単変量 SR（Age → link 変換）
├── run_pipeline.py              # 上記を順に実行するエントリポイント
├── data/                        # 生成物（git 追跡は .gitignore で制御）
│   ├── clock_samples.csv
│   ├── beta_combat.csv
│   └── selected_cpgs.csv
└── analysis_third_AI_report.md  # 結果まとめレポート（実行後に更新）
```

### 3.2 レポート

| ファイル | 内容 |
|:---|:---|
| `daily_report.md` | 作業ログ（日付・実施内容） |
| `eml-sr_model_third_AI/analysis_third_AI_report.md` | 手法・数値結果・考察・原著との差分 |

### 3.3 Git

- フェーズ完了ごとに `git add` + `git commit`（push はしない）
- コミット例: `feat(third_AI): add GEO preprocessing pipeline`, `feat(third_AI): LOOCV EN baseline`, 等

---

## 4. 実装フェーズ

### フェーズ 0: 環境・スケルトン（半日）

- [ ] `eml-sr_model_third_AI/` ディレクトリ・`README.md`・`requirements.txt` 作成
- [ ] `eml-sr_model_first_AI` を `maturin develop` または既存 wheel で import 可能にする手順を README に記載
- [ ] `config.py`: データパス `../age_cheetah/GSE310779_series_matrix.txt`、探索設定（`max_complexity=10`, `beam_width` はメモリに応じ 500〜1000）

**依存パッケージ（予定）**: `numpy`, `pandas`, `scikit-learn`, `scipy`, `matplotlib`, `pycombat`（または `combat`）

---

### フェーズ 1: 論文準拠前処理（Python）（1〜2日）

`CheetahClock_age_sex.Rmd` の年齢時計構築部分（L38〜L211）を GEO 向けに移植。

#### 1-A. GEO 読み込み（`geo_io.py`）

- `!Sample_geo_accession`, `!Sample_title`, `!Sample_source_name_ch1`, `!Sample_characteristics_ch1`, `!Sample_extract_protocol_ch1`, `!Sample_supplementary_file` をパース
- 各サンプルについて: `GSM_ID`, `Age`, `Tissue`（liver / blood / skin）, `Sex`（title から）, `batch`（プロトコルまたは idat 名から `SDZWA` / `MammCon` 相当を付与）
- β 行列: CpG × サンプル → サンプル × CpG（float）

#### 1-B. 学習コホートの定義

- **時計学習用**: `Tissue ∈ {liver, blood}` のみ（skin は除外）
- Rmd と同様、欠損年齢サンプルを除外

#### 1-C. 品質管理・外れ値除去（`preprocessing.py`）

1. **WGCNA 相当**: `goodSamplesGenes` に近い処理（全欠損 CpG 除去、サンプル/遺伝子の欠損率閾値）— `scipy` 階層クラスタリング + 距離閾値
2. **手動除去リスト**（Rmd L86–87）:
   - クラスタ外れ値: `ET0394TOX00092`, `ET0394TOX00094`, `ET0394TOX00063`, `ET0394TOX00095`
   - 死産: `ET0394TOX00084`, `ET0394TOX00080`, `ET0394TOX00069`
   - → GEO の `!Sample_supplementary_file` 内 idat 名と突合して `GSM_ID` に変換；変換表を `data/sid_gsm_map.csv` に保存
3. 除去後サンプル数・ID をログ出力

#### 1-D. ComBat バッチ補正

- `pycombat.Combat(dat=beta.T, batch=batch_vector)`（遺伝子×サンプル形式で実装）
- 補正前後の PCA を `data/pca_before_after.png` に保存

#### 1-E. ASM 年齢変換

Rmd L129–150 と同一:

\[
g(x) = \begin{cases}
\log\frac{x+k}{\text{ASM}+k} & (x < \text{ASM}) \\
\frac{x-\text{ASM}}{\text{ASM}+k} & (x \geq \text{ASM})
\end{cases}
\quad (\text{ASM}=2,\; k=0.2)
\]

逆変換 \(g^{-1}\) も実装（LOOCV 評価用）。

#### 1-F. 出力

- `data/clock_samples.csv`: メタデータ + `age_trans`
- `data/beta_combat.csv`: ComBat 後 β（サンプル × CpG）

**フェーズ 1 完了基準**: スクリプト単体実行で上記 CSV が生成され、サンプル数・年齢分布が妥当であること。

---

### フェーズ 2: Elastic Net ベースライン + LOOCV（`baseline_enet.py`）（1日）

Rmd L164–226 に準拠。

1. `cv.glmnet` 相当: `ElasticNetCV(l1_ratio=0.5, cv=n_samples)` で `lambda.min` を取得（`sklearn.linear_model.ElasticNetCV`）
2. **LOOCV ループ**（各 fold で学習 → 左-out 1 件予測）
3. 予測 `age_trans` → 逆 ASM → 暦年齢
4. 指標: **Pearson \(r\)**, **MAE**（原著と同じく LOOCV 上で報告；\(R^2\) も参考値として併記）
5. 非ゼロ係数 CpG を `data/selected_cpgs.csv` に保存（個数 ≈ 52 を目安に報告）

**比較対象**: 前処理なし簡易版（旧 `preprocess.py` 相当）との差分はレポートに表で記載（可能なら数値のみ再計算）。

---

### フェーズ 3: `eml-sr_model_first_AI` 多変量 SR（`train_eml_sr.py`）（1〜2日）

#### 3-A. 入力設計

- **説明変数**: フェーズ 2 で選ばれた CpG の **\|coef\| 上位 10〜20**（デフォルト 15、`config.py` の `N_CPG_FOR_SR` で変更）
- **目的変数**: `age_trans`（変換年齢）
- **評価**: LOOCV（各 fold で first_AI を学習サンプルのみで探索は計算量大のため、下記の二段階方式を採用）

#### 3-B. 計算量対策（LOOCV × SR）

| 方式 | 内容 |
|:---|:---|
| **主方式** | 全データで一度 `find_candidates` → パレート上位式を LOOCV で評価（構造固定・係数は fold 内再フィットは eml-sr 非対応のため、**式構造を固定して fold 外予測**） |
| **補助** | 全データ学習のベスト式 + 80/20 ホールドアウト（`eml-sr_age_cheetah_AI` と比較用・参考値） |

※ 厳密な LOOCV 再探索は \(n\) 回 × 探索コストで非現実的なため、レポートに**評価の限界**を明記。可能であれば \(n \leq 15\) のサブセットで探索付き LOOCV を追加検証。

#### 3-C. 探索設定

- `Searcher(max_complexity=10, beam_width=500)` — **`config.py` の `BEAM_WIDTH` / `MAX_COMPLEXITY` で変更**（OOM 時は `BEAM_WIDTH` を下げる）
- `find_candidates` → Test / LOOCV で \(r\), MAE, 数式（LaTeX）

#### 3-D. ベースラインとの比較表

| モデル | LOOCV \(r\) | LOOCV MAE | 備考 |
|:---|:---:|:---:|:---|
| Elastic Net（フェーズ 2） | | | 線形・52 CpG 前後 |
| eml-sr first_AI | | | 非線形数式 |

---

### フェーズ 4: GLM リンク関数のシンボリック回帰（`train_link_sr.py`）（1日）

**目的**: 固定 ASM 公式の代わりに、実年齢 \(x\) から変換年齢 \(y = g(x)\) を **単変量 SR** で発見し、生物学的解釈とフィット精度を比較する。

#### 4-A. 手順

1. フェーズ 1 のコホート（ComBat 後）で、各 CpG の年齢との相関が高い上位 1 CpG（または EN 第 1 主成分相当のスコア）を **参照メチル化スコア** \(m\) として算出
2. **固定 ASM** の \(g_{\text{ASM}}(\text{Age})\) と LOOCV EN 予測の相関を基準線とする
3. `eml-sr_model_first_AI.find_function(ages, targets)` で \(g(\text{Age})\) を探索
   - **targets 案 A**: 既知の `age_trans`（ASM）— SR が ASM を再発見できるか（検証）
   - **targets 案 B**: EN による \(\hat{y}\)（線形予測スコア）— **データ駆動リンク**の探索
4. 発見式 \(g\) の逆変換可能性・定義域（\(x \geq 0\)）をチェック
5. \(g_{\text{SR}}\) を用いた場合の LOOCV 時計精度（CpG 固定・リンクのみ差し替え）を報告

#### 4-B. 成功基準（定性的）

- ASM 再現実験（案 A）で ASM と同等または近い MSE
- 案 B で非自明な式が得られ、解釈可能な項（log, 区分的線形に近い構造等）が含まれる

---

### フェーズ 5: 統合実行・レポート・コミット（半日）

- [ ] `run_pipeline.py`: `preprocess → baseline_enet → train_eml_sr → train_link_sr`
- [ ] `analysis_third_AI_report.md` 完成（§1 概要、§2 前処理、§3 EN 結果、§4 eml-sr 結果、§5 リンク SR、§6 考察、§7 原著との差分）
- [ ] `daily_report.md` 更新（2026/06/30 作業記録）
- [ ] `git commit`（push なし）

---

## 5. 評価指標の統一

原著に合わせ、**主指標**は LOOCV 上の

- Pearson 相関 \(r\)（暦年齢 vs 逆変換予測年齢）
- MAE（年）

**副指標**: \(R^2\)、選ばれた CpG 数、数式複雑度。

---

## 6. リスクと対策

| リスク | 対策 |
|:---|:---|
| MCDB 血液が GEO に無く \(n\) が小さい | サンプル数をレポートに明記；原著との差を限界として記述 |
| 外れ値 SID と GSM の突合失敗 | 突合表を公開；クラスタリングのみの除去をフォールバック |
| eml-sr 探索が重い | `beam_width` 削減；CpG 数を 52 → 10 への段階的実験 |
| ComBat が小サンプルで不安定 | バッチ変数の確認；失敗時はバッチ補正なし版も併記 |
| first_AI 未ビルド | README に `maturin develop -m eml-sr_model_first_AI/Cargo.toml` を記載 |

---

## 7. スケジュール目安

| フェーズ | 目安 |
|:---|:---:|
| 0. スケルトン | 0.5 日 |
| 1. 前処理 | 1〜2 日 |
| 2. EN + LOOCV | 1 日 |
| 3. eml-sr SR | 1〜2 日 |
| 4. リンク SR | 1 日 |
| 5. レポート・commit | 0.5 日 |
| **合計** | **約 4〜6 日** |

---

## 8. 承諾後の着手順

1. フェーズ 0 → 1 の `geo_io.py`, `preprocessing.py` 実装・実行確認  
2. フェーズ 2 でベースライン数値取得（ここで原著 \(r \approx 0.97\) との乖離を確認）  
3. フェーズ 3・4 を並行可能な範囲で実装  
4. フェーズ 5 でレポート・commit  

---

## 9. 確認事項（ユーザー回答・2026/06/30）

| # | 項目 | 決定 |
|:---:|:---|:---|
| 1 | eml-sr 入力 CpG 数 | **\|coef\| 上位 10〜20**（デフォルト 15、`config.py` で変更可） |
| 2 | `beam_width` | **500**（`config.py` で後から変更容易にする） |
| 3 | 皮膚サンプル | **学習から除外・事後検証のみ** — 承認済み |
| 4 | リンク SR | **案 A（ASM 再現）と案 B（EN スコア）の両方** — 承認済み |

---

## 10. 前処理は Python か R か（承諾前の設計判断）

### 10.1 当初 Python にした理由

| 理由 | 説明 |
|:---|:---|
| **パイプライン統合** | `eml-sr_model_first_AI` は Python バインディング。前処理 → SR → 評価を **1 言語**でつなげやすい |
| **既存実装の継承** | `eml-sr_age_cheetah_AI/preprocess.py` が GEO 読み込み・ASM を既に持つ |
| **実行環境** | Rust/Python 中心の開発環境で、R の依存（`glmnet`, `WGCNA`, `sva`）を毎回そろえるコストを避けたかった |

### 10.2 Python 単独の弱点

原著 `CheetahClock_age_sex.Rmd` は **R 専用スタック**で書かれている。

| 処理 | 原著（R） | Python 移植 |
|:---|:---|:---|
| 外れ値・QC | `WGCNA::goodSamplesGenes` + `hclust` | `scipy` 近似（挙動が完全一致しない可能性） |
| バッチ補正 | `sva::ComBat` | `pycombat` 等（実装差で数値がずれる可能性） |
| 回帰 | `glmnet::cv.glmnet`（`alpha=0.5`, LOOCV） | `sklearn.ElasticNetCV`（正則化パラメータのスケールが異なる） |

**論文の \(r \approx 0.97\) に「できるだけ近づける」ことが主目的なら、R の方が有利**である。理由は、再実装ではなく **同じパッケージ・同じ関数**を使えるからである。

### 10.3 推奨方針（計画改訂案）

**ハイブリッド**を推奨する（承諾時に最終決定）。

```
[前処理・ベースライン]          [記号回帰・評価]
preprocess_clock.R      →      train_eml_sr.py (Python + first_AI)
  (GEO 読込・ComBat・ASM)       train_link_sr.py
  baseline LOOCV (glmnet)       run_pipeline.py（R 出力 CSV を読む）
        ↓
  data/beta_combat.csv
  data/clock_samples.csv
  data/selected_cpgs.csv
```

| 方式 | メリット | デメリット |
|:---|:---|:---|
| **A. R 前処理 + Python SR**（推奨） | 論文との一致度が最も高い；Rmd を GEO 向けに改修しやすい | R 実行環境が必要 |
| **B. Python のみ** | 環境が単純；既存 `preprocess.py` を拡張 | 数値が原著からずれるリスク大 |
| **C. R と Python 両方** | ずれの原因を切り分け可能 | 工数・メンテが増える |

**本プロジェクトの目的**（論文パイプライン上で eml-sr を比較）を考えると、**フェーズ 1〜2 は R（`preprocess_clock.R`）、フェーズ 3〜4 は Python** が妥当である。`eml-sr_model_third_AI/` 内に R スクリプトを置くことは、作業フォルダ制約に抵触しない。

Python のみを続ける場合は、レポートに「移植による差」を明示し、ベースライン \(r\) が論文に届かなくても **相対比較（EN vs eml-sr）** に主眼を置く、と位置づける。

### 10.4 承諾時の追加確認

**前処理の実装言語**を選んでください。

- **案 A（推奨）**: R で前処理 + glmnet LOOCV → CSV → Python で eml-sr  
- **案 B**: Python のみ（計画書初版どおり）  
- **案 C**: R と Python の両方で前処理し、差分をレポート  

---

**§9 のパラメータ決定 + §10 の言語方針が確定し、承諾いただければコーディングを開始します。**
