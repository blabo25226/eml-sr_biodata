#!/usr/bin/env Rscript
# replicate_paper_enet.R
# Paper-faithful CheetahClock Elastic Net (CheetahClock_age_sex.Rmd)
# Training: SDZWA liver + MCDB cheetah blood (target n=52)

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
data_root <- normalizePath(file.path(root, "..", "data", "age_cheetah"), mustWork = TRUE)

geo_path <- file.path(data_root, "GSE310779_series_matrix.txt")
mcdb_beta_path <- file.path(data_root, "cheetah_mamconsortium_betas.csv")
mcdb_meta_path <- file.path(data_root, "mcdb_cheetah_blood_meta.csv")

ASM <- 2
k <- 0.2
alpha <- 0.5
TARGET_LIVER_N <- 38

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
  data.frame(
    GSM = gsm, Title = titles, Tissue = tolower(tissues),
    Age = ages, Sex = sex, Supplementary = supp,
    stringsAsFactors = FALSE
  )
}

read_beta_matrix <- function(path) {
  lines <- readLines(path, warn = FALSE)
  begin <- which(grepl("^!series_matrix_table_begin", lines))
  beta <- read.delim(path, skip = begin, check.names = FALSE, row.names = 1)
  if ("!series_matrix_table_end" %in% rownames(beta)) {
    beta <- beta[rownames(beta) != "!series_matrix_table_end", , drop = FALSE]
  }
  mat <- as.matrix(beta)
  storage.mode(mat) <- "numeric"
  mat
}

age_transform <- function(x, maturity = ASM) {
  ifelse(is.na(x) | is.na(maturity), NA_real_,
    ifelse(x < maturity, log((x + k) / (maturity + k)), (x - maturity) / (maturity + k)))
}

age_inv_transform <- function(y, maturity = ASM) {
  ifelse(is.na(y) | is.na(maturity), NA_real_,
    ifelse(y < 0, (maturity + k) * exp(y) - k, (maturity + k) * y + maturity))
}

cluster_outliers_at_h <- function(datExpr, h = 30) {
  sampleTree <- hclust(dist(datExpr), method = "average")
  clusters <- cutree(sampleTree, h = h)
  cluster_sizes <- table(clusters)
  singleton_clusters <- as.integer(names(cluster_sizes)[cluster_sizes == 1])
  names(clusters)[clusters %in% singleton_clusters]
}

cat("=== Paper replication: Elastic Net CheetahClock ===\n")

meta_all <- parse_geo_header(geo_path)
beta_all <- read_beta_matrix(geo_path)
meta_all <- meta_all[match(colnames(beta_all), meta_all$GSM), ]

meta_liver <- meta_all[meta_all$Tissue == "liver" & !is.na(meta_all$Age), , drop = FALSE]
rownames(meta_liver) <- meta_liver$GSM
beta_liver <- beta_all[, meta_liver$GSM, drop = FALSE]
datExpr <- as.data.frame(t(beta_liver))

gsg <- goodSamplesGenes(datExpr, verbose = 0)
if (!gsg$allOK) {
  datExpr <- datExpr[gsg$goodSamples, gsg$goodGenes, drop = FALSE]
  meta_liver <- meta_liver[rownames(datExpr), , drop = FALSE]
}

# Primary: h=30 singleton outliers (Rmd)
cluster_out <- cluster_outliers_at_h(datExpr, h = 30)

# Paper stillborns (three female 0.0y neonates; GEO GSM IDs)
stillborn_gsm <- c("GSM9308716", "GSM9308720", "GSM9308721")
stillborn_gsm <- stillborn_gsm[stillborn_gsm %in% meta_liver$GSM]
remove_ids <- unique(c(cluster_out, stillborn_gsm))
cat("Cluster outliers:", length(cluster_out), "| stillborns (0.0y 1-3):", length(stillborn_gsm), "\n")

keep <- !(rownames(datExpr) %in% remove_ids)
datExpr <- datExpr[keep, , drop = FALSE]
meta_liver <- meta_liver[rownames(datExpr), , drop = FALSE]
cat("SDZWA liver after QC:", nrow(meta_liver), "(target", TARGET_LIVER_N, ")\n")

# MCDB blood 14
mammcon <- read.csv(mcdb_beta_path, check.names = FALSE)
rownames(mammcon) <- mammcon$X
mammcon <- mammcon[, -1, drop = FALSE]
beta_mammcon <- t(as.data.frame(mammcon))
mcdb_meta <- read.csv(mcdb_meta_path, stringsAsFactors = FALSE)
mcdb_meta <- mcdb_meta[match(rownames(beta_mammcon), mcdb_meta$chip_id), , drop = FALSE]
rownames(beta_mammcon) <- mcdb_meta$SID

common_cpgs <- intersect(colnames(datExpr), colnames(beta_mammcon))
beta_liver_qc <- as.matrix(datExpr)[, common_cpgs, drop = FALSE]
beta_mammcon <- beta_mammcon[, common_cpgs, drop = FALSE]
rownames(beta_liver_qc) <- rownames(datExpr)
rownames(beta_mammcon) <- mcdb_meta$SID
if (anyDuplicated(rownames(beta_liver_qc)) > 0 || anyDuplicated(rownames(beta_mammcon)) > 0) {
  stop("Duplicate sample row names in training matrices")
}

meta_liver_clock <- data.frame(
  SID = meta_liver$GSM, GSM = meta_liver$GSM,
  Age = meta_liver$Age, Sex = meta_liver$Sex,
  Study = "SDZWA", Tissue = "liver", stringsAsFactors = FALSE
)
rownames(meta_liver_clock) <- meta_liver_clock$SID

meta_mcdb_clock <- data.frame(
  SID = mcdb_meta$SID, GSM = mcdb_meta$GSM,
  Age = mcdb_meta$Age, Sex = mcdb_meta$Sex,
  Study = "MammCon", Tissue = "blood", stringsAsFactors = FALSE
)
rownames(meta_mcdb_clock) <- meta_mcdb_clock$SID

beta_clock_samples <- rbind(beta_liver_qc, beta_mammcon)
meta <- rbind(meta_liver_clock, meta_mcdb_clock)
meta <- meta[rownames(beta_clock_samples), , drop = FALSE]

cat("Training cohort:", nrow(meta), "(liver", sum(meta$Study == "SDZWA"),
    "+ MCDB", sum(meta$Study == "MammCon"), ")\n")

# ComBat (Rmd: batch = study)
beta_clock <- t(beta_clock_samples)
mod <- model.matrix(~1, data = meta)
sva_data0 <- ComBat(dat = beta_clock, batch = meta$Study, mod = mod, par.prior = TRUE, prior.plots = FALSE)
sva_data <- t(sva_data0)

meta$age_trans <- age_transform(meta$Age, ASM)
EN_methylation_data <- as.matrix(sva_data)
EN_age <- meta$age_trans
n <- length(EN_age)

glmnet_cv_training <- cv.glmnet(EN_methylation_data, EN_age, alpha = alpha, family = "gaussian", nfolds = n)
best_lambda <- glmnet_cv_training$lambda.min
cat("lambda.min:", best_lambda, "\n")

# --- Paper Rmd LOOCV (CheetahClock_age_sex.Rmd L181-207) ---
model_list <- vector("list", n)
for (i in seq_len(n)) {
  fit <- glmnet(
    EN_methylation_data[-i, , drop = FALSE], EN_age[-i],
    lambda = best_lambda, alpha = alpha, family = "gaussian"
  )
  model_list[[i]] <- fit
}
mse_values <- vapply(model_list, function(model) {
  pred <- predict(model, newx = EN_methylation_data, type = "response")
  mean((pred - EN_age)^2)
}, numeric(1))
best_model_index <- which.min(mse_values)
best_model_paper <- model_list[[best_model_index]]
pred_trans_paper <- as.numeric(predict(best_model_paper, EN_methylation_data, type = "response"))
pred_age_paper <- age_inv_transform(pred_trans_paper, ASM)

# --- Standard LOOCV (held-out per sample) ---
pred_trans_std <- numeric(n)
for (i in seq_len(n)) {
  fit <- glmnet(
    EN_methylation_data[-i, , drop = FALSE], EN_age[-i],
    lambda = best_lambda, alpha = alpha, family = "gaussian"
  )
  pred_trans_std[i] <- as.numeric(predict(fit, newx = EN_methylation_data[i, , drop = FALSE], type = "response"))
}
pred_age_std <- age_inv_transform(pred_trans_std, ASM)

report_metrics <- function(label, pred_age, pred_trans) {
  err <- meta$Age - pred_age
  r_pearson <- cor(meta$Age, pred_age, method = "pearson")
  mae_median <- median(abs(err))
  rmse_med <- sqrt(median(err^2))  # Rmd variable name MAE_LOOCV
  mse_trans <- mean((pred_trans - EN_age)^2)
  cat("\n---", label, "---\n")
  cat("  Pearson r (calendar age):", round(r_pearson, 4), "\n")
  cat("  MAE (median |error|):", round(mae_median, 4), "years\n")
  cat("  sqrt(median(error^2)) [Rmd MAE_LOOCV]:", round(rmse_med, 4), "\n")
  cat("  MSE (age_trans scale):", round(mse_trans, 4), "\n")
  invisible(list(r = r_pearson, mae = mae_median, rmd_metric = rmse_med))
}

m_paper <- report_metrics("Paper Rmd LOOCV procedure", pred_age_paper, pred_trans_paper)
m_std <- report_metrics("Standard LOOCV", pred_age_std, pred_trans_std)

cat("\n=== Paper reference (CheetahClock training LOOCV) ===\n")
cat("  r ~ 0.97, MAE ~ 0.86 years (reported)\n")

# Full-data model for CpG count
best_model <- glmnet(EN_methylation_data, EN_age, lambda = best_lambda, alpha = alpha, family = "gaussian")
coefs <- as.matrix(coef(best_model))
nz <- setdiff(rownames(coefs)[coefs[, 1] != 0], "(Intercept)")
cat("\nNon-zero CpGs (full data, lambda.min):", length(nz), "(paper: 52)\n")

loocv_df <- data.frame(
  SID = meta$SID, Age = meta$Age, age_trans = meta$age_trans,
  Study = meta$Study, Tissue = meta$Tissue,
  pred_age_paper = pred_age_paper,
  pred_age_standard = pred_age_std,
  stringsAsFactors = FALSE
)
write.csv(loocv_df, file.path(data_dir, "paper_replication_loocv.csv"), row.names = FALSE)

summary_metrics <- data.frame(
  metric = c(
    "n_samples", "n_sdwa_liver", "n_mcdb_blood", "n_cpgs_selected", "lambda_min",
    "paper_rmd_r", "paper_rmd_mae_median", "paper_rmd_sqrt_med_sq",
    "standard_loocv_r", "standard_loocv_mae_median"
  ),
  value = c(
    n, sum(meta$Study == "SDZWA"), sum(meta$Study == "MammCon"), length(nz), best_lambda,
    m_paper$r, m_paper$mae, m_paper$rmd_metric,
    m_std$r, m_std$mae
  )
)
write.csv(summary_metrics, file.path(data_dir, "paper_replication_summary.csv"), row.names = FALSE)

write.csv(meta, file.path(data_dir, "clock_samples.csv"), row.names = TRUE)
write.csv(sva_data, file.path(data_dir, "beta_combat.csv"), row.names = TRUE)

cpg_coefs <- data.frame(
  CpG = nz, Coef = coefs[nz, 1], AbsCoef = abs(coefs[nz, 1]),
  stringsAsFactors = FALSE
)
cpg_coefs <- cpg_coefs[order(-cpg_coefs$AbsCoef), ]
write.csv(cpg_coefs, file.path(data_dir, "selected_cpgs.csv"), row.names = FALSE)

full_coefs <- data.frame(term = rownames(coefs), coef = coefs[, 1], stringsAsFactors = FALSE)
write.csv(full_coefs, file.path(data_dir, "glmnet_coefs_full.csv"), row.names = FALSE)

baseline_loocv <- data.frame(
  SID = meta$SID, GSM = meta$GSM, Age = meta$Age, age_trans = meta$age_trans,
  pred_trans = pred_trans_std, pred_age = pred_age_std,
  Tissue = meta$Tissue, Study = meta$Study, stringsAsFactors = FALSE
)
write.csv(baseline_loocv, file.path(data_dir, "baseline_loocv.csv"), row.names = FALSE)
write.csv(summary_metrics, file.path(data_dir, "baseline_summary.csv"), row.names = FALSE)

cat("\nOutputs written to", data_dir, "\n")
