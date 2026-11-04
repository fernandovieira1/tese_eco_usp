#!/usr/bin/env Rscript
# =============================================================================
# 10_fig5_area_comparison.R -- replica a Figura 5 de Simoes et al. (2020)
#
# Compara 2001-2017 a area estimada pela classificacao com as estatisticas
# oficiais: (a) soja, (b) milho, (c) algodao  [IBGE/PAM, SIDRA 1612] e
# (d) floresta [PRODES].
#
#  * IBGE: area plantada (v109) por padrao; area colhida (v216) como robustez.
#  * Agregados da classificacao (config.R, CROP_GROUPS): soja = classes 5-9,
#    milho = Soy_Corn, algodao = Fallow_Cotton + Soy_Cotton.
#  * PRODES: serie derivada = floresta_classificada(ano_ancora) - desmatamento
#    acumulado do PRODES apos o ano_ancora.  Sem o arquivo manual
#    raw/ancillary/prodes_mt_rates_km2.csv (year,increment_km2) a ancora e 2007 (incrementos de 2008 em diante).
#    ESTA E UMA APROXIMACAO: o artigo nao detalha como a serie de floresta do
#    PRODES foi montada (ver README).
#
# Saidas:
#   outputs/figures/fig5_area_comparison[_replicated].{png,pdf}
#   outputs/tables/fig5_series[_replicated].csv
#   outputs/tables/fig5_correlations[_replicated].csv  (inclui valores do artigo)
#
# Uso: Rscript scripts/10_fig5_area_comparison.R
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("ggplot2", "dplyr", "tidyr", "scales"))
suppressPackageStartupMessages({library(ggplot2); library(dplyr); library(tidyr)})

tag <- if (MAPS_SOURCE == "published") "" else "_replicated"
agg <- utils::read.csv(require_file(file.path(DIR$tables, paste0("area_aggregates_year_ha", tag, ".csv")),
                                    "Rode 09_area_tables.R antes."))
ibge <- utils::read.csv(require_file(file.path(DIR$ancillary, "ibge_pam_mt_ha.csv"),
                                     "Rode 02_download_reference.R antes."))
prodes <- utils::read.csv(require_file(file.path(DIR$ancillary, "prodes_mt_increment_ha.csv"),
                                       "Rode 02_download_reference.R antes."))

# ---- Series de referencia ---------------------------------------------------
ibge_w <- ibge |>
  pivot_wider(names_from = c(product, variable), values_from = value)

# PRODES: incrementos (ha); arquivo manual (km2) sobrescreve anos coincidentes
inc <- prodes[, c("year", "increment_ha")]
manual <- file.path(DIR$ancillary, "prodes_mt_rates_km2.csv")
if (file.exists(manual)) {
  m <- utils::read.csv(manual)
  stopifnot(all(c("year", "increment_km2") %in% names(m)))
  inc <- bind_rows(data.frame(year = m$year, increment_ha = m$increment_km2 * 100),
                   inc[!inc$year %in% m$year, ])
}
inc <- inc[order(inc$year), ]
anchor <- min(inc$year) - 1L
need_years <- (anchor + 1L):max(YEARS)
stopifnot("Serie PRODES com lacunas" = all(need_years %in% inc$year))
if (anchor < min(YEARS)) { anchor <- min(YEARS) - 0L; inc <- inc[inc$year > anchor, ] }
log_msg("PRODES: ancora = %d; incrementos %d-%d", anchor, min(inc$year), max(inc$year))

f_anchor <- agg$forest_ha[agg$year == anchor]
prodes_forest <- data.frame(
  year = c(anchor, inc$year[inc$year %in% YEARS]),
  prodes_forest_ha = c(f_anchor,
                       f_anchor - cumsum(inc$increment_ha[inc$year %in% YEARS]))
)

# ---- Tabela de series -------------------------------------------------------
ser <- agg |>
  select(year, soybean_ha, corn_ha, cotton_ha, sunflower_ha, forest_ha) |>
  left_join(ibge_w |> transmute(
    year,
    ibge_soybean_ha = soybean_area_planted_ha, ibge_corn_ha = corn_area_planted_ha,
    ibge_cotton_ha = cotton_area_planted_ha, ibge_sunflower_ha = sunflower_area_planted_ha,
    ibge_soybean_harv_ha = soybean_area_harvested_ha, ibge_corn_harv_ha = corn_area_harvested_ha,
    ibge_cotton_harv_ha = cotton_area_harvested_ha, ibge_sunflower_harv_ha = sunflower_area_harvested_ha),
    by = "year") |>
  left_join(prodes_forest, by = "year")
write_table(ser, paste0("fig5_series", tag, ".csv"))

# ---- Correlacoes (vs. valores reportados no artigo) -------------------------
paper_r <- c(soybean = 0.97, cotton = 0.85, corn = 0.98, sunflower = 0.80, all_crops = 0.98)
cor_row <- function(name, est, ref, ref_var) {
  ok <- stats::complete.cases(est, ref)
  data.frame(item = name, reference = ref_var, n_years = sum(ok),
             pearson_r = if (sum(ok) >= 3) stats::cor(est[ok], ref[ok]) else NA_real_,
             paper_r = unname(paper_r[name]))
}
crops <- c("soybean", "corn", "cotton", "sunflower")
cors <- bind_rows(lapply(c("planted", "harvested"), function(v) {
  sfx <- if (v == "planted") "_ha" else "_harv_ha"
  per <- lapply(crops, function(cn) cor_row(cn, ser[[paste0(cn, "_ha")]],
                                            ser[[paste0("ibge_", cn, sfx)]], paste0("IBGE area_", v)))
  est_sum <- rowSums(ser[paste0(crops, "_ha")], na.rm = FALSE)
  ref_sum <- rowSums(ser[paste0("ibge_", crops, sfx)], na.rm = FALSE)
  bind_rows(per, list(cor_row("all_crops", est_sum, ref_sum, paste0("IBGE area_", v))))
}))
cors$diff_vs_paper <- round(cors$pearson_r - cors$paper_r, 3)
write_table(cors, paste0("fig5_correlations", tag, ".csv"))
print(cors, row.names = FALSE)

# ---- Figura -----------------------------------------------------------------
lab <- c(soybean = "(a) Soybean", corn = "(b) Corn", cotton = "(c) Cotton", forest = "(d) Forest")
est_lab <- if (MAPS_SOURCE == "published") "Classification (published maps)" else "Classification (replicated)"
src_lab <- c(est_lab, "IBGE (planted area)", "PRODES-derived")

long <- bind_rows(
  ser |> transmute(year, panel = "soybean",  src = est_lab, ha = soybean_ha),
  ser |> transmute(year, panel = "soybean",  src = "IBGE (planted area)", ha = ibge_soybean_ha),
  ser |> transmute(year, panel = "corn",     src = est_lab, ha = corn_ha),
  ser |> transmute(year, panel = "corn",     src = "IBGE (planted area)", ha = ibge_corn_ha),
  ser |> transmute(year, panel = "cotton",   src = est_lab, ha = cotton_ha),
  ser |> transmute(year, panel = "cotton",   src = "IBGE (planted area)", ha = ibge_cotton_ha),
  ser |> transmute(year, panel = "forest",   src = est_lab, ha = forest_ha),
  ser |> transmute(year, panel = "forest",   src = "PRODES-derived", ha = prodes_forest_ha)
) |>
  filter(!is.na(ha)) |>
  mutate(panel = factor(lab[panel], levels = lab),
         src = factor(src, levels = src_lab))

cols <- setNames(c("#10773e", "#d95f02", "#1b5ee4"), src_lab)
p <- ggplot(long, aes(year, ha / 1e6, colour = src, linetype = src, shape = src)) +
  geom_line(linewidth = 0.8) + geom_point(size = 1.8) +
  facet_wrap(~panel, scales = "free_y", ncol = 2) +
  scale_colour_manual(values = cols, name = NULL) +
  scale_linetype_manual(values = setNames(c("solid", "dashed", "dotdash"), src_lab), name = NULL) +
  scale_shape_manual(values = setNames(c(16, 17, 15), src_lab), name = NULL) +
  scale_x_continuous(breaks = seq(2001, 2017, 4)) +
  labs(x = NULL, y = "Area (million ha)",
       title = "Comparison of land use areas in Mato Grosso, 2001-2017",
       caption = paste0("Replication of Fig. 5, Simoes et al. (2020). ",
                        "PRODES-derived forest = classified forest in ", anchor,
                        " minus cumulative PRODES increments.")) +
  theme_bw(base_size = 11) +
  theme(legend.position = "bottom", strip.background = element_rect(fill = "grey95"),
        strip.text = element_text(hjust = 0, face = "bold"),
        plot.caption = element_text(size = 7, colour = "grey30"))

ensure_dir(DIR$figures)
for (ext in c("png", "pdf")) {
  ggsave(file.path(DIR$figures, paste0("fig5_area_comparison", tag, ".", ext)),
         p, width = 9, height = 6.5, dpi = 300)
}
log_msg("figura: outputs/figures/fig5_area_comparison%s.png", tag)
log_msg("OK. Proximo passo: 11_fig6_maps.R")
