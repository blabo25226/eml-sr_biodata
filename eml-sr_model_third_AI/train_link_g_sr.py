#!/usr/bin/env python3
"""
GLM link function g via symbolic regression.

Model: E(age_trans) = g^{-1}(eta),  eta = beta_0 + sum_j beta_j * CpG_j
Estimate g such that g(age_trans) ~= eta (link scale).
"""
from __future__ import annotations

import json
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNetCV

import config
from utils import asm_inv_transform, eval_formula, invert_link, pearson_r

warnings.filterwarnings("ignore")

try:
    import eml_sr_model_first_AI
except ImportError:
    sys.path.insert(0, str(config.ROOT.parent / "eml-sr_model_first_AI"))
    import eml_sr_model_first_AI


def load_xy():
    meta = pd.read_csv(config.CLOCK_SAMPLES_CSV, index_col=0)
    beta = pd.read_csv(config.BETA_COMBAT_CSV, index_col=0)
    cpgs = pd.read_csv(config.SELECTED_CPGS_CSV)
    top = cpgs.head(config.N_CPG_FOR_SR)["CpG"].tolist()
    X = beta.loc[meta.index, top].values.astype(float)
    age_trans = meta["age_trans"].values.astype(float)
    ages = meta["Age"].values.astype(float)
    gsm = meta.index.tolist()
    return gsm, X, age_trans, ages, top


def fit_eta(X: np.ndarray, age_trans: np.ndarray) -> tuple[np.ndarray, ElasticNetCV]:
    n = len(age_trans)
    cv = min(5, n - 1) if n > 5 else max(2, n - 1)
    enet = ElasticNetCV(l1_ratio=config.ENET_L1_RATIO, cv=cv, max_iter=10000, n_jobs=-1)
    enet.fit(X, age_trans)
    eta = enet.predict(X)
    return eta, enet


def link_mse(python_code: str, age_trans: np.ndarray, eta: np.ndarray) -> float:
    pred = eval_formula(python_code, {"v0": age_trans})
    return float(np.mean((pred - eta) ** 2))


def response_mse_invert(python_code: str, age_trans: np.ndarray, eta: np.ndarray) -> float:
    y_min, y_max = float(age_trans.min()) - 0.5, float(age_trans.max()) + 0.5
    recon = np.array([invert_link(python_code, e, y_min, y_max) for e in eta])
    return float(np.mean((recon - age_trans) ** 2))


def loocv_age_prediction(
    X: np.ndarray,
    age_trans: np.ndarray,
    ages: np.ndarray,
    link_py: str | None,
) -> tuple[np.ndarray, np.ndarray]:
    """LOOCV on chronological age. link_py=None -> identity link (age_trans_hat = eta)."""
    n = len(ages)
    pred_ages = np.zeros(n)
    y_min, y_max = float(age_trans.min()) - 0.5, float(age_trans.max()) + 0.5

    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        cv = min(5, n - 2) if n > 6 else max(2, n - 2)
        enet = ElasticNetCV(l1_ratio=config.ENET_L1_RATIO, cv=cv, max_iter=10000, n_jobs=-1)
        enet.fit(X[mask], age_trans[mask])
        eta_i = float(enet.predict(X[i : i + 1])[0])

        if link_py is None:
            at_hat = eta_i
        else:
            at_hat = invert_link(link_py, eta_i, y_min, y_max)

        pred_ages[i] = float(asm_inv_transform(np.array([at_hat]), config.ASM, config.ASM_K)[0])

    return pred_ages, ages


def main():
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    gsm, X, age_trans, ages, cpgs = load_xy()
    eta, enet = fit_eta(X, age_trans)

    pd.DataFrame(
        {"GSM": gsm, "Age": ages, "age_trans": age_trans, "eta": eta}
    ).to_csv(config.LINEAR_PREDICTOR_CSV, index=False)

    print(f"Link SR: {config.N_CPG_FOR_SR} CpGs, n={len(ages)}")
    print("Fitting link g(age_trans) ~= eta with eml-sr...")

    searcher = eml_sr_model_first_AI.Searcher(
        max_complexity=config.MAX_COMPLEXITY,
        beam_width=config.BEAM_WIDTH,
        complexity_penalty=config.COMPLEXITY_PENALTY,
    )
    inputs = [[float(v)] for v in age_trans]
    candidates = searcher.find_candidates(inputs, eta.tolist())

    cand_rows = []
    for cand in candidates:
        py = cand.to_python()
        try:
            lm = link_mse(py, age_trans, eta)
            rm = response_mse_invert(py, age_trans, eta)
        except Exception:
            continue
        cand_rows.append(
            {
                "formula": cand.formula,
                "latex": cand.to_latex(),
                "python": py,
                "complexity": cand.complexity,
                "link_mse": lm,
                "response_mse": rm,
                "link_r": pearson_r(eval_formula(py, {"v0": age_trans}), eta),
            }
        )
    finite = [r for r in cand_rows if np.isfinite(r["link_mse"])]
    finite.sort(key=lambda r: r["link_mse"])
    cand_rows = finite

    identity_link_mse = float(np.mean((age_trans - eta) ** 2))
    identity_link_r = pearson_r(age_trans, eta)

    best = cand_rows[0] if cand_rows else None
    best_py = best["python"] if best else None

    print("LOOCV (eta refit per fold; g fixed from full-data SR)...")
    pred_id, true_ages = loocv_age_prediction(X, age_trans, ages, link_py=None)
    pred_sr, _ = loocv_age_prediction(X, age_trans, ages, link_py=best_py)

    r_id = pearson_r(true_ages, pred_id)
    r_sr = pearson_r(true_ages, pred_sr)
    mae_id = float(np.median(np.abs(true_ages - pred_id)))
    mae_sr = float(np.median(np.abs(true_ages - pred_sr)))

    loocv_df = pd.DataFrame(
        {
            "GSM": gsm,
            "Age": ages,
            "pred_age_identity": pred_id,
            "pred_age_sr_link": pred_sr,
        }
    )
    loocv_df.to_csv(config.RESULTS_DIR / "link_g_loocv.csv", index=False)

    summary = pd.DataFrame(
        [
            {"model": "identity_link_15cpg", "loocv_r": r_id, "loocv_mae": mae_id},
            {"model": "sr_link_15cpg", "loocv_r": r_sr, "loocv_mae": mae_sr},
            {"model": "glmnet_42cpg_baseline_sec3", "loocv_r": 0.758, "loocv_mae": 1.88},
        ]
    )
    summary.to_csv(config.RESULTS_DIR / "link_g_summary.csv", index=False)

    out_txt = config.RESULTS_DIR / "link_g_sr_results.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("GLM link g: g(age_trans) ~= eta  (E(age_trans) = g^{-1}(eta))\n")
        f.write(f"CpGs for eta: top {config.N_CPG_FOR_SR} by |glmnet coef|\n")
        f.write(f"Identity link (train): MSE={identity_link_mse:.6f}, r={identity_link_r:.4f}\n")
        f.write("LOOCV: eta refit each fold; g fixed from full-data SR (see report)\n")
        f.write("=" * 60 + "\n")
        for i, row in enumerate(cand_rows[:10]):
            f.write(f"Rank {i+1}: link_MSE={row['link_mse']:.6f}, response_MSE={row['response_mse']:.6f}\n")
            f.write(f"  link_r={row['link_r']:.4f}, complexity={row['complexity']}\n")
            f.write(f"  {row['formula']}\n  LaTeX: {row['latex']}\n\n")
        f.write("\nLOOCV chronological age (15 CpG, ASM inverse):\n")
        f.write(f"  Identity link: r={r_id:.4f}, MAE={mae_id:.4f}\n")
        f.write(f"  SR link:       r={r_sr:.4f}, MAE={mae_sr:.4f}\n")
        f.write("  (§3 baseline glmnet 42 CpG: r=0.758, MAE=1.88)\n")

    with open(config.RESULTS_DIR / "link_g_sr_results.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "candidates": cand_rows[:10],
                "identity_link_mse": identity_link_mse,
                "loocv": {"identity": {"r": r_id, "mae": mae_id}, "sr_link": {"r": r_sr, "mae": mae_sr}},
            },
            f,
            indent=2,
        )

    print(f"Best link MSE: {best['link_mse']:.6f}" if best else "No candidate")
    print(f"LOOCV identity r={r_id:.4f}, SR link r={r_sr:.4f}")
    print(f"Saved {out_txt}")


if __name__ == "__main__":
    main()
