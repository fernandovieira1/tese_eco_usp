#!/usr/bin/env Rscript
# =============================================================================
# 08_luc_calculus.R -- pos-processamento temporal via LUC Calculus (2001-2017)
#
# Reproduz os passos 11 a 21 de `main.R` (Zenodo doi:10.5281/zenodo.3354379) e a
# Tabela 4 de Simoes et al. (2020):
#
#   Regras 1-8 (correcao de transicoes impossiveis entre Floresta, Cerrado,
#   Pastagem e Soja, aplicadas sequencialmente de 2001 a 2017):
#     1. C -> F*              ==> C -> C*
#     2. C -> C -> P* -> C    ==> C -> C -> C* -> C
#     3. C -> C -> S* -> C    ==> C -> C -> C* -> C   (S = classes 5..9)
#     4. P -> P -> C* -> C* -> P ==> P -> P -> P* -> P* -> P
#     5. F -> C* -> F -> F    ==> F -> F* -> F -> F
#     6. F -> F -> C* -> F    ==> F -> F -> F* -> F
#     7. F -> C* -> F         ==> F -> F* -> F
#     8. F -> C*              ==> F -> F*
#
#   Regras 9-10 (identificacao de Vegetacao Secundaria, classe 13, via predicados
#   RECUR e EVOLVE do LUC Calculus):
#     9.  F -> F -> P -> F*   ==> F -> F -> P -> SV*
#     10. P -> P -> F* -> P   ==> P -> P -> SV* -> P
#     (Todo pixel classificado como Floresta em t > 2001 que ja apresentou
#      qualquer classe nao-florestal em anos anteriores passa a SV = 13).
#
# Modos de execucao:
#   * SIMOES_DEMO=1: aplica `luc_calculus()` a uma pilha sintetica de 17 rasters
#     (2001-2017) contendo todas as 10 trajetorias da Tabela 4 e salva o
#     diagnostico de transicoes antes/depois em
#     `outputs/tables/demo_luc_transitions_summary.csv`.
#   * Padrao (SIMOES_DEMO=0): processa em blocos de linhas os 17 rasters de
#     `data/processed/masked/mt_masked_<ano>.tif`, grava os mapas finais em
#     `data/processed/final/mt_<ano>.tif` e recorta pelo limite estadual de MT.
#
# Uso:
#   Rscript scripts/08_luc_calculus.R
#   SIMOES_DEMO=1 Rscript scripts/08_luc_calculus.R
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d)
source(file.path(.d, "utils.R"))
source(file.path(.d, "luc_rules.R"))

need_pkgs(c("terra", "sf", "dplyr"))
suppressPackageStartupMessages({library(terra); library(sf); library(dplyr)})
ensure_dir(DIR$final)

# ---- Modo DEMO: pilha sintetica de 17 anos com todas as 10 regras -----------
if (DEMO) {
  log_msg("SIMOES_DEMO=1: aplicando LUC Calculus (regras 1-10 da Tabela 4) em pilha de 17 rasters (2001-2017)")
  nr <- 20L; nc <- 20L; nt <- length(YEARS)
  tmpl <- terra::rast(nrows = nr, ncols = nc, xmin = 0, xmax = 2000, ymin = 0, ymax = 2000,
                      crs = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181 +units=m +no_defs")
  set.seed(SEED)
  M_in <- matrix(sample(c(1L, 3L, 4L, 5L), nr * nc * nt, replace = TRUE,
                        prob = c(0.30, 0.35, 0.25, 0.10)),
                 nrow = nr * nc, ncol = nt)
  # Injeta explicitamente exemplos das regras 1 a 10 nas primeiras linhas
  M_in[1,  1:4] <- c(1L, 3L, 1L, 1L)          # Regra 1: C -> F*
  M_in[2,  1:4] <- c(1L, 1L, 4L, 1L)          # Regra 2: C -> C -> P* -> C
  M_in[3,  1:4] <- c(1L, 1L, 6L, 1L)          # Regra 3: C -> C -> S* -> C
  M_in[4,  1:5] <- c(4L, 4L, 1L, 1L, 4L)      # Regra 4: P -> P -> C* -> C* -> P
  M_in[5,  1:4] <- c(3L, 1L, 3L, 3L)          # Regra 5: F -> C* -> F -> F
  M_in[6,  1:4] <- c(3L, 3L, 1L, 3L)          # Regra 6: F -> F -> C* -> F
  M_in[7,  1:3] <- c(3L, 1L, 3L)              # Regra 7: F -> C* -> F
  M_in[8,  1:2] <- c(3L, 1L)                  # Regra 8: F -> C*
  M_in[9,  1:4] <- c(3L, 3L, 4L, 3L)          # Regra 9: F -> F -> P -> F* => SV
  M_in[10, 1:4] <- c(4L, 4L, 3L, 4L)          # Regra 10: P -> P -> F* -> P => SV

  in_paths  <- file.path(DIR$masked, sprintf("demo_stack_%d.tif", YEARS))
  out_paths <- file.path(DIR$final,  sprintf("demo_mt_%d.tif", YEARS))
  for (t in seq_len(nt)) {
    terra::writeRaster(terra::setValues(tmpl, M_in[, t]), in_paths[t],
                       overwrite = TRUE, datatype = "INT1U")
  }
  process_stack_chunks(in_paths, out_paths, luc_calculus)

  M_out <- vapply(out_paths, function(p) as.integer(terra::values(terra::rast(p), mat = FALSE)),
                  integer(nr * nc))
  summary_luc <- data.frame(
    metric = c("pixels_changed_total",
               "impossible_F_to_C_before", "impossible_F_to_C_after",
               "impossible_C_to_F_before", "impossible_C_to_F_after",
               "secondary_veg_pixels_2017_before", "secondary_veg_pixels_2017_after"),
    value  = c(sum(M_in != M_out),
               sum(M_in[, -nt] == 3L & M_in[, -1] == 1L),
               sum(M_out[, -nt] == 3L & M_out[, -1] == 1L),
               sum(M_in[, -nt] == 1L & M_in[, -1] == 3L),
               sum(M_out[, -nt] == 1L & M_out[, -1] == 3L),
               sum(M_in[, nt] == 13L),
               sum(M_out[, nt] == 13L))
  )
  write_table(summary_luc, "demo_luc_transitions_summary.csv")
  print(summary_luc, row.names = FALSE)
  log_msg("OK (modo DEMO). Mapas sinteticos pos-LUC em data/processed/final/demo_mt_<ano>.tif")
  quit(save = "no", status = 0L)
}

# ---- Modo Completo: 17 rasters (2001-2017) de Mato Grosso -------------------
in_paths  <- vapply(YEARS, function(y) {
  require_file(file.path(DIR$masked, sprintf("mt_masked_%d.tif", y)),
               "Rode Rscript scripts/07_apply_masks.R para todos os anos 2001-2017 antes.")
}, character(1))
out_paths <- vapply(YEARS, replicated_map_path, character(1))

log_msg("Aplicando LUC Calculus (Tabela 4, regras 1-10) na pilha 2001-2017...")
process_stack_chunks(in_paths, out_paths, luc_calculus, datatype = "INT1U")

# Passo 21 de main.R: recorte/mascara final pelo shapefile estadual de MT
mt_sf <- sf::st_read(
  require_file(file.path(DIR$ancillary, "mt_boundary.geojson"),
               "Rode Rscript scripts/02_download_reference.R antes."),
  quiet = TRUE
)
r_ref <- terra::rast(out_paths[1])
mt_v  <- terra::vect(sf::st_transform(mt_sf, terra::crs(r_ref)))

for (p in out_paths) {
  r <- terra::rast(p)
  r_m <- terra::mask(terra::crop(r, mt_v), mt_v)
  tmp <- paste0(p, ".mask.tif")
  terra::writeRaster(r_m, tmp, overwrite = TRUE, datatype = "INT1U", gdal = "COMPRESS=DEFLATE")
  file.rename(tmp, p)
}
log_msg("OK. Mapas finais salvos em data/processed/final/mt_<ano>.tif.")
log_msg("Para rodar 09-11 sobre estes mapas, defina SIMOES_MAPS_SOURCE=replicated.")

