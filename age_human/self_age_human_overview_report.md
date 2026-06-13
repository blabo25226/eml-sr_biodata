このファイルは `age_human` フォルダと、それに関連する論文（AltumAge）をまとめたファイルである。

# 1. 論文の概要
タイトル： **AltumAge: A pan-tissue DNA-methylation epigenetic clock based on deep learning**
著者： Lucas Paulo de Lima Camillo, Louis R Lapierre, Ritambhara Singh
掲載誌： npj Aging (2022)

DNAメチル化データから生物学的年齢を予測するエピジェネティック・クロックは、従来、線形モデル（Elastic Net回帰など、Horvathの2013年モデルが代表的）を用いて構築されてきました。
本研究では、ディープラーニング（深層学習）を活用した新たな汎組織（pan-tissue）エピジェネティック・クロックである **AltumAge** を開発しました。
AltumAge は、142もの公開データセットを用いた学習により、既存の線形モデルを複数の評価指標で上回る高い年齢予測精度を達成しています。多様な組織タイプや幅広い年齢層に対しても堅牢（ロバスト）なパフォーマンスを示す点が特徴です。

# 2. age_human の概要
現在、`age_human/` フォルダ内には AltumAge モデルの実行に必要な Python スクリプト、Jupyter Notebook、および事前学習済みのディープラーニングモデルが格納されています。

各主要ファイル・フォルダの内容は以下の通りです：
* `README.md`: AltumAge の概要、特徴、環境構築方法（TensorFlow および PyTorch）、および使い方をまとめたドキュメント。
* `AltumAge_code.ipynb`: AltumAge モデルの学習や評価のプロセスを詳細に記述したメインのノートブック。
* `example.ipynb`: AltumAge を使って実際にサンプルデータから年齢を予測する手順を簡潔に示したチュートリアルノートブック。
* `example_dependencies/`: 予測に必要な以下のファイルが格納されています。
  * `AltumAge.h5`: 事前学習済みの TensorFlow / Keras モデル。
  * `multi_platform_cpgs.pkl`: モデルの入力として必要な 20,318 個の CpG サイトのリスト。
  * `scaler.pkl`: データを前処理するためのスケーラー（RobustScaler）。
* `requirements.txt`: 実行に必要な Python パッケージ（tensorflow==2.5.0 など）のリスト。

# 3. 略語・用語一覧
本ドキュメントおよび関連ファイル内で使用されている主な略語・用語の解説です。

* **AltumAge**: 深層学習（ディープラーニング）に基づく汎組織エピジェネティック・クロックの名称。
* **Pan-tissue**: 「汎組織」の意。特定の臓器や血液だけでなく、皮膚、脳、唾液など、人体のさまざまな組織データにまたがって適用できるモデルであることを示します。
* **CpG site**: DNAの配列上でシトシン（C）の次にグアニン（G）が続く部分。哺乳類のゲノムでは、このシトシンにメチル基が付加される（DNAメチル化）ことが多く、エピジェネティック・クロックの指標として利用されます（AltumAgeでは20,318サイトを使用）。
* **Deep Learning (深層学習)**: ニューラルネットワークを用いた機械学習の手法。線形回帰では捉えきれない、メチル化データと年齢の間の複雑で非線形な関係性を学習できるのが強みです。
* **Illumina arrays (27k, 450k, EPIC)**: イルミナ社が提供するDNAメチル化を網羅的に測定するためのマイクロアレイチップ。AltumAge はこれらのマルチプラットフォームのデータに対応しています。
