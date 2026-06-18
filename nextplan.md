# 1.
eml-sr_model_first_AIでeml-srのファインマンデータセットでシンボリック回帰のテストをする。
# 2.
上記で問題を見つけて、分析アルゴリズムの改善を図る。
# 3.
eml-sr_model_first_AI_2として、
LOSS＝RMSE
を
LOSS＝MSE + elastic net
とする。
そして1.のようにテストをする。
# 4.
上記二つのeml-sr_model_first_AIでさらにage_cheetahの方程式を求める。
目的変数は対数変換したageにする。
elastic net法の利点をシンボリック回帰に組み込みたい。