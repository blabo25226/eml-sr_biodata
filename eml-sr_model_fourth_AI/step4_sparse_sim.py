#!/usr/bin/env python3
"""Step 4: Sparse Simple Index Model — g(beta' x) with spline link."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNetCV, LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler

import config
from metrics import dual_scale_metrics
from utils import load_sr_data


def fit_sim(X: np.ndarray, y: np.ndarray):
    """Fit sparse index + spline link on full data."""
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    enet = ElasticNetCV(l1_ratio=[0.1, 0.5, 0.9], cv=min(5, len(y)), max_iter=5000)
    enet.fit(Xs, y)
    eta = enet.predict(Xs)

    spline = Pipeline([
        ("spline", SplineTransformer(
            n_knots=config.SIM_SPLINE_N_KNOTS,
            degree=config.SIM_SPLINE_DEGREE,
            include_bias=False,
        )),
        ("lin", LinearRegression()),
    ])
    spline.fit(eta.reshape(-1, 1), y)

    return scaler, enet, spline


def predict_sim(scaler, enet, spline, X: np.ndarray) -> np.ndarray:
    Xs = scaler.transform(X)
    eta = enet.predict(Xs)
    return spline.predict(eta.reshape(-1, 1))


def export_g_details(spline, eta: np.ndarray) -> tuple[str, pd.DataFrame]:
    """Export spline link g(eta) coefficients and human-readable description."""
    lin = spline.named_steps["lin"]
    st = spline.named_steps["spline"]
    n_basis = lin.coef_.shape[0]
    coefs = lin.coef_.ravel()
    intercept = float(np.atleast_1d(lin.intercept_)[0])

    rows = [{"basis": i, "coef": float(coefs[i])} for i in range(n_basis)]
    g_df = pd.DataFrame(rows)
    g_df.loc[len(g_df)] = {"basis": "intercept", "coef": intercept}

    knots = getattr(st, "knots_", None)
    if knots is not None:
        g_df.loc[len(g_df)] = {"basis": "knots_eta", "coef": np.nan}
        for i, k in enumerate(np.asarray(knots).ravel()):
            g_df.loc[len(g_df)] = {"basis": f"knot_{i}", "coef": float(k)}

    eta_min, eta_max = float(eta.min()), float(eta.max())
    g_desc = (
        f"g(eta) = {intercept:.6f} + sum_j w_j * B_j(eta)  "
        f"(degree={config.SIM_SPLINE_DEGREE}, n_knots={config.SIM_SPLINE_N_KNOTS}, "
        f"eta in [{eta_min:.4f}, {eta_max:.4f}])"
    )
    return g_desc, g_df


def describe_index(cpgs: list[str], enet) -> str:
    coefs = enet.coef_
    nz_idx = np.where(np.abs(coefs) > 1e-8)[0]
    terms = [f"{coefs[j]:.4f}*{cpgs[j]}" for j in nz_idx]
    beta_str = " + ".join(terms) if terms else "0"
    return "eta = " + beta_str


def describe_model(cpgs: list[str], scaler, enet, spline, eta: np.ndarray) -> str:
    index = describe_index(cpgs, enet)
    g_desc, _ = export_g_details(spline, eta)
    return f"age_trans = g(eta), {index}; {g_desc}"


def loocv_sim(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """LOOCV: refit scaler/enet/spline on n-1 samples per fold (model class fixed)."""
    n = len(y)
    preds = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        scaler, enet, spline = fit_sim(X[mask], y[mask])
        preds[i] = float(predict_sim(scaler, enet, spline, X[i : i + 1])[0])
    return preds


def main() -> None:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta, cpgs, X, y, ages = load_sr_data()

    print(f"Step 4 - Sparse SIM: {X.shape[1]} CpGs, {len(y)} samples")

    scaler, enet, spline = fit_sim(X, y)
    Xs = scaler.transform(X)
    eta = enet.predict(Xs)
    y_pred = predict_sim(scaler, enet, spline, X)
    train_m = dual_scale_metrics(y, y_pred, ages)

    loocv_pred = loocv_sim(X, y)
    loocv_m = dual_scale_metrics(y, loocv_pred, ages)

    g_desc, g_df = export_g_details(spline, eta)
    model_desc = describe_model(cpgs, scaler, enet, spline, eta)
    nz = int(np.sum(np.abs(enet.coef_) > 1e-8))

    row = {
        "method": "sparse_sim",
        "rank": 1,
        "formula_or_model": model_desc,
        "n_nonzero_beta": nz,
        **{f"train_{k}": v for k, v in train_m.items()},
        **{f"loocv_{k}": v for k, v in loocv_m.items()},
    }

    coef_df = pd.DataFrame({
        "CpG": cpgs,
        "beta_scaled": enet.coef_,
        "intercept": [enet.intercept_] * len(cpgs),
    })
    coef_df = coef_df[np.abs(coef_df["beta_scaled"]) > 1e-8]

    out_csv = config.RESULTS_DIR / "step4_sim_summary.csv"
    pd.DataFrame([row]).to_csv(out_csv, index=False)
    coef_df.to_csv(config.RESULTS_DIR / "step4_sim_coefficients.csv", index=False)
    g_df.to_csv(config.RESULTS_DIR / "step4_sim_g_coefficients.csv", index=False)

    scaler_df = pd.DataFrame({
        "CpG": cpgs,
        "scale_mean": scaler.mean_,
        "scale_std": scaler.scale_,
    })
    scaler_df.to_csv(config.RESULTS_DIR / "step4_sim_scaler.csv", index=False)

    with open(config.RESULTS_DIR / "step4_sim_summary.json", "w", encoding="utf-8") as f:
        json.dump(row, f, indent=2, ensure_ascii=False)

    out_txt = config.RESULTS_DIR / "step4_sim_results.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("Sparse Simple Index Model\n")
        f.write(f"Model: {model_desc}\n")
        f.write(f"\nIndex eta (standardized CpGs, ElasticNetCV):\n")
        f.write(f"  intercept_enet: {enet.intercept_:.8f}\n")
        for i, cpg in enumerate(cpgs):
            if abs(enet.coef_[i]) > 1e-8:
                f.write(f"  {cpg}: {enet.coef_[i]:.8f} (on standardized scale)\n")
        f.write(f"\nLink function g(eta):\n  {g_desc}\n")
        f.write("  B-spline basis coefficients (see step4_sim_g_coefficients.csv):\n")
        for _, row in g_df.iterrows():
            if str(row["basis"]).startswith("knot"):
                f.write(f"    {row['basis']}: {row['coef']}\n")
            elif row["basis"] not in ("intercept", "knots_eta"):
                f.write(f"    B_{row['basis']}: {row['coef']:.8f}\n")
        f.write(f"    intercept: {g_df[g_df['basis'] == 'intercept']['coef'].iloc[0]:.8f}\n")
        f.write(f"Non-zero beta: {nz}\n")
        f.write(f"Train  MSE: {train_m['mse_trans']:.6f}  R²: {train_m['r2_trans']:.4f}\n")
        f.write(f"LOOCV  MSE: {loocv_m['mse_trans']:.6f}  R²: {loocv_m['r2_trans']:.4f}\n")
        f.write(f"LOOCV  r (age): {loocv_m['r_age']:.4f}  MAE: {loocv_m['mae_age']:.4f}\n")

    print(f"  Non-zero beta: {nz}")
    print(f"  LOOCV r (age): {loocv_m['r_age']:.4f}")
    print(f"Saved {out_csv}")


if __name__ == "__main__":
    main()
