"""Central configuration for eml-sr_model_fifth_AI (paper-faithful dataset)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

DATA_ROOT = ROOT.parent / "data" / "age_cheetah"
GEO_MATRIX = DATA_ROOT / "GSE310779_series_matrix.txt"
MCDB_BETA_CSV = DATA_ROOT / "cheetah_mamconsortium_betas.csv"
MCDB_META_CSV = DATA_ROOT / "mcdb_cheetah_blood_meta.csv"

ASM = 2.0
ASM_K = 0.2
ENET_L1_RATIO = 0.5

N_CPG_FOR_SR = 20
TOP_K_CANDIDATES = 10

MAX_COMPLEXITY = 10
BEAM_WIDTH = 500
COMPLEXITY_PENALTY = 0.1

PYSR_NITERATIONS = 40
PYSR_POPULATIONS = 15
PYSR_POPULATION_SIZE = 33

PREPROCESS_R = ROOT / "preprocess_clock.R"
RSCRIPT = r"C:\Program Files\R\R-4.4.2\bin\Rscript.exe"

CLOCK_SAMPLES_CSV = DATA_DIR / "clock_samples.csv"
BETA_COMBAT_CSV = DATA_DIR / "beta_combat.csv"
SELECTED_CPGS_CSV = DATA_DIR / "selected_cpgs.csv"
BASELINE_LOOCV_CSV = DATA_DIR / "baseline_loocv.csv"
BASELINE_SUMMARY_CSV = DATA_DIR / "baseline_summary.csv"
GLMNET_COEFS_FULL_CSV = DATA_DIR / "glmnet_coefs_full.csv"
HOLDOUT_BLOOD_CSV = DATA_DIR / "holdout_blood_samples.csv"
HOLDOUT_SKIN_CSV = DATA_DIR / "holdout_skin_samples.csv"
