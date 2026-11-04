#!/usr/bin/env Rscript
# =============================================================================
# setup_project.R -- cria a arvore de diretorios do projeto simoes2020
#
# Replicacao de: Simoes et al. (2020) "Land use and cover maps for Mato Grosso
# State in Brazil from 2001 to 2017". Scientific Data 7, 34.
# https://doi.org/10.1038/s41597-020-0371-4
#
# Uso (a partir de qualquer diretorio):
#   Rscript setup_project.R
#
# Variaveis de ambiente opcionais:
#   SIMOES_DATA_ROOT  raiz alternativa para data/ (ex.: 2_INTI/xdata/simoes2020).
#                     Por padrao, data/ fica dentro deste projeto.
#
# O script e idempotente: nunca apaga nem sobrescreve nada.
# =============================================================================

.args <- commandArgs(FALSE)
.file <- sub("^--file=", "", grep("^--file=", .args, value = TRUE)[1])
ROOT <- if (is.na(.file)) getwd() else dirname(normalizePath(.file, winslash = "/"))

DATA_ROOT <- Sys.getenv("SIMOES_DATA_ROOT", unset = file.path(ROOT, "data"))
DATA_ROOT <- normalizePath(DATA_ROOT, winslash = "/", mustWork = FALSE)

dirs <- c(
  # dados
  file.path(DATA_ROOT, "raw", "zenodo"),      # codigo-fonte original (Zenodo)
  file.path(DATA_ROOT, "raw", "pangaea"),     # mapas, amostras e estilo QGIS (PANGAEA)
  file.path(DATA_ROOT, "raw", "ancillary"),   # IBGE/SIDRA, PRODES, limite de MT
  file.path(DATA_ROOT, "raw", "masks"),       # mascaras (cana, agua, urbano, PRODES)
  file.path(DATA_ROOT, "raw", "masks", "sugarcane"),
  file.path(DATA_ROOT, "processed", "classified"),  # saida SVM + suavizacao
  file.path(DATA_ROOT, "processed", "masked"),      # apos mascaras + mapa-base 2001
  file.path(DATA_ROOT, "processed", "final"),       # apos LUC Calculus
  # codigo
  file.path(ROOT, "scripts"),
  file.path(ROOT, "tests"),
  # resultados
  file.path(ROOT, "outputs", "maps"),
  file.path(ROOT, "outputs", "figures"),
  file.path(ROOT, "outputs", "tables")
)

for (d in dirs) {
  created <- !dir.exists(d)
  dir.create(d, recursive = TRUE, showWarnings = FALSE)
  keep <- file.path(d, ".gitkeep")
  if (!file.exists(keep) && length(list.files(d, all.files = FALSE)) == 0L) {
    file.create(keep)
  }
  cat(sprintf("[%s] %s\n", if (created) "criado " else "existe ", d))
}

cat("\nProjeto em: ", ROOT, "\n", sep = "")
cat("Dados em  : ", DATA_ROOT, "\n", sep = "")
cat("Proximo passo: Rscript scripts/01_download_core.R\n")

