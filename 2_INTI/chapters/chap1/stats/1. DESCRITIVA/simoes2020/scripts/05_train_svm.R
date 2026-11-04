#!/usr/bin/env Rscript
# =============================================================================
# 05_train_svm.R -- treinamento do classificador SVM (kernel RBF) e validacao
#
# Reproduz a secao "Image time series classification" e a Tabela 5 de
# Simoes et al. (2020) usando `sits_train()` + `sits_svm()` e validacao cruzada
# em 5 folds (`sits_kfold_validate()`):
#
#   * Kernel: Radial Basis Function (`kernel = "radial"`)
#   * Custo : `cost = 1`
#   * Gamma : `1 / n_features` (para 4 bandas x 23 datas: `gamma = 1/92 = 0.01086957`,
#             exatamente o valor documentado no PANGAEA e no artigo; em modo DEMO
#             com 1 banda x 23 datas: `gamma = 1/23`).
#   * Formula: `sits_formula_linear()` (como em `main.R` do Zenodo).
#
# Saidas:
#   data/processed/[demo_]model_svm.rds
#   outputs/tables/[demo_]table5_cv_accuracy.csv
#   outputs/tables/[demo_]table5_confusion_matrix.csv
#
# Uso:
#   Rscript scripts/05_train_svm.R
#   SIMOES_DEMO=1 Rscript scripts/05_train_svm.R
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("sits", "e1071", "dplyr", "tibble"))
suppressPackageStartupMessages({library(sits); library(dplyr)})

in_rds <- file.path(DIR$processed, paste0(OUT_PREFIX, "samples_mt_clean.rds"))
if (!file.exists(in_rds)) {
  in_rds <- require_file(
    file.path(DIR$processed, paste0(OUT_PREFIX, "samples_mt_4bands.rds")),
    "Rode 03_extract_timeseries.R (e opcionalmente 04_som_quality_control.R) antes."
  )
}
samples_tb <- readRDS(in_rds)

bands_used <- sits_bands(samples_tb)
n_steps    <- nrow(samples_tb$time_series[[1]])
n_features <- length(bands_used) * n_steps
gamma_val  <- 1 / n_features

log_msg("Treinando SVM RBF | amostras: %d | bandas: %s | features: %d | C = %g | gamma = %.8f",
        nrow(samples_tb), paste(bands_used, collapse = ","),
        n_features, SVM$cost, gamma_val)

set.seed(SEED)
ml_method <- sits_svm(
  formula = sits_formula_linear(),
  kernel  = SVM$kernel,
  cost    = SVM$cost,
  gamma   = gamma_val,
  scale   = FALSE
)

model_svm <- sits_train(samples = samples_tb, ml_method = ml_method)
out_model <- file.path(DIR$processed, paste0(OUT_PREFIX, "model_svm.rds"))
saveRDS(model_svm, out_model)
log_msg("modelo salvo: %s", rel_to(out_model, ROOT))

# ---- Validacao cruzada de 5 folds (Tabela 5 do artigo) ----------------------
log_msg("Executando validacao cruzada de %d folds...", SVM$folds)
set.seed(SEED)
cv_res <- sits_kfold_validate(
  samples    = samples_tb,
  folds      = SVM$folds,
  ml_method  = ml_method,
  multicores = 1L
)

# Extrai matriz de confusao e acuracias do usuario (UA) e do produtor (PA)
cm <- cv_res$table
cm_df <- as.data.frame.matrix(cm)
cm_df <- tibble::rownames_to_column(cm_df, var = "predicted_or_row")
write_table(cm_df, paste0(OUT_PREFIX, "table5_confusion_matrix.csv"))

# Valores oficiais reportados na Tabela 5 do artigo (4 bandas: NDVI, EVI, NIR, MIR)
paper_tab5 <- tibble::tribble(
  ~class,          ~paper_user_acc, ~paper_prod_acc,
  "Cerrado",                  0.98,            0.99,
  "Fallow_Cotton",            0.96,            0.93,
  "Forest",                   0.99,            0.98,
  "Pasture",                  0.97,            0.98,
  "Soy_Corn",                 0.91,            0.93,
  "Soy_Cotton",               0.97,            0.97,
  "Soy_Fallow",               0.98,            0.98,
  "Soy_Millet",               0.90,            0.89,
  "Soy_Sunflower",            0.88,            0.73
)

diag_v <- diag(cm)
row_s  <- rowSums(cm)
col_s  <- colSums(cm)
# Em sits_kfold_validate (caret::confusionMatrix): linhas = Predito, colunas = Referencia
ua <- diag_v / row_s
pa <- diag_v / col_s
overall_acc <- sum(diag_v) / sum(cm)

acc_df <- tibble::tibble(
  class        = names(diag_v),
  user_acc     = round(as.numeric(ua), 4),
  prod_acc     = round(as.numeric(pa), 4),
  overall_acc  = round(overall_acc, 4),
  bands_used   = paste(bands_used, collapse = "+")
) |>
  left_join(paper_tab5, by = "class") |>
  arrange(class)

write_table(acc_df, paste0(OUT_PREFIX, "table5_cv_accuracy.csv"))
log_msg("Acuracia global (%d-fold CV): %.2f%% (artigo com 4 bandas: 96%%)",
        SVM$folds, 100 * overall_acc)
print(acc_df, n = Inf)
log_msg("OK. Proximo passo: 06_classify_smooth.R")

