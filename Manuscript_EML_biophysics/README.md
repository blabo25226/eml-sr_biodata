# Non-Monotone Response Modules and Cascades from the EML Operator

Code for the manuscript:

> **Non-Monotone Response Modules and Cascades from the EML Operator for Reduced Models of Biological Dynamics**  

## Overview

Standard saturating response functions (Hill functions) are monotone and cannot reproduce recruitment-induced overshoot or adaptive transients with a single block. This repository contains the grammar-search code that evaluates whether a restricted EML (Elementary Mathematical Logic) operator grammar can produce compact non-monotone reduced models for biological time-series data.

The **centered EML gate**

$$G_{a,b,c}(x) = (c + x)^a - bx - c^a$$

is non-monotone for $0 < a < 1$, $b > 0$ with a single block, whereas any Hill-based grammar requires at least a sum of two opposing blocks to achieve the same shape. The code implements and exhaustively searches two such grammars:

$$E \;::=\; R \;\mid\; G(E) \;\mid\; E + E \qquad \text{(EML grammar)}$$
$$E \;::=\; R \;\mid\; H(E) \;\mid\; E + E \qquad \text{(Hill grammar)}$$

and applies them to two experimental datasets and one synthetic benchmark.

## Requirements

Python 3.10+ with:

```
numpy >= 1.24
scipy >= 1.10
pandas >= 2.0
matplotlib >= 3.7
```

LaTeX must be installed and on `$PATH` for figure rendering (`text.usetex=True`). On macOS this is satisfied by MacTeX; on Linux by TeX Live.

Install Python dependencies:

```bash
pip install numpy scipy pandas matplotlib
```

## Data

| File | Source |
|------|--------|
| `LaCroix-elife-66869-fig2-data.csv` | LaCroix et al. (2022), *eLife* **11**, e66869. [doi:10.7554/eLife.66869](https://doi.org/10.7554/eLife.66869). PKA activity time courses at 2 nM and 20 nM rapamycin (Fig. 2F). |
| `Nanda-Fig2d.csv` | Nanda et al. (2023), *Nature Communications* **14**, 8356. [doi:10.1038/s41467-023-43875-y](https://doi.org/10.1038/s41467-023-43875-y). Rho-GTPase perturbation–response traces (Fig. 2D). |

Both files are deposited here for completeness and reproducibility.

## Reproducing the results

```bash
bash runme.sh
```

This runs all four figure-generating scripts in sequence. Total wall time is roughly 5–15 minutes depending on hardware.

Figures are written to the locations listed under [Output files](#output-files) below.

## Scripts

| Script | Figure | Description |
|--------|--------|-------------|
| `lacroix_grammar_search_ode.py` | Fig. 1 | Exhaustive EML-grammar search embedded in a first-order relaxation ODE, fitted to the LaCroix PKA data. Includes Hill-ODE and linker-model comparators. |
| `eml_grammar_search.py` | Fig. 2 | Exhaustive EML-grammar search (static expression, monotone-recruitment input) applied to all four Nanda Rho-GTPase traces. Computes held-out wMSE, AIC, and BIC for each candidate expression and for Hill and double-Hill comparators. |
| `hill_grammar_search.py` | Fig. 3 | Parallel Hill-grammar search on the same Nanda data, identical kinetic embedding and validation procedure, for a direct structural comparison with Fig. 2. |
| `toy_coarse_graining_benchmark.py` | Fig. 4 | Synthetic benchmark: a 50-state activation–adaptation network is coarse-grained by a fixed EML cascade (depth $K = 0\ldots10$) with a learned linear readout. Reports held-out wMSE and AIC/BIC as a function of depth. |

### Key design choices common to all scripts

- **Train/validation split**: alternating (every 4th time point held out), so the split is uniform across the time axis.
- **Weighted residuals**: $w_i = 1/\max(\sigma_i,\, 0.25 \cdot \text{median}(\sigma))$, flooring small SEM values.
- **Model selection**: primary criterion is held-out weighted MSE; AIC and BIC are computed as diagnostics from training residuals.
- **Optimization**: `scipy.optimize.least_squares` with `ftol = xtol = gtol = 1e-9`, multiple random starts per expression.

## Output files

Running `runme.sh` produces the following files:

```
lacroix_grammar_ode_best_models.{pdf,svg}   # Fig. 1
lacroix_grammar_ode_summary.csv
lacroix_grammar_ode_predictions.csv

nanda_grammar_all4_best_models.{pdf,svg}    # Fig. 2
nanda_grammar_all4_summary.csv
nanda_grammar_all4_predictions.csv
nanda_grammar_all4_aic_bic.csv              # AIC/BIC table (Appendix)

nanda_hill_grammar_all4_best_models.{pdf,svg}  # Fig. 3
nanda_hill_grammar_all4_summary.csv
nanda_hill_grammar_all4_predictions.csv

toy_eml_coarse_benchmark.{pdf,svg}          # Fig. 4
toy_eml_coarse_fit_summary.csv
toy_eml_coarse_predictions.csv
toy_eml_coarse_synthetic_data.csv
toy_eml_coarse_aic_bic.csv                 # AIC/BIC table (Appendix)
```

