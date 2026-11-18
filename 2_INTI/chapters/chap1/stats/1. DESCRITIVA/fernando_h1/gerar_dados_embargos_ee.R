# ==============================================================================
# Extração reprodutível das séries anuais e Top 10 de embargos e autos Flora
# Alinhada integralmente ao Caminho B2 de modelos_fixos_h1_prec_v2.ipynb
# ==============================================================================
suppressPackageStartupMessages({
  library(data.table)
  library(sf)
})

raiz <- normalizePath(".", winslash = "/", mustWork = TRUE)
if (!dir.exists(file.path(raiz, "2_INTI"))) {
  stop("Execute a partir da raiz do repositório tese_eco_usp.", call. = FALSE)
}

path_shp   <- file.path(raiz, "2_INTI/xdata/chap1/raw/vector/ibge/MT_Municipios_2023.zip")
path_emb   <- file.path(raiz, "2_INTI/xdata/chap1/raw/tabular/ibama/termo_embargo_historico.csv")
path_desc  <- file.path(raiz, "2_INTI/chapters/chap1/stats/2. MODELOS/grupos_h1/0_bases_complementares/painel_municipal_descritiva_h1.csv")
out_dados  <- file.path(raiz, "2_INTI/chapters/chap1/stats/1. DESCRITIVA/resultados_h1/dados")

shp_mt <- st_read(paste0("/vsizip/", path_shp), quiet = TRUE)
stopifnot(nrow(shp_mt) == 141)

desc <- fread(path_desc)
bio_map <- unique(desc[, .(ibge = as.integer(codigo_ibge), municipio, bioma_predominante)])
stopifnot(nrow(bio_map) == 141)

# 1. Novos embargos geocodificados (deduplicação 2000-2024 idêntica ao notebook v2)
dt_emb <- fread(
  path_emb,
  sep = ";",
  select = c("SEQ_TAD", "SIT_CANCELADO", "DAT_EMBARGO", "COD_MUNICIPIO", "UF",
             "NUM_LONGITUDE_TAD", "NUM_LATITUDE_TAD", "QTD_AREA_EMBARGADA"),
  encoding = "UTF-8",
  showProgress = FALSE
)
dt_mt <- dt_emb[(UF == "MT" | substr(as.character(COD_MUNICIPIO), 1, 2) == "51") & SIT_CANCELADO != "S"]
dt_mt[, dt := as.Date(substr(DAT_EMBARGO, 1, 10))]
dt_mt[, yr := as.integer(format(dt, "%Y"))]
dt_mt <- dt_mt[!is.na(yr) & yr >= 2000 & yr <= 2024]
setorder(dt_mt, SEQ_TAD, dt)
dedup_emb <- unique(dt_mt, by = "SEQ_TAD")

dedup_emb[, lon := suppressWarnings(as.numeric(gsub(",", ".", NUM_LONGITUDE_TAD)))]
dedup_emb[, lat := suppressWarnings(as.numeric(gsub(",", ".", NUM_LATITUDE_TAD)))]
pts_valid <- dedup_emb[!is.na(lon) & !is.na(lat) & lon >= -65 & lon <= -48 & lat >= -20 & lat <= -6]

sf_emb <- st_as_sf(pts_valid, coords = c("lon", "lat"), crs = st_crs(shp_mt))
joined_emb <- st_join(sf_emb, shp_mt["CD_MUN"], join = st_within)
st_geometry(joined_emb) <- NULL

dt_j24 <- as.data.table(joined_emb)[!is.na(CD_MUN) & yr >= 2001 & yr <= 2024,
                                    .(n_emb = .N), by = .(ibge = as.integer(CD_MUN), yr)]
grid24 <- CJ(ibge = bio_map$ibge, yr = 2001:2024)
pan_emb <- merge(grid24, dt_j24, by = c("ibge", "yr"), all.x = TRUE)
pan_emb[is.na(n_emb), n_emb := 0L]
pan_emb <- merge(pan_emb, bio_map, by = "ibge")

emb_anual_bio <- pan_emb[, .(
  total_termos = sum(n_emb),
  mun_com_emb = sum(n_emb > 0),
  media_mun = mean(n_emb)
), by = .(ano = yr, bioma_predominante)][order(ano, bioma_predominante)]

emb_mun <- pan_emb[, .(total_emb = sum(n_emb)), by = .(ibge, municipio, bioma_predominante)][order(-total_emb, ibge)]
emb_mun[, pct_estado := 100 * total_emb / sum(total_emb)]
emb_mun[, rank_emb := .I]

flora_mun <- desc[, .(
  total_flora_comp = sum(n_autos_flora__ibama_espacial[flag_contagem_flora_parcial__ibama_espacial %in% FALSE], na.rm = TRUE),
  anos_flora_comp = sum(!is.na(n_autos_flora__ibama_espacial) & flag_contagem_flora_parcial__ibama_espacial %in% FALSE)
), by = .(ibge = as.integer(codigo_ibge))]

top10_emb <- merge(emb_mun[1:10], flora_mun, by = "ibge", all.x = TRUE)[order(rank_emb)]

# 2. Autos de Flora (classificação completa) por ano e bioma
flora_anual_bio <- desc[, .(
  total_autos_comp = sum(n_autos_flora__ibama_espacial[flag_contagem_flora_parcial__ibama_espacial %in% FALSE], na.rm = TRUE),
  mun_comp = sum(!is.na(n_autos_flora__ibama_espacial) & flag_contagem_flora_parcial__ibama_espacial %in% FALSE),
  mun_obs = sum(!is.na(n_autos_flora__ibama_espacial))
), by = .(ano, bioma_predominante)][order(ano, bioma_predominante)]

fwrite(emb_anual_bio, file.path(out_dados, "embargos_ibama_anual_bioma.csv"))
fwrite(top10_emb, file.path(out_dados, "embargos_ibama_top10.csv"))
fwrite(flora_anual_bio, file.path(out_dados, "flora_ibama_anual_bioma.csv"))

# Resumo de verificação
res_bio_emb <- emb_anual_bio[, .(total = sum(total_termos)), by = bioma_predominante]
res_bio_emb[, pct := round(100 * total / sum(total), 1)]
cat("Embargos 2001-2024 total:", sum(res_bio_emb$total), "\n")
print(res_bio_emb)
cat("Top 10 soma:", sum(top10_emb$total_emb), sprintf("(%.1f%%)\n", sum(top10_emb$pct_estado)))
cat("Top 5 Cerrado:\n")
print(emb_mun[bioma_predominante == "Cerrado"][1:5, .(municipio, total_emb, pct_estado = round(pct_estado, 2))])
res_bio_fl <- flora_anual_bio[, .(total = sum(total_autos_comp)), by = bioma_predominante]
res_bio_fl[, pct := round(100 * total / sum(total), 1)]
cat("Autos Flora completos 2001-2024 total:", sum(res_bio_fl$total), "\n")
print(res_bio_fl)
