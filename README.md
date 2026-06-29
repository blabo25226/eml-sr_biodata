# EMLベース記号回帰によるチーター・エピジェネティック時計の関数同定

## 背景

エピジェネティック・クロック（Epigenetic Clock）は、DNAメチル化パターンから生物学的年齢を推定する手法である。従来のCheetahClockなどでは Elastic Net による線形回帰が用いられ、予測精度は高い一方で、メチル化部位間の非線形な相互作用や飽和・適応といった生物学的メカニズムは数式として明示されにくい。

本研究の目的は、**EML（Exp-Minus-Log）演算子を核とした記号回帰（シンボリック回帰）により、チーターのCpGメチル化データからエピジェネティック時計の関数を同定すること**である。具体的には、動的システムのモデリング向けに開発された MEb の文法探索と、連続最適化ベースの eml-sr ライブラリを、静的な回帰タスクに適応・改良し、解釈可能な非線形数式の発見を試みる。

対象データは、チーターのエピジェネティック・クロック研究（CheetahClock）に由来する **CpGサイトのメチル化率**である（`age_cheetah/`、`eml-sr_age_cheetah_AI/`）。データの生物学的背景と CheetahClock の概要は次節に述べる。

---

## チーターのエピジェネティック・クロック

### DNAメチル化とエピジェネティック・クロック

DNAメチル化は、DNA塩基（主にシトシン）にメチル基が付加されるエピジェネティック修飾である。同じゲノム配列を持つ細胞でも、組織や発達段階・加齢に伴いメチル化パターンは系統的に変化する。この変化の一部は個体の**生物学的年齢**と相関し、それを利用して暦年齢（chronological age）を推定するのが**エピジェネティック・クロック**（Epigenetic Clock）である。

ヒトをはじめ多くの哺乳類で、特定のゲノム領域のメチル化率が年齢とともに単調または準単調に変化することが知られている。Horvath らにより確立された手法では、多数のメチル化部位の測定値を説明変数、実年齢を目的変数とする回帰モデル（多くはペナルティ付き線形回帰）を構築し、未知サンプルの年齢を予測する。野生動物の保全では、形態や歯の形だけでは判別が難しい**実年齢の推定**が個体群動態の把握や繁殖管理に不可欠であり、メチル化に基づく時計は強力な分子ツールとなる。

### CpGサイトとメチル化率（beta値）

メチル化の測定単位として本研究で用いるのは **CpGサイト**（シトシン–リン酸–グアニンジヌクレオチド）である。ゲノム上の CpG 二量体に隣接するシトシンがメチル化されるかどうかを、DNAメチル化アレイなどの技術で定量する。各プローブ（例: `cg10501210`）は特定の CpG 座に対応し、サンプルごとに**メチル化率**が得られる。

メチル化アレイでは通常、0（非メチル化）から1（完全メチル化）の範囲の **beta値**（β値）として正規化される。本プロジェクトの `filtered_data.csv` に格納されている各列は、この beta値に相当する。エピジェネティック・クロックの回帰モデルでは、サンプル \(i\) に対し

$$
\text{Age}_i \approx f\bigl(\beta_{i,1}, \beta_{i,2}, \ldots, \beta_{i,p}\bigr)
$$

の形で、多数の CpG beta値 ($\beta_{i,j}$) から年齢を推定する。変数 \(p\) は数千〜数万に及ぶことがあり、サンプル数に比べて**高次元**であるため、変数選択や正則化が重要になる。

### チーターと CheetahClock

本研究が対象とするのは、絶滅危惧種**チーター**（*Acinonyx jubatus*）のエピジェネティック・クロック研究である（[Epigenetic clock and methylation studies in cheetahs](https://pmc.ncbi.nlm.nih.gov/articles/PMC12798976/pdf/pone.0336127.pdf)）。血液・皮膚・肝臓などの組織から DNA を抽出し、哺乳類汎用の **HorvathMammalMethylChip40** アレイでメチル化プロファイルを測定した。GEO 登録番号 **GSE310779** のデータ（`age_cheetah/GSE310779_series_matrix.txt`）が本プロジェクトの出発点である。

原著で構築された **CheetahClock** は、Elastic Net 回帰により年齢予測モデル（および性別予測モデル）を学習したものである。解析の流れ（`age_cheetah/CheetahClock_age_sex.Rmd`）はおおむね次の通りである。

1. **品質管理**: 外れ値サンプルの除去（WGCNA 等によるクラスタリング）
2. **バッチ補正**: ComBat による測定バッチ間の系統差の補正
3. **年齢変換（ASM補正）**: チーターは性成熟（ASM = 2歳）前後で成長・メチル化変化のペースが異なる。これを補正するため、実年齢を変換した **`Age_trans`** を目的変数とする
4. **モデル学習**: `cv.glmnet` による Elastic Net で、年齢に寄与する CpG サイトとその係数を推定

原著の年齢時計は **52個の CpG** を用い、血液・肝臓サンプルで高い相関（\(r \approx 0.97\)）を示した。本プロジェクトの記号回帰実験（`eml-sr_age_cheetah_AI/`）では、同じメチル化データに対し、線形の Elastic Net ではなく **EML ベースの非線形数式** \(f\) を探索し、エピジェネティック時計の関数形そのものを同定することを目指している。

---

## 方法

### 共通：データと前処理

- **データ**: チーターのDNAメチル化プロファイル（GEO: GSE310779 等、`age_cheetah/` に格納）。
- **目的変数**: 実年齢、または性成熟年齢（ASM=2）を考慮した対数変換年齢（`Age_trans`）。
- **説明変数**: 各CpGサイトのメチル化率（beta値）。eml-sr の第1段階では Elastic Net で変数選択したうえで、上位4 CpG に絞り込んで探索する。第2・第3段階では `filtered_data.csv` の全50 CpG を入力とした実験も行っている。

### MEb による記号回帰（`eml-sr_age_cheetah_AI/`）

MEb（`MEb/`、Amir Erez 論文の実装）は、EML演算子およびその変形（Gゲート等）を用いた文法探索型シンボリック回帰である。元の実装は時間変数 \(t\) を持つ**動的データ**（細胞応答の時系列）を対象としていた。

本研究では以下の改造を行い、**静的データ**への適応を実現した（詳細: `eml-sr_age_cheetah_AI/analysis_summary_report.md`）。

| 項目 | 元のMEb | 本研究での改造 |
| :--- | :--- | :--- |
| ベース変数 | 時間依存の \(R(t)\) | 抽出したCpGサイト \(V_0, V_1, \ldots\) |
| 目的関数 | 時系列の重み付き二乗誤差（wMSE） | 予測年齢と実年齢の最小二乗誤差（MSE） |
| 変数選択 | — | Elastic Net で上位4 CpG に絞り込み |
| 探索深度 | 論文既定 | `max_depth=5`（1,297パターンの全探索） |
| モデル選択 | AIC / BIC | AIC |

### eml-sr による記号回帰（段階的改良）

元の eml-sr（`eml-sr/`）は、EML演算子のみで構成される均質二分木をビームサーチし、連続最適化で数式を発見する Rust ライブラリである。本研究では次の3段階で適用・改良を行った。

#### 第1段階：Elastic Net 変数選択 + 原版 eml-sr（4 CpG）

高次元の CpG データに対し、探索前に sklearn の Elastic Net で変数選択を行い、選ばれたサイトだけを eml-sr に入力する（詳細: `eml-sr_age_cheetah_AI/preprocess.py`, `train_eml.py`）。

1. **変数選択**（`preprocess.py`）: 全 CpG に `ElasticNetCV`（`l1_ratio=0.5`, 5-fold CV）を適用し、係数の絶対値が大きい上位50サイトを `filtered_data.csv` に保存。係数一覧は `selected_features.csv`。
2. **4 CpG への絞り込み**: そのうち係数絶対値上位4つ（`cg10501210`, `cg12544505.2`, `cg23090567`, `cg10505126`）を探索変数とする。
3. **記号回帰**（`train_eml.py`）: 原版 `eml_sr` で `Age_trans` を予測。`max_complexity=10`, `beam_width=150`。線形 Elastic Net をベースラインと比較。

エンジン内の損失関数は MSE（定数への Elastic Net ペナルティなし）。

#### 第2段階：`eml-sr_model_first_AI`（定数の事後計算 / Model-First）

従来の eml-sr では ($ \pi, e $) などの固定定数が探索空間に含まれ、近似に探索リソースを消費する問題があった。改良版では以下を導入した（詳細: `eml-sr_model_first_AI/README.md`）。

- 数式木に未定パラメータ `Param` ノードを導入
- 各候補式の評価時に L-BFGS 等で定数を連続最適化（Model-First アプローチ）
- 上位レイヤーへの結合時もパラメータを再最適化可能な状態を維持

チーター実験では `filtered_data.csv` の全50 CpG を入力とした。結果は `analysis_second_AI_report.md` §4 に記載。

#### 第3段階：`eml-sr_model_second_AI`（損失関数の変更）

第2段階の実装に加え、損失関数を次のように変更した（詳細: `eml-sr_model_second_AI/daily_report.md`）。

- **変更前**: RMSE
- **変更後**: $$\text{Loss} = \text{MSE} + \alpha \cdot \left( \lambda_{\mathrm{L1}} \cdot \|C\|_1 + 0.5 \cdot (1 - \lambda_{\mathrm{L1}}) \cdot \|C\|_2^2 \right)$$（定数に対する Elastic Net ペナルティ）

$\alpha$（ペナルティ強度）と `l1_ratio`（L1/L2のバランス）は実行時に指定する。実行スクリプトは `eml-sr_age_cheetah_AI/train_eml_second_AI.py`。

---

## 結果

各手法の詳細な数値・考察は、対応フォルダ内のまとめレポートを参照のこと。

### MEb（静的回帰への適応）

出典: `eml-sr_age_cheetah_AI/analysis_summary_report.md`

AIC により選ばれた最適モデル:

$$\text{Canonical: } ((G(V_0) + G(V_2)) + V_3)$$

変数対応: \(V_0\) = `cg10501210`, \(V_2\) = `cg23090567`, \(V_3\) = `cg10505126`

| モデル（テストセット） | MAE | \(R^2\) |
| :--- | :---: | :---: |
| Elastic Net（ベースライン・線形） | 1.8233 | 0.5111 |
| MEb 適応版（深さ5・非線形） | 1.8873 | 0.4602 |

MEb は線形 Elastic Net には及ばなかったが、3つのCpGサイトが Gゲート（活性化・抑制モジュール）を経て合成される**解釈可能な非線形構造**を獲得した。訓練 MSE は 3.80 と良好であり、サンプル数の少なさに起因する過学習が示唆される。

### eml-sr 第1段階（Elastic Net 変数選択 + 4 CpG・原版 eml-sr）

出典: `eml-sr_age_cheetah_AI/analysis_summary_report.md` §4、`eml_model_results.txt`、`model_comparison.png`

- **前処理**: `preprocess.py` → `selected_features.csv`, `filtered_data.csv`
- **実行**: `train_eml.py`（4 CpG, `Age_trans`）
- **Test \(R^2\)**: 0.5208、**MAE**: 1.7851
- **獲得数式**:
  $$\text{Age}_{\mathrm{trans}} = \mathrm{cg10505126} + \ln(\mathrm{cg10505126}) + \mathrm{EML}(\arcsin(\arccos(\mathrm{cg10501210})), \mathrm{cg10501210})$$

同一4 CpG に対する線形 Elastic Net（\(R^2\) = 0.5111）を上回る非線形数式が得られた。変数選択を探索の外で行うことで、計算コストを抑えつつ解釈可能な式を発見できた。

### eml-sr 第2段階：`eml-sr_model_first_AI`（50 CpG・対数年齢）

出典: `eml-sr_age_cheetah_AI/analysis_second_AI_report.md` §4

- **ターゲット**: `Age_trans`（対数変換年齢）
- **入力**: `filtered_data.csv` の全50 CpG
- **最高性能**: Test \(R^2\) = 0.6195（複雑度10）

$$\exp(\arccos(v_{14})) - \ln(v_0) - \frac{1/v_{11}}{\sqrt{v_{27}}}$$

実年齢を直接予測した場合の最高 \(R^2\) = 0.5329 と比較し、対数変換年齢を用いることで精度が 0.60 台に向上することが確認された。

### eml-sr 第3段階：`eml-sr_model_second_AI`（MSE + 定数 Elastic Net）

出典: `eml-sr_age_cheetah_AI/analysis_second_AI_report.md`、`second_AI_results.txt`

- **設定**: `max_complexity=10`, `beam_width=1000`, `alpha=0.01`, `l1_ratio=0.5`
- **入力**: 全50 CpG（第2段階と同条件）
- **最高性能**: Test \(R^2\) = **0.6065**, MAE = 1.5785（複雑度9）

$$\frac{v_{11}}{v_{14}} \cdot e^{v_{29}} - \ln(v_2) - v_{28}$$

第2段階（\(R^2\) = 0.6195）と比べ精度はわずかに低下したが、平方根などの強引なフィッティングが剪定され、四則演算と指数・対数のみからなる**解釈しやすい数式**が得られた。

---

## 今後の展望

`nextplan.md` に基づく今後の計画は以下の通りである。

1. **過学習抑制アルゴリズムの実装**: 第3段階（定数の事後計算 + Elastic Net 適用）に、過学習抑制のオン/オフ機構を追加し、エピジェネティック時計関数の同定を再試行する。
2. **一般化線形モデル（GLM）への拡張**: リンク関数そのものをシンボリック回帰で求める。
3. **ニューラルシンボリック回帰**: 上記アプローチをニューラルネットワークと記号回帰のハイブリッドで実現する。

---

## 参考文献・ソースコード

### 論文

| 文献 | リンク |
| :--- | :--- |
| EML演算子の理論（eml-sr の数学的基盤） | [All elementary functions from a single operator](https://arxiv.org/abs/2603.21852) |
| MEb（EML文法探索・生物ダイナミクス） | [Non-Monotone Response Modules and Cascades from the EML Operator](https://arxiv.org/pdf/2605.02972) |
| チーター・エピジェネティック・クロック | [Epigenetic clock and methylation studies in cheetahs](https://pmc.ncbi.nlm.nih.gov/articles/PMC12798976/pdf/pone.0336127.pdf) |

### ソースコード

| リポジトリ | 内容 |
| :--- | :--- |
| [Amin7410/Project-Andrzej](https://github.com/Amin7410/Project-Andrzej) | eml-sr 原版の引用元（本プロジェクトの `eml-sr/`） |

### 本プロジェクト内の関連フォルダ

| フォルダ | 役割 |
| :--- | :--- |
| `MEb/` | MEb 原版コード（参照・ベースライン） |
| `age_cheetah/` | チーターデータと CheetahClock 原版解析 |
| `eml-sr/` | eml-sr 原版ライブラリ（第1段階で使用） |
| `eml-sr_model_first_AI/` | 第2段階：定数最適化（Model-First）改良版 |
| `eml-sr_model_second_AI/` | 第3段階：MSE + 定数 Elastic Net 損失関数改良版 |
| `eml-sr_age_cheetah_AI/` | チーター実験一式（`preprocess.py`, `train_eml.py`, `train_eml_second_AI.py` 等） |

作業ルールおよびドキュメント管理の詳細は `AGENTS.md` を参照。
