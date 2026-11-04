# =============================================================================
# luc_rules.R -- regras de pos-processamento (funcoes puras, testaveis)
#
# Implementa, sobre matrizes [pixels x anos], as regras de Land Use Change
# Calculus (LUC Calculus; Maciel et al., 2018) usadas por Simoes et al. (2020),
# Tabela 4, e as regras do mapa-base 2001, Tabela 3.
#
# Referencia de implementacao: main.R do Zenodo (passos 10-19), cujas regras
# 11-18 sao reproduzidas aqui como janelas deslizantes aplicadas EM SEQUENCIA e
# com atualizacao "in place" (o resultado de uma janela alimenta a seguinte),
# exatamente como no codigo original.
#
# Codigos (pre-LUC): 1 Cerrado, 3 Forest, 4 Pasture, 5-9 Soy_*, 13 SecVeg.
# NA (fora de MT) nunca e alterado.
# =============================================================================

LUC_CODES <- list(cerrado = 1L, forest = 3L, pasture = 4L, soy = 5:9, secveg = 13L)

# Janela deslizante: onde a sequencia observada em k anos consecutivos casa com
# `pattern` (lista de vetores de codigos aceitos por posicao), substitui as
# posicoes indicadas em `target` (lista nomeada: nome = posicao na janela).
luc_slide <- function(M, pattern, target) {
  stopifnot(is.matrix(M), is.list(pattern), is.list(target))
  k <- length(pattern); nt <- ncol(M)
  if (nt < k) return(M)
  for (s in seq_len(nt - k + 1L)) {
    ok <- rep(TRUE, nrow(M))
    for (j in seq_len(k)) ok <- ok & (M[, s + j - 1L] %in% pattern[[j]])
    idx <- which(ok)
    if (length(idx)) {
      for (j in names(target)) M[idx, s + as.integer(j) - 1L] <- as.integer(target[[j]])
    }
  }
  M
}

# Regras 1-8 da Tabela 4 (passos 11-18 de main.R), em ordem.
luc_rules_table4 <- function() {
  C <- LUC_CODES$cerrado; Fo <- LUC_CODES$forest; P <- LUC_CODES$pasture; S <- LUC_CODES$soy
  list(
    r1_CF_CC     = list(pattern = list(C, Fo),                target = list("2" = C)),
    r2_CCPC_CCCC = list(pattern = list(C, C, P, C),           target = list("3" = C)),
    r3_CCSC_CCCC = list(pattern = list(C, C, S, C),           target = list("3" = C)),
    r4_PPCCP_P5  = list(pattern = list(P, P, C, C, P),        target = list("3" = P, "4" = P)),
    r5_FCFF_FFFF = list(pattern = list(Fo, C, Fo, Fo),        target = list("2" = Fo)),
    r6_FFCF_FFFF = list(pattern = list(Fo, Fo, C, Fo),        target = list("3" = Fo)),
    r7_FCF_FFF   = list(pattern = list(Fo, C, Fo),            target = list("2" = Fo)),
    r8_FC_FF     = list(pattern = list(Fo, C),                target = list("2" = Fo))
  )
}

luc_apply_table4 <- function(M) {
  for (r in luc_rules_table4()) M <- luc_slide(M, r$pattern, r$target)
  M
}

# Regras 9-10 (vegetacao secundaria): uma observacao de Forest e reclassificada
# como Secondary Vegetation (13) quando o pixel teve, em algum ano anterior da
# serie (incluindo o ano-base), uma classe diferente de Forest (inclusive SV).
#   F F P F*  -> F F P SV*        (regra 9)
#   P P F* P  -> P P SV* P        (regra 10)
# Interpretacao dos predicados RECUR/EVOLVE do pacote lucCalculus; ver README.
luc_secondary_vegetation <- function(M) {
  Fo <- LUC_CODES$forest; SV <- LUC_CODES$secveg
  seen_non_forest <- rep(FALSE, nrow(M))
  for (t in seq_len(ncol(M))) {
    x <- M[, t]
    if (t > 1L) {
      idx <- which(x %in% Fo & seen_non_forest)
      if (length(idx)) M[idx, t] <- SV
    }
    seen_non_forest <- seen_non_forest | (!is.na(x) & !(x %in% Fo))
  }
  M
}

luc_calculus <- function(M) {
  storage.mode(M) <- "integer"
  luc_secondary_vegetation(luc_apply_table4(M))
}

# Regras do mapa-base 2001 (Tabela 3; passos 7-10 de main.R).  Vetores [pixels].
#   PRODES forest                       -> Forest
#   Forest & PRODES non-forest          -> Cerrado
#   Forest & PRODES deforestation       -> Secondary Vegetation
#   Forest & Cerrado2000 non-anthrop.   -> Cerrado
#   Forest & Cerrado2000 anthropized    -> Secondary Vegetation
# `cfg` = MASK_FILES (config.R) com os codigos dos mapas de entrada.
apply_base_map_rules <- function(x, prodes_forest, prodes_class, cerrado_class, cfg) {
  stopifnot(length(x) == length(prodes_forest), length(x) == length(prodes_class),
            length(x) == length(cerrado_class))
  Fo <- LUC_CODES$forest; C <- LUC_CODES$cerrado; SV <- LUC_CODES$secveg
  has <- !is.na(x)
  is_pf <- has & (prodes_forest %in% cfg$prodes_forest$value)
  x[is_pf] <- Fo
  f <- has & !is_pf & x == Fo
  f[is.na(f)] <- FALSE
  # etapa PRODES Amazonia (aplicada primeiro, como em main.R)
  nf  <- f & (prodes_class %in% cfg$prodes_2001$nonforest)
  df  <- f & (prodes_class %in% cfg$prodes_2001$deforestation)
  x[nf] <- C; x[df] <- SV
  # etapa PRODES Cerrado (somente o que ainda e Forest)
  f2  <- f & !nf & !df
  na_ <- f2 & (cerrado_class %in% cfg$cerrado_2000$non_anthropized)
  an_ <- f2 & (cerrado_class %in% cfg$cerrado_2000$anthropized)
  x[na_] <- C; x[an_] <- SV
  x
}

