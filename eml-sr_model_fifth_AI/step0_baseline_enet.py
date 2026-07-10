#!/usr/bin/env python3
"""Step 0: Elastic Net baseline metrics (MSE, R²) from R preprocess outputs."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import config
from metrics import dual_scale_metrics


def _write_linear_formula(cpgs: pd.DataFrame, out_path) -> str:
    """Build glmnet linear formula text from exported coefficients."""
    if config.GLMNET_COEFS_FULL_CSV.exists():
        full = pd.read_csv(config.GLMNET_COEFS_FULL_CSV)
        intercept = float(full.loc[full["term"] == "(Intercept)", "coef"].iloc[0])
        terms = full[(full["term"] != "(Intercept)") & (full["coef"].abs() > 1e-10)].copy()
        terms["abs_coef"] = terms["coef"].abs()
        terms = terms.sort_values("abs_coef", ascending=False)
    else:
        intercept = 0.0
        terms = cpgs.rename(columns={"CpG": "term", "Coef": "coef"})

    parts = [f"{intercept:.6f}"]
    for _, row in terms.iterrows():
        c = float(row["coef"])
        sign = "+" if c >= 0 else "-"
        parts.append(f" {sign} {abs(c):.6f}*{row['term']}")
    formula = "age_trans = " + "".join(parts)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Elastic Net (glmnet) linear model\n")
        f.write(f"lambda_min from preprocess\n")
        f.write("=" * 60 + "\n")
        f.write(formula + "\n")
        if config.GLMNET_COEFS_FULL_CSV.exists():
            f.write("\nNon-zero coefficients:\n")
            f.write(f"  (Intercept): {intercept:.8f}\n")
            for _, row in terms.iterrows():
                f.write(f"  {row['term']}: {row['coef']:.8f}\n")
    return formula


def main() -> None:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    loocv = pd.read_csv(config.BASELINE_LOOCV_CSV)
    summary = pd.read_csv(config.BASELINE_SUMMARY_CSV)
    cpgs = pd.read_csv(config.SELECTED_CPGS_CSV)

    y_trans = loocv["age_trans"].values.astype(float)
    pred_trans = loocv["pred_trans"].values.astype(float)
    ages = loocv["Age"].values.astype(float)

    m = dual_scale_metrics(y_trans, pred_trans, ages)

    summary_dict = dict(zip(summary["metric"], summary["value"]))
    formula = _write_linear_formula(
        cpgs, config.RESULTS_DIR / "step0_linear_formula.txt"
    )
    row = {
        "method": "elastic_net_glmnet",
        "n_features": int(summary_dict.get("n_cpgs_selected", len(cpgs))),
        "formula_or_model": formula[:500],
        "lambda_min": float(summary_dict.get("lambda_min", np.nan)),
        "n_samples": int(summary_dict.get("n_samples", len(loocv))),
        **{f"loocv_{k}": v for k, v in m.items()},
    }

    out_csv = config.RESULTS_DIR / "step0_baseline.csv"
    pd.DataFrame([row]).to_csv(out_csv, index=False)

    out_json = config.RESULTS_DIR / "step0_baseline.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(row, f, indent=2, ensure_ascii=False)

    print("Step 0 - Elastic Net LOOCV")
    print(f"  MSE (age_trans): {m['mse_trans']:.6f}")
    print(f"  R2  (age_trans): {m['r2_trans']:.4f}")
    print(f"  r   (age):       {m['r_age']:.4f}")
    print(f"  MAE (age, years): {m['mae_age']:.4f}")
    print(f"Saved {out_csv}")


if __name__ == "__main__":
    main()
