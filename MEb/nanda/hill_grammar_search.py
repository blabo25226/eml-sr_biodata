#!/usr/bin/env python3
"""
hill_grammar_search.py

Restricted symbolic-regression search for Hill-generated response models.

This is the Hill-function analogue of eml_grammar_search.py. It uses the same
expression grammar,

    E ::= R | G(E) | E + E

but replaces the EML gate with a full affine Hill gate,

    G_{c,A,K,h}(x) = c + A x^h / (K^h + x^h),

with c and A allowed to be positive or negative, and K,h constrained positive.

The recruitment input is

    R(t;k) = 1 - exp(-k t),

and the fitted model is

    y(t) = E(R(t;k)).

Unlike the earlier version, there is no additional global y0 + B E(...) readout
for Hill-expression models, because each Hill gate already contains its own
offset and amplitude. This makes the comparator fairer: every application of G
has the standard four-parameter Hill form requested.

Baselines:
    linear_R:       y = c + A R(t;k)
    simple_hill:    y = c + A R(t;k)^h/(K^h+R(t;k)^h)

Example
-------
python hill_grammar_search.py \
  --input Nanda-Fig2d.csv \
  --out-prefix nanda_hill_grammar_all4 \
  --search-mode exhaustive \
  --max-depth 3 \
  --max-nodes 5 \
  --plot-format pdf
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import least_squares


# -----------------------------
# Data
# -----------------------------

@dataclass
class BlockData:
    name: str
    time: np.ndarray
    mean: np.ndarray
    sem: np.ndarray
    n: np.ndarray


def parse_nanda_csv(path: Path, ignore_negative_times: bool = True) -> list[BlockData]:
    df = pd.read_csv(path, header=None)
    starts = [c for c, v in enumerate(df.iloc[0]) if isinstance(v, str) and "perturbation;" in v]
    if not starts:
        raise ValueError("No perturbation blocks found. Expected row-0 cells containing 'perturbation;'.")

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

        blocks.append(BlockData(
            name=name,
            time=out["time"].to_numpy(float),
            mean=out["mean"].to_numpy(float),
            sem=out["sem"].to_numpy(float),
            n=out["n"].to_numpy(float),
        ))

    return blocks


def weights(sem: np.ndarray, floor_fraction: float = 0.25) -> np.ndarray:
    pos = sem[np.isfinite(sem) & (sem > 0)]
    if len(pos) == 0:
        return np.ones_like(sem)
    return np.maximum(sem, np.median(pos) * floor_fraction)


def split_points(n: int, mode: str) -> tuple[np.ndarray, np.ndarray]:
    idx = np.arange(n)
    if mode == "late":
        train = idx < int(0.75 * n)
        valid = ~train
    elif mode == "alternating":
        valid = idx % 4 == 1
        train = ~valid
        train[0] = True
        valid[0] = False
    else:
        raise ValueError("split must be 'alternating' or 'late'")
    return train, valid


# -----------------------------
# Hill grammar
# -----------------------------

def R_of_t(t: np.ndarray, k: float) -> np.ndarray:
    return 1.0 - np.exp(-k * t)


def hill_sigmoid(x: np.ndarray, K: float, h: float) -> np.ndarray:
    x = np.maximum(x, 0.0)
    xh = np.power(x + 1e-12, h)
    Kh = np.power(K + 1e-12, h)
    return xh / (Kh + xh + 1e-12)


def hill_gate(x: np.ndarray, c: float, A: float, K: float, h: float) -> np.ndarray:
    """
    Full affine Hill gate:
        G(x)=c + A x^h/(K^h+x^h)

    c and A are allowed to be positive or negative.
    K and h are constrained positive by optimizer bounds.
    """
    return c + A * hill_sigmoid(x, K, h)


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
            return f"H({self.child.canonical()})"
        if self.kind == "Add":
            return f"({self.left.canonical()}+{self.right.canonical()})"
        raise ValueError(self.kind)

    def evaluate(self, R: np.ndarray, pars: np.ndarray) -> np.ndarray:
        """
        Evaluate expression.

        Hill-gate parameters are consumed in prefix order:
            H(E) consumes [c,A,K,h] then parameters for E.
            Add(L,R) consumes parameters for L, then parameters for R.
        """
        if self.kind == "R":
            return R
        if self.kind == "G":
            c, A, K, h = pars[:4]
            child_pars = pars[4:4 + 4 * self.child.gates()]
            return hill_gate(self.child.evaluate(R, child_pars), c, A, K, h)
        if self.kind == "Add":
            nleft = 4 * self.left.gates()
            return self.left.evaluate(R, pars[:nleft]) + self.right.evaluate(R, pars[nleft:])
        raise ValueError(self.kind)


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


# -----------------------------
# Fitting
# -----------------------------

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


def predict_expr(expr: Expr, p: np.ndarray, t: np.ndarray) -> np.ndarray:
    k = p[0]
    R = R_of_t(t, k)
    return expr.evaluate(R, p[1:])


def predict_linear(p: np.ndarray, t: np.ndarray) -> np.ndarray:
    c, A, k = p
    return c + A * R_of_t(t, k)


def predict_simple_hill(p: np.ndarray, t: np.ndarray) -> np.ndarray:
    c, A, K, h, k = p
    R = R_of_t(t, k)
    return hill_gate(R, c, A, K, h)


def fit_model(
    block: BlockData,
    model: str,
    expr_label: str,
    depth: int,
    nodes: int,
    gates: int,
    predict: Callable[[np.ndarray, np.ndarray], np.ndarray],
    starts: list[np.ndarray],
    lo: np.ndarray,
    hi: np.ndarray,
    train: np.ndarray,
    valid: np.ndarray,
    depth_penalty: float,
    node_penalty: float,
    max_nfev: int,
) -> FitResult:
    t, y, w = block.time, block.mean, weights(block.sem)
    best = None

    for x0 in starts:
        x0 = np.minimum(np.maximum(np.asarray(x0, float), lo + 1e-10), hi - 1e-10)

        def res(p):
            return (predict(p, t)[train] - y[train]) / w[train]

        try:
            fit = least_squares(
                res,
                x0,
                bounds=(lo, hi),
                max_nfev=max_nfev,
                ftol=1e-9,
                xtol=1e-9,
                gtol=1e-9,
            )
        except Exception:
            continue

        chi = float(np.sum(res(fit.x) ** 2))
        if best is None or chi < best[0]:
            best = (chi, fit)

    if best is None:
        raise RuntimeError(f"Fit failed: {block.name} / {expr_label}")

    train_chi2, fit = best
    pred = predict(fit.x, t)
    all_res = (pred - y) / w
    valid_chi2 = float(np.sum(all_res[valid] ** 2))
    all_chi2 = float(np.sum(all_res ** 2))
    ntr, nva, kpar = int(np.sum(train)), int(np.sum(valid)), len(fit.x)
    train_wmse = train_chi2 / ntr
    valid_wmse = valid_chi2 / nva
    aic = float(ntr * np.log(max(train_chi2, 1e-12) / ntr) + 2 * kpar)
    bic = float(ntr * np.log(max(train_chi2, 1e-12) / ntr) + kpar * np.log(ntr))
    score = float(valid_wmse + depth_penalty * depth + node_penalty * nodes)

    if model == "linear_R":
        names = ["c", "A", "k"]
    elif model == "simple_hill":
        names = ["c", "A", "K", "h", "k"]
    else:
        names = ["k"]
        for j in range(gates):
            names += [f"c{j+1}", f"A{j+1}", f"K{j+1}", f"h{j+1}"]

    return FitResult(
        block=block.name,
        model=model,
        expr=expr_label,
        depth=depth,
        nodes=nodes,
        gates=gates,
        params=fit.x,
        param_names=names,
        prediction=pred,
        train_chi2=train_chi2,
        valid_chi2=valid_chi2,
        all_chi2=all_chi2,
        train_wmse=train_wmse,
        valid_wmse=valid_wmse,
        aic_train=aic,
        bic_train=bic,
        score=score,
        n_parameters=kpar,
    )


def expr_starts_bounds(block: BlockData, expr: Expr) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    y0 = float(block.mean[0])
    ymin = float(np.min(block.mean))
    ymax = float(np.max(block.mean))
    amp = max(1.0, ymax - ymin)
    g = expr.gates()

    # Expression model parameters:
    #   k, then [c,A,K,h] for each Hill gate in prefix order.
    lo = [1e-4]
    hi = [30.0]
    for _ in range(g):
        lo += [-300.0, -1000.0, 1e-4, 0.03]
        hi += [300.0, 1000.0, 100.0, 30.0]

    starts: list[np.ndarray] = []
    if g == 0:
        return [np.asarray([0.6], float)], np.asarray(lo, float), np.asarray(hi, float)

    # The important case for nonmonotone responses is an additive pair such as
    # H(R)+H(R), which needs one positive low-threshold Hill branch and one
    # negative higher-threshold Hill branch. The previous version initialized
    # all gates with the same amplitude sign, making these fits prone to poor
    # local minima. Here each gate receives its own sign, K, and h start.
    from itertools import product

    if g == 1:
        sign_patterns = [(1.0,), (-1.0,)]
    elif g == 2:
        # The critical patterns for biphasic curves are mixed signs.
        sign_patterns = [(1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0)]
    else:
        sign_patterns = [(1.0, -1.0, 1.0), (-1.0, 1.0, -1.0), (1.0, 1.0, -1.0), (-1.0, -1.0, 1.0)]

    threshold_templates = [
        # low-threshold branch plus higher-threshold branch
        [(0.10, 1.0), (1.20, 4.0), (2.50, 6.0)],
        # reversed threshold order
        [(1.20, 4.0), (0.10, 1.0), (2.50, 6.0)],
        # moderate same-threshold start
        [(0.50, 2.0), (0.50, 2.0), (0.50, 2.0)],
    ]

    for k0 in [0.3, 0.8]:
        for signs in sign_patterns:
            for template in threshold_templates:
                p = [k0]
                for j in range(g):
                    K0, h0 = template[j % len(template)]
                    # For additive expressions the baseline is the sum of c_j,
                    # so split the observed initial value across gates. For nested
                    # expressions this is only a start; the optimizer can move it.
                    c0 = y0 / max(g, 1)
                    # Scale amplitudes down with gate count to avoid huge starts
                    # for additive expressions, but keep enough range for overshoot.
                    A0 = signs[j] * amp / max(1.0, g / 2.0)
                    p += [c0, A0, K0, h0]
                starts.append(np.asarray(p, float))

    return starts, np.asarray(lo, float), np.asarray(hi, float)


def fit_expr(block, expr, train, valid, depth_penalty, node_penalty, max_nfev):
    starts, lo, hi = expr_starts_bounds(block, expr)
    return fit_model(
        block,
        "Hill_expr",
        expr.canonical(),
        expr.depth(),
        expr.nodes(),
        expr.gates(),
        lambda p, t: predict_expr(expr, p, t),
        starts,
        lo,
        hi,
        train,
        valid,
        depth_penalty,
        node_penalty,
        max_nfev,
    )


def fit_baselines(block, train, valid, depth_penalty, node_penalty, max_nfev):
    y0 = float(block.mean[0])
    ymin = float(np.min(block.mean))
    ymax = float(np.max(block.mean))
    amp = max(1.0, ymax - ymin)

    linear_starts = []
    for A in [amp, -amp, ymax - y0, ymin - y0]:
        for k0 in [0.2, 0.6, 1.5]:
            linear_starts.append(np.asarray([y0, A, k0], float))

    hill_starts = []
    for A in [amp, -amp, ymax - y0, ymin - y0]:
        for K0 in [0.1, 0.3, 0.7, 1.5]:
            for h0 in [1.0, 2.0, 4.0, 8.0]:
                for k0 in [0.2, 0.6, 1.5]:
                    hill_starts.append(np.asarray([y0, A, K0, h0, k0], float))

    fits = [
        fit_model(
            block,
            "linear_R",
            "R",
            0,
            1,
            0,
            predict_linear,
            linear_starts,
            np.array([-300.0, -1000.0, 1e-4]),
            np.array([300.0, 1000.0, 30.0]),
            train,
            valid,
            depth_penalty,
            node_penalty,
            max_nfev,
        ),
        fit_model(
            block,
            "simple_hill",
            "H(R)",
            1,
            2,
            1,
            predict_simple_hill,
            hill_starts,
            np.array([-300.0, -1000.0, 1e-4, 0.03, 1e-4]),
            np.array([300.0, 1000.0, 100.0, 30.0, 30.0]),
            train,
            valid,
            depth_penalty,
            node_penalty,
            max_nfev,
        ),
    ]
    return fits


# -----------------------------
# Search and output
# -----------------------------

def search_block(block, exprs, mode, beam_width, split, depth_penalty, node_penalty, max_nfev):
    train, valid = split_points(len(block.time), split)
    fits = fit_baselines(block, train, valid, depth_penalty, node_penalty, max_nfev)

    if mode == "exhaustive":
        selected_exprs = exprs
    else:
        selected_exprs = sorted(exprs, key=lambda e: (e.depth(), e.nodes(), e.canonical()))[
            : beam_width * (max(e.depth() for e in exprs) + 1)
        ]

    print(f"  fitting {len(selected_exprs)} Hill expressions")
    for e in selected_exprs:
        fits.append(fit_expr(block, e, train, valid, depth_penalty, node_penalty, max_nfev))

    return fits


def fits_df(fits):
    rows = []
    for f in fits:
        rows.append({
            "block": f.block,
            "model": f.model,
            "expr": f.expr,
            "depth": f.depth,
            "nodes": f.nodes,
            "gates": f.gates,
            "n_parameters": f.n_parameters,
            "parameters": "; ".join(f"{n}={v:.8g}" for n, v in zip(f.param_names, f.params)),
            "train_chi2": f.train_chi2,
            "valid_chi2": f.valid_chi2,
            "all_chi2": f.all_chi2,
            "train_wmse": f.train_wmse,
            "valid_wmse": f.valid_wmse,
            "AIC_train": f.aic_train,
            "BIC_train": f.bic_train,
            "search_score": f.score,
        })
    df = pd.DataFrame(rows)
    df["DeltaScore_from_best"] = df.groupby("block")["search_score"].transform(lambda x: x - x.min())
    df["DeltaAIC_from_best"] = df.groupby("block")["AIC_train"].transform(lambda x: x - x.min())
    return df.sort_values(["block", "search_score"])


def save_predictions(blocks, fits, out):
    bdict = {b.name: b for b in blocks}
    rows = []
    for f in fits:
        b = bdict[f.block]
        for t, mean, sem, n, pred in zip(b.time, b.mean, b.sem, b.n, f.prediction):
            rows.append({
                "block": f.block,
                "model": f.model,
                "expr": f.expr,
                "depth": f.depth,
                "nodes": f.nodes,
                "gates": f.gates,
                "time_min": t,
                "mean": mean,
                "sem": sem,
                "n": n,
                "prediction": pred,
            })
    pd.DataFrame(rows).to_csv(out, index=False)


def plot_best(blocks, fits, expr_lookup, out):
    df = fits_df(fits)
    best = df.groupby("block").first().reset_index()
    fit_lookup = {(f.block, f.model, f.expr): f for f in fits}
    block_lookup = {b.name: b for b in blocks}

    _FS     = 9
    _FS_LEG = 7.5
    _FS_PNL = 11
    _LW_REF = 0.6

    n = len(best)
    ncols = 1 if n == 1 else (2 if n <= 4 else 3)
    nrows = int(np.ceil(n / ncols))
    panel_labels = [f'({chr(ord("a") + i)})' for i in range(n)]
    fig_w = 3.37 if ncols == 1 else 7.0
    fig_h = nrows * (3.0 if ncols == 1 else (2.8 if nrows > 1 else 3.2))

    with plt.rc_context({'text.usetex': True, 'font.family': 'serif',
                         'font.size': _FS, 'axes.labelsize': _FS,
                         'xtick.labelsize': _FS, 'ytick.labelsize': _FS}):
        fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h))
        axes = np.asarray(axes).reshape(-1)
        for ax, (_, row), lbl in zip(axes, best.iterrows(), panel_labels):
            b = block_lookup[row["block"]]
            fbest = fit_lookup[(row["block"], row["model"], row["expr"])]
            all_plotted_y = list(b.mean - b.sem) + list(b.mean + b.sem)
            tf = np.linspace(float(np.min(b.time)), float(np.max(b.time)), 500)
            to_plot = [fbest]
            for f in fits:
                if f.block == b.name and (f.model == "simple_hill" or f.expr == "H(R)"):
                    to_plot.append(f)
            seen = set()
            for f in to_plot:
                key = (f.model, f.expr)
                if key in seen:
                    continue
                seen.add(key)
                if f.model == "linear_R":
                    pred = predict_linear(f.params, tf)
                elif f.model == "simple_hill":
                    pred = predict_simple_hill(f.params, tf)
                elif f.model == "Hill_expr":
                    pred = predict_expr(expr_lookup[f.expr], f.params, tf)
                else:
                    continue
                label = (f'Best: {f.expr}' if f is fbest
                         else (f.expr if f.model == 'Hill_expr'
                               else f.model.replace('_', ' ').title()))
                ax.plot(tf, pred, linewidth=2.0, label=label, zorder=3)
                all_plotted_y.extend(pred[np.isfinite(pred)])
            ax.errorbar(b.time[::2], b.mean[::2], yerr=b.sem[::2],
                        fmt='o', markersize=2.0, capsize=1.2,
                        label=r'Mean $\pm$ SEM', zorder=2)
            ax.axhline(0, color='k', linewidth=_LW_REF, zorder=0)
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
            if n == 1:
                ax.legend(frameon=False, fontsize=_FS_LEG,
                          loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2)
            else:
                ax.legend(frameon=False, fontsize=_FS_LEG, ncol=2, loc='upper right')
            if n > 1:
                ax.text(0.0, 1.04, lbl, transform=ax.transAxes,
                        fontsize=_FS_PNL, va='bottom', ha='left', clip_on=False)
        for ax in axes[n:]:
            ax.axis('off')
        fig.tight_layout(pad=0.8)
        svg_out = str(out).replace('.pdf', '.svg')
        fig.savefig(out,     bbox_inches='tight')
        fig.savefig(svg_out, bbox_inches='tight')
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("Nanda-Fig2d.csv"))
    ap.add_argument("--out-prefix", type=Path, default=Path("hill_grammar"))
    ap.add_argument("--include-negative-times", action="store_true")
    ap.add_argument("--blocks", type=str, default="", help="Comma-separated substring filters for block names.")
    ap.add_argument("--search-mode", choices=["exhaustive", "beam"], default="exhaustive")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-nodes", type=int, default=5)
    ap.add_argument("--beam-width", type=int, default=6)
    ap.add_argument("--split", choices=["alternating", "late"], default="alternating")
    ap.add_argument("--depth-penalty", type=float, default=0.0)
    ap.add_argument("--node-penalty", type=float, default=0.0)
    ap.add_argument("--max-nfev", type=int, default=5000)
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
    print(f"Generated {len(exprs)} Hill expressions up to depth={args.max_depth}, nodes={args.max_nodes}")

    all_fits = []
    for b in blocks:
        print(f"\nSearching block: {b.name}")
        all_fits.extend(search_block(
            b,
            exprs,
            args.search_mode,
            args.beam_width,
            args.split,
            args.depth_penalty,
            args.node_penalty,
            args.max_nfev,
        ))

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    summary_path = args.out_prefix.with_name(args.out_prefix.name + "_summary.csv")
    pred_path = args.out_prefix.with_name(args.out_prefix.name + "_predictions.csv")
    plot_path = args.out_prefix.with_name(args.out_prefix.name + f"_best_models.{args.plot_format}")

    summary = fits_df(all_fits)
    summary.to_csv(summary_path, index=False)
    save_predictions(blocks, all_fits, pred_path)
    plot_best(blocks, all_fits, expr_lookup, plot_path)

    print("\nBest models by validation score:")
    print(summary.groupby("block").head(8)[[
        "block", "model", "expr", "depth", "nodes", "gates",
        "n_parameters", "valid_wmse", "AIC_train", "DeltaScore_from_best"
    ]].to_string(index=False))
    print(f"\nSaved summary: {summary_path}")
    print(f"Saved predictions: {pred_path}")
    print(f"Saved plot: {plot_path}")


if __name__ == "__main__":
    main()
