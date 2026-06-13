このファイルは `age_cheetah` フォルダと、それに関連するチーターのエピジェネティック・クロック論文をまとめたファイルである。

# 1. 論文の概要
タイトル： **Epigenetic clock and methylation studies in cheetahs** (関連論文)

本研究は、絶滅危惧種であるチーターの健康管理や保全活動に役立てるため、DNAメチル化データに基づくエピジェネティック・クロック（CheetahClock）を開発したものです。
チーターの血液や皮膚、肝臓などのメチル化データを用い、Elastic Net 回帰によって年齢予測モデルと性別予測モデルを構築しています。野生動物の正確な年齢推定は保全生態学において極めて重要であり、DNAメチル化という分子指標を用いることで、形態からは分かりにくい実年齢（生物学的年齢）を高い精度で予測できるようにしています。
また、チーターが性成熟に達するまでの成長スピードを補正するための年齢変換関数（ASM: Age at Sexual Maturity）を取り入れている点も特徴的です。

# 2. age_cheetah の概要
現在、`age_cheetah/` フォルダ内にはチーターの加齢・性別予測モデルを構築するための R スクリプトと関連データが格納されています。

各主要ファイルの内容は以下の通りです：
* `CheetahClock_age_sex.Rmd`: メチル化データの読み込み、前処理、および Elastic Net 回帰を用いた「年齢予測モデル」と「性別予測モデル」の構築を一貫して行う R Markdown スクリプト。
* `GSE310779_series_matrix.txt`: GEO (Gene Expression Omnibus) データベースから取得したチーターのDNAメチル化プロファイル（生データ/マトリックス）。

### 解析の流れ (`CheetahClock_age_sex.Rmd`)
1. **前処理・外れ値除去**: WGCNAパッケージを利用した階層的クラスタリングにより、メチル化データの外れ値サンプルを除去します。
2. **バッチ補正**: SVA (Surrogate Variable Analysis) パッケージの ComBat を使用し、異なる研究間のバッチ効果を補正します。
3. **年齢の変換**: 若年期の成長の速さを考慮し、対数線形モデルを用いた年齢変換（ASM=2歳）を適用します。
4. **モデル構築 (Elastic Net)**: `cv.glmnet` を用いてLOOCV (Leave-One-Out Cross-Validation) でペナルティ項 $\lambda$ を最適化し、スパースな予測モデル（CheetahClock_age.rds, CheetahClock_sex.rds）を作成します。

# 3. 略語・用語一覧
本ドキュメントおよび関連ファイル内で使用されている主な略語・用語の解説です。

* **CheetahClock**: 本研究で開発されたチーター専用のDNAメチル化時計（年齢・性別予測モデル）。
* **Elastic Net**: L1正則化（Lasso）とL2正則化（Ridge）を組み合わせた線形回帰の手法。高次元のメチル化データ（CpGサイト）から、年齢予測に本当に必要なサイトを選択（変数選択）しつつ過学習を防ぐために使用されます。
* **LOOCV**: Leave-One-Out Cross-Validation（個点抜き交差検証）。データセットのうち1つのサンプルをテスト用に残し、残りの全サンプルで学習を行うというプロセスを全サンプル分繰り返す検証手法。
* **WGCNA**: Weighted Gene Co-expression Network Analysis。本スクリプト内では主に `goodSamplesGenes` や階層的クラスタリングを用いてデータの品質管理・外れ値（outlier）の除去に使用されています。
* **SVA / ComBat**: Surrogate Variable Analysis。異なるバッチ（測定機関やタイミングの違い）に由来する系統的な誤差を取り除くための統計手法です。
* **ASM**: Age at Sexual Maturity（性成熟年齢）。チーターモデルでは ASM=2 と設定され、2歳以前のメチル化変化のスピードとそれ以降の変化スピードの違いを数式的に補正するために使用されています。
