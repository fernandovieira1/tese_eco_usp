#!/usr/bin/env Rscript
# =============================================================================
# run_all.R -- orquestrador do pipeline de replicacao de Simoes et al. (2020)
#
# Modos:
#   Rscript run_all.R
#     Executa setup -> aquisicao (Zenodo, PANGAEA, IBGE, PRODES) -> testes
#     unitarios do LUC Calculus -> demonstracao do pipeline sits (SOM, SVM,
#     classificacao + suavizacao Bayesiana sigma^2=10, mascaras e LUC Calculus)
#     -> tabelas descritivas anuais (2001-2017) -> Figura 5 -> Figura 6.
#
#   Rscript run_all.R --full-sits
#     Executa o pipeline sits completo (03 a 08) sobre todos os tiles MOD13Q1
#     de Mato Grosso via STAC (Microsoft Planetary Computer) em vez do modo DEMO.
#     Requer conexao de rede estavel, dezenas de GB em disco e varias horas de CPU.
# =============================================================================
.f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
ROOT <- if (is.na(.f)) getwd() else dirname(normalizePath(.f, winslash = "/"))
full_sits <- "--full-sits" %in% commandArgs(TRUE)

run_step <- function(rel_script, env_vars = character()) {
  script_path <- file.path(ROOT, rel_script)
  cat(sprintf("\n==================== %s ====================\n", rel_script))
  old_env <- Sys.getenv(names(env_vars), unset = NA_character_)
  if (length(env_vars)) do.call(Sys.setenv, as.list(env_vars))
  on.exit({
    for (nm in names(env_vars)) {
      if (is.na(old_env[[nm]])) Sys.unsetenv(nm) else do.call(Sys.setenv, setNames(list(old_env[[nm]]), nm))
    }
  }, add = TRUE)
  status <- system2(file.path(R.home("bin"), "Rscript"), args = shQuote(script_path))
  if (status != 0L) stop("Falha ao executar ", rel_script, " (status = ", status, ")", call. = FALSE)
}

run_step("setup_project.R")
run_step("scripts/01_download_core.R")
run_step("scripts/02_download_reference.R")
run_step("tests/test_luc_rules.R")

sits_env <- if (full_sits) c(SIMOES_DEMO = "0") else c(SIMOES_DEMO = "1")
run_step("scripts/03_extract_timeseries.R", sits_env)
run_step("scripts/04_som_quality_control.R", sits_env)
run_step("scripts/05_train_svm.R", sits_env)
run_step("scripts/06_classify_smooth.R", sits_env)
run_step("scripts/07_apply_masks.R", sits_env)
run_step("scripts/08_luc_calculus.R", sits_env)

run_step("scripts/09_area_tables.R")
run_step("scripts/10_fig5_area_comparison.R")
run_step("scripts/11_fig6_maps.R")

cat("\nPipeline concluido com sucesso.\n")

