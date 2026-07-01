"""Central configuration for eml-sr_model_fourth_AI."""
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

# SR input: top |coef| CpGs from glmnet
N_CPG_FOR_SR = 20
TOP_K_CANDIDATES = 10

# eml-sr_model_first_AI search
MAX_COMPLEXITY = 10
BEAM_WIDTH = 500
COMPLEXITY_PENALTY = 0.1

# PySR
PYSR_NITERATIONS = 40
PYSR_POPULATIONS = 15
PYSR_POPULATION_SIZE = 33

# EQL neural SR
EQL_HIDDEN = 12
EQL_EPOCHS = 3000
EQL_LOOCV_EPOCHS = 200
EQL_LR = 0.01
EQL_L1 = 1e-4
EQL_WEIGHT_THRESHOLD = 0.05

# Sparse SIM
SIM_SPLINE_DEGREE = 3
SIM_SPLINE_N_KNOTS = 5

# R
PREPROCESS_R = ROOT / "preprocess_clock.R"
RSCRIPT = r"C:\Program Files\R\R-4.4.2\bin\Rscript.exe"

# Pipeline outputs (preprocess_clock.R)
CLOCK_SAMPLES_CSV = DATA_DIR / "clock_samples.csv"
BETA_COMBAT_CSV = DATA_DIR / "beta_combat.csv"
SELECTED_CPGS_CSV = DATA_DIR / "selected_cpgs.csv"
BASELINE_LOOCV_CSV = DATA_DIR / "baseline_loocv.csv"
BASELINE_SUMMARY_CSV = DATA_DIR / "baseline_summary.csv"
GLMNET_COEFS_FULL_CSV = DATA_DIR / "glmnet_coefs_full.csv"
SKIN_SAMPLES_CSV = DATA_DIR / "skin_samples.csv"
