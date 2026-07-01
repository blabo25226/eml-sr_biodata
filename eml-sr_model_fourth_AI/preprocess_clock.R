#!/usr/bin/env Rscript
# preprocess_clock.R
# GEO GSE310779 -> paper-style preprocessing (WGCNA QC, ComBat, ASM, glmnet LOOCV)
# Reference: age_cheetah/CheetahClock_age_sex.Rmd

suppressPackageStartupMessages({
  library(glmnet)
  library(WGCNA)
  library(sva)
})

options(stringsAsFactors = FALSE)

root <- if (length(commandArgs(trailingOnly = FALSE)) > 0) {
  script <- sub("--file=", "", commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))])
  if (length(script)) dirname(normalizePath(script)) else getwd()
} else {
  getwd()
}

data_dir <- file.path(root, "data")
dir.create(data_dir, showWarnings = FALSE, recursive = TRUE)

geo_path <- file.path(root, "..", "age_cheetah", "GSE310779_series_matrix.txt")
geo_path <- normalizePath(geo_path, mustWork = TRUE)

ASM <- 2
k <- 0.2
alpha <- 0.5

# Rmd L86-87 (author SIDs; may not appear in GEO supplementary names)
manual_outlier_sids <- c(
  "ET0394TOX00092", "ET0394TOX00094", "ET0394TOX00063", "ET0394TOX00095",
  "ET0394TOX00084", "ET0394TOX00080", "ET0394TOX00069"
)

parse_geo_header <- function(path) {
  lines <- readLines(path, warn = FALSE)

  get_field <- function(tag) {
    idx <- grep(paste0("^", tag, "\t"), lines)
    if (length(idx) == 0) return(character(0))
    parts <- strsplit(lines[idx[1]], "\t", fixed = TRUE)[[1]][-1]
    gsub("^\"|\"$", "", parts)
  }

  gsm <- get_field("!Sample_geo_accession")
  titles <- get_field("!Sample_title")
  tissues <- get_field("!Sample_source_name_ch1")
  supp <- get_field("!Sample_supplementary_file")

  # First extract_protocol row (kit name only)
  proto_idx <- grep("^!Sample_extract_protocol_ch1\t", lines)
  protocols <- if (length(proto_idx) > 0) {
    parts <- strsplit(lines[proto_idx[1]], "\t", fixed = TRUE)[[1]][-1]
    gsub("^\"|\"$", "", parts)
  } else {
    rep(NA_character_, length(gsm))
  }

  ages <- vapply(titles, function(t) {
    m <- regexpr("([0-9]+\\.?[0-9]*)y", t, perl = TRUE)
    if (m[1] == -1) return(NA_real_)
    as.numeric(substr(t, m[1], m[1] + attr(m, "match.length") - 2))
  }, numeric(1))

  sex <- vapply(titles, function(t) {
    if (grepl("female", t, ignore.case = TRUE)) "F"
    else if (grepl("male", t, ignore.case = TRUE)) "M"
    else NA_character_
  }, character(1))

  batch <- vapply(protocols, function(p) {
    if (is.na(p)) return("unknown")
    if (grepl("Monarch", p, ignore.case = TRUE)) "Monarch"
    else if (grepl("Qiagen", p, ignore.case = TRUE)) "Qiagen"
    else "unknown"
  }, character(1))

  study <- ifelse(batch == "Monarch", "MammCon", "SDZWA")

  data.frame(
    GSM = gsm,
    Title = titles,
    Tissue = tolower(tissues),
    Age = ages,
    Sex = sex,
    Batch = batch,
    Study = study,
    Supplementary = supp,
    stringsAsFactors = FALSE
  )
}

read_beta_matrix <- function(path) {
  lines <- readLines(path, warn = FALSE)
  begin <- which(grepl("^!series_matrix_table_begin", lines))
  if (length(begin) == 0) stop("series_matrix_table_begin not found")
  beta <- read.delim(path, skip = begin, check.names = FALSE, row.names = 1)
  if ("!series_matrix_table_end" %in% rownames(beta)) {
    beta <- beta[rownames(beta) != "!series_matrix_table_end", , drop = FALSE]
  }
  mat <- as.matrix(beta)
  storage.mode(mat) <- "numeric"
  mat
}

age_transform <- function(x, maturity = ASM) {
  ifelse(
    is.na(x) | is.na(maturity), NA_real_,
    ifelse(x < maturity, log((x + k) / (maturity + k)), (x - maturity) / (maturity + k))
  )
}

age_inv_transform <- function(y, maturity = ASM) {
  ifelse(
    is.na(y) | is.na(maturity), NA_real_,
    ifelse(y < 0, (maturity + k) * exp(y) - k, (maturity + k) * y + maturity)
  )
}

cat("Reading GEO:", geo_path, "\n")
meta <- parse_geo_header(geo_path)
beta_all <- read_beta_matrix(geo_path)

# Align columns (samples) to metadata GSM order
if (!all(colnames(beta_all) %in% meta$GSM)) {
  stop("GSM IDs in matrix do not match metadata")
}
meta <- meta[match(colnames(beta_all), meta$GSM), ]
rownames(meta) <- meta$GSM

# Clock training cohort: liver + blood (skin held out)
is_clock <- meta$Tissue %in% c("liver", "blood")
is_skin <- meta$Tissue == "skin"

meta_skin <- meta[is_skin, , drop = FALSE]
beta_skin <- beta_all[, meta_skin$GSM, drop = FALSE]

meta <- meta[is_clock & !is.na(meta$Age), , drop = FALSE]
beta <- beta_all[, meta$GSM, drop = FALSE]

cat("Clock cohort (liver+blood):", nrow(meta), "samples\n")
cat("Skin (held out):", nrow(meta_skin), "samples\n")

# Transpose to samples x CpG for WGCNA-style QC
datExpr <- t(beta)
datExpr <- as.data.frame(datExpr)

gsg <- goodSamplesGenes(datExpr, verbose = 0)
if (!gsg$allOK) {
  datExpr <- datExpr[gsg$goodSamples, gsg$goodGenes, drop = FALSE]
  meta <- meta[rownames(datExpr), , drop = FALSE]
}

# Hierarchical clustering outliers (Rmd: h = 30)
sampleTree <- hclust(dist(datExpr), method = "average")
clusters <- cutree(sampleTree, h = 30)
cluster_sizes <- table(clusters)
singleton_clusters <- as.integer(names(cluster_sizes)[cluster_sizes == 1])
cluster_outliers <- names(clusters)[clusters %in% singleton_clusters]

# Map manual author SIDs via supplementary file names (if present)
sid_map <- data.frame(GSM = character(), SID = character(), stringsAsFactors = FALSE)
for (i in seq_len(nrow(meta))) {
  supp <- meta$Supplementary[i]
  for (sid in manual_outlier_sids) {
    if (grepl(sid, supp, fixed = TRUE)) {
      sid_map <- rbind(sid_map, data.frame(GSM = meta$GSM[i], SID = sid))
    }
  }
}
write.csv(sid_map, file.path(data_dir, "sid_gsm_map.csv"), row.names = FALSE)

manual_gsm <- sid_map$GSM
if (length(manual_gsm) == 0) {
  cat("Note: author SID outliers not found in GEO supplementary paths; using clustering only.\n")
}

remove_ids <- unique(c(cluster_outliers, manual_gsm))
cat("Removing", length(remove_ids), "outlier samples:", paste(remove_ids, collapse = ", "), "\n")

keep <- !(rownames(datExpr) %in% remove_ids)
datExpr <- datExpr[keep, , drop = FALSE]
meta <- meta[rownames(datExpr), , drop = FALSE]

beta_clock <- t(as.matrix(datExpr))
rownames(beta_clock) <- colnames(datExpr)
colnames(beta_clock) <- rownames(datExpr)

# ComBat batch correction (Rmd: batch = study)
batch <- meta$Study
mod <- model.matrix(~1, data = meta)
sva_data0 <- ComBat(dat = beta_clock, batch = batch, mod = mod, par.prior = TRUE, prior.plots = FALSE)
sva_data <- t(sva_data0)

meta$age_trans <- age_transform(meta$Age, ASM)

write.csv(meta, file.path(data_dir, "clock_samples.csv"), row.names = TRUE)
write.csv(sva_data, file.path(data_dir, "beta_combat.csv"), row.names = TRUE)
write.csv(meta_skin, file.path(data_dir, "skin_samples.csv"), row.names = TRUE)

# Elastic Net + LOOCV (CheetahClock_age_sex.Rmd L164-226)
EN_methylation_data <- as.matrix(sva_data)
EN_age <- meta$age_trans
n <- length(EN_age)

glmnet_cv_training <- cv.glmnet(EN_methylation_data, EN_age, alpha = alpha, family = "gaussian", nfolds = n)
best_lambda <- glmnet_cv_training$lambda.min
cat("Optimal lambda:", best_lambda, "\n")

# LOOCV predictions on age_trans scale
pred_trans <- numeric(n)
for (i in seq_len(n)) {
  fit <- glmnet(
    EN_methylation_data[-i, , drop = FALSE], EN_age[-i],
    lambda = best_lambda, alpha = alpha, family = "gaussian"
  )
  pred_trans[i] <- as.numeric(predict(fit, newx = EN_methylation_data[i, , drop = FALSE], type = "response"))
}

pred_age <- age_inv_transform(pred_trans, ASM)
r_loocv <- cor(meta$Age, pred_age, method = "pearson")
mae_loocv <- median(abs(meta$Age - pred_age))

cat("LOOCV Pearson r:", round(r_loocv, 4), " MAE:", round(mae_loocv, 4), "\n")

loocv_df <- data.frame(
  GSM = meta$GSM,
  Age = meta$Age,
  age_trans = meta$age_trans,
  pred_trans = pred_trans,
  pred_age = pred_age,
  Tissue = meta$Tissue,
  Study = meta$Study,
  stringsAsFactors = FALSE
)
write.csv(loocv_df, file.path(data_dir, "baseline_loocv.csv"), row.names = FALSE)

# Full-data glmnet for CpG selection
best_model <- glmnet(EN_methylation_data, EN_age, lambda = best_lambda, alpha = alpha, family = "gaussian")
coefs <- as.matrix(coef(best_model))
nz <- rownames(coefs)[coefs[, 1] != 0]
nz <- setdiff(nz, "(Intercept)")
cat("Non-zero CpGs:", length(nz), "\n")

cpg_coefs <- data.frame(
  CpG = nz,
  Coef = coefs[nz, 1],
  AbsCoef = abs(coefs[nz, 1]),
  stringsAsFactors = FALSE
)
cpg_coefs <- cpg_coefs[order(-cpg_coefs$AbsCoef), ]
write.csv(cpg_coefs, file.path(data_dir, "selected_cpgs.csv"), row.names = FALSE)

full_coefs <- data.frame(
  term = rownames(coefs),
  coef = coefs[, 1],
  stringsAsFactors = FALSE
)
write.csv(full_coefs, file.path(data_dir, "glmnet_coefs_full.csv"), row.names = FALSE)

summary_metrics <- data.frame(
  metric = c("n_samples", "n_cpgs_selected", "lambda_min", "loocv_r", "loocv_mae"),
  value = c(n, nrow(cpg_coefs), best_lambda, r_loocv, mae_loocv)
)
write.csv(summary_metrics, file.path(data_dir, "baseline_summary.csv"), row.names = FALSE)

# PCA plot before/after ComBat
if (requireNamespace("ggplot2", quietly = TRUE)) {
  png(file.path(data_dir, "pca_batch.png"), width = 900, height = 420)
  par(mfrow = c(1, 2))
  pre <- prcomp(t(beta_clock), scale. = FALSE)
  plot(pre$x[, 1:2], col = ifelse(meta$Study == "SDZWA", "green4", "sienna1"), pch = 16,
       main = "Before ComBat", xlab = "PC1", ylab = "PC2")
  post <- prcomp(t(sva_data0), scale. = FALSE)
  plot(post$x[, 1:2], col = ifelse(meta$Study == "SDZWA", "green4", "sienna1"), pch = 16,
       main = "After ComBat", xlab = "PC1", ylab = "PC2")
  dev.off()
}

cat("Preprocessing complete. Outputs in", data_dir, "\n")
