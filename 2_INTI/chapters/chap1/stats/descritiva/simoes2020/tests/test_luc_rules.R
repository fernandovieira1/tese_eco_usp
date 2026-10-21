#!/usr/bin/env Rscript
# =============================================================================
# tests/test_luc_rules.R -- testes unitarios das regras de pos-processamento
# Uso: Rscript tests/test_luc_rules.R   (sem dependencias alem do R base)
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
.here <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
ROOT <- if (basename(.here) == "tests") dirname(.here) else .here
source(file.path(ROOT, "scripts", "luc_rules.R"))
source(file.path(ROOT, "scripts", "config.R"), local = TRUE) -> .ignored

n_ok <- 0L; n_fail <- 0L
check <- function(name, got, want) {
  if (identical(as.integer(got), as.integer(want))) { n_ok <<- n_ok + 1L; cat("ok   ", name, "\n") }
  else { n_fail <<- n_fail + 1L; cat("FAIL ", name, "\n   got : ", got, "\n   want: ", want, "\n") }
}
row <- function(...) matrix(as.integer(c(...)), nrow = 1)
t4  <- function(...) as.vector(luc_apply_table4(row(...)))
lc  <- function(...) as.vector(luc_calculus(row(...)))

# ---- Tabela 4, regras 1-8 ---------------------------------------------------
check("R1  C F F P      -> C C C P",   t4(1, 3, 3, 4),       c(1, 1, 1, 4))
check("R2  C C P C      -> C C C C",   t4(1, 1, 4, 1),       c(1, 1, 1, 1))
check("R3  C C Soy C    -> C C C C",   t4(1, 1, 7, 1),       c(1, 1, 1, 1))
check("R3b C C Pasture(sem soja) ok",  t4(1, 1, 4, 4),       c(1, 1, 4, 4))
check("R4  P P C C P    -> P P P P P", t4(4, 4, 1, 1, 4),    c(4, 4, 4, 4, 4))
check("R5  F C F F      -> F F F F",   t4(3, 1, 3, 3),       c(3, 3, 3, 3))
check("R6  F F C F      -> F F F F",   t4(3, 3, 1, 3),       c(3, 3, 3, 3))
check("R7  F C F        -> F F F",     t4(3, 1, 3),          c(3, 3, 3))
check("R8  F C          -> F F",       t4(3, 1),             c(3, 3))
check("R8  F C C C      -> F F F F",   t4(3, 1, 1, 1),       c(3, 3, 3, 3))
check("sem regra: C P C (so 2 C) mantem", t4(1, 4, 1),       c(1, 4, 1))
check("sem regra: P F P mantem (antes de SV)", t4(4, 3, 4),  c(4, 3, 4))

# ---- Vegetacao secundaria (regras 9-10) -------------------------------------
check("R9  F F P F      -> F F P SV",  lc(3, 3, 4, 3),       c(3, 3, 4, 13))
check("R10 P P F P P    -> P P SV P P", lc(4, 4, 3, 4, 4),   c(4, 4, 13, 4, 4))
check("floresta estavel nao vira SV",  lc(3, 3, 3, 3),       c(3, 3, 3, 3))
check("P -> F permanece SV",           lc(4, 4, 3, 3),       c(4, 4, 13, 13))
check("SV base 2001 -> F vira SV",     lc(13, 3, 3),         c(13, 13, 13))
check("Cerrado -> F e cerrado (R1)",   lc(1, 1, 3, 3),       c(1, 1, 1, 1))
check("Soja -> F vira SV",             lc(6, 6, 3),          c(6, 6, 13))

# ---- NA e dimensoes ---------------------------------------------------------
M <- rbind(c(NA, NA, NA), c(3, 4, 3))
out <- luc_calculus(M)
check("NA preservado",                 is.na(out[1, ]),      c(1, 1, 1))
check("linha valida processada",       out[2, ],             c(3, 4, 13))
check("17 anos: forma preservada",     dim(luc_calculus(matrix(3L, 5, 17))), c(5, 17))

# ---- Invariantes apos Tabela 4 (regras 1-8 em sequencia, como em main.R) ----
set.seed(1)
R <- matrix(sample(c(1L, 3L, 4L, 5L), 20000 * 17, replace = TRUE, prob = c(.3, .3, .3, .1)), ncol = 17)
A <- luc_apply_table4(R)
bad_fc <- sum(A[, -17] == 3L & A[, -1] == 1L)
bad_cf <- sum(A[, -17] == 1L & A[, -1] == 3L)
check("invariante: nenhum par (F,C) consecutivo apos regras 1-8", bad_fc, 0L)
check("invariante: nenhum par (C,F) consecutivo apos regras 1-8", bad_cf, 0L)
check("ordem sequencial main.R: C C S C P C -> C C C C P C (1 passada)",
      t4(1, 1, 5, 1, 4, 1), c(1, 1, 1, 1, 4, 1))

# ---- Regras do mapa-base 2001 ----------------------------------------------
cfg <- MASK_FILES
x   <- c(3, 3, 3, 3, 3, 4, 12, 3)         # SVM + mascaras
pf  <- c(13, 0, 0, 0, 0, 13, 13, 0)       # PRODES floresta
pc  <- c(0, 4, 7, 0, 0, 0, 0, 0)          # PRODES classes (4 nao-floresta, 7 desmat.)
cc  <- c(0, 0, 0, 0, 14, 0, 0, 0)         # Cerrado 2000 (0 nao-antropizado, 14 antropizado)
res <- apply_base_map_rules(as.integer(x), as.integer(pf), as.integer(pc), as.integer(cc), cfg)
check("base: PRODES floresta -> Forest (inclui sobre pastagem/agua)", res[c(1, 6, 7)], c(3, 3, 3))
check("base: F & PRODES nao-floresta -> Cerrado",   res[2], 1)
check("base: F & PRODES desmatamento -> SV",        res[3], 13)
check("base: F & Cerrado2000 nao-antrop. -> Cerrado", res[4], 1)
check("base: F & Cerrado2000 antropizado -> SV",    res[5], 13)
check("base: sem mascara, F permanece",             res[8], 1)  # cc==0 e nao-antropizado -> Cerrado

cat(sprintf("\n%d ok, %d falhas\n", n_ok, n_fail))
if (n_fail > 0L) quit(status = 1L)

