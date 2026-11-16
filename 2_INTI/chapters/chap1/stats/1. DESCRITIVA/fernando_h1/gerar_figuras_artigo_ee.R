# ==============================================================================
# Geração padronizada das figuras do Capítulo 1 / Artigo (Ecological Economics)
# ==============================================================================
suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(readr)
})

raiz <- normalizePath(".", winslash = "/", mustWork = TRUE)
if (!dir.exists(file.path(raiz, "2_INTI"))) {
  stop("Execute a partir da raiz do repositório tese_eco_usp.", call. = FALSE)
}

dir_dados_h1   <- file.path(raiz, "2_INTI/chapters/chap1/stats/1. DESCRITIVA/resultados_h1/dados")
dir_dados_pre  <- file.path(raiz, "2_INTI/chapters/chap1/stats/0. PRELIMINARES/dados")
dir_modelos    <- file.path(raiz, "2_INTI/audit/readequacao_artigo1_20261112/saidas/modelos_prec_v2")
out_fig_main   <- file.path(raiz, "2_INTI/chapters/chap1/stats/figuras")
out_fig_res    <- file.path(raiz, "2_INTI/chapters/chap1/stats/1. DESCRITIVA/resultados_h1/figuras")
dir.create(out_fig_main, recursive = TRUE, showWarnings = FALSE)
dir.create(out_fig_res, recursive = TRUE, showWarnings = FALSE)

# Tema editorial unificado (limpo, sem títulos/captions internos, fonte >= 9pt)
tema_ee <- theme_bw(base_size = 10.5) +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(color = "grey91", linewidth = 0.35),
    panel.border = element_rect(color = "grey45", linewidth = 0.5),
    strip.background = element_rect(fill = "grey96", color = "grey70", linewidth = 0.4),
    strip.text = element_text(face = "bold", size = 9.5, color = "grey15"),
    axis.title = element_text(size = 9.5, color = "grey15"),
    axis.text = element_text(size = 8.8, color = "grey25"),
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size = 9),
    legend.key.width = unit(1.3, "cm"),
    legend.margin = margin(t = 0, b = 0)
  )
theme_set(tema_ee)

rotulo_pt <- function(x) format(x, decimal.mark = ",", big.mark = ".", scientific = FALSE, trim = TRUE)
cores_biomas <- c("Amazônia" = "#009E73", "Cerrado" = "#D55E00", "Pantanal" = "#0072B2")

salvar_padrao <- function(g, nome, largura = 8, altura = 4.5, copiar_res = FALSE) {
  destinos <- if (copiar_res) c(out_fig_main, out_fig_res) else out_fig_main
  for (d in destinos) {
    ggsave(file.path(d, paste0(nome, ".png")), g, width = largura, height = altura, dpi = 320, bg = "white")
    ggsave(file.path(d, paste0(nome, ".pdf")), g, width = largura, height = altura,
           device = grDevices::pdf, useDingbats = FALSE, encoding = "ISOLatin1.enc")
  }
  cat("Salvo:", nome, sprintf("(%.1f x %.1f in)\n", largura, altura))
}

# 1. fig01_conversao ---------------------------------------------------------
conv <- read_csv(file.path(dir_dados_h1, "conversao_anual.csv"), show_col_types = FALSE) |>
  mutate(
    destino = factor(destino, levels = c("Agricultura", "Pastagem")),
    amostra = factor(amostra, levels = c("Municípios fixos", "Disponível no ano"))
  )

g1 <- ggplot(conv, aes(ano, taxa_agregada_pct, color = amostra, linetype = amostra)) +
  geom_line(linewidth = 0.8) +
  facet_wrap(~ destino, ncol = 1, scales = "free_y") +
  scale_color_manual(values = c("Municípios fixos" = "#0072B2", "Disponível no ano" = "#666666")) +
  scale_linetype_manual(values = c("Municípios fixos" = "solid", "Disponível no ano" = "dashed")) +
  scale_x_continuous(breaks = c(2001, 2005, 2010, 2015, 2020, 2024)) +
  scale_y_continuous(limits = c(0, NA), labels = rotulo_pt) +
  labs(x = "Ano final da transição", y = "Conversão bruta / vegetação nativa inicial (%)")
salvar_padrao(g1, "fig01_conversao", largura = 7.6, altura = 4.6, copiar_res = TRUE)

# 2. fig02_distribuicao ------------------------------------------------------
dist_df <- read_csv(file.path(dir_dados_h1, "distribuicao_municipal.csv"), show_col_types = FALSE) |>
  mutate(
    bioma_predominante = factor(bioma_predominante, levels = c("Amazônia", "Cerrado", "Pantanal")),
    destino = factor(destino, levels = c("Agricultura", "Pastagem"))
  )
cont_fixa <- dist_df |> distinct(codigo_ibge, bioma_predominante) |> count(bioma_predominante)
rot_bio <- setNames(paste0(cont_fixa$bioma_predominante, "\n(n = ", cont_fixa$n, ")"), cont_fixa$bioma_predominante)

g2 <- ggplot(dist_df, aes(bioma_predominante, media_temporal_pct, color = bioma_predominante, shape = bioma_predominante)) +
  geom_point(position = position_jitter(width = 0.14, height = 0, seed = 2026), size = 2.0, alpha = 0.82) +
  facet_wrap(~ destino, scales = "free_y") +
  scale_color_manual(values = cores_biomas, drop = FALSE) +
  scale_shape_manual(values = c("Amazônia" = 16, "Cerrado" = 17, "Pantanal" = 15), drop = FALSE) +
  scale_x_discrete(labels = rot_bio, drop = FALSE) +
  scale_y_continuous(limits = c(0, NA), labels = rotulo_pt) +
  labs(x = "Predominância territorial do município", y = "Média municipal da taxa anual (%)") +
  theme(legend.position = "none")
salvar_padrao(g2, "fig02_distribuicao", largura = 7.6, altura = 3.8, copiar_res = TRUE)

# 3. fig03_precos ------------------------------------------------------------
precos <- read_csv(file.path(dir_dados_h1, "precos_anuais.csv"), show_col_types = FALSE) |>
  mutate(produto = factor(produto, levels = c("Soja", "Milho", "Carne bovina")))

g3 <- ggplot(precos, aes(ano_preco, indice, color = produto, linetype = produto)) +
  geom_line(linewidth = 0.85) +
  scale_color_manual(values = c("Soja" = "#0072B2", "Milho" = "#D55E00", "Carne bovina" = "#333333")) +
  scale_linetype_manual(values = c("Soja" = "solid", "Milho" = "dashed", "Carne bovina" = "dotdash")) +
  scale_x_continuous(breaks = c(2000, 2005, 2010, 2015, 2020, 2023)) +
  scale_y_continuous(limits = c(0, NA), labels = rotulo_pt) +
  labs(x = "Ano da cotação (defasada em t - 1 no painel)", y = "Índice do preço real em USD de 2024 (2000 = 100)")
salvar_padrao(g3, "fig03_precos", largura = 7.6, altura = 3.8, copiar_res = TRUE)

# 4. fig04_ibama (CORREÇÃO DOS EIXOS TROCADOS) -------------------------------
ibama <- read_csv(file.path(dir_dados_h1, "ibama_anual.csv"), show_col_types = FALSE)
pA <- "A. Cobertura dos registros (número de municípios)"
pB <- "B. Autuações na categoria Flora (autos por município)"
ibama_plot <- bind_rows(
  ibama |> transmute(ano, painel = pA, serie = "Contagem observada", valor = n_observado),
  ibama |> transmute(ano, painel = pA, serie = "Classificação completa", valor = n_classificado),
  ibama |> transmute(ano, painel = pB, serie = "Média municipal", valor = media),
  ibama |> transmute(ano, painel = pB, serie = "Mediana municipal", valor = mediana)
) |> mutate(
  painel = factor(painel, levels = c(pA, pB)),
  serie = factor(serie, levels = c("Contagem observada", "Classificação completa", "Média municipal", "Mediana municipal"))
)

g4 <- ggplot(ibama_plot, aes(ano, valor, color = serie, linetype = serie)) +
  geom_line(linewidth = 0.8) +
  facet_wrap(~ painel, ncol = 1, scales = "free_y") +
  scale_x_continuous(breaks = c(2001, 2005, 2010, 2015, 2020, 2024)) +
  scale_y_continuous(limits = c(0, NA), labels = rotulo_pt) +
  scale_color_manual(values = c(
    "Contagem observada" = "#666666", "Classificação completa" = "#0072B2",
    "Média municipal" = "#D55E00", "Mediana municipal" = "#222222"
  )) +
  scale_linetype_manual(values = c(
    "Contagem observada" = "solid", "Classificação completa" = "dashed",
    "Média municipal" = "solid", "Mediana municipal" = "dotdash"
  )) +
  labs(x = "Ano de lavratura", y = NULL) +
  guides(color = guide_legend(nrow = 2), linetype = guide_legend(nrow = 2))
salvar_padrao(g4, "fig04_ibama", largura = 7.6, altura = 5.0, copiar_res = TRUE)

# 5. fig05_lavouras (sem título interno, mesma paleta/tema) ------------------
lav_raw <- read_csv(file.path(dir_dados_pre, "oferta_agricultura_anual.csv"), show_col_types = FALSE) |>
  mutate(
    produto = factor(if_else(produto == "soja", "Soja", "Milho"), levels = c("Soja", "Milho")),
    amostra = factor(amostra, levels = c("Municípios fixos", "Disponível no ano")),
    valor_grafico = if_else(indicador == "rendimento_kg_ha", valor / 1000, valor / 1e6),
    painel = factor(indicador,
      levels = c("area_plantada_ha", "area_colhida_ha", "producao_t", "rendimento_kg_ha"),
      labels = c("Área plantada\n(milhões de ha)", "Área colhida\n(milhões de ha)",
                 "Produção\n(milhões de t)", "Rendimento\n(t / ha colhido)"))
  )
ext_rend <- lav_raw |>
  filter(indicador == "rendimento_kg_ha", amostra == "Municípios fixos", ano %in% range(ano)) |>
  mutate(rotulo = formatC(valor_grafico, format = "f", digits = 2, decimal.mark = ","),
         alinhamento = if_else(ano == min(ano), 0, 1))

g5 <- ggplot(lav_raw, aes(ano, valor_grafico, color = amostra, linetype = amostra)) +
  geom_line(linewidth = 0.75) +
  facet_grid(painel ~ produto, scales = "free_y") +
  geom_point(data = ext_rend, size = 1.8, show.legend = FALSE) +
  geom_label(data = ext_rend, aes(label = rotulo, hjust = alinhamento), vjust = 1.35,
             fill = "white", linewidth = 0, label.padding = grid::unit(0.1, "lines"),
             size = 3.1, fontface = "bold", show.legend = FALSE) +
  scale_color_manual(values = c("Municípios fixos" = "#0072B2", "Disponível no ano" = "#777777")) +
  scale_linetype_manual(values = c("Municípios fixos" = "solid", "Disponível no ano" = "dashed")) +
  scale_x_continuous(breaks = c(2001, 2005, 2010, 2015, 2020, 2024)) +
  scale_y_continuous(limits = c(0, NA), labels = rotulo_pt) +
  labs(x = "Ano", y = NULL)
salvar_padrao(g5, "fig05_lavouras", largura = 7.6, altura = 7.4, copiar_res = FALSE)

# 6. fig09_exportacoes (sem título/caption interno, mesma paleta/tema) -------
exp_raw <- read_csv(file.path(dir_dados_pre, "oferta_exportacoes_anual.csv"), show_col_types = FALSE) |>
  mutate(
    produto = factor(case_when(
      produto == "soja" ~ "Soja",
      produto == "milho" ~ "Milho",
      TRUE ~ "Carne bovina"
    ), levels = c("Soja", "Milho", "Carne bovina")),
    painel = factor(indicador,
      levels = c("exportacao_fob_usd_nominal_domicilio", "exportacao_kg_liquido_domicilio"),
      labels = c("Valor FOB\n(US$ bilhões correntes)", "Peso líquido\n(milhões de t)")),
    valor_plot = valor / 1e9
  )

g9 <- ggplot(exp_raw, aes(ano, valor_plot)) +
  geom_line(linewidth = 0.8, color = "#0072B2") +
  facet_grid(painel ~ produto, scales = "free_y") +
  scale_x_continuous(breaks = c(2001, 2012, 2024)) +
  scale_y_continuous(limits = c(0, NA), labels = rotulo_pt) +
  labs(x = "Ano", y = NULL) +
  theme(panel.spacing = unit(0.9, "lines"))
salvar_padrao(g9, "fig09_exportacoes", largura = 7.6, altura = 4.8, copiar_res = FALSE)

# 7. fig10_coef_regimes_embargos (NOVO: Visualização de Regimes e Embargos) --
res_mod <- read_csv(file.path(dir_modelos, "resultados_modelos.csv"), show_col_types = FALSE)
grad_emb <- read_csv(file.path(dir_modelos, "onda2_embargos_gradiente.csv"), show_col_types = FALSE)

reg_df <- res_mod |>
  filter(id %in% c("REG_prc_soja_Amz", "REG_prc_soja_Cer", "REG_lvl_soja_Amz", "REG_lvl_soja_Cer"),
         grepl("^xs_(p|r_p)[123]$", termo)) |>
  mutate(
    especificacao = if_else(grepl("^REG_prc", id), "Painel A (base)", "Painel B (irrestrito)"),
    bioma = if_else(grepl("_Amz$", id), "Amazônia", "Cerrado"),
    regime = case_when(
      grepl("1$", termo) ~ "2001–2005",
      grepl("2$", termo) ~ "2006–2011",
      TRUE ~ "2012–2024"
    ),
    regime = factor(regime, levels = c("2001–2005", "2006–2011", "2012–2024")),
    ic_inf = estimativa - 1.96 * erro_padrao,
    ic_sup = estimativa + 1.96 * erro_padrao
  )

g_reg <- ggplot(reg_df, aes(regime, estimativa, color = bioma, shape = especificacao)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.45) +
  geom_errorbar(aes(ymin = ic_inf, ymax = ic_sup),
                position = position_dodge(width = 0.45), width = 0.16, linewidth = 0.6) +
  geom_point(position = position_dodge(width = 0.45), size = 2.4) +
  scale_color_manual(values = c("Amazônia" = "#009E73", "Cerrado" = "#D55E00")) +
  scale_shape_manual(values = c("Painel A (base)" = 16, "Painel B (irrestrito)" = 1)) +
  scale_y_continuous(labels = rotulo_pt) +
  labs(x = "Regime institucional", y = expression("Gradiente preço–aptidão (soja, " * hat(beta) * ")")) +
  guides(color = guide_legend(order = 1), shape = guide_legend(order = 2))

grad_soja <- grad_emb |>
  filter(cultura == "soja", n_emb_l1 <= 20)

g_emb <- ggplot(grad_soja, aes(n_emb_l1, gradiente)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey45", linewidth = 0.45) +
  geom_ribbon(aes(ymin = ic95_inf, ymax = ic95_sup), fill = "#0072B2", alpha = 0.16) +
  geom_line(color = "#0072B2", linewidth = 0.85) +
  geom_point(color = "#0072B2", size = 2.1) +
  scale_x_continuous(breaks = c(0, 2, 5, 10, 15, 20)) +
  scale_y_continuous(labels = rotulo_pt) +
  labs(x = "Novos embargos do IBAMA em t - 1 (termos/ano)",
       y = "Gradiente marginal (IC 95%)")

# Salvar painel combinado com gridExtra/patchwork ou viewport básico de grid
suppressPackageStartupMessages(library(grid))
g10_file_pdf <- file.path(out_fig_main, "fig10_coef_regimes_embargos.pdf")
g10_file_png <- file.path(out_fig_main, "fig10_coef_regimes_embargos.png")

draw_combo <- function() {
  grid.newpage()
  pushViewport(viewport(layout = grid.layout(1, 2, widths = unit(c(1.1, 0.9), "null"))))
  print(g_reg + labs(subtitle = "A. Sensibilidade preço–aptidão por regime e bioma") +
          theme(plot.subtitle = element_text(face = "bold", size = 9.5),
                legend.box = "vertical", legend.spacing.y = unit(0.05, "cm")),
        vp = viewport(layout.pos.row = 1, layout.pos.col = 1))
  print(g_emb + labs(subtitle = "B. Modulação marginal por novos embargos (soja)") +
          theme(plot.subtitle = element_text(face = "bold", size = 9.5)),
        vp = viewport(layout.pos.row = 1, layout.pos.col = 2))
}

pdf(g10_file_pdf, width = 9.2, height = 4.2, useDingbats = FALSE, encoding = "ISOLatin1.enc")
draw_combo()
dev.off()
png(g10_file_png, width = 9.2, height = 4.2, units = "in", res = 320, bg = "white")
draw_combo()
dev.off()
cat("Salvo: fig10_coef_regimes_embargos (9.2 x 4.2 in)\n")
