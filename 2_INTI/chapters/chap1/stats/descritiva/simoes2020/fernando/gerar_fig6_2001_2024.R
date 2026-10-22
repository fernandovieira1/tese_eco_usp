#!/usr/bin/env Rscript
# ==============================================================================
# Script: gerar_fig6_2001_2024.R
# Projeto: Tese de Doutorado — Fernando Souza de Vieira (FEA/USP)
# Diretório: 2_INTI/chapters/chap1/stats/descritiva/simoes2020/fernando/
#
# Objetivo:
#   Gerar uma nova versão atualizada da Figura 6 de Simoes et al. (2020)
#   ("Land use and cover maps for Mato Grosso State in Brazil from 2001 to 2017",
#   Scientific Data, 7, 34), comparando os anos de 2001 e 2024 a partir do
#   catálogo oficial do Google Earth Engine (via `rgee`), com:
#     1. Busca exaustiva no GEE pela coleção consolidada mais recente do
#        MapBiomas Brasil (Coleção 10.1, que inclui 2024) e bloco `tryCatch`
#        com fallback automático para 2023 + `warning()` caso a banda de 2024
#        não esteja disponível no asset consultado.
#     2. Matriz rigorosa de reclassificação (`terra::classify`) para 7 classes
#        consolidadas em português:
#          - 'Soja e Milho' (exclusivamente soja + 2ª safra de grãos/milho)
#          - 'Pecuária' (pastagem)
#          - 'Floresta' (formação florestal primária / alagável)
#          - 'Cerrado' (formação savânica / campestre / áreas úmidas nativas)
#          - 'Área Urbana' (infraestrutura urbana)
#          - 'Áreas Alagadas' (corpos d'água)
#          - 'Outras Culturas' (soja-algodão, soja safra única/pousio,
#            soja-milheto, soja-girassol, cana, algodão safra única,
#            vegetação secundária e todas as demais classes restantes)
#     3. Reprojeção estrita para coordenadas geográficas SIRGAS 2000 (EPSG:4674)
#        removendo a inclinação (~30-40 graus) da projeção Sinusoidal MODIS.
#     4. Sobreposição das fronteiras dos biomas (Amazônia, Cerrado, Pantanal)
#        via `geobr::read_biomes()` com linhas tracejadas (`linetype = "dashed"`)
#        e rótulos posicionados exclusivamente nas bordas externas ao polígono
#        de Mato Grosso.
#     5. Layout facetado (`facet_wrap`) lado a lado (2001 vs. 2024/2023),
#        legenda única em português e tema limpo (`theme_void()`).
# ==============================================================================

suppressPackageStartupMessages({
  library(reticulate)
  library(rgee)
  library(terra)
  library(sf)
  library(geobr)
  library(ggplot2)
  library(ggspatial)
})

sf::sf_use_s2(FALSE)

# ------------------------------------------------------------------------------
# 0. Caminhos e Estrutura de Diretórios
# ------------------------------------------------------------------------------
get_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/")))
  }
  normalizePath(
    "2_INTI/chapters/chap1/stats/descritiva/simoes2020/fernando",
    winslash = "/",
    mustWork = FALSE
  )
}

BASE_DIR <- get_script_dir()
DATA_DIR <- file.path(BASE_DIR, "data")
OUT_DIR  <- file.path(BASE_DIR, "outputs")

for (d in c(BASE_DIR, DATA_DIR, OUT_DIR)) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE, showWarnings = FALSE)
}

cat("======================================================================\n")
cat("  NOVA FIGURA 6 (SIMOES ET AL., 2020) — MATO GROSSO: 2001 vs. 2024\n")
cat("  Diretório do projeto:", BASE_DIR, "\n")
cat("======================================================================\n")

# CRS alvo: SIRGAS 2000 Geográfico (EPSG:4674) — elimina a inclinação Sinusoidal
TARGET_CRS  <- "EPSG:4674"
TARGET_EPSG <- 4674L

# Resolução espacial de download no GEE (500 m preserva as pirâmides nativas do GEE
# com >6 milhões de pixels na grade estadual, ideal para plotagem vetorial/raster em 300 DPI)
GEE_SCALE_M <- 500L
options(timeout = 600)

# ------------------------------------------------------------------------------
# 1. Inicialização do Google Earth Engine (`rgee` / `reticulate`)
# ------------------------------------------------------------------------------
init_gee_session <- function(gee_project = Sys.getenv("GEE_PROJECT", unset = "grand-icon-237222")) {
  # Localiza automaticamente o ambiente Python `.venv` do repositório caso exista
  repo_root_candidates <- c(
    normalizePath(file.path(BASE_DIR, "../../../../../.."), winslash = "/", mustWork = FALSE),
    normalizePath(getwd(), winslash = "/", mustWork = FALSE)
  )
  for (cand in repo_root_candidates) {
    venv_py <- file.path(cand, ".venv", "Scripts", "python.exe")
    if (file.exists(venv_py)) {
      Sys.setenv(RETICULATE_PYTHON = normalizePath(venv_py, winslash = "/"))
      break
    }
  }

  cat(sprintf("[1/6] Inicializando Google Earth Engine via rgee (projeto: %s)...\n", gee_project))
  ee <- reticulate::import("ee")

  tryCatch({
    ee$Initialize(project = gee_project)
    cat("  -> Sessão GEE autenticada e ativa com sucesso.\n")
  }, error = function(e) {
    cat("  -> Tentando rgee::ee_Initialize() padrão...\n")
    rgee::ee_Initialize(drive = FALSE, gcs = FALSE, quiet = TRUE)
  })

  ee
}

ee <- init_gee_session()

# ------------------------------------------------------------------------------
# 2. Aquisição de Limites Vetoriais (Mato Grosso e Biomas via `geobr`)
# ------------------------------------------------------------------------------
cat("[2/6] Carregando limites de Mato Grosso e Biomas via geobr (EPSG:4674)...\n")

mt_state <- tryCatch({
  geobr::read_state(code_state = "MT", year = 2020, showProgress = FALSE)
}, error = function(e) {
  fallback_geojson <- normalizePath(
    file.path(BASE_DIR, "../data/raw/ancillary/mt_boundary.geojson"),
    winslash = "/", mustWork = TRUE
  )
  sf::st_read(fallback_geojson, quiet = TRUE)
})
mt_state <- sf::st_transform(mt_state, TARGET_EPSG)
mt_state <- sf::st_make_valid(mt_state)

biomes_all <- geobr::read_biomes(year = 2019, showProgress = FALSE)
biomes_all <- sf::st_transform(biomes_all, TARGET_EPSG)
biomes_all <- sf::st_make_valid(biomes_all)

target_biomes <- c("Amazônia", "Cerrado", "Pantanal")
biomes_3 <- biomes_all[biomes_all$name_biome %in% target_biomes, ]

# Recorta os polígonos dos biomas para a extensão de Mato Grosso
biomes_mt <- suppressWarnings(sf::st_intersection(biomes_3, sf::st_geometry(mt_state)))
biomes_mt <- sf::st_make_valid(biomes_mt)

# Gera os contornos individuais de cada bioma com um leve recuo interno (-0.018 grau)
# para que as fronteiras tracejadas de biomas vizinhos (Amazônia, Cerrado, Pantanal)
# corram lado a lado com suas respectivas cores sem sobreposição de traços
biomes_mt_buffered <- suppressWarnings(sf::st_buffer(biomes_mt, dist = -0.018))
biomes_mt_lines    <- sf::st_boundary(biomes_mt_buffered)
biomes_mt_lines$name_biome <- factor(
  biomes_mt_lines$name_biome,
  levels = c("Amazônia", "Cerrado", "Pantanal")
)

# Cores específicas para os tracejados e rótulos de cada bioma:
#   - Amazônia : tom de verde escuro florestal (#005824)
#   - Cerrado  : tom de marrom terroso (#7F3B08)
#   - Pantanal : tom de azul profundo (#084594)
BIOME_COLORS <- c(
  "Amazônia" = "#005824",
  "Cerrado"  = "#7F3B08",
  "Pantanal" = "#084594"
)

# Posições dos rótulos dos biomas ESTRITAMENTE DO LADO DE FORA (bordas externas)
# do polígono de Mato Grosso, evitando qualquer obstrução dos pixels internos:
#   - Amazônia: imediatamente acima da fronteira norte reta de MT (sul do Pará)
#   - Cerrado: imediatamente a sudeste/leste da fronteira externa do Cerrado mato-grossense
#   - Pantanal: imediatamente abaixo da fronteira sul do Pantanal mato-grossense
biome_labels_df <- data.frame(
  name_biome  = factor(c("Amazônia", "Cerrado", "Pantanal"), levels = names(BIOME_COLORS)),
  lon         = c(-55.00,     -51.45,    -57.15),
  lat         = c( -9.15,     -16.40,    -18.35),
  biome_color = unname(BIOME_COLORS[c("Amazônia", "Cerrado", "Pantanal")]),
  stringsAsFactors = FALSE
)

# Verificação geométrica rigorosa: nenhum rótulo pode interceptar o interior de MT
pts_check <- sf::st_as_sf(biome_labels_df, coords = c("lon", "lat"), crs = TARGET_EPSG)
is_inside_mt <- lengths(sf::st_intersects(pts_check, mt_state)) > 0
if (any(is_inside_mt)) {
  stop("Erro geométrico: rótulo de bioma posicionado dentro do polígono de Mato Grosso.")
}
cat("  -> Verificação geométrica aprovada: todos os 3 rótulos estão fora do polígono de MT.\n")

# ------------------------------------------------------------------------------
# 3. Busca Exaustiva no Catálogo GEE e Seleção do Ano Alvo (2001 e 2024 / fallback 2023)
# ------------------------------------------------------------------------------
cat("[3/6] Inspecionando catálogo do Google Earth Engine para dados de 2001 e 2024...\n")

# Candidatos oficiais em ordem de prioridade (Coleção 10.1 consolidada possui 1985-2024;
# Coleção 10 possui 1985-2024; Coleção 9 possui 1985-2023)
GEE_COVERAGE_CANDIDATES <- c(
  "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1",
  "projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_coverage_v2",
  "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1"
)

# Assets complementares do MapBiomas no GEE (todos com política de pirâmide MODE):
#  - `soy_corn` (Soja + 2ª safra de grãos/milho) vs `soy_cotton` (Soja + 2ª safra algodão)
#    vs `soy_fallow` (Soja safra única)
#  - `Secondary Vegetation` (Vegetação secundária consolidada: classes 3 e 5 em dsv_v3)
GEE_SECOND_CROP_ASSET <- "projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_agriculture_second_crop_v1"
GEE_SECVEG_DSV_ASSET  <- "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_deforestation_secondary_vegetation_v3"

select_best_gee_collection <- function(ee, candidates) {
  for (asset_id in candidates) {
    info <- tryCatch(ee$Image(asset_id)$bandNames()$getInfo(), error = function(e) NULL)
    if (!is.null(info) && length(info) > 0) {
      cat(sprintf("  -> Asset GEE selecionado: %s (%d bandas: %s a %s)\n",
                  asset_id, length(info), info[1], tail(info, 1)))
      return(list(asset_id = asset_id, bands = as.character(info)))
    }
  }
  stop("Nenhum asset do MapBiomas pôde ser acessado no catálogo do GEE.")
}

selected_cov <- select_best_gee_collection(ee, GEE_COVERAGE_CANDIDATES)

# Função auxiliar para baixar uma banda bruta do GEE rapidamente (usando as pirâmides
# nativas do asset no servidor do GEE) e alinhar à grade de referência
download_single_gee_band <- function(ee, asset_id, band_name, roi_rect, scale_m, dest_tmp) {
  img_full <- ee$Image(asset_id)
  avail    <- as.character(img_full$bandNames()$getInfo())
  if (!(band_name %in% avail)) {
    stop(sprintf("Banda '%s' inexistente no asset GEE '%s'.", band_name, asset_id))
  }
  img_band <- img_full$select(band_name)$toByte()
  dl_url   <- img_band$getDownloadURL(list(
    name   = paste0(gsub("[^A-Za-z0-9_]", "_", basename(asset_id)), "_", band_name),
    region = roi_rect,
    scale  = as.integer(scale_m),
    crs    = TARGET_CRS,
    format = "GEO_TIFF"
  ))
  h <- curl::new_handle(timeout = 600, connecttimeout = 60)
  curl::curl_download(dl_url, destfile = dest_tmp, quiet = TRUE, handle = h)
  terra::rast(dest_tmp)
}

#Matriz de conversão das classes brutas do MapBiomas para os códigos 1..13 de Simoes et al. (2020)
MB_TO_SIMOES13_MATRIX <- matrix(c(
  4,  1,  11, 1,  12, 1,  29, 1,  32, 1,  50, 1, # Cerrado / Formações savânicas e campestres -> 1
  62, 2,                                         # Fallow_Cotton / Algodão safra única -> 2
  3,  3,  5,  3,  6,  3,  49, 3,                 # Forest / Formações florestais -> 3
  15, 4,                                         # Pasture / Pastagem -> 4
  39, 5,                                         # Soybean (refinado abaixo pela 2ª safra) -> 5
  41, 8,                                         # Outras lavouras temporárias / milheto -> 8
  40, 9,  35, 9,  36, 9,  46, 9,  47, 9,  48, 9, # Arroz / girassol / lavouras perenes -> 9
  9,  8,  13, 8,  14, 8,  18, 8,  19, 8,  21, 8, # Silvicultura, mosaico de usos -> 8
  22, 8,  23, 8,  25, 8,  30, 8,  75, 8,         # Outras áreas -> 8
  26, 11, 31, 11, 33, 11,                        # Water / Corpos d'água -> 11
  20, 12,                                        # Sugarcane / Cana-de-açúcar -> 12
  24, 13                                         # Urban Area / Área urbanizada -> 13
), ncol = 2, byrow = TRUE)

# Função para baixar um ano específico do GEE como GeoTIFF em SIRGAS 2000 (EPSG:4674)
download_gee_year_raster <- function(ee, cov_asset_id, year_int, mt_sf, dest_tif, scale_m = 500L) {
  if (file.exists(dest_tif) && file.info(dest_tif)$size > 50000) {
    cat(sprintf("  -> Raster de %d já presente em cache local: %s\n", year_int, basename(dest_tif)))
    return(terra::rast(dest_tif))
  }

  bb <- sf::st_bbox(mt_sf)
  roi_rect <- ee$Geometry$Rectangle(
    coords   = list(as.numeric(bb["xmin"]) - 0.08,
                    as.numeric(bb["ymin"]) - 0.08,
                    as.numeric(bb["xmax"]) + 0.08,
                    as.numeric(bb["ymax"]) + 0.08),
    proj     = "EPSG:4326",
    geodesic = FALSE
  )

  band_cov <- sprintf("classification_%d", year_int)
  band_age <- sprintf("age_%d", year_int)

  cat(sprintf("  -> Baixando banda principal '%s' do GEE (CRS: %s, escala: %d m)...\n",
              band_cov, TARGET_CRS, as.integer(scale_m)))
  tmp_cov <- tempfile(pattern = sprintf("cov_%d_", year_int), fileext = ".tif")
  r_cov   <- download_single_gee_band(ee, cov_asset_id, band_cov, roi_rect, scale_m, tmp_cov)

  # Converte códigos MapBiomas para a base 1..13 de Simoes et al. (2020),
  # preservando 0 e 27 (Não observado / fora do polígono) como NA
  r_cov[r_cov == 0L | r_cov == 27L] <- NA
  r_base13 <- terra::classify(r_cov, rcl = MB_TO_SIMOES13_MATRIX, others = 8L)
  r_base13[is.na(r_cov)] <- NA

  # Refina Soja (39) com a camada oficial de 2ª safra do GEE:
  #   - Soja (39) + 2ª safra grãos/milho (sc == 1)  -> 5 (Soy_Corn)
  #   - Soja (39) + 2ª safra algodão     (sc == 62) -> 6 (Soy_Cotton)
  #   - Soja (39) + sem 2ª safra         (sc == 0)  -> 7 (Soy_Fallow)
  tmp_sc <- tempfile(pattern = sprintf("sc_%d_", year_int), fileext = ".tif")
  tryCatch({
    cat(sprintf("  -> Baixando camada de 2ª safra agrícola (%d) do GEE...\n", year_int))
    r_sc <- download_single_gee_band(ee, GEE_SECOND_CROP_ASSET, band_cov, roi_rect, scale_m, tmp_sc)
    r_sc <- terra::resample(r_sc, r_cov, method = "near")
    r_sc[is.na(r_sc)] <- 0L
    r_base13[r_cov == 39L & r_sc == 1L]  <- 5L
    r_base13[r_cov == 39L & r_sc == 62L] <- 6L
    r_base13[r_cov == 39L & r_sc == 0L]  <- 7L
  }, error = function(e) {
    cat(sprintf("  -> Aviso: camada de 2ª safra não aplicada para %d (%s).\n", year_int, conditionMessage(e)))
  })

  # Refina Vegetação Secundária (10) com a camada oficial categórica (pirâmide MODE)
  # `deforestation_secondary_vegetation_v3` (códigos 3 = Veg. Secundária e 5 = Regeneração)
  tmp_dsv <- tempfile(pattern = sprintf("dsv_%d_", year_int), fileext = ".tif")
  tryCatch({
    cat(sprintf("  -> Baixando camada categórica de vegetação secundária (%d) do GEE...\n", year_int))
    r_dsv <- download_single_gee_band(ee, GEE_SECVEG_DSV_ASSET, band_cov, roi_rect, scale_m, tmp_dsv)
    r_dsv <- terra::resample(r_dsv, r_cov, method = "near")
    r_dsv[is.na(r_dsv)] <- 0L
    r_base13[(r_cov %in% c(3L, 4L, 6L, 12L)) & (r_dsv == 3L | r_dsv == 5L)] <- 10L
  }, error = function(e) {
    cat(sprintf("  -> Aviso: camada de vegetação secundária não aplicada para %d (%s).\n", year_int, conditionMessage(e)))
  })

  # Recorta e mascara estritamente pelo contorno oficial de Mato Grosso em EPSG:4674
  mt_vec <- terra::vect(mt_sf)
  r_crop <- terra::crop(r_base13, mt_vec)
  r_mask <- terra::mask(r_crop, mt_vec, filename = dest_tif, overwrite = TRUE,
                        wopt = list(datatype = "INT1U", NAflag = 255L, gdal = c("COMPRESS=DEFLATE")))
  unlink(c(tmp_cov, tmp_sc, tmp_dsv))
  cat(sprintf("  -> Download e recorte de %d concluídos: %s\n", year_int, basename(dest_tif)))
  terra::rast(dest_tif)
}

# 3.1 Download obrigatório do ano base: 2001
tif_raw_2001 <- file.path(DATA_DIR, "mt_gee_2001_13classes_sirgas2000.tif")
r_raw_2001   <- download_gee_year_raster(
  ee           = ee,
  cov_asset_id = selected_cov$asset_id,
  year_int     = 2001L,
  mt_sf        = mt_state,
  dest_tif     = tif_raw_2001,
  scale_m      = GEE_SCALE_M
)

# 3.2 EXIGÊNCIA: Bloco `tryCatch` para tentar obter 2024 no GEE; caso falhe por
#     inexistência da banda/ano no asset GEE, faz fallback automático para 2023
#     e emite um `warning()` explícito no console do R.
FINAL_YEAR_TARGET <- 2024L
FINAL_YEAR_USED   <- NULL

r_raw_final <- tryCatch({
  tif_2024 <- file.path(DATA_DIR, "mt_gee_2024_13classes_sirgas2000.tif")
  r_24 <- download_gee_year_raster(
    ee           = ee,
    cov_asset_id = selected_cov$asset_id,
    year_int     = 2024L,
    mt_sf        = mt_state,
    dest_tif     = tif_2024,
    scale_m      = GEE_SCALE_M
  )
  FINAL_YEAR_USED <- 2024L
  r_24
}, error = function(e) {
  warning(
    sprintf(
      "Camada consolidada de 2024 não encontrada ou indisponível no asset GEE ('%s': %s). Utilizando fallback automático para o ano de 2023.",
      selected_cov$asset_id, conditionMessage(e)
    ),
    call. = FALSE,
    immediate. = TRUE
  )
  tif_2023 <- file.path(DATA_DIR, "mt_gee_2023_13classes_sirgas2000.tif")
  r_23 <- download_gee_year_raster(
    ee           = ee,
    cov_asset_id = selected_cov$asset_id,
    year_int     = 2023L,
    mt_sf        = mt_state,
    dest_tif     = tif_2023,
    scale_m      = GEE_SCALE_M
  )
  FINAL_YEAR_USED <<- 2023L
  r_23
})

cat(sprintf("  -> Anos efetivamente carregados para comparação: 2001 e %d.\n", FINAL_YEAR_USED))

# ------------------------------------------------------------------------------
# 4. Reprojeção Estrita para Coordenadas Geográficas (SIRGAS 2000 - EPSG:4674)
# ------------------------------------------------------------------------------
cat("[4/6] Verificando/reprojetando rasters e vetores para SIRGAS 2000 (EPSG:4674)...\n")

ensure_sirgas2000_raster <- function(r) {
  if (!terra::same.crs(r, TARGET_CRS)) {
    r <- terra::project(r, TARGET_CRS, method = "near")
  }
  r
}

r_raw_2001  <- ensure_sirgas2000_raster(r_raw_2001)
r_raw_final <- ensure_sirgas2000_raster(r_raw_final)

# ------------------------------------------------------------------------------
# 5. Reclassificação Rigorosa de Uso do Solo (Legenda em Português — 7 Classes)
# ------------------------------------------------------------------------------
cat("[5/6] Aplicando matriz de reclassificação rigorosa (`terra::classify`)...\n")

# Definição das 7 classes consolidadas em português:
#   1 = 'Soja e Milho'   -> EXCLUSIVAMENTE `soy_corn` (5 na legenda Simoes / Soja+2ª safra no MapBiomas)
#   2 = 'Pecuária'       -> `pasture` (4 na legenda Simoes / 15 no MapBiomas)
#   3 = 'Floresta'       -> `forest` (3 na legenda Simoes / 3, 5, 6, 49 no MapBiomas)
#   4 = 'Cerrado'        -> `cerrado` (1 na legenda Simoes / 4, 11, 12 no MapBiomas)
#   5 = 'Área Urbana'    -> `Urban Area` (13 na legenda Simoes / 24 no MapBiomas)
#   6 = 'Áreas Alagadas' -> `Water` (11 na legenda Simoes / 26, 31, 33 no MapBiomas)
#   7 = 'Outras Culturas'-> Agrupa `soy_cotton` (6), `soy_fallow` (7), `soy_millet` (8),
#                           `soy_sunflower` (9), `sugarcane` (12), `Fallow_Cotton` (2),
#                           `Secondary Vegetation` (10) e todas as demais classes restantes
RECLASS_TABLE <- data.frame(
  orig_code   = 1:13,
  orig_label  = c(
    "Cerrado",              # 1
    "Fallow_Cotton",        # 2
    "Forest",               # 3
    "Pasture",              # 4
    "Soy_Corn",             # 5
    "Soy_Cotton",           # 6
    "Soy_Fallow",           # 7
    "Soy_Millet",           # 8
    "Soy_Sunflower",        # 9
    "Secondary Vegetation", # 10
    "Water",                # 11
    "Sugarcane",            # 12
    "Urban Area"            # 13
  ),
  new_code    = c(
    4L, # 1  (Cerrado)              -> 4 ('Cerrado')
    7L, # 2  (Fallow_Cotton)        -> 7 ('Outras Culturas')
    3L, # 3  (Forest)               -> 3 ('Floresta')
    2L, # 4  (Pasture)              -> 2 ('Pecuária')
    1L, # 5  (Soy_Corn)             -> 1 ('Soja e Milho') [EXCLUSIVAMENTE]
    7L, # 6  (Soy_Cotton)           -> 7 ('Outras Culturas')
    7L, # 7  (Soy_Fallow)           -> 7 ('Outras Culturas')
    7L, # 8  (Soy_Millet)           -> 7 ('Outras Culturas')
    7L, # 9  (Soy_Sunflower)        -> 7 ('Outras Culturas')
    7L, # 10 (Secondary Vegetation) -> 7 ('Outras Culturas')
    6L, # 11 (Water)                -> 6 ('Áreas Alagadas')
    7L, # 12 (Sugarcane)            -> 7 ('Outras Culturas')
    5L  # 13 (Urban Area)           -> 5 ('Área Urbana')
  ),
  new_label_pt = c(
    "Cerrado",
    "Outras Culturas",
    "Floresta",
    "Pecuária",
    "Soja e Milho",
    "Outras Culturas",
    "Outras Culturas",
    "Outras Culturas",
    "Outras Culturas",
    "Outras Culturas",
    "Áreas Alagadas",
    "Outras Culturas",
    "Área Urbana"
  ),
  stringsAsFactors = FALSE
)

utils::write.csv(
  RECLASS_TABLE,
  file.path(OUT_DIR, "matriz_reclassificacao.csv"),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)

# Matriz `is-becomes` para `terra::classify()`, com `others = 7L` ('Outras Culturas')
# garantindo que rigorosamente qualquer classe remanescente caia em 'Outras Culturas'
rcl_matrix <- as.matrix(RECLASS_TABLE[, c("orig_code", "new_code")])

PT_CLASSES <- data.frame(
  id    = 1:7,
  label = c(
    "Soja e Milho",
    "Pecuária",
    "Floresta",
    "Cerrado",
    "Área Urbana",
    "Áreas Alagadas",
    "Outras Culturas"
  ),
  color = c(
    "#E66101", # 1: Soja e Milho (laranja/âmbar vibrante)
    "#F4DE9C", # 2: Pecuária (amarelo-palha / pastagem)
    "#1B7837", # 3: Floresta (verde escuro florestal)
    "#8CCD65", # 4: Cerrado (verde claro savânico)
    "#D7191C", # 5: Área Urbana (vermelho intenso)
    "#2B5C8F", # 6: Áreas Alagadas (azul corpos d'água)
    "#B266B2"  # 7: Outras Culturas (lilás/roxo agrícola)
  ),
  stringsAsFactors = FALSE
)

reclassify_lulc <- function(r_in, mt_sf, out_tif) {
  mt_vec <- terra::vect(mt_sf)
  r_in[r_in == 0L | r_in == 255L] <- NA
  r_in   <- terra::mask(terra::crop(r_in, mt_vec), mt_vec)
  r_re   <- terra::classify(r_in, rcl = rcl_matrix, others = 7L)
  r_re[is.na(r_in)] <- NA
  r_re   <- terra::mask(r_re, mt_vec)
  levels(r_re) <- data.frame(id = PT_CLASSES$id, classe_pt = PT_CLASSES$label)
  terra::coltab(r_re) <- data.frame(
    value = PT_CLASSES$id,
    t(grDevices::col2rgb(PT_CLASSES$color)),
    alpha = 255L
  )
  terra::writeRaster(
    r_re,
    filename  = out_tif,
    overwrite = TRUE,
    wopt      = list(datatype = "INT1U", NAflag = 255L, gdal = c("COMPRESS=DEFLATE"))
  )
  terra::rast(out_tif)
}

tif_reclass_2001  <- file.path(DATA_DIR, "mt_reclass_2001_sirgas2000.tif")
tif_reclass_final <- file.path(DATA_DIR, sprintf("mt_reclass_%d_sirgas2000.tif", FINAL_YEAR_USED))

r_2001_pt  <- reclassify_lulc(r_raw_2001,  mt_state, tif_reclass_2001)
r_final_pt <- reclassify_lulc(r_raw_final, mt_state, tif_reclass_final)

# Calcula estatísticas tabulares de área (em hectares, Mha e %) usando `terra::cellSize`
compute_area_table <- function(r_pt, year_int) {
  cell_ha <- terra::cellSize(r_pt, unit = "ha")
  z <- terra::zonal(cell_ha, r_pt, fun = "sum", na.rm = TRUE)
  colnames(z) <- c("class_label", "area_ha")
  df <- merge(
    PT_CLASSES[, c("id", "label")],
    z,
    by.x = "label",
    by.y = "class_label",
    all.x = TRUE
  )
  df$area_ha[is.na(df$area_ha)] <- 0
  df <- df[order(df$id), ]
  df$year      <- year_int
  df$area_Mha  <- round(df$area_ha / 1e6, 4)
  df$pct_state <- round(100 * df$area_ha / sum(df$area_ha), 2)
  df[, c("year", "id", "label", "area_ha", "area_Mha", "pct_state")]
}

tab_areas <- rbind(
  compute_area_table(r_2001_pt, 2001L),
  compute_area_table(r_final_pt, FINAL_YEAR_USED)
)
utils::write.csv(
  tab_areas,
  file.path(OUT_DIR, sprintf("tabela_areas_reclassificadas_2001_%d.csv", FINAL_YEAR_USED)),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)
print(tab_areas[, c("year", "label", "area_Mha", "pct_state")], row.names = FALSE)

# ------------------------------------------------------------------------------
# 6. Construção da Visualização Final (`ggplot2` + `facet_wrap` + `geobr`)
# ------------------------------------------------------------------------------
cat("[6/6] Gerando Figura 6 atualizada (2001 vs. ", FINAL_YEAR_USED, ") em PDF e PNG...\n", sep = "")

# Converte rasters reclassificados em dataframe para plotagem facetada no ggplot2
raster_to_df <- function(r_pt, year_label) {
  # Caso a grade tenha muitos milhões de células, usa agregação modal suave apenas se necessário
  df <- terra::as.data.frame(r_pt, xy = TRUE, na.rm = TRUE)
  colnames(df) <- c("x", "y", "classe_pt")
  df$ano <- as.character(year_label)
  df
}

df_plot <- rbind(
  raster_to_df(r_2001_pt,  "2001"),
  raster_to_df(r_final_pt, as.character(FINAL_YEAR_USED))
)
df_plot$ano <- factor(df_plot$ano, levels = c("2001", as.character(FINAL_YEAR_USED)))

# Ordem lógica na legenda consolidada em português
legend_order <- c(
  "Floresta",
  "Cerrado",
  "Pecuária",
  "Soja e Milho",
  "Outras Culturas",
  "Áreas Alagadas",
  "Área Urbana"
)
df_plot$classe_pt <- factor(df_plot$classe_pt, levels = legend_order)

palette_named <- setNames(PT_CLASSES$color, PT_CLASSES$label)[legend_order]

# Replicar os rótulos externos dos biomas para aparecerem em ambas as facetas (2001 e 2024)
biome_labels_facets <- rbind(
  transform(biome_labels_df, ano = factor("2001", levels = levels(df_plot$ano))),
  transform(biome_labels_df, ano = factor(as.character(FINAL_YEAR_USED), levels = levels(df_plot$ano)))
)

# Segmentos sutis ligando os rótulos externos à borda do respectivo bioma
biome_leader_df <- data.frame(
  name_biome  = factor(c("Amazônia", "Cerrado", "Pantanal"), levels = names(BIOME_COLORS)),
  x           = c(-55.00,     -52.00,    -57.15),
  y           = c( -9.40,     -16.40,    -18.10),
  xend        = c(-55.00,     -52.52,    -57.15),
  yend        = c( -9.85,     -16.40,    -17.75),
  biome_color = unname(BIOME_COLORS[c("Amazônia", "Cerrado", "Pantanal")]),
  stringsAsFactors = FALSE
)
biome_leaders_facets <- rbind(
  transform(biome_leader_df, ano = factor("2001", levels = levels(df_plot$ano))),
  transform(biome_leader_df, ano = factor(as.character(FINAL_YEAR_USED), levels = levels(df_plot$ano)))
)

bb_mt <- sf::st_bbox(mt_state)

p_fig6 <- ggplot() +
  # 1. Pixels reclassificados de Uso e Cobertura do Solo (SIRGAS 2000 - EPSG:4674)
  geom_raster(
    data = df_plot,
    aes(x = x, y = y, fill = classe_pt)
  ) +
  # 2. Contorno externo discreto do Estado de Mato Grosso
  geom_sf(
    data        = mt_state,
    fill        = NA,
    color       = "#333333",
    linewidth   = 0.35,
    inherit.aes = FALSE
  ) +
  # 3. Halo claro sutil sob as fronteiras dos biomas para garantir contraste sobre os pixels
  geom_sf(
    data        = biomes_mt_lines,
    color       = "#FFFFFF",
    alpha       = 0.70,
    linewidth   = 1.15,
    inherit.aes = FALSE,
    show.legend = FALSE
  ) +
  # 4. Fronteiras dos Biomas em linhas tracejadas coloridas conforme o bioma:
  #    Amazônia (verde), Cerrado (marrom) e Pantanal (azul)
  geom_sf(
    data        = biomes_mt_lines,
    aes(color = name_biome),
    linetype    = "dashed",
    linewidth   = 0.72,
    inherit.aes = FALSE,
    show.legend = FALSE
  ) +
  # 5. Rótulos dos biomas posicionados APENAS do lado de fora / bordas externas de MT
  geom_segment(
    data        = biome_leaders_facets,
    aes(x = x, y = y, xend = xend, yend = yend, color = name_biome),
    linewidth   = 0.45,
    linetype    = "dashed",
    inherit.aes = FALSE,
    show.legend = FALSE
  ) +
  geom_label(
    data          = biome_labels_facets,
    aes(x = lon, y = lat, label = name_biome, color = name_biome),
    fontface      = "bold.italic",
    family        = "sans",
    size          = 3.5,
    fill          = "#FFFFFF",
    alpha         = 0.94,
    linewidth     = 0.35,
    label.padding = unit(0.20, "lines"),
    inherit.aes   = FALSE,
    show.legend   = FALSE
  ) +
  scale_color_manual(
    values = BIOME_COLORS,
    guide  = "none"
  ) +
  # 5. Escala gráfica discreta e seta Norte (ggspatial)
  ggspatial::annotation_scale(
    location   = "bl",
    width_hint = 0.22,
    bar_cols   = c("#222222", "#FFFFFF"),
    text_cex   = 0.68,
    line_width = 0.5,
    pad_x      = unit(0.4, "cm"),
    pad_y      = unit(0.3, "cm")
  ) +
  ggspatial::annotation_north_arrow(
    location    = "tl",
    which_north = "true",
    height      = unit(0.85, "cm"),
    width       = unit(0.85, "cm"),
    pad_x       = unit(0.35, "cm"),
    pad_y       = unit(0.35, "cm"),
    style       = ggspatial::north_arrow_fancy_orienteering(
      fill      = c("#FFFFFF", "#222222"),
      line_col  = "#222222",
      text_size = 7
    )
  ) +
  # 6. Paleta de cores consolidada em português (bloco único)
  scale_fill_manual(
    name   = "Uso e Cobertura do Solo",
    values = palette_named,
    drop   = FALSE,
    guide  = guide_legend(
      nrow           = 1,
      byrow          = TRUE,
      title.position = "top",
      title.hjust    = 0.5,
      keywidth       = unit(0.65, "cm"),
      keyheight      = unit(0.42, "cm")
    )
  ) +
  # 7. Coordenadas Geográficas retas (0 grau de inclinação N-S) com margem para os rótulos externos
  coord_sf(
    crs    = TARGET_EPSG,
    xlim   = c(as.numeric(bb_mt["xmin"]) - 0.55, as.numeric(bb_mt["xmax"]) + 1.35),
    ylim   = c(as.numeric(bb_mt["ymin"]) - 0.85, as.numeric(bb_mt["ymax"]) + 0.55),
    expand = FALSE
  ) +
  # 8. Layout facetado lado a lado (2001 vs. 2024/2023)
  facet_wrap(~ ano, ncol = 2) +
  # 9. Tema limpo sem eixos de latitude/longitude e sem gridlines (`theme_void()`)
  theme_void(base_size = 11) +
  theme(
    plot.background  = element_rect(fill = "#FFFFFF", color = NA),
    panel.background = element_rect(fill = "#FFFFFF", color = NA),
    strip.text       = element_text(
      size   = 14,
      face   = "bold",
      color  = "#111111",
      margin = margin(t = 6, b = 6)
    ),
    panel.spacing    = unit(0.8, "cm"),
    legend.position  = "bottom",
    legend.box       = "horizontal",
    legend.title     = element_text(size = 10.5, face = "bold", color = "#111111"),
    legend.text      = element_text(size = 9.5, color = "#222222"),
    legend.margin    = margin(t = 6, b = 4),
    plot.margin      = margin(t = 8, r = 10, b = 8, l = 10)
  )

# Salva nos diretórios `fernando/outputs/` e `fernando/` (raiz do projeto solicitado)
pdf_out_1 <- file.path(OUT_DIR,  sprintf("fig6_uso_solo_mt_2001_%d.pdf", FINAL_YEAR_USED))
png_out_1 <- file.path(OUT_DIR,  sprintf("fig6_uso_solo_mt_2001_%d.png", FINAL_YEAR_USED))
pdf_out_2 <- file.path(BASE_DIR, sprintf("fig6_uso_solo_mt_2001_%d.pdf", FINAL_YEAR_USED))
png_out_2 <- file.path(BASE_DIR, sprintf("fig6_uso_solo_mt_2001_%d.png", FINAL_YEAR_USED))

ggsave(pdf_out_1, plot = p_fig6, width = 12.5, height = 6.8, units = "in", device = "pdf")
ggsave(png_out_1, plot = p_fig6, width = 12.5, height = 6.8, units = "in", dpi = 300, bg = "white")

file.copy(pdf_out_1, pdf_out_2, overwrite = TRUE)
file.copy(png_out_1, png_out_2, overwrite = TRUE)

cat("======================================================================\n")
cat("  CONCLUÍDO COM SUCESSO!\n")
cat("  -> Figura PDF:", pdf_out_2, "\n")
cat("  -> Figura PNG:", png_out_2, "\n")
cat("  -> Tabela CSV:", file.path(OUT_DIR, sprintf("tabela_areas_reclassificadas_2001_%d.csv", FINAL_YEAR_USED)), "\n")
cat("======================================================================\n")

