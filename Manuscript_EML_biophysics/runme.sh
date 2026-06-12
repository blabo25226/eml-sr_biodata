# Fig 1
python lacroix_grammar_search_ode.py \
  --input LaCroix-elife-66869-fig2-data.csv \
  --out-prefix lacroix_grammar_ode \
  --search-mode exhaustive \
  --max-depth 2 \
  --max-nodes 5 \
  --plot-format pdf

# Fig 2
python eml_grammar_search.py \
   --input Nanda-Fig2d.csv \
   --out-prefix nanda_grammar_all4 \
   --search-mode exhaustive \
   --max-depth 3 \
   --max-nodes 5 \
   --plot-format pdf

# Fig 3
python hill_grammar_search.py \
  --input Nanda-Fig2d.csv \
  --out-prefix nanda_hill_grammar_all4 \
  --search-mode exhaustive \
  --max-depth 3 \
  --max-nodes 5 \
  --plot-format pdf

# Fig 4
python toy_coarse_graining_benchmark.py \
  --out-prefix toy_eml_coarse \
  --Kmax 10 \
  --noise-sd 0.015 \
  --seed 1 \
  --plot-format pdf


