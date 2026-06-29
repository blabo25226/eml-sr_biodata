"""Central configuration for eml-sr_model_third_AI (edit here to tune runs)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

GEO_MATRIX = ROOT.parent / "age_cheetah" / "GSE310779_series_matrix.txt"

# ASM age transform (CheetahClock_age_sex.Rmd)
ASM = 2.0
ASM_K = 0.2

# Elastic Net (glmnet alpha = 0.5 in Rmd)
ENET_L1_RATIO = 0.5

# eml-sr_model_first_AI search
MAX_COMPLEXITY = 10
BEAM_WIDTH = 500
COMPLEXITY_PENALTY = 0.1
N_CPG_FOR_SR = 15  # top |coef| CpGs from glmnet (range 10–20)

# R script path
PREPROCESS_R = ROOT / "preprocess_clock.R"
RSCRIPT = r"C:\Program Files\R\R-4.4.2\bin\Rscript.exe"

# Pipeline outputs (produced by preprocess_clock.R)
CLOCK_SAMPLES_CSV = DATA_DIR / "clock_samples.csv"
BETA_COMBAT_CSV = DATA_DIR / "beta_combat.csv"
SELECTED_CPGS_CSV = DATA_DIR / "selected_cpgs.csv"
BASELINE_LOOCV_CSV = DATA_DIR / "baseline_loocv.csv"
SKIN_SAMPLES_CSV = DATA_DIR / "skin_samples.csv"
