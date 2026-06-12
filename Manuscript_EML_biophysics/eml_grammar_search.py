#!/usr/bin/env python3
"""
eml_grammar_search.py

Restricted symbolic-regression search for EML-generated response models.

This upgrades eml_beam_search.py by adding branching expressions. It supports:

    E ::= R | G(E) | E + E

where

    R(t;k) = 1 - exp(-k t)
    G_{a,b,c}(x) = eml(a ln(c+x), exp(bx)) - c^a
                 = (c+x)^a - b x - c^a

A fitted model is

    y(t) = y0 + B E(R(t;k)).

This is deliberately not a search over the full formal universality of EML.
The goal is a controlled grammar with explicit penalties, held-out validation,
and interpretable expanded equations.

Example:
python eml_grammar_search.py \
  --input Nanda-Fig2d.csv \
  --out-prefix nanda_grammar \
  --blocks "RhoA perturbation; Rac1 response" \
  --search-mode exhaustive \
  --max-depth 3 \
  --max-nodes 5 \
  --plot-format png
"""

from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import least_squares


@dataclass
class BlockData:
    name: str
    time: np.ndarray
    mean: np.ndarray
    sem: np.ndarray
    n: np.ndarray


@dataclass(frozen=True)
class Expr:
    kind: str
    child: Optional["Expr"] = None
    left: Optional["Expr"] = None
    right: Optional["Expr"] = None

    @staticmethod
    def R() -> "Expr":
        return Expr("R")

    @staticmethod
    def G(x: "Expr") -> "Expr":
        return Expr("G", child=x)

    @staticmethod
    def Add(a: "Expr", b: "Expr") -> "Expr":
        # Canonicalize commutative addition.
        return Expr("Add", left=a, right=b) if a.canonical() <= b.canonical() else Expr("Add", left=b, right=a)

    def depth(self) -> int:
        if self.kind == "R":
            return 0
        if self.kind == "G":
            return 1 + self.child.depth()
        if self.kind == "Add":
            return max(self.left.depth(), self.right.depth())
        raise ValueError(self.kind)

    def nodes(self) -> int:
        if self.kind == "R":
            return 1
        if self.kind == "G":
            return 1 + self.child.nodes()
        if self.kind == "Add":
            return 1 + self.left.nodes() + self.right.nodes()
        raise ValueError(self.kind)

    def gates(self) -> int:
        if self.kind == "R":
            return 0
        if self.kind == "G":
            return 1 + self.child.gates()
        if self.kind == "Add":
            return self.left.gates() + self.right.gates()
        raise ValueError(self.kind)

    def canonical(self) -> str:
        if self.kind == "R":
            return "R"
        if self.kind == "G":
            return f"G({self.child.canonical()})"
        if self.kind == "Add":
            return f"({self.left.canonical()}+{self.right.canonical()})"
        raise ValueError(self.kind)

    def evaluate(self, R: np.ndarray, pars: np.ndarray) -> np.ndarray:
        # pars are consumed in prefix order.
        if self.kind == "R":
            return R
        if self.kind == "G":
            a, b, c = pars[:3]
            child_pars = pars[3:3 + 3 * self.child.gates()]
            return gate(self.child.evaluate(R, child_pars), a, b, c)
        if self.kind == "Add":
            nleft = 3 * self.left.gates()
            return self.left.evaluate(R, pars[:nleft]) + self.right.evaluate(R, pars[nleft:])
        raise ValueError(self.kind)


@dataclass
class FitResult:
    block: str
    model: str
    expr: str
    depth: int
    nodes: int
    gates: int
    params: np.ndarray
    param_names: list[str]
    prediction: np.ndarray
    train_chi2: float
    valid_chi2: float
    all_chi2: float
    train_wmse: float
    valid_wmse: float
    aic_train: float
    bic_train: float
    score: float
    n_parameters: int
    n_train: int


def parse_nanda_csv(path: Path, ignore_negative_times: bool = True) -> list[BlockData]:
    df = pd.read_csv(path, header=None)
    starts = [c for c, v in enumerate(df.iloc[0]) if isinstance(v, str) and "perturbation;" in v]
    if not starts:
        raise ValueError("No perturbation blocks found.")
    blocks = []
    for i, c0 in enumerate(starts):
        c1 = starts[i + 1] if i + 1 < len(starts) else df.shape[1]
        name = str(df.iat[0, c0]).strip()
        time = pd.to_numeric(df.iloc[3:, c0], errors="coerce")
        vals = df.iloc[3:, c0 + 1:c1].apply(pd.to_numeric, errors="coerce")
        vals = vals.loc[:, vals.notna().sum(axis=0) >= 10]
        n = vals.notna().sum(axis=1)
        mean = vals.mean(axis=1, skipna=True)
        sem = vals.std(axis=1, skipna=True) / np.sqrt(n)
        out = pd.DataFrame({"time": time, "mean": mean, "sem": sem, "n": n}).dropna(subset=["time", "mean"])
        if ignore_negative_times:
            out = out[out["time"] >= 0]
        blocks.append(BlockData(name, out["time"].to_numpy(float), out["mean"].to_numpy(float),
                                out["sem"].to_numpy(float), out["n"].to_numpy(float)))
    return blocks


def weights(sem: np.ndarray, floor_fraction: float = 0.25) -> np.ndarray:
    pos = sem[np.isfinite(sem) & (sem > 0)]
    return np.ones_like(sem) if len(pos) == 0 else np.maximum(sem, np.median(pos) * floor_fraction)


def split_points(n: int, mode: str) -> tuple[np.ndarray, np.ndarray]:
    idx = np.arange(n)
    if mode == "late":
        train = idx < int(0.75 * n)
        valid = ~train
    else:
        valid = idx % 4 == 1
        train = ~valid
        train[0] = True
        valid[0] = False
    return train, valid


def R_of_t(t: np.ndarray, k: float) -> np.ndarray:
    return 1.0 - np.exp(-k * t)


def gate(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    xp = np.maximum(c + x, 1e-9)
    return xp**a - b * x - c**a


def generate_expressions(max_depth: int, max_nodes: int) -> list[Expr]:
    exprs = {"R": Expr.R()}
    changed = True
    while changed:
        changed = False
        cur = list(exprs.values())
        for e in cur:
            g = Expr.G(e)
            if g.depth() <= max_depth and g.nodes() <= max_nodes and g.canonical() not in exprs:
                exprs[g.canonical()] = g
                changed = True
        cur = list(exprs.values())
        for i, a in enumerate(cur):
            for b in cur[i:]:
                s = Expr.Add(a, b)
                if s.depth() <= max_depth and s.nodes() <= max_nodes and s.canonical() not in exprs:
                    exprs[s.canonical()] = s
                    changed = True
    return sorted(exprs.values(), key=lambda e: (e.depth(), e.nodes(), e.canonical()))


def predict_expr(expr: Expr, p: np.ndarray, t: np.ndarray) -> np.ndarray:
    y0, B, k = p[:3]
    return y0 + B * expr.evaluate(R_of_t(t, k), p[3:])


def predict_linear(p: np.ndarray, t: np.ndarray) -> np.ndarray:
    y0, B, k = p
    return y0 + B * R_of_t(t, k)


def predict_hill(p: np.ndarray, t: np.ndarray) -> np.ndarray:
    y0, B, K, h, k = p
    R = R_of_t(t, k)
    return y0 + B * R**h / (K**h + R**h + 1e-12)


def predict_double_hill(p: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Two additive Hill terms sharing a common rate constant k.
    Params: y0, k, B1, K1, h1, B2, K2, h2  (8 parameters).
    """
    y0, k, B1, K1, h1, B2, K2, h2 = p
    R = R_of_t(t, k)
    return (y0
            + B1 * R**h1 / (K1**h1 + R**h1 + 1e-12)
            + B2 * R**h2 / (K2**h2 + R**h2 + 1e-12))


def fit_model(block: BlockData, model: str, expr_label: str, depth: int, nodes: int, gates: int,
              predict: Callable[[np.ndarray, np.ndarray], np.ndarray],
              starts: list[np.ndarray], lo: np.ndarray, hi: np.ndarray,
              train: np.ndarray, valid: np.ndarray, depth_penalty: float,
              node_penalty: float, max_nfev: int) -> FitResult:
    t, y, w = block.time, block.mean, weights(block.sem)
    best = None
    for x0 in starts:
        x0 = np.minimum(np.maximum(np.asarray(x0, float), lo + 1e-10), hi - 1e-10)
        def res(p):
            return (predict(p, t)[train] - y[train]) / w[train]
        try:
            fit = least_squares(res, x0, bounds=(lo, hi), max_nfev=max_nfev,
                                ftol=1e-9, xtol=1e-9, gtol=1e-9)
        except Exception:
            continue
        chi = float(np.sum(res(fit.x)**2))
        if best is None or chi < best[0]:
            best = (chi, fit)
    if best is None:
        raise RuntimeError(f"Fit failed: {block.name} / {expr_label}")
    train_chi2, fit = best
    pred = predict(fit.x, t)
    all_res = (pred - y) / w
    valid_chi2 = float(np.sum(all_res[valid]**2))
    all_chi2 = float(np.sum(all_res**2))
    ntr, nva, kpar = int(np.sum(train)), int(np.sum(valid)), len(fit.x)
    train_wmse = train_chi2 / ntr
    valid_wmse = valid_chi2 / nva
    aic = float(ntr * np.log(train_chi2 / ntr) + 2 * kpar)
    bic = float(ntr * np.log(train_chi2 / ntr) + kpar * np.log(ntr))
    score = float(valid_wmse + depth_penalty * depth + node_penalty * nodes)
    names = ["y0", "B", "k"]
    if model == "hill":
        names = ["y0", "B", "K", "h", "k"]
    elif model == "double_hill":
        names = ["y0", "k", "B1", "K1", "h1", "B2", "K2", "h2"]
    elif model.startswith("EML"):
        for j in range(gates):
            names += [f"a{j+1}", f"b{j+1}", f"c{j+1}"]
    return FitResult(block.name, model, expr_label, depth, nodes, gates, fit.x, names, pred,
                     train_chi2, valid_chi2, all_chi2, train_wmse, valid_wmse,
                     aic, bic, score, kpar, ntr)


def expr_starts_bounds(block: BlockData, expr: Expr) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    y0 = float(block.mean[0])
    amp = max(1.0, float(np.max(block.mean) - np.min(block.mean)))
    g = expr.gates()
    lo = [-300.0, -1e6, 1e-4]
    hi = [300.0, 1e6, 100.0]
    for _ in range(g):
        lo += [0.01, 1e-6, 0.0]
        hi += [1000.0, 500.0, 10.0]
    starts = []
    # Primary starts: two amplitude signs with default gate params.
    for B in [amp, -amp]:
        p = [y0, B, 0.8]
        for j in range(g):
            c0 = 1e-6 if j == g - 1 else 0.1
            p += [0.55, 1.0 if j == g - 1 else 0.5, c0]
        starts.append(np.asarray(p, float))
    # Additional starts: diverse k and gate shapes for better coverage.
    for B in [amp, -amp]:
        for k0 in [0.15, 0.5]:
            p = [y0, B, k0]
            for _ in range(g):
                p += [1.5, 1.0, 0.3]
            starts.append(np.asarray(p, float))
        p = [y0, B, 0.3]
        for _ in range(g):
            p += [2.0, 0.5, 0.5]
        starts.append(np.asarray(p, float))
    return starts, np.asarray(lo, float), np.asarray(hi, float)


def fit_expr(block, expr, train, valid, depth_penalty, node_penalty, max_nfev):
    starts, lo, hi = expr_starts_bounds(block, expr)
    return fit_model(block, "EML_expr", expr.canonical(), expr.depth(), expr.nodes(), expr.gates(),
                     lambda p, t: predict_expr(expr, p, t), starts, lo, hi,
                     train, valid, depth_penalty, node_penalty, max_nfev)


def fit_baselines(block, train, valid, depth_penalty, node_penalty, max_nfev):
    y0 = float(block.mean[0])
    amp = max(1.0, float(np.max(block.mean) - np.min(block.mean)))
    fits = [
        fit_model(block, "linear_R", "R", 0, 1, 0, predict_linear,
                  [np.array([y0, amp, 0.5]), np.array([y0, -amp, 0.5])],
                  np.array([-300.0, -1e6, 1e-4]), np.array([300.0, 1e6, 100.0]),
                  train, valid, depth_penalty, node_penalty, max_nfev),
        fit_model(block, "hill", "R^h/(K^h+R^h)", 0, 1, 0, predict_hill,
                  [np.array([y0, amp, 0.5, 2.0, 0.8]), np.array([y0, -amp, 0.5, 2.0, 0.8])],
                  np.array([-300.0, -1e6, 1e-4, 0.03, 1e-4]),
                  np.array([300.0, 1e6, 100.0, 30.0, 100.0]),
                  train, valid, depth_penalty, node_penalty, max_nfev),
        fit_model(block, "double_hill", "(H(R)+H(R))", 1, 3, 0, predict_double_hill,
                  [np.array([y0, 0.5, amp/2, 0.5, 2.0, amp/2, 2.0, 2.0]),
                   np.array([y0, 0.5, -amp/2, 0.5, 2.0, -amp/2, 2.0, 2.0]),
                   np.array([y0, 0.5,  amp,   0.5, 2.0, -amp/2, 2.0, 2.0]),
                   np.array([y0, 0.5, -amp,   0.5, 2.0,  amp/2, 2.0, 2.0])],
                  np.array([-300.0, 1e-4, -1e6, 1e-4, 0.03, -1e6, 1e-4, 0.03]),
                  np.array([ 300.0, 100.0, 1e6, 100.0, 30.0,  1e6, 100.0, 30.0]),
                  train, valid, depth_penalty, node_penalty, max_nfev),
    ]
    return fits


def search_block(block, exprs, mode, beam_width, split, depth_penalty, node_penalty, max_nfev):
    train, valid = split_points(len(block.time), split)
    fits = fit_baselines(block, train, valid, depth_penalty, node_penalty, max_nfev)
    if mode == "exhaustive":
        selected_exprs = exprs
    else:
        # Practical approximation: enumerate all allowed expressions, then keep only the
        # smallest set by depth/nodes before fitting. This is a deterministic beam-like
        # pruning that avoids fitting huge trees early.
        selected_exprs = sorted(exprs, key=lambda e: (e.depth(), e.nodes(), e.canonical()))[:beam_width * (max(e.depth() for e in exprs) + 1)]
    print(f"  fitting {len(selected_exprs)} EML expressions")
    for e in selected_exprs:
        fits.append(fit_expr(block, e, train, valid, depth_penalty, node_penalty, max_nfev))
    return fits


def fits_df(fits):
    rows = []
    for f in fits:
        rows.append({
            "block": f.block, "model": f.model, "expr": f.expr,
            "depth": f.depth, "nodes": f.nodes, "gates": f.gates,
            "n_parameters": f.n_parameters, "N_T": f.n_train,
            "parameters": "; ".join(f"{n}={v:.8g}" for n, v in zip(f.param_names, f.params)),
            "train_chi2": f.train_chi2, "valid_chi2": f.valid_chi2, "all_chi2": f.all_chi2,
            "train_wmse": f.train_wmse, "valid_wmse": f.valid_wmse,
            "AIC_train": f.aic_train, "BIC_train": f.bic_train, "search_score": f.score,
        })
    df = pd.DataFrame(rows)
    df["DeltaScore_from_best"] = df.groupby("block")["search_score"].transform(lambda x: x - x.min())
    df["DeltaAIC_from_best"] = df.groupby("block")["AIC_train"].transform(lambda x: x - x.min())
    df["DeltaBIC_from_best"] = df.groupby("block")["BIC_train"].transform(lambda x: x - x.min())
    return df.sort_values(["block", "search_score"])


def save_predictions(blocks, fits, out):
    bdict = {b.name: b for b in blocks}
    rows = []
    for f in fits:
        b = bdict[f.block]
        for t, mean, sem, n, pred in zip(b.time, b.mean, b.sem, b.n, f.prediction):
            rows.append({"block": f.block, "model": f.model, "expr": f.expr, "depth": f.depth,
                         "nodes": f.nodes, "gates": f.gates, "time_min": t,
                         "mean": mean, "sem": sem, "n": n, "prediction": pred})
    pd.DataFrame(rows).to_csv(out, index=False)


def plot_best(blocks, fits, expr_lookup, out, svg_out):
    df = fits_df(fits)
    # Show the best EML expression per block; double_hill/hill are comparators only.
    eml_df = df[df["model"] == "EML_expr"]
    best = eml_df.groupby("block").first().reset_index()
    fit_lookup = {(f.block, f.model, f.expr): f for f in fits}
    block_lookup = {b.name: b for b in blocks}

    _FS     = 9     # axis labels / tick labels (~10 pt PRE body at 7-inch figure width)
    _FS_LEG = 7.5   # legend entries
    _FS_PNL = 11    # panel labels, slightly larger than body text
    _LW_REF = 0.6   # y = 0 reference line width

    n = len(best)
    ncols = 1 if n == 1 else (2 if n <= 4 else 3)
    nrows = int(np.ceil(n / ncols))
    panel_labels = [f'({chr(ord("a") + i)})' for i in range(n)]
    # Single-column width for one panel; double-column for multi-panel layouts.
    fig_w = 3.37 if ncols == 1 else 7.0
    # Multi-row double-column (n=3,4): 2.8 in/row → 5.6 in total for 2×2 layout.
    fig_h = nrows * (3.0 if ncols == 1 else (2.8 if nrows > 1 else 3.2))

    with plt.rc_context({'text.usetex': True, 'font.family': 'serif',
                         'font.size': _FS, 'axes.labelsize': _FS,
                         'xtick.labelsize': _FS, 'ytick.labelsize': _FS}):
        fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h))
        axes = np.asarray(axes).reshape(-1)
        for ax, (_, row), lbl in zip(axes, best.iterrows(), panel_labels):
            b = block_lookup[row["block"]]
            fbest = fit_lookup[(row["block"], row["model"], row["expr"])]
            # Collect all y values for ylim (use every point for range, not just plotted ones).
            all_plotted_y = list(b.mean - b.sem) + list(b.mean + b.sem)
            tf = np.linspace(float(np.min(b.time)), float(np.max(b.time)), 500)
            to_plot = [fbest]
            for f in fits:
                if f.block == b.name and (f.model == "hill" or f.expr == "G(R)"):
                    to_plot.append(f)
            seen = set()
            for f in to_plot:
                key = (f.model, f.expr)
                if key in seen:
                    continue
                seen.add(key)
                if f.model == "linear_R":
                    pred = predict_linear(f.params, tf)
                elif f.model == "hill":
                    pred = predict_hill(f.params, tf)
                elif f.model == "EML_expr":
                    pred = predict_expr(expr_lookup[f.expr], f.params, tf)
                else:
                    continue
                label = (f'Best: {f.expr}' if f is fbest
                         else (f.expr if f.model == 'EML_expr'
                               else f.model.replace('_', ' ').title()))
                # zorder=3 keeps fit curves on top of the data markers (zorder=2).
                ax.plot(tf, pred, linewidth=2.0, label=label, zorder=3)
                all_plotted_y.extend(pred[np.isfinite(pred)])
            # Data drawn after range collection but before legend; zorder=2 keeps it
            # below the fit curves yet above the y=0 reference (zorder=0).
            # Every second point reduces visual clutter without losing information.
            ax.errorbar(b.time[::2], b.mean[::2], yerr=b.sem[::2],
                        fmt='o', markersize=2.0, capsize=1.2,
                        label=r'Mean $\pm$ SEM', zorder=2)
            ax.axhline(0, color='k', linewidth=_LW_REF, zorder=0)
            # Set ylim from data + prediction range, rounded to a clean step.
            arr = np.asarray(all_plotted_y)
            arr = arr[np.isfinite(arr)]
            if len(arr):
                pad  = 0.10 * (arr.max() - arr.min())
                rng  = (arr.max() - arr.min()) * 1.2
                step = next((s for s in [1, 2, 5, 10, 20, 50, 100] if rng / s <= 8), 100)
                ylo  = np.floor((arr.min() - pad) / step) * step
                yhi  = np.ceil( (arr.max() + pad) / step) * step
                ax.set_ylim(ylo, yhi)
            ax.set_title(b.name.replace('; ', ';\n'), fontsize=_FS)
            ax.set_xlabel('Time (min)')
            ax.set_ylabel(r'\% Change')
            # Single-panel: place legend below the x-axis to avoid covering the data.
            # Multi-panel: let matplotlib choose the best interior location.
            if n == 1:
                ax.legend(frameon=False, fontsize=_FS_LEG,
                          loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2)
            else:
                ax.legend(frameon=False, fontsize=_FS_LEG, ncol=2, loc='upper right')
            # Panel label outside the plot area, top-left corner (multi-panel only).
            if n > 1:
                ax.text(0.0, 1.04, lbl, transform=ax.transAxes,
                        fontsize=_FS_PNL, va='bottom', ha='left', clip_on=False)
        for ax in axes[n:]:
            ax.axis('off')
        fig.tight_layout(pad=0.8)
        fig.savefig(out,     bbox_inches='tight')
        fig.savefig(svg_out, bbox_inches='tight')
    plt.close(fig)


def write_aic_bic_table(all_fits, out_path):
    """Write a focused AIC/BIC comparison CSV for reporting in the manuscript.

    Rows included per block:
      - Hill baseline (H(R))
      - Double-Hill baseline ((H(R)+H(R)))
      - G(R)  — depth-1 EML gate
      - Best EML expression (lowest search_score per block)
      Columns: block, model, expr, depth, n_parameters, N_T,
               valid_wmse, train_chi2, AIC_train, BIC_train,
               DeltaAIC_from_best, DeltaBIC_from_best
    """
    df = fits_df(all_fits)
    # Expressions always included regardless of rank
    anchor_exprs = {"R^h/(K^h+R^h)", "(H(R)+H(R))", "G(R)"}
    # Best EML expression per block (lowest search score among EML_expr)
    best_eml_idx = (df[df["model"] == "EML_expr"]
                    .groupby("block")["search_score"].idxmin())
    best_eml_exprs = set(df.loc[best_eml_idx, "expr"])
    keep_mask = df["expr"].isin(anchor_exprs | best_eml_exprs)
    out = df[keep_mask][["block", "model", "expr", "depth", "n_parameters", "N_T",
                          "valid_wmse", "train_chi2",
                          "AIC_train", "BIC_train",
                          "DeltaAIC_from_best", "DeltaBIC_from_best"]].copy()
    out = out.sort_values(["block", "AIC_train"])
    out.to_csv(out_path, index=False)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("Nanda-Fig2d.csv"))
    ap.add_argument("--out-prefix", type=Path, default=Path("eml_grammar"))
    ap.add_argument("--include-negative-times", action="store_true")
    ap.add_argument("--blocks", type=str, default="")
    ap.add_argument("--search-mode", choices=["exhaustive", "beam"], default="exhaustive")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-nodes", type=int, default=5)
    ap.add_argument("--beam-width", type=int, default=6)
    ap.add_argument("--split", choices=["alternating", "late"], default="alternating")
    ap.add_argument("--depth-penalty", type=float, default=0.0)
    ap.add_argument("--node-penalty", type=float, default=0.0)
    ap.add_argument("--max-nfev", type=int, default=3000)
    ap.add_argument("--plot-format", choices=["pdf", "png"], default="pdf")
    args = ap.parse_args()

    blocks = parse_nanda_csv(args.input, ignore_negative_times=not args.include_negative_times)
    if args.blocks.strip():
        filters = [x.strip() for x in args.blocks.split(",") if x.strip()]
        blocks = [b for b in blocks if any(f in b.name for f in filters)]
    if not blocks:
        raise ValueError("No blocks selected.")

    exprs = generate_expressions(args.max_depth, args.max_nodes)
    expr_lookup = {e.canonical(): e for e in exprs}
    print(f"Generated {len(exprs)} expressions up to depth={args.max_depth}, nodes={args.max_nodes}")

    all_fits = []
    for b in blocks:
        print(f"\nSearching block: {b.name}")
        all_fits.extend(search_block(b, exprs, args.search_mode, args.beam_width,
                                     args.split, args.depth_penalty, args.node_penalty, args.max_nfev))

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    summary_path  = args.out_prefix.with_name(args.out_prefix.name + "_summary.csv")
    pred_path     = args.out_prefix.with_name(args.out_prefix.name + "_predictions.csv")
    plot_path     = args.out_prefix.with_name(args.out_prefix.name + f"_best_models.{args.plot_format}")
    svg_path      = args.out_prefix.with_name(args.out_prefix.name + "_best_models.svg")
    aic_bic_path  = args.out_prefix.with_name(args.out_prefix.name + "_aic_bic.csv")

    summary = fits_df(all_fits)
    summary.to_csv(summary_path, index=False)
    save_predictions(blocks, all_fits, pred_path)
    plot_best(blocks, all_fits, expr_lookup, plot_path, svg_path)
    aic_bic = write_aic_bic_table(all_fits, aic_bic_path)

    print("\nBest models by validation score:")
    print(summary.groupby("block").head(8)[["block", "model", "expr", "depth", "nodes", "gates",
                                            "n_parameters", "valid_wmse", "AIC_train",
                                            "DeltaScore_from_best"]].to_string(index=False))
    print(f"\nSaved summary:     {summary_path}")
    print(f"Saved predictions: {pred_path}")
    print(f"Saved plot:        {plot_path}")
    print(f"Saved SVG:         {svg_path}")
    print(f"Saved AIC/BIC table: {aic_bic_path}")
    print("\nAIC/BIC comparison table:")
    print(aic_bic[["block", "expr", "n_parameters", "N_T", "valid_wmse",
                   "AIC_train", "BIC_train",
                   "DeltaAIC_from_best", "DeltaBIC_from_best"]].to_string(index=False))

    # --- Fit parameters for caption ---
    for block_name, grp in summary.groupby("block", sort=False):
        best_row = grp.iloc[0]
        best_fit = next(f for f in all_fits
                        if f.block == block_name
                        and f.model == best_row["model"]
                        and f.expr  == best_row["expr"])
        print(f"\n=== Best fit: {block_name} ===")
        print(f"  model={best_fit.model}, expr={best_fit.expr}, "
              f"depth={best_fit.depth}, nodes={best_fit.nodes}, gates={best_fit.gates}")
        for pn, pv in zip(best_fit.param_names, best_fit.params):
            print(f"  {pn} = {pv:.4g}")
        print(f"  train wMSE = {best_fit.train_wmse:.4g},  valid wMSE = {best_fit.valid_wmse:.4g}")
        for f in all_fits:
            if f.block == block_name and f is not best_fit and (f.model == "hill" or f.expr == "G(R)"):
                tag = "Hill" if f.model == "hill" else f"EML {f.expr}"
                print(f"\n  --- Comparison ({tag}) ---")
                for pn, pv in zip(f.param_names, f.params):
                    print(f"  {pn} = {pv:.4g}")
                print(f"  train wMSE = {f.train_wmse:.4g},  valid wMSE = {f.valid_wmse:.4g}")


if __name__ == "__main__":
    main()
