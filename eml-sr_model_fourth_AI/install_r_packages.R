# One-time setup for preprocess_clock.R
cran_pkgs <- c("glmnet", "WGCNA", "BiocManager")
for (p in cran_pkgs) {
  if (!requireNamespace(p, quietly = TRUE)) {
    install.packages(p, repos = "https://cloud.r-project.org")
  }
}
if (!requireNamespace("sva", quietly = TRUE)) {
  BiocManager::install("sva", update = FALSE, ask = FALSE)
}
for (p in c("impute", "preprocessCore")) {
  if (!requireNamespace(p, quietly = TRUE)) {
    BiocManager::install(p, update = FALSE, ask = FALSE)
  }
}
