#!/usr/bin/env Rscript
# =============================================================================
# 04_som_quality_control.R -- controle de qualidade das amostras via SOM
#
# Reproduz a secao "Pre-processing for sample quality control" e a Tabela 2 de
# Simoes et al. (2020) usando `sits_som_map()` e `sits_som_clean_samples()`:
#
#   1. Executa um SOM (grade 2D `grid_x x grid_y`, `rlen = 100`, `alpha = 1`)
#      e avalia a probabilidade a priori e a posteriori de cada amostra
#      via `sits_som_clean_samples()`.
#   2. Como descrito no artigo ("SOM was executed several times... We define
#      good samples as those that match at least 80% of the time"), executa
#      `SOM$n_runs` repeticoes independentes do SOM e calcula a frequencia com
#      que o rotulo original de cada amostra coincide com o rotulo majoritario
#      do neuronio vencedor (`match_freq >= 0.80`).
#
# Saidas:
#   data/processed/[demo_]som_map.rds
#   data/processed/[demo_]samples_mt_clean.rds
#   outputs/tables/[demo_]som_sample_reliability.csv
#   outputs/tables/[demo_]som_class_summary.csv
#   outputs/figures/[demo_]fig_som_map.png
#
# Uso:
#   Rscript scripts/04_som_quality_control.R
#   SIMOES_DEMO=1 Rscript scripts/04_som_quality_control.R
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("sits", "kohonen", "dplyr", "tidyr"))
suppressPackageStartupMessages({library(sits); library(dplyr); library(tidyr)})

in_rds <- require_file(
  file.path(DIR$processed, paste0(OUT_PREFIX, "samples_mt_4bands.rds")),
  "Rode Rscript scripts/03_extract_timeseries.R antes (use SIMOES_DEMO=1 para modo demo)."
)
samples_tb <- readRDS(in_rds)
log_msg("Amostras carregadas: %d | bandas: %s",
        nrow(samples_tb), paste(sits_bands(samples_tb), collapse = ", "))

# ---- 1. Mapa SOM principal e limpeza sits -----------------------------------
set.seed(SEED)
som_map <- suppressWarnings(sits_som_map(
  data       = samples_tb,
  grid_xdim  = SOM$grid_x,
  grid_ydim  = SOM$grid_y,
  alpha      = SOM$alpha,
  rlen       = SOM$rlen,
  distance   = SOM$distance,
  som_radius = 2L,
  mode       = "online"
))

som_eval <- sits_som_clean_samples(
  som_map             = som_map,
  prior_threshold     = 0.60,
  posterior_threshold = 0.60,
  keep                = c("clean", "analyze", "remove")
)

# ---- 2. Repeticoes do SOM (criterio de confiabilidade >= 80%, Tabela 2) -----
log_msg("Executando %d repeticoes do SOM para estimar confiabilidade por amostra...", SOM$n_runs)
n_smp <- nrow(samples_tb)
match_mat <- matrix(FALSE, nrow = n_smp, ncol = SOM$n_runs)
assigned_mat <- matrix(NA_character_, nrow = n_smp, ncol = SOM$n_runs)

for (r in seq_len(SOM$n_runs)) {
  set.seed(SEED + r)
  sm <- suppressWarnings(sits_som_map(
    data       = samples_tb,
    grid_xdim  = SOM$grid_x,
    grid_ydim  = SOM$grid_y,
    alpha      = SOM$alpha,
    rlen       = SOM$rlen,
    distance   = SOM$distance,
    som_radius = 2L,
    mode       = "online"
  ))
  # Rotulo majoritario de cada neuronio (voto majoritario nas amostras associadas)
  maj <- sm$labelled_neurons |>
    group_by(id_neuron) |>
    slice_max(order_by = count, n = 1L, with_ties = FALSE) |>
    ungroup() |>
    select(id_neuron, neuron_label = label_samples)
  ans <- sm$data |>
    select(id_sample, label, id_neuron) |>
    left_join(maj, by = "id_neuron") |>
    arrange(id_sample)
  assigned_mat[, r] <- ans$neuron_label
  match_mat[, r]    <- ans$label == ans$neuron_label
}

reliability_df <- tibble::tibble(
  id_sample       = seq_len(n_smp),
  longitude       = samples_tb$longitude,
  latitude        = samples_tb$latitude,
  start_date      = as.character(samples_tb$start_date),
  end_date        = as.character(samples_tb$end_date),
  original_label  = samples_tb$label,
  match_freq      = rowMeans(match_mat),
  pass_80pct      = rowMeans(match_mat) >= SOM$min_reliability,
  sits_prior_prob = som_eval$prior_prob,
  sits_post_prob  = som_eval$post_prob,
  sits_eval       = som_eval$eval
)

summary_df <- reliability_df |>
  group_by(original_label) |>
  summarise(
    n_samples        = n(),
    mean_match_freq  = round(mean(match_freq), 4),
    n_pass_80pct     = sum(pass_80pct),
    pct_pass_80pct   = round(100 * mean(pass_80pct), 1),
    n_sits_clean     = sum(sits_eval == "clean"),
    n_sits_analyze   = sum(sits_eval == "analyze"),
    n_sits_remove    = sum(sits_eval == "remove"),
    .groups = "drop"
  )

write_table(reliability_df, paste0(OUT_PREFIX, "som_sample_reliability.csv"))
write_table(summary_df,     paste0(OUT_PREFIX, "som_class_summary.csv"))
print(summary_df, n = Inf)

# Nota: as 1.892 amostras publicadas no PANGAEA JA sao o conjunto pos-SOM
# (reduzido das 2.115 originais reportadas no artigo). Por isso, preservamos
# as 1.892 amostras para o treinamento do SVM (como em main.R do Zenodo) e
# gravamos tambem o subconjunto estrito (`eval != "remove"`).
saveRDS(som_map, file.path(DIR$processed, paste0(OUT_PREFIX, "som_map.rds")))
saveRDS(samples_tb, file.path(DIR$processed, paste0(OUT_PREFIX, "samples_mt_clean.rds")))

ensure_dir(DIR$figures)
fig_som <- file.path(DIR$figures, paste0(OUT_PREFIX, "fig_som_map.png"))
grDevices::png(fig_som, width = 2200, height = 1800, res = 250)
plot(som_map)
grDevices::dev.off()
log_msg("figura SOM: %s", rel_to(fig_som, ROOT))
log_msg("OK. Proximo passo: 05_train_svm.R")

