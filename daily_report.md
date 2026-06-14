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
