#!/usr/bin/env Rscript
# =============================================================================
# 01_download_core.R -- aquisicao dos dados e do codigo originais
#
#  (a) Zenodo  doi:10.5281/zenodo.3354379  -> codigo-fonte original (main.R)
#  (b) PANGAEA doi:10.1594/PANGAEA.899706  -> 17 mapas anuais (GeoTIFF),
#      estilo QGIS (.qml) e CSV com as 1.892 amostras de treinamento
#
# A lista de arquivos do PANGAEA e lida do proprio registro (tabela
# "textfile"), nao codificada; tamanhos sao conferidos contra o registro e o
# MD5 do Zenodo contra a API.  Proveniencia (sha256) vai para raw/MANIFEST.csv.
#
# Uso: Rscript scripts/01_download_core.R [--force]
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
ROOT <- dirname(.d); source(file.path(.d, "utils.R"))

need_pkgs(c("curl", "jsonlite", "digest"))
force <- cli_flag("force")

# ---- (a) Zenodo -------------------------------------------------------------
log_msg("Zenodo: registro %s", ZENODO_RECORD_ID)
rec <- jsonlite::fromJSON(sprintf("https://zenodo.org/api/records/%s", ZENODO_RECORD_ID))
log_msg("  titulo : %s", rec$metadata$title)
log_msg("  versao : %s", rec$metadata$version)
log_msg("  licenca: %s", rec$metadata$license$id %||% "ver registro")

zf <- rec$files
stopifnot(nrow(zf) >= 1L)
for (i in seq_len(nrow(zf))) {
  fname <- basename(zf$key[i])
  dest  <- file.path(DIR$zenodo, fname)
  md5   <- sub("^md5:", "", zf$checksum[i])
  download_file(zf$links$self[i], dest, md5 = md5, overwrite = force)
  write_manifest(dest, source = paste0("zenodo:", ZENODO_RECORD_ID), url = zf$links$self[i])
  if (grepl("\\.zip$", fname)) {
    exdir <- file.path(DIR$zenodo, "src")
    ensure_dir(exdir)
    utils::unzip(dest, exdir = exdir)
    mains <- list.files(exdir, pattern = "^main\\.R$", recursive = TRUE, full.names = TRUE)
    log_msg("  codigo original extraido: %s", paste(rel_to(mains, DIR$zenodo), collapse = ", "))
  }
}

# ---- (b) PANGAEA ------------------------------------------------------------
log_msg("PANGAEA: %s", PANGAEA_DOI)
tab_file <- file.path(DIR$pangaea, "pangaea_899706_index.tab")
download_file(PANGAEA_TABLE, tab_file, overwrite = force)

lines <- readLines(tab_file, encoding = "UTF-8", warn = FALSE)
hdr_end <- which(trimws(lines) == "*/")[1]
stopifnot(!is.na(hdr_end))
idx <- utils::read.delim(text = paste(lines[(hdr_end + 1L):length(lines)], collapse = "\n"),
                         sep = "\t", quote = "", stringsAsFactors = FALSE,
                         check.names = FALSE, encoding = "UTF-8")
names(idx) <- c("content", "format", "size_kb", "file", "url")

expected <- c(sprintf("mt_%d_v3_1.tif", YEARS), "QGIS_style_mt_v3.qml",
              "training_dataset_v3.csv")
missing <- setdiff(expected, idx$file)
if (length(missing)) stop("Arquivos esperados ausentes no registro PANGAEA: ",
                          paste(missing, collapse = ", "))

for (i in seq_len(nrow(idx))) {
  dest <- file.path(DIR$pangaea, idx$file[i])
  download_file(idx$url[i], dest, overwrite = force)
  got_kb <- file.size(dest) / 1024
  if (abs(got_kb - idx$size_kb[i]) > 1) {
    warning(sprintf("Tamanho divergente em %s: %.1f kB (registro: %.1f kB)",
                    idx$file[i], got_kb, idx$size_kb[i]))
  }
  write_manifest(dest, source = paste0("pangaea:", PANGAEA_DOI), url = idx$url[i])
}

# ---- Verificacoes -----------------------------------------------------------
smp <- utils::read.csv(file.path(DIR$pangaea, "training_dataset_v3.csv"),
                       stringsAsFactors = FALSE)
stopifnot(identical(names(smp), c("id", "longitude", "latitude", "start_date", "end_date", "label")))
log_msg("amostras de treinamento: %d (esperado: 1892)", nrow(smp))
if (nrow(smp) != 1892L) warning("Numero de amostras difere do artigo (1.892).")
print(table(smp$label))

log_msg("OK. Proximo passo: Rscript scripts/02_download_reference.R")

