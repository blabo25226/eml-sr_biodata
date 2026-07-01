#!/usr/bin/env Rscript
# Export glmnet full coefficients from existing fourth_AI data/
suppressPackageStartupMessages(library(glmnet))

root <- if (length(sys.frames()) > 0) {
  script <- sub("--file=", "", commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))])
  if (length(script) && nzchar(script)) dirname(normalizePath(script, mustWork = FALSE)) else getwd()
} else {
  getwd()
}
data_dir <- file.path(root, "data")

meta <- read.csv(file.path(data_dir, "clock_samples.csv"), row.names = 1)
beta <- as.matrix(read.csv(file.path(data_dir, "beta_combat.csv"), row.names = 1))
beta <- beta[rownames(meta), , drop = FALSE]
y <- meta$age_trans
summary <- read.csv(file.path(data_dir, "baseline_summary.csv"))
lam <- summary$value[summary$metric == "lambda_min"]

fit <- glmnet(beta, y, alpha = 0.5, lambda = lam, family = "gaussian")
coefs <- as.matrix(coef(fit))
full_coefs <- data.frame(term = rownames(coefs), coef = coefs[, 1], stringsAsFactors = FALSE)
write.csv(full_coefs, file.path(data_dir, "glmnet_coefs_full.csv"), row.names = FALSE)
cat("Wrote glmnet_coefs_full.csv\n")
