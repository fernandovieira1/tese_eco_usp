#!/usr/bin/env Rscript
# =============================================================================
# 03_extract_timeseries.R -- series temporais MOD13Q1 das 1.892 amostras
#
# Simoes et al. (2020) extraem 23 observacoes anuais das bandas NDVI, EVI, NIR e
# MIR (92 atributos por amostra) para os 1.892 pontos de `training_dataset_v3.csv`.
# O servico WTSS do INPE usado em 2019 foi descontinuado; este script resolve a
# aquisicao em tres modos:
#
#   1. SIMOES_DEMO=1: usa `sits::samples_modis_ndvi` (as mesmas 1.892 amostras
#      de MT, com a banda NDVI embutida no pacote `sits`) para execucao offline
#      imediata de 04_som_quality_control.R e 05_train_svm.R.
#   2. Pacote legado `inSitu` instalado (`br_mt_1_8K_9classes_6bands`): seleciona
#      as 4 bandas do artigo (NDVI, EVI, NIR, MIR) e salva em `data/processed/`.
#   3. Coleta via STAC no Microsoft Planetary Computer (`MOD13Q1-6.1`) com
#      `sits_cube()` + `sits_get_data()` para as coordenadas/datas do CSV.
#
# Saida:
#   data/processed/[demo_]samples_mt_4bands.rds
#   outputs/tables/table1_training_samples_distribution.csv
#
# Uso:
#   Rscript scripts/03_extract_timeseries.R
#   SIMOES_DEMO=1 Rscript scripts/03_extract_timeseries.R
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("sits", "dplyr", "tibble"))
suppressPackageStartupMessages({library(sits); library(dplyr)})

force <- cli_flag("force")
ensure_dir(DIR$processed)

# ---- Tabela 1 do artigo (distribuicao das 1.892 amostras) -------------------
csv_path <- require_file(
  file.path(DIR$pangaea, "training_dataset_v3.csv"),
  "Rode Rscript scripts/01_download_core.R antes."
)
smp_csv <- utils::read.csv(csv_path, stringsAsFactors = FALSE)

tab1 <- smp_csv |>
  count(label, name = "count") |>
  arrange(label) |>
  mutate(frequency_pct = round(100 * count / sum(count), 1))
write_table(tab1, "table1_training_samples_distribution.csv")

out_rds <- file.path(DIR$processed, paste0(OUT_PREFIX, "samples_mt_4bands.rds"))
if (file.exists(out_rds) && !force) {
  log_msg("ja existe: %s", rel_to(out_rds, ROOT))
  quit(save = "no", status = 0L)
}

# ---- Modo 1: DEMO (offline com sits::samples_modis_ndvi) --------------------
if (DEMO) {
  log_msg("SIMOES_DEMO=1: carregando sits::samples_modis_ndvi (1.892 amostras, banda NDVI)")
  data("samples_modis_ndvi", package = "sits", envir = environment())
  samples_tb <- samples_modis_ndvi
  saveRDS(samples_tb, out_rds)
  log_msg("salvo: %s (%d amostras; bandas: %s)",
          rel_to(out_rds, ROOT), nrow(samples_tb),
          paste(sits_bands(samples_tb), collapse = ", "))
  quit(save = "no", status = 0L)
}

# ---- Modo 2: pacote inSitu (se disponivel localmente) -----------------------
if (requireNamespace("inSitu", quietly = TRUE)) {
  log_msg("Carregando br_mt_1_8K_9classes_6bands do pacote inSitu...")
  e <- new.env(parent = emptyenv())
  utils::data("br_mt_1_8K_9classes_6bands", package = "inSitu", envir = e)
  raw_tb <- e$br_mt_1_8K_9classes_6bands
  b_avail <- sits_bands(raw_tb)
  samples_tb <- sits_select(raw_tb, bands = b_avail[match(BANDS, toupper(b_avail))])
  saveRDS(samples_tb, out_rds)
  log_msg("salvo: %s (%d amostras)", rel_to(out_rds, ROOT), nrow(samples_tb))
  quit(save = "no", status = 0L)
}

# ---- Modo 3: extracao via STAC (Microsoft Planetary Computer, MOD13Q1-6.1) --
log_msg("Extraindo series MOD13Q1-6.1 via MPC para %d amostras...", nrow(smp_csv))
roi_bbox <- c(
  lon_min = min(smp_csv$longitude) - 0.1,
  lat_min = min(smp_csv$latitude)  - 0.1,
  lon_max = max(smp_csv$longitude) + 0.1,
  lat_max = max(smp_csv$latitude)  + 0.1
)
cube <- sits_cube(
  source     = CUBE$source,
  collection = CUBE$collection,
  bands      = BANDS,
  roi        = roi_bbox,
  start_date = min(smp_csv$start_date),
  end_date   = max(smp_csv$end_date)
)
samples_tb <- sits_get_data(
  cube       = cube,
  samples    = csv_path,
  bands      = BANDS,
  multicores = max(1L, parallel::detectCores(logical = FALSE) - 1L)
)
saveRDS(samples_tb, out_rds)
log_msg("salvo: %s (%d amostras)", rel_to(out_rds, ROOT), nrow(samples_tb))
