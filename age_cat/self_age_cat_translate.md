# ネコにおけるエピジェネティック時計とメチル化の研究 (Epigenetic clock and methylation studies in cats)

## 概要 (Abstract)
ヒトのDNAメチル化プロファイルは、高精度な老化のバイオマーカー（「エピジェネティック時計」）の開発に成功裏に用いられてきました。これらのヒト用エピジェネティック時計が、動物界のすべての種に直ちに適用できるわけではありませんが、その基盤となる原理は、進化的にヒトから遠く離れた動物においてさえも保存されているように見えます。これは、マウスやその他の哺乳類種向けのエピジェネティック時計の最近の開発によって例証されています。本稿では、複数の哺乳類種間で高度に保存されたDNA配列に隣接するCpGのメチル化プロファイルに基づく、イエネコ（*Felis catus*）のエピジェネティック時計について説明します。これらのCpGのメチル化レベルは、カスタム設計されたInfiniumアレイ（HorvathMammalMethylChip40）を使用して測定されました。これらから、ネコ用の3つのエピジェネティック時計を提示します。そのうちの1つはネコの血液サンプルのみに適用され、残りの2つの二重種（ヒト-ネコ）時計はネコとヒトの両方に適用されます。私たちは、これらのイエネコの時計が、チーター、トラ、ライオンにおいても年齢と高い相関を示すことを実証します。ネコのためのこれらのエピジェネティック時計は、ネコの健康状態のモニタリングや、抗老化介入の特定および検証に使用されるために、さらに開発される可能性を秘めていると期待されます。

## 導入 (Introduction)
イエネコの飼い主の多くは、この広く人気のあるペットの短い寿命を嘆いています。動物の年齢データベース（anAge）[1, 2]によると、ネコの最大（確認済み）寿命は30年ですが、ほとんどのネコは20歳になる前に病気で亡くなります[3]。年齢が動物の大部分の病気において最大の危険因子であることは間違いなく、ネコも例外ではありません。老化を遅らせるための介入が模索されています。理想的には、進化的にヒトに近く、サイズが似ており、遺伝的多様性が高く、ヒトと同じ環境を共有する種でテストを行うべきです。イヌがこれらの基準を満たしていることは認識されています[4–6]。しかし、ネコも飼い主であるヒトと似た環境や生活条件を共有しているにもかかわらず、これらの調査はネコにはまだ拡張されていません。老化に影響を与える環境因子や生活条件の特定、および潜在的な緩和策は、ネコを代理（proxy）として用いることで達成できます。しかし、そのような調査の前提条件となるのは、ネコとヒトの両方にとっての高精度な老化のバイオマーカーのセットです。さまざまな個々の組織や複数の組織に対するヒトのエピジェネティック時計に関する豊富な文献[7–10]がある一方で、ネコ用の既存のエピジェネティック時計については私たちが知る限り存在しません。

ヒトのエピジェネティック時計は、ヒトの抗老化臨床試験における生物学的年齢の測定[7, 11]を含む、多くの生物医学的応用をすでに見出しています。これが、マウスやイヌ[12–18]などの他の哺乳類における同様の時計の開発を促しました。本研究では、ネコのためのエピジェネティック時計を開発し評価することを目指しました。このようなバイオマーカーは、有望な抗老化介入をヒトからネコへ、あるいはその逆へ翻訳するために必要であり、また、現在定量的な尺度が利用できないネコの健康状態について情報を得るためにネコのエピジェネティックな老化速度を利用する可能性を提供するためにも必要です。具体的には、本稿ではネコの血液に対するDNAメチル化ベースの年齢バイオマーカー（エピジェネティック時計）を提示します。

細胞のDNAメチル化の度合いが年齢とともに変化することは、古くから知られていました[19–21]。これらの変化の意義と特異性は、ヒトゲノム上の特定のCpG位置のメチル化レベルの同時定量を可能にするアレイベースの技術が開発されるまでは、推測の域を出ませんでした。技術の進歩に伴い、複数のDNA座位における加齢に関連したメチル化の変化を組み合わせて、すべてのヒト組織に対する高精度な年齢推定器を開発する機会と洞察がもたらされました[7, 8, 10]。例えば、ヒトの全組織（pan-tissue）時計は、353個のCpGのメチル化レベルの加重平均を組み合わせて、DNAm ageまたはエピジェネティック年齢[22]と呼ばれる年齢推定値を算出します。そのような年齢推定器に期待される通り、そのエピジェネティック年齢の予測は暦年齢（chronological age）と密接に一致します。しかし、それ以上にはるかに重要なのは、エピジェネティック年齢と暦年齢の乖離（「エピジェネティック年齢の加速（epigenetic age acceleration）」と呼ばれる）が、さまざまな既知の危険因子を調整した後でも、複数の健康状態を予測するという発見です[23–28]。具体的には、エピジェネティック年齢の加速は、認知および身体機能[29]、アルツハイマー病[30]、百寿者（centenarian）のステータス[27, 31]、ダウン症候群[32]、プロジェリア（早老症）[33, 34]、HIV感染[35]、ハンチントン病[36]、肥満[37]、および閉経[38]などに関連していますが、これらに限定されません。エピジェネティック年齢はまた、年齢、性別、喫煙状況などの既知の危険因子を調整した後でも、死亡率を予測します[23–28]。総じて、エピジェネティック年齢が生物学的年齢の指標であるという証拠は説得力があります[39–41]。

私たちは以前、ヒトのDNAメチル化プロファイルのみで訓練されたヒトの全組織時計がチンパンジーに直接適用できることを示しましたが[22]、進化的なゲノム配列の分岐の結果として、他の動物に対する有用性は失われます。最近、他の研究者たちがマウス用のエピジェネティック時計を構築し、カロリー制限や成長ホルモン受容体ノックアウト[12–17]などのベンチマークとなる長寿介入を用いてそれらを成功裏に検証しました。暦年齢のためのマウスのエピジェネティック時計のほとんどは、マウスにおける死亡リスクの予測有用性に関してまだ評価されていません。しかし、マウス用のメチル化ベースの平均余命（life expectancy）予測器は開発されています[42]。

全体として、これらの独立した取り組みは、エピジェネティック時計の根底にある生物学的原理が哺乳綱内の異なる種のメンバー間で共有されていること、そしてエピジェネティック時計の開発を他の哺乳類種に拡張することが可能であり実現可能であることを示しています。私たちの現在の研究は、ネコとヒトの生涯全体にわたる暦年齢のDNAメチル化ベースの推定器（二重種時計）を開発することを主な目標として追求しました。ヒトとネコの二重種モデルが他の種にも適用されるかどうかを評価するために、他のネコ科動物（チーター、トラ、ライオン）および哺乳綱の非ネコ科動物（モルモット、ウサギ、フェレット、アルパカ）においてそれらを評価しました。最後に、私たちは年齢とともにメチル化を獲得/喪失するゲノム領域を特定するために、ネコにおける加齢に伴うメチル化レベルの変化を特徴付けます。

## 結果 (Results)
私たちは、さまざまな品種のネコから得られた、年齢が0.21歳から20.9歳にわたる $n=130$ の血液サンプルからDNAメチル化プロファイルを生成しました（Table 1 および 2）。教師なし階層的クラスタリング分析において、ネコの品種は明確なクラスターに対応していませんでした（Fig. 1のカラーバンド）。これは、哺乳類アレイ上のほとんどのCpGがネコの品種間で異ならないことを示唆しています。血液サンプルの大部分は避妊・去勢されたネコからのものでした：避妊済みのメス50匹、去勢済みのオス51匹、未避妊のメス9匹、未去勢のオス19匹です。それらのDNAメチル化プロファイルは性別によってクラスター化されました（Fig. 1）。ネコのサンプルのうち1つは、その性別がクラスタリングのパターンと一致しなかったため、分析から除外されました。

![Table 1](./age_cat/self_figure/table1.png)
**Table 1** 8種類の異なる非ヒト種の血液メチル化データの説明。

![Table 2](./age_cat/self_figure/table2.png)
**Table 2** ネコの時計の開発に使用されたネコの品種の説明。

![Fig. 1](./age_cat/self_figure/fig1.png)
**Fig. 1** ネコからの血液サンプルの教師なし階層的クラスタリング。

その後の性別に対するランダムフォレスト分析では、完璧な（out-of-bag, OOB）精度推定（誤分類ゼロ）が得られました。避妊・去勢のステータスは年齢と強く交絡していました：未避妊・未去勢の動物28匹中25匹が0.8歳未満でした。若いサンプルに分析を限定した場合、避妊・去勢ステータスのランダムフォレスト予測分析は高いOOBエラー率（60%以上のエラー率）をもたらしました。

私たちの二重種（dual-species）時計が他の種にどの程度一般化されるかを研究するために、非イエネコ種（チーター $n=14$、ライオン $n=5$、トラ $n=7$）およびより遠縁の哺乳類種（モルモット $n=2$、ウサギ $n=5$、フェレット $n=2$、アルパカ $n=5$）の血液DNAメチル化プロファイルも生成しました（Table 1）。予想されるように、これらのメチル化プロファイルは種によって明確にクラスター化されました（Supplementary Figure S1）。

### エピジェネティック時計 (Epigenetic clocks)
私たちは、対象となる「種」と「年齢の測定基準」という2つの特徴に関して異なる、ネコ用の3つのエピジェネティック時計を開発しました。基本となる「ネコの時計」は34個のCpGで構成されており、ネコの血液DNAメチル化プロファイルのみでトレーニングされました。一方、二重種（ヒト-ネコ）のエピジェネティック時計は、ネコとヒトの両方のDNAメチル化データを使用してトレーニングされました。その結果得られた2つのヒト-ネコ時計は、年齢の測定方法が異なります。一方は、563個のCpGのメチル化プロファイルに基づいて、ネコとヒトの暦年齢（chronological ages、単位：年）を推定します。もう一方は、540個のCpGのメチル化プロファイルを用いて、動物の暦年齢をその種の最大寿命で割った「相対年齢（relative age）」を推定し、0から1の間の値を出力します。この相対年齢比率は、ネコとヒトのような全く異なる寿命を持つ種の間で、暦年齢の直接比較では不可能な、整列された生物学的に意味のある比較を可能にするため、非常に有利です。

エピジェネティック時計の偏りのない推定値を得るために、トレーニングデータの交差検証（cross-validation）分析を実施しました。基本のネコの時計を開発するために用いられたトレーニングデータはネコの血液DNAメチル化プロファイルで構成されていましたが、ヒト-ネコの時計の両方についてはヒトとネコの両方のDNAメチル化プロファイルがトレーニングデータを構成しました。交差検証の研究により、年齢の相関 $R$（年齢推定値であるDNAm年齢と暦年齢との間のピアソン相関として定義）と、中央絶対誤差（median absolute error）の偏りのない推定値が報告されました。その名が示す通り、「ネコの血液時計」は血液の年齢推定において非常に高精度です（$R=0.97$、中央絶対誤差 0.83年、Fig. 2A）。「暦年齢のためのヒト-ネコ時計」は、両方の種のDNAメチル化プロファイルを一緒に分析した場合に非常に高精度であり（$R=0.98$、Fig. 2B）、ネコの血液サンプルのみに限定した場合でも驚くほど高精度を保ちます（$R=0.97$、Fig. 2C）。同様に、「相対年齢のためのヒト-ネコ時計」は、両方の種からのサンプルに分析を適用した場合（$R=0.98$、Fig. 2D）でも、ネコのサンプルのみに適用した場合（$R=0.97$、Fig. 2E）でも、分析対象に関わらず高い相関を示します。これは、相対年齢を用いることで、寿命が大きく異なる種の暦年齢を単一の公式で測定する際に生じる固有の「歪み（skewing）」を回避できることを実証しています。

交差検証分析によれば、両方のヒト-ネコ時計は、ヒトの血液および皮膚サンプルにおいても非常に精度の高い推定値をもたらします（$R \ge 0.96$、Supplementary Figure S2）。

![Fig. 2](./age_cat/self_figure/fig2.png)
**Fig. 2** イエネコとヒトのエピジェネティック時計の交差検証研究。

### 他のネコ科3種への適用 (Application to 3 other cat species)
イエネコの時計が他のネコ科動物に一般化できるかどうかを調べるために、これらの時計をチーター（*Acinonyx jubatus*）、ライオン（*Panthera leo nubica*）、およびトラ（*Panthera tigris*）の血液サンプルに適用しました。
3つのイエネコ時計はすべて、チーター（$r \ge 0.85$、Fig. 3A–C）、ライオン（$r \ge 0.98$、Fig. 3D–F）、トラ（$r > 0.97$、Fig. 3G–I）の血液サンプルにおいて、年齢とそのDNAメチル化年齢推定値の間に高い相関をもたらしました。高い相関係数は、これらのネコの時計が、これら非イエネコ種の血液サンプルを年齢に関して順位付け（rank-order）するために使用できることを示しています。しかしながら、イエネコの時計のキャリブレーションは不十分であり、これらの異なる種における高い中央絶対誤差が示すように、系統的なオフセットが存在します。中央絶対誤差に関していえば、イエネコ専用時計はヒト-ネコ時計を上回ります。例えばライオンの場合、純粋なネコの時計では MAE = 1.4年であるのに対し、暦年齢のヒト-ネコ時計では MAE = 11.6年でした（Fig. 3D, E）。同様の乖離はトラでも観察され、純粋なネコの時計では MAE = 3.0年、ヒト-ネコ時計では MAE = 8.9年でした（Fig. 3G, H）。

![Fig. 3](./age_cat/self_figure/fig3.png)
**Fig. 3** チーター、ライオン、およびトラにおける評価。

### 加齢に関連するCpG (Age-related CpGs)
HorvathMammalMethylChip40からの合計34,851個のプローブが、Felis_catus_9.0.100ゲノムアセンブリにおける5,379個の遺伝子に近接する遺伝子座にアラインメントされました。アレイ上のプローブの種間保存性が高いため、ネコのメチル化データからの発見は、おそらくヒトや他の哺乳類種に外挿できると考えられます。暦年齢のエピゲノム全体関連分析（Epigenome-wide association analysis）により、年齢がDNAメチル化の変化に非常に有意な影響を与えることが明らかになりました（Fig. 4A）。1,379個のCpGのメチル化レベルが年齢の関数として変化し、その有意性は $p < 10^{-8}$ でした。最大のメチル化変化を示したCpGおよび対応する近傍遺伝子は以下の通りです：SLC12A5プロモーター（相関検定Z統計量 $z=20$）、HECTD2エクソン（$z=-17$）、NEUROD1プロモーター内の8つのCpGにおける高メチル化（$z=8.3 \sim 16.7$）、FOXG1イントロン内の2つのCpGにおける高メチル化（$z=8.9 \sim 16.4$）、およびFOXG1エクソン内の5つのCpG（$z=8.5 \sim 11.1$、Fig. 4A）。加齢に関連するCpGは、遺伝子領域内だけでなく、転写開始点との相対位置で定義可能な遺伝子間領域にも分布していました（Fig. 4B）。プロモーターと5'UTRにおいて、CpGの76%が年齢とともにメチル化を増加させていました。

これらの領域は主にCpGアイランドで構成されており、これはCpGアイランドが他のCpGサイトと比較して年齢とのより高い正の相関を持つことを実証する私たちのその後の分析と一致しています（Fig. 4C）。

転写因子エンリッチメント分析は、SP1結合サイトにおける低メチル化とPAX4結合サイトにおける高メチル化が、ネコの血液において加齢に関連した変化を示すトップモチーフの中にあることを示唆しています（Fig. 4D）。

有意なCpGの遺伝子レベルのエンリッチメント分析により、転写因子活性の変化、発生、神経系の変化、および糖尿病の発症に関連する経路が強調されましたが、これらはすべてヒトや他の種における老化の生物学と重複しています（Fig. 4E）。以下で議論するように、いくつかの上流の制御因子（upstream regulators）も特定されました。

私たちはさらに、ネコにおけるDNAメチル化による老化の組織特異的なエピゲノム状態のエンリッチメントを調べました。クロマチン状態分析とヒストン3マークの両方において、高メチル化されたCpGおよび低メチル化されたCpGの双方に対して予測された上位の組織タイプは血液でした。これはネコのDNAが抽出されたまさにその組織であるため、理にかなっています（Supplementary Figure S3）。加齢に関連する低メチル化CpGは、主にアクティブな転写開始点（TSS）とエンハンサー領域の周辺に存在していました。これらのCpGには、アクティブな転写に関連するH3K4me1およびH3K4me3修飾もマークされていました。対照的に、加齢に関連する高メチル化は、主に二価/ポイズドTSS（bivalent/poised TSS）、二価TSS/エンハンサーの周辺、二価エンハンサー、および抑制されたポリコーム結合部位で発生します。高メチル化CpGのヒストンマークには、H3K27me3（※原論文ではH3K27me27と表記されていますがH3K27me3の誤植と推測されます）、H3K4me1、およびH3K9me3が含まれていました。これらは総じて、これらの部位からの遺伝子発現の抑制と一致しています。DNaseI高感受性マーク（DHS）は血液を私たちのターゲット組織タイプとして特定しませんでした。これは、ヌクレオソームが枯渇した（オープンクロマチン）部位における加齢に関連するDNAメチル化の変化が、おそらく組織特異的ではないことを示唆しています。

![Fig. 4](./age_cat/self_figure/fig4.png)
**Fig. 4** イエネコ（*Felis catus*）の血液における暦年齢のエピゲノム全体関連（EWAS）。

### ネコの時計の他の種への適用 (Applying the cat clocks to other species)
これら3つのネコの時計を開発した後、私たちはそれらを使用して、他の4つの哺乳類種（モルモット、ウサギ、フェレット、アルパカ）からの血液DNAメチル化プロファイルの年齢を推定しました（Fig. 5）。これらの時計がそれらの動物の年齢を正確に推定することは期待されていませんでした。むしろこれは、年齢とDNAm年齢との間の高い相関係数によって示されるように、これらのネコの時計が、非ネコ科種内の動物の年齢を「互いに相対的に」どの程度予測できるかを確認するために実施されました。当然のことながら、暦年齢で動作するネコの時計およびヒト-ネコ時計は、動物の暦年齢から大きく離れた推定値を記録しました。それにもかかわらず、これら2つの時計は、動物の年齢を互いに相対的に（同種内で）正しく予測しました。これは、2つ目の二重種時計である相対年齢のヒト-ネコ時計でも同様に観察されました。特にモルモットとフェレットについてはサンプルの不足が解釈にいくらかの注意を必要とすることは認められますが、総じてこれらの結果は、「ある哺乳類種のために開発されたエピジェネティック時計が、他の種にも限られた範囲で適用でき、DNAメチル化の変化と年齢の関連性を明らかにする」という事実と一致しています。

![Fig. 5](./age_cat/self_figure/fig5.png)
**Fig. 5** 非ネコ科種に適用されたネコのエピジェネティック時計。

## 議論 (Discussion)
私たちは以前、さまざまなバージョンのヒトIllumina DNAメチル化アレイから得られたDNAメチル化プロファイルから、いくつかのヒトのエピジェネティック時計を開発しました。これらのアレイはヒトゲノムに特異的であるため、種の壁を越えるための重要なステップは、多数の哺乳類種間で高度に保存された隣接DNA配列を持つ最大36,000個のCpGをプロファイリングする「哺乳類DNAメチル化アレイ」の使用でした。このアレイを使用して128の血液サンプルをプロファイリングしたことは、これまでで最も包括的なイエネコのエピジェネティック・データセットとなります。これらのデータにより、イエネコの全生涯（誕生から老齢まで）に適用可能な、高精度なDNAメチル化ベースの年齢推定器を構築することができました。哺乳綱全体で進化的に保存されたDNA配列内に埋め込まれたCpGを使用してネコの時計を導出することに成功したことは、老化の基盤となる生物学的メカニズムの保存性をさらに裏付けるものです。同種（モルモット、ウサギ、フェレット、アルパカ）の動物の年齢を互いに相対的に正しく予測するネコ時計の能力は、この考えをさらに支持しています。エピジェネティックな老化のメカニズムはまだ特定されておらず、詳細な記述もされていませんが、多くの哺乳類種、あるいはおそらくそれを超えた種におけるその存在は、古代からの起源を示しています。ネコの時計がネコの健康に貢献するという可能性は、ヒトのエピジェネティック年齢の加速が幅広い主要な形質、健康状態、および病理と関連しているという事実によって裏付けられます。年齢の加速がなぜこれらの特性に関連しているのかはまだ不明ですが、同様の研究をネコに拡張することで、ネコの生物学的フィットネスの代理（surrogate）または指標としての「エピジェネティック年齢加速」の開発が可能になるかもしれないことを示唆しています。

同様に重要なネコの時計の可能性は、老化研究にイエネコを含めることの実現可能性です。イエネコは飼い主であるヒトと同じ生活環境を共有していますが、寿命はかなり短いです。これにより、老化に影響を与える要因や老化の潜在的な緩和策についての調査だけでなく、それらが寿命に与える影響（ヒトでは容易に実施できない）についての調査も可能になります。しかし、加齢に関連する知見をネコからヒトへ正確に翻訳するには、年齢の等価性（age-equivalence）の正確で精密な尺度が不可欠です。「1歳のネコは15歳のヒトに相当し、2歳のネコは24歳のヒトに相当し、それ以降はネコの1年ごとに4年を加算する」という現在の経験則は、非常に大まかな近似に過ぎません。

私たちはこのニーズを2段階のプロセスを通じて満たしました。まず、ネコとヒトのDNAメチル化プロファイルを組み合わせて「二重種時計（ヒト-ネコ）」を生成しました。これは、ヒトの年齢推定と同様にネコの年齢推定（暦年単位）においても高精度です。これは、単一の数式に基づいて異なる種のエピジェネティック時計を構築することの実現可能性を示しています。この単一の数式が両方の種に等しく適用可能であるという事実は、エピジェネティックな老化メカニズムが高度に保存されていることを効果的に示しています。しかし、ネコとヒトのような全く異なる最大寿命を持つ2つの種を単一の代表的なグラフに組み込むことは、年齢範囲に沿ったデータポイントの極端な分布という避けられない課題を提起します。さらに、これはこれら2つの種間の年齢等価性の課題を解決するものではありません。私たちは、すべてのネコとヒトの年齢を、それぞれの種の最大記録年齢（種の寿命）、つまりネコの場合は30年、ヒトの場合は122年[1, 2]に対する比率として表現することで、これら2つの課題に同時に取り組みました。比率を生成する数学的操作は、時間の暦単位を排除し、生物の年齢をその種自身の最大年齢に対する比率で示す値を生み出します。これにより、生物学的年齢の意味のある現実的な種間比較が可能になります。例えば、非常に高齢である20歳のネコの生物学的フィットネスは、若い20歳のヒトのそれとは同等ではありません。しかし、相対エピジェネティック年齢が0.5のネコは、同様の相対エピジェネティック年齢を持つヒトとより比較可能です。総じて、異なる種のエピジェネティック年齢を測定するために単一の数式を使用できることと、時間の暦単位を「寿命の割合」に置き換えることは、種間研究と種間の利益を推進する2つの重要な革新です。イヌとヒトのメチロームの比較では、イヌの年をヒトの年に変換し、2つの種間の主要な生理学的マイルストーンのタイミングを一致させる非線形関係が明らかになりました[43]。相対年齢のための私たちの二重種時計は、異なる種間の非線形関係を仮定しません。

ネコの血液における加齢に関連したメチル化の変化の詳細な分析により、年齢とともにメチル化が増加したCpGは主にプロモーター、CpGアイランド、およびエクソン内に位置していることが明らかになりました。一方、年齢とともに脱メチル化されるCpGは、イントロン内に存在することが最も多いです。DNAメチル化の結果、特にCpGアイランドとプロモーター内での結果は、大部分が転写の抑制です。しかし、イントロンの脱メチル化の結果を一般化するのは容易ではありません。これらのメチル化の変化が、年齢の関数としてこれらのCpGに近接する（あるいはおそらく遠位の）遺伝子の発現をどのように調整するかについては多くの推測が可能です。正確な理解が不足しているとはいえ、これらのエピジェネティックな変化は、広く観察されている加齢に伴う遺伝子発現の変化と一致しており、おそらくそれを媒介していると考えられます。

転写因子エンリッチメント分析は、SP1結合サイトの低メチル化とPAX4結合サイトの高メチル化が、ネコの血液において加齢に伴う変化を示すトップモチーフの1つであることを示唆しています（Fig. 4D）。

原則として、これは年齢の増加に伴いSP1タンパク質がその結合部位のいくつかにアクセスしやすくなることを示します。しかし、SP1は細胞の成長、アポトーシス、免疫応答からクロマチンリモデリングに至るまで、多様な細胞プロセスに関与する多くの遺伝子の転写を活性化するため、この結果を予測するのは困難です。それでも、4つの転写因子（SMAD3、SP1、SP3、およびE2F1）の遺伝子ターゲットの集合的なエンリッチメントは、それらがテロメラーゼ調節に関与していることを示しています（エンリッチメント $p=3e^{-9}$）。さらに、SP1およびE2F1ターゲット遺伝子はマイトファジーにも関与しています（エンリッチメント $p=2e^{-4}$）。老化におけるテロメラーゼとマイトファジーの両方の関与は文献でよく証明されています[44]。一方、PAX4はその標的遺伝子が分化と発生に関与する転写因子であり、TFAP2も同様です。

ネコにおける加齢に伴う遺伝子発現の変化に関する実証データがない中で、私たちは加齢に関連するCpGの近傍にある遺伝子を特定し、続いてこれらの遺伝子に関連する細胞内経路、あるいは疾患/状態を突き止めました。当然のことながら、これらはすぐに老化の原因であると容易に理解できるような明確な結果をもたらしませんでした。実際、老化に関する私たちの理解は初期段階にあり、これらの加齢に伴う変化の原因と結果を分離することは困難な試みです。その代わり、これらの結果が提供するのは、加齢に伴ってなぜ、どのようにそれらの変化が起こるのかを確認するために、さらに調査しテストすべき「潜在的な経路への初期の垣間見」です。この点に関して、生物の発生および器官と組織機能の維持に関与する経路が、特定された上位の経路の大部分を構成していることは注目に値します。これは例えば、がん遺伝子、腫瘍抑制遺伝子、およびDNA修復タンパク質やチェックポイントタンパク質の発現の変化が頻繁に見られるがんとは対照的です。言い換えれば、加齢に伴う変化は、細胞の増殖や修復ではなく、細胞機能とアイデンティティの「発生と維持」に関与しているように見えます。これは、PAX4およびTFAP2転写因子のターゲットに対する加齢に伴うメチル化変化の高いスコアと一致しており、これらの標的遺伝子は分化と発生に関与しています。これはさらに、PRC2、Suz12、およびヒストンH3K27me3のターゲット座位が加齢に伴い高メチル化されるものとして特定された事実によって象徴されます。Suz12はPRC2の構成要素であり、ヒストンH3K27をメチル化し、これがクロマチンに結合して細胞のコミットメント、細胞の分化、および細胞のアイデンティティ維持に主に関与する遺伝子の転写を防ぎます。興味深いことに、イヌにおいて、Suz12およびヒストンH3K27me3のターゲットは加齢に伴って同様に修飾されます[18]。実際、このような加齢に関連するメチル化は、以前にヒトにおいてPRC2ターゲット部位のCpGで不釣り合いに発生することが特定されており[20]、老化における「発生プロセス」の重要性と、老化プロセスの種間保存性を補強しています。これは、eForgeバージョン2[45]で分析された加齢に関連するネコのCpGにおいて、二価クロマチンドメイン、PRC結合部位、およびH3K27me3の高メチル化が非常に強く特徴づけられたという事実によってさらに裏付けられています。加齢に関連するCpGの計算分析で高得点を得た転写因子、クロマチン状態、遺伝子、および経路の「種間の一致」は、多数のヒットの中から最も関連性の高いものを特定するための非常に効果的な方法です。この点に関して、TFAP2、ZFP161、およびE2F1/3は、そのDNA上の結合部位が、コウモリ（論文別送）と同様にネコにおいても加齢に伴いますますメチル化されるタンパク質です。進化的に離れたこれらの種がこのような類似性を示すという事実は、これらのタンパク質とその機能により大きな注意を払うことを促します。前述のように、TFAP2は細胞分化と器官発生に関与する標的遺伝子を持つ転写因子です。ZFP161タンパク質はGCリッチなDNA領域に結合し、DNA複製フォークの安定性を調節し、ゲノムの安定性を維持します[46]。別のゲノム安定化タンパク質である網膜芽細胞腫タンパク質（RB）が、これら2つの種において加齢に伴い結合部位がますますメチル化されるE2F転写因子への結合を通じてその効果を発揮することは興味深いです[47, 48]。ゲノムの不安定性は老化[50]だけでなく、がん[49]の「ホールマーク（特徴）」でもあるため、これは特に関連性があります。これら2つの生物学的状態の関係は古くから認識されており、これらの研究におけるそれらの共出現は、この関係を強固にし、解明が待たれる潜在的な共通メカニズムを示唆しています。さらに、テロメラーゼ発現とマイトファジーを調節する転写因子のターゲットに対する加齢に関連したメチル化変化の特定も、このつながりの可能性を物語っています。テロメラーゼ、マイトファジー、ゲノムの不安定性、およびエピジェネティクスの調節が、ネコの老化に関連していることは注目に値します。これらは、特定された老化の9つのホールマークのうちの4つだからです[44]。

この記事は主にイエネコに関心を持っています。他のネコ科種および非ネコ科種の研究はサンプル数が少ないことに苦しんでいることを認めます。相関係数の推定値が将来の研究のデザインに情報を提供する可能性があるため、私たちはこの資料を提示します。ネコのための私たちのエピジェネティック時計は、死亡率や疾患リスクなどの実際に臨床的に関連する結果に対してまだ検証されていません。これらの時計が生物学的年齢の適用可能な尺度と見なされる前に、この批判的評価を行う必要があります。

ネコにおける将来の介入研究は、コンパニオンであるイヌでの研究を補完するものと期待しています。2つの異なるコンパニオンペット種で有益な抗老化介入は、単一の種でのみ機能するものよりも有望であると言えます。エピジェネティック時計が開発され利用可能になる哺乳類の数が増えるにつれて、これまでネコや他の哺乳類で特定された加齢に関連する特徴（発生とゲノムの不安定性）が引き続き現れるかどうかを確認することは、非常に有益になります。これまでに浮かび上がってきた全体像は、私たちの生活環境を親密に共有するネコなどの哺乳類の老化の理解が、ヒトの老化に翻訳できるという考えを強固にしています。哺乳類メチル化アレイにおいて、二重種（ヒト-ネコ）時計は、この努力を大いに助ける革新です。

## 材料と方法 (Materials and methods)

### 研究サンプル (Study samples)

#### ネコ科およびその他の動物の血液サンプル (Feline and other animal blood samples)
王立獣医大学（RVC）のDNAアーカイブから、以前のルーチンの血液学的検査の残余であるネコのエチレンジアミン四酢酸（EDTA）血液サンプルを検索しました。ネコは、入手可能なサンプルに基づき、全範囲にわたる均一な分布、入手可能な品種、および避妊去勢ステータスを考慮して、可能な限り最も広い年齢範囲を代表するように選択されました。サンプルは獣医学的調査のために提示されたネコに由来するため、認定獣医臨床病理学者（BSz）によってレビューされた、入手可能な臨床検査データ（血液学、血清生化学、内分泌学）に異常がないか最小限であるネコが選択されました。DNAサンプルはさまざまな期間（0〜11年）$-80$°Cで凍結保存されました。モルモット、ウサギ、フェレット、およびアルパカのサンプルも、獣医療のために提示されたルーチン患者からの残余サンプルでした。サンプルの収集はRVCの臨床研究倫理審査委員会によって承認されました（URN: 2019 1947–2）。ネコの血液からのゲノムDNAは、Zymo DNA抽出キットを使用して製造元の指示に従って抽出されました。DNAは水で溶出され、提供された指示に従ってpicogreenキットで定量されました。

#### 非イエネコ種 (Non-domestic cat species)
チーター（学名 *Acinonyx jubatus*）、ライオン（*Panthera leo nubica*）、およびトラ（*Panthera tigris*）からの血液サンプルは、Busch GardensおよびWhite Oak Conservationに位置するこれらの動物園飼育動物からのルーチンの健康診断中に日和見的に（opportunistically）収集され保管されました。これらのサンプルはTable 1に記載されています。

#### ヒト組織サンプル (Human tissue samples)
ヒト-ネコ時計を構築するために、年齢が0歳から93歳にわたる個体からの $n=1211$ のヒト組織サンプル（脂肪、血液、骨髄、真皮、表皮、心臓、ケラチノサイト、線維芽細胞、腎臓、肝臓、肺、リンパ節、筋肉、下垂体、皮膚、脾臓）から以前に生成されたメチル化データを分析しました。組織サンプルは3つのソースから来ました。組織および臓器サンプルはNational NeuroAIDS Tissue Consortium[51]からです。血液サンプルはCape Town Adolescent Antiretroviral Cohort研究[52]からです。皮膚およびその他の初代細胞はKenneth Raj[53]によって提供されました。倫理承認は以下の通りです：IRB#15–001,454, IRB#16–000,471, IRB#18–000,315, IRB#16–002,028。

### DNAメチル化データ (DNA methylation data)
すべてのメチル化データは、カスタムInfiniumアレイ「HorvathMammalMethylChip40」[54]で生成されました。この哺乳類メチル化アレイは、哺乳類において高度に保存されたCpGの広範なカバー率（数千倍）を提供します。アレイ上の37,492個のCpGのうち、哺乳類種のシトシンDNAメチル化レベルを評価するために35,988個のプローブが選択されました[54]。各プローブの特定の種のサブセットは、チップのマニフェストファイルに提供されています。各プローブのベータ値を定義するためにSeSaMe正規化手法が使用されました[55]。

### 罰則付き回帰モデル (Penalized regression models)
時計のセットの詳細（CpG、ゲノム座標）とRソフトウェアコードはSupplement（補足資料）に提供されています。
罰則付き回帰モデル（Penalized regression models）はglmnet[56]を用いて作成されました。私たちは「エラスティックネット（elastic net）」回帰（alpha=0.5）によって生成されたモデルを調査しました。最適なペナルティパラメータはすべての場合において、トレーニングセットに対する10分割の内部交差検証（cv.glmnet）を使用することで自動的に決定されました。定義上、エラスティックネット回帰のアルファ値は0.5（リッジ回帰とラッソ回帰の中間点）に設定されており、モデルのパフォーマンスのために最適化されていません。
異なるDNAmベースの年齢推定器の精度の偏りのない（または少なくとも偏りの少ない）推定値に到達するために、交差検証スキームを実行しました。1つのタイプは、回帰から1つのサンプルを除外し（LOOCV）、そのサンプルの年齢を予測し、すべてのサンプルについて反復することから成りました。重要なステップは暦年齢（従属変数）の変換です。ネコの血液時計には変換は使用されませんでしたが、暦年齢の二重種時計には対数線形変換を使用しました（Supplement）。時計の基礎となる係数値とCpGは補足資料（Supplementary Material）で見つけることができます。

### 相対年齢の推定 (Relative age estimation)
寿命が大きく異なるネコとヒトの年齢推定に生物学的な意味を持たせるため、また、年齢範囲全体でネコとヒトからのデータポイントの分布が等しくないことによる避けられない歪みを克服するために、「相対年齢 = 年齢 / 最大寿命（Relative age = Age / maxLifespan）」という式を使用して相対年齢の推定が行われました。ここで、2つの種の最大寿命はanAgeデータベース[1]から選択されました。

### 年齢のエピゲノム全体関連研究 (Epigenome-wide association studies of age)
EWASは、「WGCNA」Rパッケージ[57]のR関数「standardScreeningNumericTrait」を使用して各組織で個別に実行されました。次に、Stoufferのメタ分析手法を使用して組織間で結果を結合しました。

### 謝辞・データ可用性等 (Funding / Data availability)
**Funding（資金提供）** 本研究はPaul G. Allen Frontiers Group (SH)、National Institute of Aging 1U19AG057758によって支援されました。追加のネコ科種はWhite Oak Conservationにより快く提供されました。
**Data availability（データ可用性）** データは、Mammalian Methylation Consortiumからのデータリリースの一環として公開される予定です。これらのCpGのゲノムアノテーションは、Githubの https://github.com/shorvath/MammalianMethylationConsortium で見つけることができます。

## 参考文献 (References)
[1] de Magalhaes JP, Costa J, Church GM. “An analysis of the relationship between metabolism, developmental schedules, and longevity using phylogenetic independent contrasts,” (英語). J Gerontol A Biol Sci Med Sci. 2007;62(2):149–60.
[2] J. P. de Magalhaes, J. Costa, and O. Toussaint, "HAGR: the human ageing genomic resources," Nucleic Acids Res, vol. 33, no. Database issue, pp. D537–43, Jan 1 2005, https://doi.org/10.1093/nar/gki017.
[3] D. G. O’Neill, D. B. Church, P. D. McGreevy, P. C. Thomson, and D. C. Brodbelt. Longevity and mortality of cats attending primary care veterinary practices in England. Journal of Feline Medicine and Surgery, vol. 17, no. 2, pp. 125–133, 2015, https://doi.org/10.1177/1098612X14536176.
[4] M. Kaeberlein, K. E. Creevy, and D. E. L. Promislow. The dog aging project: translational geroscience in companion animals. Mamm Genome, vol. 27, no. 7, pp. 279–288, 2016, https://doi.org/10.1007/s00335-016-9638-7.
[5] Gilmore KM, Greer KA. “Why is the dog an ideal model for aging research?,” (英語). Exp Gerontol. 2015;71:14–20. https://doi.org/10.1016/j.exger.2015.08.008.
[6] J. J. Hayward ら, "Complex disease and phenotype mapping in the domestic dog," Nature Communications, vol. 7, no. 1, p. 10460, 2016, https://doi.org/10.1038/ncomms10460.
[7] S. Horvath and K. Raj, "DNA methylation-based biomarkers and the epigenetic clock theory of ageing," (英語), Nat Rev Genet, Apr 11 2018, https://doi.org/10.1038/s41576-018-0004-3.
[8] Field AE, Robertson NA, Wang T, Havas A, Ideker T, Adams PD. “DNA methylation clocks in aging: categories, causes, and consequences,” (英語). Mol Cell. 2018;71(6):882–95. https://doi.org/10.1016/j.molcel.2018.08.008.
[9] K. Raj and S. Horvath. Current perspectives on the cellular and molecular features of epigenetic ageing. Exp Biol Med, p. 1535370220918329, 2020, https://doi.org/10.1177/1535370220918329.
[10] C. G. Bell ら DNA methylation aging clocks: challenges and recommendations. Genome Biology, vol. 20, no. 1, p. 249, 2019, https://doi.org/10.1186/s13059-019-1824-y.
[11] Fahy GM, ら Reversal of epigenetic aging and immunosenescent trends in humans. Aging Cell. 2019;18(6): e13028. https://doi.org/10.1111/acel.13028.
[12] D. A. Petkovich, D. I. Podolskiy, A. V. Lobanov, S. G. Lee, R. A. Miller, and V. N. Gladyshev, "Using DNA methylation profiling to evaluate biological age and longevity interventions," (英語), Cell Metab, vol. 25, no. 4, pp. 954–960 e6, Apr 4 2017, https://doi.org/10.1016/j.cmet.2017.03.016.
[13] J. J. Cole ら, "Diverse interventions that extend mouse lifespan suppress shared age-associated epigenetic changes at critical gene regulatory regions," (英語), Genome Biol, vol. 18, no. 1, p. 58, Mar 28 2017. https://doi.org/10.1186/s13059-017-1185-3.
[14] T. Wang ら, "Epigenetic aging signatures in mice livers are slowed by dwarfism, calorie restriction and rapamycin treatment," (英語), Genome Biol, vol. 18, no. 1, p. 57, Mar 28 2017, https://doi.org/10.1016/s13059-017-1186-2.
[15] T. M. Stubbs ら, "Multi-tissue DNA methylation age predictor in mouse," Genome Biol, vol. 18, no. 1, p. 68, Apr 11 2017, https://doi.org/10.1186/s13059-017-1203-5.
[16] Thompson MJ, ら “A multi-tissue full lifespan epigenetic clock for mice,” (英語). Aging (Albany NY). 2018;10(10):2832–54. https://doi.org/10.18632/aging.101590.
[17] M. V. Meer, D. I. Podolskiy, A. Tyshkovskiy, and V. N. Gladyshev. A whole lifespan mouse multi-tissue DNA methylation clock. eLife, vol. 7, p. e40675, 2018, https://doi.org/10.7554/eLife.40675.
[18] M. J. Thompson, B. vonHoldt, S. Horvath, and M. Pellegrini. An epigenetic aging clock for dogs and wolves. Aging (Albany NY), vol. 9, no. 3, pp. 1055–1068, 2017, https://doi.org/10.18632/aging.101211.
[19] V. K. Rakyan ら Human aging-associated DNA hypermethylation occurs preferentially at bivalent chromatin domains, (英語), Genome Res, vol. 20, no. 4, pp. 434–9, Apr 2010, https://doi.org/10.1101/gr.103101.109.
[20] Teschendorff AE, ら “Age-dependent DNA methylation of genes that are suppressed in stem cells is a hallmark of cancer,” (英語). Genome Res. 2010;20(4):440–6. https://doi.org/10.1101/gr.103606.109.
[21] J.-P. Issa Aging and epigenetic drift: a vicious cycle. J Clin Invest, vol. 124, no. 1, pp. 24–29, 2014
[22] Horvath S. “DNA methylation age of human tissues and cell types,” (英語). Genome Biol. 2013;14(10):R115. https://doi.org/10.1186/gb-2013-14-10-r115.
[23] R. Marioni ら DNA methylation age of blood predicts all-cause mortality in later life. Genome Biol., vol. 16, no. 1, p. 25, 2015. [オンライン]. 利用可能: http://genomebiology.com/2015/16/1/25.
[24] Christiansen L, ら “DNA methylation age is associated with mortality in a longitudinal Danish twin study,” (英語). Aging Cell. 2016;15(1):149–54. https://doi.org/10.1111/acel.12421.
[25] Perna L, Zhang Y, Mons U, Holleczek B, Saum KU, Brenner H. Epigenetic age acceleration predicts cancer, cardiovascular, and all-cause mortality in a German case cohort. Clin Epigenetics. 2016;8:64. https://doi.org/10.1186/s13148-016-0228-z.
[26] Chen BH, ら “DNA methylation-based measures of biological age: meta-analysis predicting time to death,” (英語). Aging (Albany NY). 2016;8(9):1844–65. https://doi.org/10.18632/aging.101020.
[27] Horvath S, ら “Decreased epigenetic age of PBMCs from Italian semi-supercentenarians and their offspring,” (英語). Aging (Albany NY). 2015;7(12):1159–70. https://doi.org/10.18632/aging.100861.
[28] Lu AT, ら “DNA methylation GrimAge strongly predicts lifespan and healthspan,” (英語). Aging (Albany NY). 2019;11(2):303–27. https://doi.org/10.18632/aging.101684.
[29] R. Marioni, S. Shah, A. F. McRae, S. J. Ritchie, and G. Muniz-Terrera. The epigenetic clock is correlated with physical and cognitive fitness in the Lothian Birth Cohort 1936. Int J Epidemiol, vol. 44, 2015, https://doi.org/10.1093/ije/dyu277
[30] Levine ME, Lu AT, Bennett DA, Horvath S. “Epigenetic age of the pre-frontal cortex is associated with neuritic plaques, amyloid load, and Alzheimer’s disease related cognitive functioning,” (英語). Aging (Albany NY). 2015;7(12):1198–211. https://doi.org/10.18632/aging.100864.
[31] Horvath S, ら “The cerebellum ages slowly according to the epigenetic clock,” (英語). Aging (Albany NY). 2015;7(5):294–306.
[32] S. Horvath ら Accelerated epigenetic aging in Down syndrome. Aging Cell, vol. 14, no. 1, 2015. https://doi.org/10.1111/acel.12325.
[33] S. Horvath, J. Oshima, G. Martin, K. Raj, and S. Matsuyama. Epigenetic age estimator for skin and blood applied to Hutchinson Gilford Progeria, 2018.
[34] Maierhofer A, Flunkert J, Oshima J, Martin GM, Haaf T, Horvath S. “Accelerated epigenetic aging in Werner syndrome,” (英語). Aging (Albany NY). 2017;9(4):1143–52. https://doi.org/10.18632/aging.101217.
[35] Horvath S, Levine AJ. “HIV-1 infection accelerates age according to the epigenetic clock,” (英語). J Infect Dis. 2015;212(10):1563–73. https://doi.org/10.1093/infdis/jiv277.
[36] Horvath S, ら “Huntington’s disease accelerates epigenetic aging of human brain and disrupts DNA methylation levels,” (英語). Aging (Albany NY). 2016;8(7):1485–512. https://doi.org/10.18632/aging.101005.
[37] Horvath S, ら Obesity accelerates epigenetic aging of human liver. Proc Natl Acad Sci U S A. 2014;111(43):15538–43. https://doi.org/10.1073/pnas.1412759111.
[38] Levine ME, ら “Menopause accelerates biological aging,” (英語). Proc Natl Acad Sci U S A. 2016;113(33):9327–32. https://doi.org/10.1073/pnas.1604558113.
[39] Jylhava J, Pedersen NL, Hagg S. Biological age predictors. EBioMedicine. 2017;21:29–36. https://doi.org/10.1016/j.ebiom.2017.03.046.
[40] X. Li ら Longitudinal trajectories, correlations and mortality associations of nine biological ages across 20-years follow-up, (英語), eLife, vol. 9, p. e51507, 2020, https://doi.org/10.7554/eLife.51507.
[41] Ferrucci L, ら Measuring biological aging in humans: A quest. Aging Cell. 2020;19(2): e13080. https://doi.org/10.1111/acel.13080.
[42] M. B. Schultz ら, "Age and life expectancy clocks based on machine learning analysis of mouse frailty," Nature Communications, vol. 11, no. 1, p. 4618, 2020. https://doi.org/10.1038/s41467-020-18446-0.
[43] T. Wang ら, Quantitative translation of dog-to-human aging by conserved remodeling of the DNA Methylome. Cell Systems, vol. 11, no. 2, pp. 176–185.e6, 2020, https://doi.org/10.1016/j.cels.2020.06.006.
[44] Lopez-Otin C, Blasco MA, Partridge L, Serrano M, Kroemer G. “The hallmarks of aging,” (英語). Cell. 2013;153(6):1194–217. https://doi.org/10.1016/j.cell.2013.05.039.
[45] Breeze CE, ら eFORGE v2.0: updated analysis of cell type-specific signal in epigenomic data. Bioinformatics. 2019;35(22):4767–9. https://doi.org/10.1093/bioinformatics/btz456.
[46] W. Kim ら ZFP161 regulates replication fork stability and maintenance of genomic stability by recruiting the ATR/ATRIP complex, (英語), Nat Commun, vol. 10, no. 1, p. 5304, 2019, https://doi.org/10.1038/s41467-019-13321-z.
[47] R. Vélez-Cruz and D. G. Johnson. The retinoblastoma (RB) tumor suppressor: pushing back against genome instability on multiple fronts," (英語), Int J Mol Sci, vol. 18, no. 8, 2017, https://doi.org/10.3390/ijms18081776.
[48] Lee M, Rivera-Rivera Y, Moreno CS, Saavedra HI. “The E2F activators control multiple mitotic regulators and maintain genomic integrity through Sgo1 and BubR1,” (英語). Oncotarget. 2017;8(44):77649–72. https://doi.org/10.18632/oncotarget.20765.
[49] Negrini S, Gorgoulis VG, Halazonetis TD. “Genomic instability–an evolving hallmark of cancer,” (英語). Nat Rev Mol Cell Biol. 2010;11(3):220–8. https://doi.org/10.1038/nrm2858.
[50] Vijg J, Suh Y. “Genome instability and aging,” (英語). Annu Rev Physiol. 2013;75:645–68. https://doi.org/10.1146/annurev-physiol-030212-183715.
[51] Morgello S, ら The National NeuroAIDS Tissue Consortium: a new paradigm in brain banking with an emphasis on infectious disease. Neuropathol Appl Neurobiol. 2001;27(4):326–35.
[52] Horvath S, ら “Perinatally acquired HIV infection accelerates epigenetic aging in South African adolescents,” (英語). AIDS (London, England). 2018;32(11):1465–74. https://doi.org/10.1097/QAD.0000000000001854.
[53] Kabacik S, Horvath S, Cohen H, Raj K. “Epigenetic ageing is distinct from senescence-mediated ageing and is not prevented by telomerase expression,” (英語). Aging (Albany NY). 2018;10(10):2800–15. https://doi.org/10.18632/aging.101588.
[54] A. Arneson ら A mammalian methylation array for profiling methylation levels at conserved sequences. bioRxiv, p. 2021.01.07.425637, 2021, https://doi.org/10.1101/2021.01.07.425637.
[55] Zhou W, Triche TJ Jr, Laird PW, Shen H. SeSAMe: reducing artifactual detection of DNA methylation by Infinium beadchips in genomic deletions. Nucleic Acids Res. 2018;46(20):e123–e123. https://doi.org/10.1093/nar/gky691.
[56] Friedman J, Hastie T, Tibshirani R. Regularization paths for generalized linear models via coordinate descent. J Stat Softw. 2010;33(1):1–22.
[57] P. Langfelder and S. Horvath. WGCNA: an R package for weighted correlation network analysis," BMC Bioinformatics, vol. 9, no. 1, p. 559, 2008. [オンライン]. 利用可能: http://www.biomedcentral.com/1471-2105/9/559.
[58] T. L. Bailey ら, "MEME Suite: tools for motif discovery and searching," Nucleic Acids Research, vol. 37, no. suppl_2, pp. W202-W208, 2009, https://doi.org/10.1093/nar/gkp335.
[59] C. Y. McLean ら GREAT improves functional interpretation of cis-regulatory regions," Nat Biotechnol, vol. 28, 2010, https://doi.org/10.1038/nbt.1630.
