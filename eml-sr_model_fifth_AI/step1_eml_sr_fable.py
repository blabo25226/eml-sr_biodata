#!/usr/bin/env python3
"""Step 1: eml-sr_fable symbolic regression (CpG -> age_trans) on paper-faithful data."""
from __future__ import annotations

import json
import sys
import warnings

import numpy as np
import pandas as pd

import config
from metrics import dual_scale_metrics
from utils import load_sr_data, predict_fable

warnings.filterwarnings("ignore")

try:
    import eml_sr_fable
except ImportError:
    sys.path.insert(0, str(config.ROOT.parent / "eml-sr_fable"))
    import eml_sr_fable


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if not np.all(np.isfinite(y_pred)):
        return float("inf")
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def pick_conservative(candidates, X: np.ndarray, y: np.ndarray, band_ratio: float):
    """Within 5% RMSE band, pick minimum complexity (manual §3.3)."""
    scored = []
    for cand in candidates:
        preds = predict_fable(cand, X)
        scored.append((cand, rmse(y, preds)))
    finite = [(c, r) for c, r in scored if np.isfinite(r)]
    if not finite:
        raise RuntimeError("No finite eml-sr_fable candidates")
    best_rmse = min(r for _, r in finite)
    band = [(c, r) for c, r in finite if r <= best_rmse * band_ratio]
    return min(band, key=lambda cr: (cr[0].complexity, cr[1]))[0]


def loocv_structure_fixed(cand, X: np.ndarray, n: int) -> np.ndarray:
    """Structure-fixed LOOCV: same formula for all points (fourth_AI convention)."""
    preds = np.zeros(n)
    for i in range(n):
        p = predict_fable(cand, X[i : i + 1])
        preds[i] = float(p[0]) if len(p) else np.nan
    return preds


def make_searcher() -> eml_sr_fable.Searcher:
    return eml_sr_fable.Searcher(
        max_complexity=config.FABLE_MAX_COMPLEXITY,
        complexity_penalty=config.FABLE_COMPLEXITY_PENALTY,
        beam_width=config.FABLE_BEAM_WIDTH,
        time_budget_s=config.FABLE_TIME_BUDGET_S,
        subsample_size=config.FABLE_SUBSAMPLE_SIZE,
        early_exit_threshold=config.FABLE_EARLY_EXIT_THRESHOLD,
        refinement_top_k=config.FABLE_REFINEMENT_TOP_K,
        snap_constants=True,
        powerlaw_stage=True,
        ratio_search=True,
        rational_stage=True,
        affine_scaling=True,
        max_boost_terms=config.FABLE_MAX_BOOST_TERMS,
        verbose=True,
    )


def candidate_record(cand, X: np.ndarray, y: np.ndarray, ages: np.ndarray, n: int) -> dict:
    y_pred = predict_fable(cand, X)
    if not np.all(np.isfinite(y_pred)):
        raise ValueError("non-finite train predictions")

    train_m = dual_scale_metrics(y, y_pred, ages)
    loocv_pred = loocv_structure_fixed(cand, X, n)
    loocv_m = dual_scale_metrics(y, loocv_pred, ages)

    return {
        "formula": cand.formula,
        "latex": cand.to_latex(),
        "python": cand.to_python(),
        "complexity": cand.complexity,
        "cand_error": cand.error,
        "train_rmse_trans": rmse(y, y_pred),
        **{f"train_{k}": v for k, v in train_m.items()},
        **{f"loocv_{k}": v for k, v in loocv_m.items()},
    }


def main() -> None:
    if not config.CLOCK_SAMPLES_CSV.exists():
        raise FileNotFoundError(
            f"Missing {config.CLOCK_SAMPLES_CSV}. Run: Rscript replicate_paper_enet.R"
        )

    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta, cpgs, X, y, ages = load_sr_data()
    n = len(y)

    print(f"Step 1 - eml-sr_fable: {X.shape[1]} CpGs, {n} samples")
    print(
        f"  settings: beam={config.FABLE_BEAM_WIDTH}, "
        f"max_cplx={config.FABLE_MAX_COMPLEXITY}, "
        f"time_budget={config.FABLE_TIME_BUDGET_S}s, "
        f"early_exit={config.FABLE_EARLY_EXIT_THRESHOLD}"
    )

    searcher = make_searcher()
    candidates = searcher.find_candidates(X.tolist(), y.tolist())
    print(f"  Pareto candidates: {len(candidates)}")

    conservative = pick_conservative(
        candidates, X, y, band_ratio=config.FABLE_CONSERVATIVE_BAND
    )

    results = []
    for cand in candidates:
        try:
            results.append(candidate_record(cand, X, y, ages, n))
        except (ValueError, TypeError):
            continue

    results.sort(key=lambda r: r["train_rmse_trans"])
    top = results[: config.TOP_K_CANDIDATES]

    cons_row = candidate_record(conservative, X, y, ages, n)
    cons_row["selection"] = "conservative_band"

    out_txt = config.RESULTS_DIR / "step1_eml_sr_fable_results.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("eml-sr_fable — eml-sr_model_fifth_AI (paper-faithful n=52)\n")
        f.write(f"CpGs: top {config.N_CPG_FOR_SR} by |glmnet coef|\n")
        f.write(
            f"beam_width={config.FABLE_BEAM_WIDTH}, "
            f"max_complexity={config.FABLE_MAX_COMPLEXITY}, "
            f"time_budget_s={config.FABLE_TIME_BUDGET_S}\n"
        )
        f.write(f"early_exit_threshold={config.FABLE_EARLY_EXIT_THRESHOLD}\n")
        f.write(f"Top {config.TOP_K_CANDIDATES} by train RMSE (structure-fixed LOOCV)\n")
        f.write("=" * 60 + "\n")
        f.write("Conservative pick (5% RMSE band, min complexity):\n")
        f.write(f"  Complexity: {cons_row['complexity']}\n")
        f.write(f"  Train RMSE: {cons_row['train_rmse_trans']:.6f}  R2: {cons_row['train_r2_trans']:.4f}\n")
        f.write(f"  LOOCV r (age): {cons_row['loocv_r_age']:.4f}  MAE: {cons_row['loocv_mae_age']:.4f}\n")
        f.write(f"  Formula: {cons_row['formula']}\n")
        f.write(f"  LaTeX: {cons_row['latex']}\n\n")

        for i, res in enumerate(top):
            f.write(f"Rank {i + 1}\n")
            f.write(f"  Complexity: {res['complexity']}\n")
            f.write(f"  Train RMSE: {res['train_rmse_trans']:.6f}  R2: {res['train_r2_trans']:.4f}\n")
            f.write(f"  LOOCV MSE: {res['loocv_mse_trans']:.6f}  R2: {res['loocv_r2_trans']:.4f}\n")
            f.write(f"  LOOCV r (age): {res['loocv_r_age']:.4f}  MAE: {res['loocv_mae_age']:.4f}\n")
            f.write(f"  Formula: {res['formula']}\n")
            f.write(f"  LaTeX: {res['latex']}\n\n")

        f.write("CpG mapping (v_i):\n")
        for i, cpg in enumerate(cpgs):
            f.write(f"  v{i}: {cpg}\n")

    out_csv = config.RESULTS_DIR / "step1_eml_sr_fable_candidates.csv"
    pd.DataFrame(top).to_csv(out_csv, index=False)
    pd.DataFrame([cons_row]).to_csv(
        config.RESULTS_DIR / "step1_eml_sr_fable_conservative.csv", index=False
    )

    with open(config.RESULTS_DIR / "step1_eml_sr_fable_candidates.json", "w", encoding="utf-8") as f:
        json.dump({"top": top, "conservative": cons_row}, f, indent=2, ensure_ascii=False)

    if top:
        print(f"  Best train RMSE: {top[0]['train_rmse_trans']:.6f}")
        print(f"  Best LOOCV r (age): {top[0]['loocv_r_age']:.4f}")
    print(f"  Conservative LOOCV r (age): {cons_row['loocv_r_age']:.4f}")
    print(f"Saved {out_txt}")


if __name__ == "__main__":
    main()
