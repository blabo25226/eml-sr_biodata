# §5 作業計画書（改訂）— GLM リンク関数 $g$ のシンボリック回帰

**作成日**: 2026/06/30  
**対象ブランチ**: `20260630_create_model_third`  
**編集範囲**: `eml-sr_model_third_AI/` および `daily_report.md`（§3・§4 は変更しない）  
**方針**: 現行 §5（`train_link_sr.py`、レポート §5、関連 results）を**破棄**し、本計画に基づき作り直す

---

## 0. 改訂の理由（現行 §5 の問題）

現行実装は **Age → `age_trans`（ASM 変換）** の単変量 SR だった。

- `age_trans` は Age の決定的変換であり、**説明変数と目的変数が同じ情報の別表現**に近い
- $r$ が高いのは当然で、**リンク関数の同定**にならない
- `nextplan.md` #1「一般化線形モデルのリンク関数を SR で求める」の意図と不一致

---

## 1. 目的（正しい定式化）

一般化線形モデル（GLM）として、CheetahClock の線形部分とリンクを分離する。

$$
E(\texttt{age\_trans}) = g^{-1}(\eta), \qquad
\eta = \beta_0 + \sum_{j=1}^{p} \beta_j \,\mathrm{CpG}_j
$$

| 記号 | 意味 |
|:---|:---|
| $\mathrm{CpG}_j$ | ComBat 補正後のメチル化率 $\beta$（第 $j$ サイト） |
| $\eta$ | **線形予測子**（定数 + CpG の線形結合；glmnet で推定） |
| $\texttt{age\_trans}$ | ASM 変換年齢（応答変数；§2 前処理で算出） |
| $g$ | **リンク関数**（今回 SR で探索する対象） |
| $g^{-1}$ | 平均応答を与える逆リンク |

原著 glmnet は実質 **恒等リンク** $g^{-1}(\eta)=\eta$（すなわち $\texttt{age\_trans} \approx \eta$）でフィットしている。  
本 §5 では **$g$ を eml-sr でデータから推定**し、恒等リンク・固定 ASM パイプラインと比較する。

### 1.1 なぜ循環にならないか

| 量 | 由来 |
|:---|:---|
| $\eta$ | **CpG $\beta$ のみ**から構成（メチル化） |
| $\texttt{age\_trans}$ | **暦年齢**から ASM で構成（年齢側変換） |

$g$ は **メチル化線形スコアと変換年齢の間**を結ぶ。Age を $\eta$ の説明変数にする現行 §5 とは異なる。

---

## 2. 参照・前提

| 項目 | 内容 |
|:---|:---|
| 前処理 | 既存 `preprocess_clock.R` の出力をそのまま使用（§2 再実行不要） |
| 線形結合 | §3 と同じ glmnet（`alpha=0.5`, LOOCV $\lambda$）の係数・線形予測子 |
| SR エンジン | `eml-sr_model_first_AI`（`find_function` / `find_candidates`） |
| TeX | `AGENTS.md` に従う（`$...$` / `$$...$$`；`\approx` 等は可） |

---

## 3. 破棄・置換するファイル

| 操作 | パス |
|:---|:---|
| **削除** | `train_link_sr.py` |
| **削除** | `results/link_sr_results.txt`, `results/link_sr_results.json` |
| **新規** | `train_link_g_sr.py`（§5 本体） |
| **書き換え** | `analysis_third_AI_report.md` の **§5 のみ**（§1–4, §6–8 は維持） |
| **更新** | `run_pipeline.py`（link ステップを新スクリプトに差し替え） |
| **更新** | `daily_report.md`（作業記録） |

§5 の説明・結果は **`eml-sr_model_third_AI/analysis_third_AI_report.md` の §5 のみ** に記載する（ルート `README.md` は変更しない）。

`WORK_PLAN.md` フェーズ 4 の旧記述は、承諾後に本計画への参照コメントを追記する（任意）。

---

## 4. 実装手順

### ステップ 1: 線形予測子 $\eta$ の取得

1. `data/beta_combat.csv`, `data/clock_samples.csv` を読み込む
2. §3 と同条件で glmnet 相当の線形モデルを構築
   - **推奨**: R の `preprocess_clock.R` 出力の `selected_cpgs.csv` および `baseline_loocv.csv` を活用
   - 全データ fit で $\hat\beta$ を得て、各サンプル $i$ について  
     $\eta_i = \hat\beta_0 + \sum_j \hat\beta_j \,\mathrm{CpG}_{ij}$
3. `data/linear_predictor.csv` に保存（列: `GSM`, `age_trans`, `eta`, `Age`）

**注意**: LOOCV 評価時は **各 fold で $\eta$ を再計算**（データリーク防止）。

### ステップ 2: リンク関数 $g$ の SR

GLM のリンクは $g(E[y]) = \eta$。観測 $(\texttt{age\_trans}_i, \eta_i)$ に対し

$$
g(\texttt{age\_trans}_i) \approx \eta_i
$$

を満たす $g$ を **単変量 SR** で探索する。

| 実装 | 内容 |
|:---|:---|
| 入力 $x$ | $\texttt{age\_trans}_i$ |
| ターゲット $y$ | $\eta_i$ |
| API | `searcher.find_function(age_trans, eta)` および `find_candidates` |
| 探索設定 | `config.py` の `BEAM_WIDTH`, `MAX_COMPLEXITY`（リンク用に `MAX_COMPLEXITY_LINK` を追加可） |

得られた $ \hat g $ について、逆リンク $\hat g^{-1}$ で $\widehat{\texttt{age\_trans}}_i = \hat g^{-1}(\eta_i)$ を数値的に評価する（必要ならグリッドまたは 1 次元 Newton）。

**恒等リンク基準**: $g(\texttt{age\_trans}) = \texttt{age\_trans}$（すなわち $\eta \approx \texttt{age\_trans}$）との MSE / $r$ を比較。

### ステップ 3: 評価（意味のある指標）

| 評価 | 内容 |
|:---|:---|
| **リンク尺度** | $\mathrm{MSE}(g(\texttt{age\_trans}), \eta)$、Pearson $r$ |
| **応答再構成** | $\mathrm{MSE}(\hat g^{-1}(\eta), \texttt{age\_trans})$ |
| **暦年齢 LOOCV** | 各 fold: CpG → $\eta$（glmnet）→ $\hat g^{-1}(\eta)$ → `age_trans` 予測 → **逆 ASM** → 暦年齢；§3 の EN LOOCV $r$, MAE と**同じ指標**で比較 |
| **基準線** | (a) 恒等リンク $\hat y = \eta$、(b) §3 glmnet LOOCV（既存 `baseline_loocv.csv`） |

**主評価指標**は §3 と揃え **LOOCV 上の暦年齢 $r$ と MAE**。リンク尺度の $r$ だけでは判断しない（現行 §5 の教訓）。

### ステップ 4: 出力

| ファイル | 内容 |
|:---|:---|
| `data/linear_predictor.csv` | $\eta$, `age_trans`, Age |
| `results/link_g_sr_results.txt` | 上位候補 $g$、LaTeX、複雑度、各種 MSE |
| `results/link_g_loocv.csv` | LOOCV 暦年齢予測（恒等 vs SR リンク） |
| `results/link_g_summary.csv` | $r$, MAE 比較表 |

---

## 5. レポート §5 の構成（書き直し後）

1. **GLM 定式化**（上記数式）
2. **推定手順**（$\eta$ の取り方、SR で $g$ を求める向き）
3. **結果表**（恒等リンク vs SR リンク；LOOCV $r$, MAE）
4. **考察**（$g$ が恒等からどうずれるか；生物学解釈の草案）
5. **旧 §5 との関係**（Task A/B は破棄した旨を 1 文）

---

## 6. リスクと対策

| リスク | 対策 |
|:---|:---|
| $\hat g^{-1}$ が数値不安定 | 単調性チェック；複雑度上限；恒等リンクにフォールバック比較 |
| LOOCV で SR 再探索は重い | **fold 内**: glmnet のみ再 fit；**$g$ は全データで一度推定**した式を固定して LOOCV（限界をレポートに明記）。余力があれば fold 内 SR |
| $\eta$ と `age_trans` のスケール差 | 標準化オプションを `config.py` に用意（デフォルトは生スケール） |

---

## 7. スケジュール目安

| ステップ | 目安 |
|:---|:---:|
| 旧ファイル削除・`train_link_g_sr.py` 実装 | 0.5–1 日 |
| LOOCV 評価・結果 CSV | 0.5 日 |
| レポート §5 書き換え・`daily_report`・commit | 0.5 日 |
| **合計** | **約 1.5–2 日** |

---

## 8. 承諾時の確認事項

1. **CpG 集合**: §3 glmnet の非ゼロ CpG 全件（42 前後）か、§4 と同様 **上位 15** に限定するか  
2. **LOOCV と SR**: 上記「$g$ 固定・$\eta$ のみ fold 内 refit」でよいか（厳密 fold 内 SR は時間がかかる）  
3. **恒等リンク以外の基準**: 論文 ASM は `age_trans` 定義に既に含まれるため、**応答側の $g$** の比較は恒等 vs SR のみでよいか  

---

## 9. 承諾後の着手順

1. 旧 `train_link_sr.py` と `results/link_sr_*` を削除  
2. `train_link_g_sr.py` 実装・実行  
3. `analysis_third_AI_report.md` §5 差し替え  
4. `run_pipeline.py` 更新  
5. `daily_report.md` 追記・`git commit`（push なし）

---

**本計画を承諾いただければ、§5 の作り直しを開始します。**
