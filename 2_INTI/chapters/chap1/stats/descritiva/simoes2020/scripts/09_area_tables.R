#!/usr/bin/env Rscript
# =============================================================================
# 09_area_tables.R -- agrega os rasters anuais em dataframes tabulares
#
# Para cada ano (2001-2017): contagem de pixels por classe e area em hectares.
# Fonte dos mapas: SIMOES_MAPS_SOURCE = "published" (PANGAEA; padrao) ou
# "replicated" (saida de 08_luc_calculus.R).
#
# Area do pixel = res_x * res_y (projecao senoidal MODIS e equivalente em area;
# ~5,37 ha para 231,656 m).  Ver README, "Decisoes e premissas".
#
# Saidas (outputs/tables/):
#   area_by_class_year_ha_long[_replicated].csv   year, code, label, pixels, area_ha
#   area_by_class_year_ha_wide[_replicated].csv   uma coluna por classe
#   area_aggregates_year_ha[_replicated].csv      culturas, floresta, pastagem...
#
# Uso: Rscript scripts/09_area_tables.R [--years=2001:2017]
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("terra", "dplyr", "tidyr"))
suppressPackageStartupMessages({library(dplyr); library(tidyr)})

years <- cli_years()
tag <- if (MAPS_SOURCE == "published") "" else "_replicated"
log_msg("Fonte dos mapas: %s | anos: %d-%d", MAPS_SOURCE, min(years), max(years))

rows <- lapply(years, function(y) {
  p <- require_file(map_path(y), "Rode 01_download_core.R (published) ou 08_luc_calculus.R (replicated).")
  r <- terra::rast(p)
  a <- pixel_area_ha(r)
  cc <- class_counts(r)
  unknown <- setdiff(cc$code, c(0L, CLASSES$code))
  if (length(unknown)) warning(sprintf("Ano %d: codigos fora da legenda: %s", y, paste(unknown, collapse = ",")))
  cc <- cc[cc$code %in% CLASSES$code, ]
  log_msg("%d: %s pixels validos | %.4f ha/pixel", y, format(sum(cc$pixels), big.mark = ",", decimal.mark = "."), a)
  data.frame(year = y, code = cc$code, pixels = cc$pixels,
             pixel_ha = a, area_ha = cc$pixels * a)
})
long <- bind_rows(rows) |>
  left_join(CLASSES[, c("code", "label")], by = "code") |>
  complete(year, nesting(code, label), fill = list(pixels = 0, area_ha = 0)) |>
  group_by(year) |> mutate(pixel_ha = max(pixel_ha, na.rm = TRUE)) |> ungroup() |>
  arrange(year, code) |>
  select(year, code, label, pixels, pixel_ha, area_ha)

wide <- long |>
  select(year, label, area_ha) |>
  pivot_wider(names_from = label, values_from = area_ha)

wide_tot <- long |> group_by(year) |>
  summarise(total_classified_ha = sum(area_ha), .groups = "drop")

# Agregados (premissas em config.R: CROP_GROUPS)
grp <- function(codes) long |> filter(code %in% codes) |>
  group_by(year) |> summarise(v = sum(area_ha), .groups = "drop")
agg <- wide_tot
for (nm in names(CROP_GROUPS)) agg[[paste0(nm, "_ha")]] <- grp(CROP_GROUPS[[nm]])$v
agg$agriculture_ha <- grp(c(CODE$fallow_cotton, CODE$soy))$v   # classes agricolas (2, 5-9)
agg$pasture_ha     <- grp(CODE$pasture)$v
agg$forest_ha      <- grp(CODE$forest)$v
agg$cerrado_ha     <- grp(CODE$cerrado)$v
agg$secveg_ha      <- grp(CODE$secveg)$v

write_table(long, paste0("area_by_class_year_ha_long", tag, ".csv"))
write_table(wide |> left_join(wide_tot, by = "year"),
            paste0("area_by_class_year_ha_wide", tag, ".csv"))
write_table(agg,  paste0("area_aggregates_year_ha", tag, ".csv"))

cat("\nAgregados (milhoes de ha):\n")
print(agg |> mutate(across(-year, ~ round(.x / 1e6, 3))), n = Inf, width = Inf)
log_msg("OK. Proximo passo: 10_fig5_area_comparison.R")
