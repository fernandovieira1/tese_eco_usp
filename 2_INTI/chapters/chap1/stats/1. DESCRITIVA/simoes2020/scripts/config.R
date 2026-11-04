# =============================================================================
# config.R -- parametros globais da replicacao de Simoes et al. (2020)
# Todos os scripts fazem source() deste arquivo (via utils.R).
# =============================================================================

# ---- Raiz do projeto e dos dados --------------------------------------------
# `ROOT` precisa ter sido definido pelo script chamador (ver bloco de bootstrap
# no topo de cada script); aqui apenas derivamos os demais caminhos.
stopifnot(exists("ROOT"))

# Os dados podem ficar fora do projeto (recomendado pelo RESEARCH_PROTOCOL:
# dados ativos em 2_INTI/xdata/). Exemplo:
#   setx SIMOES_DATA_ROOT "C:/.../2_INTI/xdata/simoes2020"
DATA_ROOT <- normalizePath(
  Sys.getenv("SIMOES_DATA_ROOT", unset = file.path(ROOT, "data")),
  winslash = "/", mustWork = FALSE
)

DIR <- list(
  root       = ROOT,
  scripts    = file.path(ROOT, "scripts"),
  raw        = file.path(DATA_ROOT, "raw"),
  zenodo     = file.path(DATA_ROOT, "raw", "zenodo"),
  pangaea    = file.path(DATA_ROOT, "raw", "pangaea"),
  ancillary  = file.path(DATA_ROOT, "raw", "ancillary"),
  masks      = file.path(DATA_ROOT, "raw", "masks"),
  processed  = file.path(DATA_ROOT, "processed"),
  classified = file.path(DATA_ROOT, "processed", "classified"),
  masked     = file.path(DATA_ROOT, "processed", "masked"),
  final      = file.path(DATA_ROOT, "processed", "final"),
  maps       = file.path(ROOT, "outputs", "maps"),
  figures    = file.path(ROOT, "outputs", "figures"),
  tables     = file.path(ROOT, "outputs", "tables")
)

# ---- Fontes de dados --------------------------------------------------------
ZENODO_RECORD_ID <- "3354379"                 # doi:10.5281/zenodo.3354379
PANGAEA_DOI      <- "10.1594/PANGAEA.899706"  # versao 3 do conjunto de dados
PANGAEA_TABLE    <- paste0("https://doi.pangaea.de/", PANGAEA_DOI,
                           "?format=textfile&charset=UTF-8")
IBGE_SIDRA_BASE  <- "https://apisidra.ibge.gov.br/values"
IBGE_MT_BOUNDARY <- paste0("https://servicodados.ibge.gov.br/api/v3/malhas/",
                           "estados/51?formato=application/vnd.geo+json",
                           "&qualidade=maxima")
PRODES_AMZ_WFS   <- "https://terrabrasilis.dpi.inpe.br/geoserver/ows"
PRODES_AMZ_LAYER <- "prodes-legal-amz:yearly_deforestation"

# ---- Periodo ----------------------------------------------------------------
# O ano Y cobre o ano agricola de 1-set-(Y-1) a 31-ago-Y (23 imagens MOD13Q1).
YEARS <- 2001:2017
year_window <- function(y) c(start = sprintf("%d-09-01", y - 1L),
                             end   = sprintf("%d-08-31", y))

# ---- Fonte dos mapas usados nas etapas 09-11 --------------------------------
# "published"  : mapas oficiais do PANGAEA (padrao; reproduz Figs. 5 e 6)
# "replicated" : mapas gerados por este pipeline (etapas 03-08)
MAPS_SOURCE <- Sys.getenv("SIMOES_MAPS_SOURCE", unset = "published")
stopifnot(MAPS_SOURCE %in% c("published", "replicated"))

# ---- Modo demonstracao ------------------------------------------------------
# SIMOES_DEMO=1 usa sits::samples_modis_ndvi (as mesmas 1.892 amostras, mas so
# com NDVI) para testar SOM + SVM offline. Saidas recebem prefixo "demo_".
DEMO       <- identical(Sys.getenv("SIMOES_DEMO", unset = "0"), "1")
OUT_PREFIX <- if (DEMO) "demo_" else ""

# ---- Classes (codigos, rotulos e cores) -------------------------------------
# Codigos e rotulos: QGIS_style_mt_v3.qml (PANGAEA) e main.R (Zenodo).
# Cores: paleta oficial do QML, conferida por 11_fig6_maps.R.
CLASSES <- data.frame(
  code  = 1:13,
  label = c("Cerrado", "Fallow_Cotton", "Forest", "Pasture", "Soy_Corn",
            "Soy_Cotton", "Soy_Fallow", "Soy_Millet", "Soy_Sunflower",
            "Sugarcane", "Urban Area", "Water", "Secondary Vegetation"),
  color = c("#b3cc33", "#be94e8", "#10773e", "#eeefce", "#e4a540",
            "#a4507d", "#c948a2", "#be5b1d", "#f09cde",
            "#877712", "#614040", "#1b5ee4", "#0cf8c1"),
  stringsAsFactors = FALSE
)
# Codigos usados pelo SVM (alfabetico, igual ao QML): 1-9.
SVM_CLASSES <- CLASSES$label[1:9]

# Codigos nomeados (evita "numeros magicos" nas regras)
CODE <- list(
  cerrado = 1L, fallow_cotton = 2L, forest = 3L, pasture = 4L,
  soy = 5:9L, sugarcane = 10L, urban = 11L, water = 12L, secveg = 13L
)

# Agregados usados na comparacao com IBGE (Fig. 5) -- ver README, secao
# "Decisoes e premissas".
CROP_GROUPS <- list(
  soybean   = c(5L, 6L, 7L, 8L, 9L),  # qualquer classe com soja
  corn      = 5L,                      # Soy_Corn (milho safrinha)
  cotton    = c(2L, 6L),               # Fallow_Cotton + Soy_Cotton
  sunflower = 9L                       # Soy_Sunflower
)

# ---- Parametros de modelagem (artigo + PANGAEA) -----------------------------
SEED <- 20200101L

SOM <- list(
  grid_x = 12L, grid_y = 12L, rlen = 100L, alpha = 1,
  distance = "euclidean",   # artigo nao especifica; "dtw" e o padrao do sits
  n_runs = 10L,             # artigo: "SOM foi executado varias vezes"
  min_reliability = 0.80    # artigo: amostras boas casam >= 80% das vezes
)

SVM <- list(
  kernel = "radial",
  cost   = 1,
  # gamma = 1/92 = 1/(23 passos x 4 bandas); calculado em 05_train_svm.R
  folds  = 5L
)
BANDS <- c("NDVI", "EVI", "NIR", "MIR")

SMOOTH <- list(
  window_size   = 3L,    # vizinhanca de Chebyshev = 1 (janela 3x3)
  smoothness    = 10,    # sigma^2 = 10 para todas as classes
  neigh_fraction = 1.0   # todos os vizinhos da janela
)

# Fonte de series temporais (colecao 6.1 do MPC; o artigo usou a colecao 6)
CUBE <- list(source = "MPC", collection = "MOD13Q1-6.1")

# ---- Mascaras (formato esperado em data/raw/masks/) -------------------------
# Os codigos replicam os usados em main.R (Zenodo).  Ver README.md.
MASK_FILES <- list(
  urban            = list(file = "urban_area.tif",          value = 11L),
  water            = list(file = "water.tif",               value = 12L),
  sugarcane_dir    = "sugarcane",                           # canasat_YYYY.tif
  sugarcane_years  = 2003:2016,
  sugarcane_value  = 10L,
  prodes_forest    = list(file = "prodes_amz_2001_forest.tif", value = 13L),
  prodes_2001      = list(file = "prodes_amz_2001.tif",
                          nonforest = 4L, deforestation = 7L),
  cerrado_2000     = list(file = "prodes_cerrado_2000.tif",
                          non_anthropized = 0L, anthropized = 14L)
)

