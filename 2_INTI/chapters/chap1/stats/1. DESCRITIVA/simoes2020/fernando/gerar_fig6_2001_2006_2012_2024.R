#!/usr/bin/env Rscript
# ==============================================================================
# Script: gerar_fig6_2001_2006_2012_2024.R
# Projeto: Tese de Doutorado — Fernando Souza de Vieira (FEA/USP)
# Diretório: 2_INTI/chapters/chap1/stats/1. DESCRITIVA/simoes2020/fernando/
#
# Objetivo:
#   Estender a Figura 1 do capítulo (baseada em Simoes et al., 2020 / MapBiomas
#   Coleção 10.1) para quatro recortes em arranjo 2x2 (ordem de leitura em Z):
#     - Superior esquerdo (L1C1): (a) 2001 (início do painel)
#     - Superior direito  (L1C2): (b) 2006 (Moratória da Soja)
#     - Inferior esquerdo (L2C1): (c) 2012 (Código Florestal)
#     - Inferior direito  (L2C2): (d) 2024 (período final)
#   Utiliza os rasters em cache de 2001 e 2024 e baixa 2006 e 2012 dos mesmos
#   assets oficiais do MapBiomas via GEE (EPSG:4674, escala 500 m).
# ==============================================================================

suppressPackageStartupMessages({
  library(reticulate)
  library(terra)
  library(sf)
  library(geobr)
  library(ggplot2)
  library(ggspatial)
  library(patchwork)
})

sf::sf_use_s2(FALSE)

get_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/")))
  }
  normalizePath(
    "2_INTI/chapters/chap1/stats/1. DESCRITIVA/simoes2020/fernando",
    winslash = "/",
    mustWork = FALSE
  )
}

BASE_DIR   <- get_script_dir()
DATA_DIR   <- file.path(BASE_DIR, "data")
LOCAL_OUT  <- file.path(BASE_DIR, "outputs")
AUDIT_OUT  <- normalizePath(file.path(BASE_DIR, "../../../../../../audit/readequacao_artigo1_20261112/saidas/mapa_fig6"),
                            winslash = "/", mustWork = FALSE)
TEXT_FIG   <- normalizePath(file.path(BASE_DIR, "../../../..", "text/figuras"),
                            winslash = "/", mustWork = FALSE)

for (d in c(BASE_DIR, DATA_DIR, LOCAL_OUT, AUDIT_OUT, TEXT_FIG)) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE, showWarnings = FALSE)
}

TARGET_CRS  <- "EPSG:4674"
TARGET_EPSG <- 4674L
GEE_SCALE_M <- 500L
options(timeout = 600)

YEARS_TARGET <- c(2001L, 2006L, 2012L, 2024L)

cat("======================================================================\n")
cat("  FIGURA 1 (2x2): MT 2001, 2006, 2012 e 2024\n")
cat("======================================================================\n")

# ------------------------------------------------------------------------------
# 1. Inicialização GEE (apenas se faltar algum raster bruto no cache local)
# ------------------------------------------------------------------------------
init_gee_session <- function(gee_project = Sys.getenv("GEE_PROJECT", unset = "grand-icon-237222")) {
  repo_root_candidates <- c(
    normalizePath(file.path(BASE_DIR, "../../../../../../.."), winslash = "/", mustWork = FALSE),
    normalizePath(getwd(), winslash = "/", mustWork = FALSE)
  )
  for (cand in repo_root_candidates) {
    venv_py <- file.path(cand, ".venv", "Scripts", "python.exe")
    if (file.exists(venv_py)) {
      Sys.setenv(RETICULATE_PYTHON = normalizePath(venv_py, winslash = "/"))
      break
    }
  }
  cat(sprintf("[1/6] Inicializando Google Earth Engine (projeto: %s)...\n", gee_project))
  ee <- reticulate::import("ee")
  ee$Initialize(project = gee_project)
  cat("  -> Sessão GEE autenticada.\n")
  ee
}

raw_paths <- setNames(
  file.path(DATA_DIR, sprintf("mt_gee_%d_13classes_sirgas2000.tif", YEARS_TARGET)),
  as.character(YEARS_TARGET)
)
all_cached <- all(file.exists(raw_paths) & file.info(raw_paths)$size > 50000)

ee <- if (all_cached) {
  cat("[1/6] Todos os 4 rasters brutos já estão em cache local; GEE dispensado.\n")
  NULL
} else {
  init_gee_session()
}

# ------------------------------------------------------------------------------
# 2. Limites vetoriais de Mato Grosso e Biomas (`geobr`)
# ------------------------------------------------------------------------------
cat("[2/6] Carregando limites de Mato Grosso e Biomas (EPSG:4674)...\n")

mt_state <- tryCatch({
  geobr::read_state(code_state = "MT", year = 2020, showProgress = FALSE)
}, error = function(e) {
  fallback_geojson <- normalizePath(
    file.path(BASE_DIR, "../data/raw/ancillary/mt_boundary.geojson"),
    winslash = "/", mustWork = TRUE
  )
  sf::st_read(fallback_geojson, quiet = TRUE)
})
mt_state <- sf::st_make_valid(sf::st_transform(mt_state, TARGET_EPSG))

biomes_all <- sf::st_make_valid(sf::st_transform(geobr::read_biomes(year = 2019, showProgress = FALSE), TARGET_EPSG))
target_biomes <- c("Amazônia", "Cerrado", "Pantanal")
biomes_3  <- biomes_all[biomes_all$name_biome %in% target_biomes, ]
biomes_mt <- sf::st_make_valid(suppressWarnings(sf::st_intersection(biomes_3, sf::st_geometry(mt_state))))

biomes_mt_buffered <- suppressWarnings(sf::st_buffer(biomes_mt, dist = -0.018))
biomes_mt_lines    <- sf::st_boundary(biomes_mt_buffered)
biomes_mt_lines$name_biome <- factor(biomes_mt_lines$name_biome, levels = target_biomes)

BIOME_COLORS <- c(
  "Amazônia" = "#005824",
  "Cerrado"  = "#7F3B08",
  "Pantanal" = "#084594"
)

biome_labels_df <- data.frame(
  name_biome  = factor(target_biomes, levels = names(BIOME_COLORS)),
  lon         = c(-55.00, -51.45, -57.15),
  lat         = c( -9.15, -16.40, -18.35),
  biome_color = unname(BIOME_COLORS[target_biomes]),
  stringsAsFactors = FALSE
)

pts_check <- sf::st_as_sf(biome_labels_df, coords = c("lon", "lat"), crs = TARGET_EPSG)
if (any(lengths(sf::st_intersects(pts_check, mt_state)) > 0)) {
  stop("Erro geométrico: rótulo de bioma posicionado dentro do polígono de MT.")
}

biome_leader_df <- data.frame(
  name_biome  = factor(target_biomes, levels = names(BIOME_COLORS)),
  x           = c(-55.00, -52.00, -57.15),
  y           = c( -9.40, -16.40, -18.10),
  xend        = c(-55.00, -52.52, -57.15),
  yend        = c( -9.85, -16.40, -17.75),
  biome_color = unname(BIOME_COLORS[target_biomes]),
  stringsAsFactors = FALSE
)

# ------------------------------------------------------------------------------
# 3. Aquisição GEE idêntica à do script base (2001, 2006, 2012, 2024)
# ------------------------------------------------------------------------------
cat("[3/6] Carregando / baixando camadas MapBiomas Coleção 10.1 (500 m)...\n")

COV_ASSET     <- "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"
SECOND_ASSET  <- "projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_agriculture_second_crop_v1"
SECVEG_ASSET  <- "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_deforestation_secondary_vegetation_v3"

MB_TO_SIMOES13_MATRIX <- matrix(c(
  4,  1,  11, 1,  12, 1,  29, 1,  32, 1,  50, 1,
  62, 2,
  3,  3,  5,  3,  6,  3,  49, 3,
  15, 4,
  39, 5,
  41, 8,
  40, 9,  35, 9,  36, 9,  46, 9,  47, 9,  48, 9,
  9,  8,  13, 8,  14, 8,  18, 8,  19, 8,  21, 8,
  22, 8,  23, 8,  25, 8,  30, 8,  75, 8,
  26, 11, 31, 11, 33, 11,
  20, 12,
  24, 13
), ncol = 2, byrow = TRUE)

download_single_gee_band <- function(ee, asset_id, band_name, roi_rect, scale_m, dest_tmp) {
  img_full <- ee$Image(asset_id)
  avail    <- as.character(img_full$bandNames()$getInfo())
  if (!(band_name %in% avail)) {
    stop(sprintf("Banda '%s' inexistente no asset '%s'.", band_name, asset_id))
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

download_gee_year_raster <- function(ee, year_int, mt_sf, dest_tif, ref_rast = NULL, scale_m = 500L) {
  if (file.exists(dest_tif) && file.info(dest_tif)$size > 50000) {
    cat(sprintf("  -> Cache local encontrado para %d: %s\n", year_int, basename(dest_tif)))
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

  cat(sprintf("  -> Baixando '%s' (%d)...\n", band_cov, year_int))
  tmp_cov <- tempfile(pattern = sprintf("cov_%d_", year_int), fileext = ".tif")
  r_cov   <- download_single_gee_band(ee, COV_ASSET, band_cov, roi_rect, scale_m, tmp_cov)
  if (!is.null(ref_rast) && !terra::compareGeom(r_cov, ref_rast, stopOnError = FALSE)) {
    r_cov <- terra::resample(r_cov, ref_rast, method = "near")
  }
  r_cov[r_cov == 0L | r_cov == 27L] <- NA
  r_base13 <- terra::classify(r_cov, rcl = MB_TO_SIMOES13_MATRIX, others = 8L)
  r_base13[is.na(r_cov)] <- NA

  tmp_sc <- tempfile(pattern = sprintf("sc_%d_", year_int), fileext = ".tif")
  cat(sprintf("  -> Baixando 2ª safra (%d)...\n", year_int))
  r_sc <- download_single_gee_band(ee, SECOND_ASSET, band_cov, roi_rect, scale_m, tmp_sc)
  r_sc <- terra::resample(r_sc, r_cov, method = "near")
  r_sc[is.na(r_sc)] <- 0L
  r_base13[r_cov == 39L & r_sc == 1L]  <- 5L
  r_base13[r_cov == 39L & r_sc == 62L] <- 6L
  r_base13[r_cov == 39L & r_sc == 0L]  <- 7L

  tmp_dsv <- tempfile(pattern = sprintf("dsv_%d_", year_int), fileext = ".tif")
  cat(sprintf("  -> Baixando vegetação secundária (%d)...\n", year_int))
  r_dsv <- download_single_gee_band(ee, SECVEG_ASSET, band_cov, roi_rect, scale_m, tmp_dsv)
  r_dsv <- terra::resample(r_dsv, r_cov, method = "near")
  r_dsv[is.na(r_dsv)] <- 0L
  r_base13[(r_cov %in% c(3L, 4L, 6L, 12L)) & (r_dsv == 3L | r_dsv == 5L)] <- 10L

  mt_vec <- terra::vect(mt_sf)
  r_crop <- terra::crop(r_base13, mt_vec)
  terra::mask(r_crop, mt_vec, filename = dest_tif, overwrite = TRUE,
              wopt = list(datatype = "INT1U", NAflag = 255L, gdal = c("COMPRESS=DEFLATE")))
  unlink(c(tmp_cov, tmp_sc, tmp_dsv))
  cat(sprintf("  -> Concluído %d: %s\n", year_int, basename(dest_tif)))
  terra::rast(dest_tif)
}

r_2001_raw <- terra::rast(raw_paths[["2001"]])
raw_list <- lapply(YEARS_TARGET, function(yr) {
  download_gee_year_raster(ee, yr, mt_state, raw_paths[[as.character(yr)]], ref_rast = r_2001_raw, scale_m = GEE_SCALE_M)
})
names(raw_list) <- as.character(YEARS_TARGET)

# ------------------------------------------------------------------------------
# 4. Reclassificação para as 7 classes (legenda vigente: "Outros usos e coberturas")
# ------------------------------------------------------------------------------
cat("[4/6] Reclassificando os 4 anos para as 7 classes em português...\n")

RECLASS_TABLE <- data.frame(
  orig_code = 1:13,
  new_code  = c(4L, 7L, 3L, 2L, 1L, 7L, 7L, 7L, 7L, 7L, 6L, 7L, 5L)
)
rcl_matrix <- as.matrix(RECLASS_TABLE)

PT_CLASSES <- data.frame(
  id    = 1:7,
  label = c(
    "Soja e Milho",
    "Pecuária",
    "Floresta",
    "Cerrado",
    "Área Urbana",
    "Áreas Alagadas",
    "Outros usos e coberturas"
  ),
  color = c(
    "#E66101",
    "#F4DE9C",
    "#1B7837",
    "#8CCD65",
    "#D7191C",
    "#2B5C8F",
    "#B266B2"
  ),
  stringsAsFactors = FALSE
)

reclassify_lulc <- function(r_in, mt_sf, out_tif) {
  if (!terra::same.crs(r_in, TARGET_CRS)) {
    r_in <- terra::project(r_in, TARGET_CRS, method = "near")
  }
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
    r_re, filename = out_tif, overwrite = TRUE,
    wopt = list(datatype = "INT1U", NAflag = 255L, gdal = c("COMPRESS=DEFLATE"))
  )
  terra::rast(out_tif)
}

reclass_list <- lapply(names(raw_list), function(yr_str) {
  out_tif <- file.path(AUDIT_OUT, sprintf("mt_reclass_%s_sirgas2000.tif", yr_str))
  reclassify_lulc(raw_list[[yr_str]], mt_state, out_tif)
})
names(reclass_list) <- names(raw_list)

# ------------------------------------------------------------------------------
# 5. Cálculo das áreas por classe nos 4 recortes
# ------------------------------------------------------------------------------
cat("[5/6] Calculando tabela de áreas reclassificadas (2001, 2006, 2012, 2024)...\n")

compute_area_table <- function(r_pt, year_int) {
  cell_ha <- terra::cellSize(r_pt, unit = "ha")
  z <- terra::zonal(cell_ha, r_pt, fun = "sum", na.rm = TRUE)
  colnames(z) <- c("class_label", "area_ha")
  df <- merge(PT_CLASSES[, c("id", "label")], z, by.x = "label", by.y = "class_label", all.x = TRUE)
  df$area_ha[is.na(df$area_ha)] <- 0
  df <- df[order(df$id), ]
  df$year      <- year_int
  df$area_Mha  <- round(df$area_ha / 1e6, 4)
  df$pct_state <- round(100 * df$area_ha / sum(df$area_ha), 2)
  df[, c("year", "id", "label", "area_ha", "area_Mha", "pct_state")]
}

tab_areas_4 <- do.call(rbind, lapply(YEARS_TARGET, function(yr) {
  compute_area_table(reclass_list[[as.character(yr)]], yr)
}))

for (d in c(LOCAL_OUT, AUDIT_OUT)) {
  utils::write.csv(
    tab_areas_4,
    file.path(d, "tabela_areas_reclassificadas_2001_2006_2012_2024.csv"),
    row.names = FALSE, fileEncoding = "UTF-8"
  )
}
print(tab_areas_4[, c("year", "label", "area_Mha", "pct_state")], row.names = FALSE)

# ------------------------------------------------------------------------------
# 6. Mapa 2x2 em sentido horário com painel (a) limpo
#    Superior esq.: (a) 2001
#    Superior dir.: (b) 2006 (Moratória da Soja)
#    Inferior dir.: (c) 2012 (Código Florestal)
#    Inferior esq.: (d) 2024
# ------------------------------------------------------------------------------
cat("[6/6] Gerando figura 2x2 em sentido horário (PDF e PNG)...\n")

legend_order <- c(
  "Floresta",
  "Cerrado",
  "Pecuária",
  "Soja e Milho",
  "Outros usos e coberturas",
  "Áreas Alagadas",
  "Área Urbana"
)
palette_named <- setNames(PT_CLASSES$color, PT_CLASSES$label)[legend_order]
bb_mt <- sf::st_bbox(mt_state)

xlim_shared <- c(as.numeric(bb_mt["xmin"]) - 0.55, as.numeric(bb_mt["xmax"]) + 1.35)
ylim_shared <- c(as.numeric(bb_mt["ymin"]) - 0.85, as.numeric(bb_mt["ymax"]) + 0.55)

build_map_panel <- function(r_pt, panel_title) {
  df <- terra::as.data.frame(r_pt, xy = TRUE, na.rm = TRUE)
  colnames(df) <- c("x", "y", "classe_pt")
  df$classe_pt <- factor(df$classe_pt, levels = legend_order)

  ggplot() +
    geom_raster(data = df, aes(x = x, y = y, fill = classe_pt)) +
    geom_sf(data = mt_state, fill = NA, color = "#333333", linewidth = 0.30, inherit.aes = FALSE) +
    geom_sf(data = biomes_mt_lines, color = "#FFFFFF", alpha = 0.70, linewidth = 1.0,
            inherit.aes = FALSE, show.legend = FALSE) +
    geom_sf(data = biomes_mt_lines, aes(color = name_biome), linetype = "dashed", linewidth = 0.65,
            inherit.aes = FALSE, show.legend = FALSE) +
    geom_segment(
      data = biome_leader_df,
      aes(x = x, y = y, xend = xend, yend = yend, color = name_biome),
      linewidth = 0.42, linetype = "dashed", inherit.aes = FALSE, show.legend = FALSE
    ) +
    geom_label(
      data = biome_labels_df,
      aes(x = lon, y = lat, label = name_biome, color = name_biome),
      fontface = "bold.italic", family = "sans", size = 3.1,
      fill = "#FFFFFF", alpha = 0.94, linewidth = 0.30,
      label.padding = unit(0.18, "lines"), inherit.aes = FALSE, show.legend = FALSE
    ) +
    scale_color_manual(values = BIOME_COLORS, guide = "none") +
    scale_fill_manual(
      name   = "Uso e Cobertura do Solo",
      values = palette_named,
      drop   = FALSE,
      guide  = guide_legend(
        nrow = 1, byrow = TRUE, title.position = "top", title.hjust = 0.5,
        keywidth = unit(0.60, "cm"), keyheight = unit(0.38, "cm")
      )
    ) +
    coord_sf(crs = TARGET_EPSG, xlim = xlim_shared, ylim = ylim_shared, expand = FALSE) +
    labs(title = panel_title) +
    theme_void(base_size = 10.5) +
    theme(
      plot.background  = element_rect(fill = "#FFFFFF", color = NA),
      panel.background = element_rect(fill = "#FFFFFF", color = NA),
      plot.title       = element_text(size = 11.5, face = "bold", color = "#111111", hjust = 0.5,
                                      margin = margin(t = 2, b = 3)),
      plot.margin      = margin(t = 3, r = 4, b = 3, l = 4)
    )
}

p_2001 <- build_map_panel(reclass_list[["2001"]], "(a) 2001")
p_2006 <- build_map_panel(reclass_list[["2006"]], "(b) 2006 (Moratória da Soja)")
p_2012 <- build_map_panel(reclass_list[["2012"]], "(c) 2012 (Código Florestal)")
p_2024 <- build_map_panel(reclass_list[["2024"]], "(d) 2024")

# Arranjo 2x2 em ordem cronológica (leitura em Z):
#   Linha 1 : (a) 2001 | (b) 2006
#   Linha 2 : (c) 2012 | (d) 2024
p_grid_base <- (p_2001 | p_2006) / (p_2012 | p_2024) +
  patchwork::plot_layout(guides = "collect") &
  theme(
    legend.position  = "bottom",
    legend.box       = "horizontal",
    legend.title     = element_text(size = 10, face = "bold", color = "#111111"),
    legend.text      = element_text(size = 9, color = "#222222"),
    legend.margin    = margin(t = 24, b = 2),
    plot.background  = element_rect(fill = "#FFFFFF", color = NA)
  )

# Mede a largura exata de um painel geográfico no grid para que a barra de 300 km
# tenha escala geodésica rigorosamente idêntica à dos mapas
gt_base    <- patchwork::patchworkGrob(p_grid_base)
col_widths <- grid::convertWidth(gt_base$widths, "in", valueOnly = TRUE)
fig_w_in   <- 11.4
fig_h_in   <- 10.8
# No layout patchwork 2 colunas com painéis idênticos, a largura do painel é:
# (largura total - soma das margens fixas entre painéis) / 2
null_w     <- max(0, fig_w_in - sum(col_widths)) / 2
panel_w_npc <- null_w / fig_w_in

row_heights <- grid::convertHeight(gt_base$heights, "in", valueOnly = TRUE)
null_h      <- max(0, fig_h_in - sum(row_heights)) / 2
panel_h_npc <- max(null_h / fig_h_in, 0.44)

p_north_overlay <- ggplot() +
  geom_sf(data = mt_state, fill = NA, color = NA) +
  coord_sf(crs = TARGET_EPSG, xlim = xlim_shared, ylim = ylim_shared, expand = FALSE) +
  ggspatial::annotation_north_arrow(
    location = "tl", which_north = "true",
    height = unit(0.85, "cm"), width = unit(0.85, "cm"),
    pad_x = grid::unit(0.5, "npc") - grid::unit(0.425, "cm"),
    pad_y = unit(0.05, "cm"),
    style = ggspatial::north_arrow_fancy_orienteering(
      fill = c("#FFFFFF", "#222222"), line_col = "#222222", text_size = 7
    )
  ) +
  theme_void() +
  theme(plot.background = element_rect(fill = NA, color = NA),
        panel.background = element_rect(fill = NA, color = NA),
        plot.margin = margin(0, 0, 0, 0))

# Mede a largura total da escala mantendo a exata razão de aspecto do painel geográfico
p_scale_probe <- ggplot() +
  geom_sf(data = mt_state, fill = NA, color = NA) +
  coord_sf(crs = TARGET_EPSG, xlim = xlim_shared, ylim = ylim_shared, expand = FALSE) +
  ggspatial::annotation_scale(
    location = "bl", width_hint = 0.22,
    bar_cols = c("#222222", "#FFFFFF"),
    text_cex = 0.72, line_width = 0.50,
    pad_x = unit(0, "cm"), pad_y = unit(0, "cm")
  ) +
  theme_void() +
  theme(plot.margin = margin(0, 0, 0, 0))
g_probe <- ggplotGrob(p_scale_probe)
pan_p   <- g_probe$grobs[[which(g_probe$layout$name == "panel")]]
r_probe <- pan_p$children[[grep("rect", names(pan_p$children))[1]]]
t_probe <- pan_p$children[[grep("text", names(pan_p$children))[1]]]
grid::pushViewport(grid::viewport(width = grid::unit(null_w, "in"),
                                  height = grid::unit(panel_h_npc * fig_h_in, "in")))
bar_w_cm <- grid::convertWidth(r_probe$width, "cm", valueOnly = TRUE)[1]
n_bars   <- max(length(r_probe$x), length(r_probe$width))
txt_cm   <- grid::convertWidth(grid::grobWidth(t_probe), "cm", valueOnly = TRUE)
grid::popViewport()
sb_total_cm <- n_bars * bar_w_cm + 0.15 + txt_cm
cat(sprintf("  -> Escala geodésica central: %d blocos = %.2f cm (barra+texto = %.2f cm)\n",
            n_bars, n_bars * bar_w_cm, sb_total_cm))
sb_pad_x    <- grid::unit(0.5, "npc") - grid::unit(0.5 * sb_total_cm, "cm")

p_scale_overlay <- ggplot() +
  geom_sf(data = mt_state, fill = NA, color = NA) +
  coord_sf(crs = TARGET_EPSG, xlim = xlim_shared, ylim = ylim_shared, expand = FALSE) +
  ggspatial::annotation_scale(
    location = "bl", width_hint = 0.22,
    bar_cols = c("#222222", "#FFFFFF"),
    text_cex = 0.72, line_width = 0.50,
    pad_x = sb_pad_x, pad_y = unit(0.05, "cm")
  ) +
  theme_void() +
  theme(plot.background = element_rect(fill = NA, color = NA),
        panel.background = element_rect(fill = NA, color = NA),
        plot.margin = margin(0, 0, 0, 0))

p_fig1_2x2 <- cowplot::ggdraw(p_grid_base) +
  cowplot::draw_plot(p_north_overlay, x = 0.5 - panel_w_npc / 2, y = 0.50,
                     width = panel_w_npc, height = panel_h_npc) +
  cowplot::draw_plot(p_scale_overlay, x = 0.5 - panel_w_npc / 2, y = 0.068,
                     width = panel_w_npc, height = panel_h_npc)

fname_base <- "fig6_uso_solo_mt_2001_2006_2012_2024"
for (d in c(LOCAL_OUT, AUDIT_OUT, TEXT_FIG)) {
  ggsave(file.path(d, paste0(fname_base, ".pdf")), plot = p_fig1_2x2, width = fig_w_in, height = fig_h_in, units = "in", device = "pdf")
}
for (d in c(LOCAL_OUT, AUDIT_OUT)) {
  ggsave(file.path(d, paste0(fname_base, ".png")), plot = p_fig1_2x2, width = fig_w_in, height = fig_h_in, units = "in", dpi = 300, bg = "white")
}

cat("Concluído com sucesso! Arquivos salvos em:\n")
cat("  -", file.path(TEXT_FIG, paste0(fname_base, ".pdf")), "\n")
cat("  -", file.path(LOCAL_OUT, paste0(fname_base, ".png")), "\n")
