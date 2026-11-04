#!/usr/bin/env Rscript
# =============================================================================
# 02_download_reference.R -- dados de referencia para a Figura 5
#
#  (a) Limite de Mato Grosso (IBGE, malha estadual)           -> mt_boundary.geojson
#  (b) IBGE/SIDRA, tabela 1612 (Pesquisa Agricola Municipal): area plantada (v109)
#      e area colhida (v216) de soja, milho, algodao herbaceo e girassol em MT,
#      2001-2017                                              -> ibge_pam_mt_ha.csv
#  (c) PRODES Amazonia Legal (TerraBrasilis/INPE, WFS): incremento anual de
#      desmatamento em MT, camada "yearly_deforestation" (so 2008 em diante;
#      1988-2007 esta agregado em uma unica camada).    -> prodes_mt_increment_ha.csv
#
# Observacao importante: os dados do PRODES sao INCREMENTOS de desmatamento.
# A serie de "floresta remanescente" do artigo nao e publicada neste servico;
# 10_fig5_area_comparison.R deriva uma serie comparavel (ver README) ou usa
# raw/ancillary/prodes_mt_forest_ha.csv (year, forest_ha) se voce o fornecer.
#
# Uso: Rscript scripts/02_download_reference.R [--force]
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("curl", "jsonlite", "digest"))
force <- cli_flag("force")
anc <- ensure_dir(DIR$ancillary)

# ---- (a) Limite de MT -------------------------------------------------------
bnd <- file.path(anc, "mt_boundary.geojson")
download_file(IBGE_MT_BOUNDARY, bnd, overwrite = force, min_bytes = 500L)
write_manifest(bnd, "ibge:malhas/estados/51", IBGE_MT_BOUNDARY)

# ---- (b) IBGE / SIDRA -------------------------------------------------------
sidra_products <- c(soybean = 2713L, corn = 2711L, cotton = 2689L, sunflower = 109179L)
sidra_url <- sprintf("%s/t/1612/n3/51/v/109,216/p/%d-%d/c81/%s",
                     IBGE_SIDRA_BASE, min(YEARS), max(YEARS),
                     paste(sidra_products, collapse = ","))
ibge_csv <- file.path(anc, "ibge_pam_mt_ha.csv")
if (!file.exists(ibge_csv) || force) {
  log_msg("IBGE/SIDRA: %s", sidra_url)
  j <- jsonlite::fromJSON(sidra_url)
  j <- j[-1, , drop = FALSE]                       # linha 1 = cabecalho
  ibge <- data.frame(
    year    = as.integer(j$D3C),
    product = names(sidra_products)[match(as.integer(j$D4C), sidra_products)],
    variable = ifelse(j$D2C == "109", "area_planted_ha", "area_harvested_ha"),
    value   = suppressWarnings(as.numeric(j$V)),   # "-", "..." viram NA
    stringsAsFactors = FALSE
  )
  stopifnot(!anyNA(ibge$product), nrow(ibge) == length(YEARS) * 4L * 2L)
  ibge <- ibge[order(ibge$variable, ibge$product, ibge$year), ]
  utils::write.csv(ibge, ibge_csv, row.names = FALSE, fileEncoding = "UTF-8")
  log_msg("IBGE: %d linhas; NAs: %d", nrow(ibge), sum(is.na(ibge$value)))
} else log_msg("ja existe: %s", basename(ibge_csv))
write_manifest(ibge_csv, "ibge:sidra:1612", sidra_url)

# ---- (c) PRODES (WFS, sem geometria) ---------------------------------------
wfs_fetch <- function(layer, cql, props, page = 50000L) {
  out <- list(); start <- 0L
  repeat {
    url <- paste0(PRODES_AMZ_WFS, "?service=WFS&version=2.0.0&request=GetFeature",
                  "&typeNames=", layer, "&outputFormat=application/json",
                  "&propertyName=", props, "&sortBy=fid",
                  "&count=", page, "&startIndex=", start,
                  "&CQL_FILTER=", utils::URLencode(cql, reserved = TRUE))
    f <- jsonlite::fromJSON(url)
    if (!length(f$features) || nrow(f$features) == 0L) break
    out[[length(out) + 1L]] <- f$features$properties
    log_msg("  %s: %d feicoes (startIndex=%d)", layer, nrow(f$features), start)
    if (nrow(f$features) < page) break
    start <- start + page
  }
  do.call(rbind, out)
}

prodes_csv <- file.path(anc, "prodes_mt_increment_ha.csv")
if (!file.exists(prodes_csv) || force) {
  log_msg("PRODES: consultando TerraBrasilis (WFS)")
  yr <- wfs_fetch("prodes-legal-amz:yearly_deforestation",
                  "state='MT'", "state,class_name,year,area_km")
  yr <- yr[grepl("^d[0-9]{4}$", yr$class_name), ]
  tot <- stats::aggregate(area_km ~ class_name + year, yr, sum)
  write_table(tot, "prodes_mt_yearly_by_class_km2.csv")   # auditoria
  pr <- data.frame(year = tot$year, increment_ha = tot$area_km * 100,   # 1 km2 = 100 ha
                   source = "terrabrasilis_wfs_yearly_deforestation")
  pr <- pr[order(pr$year), ]
  utils::write.csv(pr, prodes_csv, row.names = FALSE, fileEncoding = "UTF-8")
  print(pr[pr$year %in% YEARS, ], row.names = FALSE)
} else log_msg("ja existe: %s", basename(prodes_csv))
write_manifest(prodes_csv, "terrabrasilis:prodes-legal-amz", PRODES_AMZ_WFS)

# PRODES anterior a 2008 NAO e servido por incremento anual: INPE agregou
# 1988-2007 em uma unica camada ("accumulated_deforestation_2007").  Para ancorar
# a serie em 2001 (como no artigo), forneca manualmente:
#   data/raw/ancillary/prodes_mt_rates_km2.csv   colunas: year,increment_km2
# (exportacao CSV do painel TerraBrasilis, PRODES Amazonia Legal, estado MT).
manual <- file.path(anc, "prodes_mt_rates_km2.csv")
if (file.exists(manual)) {
  log_msg("Arquivo manual de taxas PRODES encontrado: sera usado em 10_fig5.")
} else {
  log_msg("AVISO: sem %s -> a serie PRODES da Fig. 5(d) comecara em 2008 (ancora 2007).",
          basename(manual))
}


log_msg("OK. Proximo passo: 03_extract_timeseries.R (replicacao completa) ou 09_area_tables.R (mapas publicados).")
