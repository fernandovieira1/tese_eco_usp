#!/usr/bin/env Rscript
# =============================================================================
# 06_classify_smooth.R -- classificacao de cubos MOD13Q1 + suavizacao Bayesiana
#
# Reproduz as secoes "Image time series classification" e "Local smoothing by
# Bayesian filtering" (Figura 4) de Simoes et al. (2020) usando a API moderna
# do pacote `sits`:
#   sits_cube() -> sits_classify() -> sits_smooth() -> sits_label_classification()
#
# Parametros de suavizacao espacial (Bayesian smoothing):
#   * variancia local (smoothness) sigma^2 = 10 para todas as classes
#   * vizinhanca local de Chebyshev (3x3 no artigo; `sits` >= 1.5 exige
#     `window_size >= 5`, ajustado automaticamente se 3 nao for aceito pela
#     versao instalada do `sits`).
#
# Modos de execucao:
#   * SIMOES_DEMO=1 : classifica e aplica o filtro Bayesiano (sigma^2 = 10) no
#     recorte real MOD13Q1 de Sinop-MT embutido no pacote `sits`
#     (`extdata/raster/mod13q1`), replicando o experimento da Figura 4 do artigo
#     e salvando `outputs/figures/demo_fig4_sinop_smoothing.png`.
#   * Padrao (SIMOES_DEMO=0): classifica os tiles MOD13Q1 de Mato Grosso ano a
#     ano (2001-2017, de 01/set/(Y-1) a 31/ago/Y) via STAC (`MPC` / `MOD13Q1-6.1`),
#     aplica `sits_smooth(smoothness = 10)` + `sits_label_classification()` e
#     gera os mosaicos anuais em `data/processed/classified/mt_smooth_<ano>.tif`.
#
# Uso:
#   SIMOES_DEMO=1 Rscript scripts/06_classify_smooth.R
#   Rscript scripts/06_classify_smooth.R [--years=2001:2017]
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("sits", "terra", "sf"))
suppressPackageStartupMessages({library(sits); library(terra); library(sf)})

ensure_dir(DIR$classified)
model_rds <- require_file(
  file.path(DIR$processed, paste0(OUT_PREFIX, "model_svm.rds")),
  "Rode Rscript scripts/05_train_svm.R antes."
)
model_svm <- readRDS(model_rds)

# Em sits >= 1.5, window_size minimo em sits_smooth() e 5L; se 3L for aceito,
# usa 3L (exatamente a janela 3x3 descrita no artigo), senao usa 5L.
run_smooth <- function(probs_cube, out_dir, version_tag) {
  ws <- SMOOTH$window_size
  res <- tryCatch(
    sits_smooth(
      cube           = probs_cube,
      window_size    = ws,
      neigh_fraction = SMOOTH$neigh_fraction,
      smoothness     = SMOOTH$smoothness,
      memsize        = 4L,
      multicores     = 1L,
      output_dir     = out_dir,
      version        = version_tag,
      progress       = FALSE
    ),
    error = function(e) {
      log_msg("Nota: sits_smooth com window_size=%d retornou '%s'; usando window_size=5L (minimo no sits >= 1.5).",
              ws, conditionMessage(e))
      sits_smooth(
        cube           = probs_cube,
        window_size    = 5L,
        neigh_fraction = SMOOTH$neigh_fraction,
        smoothness     = SMOOTH$smoothness,
        memsize        = 4L,
        multicores     = 1L,
        output_dir     = out_dir,
        version        = version_tag,
        progress       = FALSE
      )
    }
  )
  res
}

# ---- Modo DEMO: recorte MOD13Q1 de Sinop-MT (Figura 4 do artigo) ------------
if (DEMO) {
  log_msg("SIMOES_DEMO=1: classificando cubo MOD13Q1 de Sinop-MT (ilustracao da Fig. 4)")
  data_dir <- system.file("extdata/raster/mod13q1", package = "sits")
  sinop_dir <- ensure_dir(file.path(DIR$classified, "demo_sinop"))
  # Remove artefatos anteriores do mesmo version_tag para idempotencia
  unlink(list.files(sinop_dir, full.names = TRUE))

  sinop_cube <- sits_cube(
    source     = "BDC",
    collection = "MOD13Q1-6.1",
    data_dir   = data_dir,
    progress   = FALSE
  )
  probs_cube <- sits_classify(
    data       = sinop_cube,
    ml_model   = model_svm,
    memsize    = 4L,
    multicores = 1L,
    output_dir = sinop_dir,
    version    = "raw",
    progress   = FALSE
  )
  raw_map <- sits_label_classification(
    cube       = probs_cube,
    memsize    = 4L,
    multicores = 1L,
    output_dir = sinop_dir,
    version    = "raw",
    progress   = FALSE
  )
  smooth_probs <- run_smooth(probs_cube, sinop_dir, "bayes_s10")
  smooth_map <- sits_label_classification(
    cube       = smooth_probs,
    memsize    = 4L,
    multicores = 1L,
    output_dir = sinop_dir,
    version    = "bayes_s10",
    progress   = FALSE
  )

  r_raw    <- terra::rast(raw_map$file_info[[1]]$path[1])
  r_smooth <- terra::rast(smooth_map$file_info[[1]]$path[1])
  pct_diff <- round(100 * mean(terra::values(r_raw) != terra::values(r_smooth), na.rm = TRUE), 2)
  log_msg("Sinop-MT: %.2f%% dos pixels reclassificados pelo filtro Bayesiano (sigma^2 = %g)",
          pct_diff, SMOOTH$smoothness)

  ensure_dir(DIR$figures)
  fig_path <- file.path(DIR$figures, "demo_fig4_sinop_smoothing.png")
  grDevices::png(fig_path, width = 2000, height = 950, res = 220)
  graphics::par(mfrow = c(1, 2), mar = c(2, 2, 3, 4))
  terra::plot(r_raw,    main = "(1) SVM classification (raw)")
  terra::plot(r_smooth, main = sprintf("(2) SVM + Bayesian smoothing (sigma^2 = %g)", SMOOTH$smoothness))
  grDevices::dev.off()
  log_msg("figura salva: %s", rel_to(fig_path, ROOT))
  quit(save = "no", status = 0L)
}

# ---- Modo Completo: Mato Grosso 2001-2017 via STAC (MPC / MOD13Q1-6.1) ------
years <- cli_years()
mt_sf <- sf::st_read(
  require_file(file.path(DIR$ancillary, "mt_boundary.geojson"),
               "Rode Rscript scripts/02_download_reference.R antes."),
  quiet = TRUE
)

# Mapa de traducao dos rotulos do modelo para os codigos oficiais (1..9)
model_labels <- sits_labels(model_svm)
label_to_code <- CLASSES$code[match(model_labels, CLASSES$label)]
stopifnot(!anyNA(label_to_code))

for (yr in years) {
  out_tif <- file.path(DIR$classified, sprintf("mt_smooth_%d.tif", yr))
  if (file.exists(out_tif) && !cli_flag("force")) {
    log_msg("ja existe: %s", rel_to(out_tif, ROOT))
    next
  }
  w <- year_window(yr)
  yr_dir <- ensure_dir(file.path(DIR$classified, sprintf("tiles_%d", yr)))
  log_msg("Classificando ano-safra %d (%s a %s)...", yr, w["start"], w["end"])

  cube_yr <- sits_cube(
    source     = CUBE$source,
    collection = CUBE$collection,
    bands      = BANDS,
    roi        = mt_sf,
    start_date = w["start"],
    end_date   = w["end"],
    progress   = FALSE
  )
  probs_yr <- sits_classify(
    data       = cube_yr,
    ml_model   = model_svm,
    memsize    = 8L,
    multicores = max(1L, parallel::detectCores(logical = FALSE) - 1L),
    output_dir = yr_dir,
    version    = sprintf("v%d", yr),
    progress   = TRUE
  )
  smooth_yr <- run_smooth(probs_yr, yr_dir, sprintf("smooth_%d", yr))
  class_yr  <- sits_label_classification(
    cube       = smooth_yr,
    memsize    = 8L,
    multicores = max(1L, parallel::detectCores(logical = FALSE) - 1L),
    output_dir = yr_dir,
    version    = sprintf("smooth_%d", yr),
    progress   = TRUE
  )

  # Mosaico dos tiles do ano e recodificacao para 1..9 (ordem oficial do QML)
  tile_paths <- vapply(class_yr$file_info, function(fi) fi$path[1], character(1))
  r_list <- lapply(tile_paths, terra::rast)
  r_mos  <- if (length(r_list) == 1L) r_list[[1]] else do.call(terra::merge, r_list)
  if (!identical(seq_along(model_labels), as.integer(label_to_code))) {
    r_mos <- terra::classify(r_mos, cbind(seq_along(model_labels), label_to_code))
  }
  terra::writeRaster(r_mos, out_tif, overwrite = TRUE,
                     datatype = "INT1U", gdal = "COMPRESS=DEFLATE")
  log_msg("mosaico salvo: %s", rel_to(out_tif, ROOT))
}
log_msg("OK. Proximo passo: 07_apply_masks.R")

