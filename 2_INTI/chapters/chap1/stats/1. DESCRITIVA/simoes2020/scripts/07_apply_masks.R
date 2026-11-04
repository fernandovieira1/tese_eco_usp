#!/usr/bin/env Rscript
# =============================================================================
# 07_apply_masks.R -- aplicacao das mascaras tematicas e regras do mapa-base 2001
#
# Reproduz os passos 4 a 10 de `main.R` (Zenodo doi:10.5281/zenodo.3354379) e a
# Tabela 3 de Simoes et al. (2020):
#
#   Passo 4: Mascara de area urbana (codigo 11) em todos os anos (2001-2017)
#   Passo 5: Mascara de cana-de-acucar Canasat (codigo 10) nos anos 2003-2016
#   Passo 6: Mascara de agua Pekel et al. (codigo 12) em todos os anos (2001-2017)
#   Passos 7-10 (somente ano-base 2001, Tabela 3):
#     * PRODES Amazonia 2001 == Floresta                     -> Floresta (3)
#     * Classificado == Floresta & PRODES == Nao-Floresta    -> Cerrado (1)
#     * Classificado == Floresta & PRODES == Desmatamento    -> Veg. Secundaria (13)
#     * Classificado == Floresta & Cerrado2000 == Nao-Antrop -> Cerrado (1)
#     * Classificado == Floresta & Cerrado2000 == Antropizado-> Veg. Secundaria (13)
#
# As mascaras originais eram distribuidas no pacote `inSitu` (extdata/MT/masks),
# hoje arquivado. Este script procura as mascaras primeiro em `inSitu` (se
# instalado) e depois em `data/raw/masks/` (ver `MASK_FILES` em `config.R`).
#
# Em modo `SIMOES_DEMO=1`, executa um teste sintetico completo das mascaras e
# das regras da Tabela 3 sobre um raster de demonstracao e grava o sumario em
# `outputs/tables/demo_masks_verification.csv`.
#
# Uso:
#   Rscript scripts/07_apply_masks.R [--years=2001:2017]
#   SIMOES_DEMO=1 Rscript scripts/07_apply_masks.R
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d)
source(file.path(.d, "utils.R"))
source(file.path(.d, "luc_rules.R"))

need_pkgs(c("terra"))
suppressPackageStartupMessages(library(terra))
ensure_dir(DIR$masked)

# ---- Modo DEMO: verificacao em raster sintetico -----------------------------
if (DEMO) {
  log_msg("SIMOES_DEMO=1: validando mascaras (passos 4-6) e mapa-base 2001 (Tabela 3) em grade sintetica")
  nr <- 20L; nc <- 20L
  tmpl <- terra::rast(nrows = nr, ncols = nc, xmin = 0, xmax = 2000, ymin = 0, ymax = 2000,
                      crs = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181 +units=m +no_defs")
  set.seed(SEED)
  base_vals <- sample(c(1L, 3L, 4L, 5L, 6L), nr * nc, replace = TRUE)
  # Mascaras sinteticas
  urb <- integer(nr * nc); urb[1:10] <- MASK_FILES$urban$value
  sug <- integer(nr * nc); sug[11:25] <- MASK_FILES$sugarcane_value
  wat <- integer(nr * nc); wat[21:35] <- MASK_FILES$water$value # sobrepoe cana (agua prevalece, passo 6 apos 5)
  pf  <- integer(nr * nc); pf[36:50]  <- MASK_FILES$prodes_forest$value
  pc  <- integer(nr * nc); pc[51:70]  <- MASK_FILES$prodes_2001$nonforest; pc[71:90] <- MASK_FILES$prodes_2001$deforestation
  cc  <- rep(99L, nr * nc); cc[91:110] <- MASK_FILES$cerrado_2000$non_anthropized; cc[111:130] <- MASK_FILES$cerrado_2000$anthropized

  # Aplica ordem exata de main.R: (4) urbano -> (5) cana (2003-2016) -> (6) agua -> (7-10) base 2001
  for (yr in c(2001L, 2005L)) {
    v <- base_vals
    v[urb == MASK_FILES$urban$value] <- CODE$urban
    if (yr %in% MASK_FILES$sugarcane_years) v[sug == MASK_FILES$sugarcane_value] <- CODE$sugarcane
    v[wat == MASK_FILES$water$value] <- CODE$water
    if (yr == 2001L) v <- apply_base_map_rules(v, pf, pc, cc, MASK_FILES)
    r_out <- terra::setValues(tmpl, v)
    terra::writeRaster(r_out, file.path(DIR$masked, sprintf("demo_mt_masked_%d.tif", yr)),
                       overwrite = TRUE, datatype = "INT1U")
  }
  r01 <- terra::rast(file.path(DIR$masked, "demo_mt_masked_2001.tif"))
  r05 <- terra::rast(file.path(DIR$masked, "demo_mt_masked_2005.tif"))
  df_ver <- rbind(
    transform(class_counts(r01), year = 2001L),
    transform(class_counts(r05), year = 2005L)
  )
  write_table(df_ver, "demo_masks_verification.csv")
  log_msg("OK (modo DEMO). Proximo passo: SIMOES_DEMO=1 Rscript scripts/08_luc_calculus.R")
  quit(save = "no", status = 0L)
}

# ---- Localiza mascaras (inSitu ou data/raw/masks) ---------------------------
find_mask <- function(rel_insitu, local_path) {
  if (requireNamespace("inSitu", quietly = TRUE)) {
    p <- system.file(rel_insitu, package = "inSitu")
    if (nzchar(p) && file.exists(p)) return(p)
  }
  require_file(
    local_path,
    paste0("Mascara ausente. Forneca em ", rel_to(local_path, ROOT),
           " ou instale o pacote legado `e-sensing/inSitu`.")
  )
}

m_urban <- terra::rast(find_mask("extdata/MT/masks/urban_area.tif",
                                 file.path(DIR$masks, MASK_FILES$urban$file)))
m_water <- terra::rast(find_mask("extdata/MT/masks/water.tif",
                                 file.path(DIR$masks, MASK_FILES$water$file)))

years <- cli_years()
for (yr in years) {
  in_tif <- require_file(
    file.path(DIR$classified, sprintf("mt_smooth_%d.tif", yr)),
    "Rode Rscript scripts/06_classify_smooth.R antes."
  )
  out_tif <- file.path(DIR$masked, sprintf("mt_masked_%d.tif", yr))
  if (file.exists(out_tif) && !cli_flag("force")) {
    log_msg("ja existe: %s", rel_to(out_tif, ROOT))
    next
  }

  r <- terra::crop(terra::rast(in_tif), m_urban)
  in_list <- list(r, m_urban, m_water)
  has_sug <- yr %in% MASK_FILES$sugarcane_years
  if (has_sug) {
    sug_p <- find_mask(
      sprintf("extdata/MT/masks/sugarcane/canasat_%d.tif", yr),
      file.path(DIR$masks, MASK_FILES$sugarcane_dir, sprintf("canasat_%d.tif", yr))
    )
    in_list[[length(in_list) + 1L]] <- terra::rast(sug_p)
  }
  is_2001 <- yr == 2001L
  if (is_2001) {
    in_list[[length(in_list) + 1L]] <- terra::rast(find_mask(
      "extdata/MT/masks/PRODES_2001_forest.tif",
      file.path(DIR$masks, MASK_FILES$prodes_forest$file)))
    in_list[[length(in_list) + 1L]] <- terra::rast(find_mask(
      "extdata/MT/masks/PRODES_2001.tif",
      file.path(DIR$masks, MASK_FILES$prodes_2001$file)))
    in_list[[length(in_list) + 1L]] <- terra::rast(find_mask(
      "extdata/MT/masks/PRODES-Cerrado_2000.tif",
      file.path(DIR$masks, MASK_FILES$cerrado_2000$file)))
  }

  in_paths <- vapply(in_list, function(x) terra::sources(x)[1], character(1))
  process_stack_chunks(in_paths, out_tif, function(M) {
    x <- M[, 1]
    u <- M[, 2]
    w <- M[, 3]
    col_i <- 4L
    # Passo 4: Area Urbana (11)
    x[which(u == MASK_FILES$urban$value)] <- CODE$urban
    # Passo 5: Cana-de-acucar (10) em 2003-2016
    if (has_sug) {
      s <- M[, col_i]; col_i <- col_i + 1L
      x[which(s == MASK_FILES$sugarcane_value)] <- CODE$sugarcane
    }
    # Passo 6: Agua (12)
    x[which(w == MASK_FILES$water$value)] <- CODE$water
    # Passos 7-10: Regras do mapa-base 2001 (Tabela 3)
    if (is_2001) {
      pf <- M[, col_i]; pc <- M[, col_i + 1L]; cc <- M[, col_i + 2L]
      x <- apply_base_map_rules(x, pf, pc, cc, MASK_FILES)
    }
    matrix(x, ncol = 1L)
  })
  log_msg("mascaras aplicadas (%d): %s", yr, rel_to(out_tif, ROOT))
}
log_msg("OK. Proximo passo: 08_luc_calculus.R")

