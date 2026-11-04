#!/usr/bin/env Rscript
# =============================================================================
# 11_fig6_maps.R -- replica a Figura 6 de Simoes et al. (2020)
#
# Mapas de uso e cobertura do solo de Mato Grosso em 2001 e 2017 (com as mascaras
# de cana, area urbana e agua), usando a paleta OFICIAL do arquivo QML do PANGAEA.
# Pacotes: terra (raster), sf (limite estadual), tmap (mapas).
#
# Saidas:
#   outputs/figures/fig6_land_use_2001_2017[_replicated].{png,pdf}
#   outputs/figures/fig6_map_<ano>[_replicated].png
#   outputs/maps/mt_<ano>_colored[_replicated].tif   (GeoTIFF com tabela de cores)
#
# Uso: Rscript scripts/11_fig6_maps.R [--years=2001,2017]
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("terra", "sf", "tmap", "xml2"))
suppressPackageStartupMessages({library(terra); library(sf); library(tmap)})

years <- cli_years(default = c(2001L, 2017L))
tag <- if (MAPS_SOURCE == "published") "" else "_replicated"

# ---- Paleta oficial: confere config.R contra o QML --------------------------
qml <- require_file(file.path(DIR$pangaea, "QGIS_style_mt_v3.qml"), "Rode 01_download_core.R antes.")
pal_qml <- read_qml_palette(qml)
pal_qml <- pal_qml[order(pal_qml$code), ]
stopifnot(identical(pal_qml$code, CLASSES$code))
if (!identical(tolower(pal_qml$color), tolower(CLASSES$color)) ||
    !identical(sub("^[0-9]+\\. ", "", pal_qml$label), CLASSES$label)) {
  stop("Paleta/rotulos em config.R divergem do QML oficial; atualize CLASSES.")
}
log_msg("paleta oficial conferida contra o QML (13 classes)")

# ---- Dados ------------------------------------------------------------------
rl <- lapply(years, function(y) terra::rast(require_file(map_path(y))))
names(rl) <- as.character(years)
mt <- sf::st_read(require_file(file.path(DIR$ancillary, "mt_boundary.geojson"),
                               "Rode 02_download_reference.R antes."), quiet = TRUE)
mt <- sf::st_transform(mt, terra::crs(rl[[1]]))

present <- sort(unique(unlist(lapply(rl, function(r) class_counts(r)$code))))
cl <- CLASSES[CLASSES$code %in% present, ]
log_msg("classes presentes em %s: %s", paste(years, collapse = "/"), paste(cl$code, collapse = ","))

as_cat <- function(r) {
  drop <- setdiff(CLASSES$code, cl$code)            # classes ausentes: nada a reclassificar
  if (length(drop)) r <- terra::classify(r, cbind(drop, NA_integer_))
  levels(r) <- data.frame(value = cl$code, class = cl$label)
  r
}
rcat <- lapply(rl, as_cat)

# ---- GeoTIFFs coloridos (abrem ja estilizados no QGIS) ----------------------
ensure_dir(DIR$maps)
for (nm in names(rl)) {
  r <- rl[[nm]]
  terra::coltab(r) <- data.frame(value = CLASSES$code, col = CLASSES$color)
  terra::writeRaster(r, file.path(DIR$maps, sprintf("mt_%s_colored%s.tif", nm, tag)),
                     overwrite = TRUE, datatype = "INT1U", gdal = "COMPRESS=DEFLATE")
}

# ---- Mapas (tmap v4) --------------------------------------------------------
tmap::tmap_mode("plot")
tmap::tmap_options(raster.max_cells = c(plot = 8e6, view = 1e6))
pal <- stats::setNames(cl$color, cl$label)

map_one <- function(r, ttl, legend = TRUE) {
  tmap::tm_shape(r) +
    tmap::tm_raster(
      col.scale  = tmap::tm_scale_categorical(values = pal, levels = cl$label),
      col.legend = if (legend) {
        tmap::tm_legend(title = "Land use and cover",
                        position = tmap::tm_pos_out("right", "center"))
      } else tmap::tm_legend(show = FALSE)
    ) +
    tmap::tm_shape(mt) + tmap::tm_borders(col = "grey25", lwd = 0.7) +
    tmap::tm_title(ttl, position = tmap::tm_pos_in("left", "top")) +
    tmap::tm_compass(type = "arrow", position = tmap::tm_pos_in("right", "top"), size = 1.5) +
    tmap::tm_scalebar(breaks = c(0, 100, 200, 300), position = tmap::tm_pos_in("left", "bottom")) +
    tmap::tm_layout(frame = FALSE)
}

for (nm in names(rcat)) {
  m <- map_one(rcat[[nm]], nm)
  tmap::tmap_save(m, file.path(DIR$figures, sprintf("fig6_map_%s%s.png", nm, tag)),
                  width = 7.5, height = 5.5, dpi = 300)
}

# Painel unico com legenda compartilhada (Fig. 6)
stk <- terra::rast(rcat); names(stk) <- names(rcat)
m_all <- tmap::tm_shape(stk) +
  tmap::tm_raster(
    col.scale  = tmap::tm_scale_categorical(values = pal, levels = cl$label),
    col.legend = tmap::tm_legend(title = "Land use and cover",
                                 position = tmap::tm_pos_out("right", "center")),
    col.free   = FALSE
  ) +
  tmap::tm_shape(mt) + tmap::tm_borders(col = "grey25", lwd = 0.7) +
  tmap::tm_facets(nrow = 1) +
  tmap::tm_layout(frame = FALSE, panel.label.bg.color = "grey95")
for (ext in c("png", "pdf")) {
  tmap::tmap_save(m_all, file.path(DIR$figures, sprintf("fig6_land_use_%s%s.%s",
                                                       paste(years, collapse = "_"), tag, ext)),
                  width = 11.5, height = 5.2, dpi = 300)
}
log_msg("OK: figuras em outputs/figures/ (fig6_*)")
