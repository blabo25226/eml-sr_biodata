# Daily Report

## 2026/06/12
### 過去の作業内容（git commit履歴より抽出）
* `first commit`: リポジトリの初期化と基本構成の作成。
* `sort filse and make report`: ファイル構成の整理および初期レポート群の作成。
* `make AGENTS.md and sort out`: プロジェクトのルールやAIの指示をまとめた `AGENTS.md` の作成と全体の整理。
* `write reports`: MEbフォルダ内の各種検証スクリプト（`toy`, `nanda`, `lacroix` 等）に関する数学的な仕組みと出力データの詳細な解説レポートの作成。
* `main report copy`: EML論文の本編に関するまとめである `self_MEb_main_report.md` などの作成・コピー。

## 2026/06/14

### 私（ユーザー）の作業
* プロジェクト内に新しいフォルダ（`age_cat`, `age_cheetah`, `age_human`）および関連ファイルを追加（git commit: `add age paper folders`）。
* `source.md` に新しい論文（ネコ、チーター、ヒトの加齢に関するエピジェネティック・クロック論文）のリンクを追記。
* `AGENTS.md` に新たな運用ルール（4. 作業に関する規定：`daily_report.md`, `self_xxx_overview_report.md` の作成など）を追加。
* AIエージェントに対し、追加されたディレクトリやファイルの確認、および `AGENTS.md` の `# Directory Structure & Context` セクションの更新を指示。
* eml-srを実行するためのソースコード群を含むGithubフォルダ（`eml-sr/`）をプロジェクト内に追加。

### AI（エージェント）の作業
* `source.md` および各新規フォルダ内のファイル（READMEやコードなど）を読み込み、内容を把握。
* 指示に基づき、`AGENTS.md` の `# Directory Structure & Context` を編集し、新規フォルダ（`age_cat`, `age_cheetah`, `age_human`）と追加された論文リンクの説明を反映。
* ルールに従い、各新規フォルダ内に概要資料を作成：
    * `age_cat/self_age_cat_overview_report.md`
    * `age_cheetah/self_age_cheetah_overview_report.md`
    * `age_human/self_age_human_overview_report.md`
* 上記概要資料について、既存の `self_MEb_overview_report.md` のフォーマット（論文の概要、フォルダの概要、略語・用語一覧）を踏襲して記述。
* `eml-sr` フォルダの追加に伴い、`eml-sr/README.md` を読み込み、同様に概要資料（`eml-sr/self_eml-sr_overview_report.md`）を作成。
* `daily_report.md`（本ファイル）に本日の作業内容を記録。

## 2026/06/15

### 私（ユーザー）の作業
* `AGENTS.md` のルールを更新し、論文翻訳やソース参照に関する規定を追加・修正。
* ネコのエピジェネティック時計論文（`age_cat`）の翻訳構成の提案を承諾し、画像配置場所（`./age_cat/self_figure`）を指定して和訳の開始を指示。
* 第2回の和訳に際し、配置した図表についての情報を `daily_report.md` にメモするよう指示。

### AI（エージェント）の作業
* 更新された `AGENTS.md` を確認し、新しいルールを把握。
* `age_cat_paper.pdf` の和訳に着手し、第1回として「概要（Abstract）」と「導入（Introduction）」の翻訳を作成（`age_cat/self_age_cat_translate.md`）。
* 続いて第2回として「結果（Results）前半」の和訳を追加し、指定の通り図表へのリンクを配置。
* 第3回として「結果（Results）後半」と対応する図表を追記。
* 第4回として「議論（Discussion）」および「材料と方法（Materials and methods）」の翻訳を追記し、論文本文の和訳をすべて完了。
* `AGENTS.md` に追加されたルールに従い、`age_cat_paper.pdf` の「参考文献（References）」のフォーマットを整えつつ和訳して追記。
* 同様に、既存の `MEb/self_MEb_translate.md` についても `AGENTS.md` の新ルール（参考文献の和訳追加）に準拠させるため、「参考文献 (References)」を追記。
* `daily_report.md` を更新し、以下の通り第2回で配置した図表の情報をメモ。

#### [age_cat] 第2回和訳での図表配置メモ
| 図表名 | 論文上の位置 | マークダウンでの行数 | 仮設定したファイル名 |
| :--- | :--- | :--- | :--- |
| Table 1 | Page 3 | 20行目 | `./age_cat/self_figure/table1.png` |
| Table 2 | Page 3 | 23行目 | `./age_cat/self_figure/table2.png` |
| Fig. 1 | Page 4 | 26行目 | `./age_cat/self_figure/fig1.png` |
| Fig. 2 | Page 5 | 40行目 | `./age_cat/self_figure/fig2.png` |
| Fig. 3 | Page 6 | 47行目 | `./age_cat/self_figure/fig3.png` |
| Fig. 4 | Page 9 | 62行目 | `./age_cat/self_figure/fig4.png` |
| Fig. 5 | Page 11 | 68行目 | `./age_cat/self_figure/fig5.png` |
