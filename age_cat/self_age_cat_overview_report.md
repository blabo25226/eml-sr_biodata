このファイルは `age_cat` フォルダと、それに関連する論文（Mammalian Methylation Consortium関連の研究やネコの加齢クロックに関する論文）をまとめたファイルである。

# 1. 論文の概要
タイトル： **Epigenetic clock and methylation studies in cats** (および Mammalian Methylation Consortium 関連論文)
著者： Mammalian Methylation Consortium (Haghani, A. ら)

DNAメチル化の加齢に伴う変化を利用して生物学的年齢を推定する「エピジェネティック・クロック（Epigenetic clock）」は、多くの哺乳類で開発されています。
本研究群では、Mammal40k や Mammal320k といった哺乳類全般の保存された配列をターゲットとするメチル化アレイを開発し、ネコを含むさまざまな哺乳類種にまたがる「汎哺乳類（pan-mammalian）エピジェネティック・クロック」や、各種特有のクロックを構築しています。
特に最近の進展として、アンサンブル学習を用いて複数のクロックモデルを組み合わせることで、種や組織の違いを超えて高い精度で年齢を予測する **EnsembleAge** パッケージなども提案されています。

# 2. age_cat の概要
現在、`age_cat/` フォルダ内には Mammalian Methylation Consortium から提供された各種ソースコードやメタデータが格納されています。

各主要ファイル・フォルダの内容は以下の通りです：
* `README.md`: Mammalian Methylation Consortium の GitHub ページの内容をまとめたドキュメント。各コードの概要や引用論文が記載されています。
* `EnsembleAge/`: 複数のプラットフォーム（Human, Mammal40k, Mammal320k）に対応し、自動で最適なエピジェネティック年齢予測を行う R パッケージ。
* `UniversalPanMammalianClock/`: 哺乳類全体で共通して使える汎用クロック（Universal blood/skin clocks など）の構築コード。
* `MammalianMethylationPredictors/`: 特定の種、組織、あるいは性別などを予測するためのモデル群。
* `FundamentalEquations/`, `MammalianNetworkAnalysis, Amin Haghani/` 等: データ解析やネットワーク解析に使用される基盤となる R コード群。

# 3. 略語・用語一覧
本ドキュメントおよび関連ファイル内で使用されている主な略語・用語の解説です。

* **Epigenetic clock**: エピジェネティック・クロック（DNAメチル化時計）。DNAの特定のCpGサイトにおけるメチル化レベルの加齢に伴う変化を機械学習モデルで学習し、生物学的な年齢を推定する手法。
* **Mammal40k / Mammal320k**: 哺乳類間で高度に保存されたDNA配列上にあるCpGサイトを選択的に搭載した、カスタムDNAメチル化アレイ。これにより、ヒト用のアレイでは難しかった異種間での直接的な比較や普遍的な加齢モデルの構築が可能になりました。
* **EnsembleAge**: 複数のエピジェネティック・クロック（Static, Dynamic, Universal など110以上のモデル）をアンサンブル手法で統合し、より頑健で正確な年齢予測を行う R パッケージ。
* **Pan-mammalian**: 「汎哺乳類」の意。特定の1種だけでなく、多様な哺乳類種に共通して適用できるモデルや解析を指します。
