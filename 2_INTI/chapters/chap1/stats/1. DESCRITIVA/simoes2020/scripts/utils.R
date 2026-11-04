# =============================================================================
# utils.R -- funcoes auxiliares compartilhadas
# Uso (bootstrap no topo de cada script):
#   .f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
#   .d <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
#   if (basename(.d) != "scripts") .d <- file.path(.d, "scripts")
#   ROOT <- dirname(.d); source(file.path(.d, "utils.R"))
# =============================================================================

stopifnot(exists("ROOT"), exists(".d"))
source(file.path(.d, "config.R"))

# Operador %||% (base R >= 4.4); definicao de reserva para versoes antigas.
if (!exists("%||%", envir = baseenv())) {
  `%||%` <- function(x, y) if (is.null(x)) y else x
}

# ---- Mensagens e checagens --------------------------------------------------
log_msg <- function(...) {
  cat(format(Sys.time(), "[%Y-%m-%d %H:%M:%S] "), sprintf(...), "\n", sep = "")
  invisible(NULL)
}

need_pkgs <- function(pkgs) {
  miss <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
  if (length(miss)) {
    stop("Pacotes ausentes: ", paste(miss, collapse = ", "),
         "\nInstale com: install.packages(c(",
         paste(sprintf("'%s'", miss), collapse = ", "), "))", call. = FALSE)
  }
  if ("sits" %in% pkgs && requireNamespace("torch", quietly = TRUE) &&
      !isTRUE(tryCatch(torch::torch_is_installed(), error = function(e) FALSE))) {
    ns <- asNamespace("sits")
    for (fn in c(".torch_gpu_classification", ".torch_cuda_enabled")) {
      if (exists(fn, envir = ns, inherits = FALSE)) {
        unlockBinding(fn, ns)
        assign(fn, function(...) FALSE, envir = ns)
        lockBinding(fn, ns)
      }
    }
  }
  invisible(TRUE)
}

ensure_dir <- function(path) {
  if (!dir.exists(path)) dir.create(path, recursive = TRUE, showWarnings = FALSE)
  invisible(path)
}

require_file <- function(path, hint = NULL) {
  if (!file.exists(path)) {
    stop("Arquivo nao encontrado: ", path,
         if (!is.null(hint)) paste0("\n", hint) else "", call. = FALSE)
  }
  invisible(path)
}

# ---- Argumentos de linha de comando ----------------------------------------
# --years=2001:2005 | --years=2001,2017    --force
cli_flag <- function(name) paste0("--", name) %in% commandArgs(TRUE)

cli_years <- function(default = YEARS) {
  a <- grep("^--years=", commandArgs(TRUE), value = TRUE)
  if (!length(a)) return(default)
  tok <- strsplit(sub("^--years=", "", a[1]), ",", fixed = TRUE)[[1]]
  yrs <- unlist(lapply(tok, function(t) {
    if (grepl(":", t, fixed = TRUE)) {
      p <- as.integer(strsplit(t, ":", fixed = TRUE)[[1]])
      seq.int(p[1], p[2])
    } else as.integer(t)
  }))
  if (anyNA(yrs) || any(!yrs %in% YEARS)) {
    stop("--years invalido; use anos entre ", min(YEARS), " e ", max(YEARS))
  }
  sort(unique(yrs))
}

# ---- Download com verificacao e manifesto ----------------------------------
download_file <- function(url, dest, md5 = NULL, min_bytes = 1L,
                          overwrite = FALSE, retries = 3L) {
  need_pkgs("curl")
  ensure_dir(dirname(dest))
  if (file.exists(dest) && !overwrite) {
    if (is.null(md5) || unname(tools::md5sum(dest)) == md5) {
      log_msg("ja existe: %s", basename(dest))
      return(invisible(dest))
    }
    log_msg("md5 divergente, baixando de novo: %s", basename(dest))
  }
  tmp <- paste0(dest, ".part")
  ok <- FALSE
  for (i in seq_len(retries)) {
    res <- try(curl::curl_download(url, tmp, quiet = TRUE,
                                   handle = curl::new_handle(
                                     timeout = 600, followlocation = TRUE)),
               silent = TRUE)
    if (!inherits(res, "try-error") && file.exists(tmp) &&
        file.size(tmp) >= min_bytes) { ok <- TRUE; break }
    log_msg("falha (%d/%d): %s", i, retries, basename(dest)); Sys.sleep(2 * i)
  }
  if (!ok) stop("Download falhou: ", url, call. = FALSE)
  if (!is.null(md5) && unname(tools::md5sum(tmp)) != md5) {
    unlink(tmp); stop("MD5 nao confere para ", basename(dest), call. = FALSE)
  }
  file.rename(tmp, dest)
  log_msg("baixado: %s (%.1f kB)", basename(dest), file.size(dest) / 1024)
  invisible(dest)
}

# Caminho relativo a uma base (sem regex).
rel_to <- function(path, base) {
  p <- normalizePath(path, winslash = "/", mustWork = FALSE)
  b <- normalizePath(base, winslash = "/", mustWork = FALSE)
  if (startsWith(p, paste0(b, "/"))) substring(p, nchar(b) + 2L) else p
}

# Registra proveniencia (sha256) em <raw>/MANIFEST.csv sem duplicar linhas.
write_manifest <- function(path, source, url) {
  need_pkgs("digest")
  mf <- file.path(DIR$raw, "MANIFEST.csv")
  row <- data.frame(
    file = rel_to(path, DIR$raw),
    source = source, url = url, bytes = file.size(path),
    sha256 = digest::digest(path, algo = "sha256", file = TRUE),
    retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
    stringsAsFactors = FALSE
  )
  old <- if (file.exists(mf)) utils::read.csv(mf, stringsAsFactors = FALSE) else NULL
  if (!is.null(old)) old <- old[old$file != row$file, , drop = FALSE]
  utils::write.csv(rbind(old, row), mf, row.names = FALSE, fileEncoding = "UTF-8")
  invisible(row)
}

write_table <- function(df, name, dir = DIR$tables) {
  ensure_dir(dir)
  p <- file.path(dir, name)
  utils::write.csv(df, p, row.names = FALSE, fileEncoding = "UTF-8")
  log_msg("tabela: %s", rel_to(p, ROOT))
  invisible(p)
}

# ---- Caminhos dos mapas anuais ---------------------------------------------
published_map_path <- function(year) {
  file.path(DIR$pangaea, sprintf("mt_%d_v3_1.tif", year))
}
replicated_map_path <- function(year) {
  file.path(DIR$final, sprintf("mt_%d.tif", year))
}
map_path <- function(year, source = MAPS_SOURCE) {
  if (source == "published") published_map_path(year) else replicated_map_path(year)
}

# ---- Raster -----------------------------------------------------------------
# Area do pixel em hectares.  Os mapas estao na projecao senoidal MODIS, que e
# equivalente em area: a area de cada pixel e res_x * res_y em qualquer latitude
# (~5,37 ha para 231,656 m).  Para qualquer outra projecao, usa-se cellSize().
pixel_area_ha <- function(r) {
  proj <- terra::crs(r, proj = TRUE)
  if (grepl("+proj=sinu", proj, fixed = TRUE)) {
    prod(terra::res(r)) / 1e4
  } else {
    stop("CRS nao e senoidal; calcule area por pixel com terra::cellSize().")
  }
}

# Contagem de pixels por codigo de classe (sem NA), em data.frame.
class_counts <- function(r) {
  f <- terra::freq(r)
  out <- data.frame(code = as.integer(f$value), pixels = as.numeric(f$count))
  out[!is.na(out$code), , drop = FALSE]
}

# Processa uma pilha de rasters (mesma geometria) em blocos de linhas.
#   fun(M): M e matriz [pixels x camadas] (inteiros; NA = fora de MT);
#           deve devolver matriz [pixels x length(out_paths)].
process_stack_chunks <- function(in_paths, out_paths, fun, datatype = "INT1U",
                                 chunk_cells = 3e6) {
  rs <- lapply(in_paths, terra::rast)
  nr <- terra::nrow(rs[[1]]); nc <- terra::ncol(rs[[1]])
  for (r in rs) stopifnot(terra::nrow(r) == nr, terra::ncol(r) == nc)
  outs <- lapply(seq_along(out_paths), function(i) terra::rast(rs[[1]]))
  tmp_paths <- paste0(out_paths, ".part.tif")
  for (i in seq_along(outs)) {
    terra::writeStart(outs[[i]], tmp_paths[i], overwrite = TRUE,
                      datatype = datatype, gdal = c("COMPRESS=DEFLATE"))
  }
  on.exit(suppressWarnings(for (i in seq_along(outs)) try(terra::writeStop(outs[[i]]), silent = TRUE)), add = TRUE)
  step <- max(1L, floor(chunk_cells / nc))
  for (r0 in seq(1L, nr, by = step)) {
    n <- min(step, nr - r0 + 1L)
    M <- vapply(rs, function(r) as.integer(terra::values(r, row = r0, nrows = n, mat = FALSE)),
                integer(n * nc))
    if (is.null(dim(M))) M <- matrix(M, ncol = length(rs))
    res <- fun(M)
    stopifnot(is.matrix(res), nrow(res) == nrow(M), ncol(res) == length(out_paths))
    for (i in seq_along(outs)) terra::writeValues(outs[[i]], res[, i], r0, n)
  }
  for (i in seq_along(outs)) terra::writeStop(outs[[i]])
  on.exit()
  file.rename(tmp_paths, out_paths)
  invisible(out_paths)
}

# Leitura da paleta oficial do arquivo QML (QGIS) do PANGAEA.
read_qml_palette <- function(qml) {
  need_pkgs("xml2")
  x <- xml2::read_xml(qml)
  e <- xml2::xml_find_all(x, ".//rasterrenderer/colorPalette/paletteEntry")
  df <- data.frame(
    code  = as.integer(xml2::xml_attr(e, "value")),
    color = xml2::xml_attr(e, "color"),
    label = xml2::xml_attr(e, "label"),
    stringsAsFactors = FALSE
  )
  df[df$code %in% 1:13, , drop = FALSE]
}
