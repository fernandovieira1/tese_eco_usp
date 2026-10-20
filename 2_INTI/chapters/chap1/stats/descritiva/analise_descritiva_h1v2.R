# Análise descritiva H1
#
# 01. Ambiente, caminhos e opções de visualização ----------------------------
exportar <- FALSE
abrir_tabelas <- FALSE  # TRUE abre cada tabela mostrada também no Data Viewer.
linhas_previa <- 12L    # Limita apenas a impressão, nunca os dados ou cálculos.

options(stringsAsFactors = FALSE, scipen = 6)
invisible(Sys.setlocale("LC_CTYPE", "Portuguese_Brazil.utf8"))
suppressPackageStartupMessages({
  library(arrow); library(dplyr); library(tidyr); library(ggplot2); library(readr)
})
# Aceita a raiz ou qualquer subpasta do repositório como diretório de trabalho.
# No RStudio, também tenta localizar a raiz pelo arquivo aberto no editor.
# Se não encontrar, use Session > Set Working Directory > To Source File Location
# e execute esta seção novamente.
localizar_raiz <- function(inicio = getwd()) {
  candidatos <- inicio
  if (interactive() && requireNamespace("rstudioapi", quietly = TRUE) &&
      rstudioapi::isAvailable()) {
    caminho_editor <- tryCatch(rstudioapi::getSourceEditorContext()$path,
                               error = function(e) "")
    if (nzchar(caminho_editor)) candidatos <- c(candidatos, dirname(caminho_editor))
  }
  argumento <- grep("^--file=", commandArgs(FALSE), value = TRUE)
  if (length(argumento)) {
    candidatos <- c(candidatos, dirname(sub("^--file=", "", argumento[1])))
  }
  for (candidato in candidatos) {
    atual <- normalizePath(candidato, winslash = "/", mustWork = TRUE)
    repeat {
      if (file.exists(file.path(atual, "2_INTI/RESEARCH_PROTOCOL.md"))) return(atual)
      acima <- dirname(atual)
      if (identical(acima, atual)) break
      atual <- acima
    }
  }
  stop("Raiz não localizada. Defina o diretório de trabalho na pasta do script ou na raiz do projeto.")
}
raiz_projeto <- localizar_raiz()
setwd(raiz_projeto)
message("Raiz do projeto: ", raiz_projeto)
message("Exportação: ", if (exportar) "ativada (pastas v2)" else "desativada; resultados no Environment/Console/Plots")
base <- "2_INTI/chapters/chap1/stats/descritiva"
out <- file.path(base, "resultados_h1v2")
audit <- "2_INTI/audit/descritiva_chap1_20261020/v2"
if (exportar) {
  for (p in c(out, file.path(out, c("figuras", "tabelas", "dados")), audit))
    dir.create(p, recursive = TRUE, showWarnings = FALSE)
}
# Apenas a apresentação muda: a prévia não filtra nem modifica o objeto.
mostrar_tabela <- function(x, name, diagnostic = FALSE) {
  cat("\n", name, ": ", nrow(x), " linhas x ", ncol(x), " colunas\n", sep = "")
  print(as_tibble(x), n = if (nrow(x) <= 24L) nrow(x) else linhas_previa, width = 110)
  if (abrir_tabelas && interactive()) View(as.data.frame(x), title = name)
  if (exportar) {
    write_csv(x, file.path(if (diagnostic) audit else file.path(out,"dados"),
                          paste0(name,".csv")), na = "")
  }
  invisible(x)
}
log <- character()
check <- function(ok, message) {
  if (!isTRUE(ok)) stop(message)
  log <<- c(log, paste("OK:", message))
  cat("OK:", message, "\n")
}

# 02. Ler os dados e a proveniência ----
source_path <- "2_INTI/chapters/chap1/stats/EDA/paineis/painel_tese_chap1_pt.csv"
canonical <- "2_INTI/xdata/chap1/processed/harmonizacao/painel_notebook/paineis/painel_tese_chap1_pt.csv"
input_paths <- c(file.path(base,c("df_h1","df_h1_proveniencia")), source_path, canonical,
  "2_INTI/xdata/chap1/processed/harmonizacao/painel_notebook/dicionario_painel.csv",
  "2_INTI/xdata/chap1/processed/territorio_141/municipios_referencia.json")
hash_before <- tools::md5sum(input_paths)
d <- as.data.frame(read_parquet(input_paths[1]))
prov <- as.data.frame(read_parquet(input_paths[2]))
src <- read_csv(source_path, show_col_types=FALSE, progress=FALSE,
                col_types=cols(codigo_ibge=col_character())) |> arrange(codigo_ibge,ano)
can <- read_csv(canonical, show_col_types=FALSE, progress=FALSE,
                col_types=cols(codigo_ibge=col_character())) |> arrange(codigo_ibge,ano)
dim(d)
head(names(d), 20)
print(head(prov, 5))
# Para consultar a base completa no Data Viewer: View(d)

# 03. Conferir a origem e recuperar município/ano ----
check(isTRUE(all.equal(src,can,check.attributes=FALSE,tolerance=1e-12)),
      "Cópia EDA e painel canônico coincidem após ordenar pelas chaves")
check(nrow(d)==nrow(src) && all(names(d)%in%names(src)), "Estrutura compatível para recuperar chaves")
# O notebook ordenou o MultiIndex e exportou index=False. NÃO basta presumir a ordem:
# todas as células e máscaras NA das 176 colunas precisam coincidir com o painel identificado.
reconcile <- bind_rows(lapply(names(d), function(n) {
  a <- d[[n]]; b <- src[[n]]
  if (is.logical(a)) b <- as.logical(b)
  mask <- identical(is.na(a),is.na(b))
  delta <- if (is.numeric(a) && any(!is.na(a))) max(abs(a-b),na.rm=TRUE) else NA_real_
  tibble(coluna=n, ausencias_iguais=mask,
         valores_iguais=isTRUE(all.equal(a,b,check.attributes=FALSE,tolerance=1e-12)),
         max_diferenca=delta)
}))
mostrar_tabela(reconcile,"reconciliacao_176_colunas",TRUE)
check(all(reconcile$ausencias_iguais & reconcile$valores_iguais), "176 colunas reconciliadas; chaves recuperadas sem junção por posição não validada")
check(!anyDuplicated(src[c("codigo_ibge","ano")]), "Chave município-ano única")
check(!anyNA(src[c("codigo_ibge","ano")]), "Chaves sem ausências")
check(n_distinct(src$codigo_ibge)==141 && identical(sort(unique(src$ano)),as.double(2001:2024)),
      "141 territórios e anos 2001-2024")
check(all(table(src$codigo_ibge)==24), "Grade estrutural balanceada")
# Nomes municipais, usados somente como identificadores.

# 04. Identificadores e classificação territorial ----
cad <- jsonlite::fromJSON(input_paths[6])
cad$codigo_ibge <- as.character(cad$codigo_ibge)
check(!anyDuplicated(cad$codigo_ibge), "Cadastro municipal único")
keys <- src |> select(codigo_ibge,ano) |> left_join(cad,by="codigo_ibge")
check(!anyNA(keys$municipio), "Nomes municipais recuperados")
full <- bind_cols(keys, as_tibble(d))
shares <- c("biome_amazonia_share_i","biome_cerrado_share_i","biome_pantanal_share_i")
biomes <- c("Amazônia","Cerrado","Pantanal")
fr <- as.matrix(full[shares])
check(all(fr>=-1e-8 & fr<=1+1e-8), "Frações de bioma entre zero e um, tolerância geométrica 1e-8; sem recorte dos valores")
check(all(rowSums(fr)<=1+1e-8 & rowSums(fr)>.99), "Frações territoriais sem sobreposição ou lacuna grande")
check(all(rowSums(fr==apply(fr,1,max))==1), "Sem empate na predominância")
full$bioma_predominante <- factor(biomes[max.col(fr,ties.method="first")],levels=biomes)
full$multibioma <- rowSums(fr>1e-6)>1
full$y_completo <- as.logical(src$y_cobertura_completa)
full$fracao_y <- src$y_fracao_area_valida_par
full$area_y <- src$y_area_total_ha

# 05. Selecionar as mesmas 15 variáveis ----
yc <- c("conversao_ha__agricultura","conversao_ha__pastagem")
yt <- c("taxa_conversao__agricultura","taxa_conversao__pastagem")
pr <- paste0("preco_real_usd2024_media_anual_lag1__",c("soja","milho","carne_bovina"))
cap <- c("capacidade_valor__soja__gaez_yxHr0_soy","capacidade_valor__milho__gaez_yxHr0_mze")
inst <- "n_autos_flora__ibama_espacial"
partial <- "flag_contagem_flora_parcial__ibama_espacial"
# Quinze campos analíticos, incluindo três frações e uma flag de qualidade.
selected <- c(yc,yt,"y_nativa_inicial_ha",pr,cap,shares,inst,partial)
check(length(selected)==15 && all(selected%in%names(d)), "Quinze variáveis selecionadas, nomes preservados")
sel <- full |> select(codigo_ibge,municipio,ano,bioma_predominante,all_of(selected))
if (exportar) {
  saveRDS(sel,file.path(out,"dados","df_h1_selecionado.rds"),version=3)
  write_parquet(sel,file.path(out,"dados","df_h1_selecionado.parquet"),compression="zstd")
}
glimpse(sel)
# Para consultar todas as linhas: View(sel)
mostrar_tabela(sel,"df_h1_selecionado")

# 06. Conferir taxas, denominadores, ausências e tipos ----
check(all(complete.cases(full[yc])==full$y_completo), "Ausência de conversão corresponde à cobertura incompleta")
for (j in 1:2) {
  good <- !is.na(full[[yt[j]]])
  check(all(full[[yc[j]]][good]>=0 & full[[yt[j]]][good]>=0 & full[[yt[j]]][good]<=1),
        paste("Domínio de conversão e taxa:",j))
  check(max(abs(full[[yt[j]]][good]-full[[yc[j]]][good]/full$y_nativa_inicial_ha[good]))<1e-12,
        paste("Taxa = área / estoque nativo na mesma máscara:",j))
}
check(all(rowSums(full[yc],na.rm=FALSE)<=full$y_nativa_inicial_ha+1e-4,na.rm=TRUE),
      "Soma dos destinos não excede estoque nativo")
check(all(full$y_nativa_inicial_ha>0), "Nenhum denominador nativo nulo")
for (n in c(shares,cap)) check(all(tapply(full[[n]],full$codigo_ibge,n_distinct)==1),
  paste("Constante por município:",n))
for (n in pr) check(all(tapply(full[[n]],full$ano,n_distinct)==1),
  paste("Preço comum a todos os municípios no ano:",n))
profile <- bind_rows(lapply(names(d),function(n) {
  x<-d[[n]]; z<-x[!is.na(x)]
  tibble(coluna=n,tipo=class(x)[1],n=length(x),validos=length(z),ausentes=sum(is.na(x)),
    proporcao_ausente=mean(is.na(x)),zeros=sum(z==0),min=if(length(z)) min(z) else NA_real_,
    mediana=if(length(z)) median(as.numeric(z)) else NA_real_,
    p99=if(length(z)) unname(quantile(as.numeric(z),.99)) else NA_real_,
    max=if(length(z)) max(z) else NA_real_,
    constante_municipal=all(tapply(x,full$codigo_ibge,function(v)n_distinct(v,na.rm=TRUE))<=1),
    comum_anual=all(tapply(x,full$ano,function(v)n_distinct(v,na.rm=TRUE))<=1))
}))
mostrar_tabela(profile,"perfil_base_completa",TRUE)
check(!any(vapply(d,function(x)is.numeric(x)&&any(is.infinite(x)),logical(1))),"Sem valores infinitos")

# 07. Cobertura da amostra e municípios fixos ----
balanced <- full |> group_by(codigo_ibge) |> summarise(fixo=all(y_completo),.groups="drop")
full <- left_join(full,balanced,by="codigo_ibge")
municipal <- full |> filter(ano==2001)
mostrar_tabela(full |> select(codigo_ibge,municipio,ano,bioma_predominante,y_completo,fracao_y,area_y,fixo,multibioma),
    "suporte_observacoes",TRUE)
mask_summary <- full |> group_by(y_completo) |> summarise(
  pares=n(),min_fracao_valida=min(fracao_y),p25_fracao_valida=quantile(fracao_y,.25),
  mediana_fracao_valida=median(fracao_y),p75_fracao_valida=quantile(fracao_y,.75),
  max_fracao_valida=max(fracao_y),.groups="drop")
mostrar_tabela(mask_summary,"cobertura_espacial_pares",TRUE)
coverage <- full |> group_by(ano,bioma_predominante) |> summarise(
  n_grade=n(),n_y=sum(y_completo),n_fixo=sum(fixo),n_ibama_observado=sum(!is.na(.data[[inst]])),
  n_ibama_classificado=sum(!is.na(.data[[inst]]) & .data[[partial]]%in%FALSE),
  .groups="drop")
mostrar_tabela(coverage,"cobertura_ano_bioma",TRUE)
ct <- full |> group_by(bioma_predominante) |> summarise(
  municipios=n_distinct(codigo_ibge),municipios_multibioma=n_distinct(codigo_ibge[multibioma]),
  n_grade=n(),n_y=sum(y_completo),pct_y=100*mean(y_completo),
  municipios_fixos=n_distinct(codigo_ibge[fixo]),.groups="drop")
mostrar_tabela(ct,"tabela_cobertura")

# 08. Conversão anual: razão entre somas e média das taxas ----
annual <- bind_rows(lapply(c(FALSE,TRUE),function(fixed) {
  x<- full |> filter(y_completo, !fixed | fixo)
  bind_rows(lapply(1:2,function(j) x |> group_by(ano) |> summarise(
    n=n(),area_ha=sum(.data[[yc[j]]]),nativa_inicial_ha=sum(y_nativa_inicial_ha),
    taxa_agregada_pct=100*area_ha/nativa_inicial_ha,
    media_taxas_pct=100*mean(.data[[yt[j]]]),mediana_taxas_pct=100*median(.data[[yt[j]]]),
    .groups="drop") |> mutate(destino=c("Agricultura","Pastagem")[j],
      amostra=if(fixed) "Municípios fixos" else "Disponível no ano")))
}))
mostrar_tabela(annual,"conversao_anual")

# 09. Distribuição municipal e extremos ----
# Comparação territorial principal: média temporal de cada município da amostra fixa.
# Cada ponto tem 24 anos; não confundir municípios de predominância com polígonos de biomas.
mun_rates <- full |> filter(fixo) |> group_by(codigo_ibge,municipio,bioma_predominante) |>
  summarise(n_anos=n(),Agricultura=100*mean(taxa_conversao__agricultura),
            Pastagem=100*mean(taxa_conversao__pastagem),.groups="drop") |>
  pivot_longer(c(Agricultura,Pastagem),names_to="destino",values_to="media_temporal_pct")
mostrar_tabela(mun_rates,"distribuicao_municipal")
# Diagnóstico alternativo: todos os pares válidos, amostra variável, sem substituir a principal.
by_biome <- full |> filter(y_completo) |> group_by(ano,bioma_predominante) |>
  summarise(n=n(),agricultura_ha=sum(conversao_ha__agricultura),pastagem_ha=sum(conversao_ha__pastagem),
    nativa_ha=sum(y_nativa_inicial_ha),agricultura_pct=100*agricultura_ha/nativa_ha,
    pastagem_pct=100*pastagem_ha/nativa_ha,.groups="drop")
mostrar_tabela(by_biome,"conversao_ano_grupo",TRUE)
extremes <- bind_rows(lapply(1:2,function(j) full |> filter(y_completo) |>
  arrange(desc(.data[[yt[j]]])) |> slice_head(n=10) |>
  transmute(codigo_ibge,municipio,ano,bioma_predominante,destino=c("Agricultura","Pastagem")[j],
    conversao_ha=.data[[yc[j]]],denominador_ha=y_nativa_inicial_ha,taxa=.data[[yt[j]]])))
mostrar_tabela(extremes,"extremos_taxas_sem_exclusao",TRUE)

# 10. Preços: uma observação por ano e produto ----
prices <- full |> select(ano,all_of(pr)) |> distinct() |>
  pivot_longer(all_of(pr),names_to="variavel",values_to="preco") |>
  mutate(produto=c("Soja","Milho","Carne bovina")[match(variavel,pr)],ano_preco=ano-1,
    unidade=ifelse(produto=="Carne bovina","USD de 2024/kg","USD de 2024/t")) |>
  group_by(produto) |> arrange(ano_preco,.by_group=TRUE) |>
  mutate(indice=100*preco/preco[ano_preco==2000]) |> ungroup()
check(nrow(prices)==72,"Preços: 24 anos distintos por produto, sem pseudorreplicação municipal")
mostrar_tabela(prices,"precos_anuais")

# 11. Capacidade produtiva: uma observação por município ----
cap_long <- municipal |> select(codigo_ibge,municipio,bioma_predominante,all_of(cap)) |>
  pivot_longer(all_of(cap),names_to="variavel",values_to="kg_ms_ha") |>
  mutate(produto=c("Soja","Milho")[match(variavel,cap)])
cap_summary <- cap_long |> group_by(produto,bioma_predominante) |> summarise(
  n=n(),media=mean(kg_ms_ha),mediana=median(kg_ms_ha),p25=quantile(kg_ms_ha,.25),
  p75=quantile(kg_ms_ha,.75),min=min(kg_ms_ha),max=max(kg_ms_ha),.groups="drop")
mostrar_tabela(cap_long,"capacidade_municipal"); mostrar_tabela(cap_summary,"tabela_capacidade")
# Cenário baixo insumo é diagnóstico de sensibilidade; não selecionado pelo ajuste.
mostrar_tabela(municipal |> select(codigo_ibge,bioma_predominante,all_of(cap),
  capacidade_valor__soja__gaez_yxLr0_soy,capacidade_valor__milho__gaez_yxLr0_mze),
  "capacidade_cenarios",TRUE)

# 12. Autuações: cobertura e estatísticas condicionais ----
institution <- full |> group_by(ano) |> summarise(n_grade=n(),
  n_observado=sum(!is.na(.data[[inst]])),
  n_parcial=sum(!is.na(.data[[inst]]) & .data[[partial]]%in%TRUE),
  n_classificado=sum(!is.na(.data[[inst]]) & .data[[partial]]%in%FALSE),
  n_zero_classificado=sum(.data[[inst]]==0 & .data[[partial]]%in%FALSE,na.rm=TRUE),
  media=mean(.data[[inst]][.data[[partial]]%in%FALSE],na.rm=TRUE),
  mediana=median(.data[[inst]][.data[[partial]]%in%FALSE],na.rm=TRUE),
  .groups="drop")
mostrar_tabela(institution,"ibama_anual")
mostrar_tabela(full |> select(codigo_ibge,municipio,ano,all_of(inst),all_of(partial),
  flag_sem_registro_identificado__ibama_espacial,n_autos_observados__ibama_espacial,
  n_autos_flora__ibama_informada,flag_contagem_flora_parcial__ibama_informada),
  "ibama_qualidade_e_associacao",TRUE)


# 13. Dicionário e candidatas excluídas ----
# Dicionário: definição herdada, fontes verificadas nos scripts locais, e decisão descritiva.
meta <- read_csv(input_paths[5], show_col_types=FALSE)
labels <- c("Conversão para agricultura","Conversão para pastagem","Taxa de conversão para agricultura",
  "Taxa de conversão para pastagem","Vegetação nativa inicial compatível",
  "Preço real anterior da soja","Preço real anterior do milho","Preço real anterior da carne bovina",
  "Rendimento potencial da soja (alto insumo)","Rendimento potencial do milho (alto insumo)",
  "Fração municipal na Amazônia","Fração municipal no Cerrado","Fração municipal no Pantanal",
  "Autos de Flora espacialmente localizados","Classificação temática parcial de autos")
sources <- c(rep("MapBiomas Brasil, Coleção 10.1, coverage_v1; IBGE malha MT 2023",5),
  rep("Banco Mundial, Pink Sheet; CPI-U BLS/FRED CPIAUCNS",3),
  rep("FAO/IIASA, GAEZ v4, clima 1961-1990, terras 2010",2),
  rep("IBGE biomas 2019 e malha municipal MT 2023",3),rep("IBAMA, autos de infração",2))
evidence <- paste0("2_INTI/chapters/chap1/stats/AED/pt/",
  c(rep("harmonizacao_terra.py; obter_transicoes_mapbiomas.py",5),
    rep("harmonizacao_economia.py; painel_anual_fontes.py",3),
    rep("harmonizacao_economia.py; reconstruir_141_estaticas.py",5),
    rep("harmonizacao_instituicoes.py; reconstruir_141_ibama.py",2)))
roles <- c(rep("Resultado central H1, por destino",4),"Denominador da taxa",
  rep("Incentivo de mercado; não retorno líquido",3),rep("Heterogeneidade da capacidade produtiva",2),
  rep("Classificação territorial e identificação de municípios mistos",3),
  "Dimensão observada da atuação administrativa","Qualidade indispensável à interpretação de autuações")
limits <- c(rep("NA se qualquer área do par não é observada; mudança entre mapas não identifica causa nem legalidade.",4),
  "Preenchido inclusive nos pares incompletos: nesses casos é estoque apenas na máscara observada, não denominador válido para recuperar Y ausente.",
  rep("Ano civil t-1; poder de compra em USD, não preço local em BRL, lucro ou expectativa observada.",3),
  rep("Cenário alto insumo e sequeiro; matéria seca; terras 2010 impedem presumir predeterminação completa.",2),
  rep("Município pode cruzar biomas; não ratear conversões pela fração; pequenas lacunas geométricas preservadas.",3),
  "Contagem depende de infrações, fiscalização e localização; ausência não é zero; Flora inclui transporte florestal.",
  "False certifica classificação nos registros usados, não completude da fiscalização ou da fonte.")
formulas <- c(
  "Soma da área dos pixels com classe nativa em t-1 e agrícola em t; NA se par incompleto.",
  "Soma da área dos pixels com classe nativa em t-1 e pastagem em t; NA se par incompleto.",
  "conversao_ha__agricultura / y_nativa_inicial_ha; exige denominador positivo e par completo.",
  "conversao_ha__pastagem / y_nativa_inicial_ha; exige denominador positivo e par completo.",
  "Soma das áreas das transições com origem nativa em t-1 na máscara válida do par, incluindo permanências.",
  rep("Média dos 12 preços mensais de t-1 × média(CPI-U em 2024) / CPI-U do respectivo mês; deflação antes da média.",3),
  rep("Média dos pixels GAEZ yxHr0 válidos dentro do município, ponderada por cos(latitude); sem padronização z.",2),
  paste0("Área da interseção do município com ",biomes," / área municipal inteira em EPSG:5880; sem renormalização."),
  "Número de IDs de autos classificados em TIPO_INFRACAO=Flora, por ano de lavratura e município espacial; NA se nenhum registro identificado ou tema indeterminado sem positivo.",
  "True se existe registro sem ID ou tema Flora indeterminado no grupo; False se classificação completa nos registros; NA se grupo sem registro identificado.")
dictionary <- tibble(nome_original=selected,nome_final=selected,rotulo=labels,papel=roles,
  fonte_primaria=sources,evidencia=evidence,limitacao_adicional=limits,
  formula=formulas,
  justificativa=c(rep("Separar magnitude, intensidade e destinos conforme objetivo i da introdução.",5),
    rep("Representar preços das lavouras e da pecuária sem repetir logs e interações.",3),
    rep("Descrever cenário físico em unidade legível; alto insumo é ilustração, não escolha econométrica.",2),
    rep("Preservar heterogeneidade territorial sem atribuir todo município a um bioma puro.",3),
    "Flora tem vínculo ambiental e classificação explícita; associação espacial usa a malha comum.",
    "Preservar distinção entre contagem integralmente classificada e parcial.")) |>
  left_join(meta |> select(nome_original=coluna_painel,unidade,regra_bloco_origem=regra,
                           tabelas_origem,coluna_origem),by="nome_original") |>
  left_join(prov |> select(nome_original=coluna,definicao=definicao_dicio),by="nome_original") |>
  left_join(profile |> select(nome_original=coluna,validos,ausentes,proporcao_ausente),by="nome_original")
dictionary$cobertura <- c(rep("2001-2024: município-ano",5),
  rep("2000-2023: 24 preços anuais, repetidos na grade 2001-2024",3),
  rep("141 municípios; constante nos 24 anos",5),rep("2001-2024: município-ano, cobertura desigual",2))
check(nrow(dictionary)==15 && !anyNA(dictionary$definicao),"Dicionário completo e único")
mostrar_tabela(dictionary |> select(rotulo, unidade, validos, ausentes, proporcao_ausente),
               "dicionario_cobertura", diagnostic = TRUE)
# Para ler definições, fontes e fórmulas completas: View(dictionary)
if (exportar) write_csv(dictionary,file.path(out,"dicionario_variaveis.csv"),na="")
excluded <- tibble(candidatas=c("Logs, variações de preços e interações","PAM contemporânea e defasada",
  "PAM 1991-2000 (mínimo sete anos)","GAEZ baixo insumo e índices sx",
  "Multas e autos por código informado","Autos Desmatamento/Desmatamento e Queimada",
  "Rebanho e lotação","Estoques legados e participações de uso","Chuva e relevo"),
  motivo=c("Redundância para descritiva; pertencem à especificação futura.",
  "Rendimento realizado é endógeno ao manejo e à seleção das áreas; não é aptidão predeterminada.",
  "Cobertura seletiva e harmonização histórica pendente; não excluir municípios por essa medida.",
  "Cenários alternativos; baixo insumo exportado no diagnóstico; sx não é rendimento.",
  "Multas não medem pagamentos; associação informada pode divergir da malha comum; contraste em diagnóstico.",
  "Tema mais estreito com maior ausência; não somar com Flora, pois os temas se sobrepõem.",
  "Não são produtividade de carne; datas e território da PPM ainda demandam compatibilização.",
  "Não substituem denominador na máscara de Y; diferença de estoque não é conversão bruta.",
  "Controles potenciais, secundários para as perguntas descritivas desta seção."))
print(excluded, n = Inf, width = 110)
if (abrir_tabelas && interactive()) View(excluded)
if (exportar) write_csv(excluded,file.path(out,"candidatas_excluidas.csv"))


# 14. Preparar o estilo dos gráficos ----
# Figuras: vetores PDF e PNG 320 dpi; linhas/tipos também distinguem séries em cinza.
pal <- c("Amazônia"="#0072B2","Cerrado"="#D55E00","Pantanal"="#009E73")
theme_set(theme_bw(base_size=11,base_family="sans")+
  theme(panel.grid.minor=element_blank(),legend.position="bottom",
        legend.title=element_blank(),strip.background=element_rect(fill="grey95"),
        plot.margin=margin(8,12,8,8)))
# print(p1), etc., desenha na sessão. Esta função só exporta se exportar=TRUE.
save_plot <- function(p,name,width=7,height=4.4) {
  if (!exportar) return(invisible(p))
  ggsave(file.path(out,"figuras",paste0(name,".pdf")),p,width=width,height=height,
    device=grDevices::pdf,useDingbats=FALSE,encoding="ISOLatin1.enc")
  ggsave(file.path(out,"figuras",paste0(name,".png")),p,width=width,height=height,dpi=320,bg="white")
}

# 15. Visualizar a evolução da conversão ----
p1 <- ggplot(annual,aes(ano,taxa_agregada_pct,color=amostra,linetype=amostra))+
  geom_line(linewidth=.65)+facet_wrap(~destino,ncol=1,scales="fixed")+
  scale_color_manual(values=c("Disponível no ano"="#777777","Municípios fixos"="#0072B2"))+
  scale_linetype_manual(values=c("Disponível no ano"="dashed","Municípios fixos"="solid"))+
  scale_x_continuous(breaks=c(2001,2005,2010,2015,2020,2024))+
  scale_y_continuous(limits=c(0,NA),labels=function(x)format(x,decimal.mark=",",trim=TRUE))+
  labs(x="Ano final da transição",y="Conversão / vegetação inicial (%)")
print(p1)  # Execute esta linha para mostrar/reabrir o gráfico em Plots.
save_plot(p1,"fig01_conversao",height=4.8)

# 16. Visualizar a distribuição municipal ----
nr <- table(municipal$bioma_predominante[municipal$fixo])
axis_biome <- setNames(paste0(biomes,"\n(n = ",as.integer(nr),")"),biomes)
# Posição horizontal determinística por município: mostra todos os pontos sem sorteio.
mun_rates <- mun_rates |> group_by(destino,bioma_predominante) |> arrange(media_temporal_pct,.by_group=TRUE) |>
  mutate(x=as.integer(bioma_predominante)+if(n()>1) seq(-.15,.15,length.out=n()) else 0) |> ungroup()
p2 <- ggplot(mun_rates,aes(x,media_temporal_pct,color=bioma_predominante,shape=bioma_predominante))+
  geom_point(size=1.7,alpha=.8)+facet_wrap(~destino,ncol=2)+
  scale_color_manual(values=pal)+scale_shape_manual(values=c(16,17,15))+
  scale_x_continuous(breaks=1:3,labels=axis_biome,limits=c(.6,3.4))+
  scale_y_continuous(limits=c(0,NA),labels=function(x)format(x,decimal.mark=",",trim=TRUE))+
  labs(x="Predominância territorial do município",y="Média municipal da taxa anual (%)")+
  theme(legend.position="none")
print(p2)  # Execute esta linha para mostrar/reabrir o gráfico em Plots.
save_plot(p2,"fig02_distribuicao",height=3.7)

# 17. Visualizar os preços reais ----
p3 <- ggplot(prices,aes(ano_preco,indice,color=produto,linetype=produto))+
  geom_line(linewidth=.7)+scale_color_manual(values=c("Soja"="#0072B2","Milho"="#D55E00","Carne bovina"="#333333"))+
  scale_linetype_manual(values=c("Soja"="solid","Milho"="dashed","Carne bovina"="dotdash"))+
  scale_x_continuous(breaks=c(2000,2005,2010,2015,2020,2023))+
  scale_y_continuous(limits=c(0,NA))+
  labs(x="Ano do preço (t - 1 na base)",y="Índice do preço real (2000 = 100)")
print(p3)  # Execute esta linha para mostrar/reabrir o gráfico em Plots.
save_plot(p3,"fig03_precos",height=3.6)

# 18. Visualizar cobertura e autuações do IBAMA ----
ip <- bind_rows(institution |> transmute(ano,painel="A. Cobertura das contagens de Flora",
    serie="Contagem observada",valor=n_observado),
  institution |> transmute(ano,painel="A. Cobertura das contagens de Flora",
    serie="Classificação completa nos registros",valor=n_classificado),
  institution |> transmute(ano,painel="B. Autos por município com classificação completa",
    serie="Média",valor=media),
  institution |> transmute(ano,painel="B. Autos por município com classificação completa",
    serie="Mediana",valor=mediana))
p4 <- ggplot(ip,aes(ano,valor,color=serie,linetype=serie))+
  geom_line(linewidth=.7)+facet_wrap(~painel,ncol=1,scales="free_y")+
  scale_x_continuous(breaks=c(2001,2005,2010,2015,2020,2024))+
  scale_y_continuous(limits=c(0,NA))+
  scale_color_manual(values=c("#777777","#0072B2","#D55E00","#333333"))+
  scale_linetype_manual(values=c("solid","dashed","solid","dotdash"))+
  labs(x="Ano de lavratura",y="Municípios (A) / autos por município (B)")+
  guides(color=guide_legend(nrow=2),linetype=guide_legend(nrow=2))
print(p4)  # Execute esta linha para mostrar/reabrir o gráfico em Plots.
save_plot(p4,"fig04_ibama",height=5.2)


# 19. Tabelas do artigo e fragmentos LaTeX ----
# Tabelas em LaTeX, sem pacote adicional; números e macros vêm dos mesmos resultados.
fmt <- function(x,k=0) formatC(x,format="f",digits=k,big.mark=".",decimal.mark=",")
# As duas tabelas numéricas podem ser examinadas sem interpretar código LaTeX.
print(ct, n = Inf, width = 110)
print(cap_summary, n = Inf, width = 110)
tabelas_latex <- list()
table_tex <- function(name,caption,label,head,rows,note,align) {
  conteudo <- c("\\begin{table}[htbp]","\\centering","\\small",
    paste0("\\caption{",caption,"}\\label{",label,"}"),
    paste0("\\begin{tabular}{",align,"}"),"\\hline",paste0(head," \\\\"),
    "\\hline",paste0(rows," \\\\"),"\\hline","\\end{tabular}",
    "\\par\\smallskip\\begin{minipage}{\\textwidth}\\footnotesize",
    note,"\\end{minipage}","\\end{table}")
  tabelas_latex[[name]] <<- conteudo
  if (exportar) writeLines(conteudo,file.path(out,"tabelas",paste0(name,".tex")),useBytes=TRUE)
  invisible(conteudo)
}
rows <- apply(as.data.frame(ct),1,function(r)paste(c(r[1],fmt(as.numeric(r[2])),
  fmt(as.numeric(r[3])),fmt(as.numeric(r[5])),fmt(as.numeric(r[6]),1),
  fmt(as.numeric(r[7]))),collapse=" & "))
table_tex("tab01_cobertura","Cobertura da conversão por predominância territorial, 2001--2024",
  "tab:h1-cobertura","Grupo & Municípios & Mistos & Pares válidos & \\% da grade & Fixos",
  rows,paste0("Fonte: elaboração própria com MapBiomas 10.1 e IBGE. ",
  "Pares válidos são observações município-ano com cobertura integral do par de mapas. ",
  "Fixos: municípios com conversão observada nos 24 anos. Mistos: mais de um bioma com fração superior a $10^{-6}$. ",
  "Predominância significa a maior fração da área municipal; não equivale a observar apenas a porção desse bioma."),
  "lrrrrr")
rows <- apply(as.data.frame(cap_summary),1,function(r)paste(c(r[1],r[2],fmt(as.numeric(r[3])),
  fmt(as.numeric(r[5])),paste0(fmt(as.numeric(r[6])),"--",fmt(as.numeric(r[7])))),collapse=" & "))
table_tex("tab02_capacidade","Rendimento potencial municipal no cenário de alto insumo e sequeiro",
  "tab:h1-capacidade","Cultura & Predominância & Municípios & Mediana & P25--P75",
  rows,"Fonte: elaboração própria com FAO/IIASA, GAEZ v4, clima 1961--1990 e terras de 2010; agregação municipal na malha IBGE 2023. Unidade: kg de matéria seca por hectare. Cada município entra uma vez, com peso igual. P25--P75 delimita a metade central da distribuição. O cenário não representa o rendimento realizado nem garante capacidade predeterminada em relação a todo o painel.",
  "llrrr")

# 20. Números do texto e resumo dos resultados ----
first <- annual |> filter(ano==2001,amostra=="Municípios fixos")
last <- annual |> filter(ano==2024,amostra=="Municípios fixos")
tot <- full |> filter(y_completo) |> summarise(a=sum(conversao_ha__agricultura),p=sum(conversao_ha__pastagem))
macros <- c(
  Hobs=fmt(nrow(full)),Hvalid=fmt(sum(full$y_completo)),Hmissing=fmt(sum(!full$y_completo)),
  HmissingPct=fmt(100*mean(!full$y_completo),1),Hfixed=fmt(sum(municipal$fixo)),
  HminFracExcl=fmt(100*min(full$fracao_y[!full$y_completo]),4),
  HfixedObs=fmt(sum(full$fixo)),Hmixed=fmt(sum(municipal$multibioma)),
  HnMin=fmt(min(table(full$ano[full$y_completo]))),HnMax=fmt(max(table(full$ano[full$y_completo]))),
  HpastShare=fmt(100*tot$p/(tot$a+tot$p),1),
  HagFirst=fmt(first$taxa_agregada_pct[first$destino=="Agricultura"],2),
  HagLast=fmt(last$taxa_agregada_pct[last$destino=="Agricultura"],2),
  HpaFirst=fmt(first$taxa_agregada_pct[first$destino=="Pastagem"],2),
  HpaLast=fmt(last$taxa_agregada_pct[last$destino=="Pastagem"],2),
  HibValid=fmt(sum(!is.na(full[[inst]]))),
  HibComplete=fmt(sum(!is.na(full[[inst]]) & full[[partial]]%in%FALSE)),
  HibMin=fmt(min(institution$n_classificado)),HibMax=fmt(max(institution$n_classificado)),
  HmaxAg=fmt(100*max(full$taxa_conversao__agricultura,na.rm=TRUE),2),
  HmaxPa=fmt(100*max(full$taxa_conversao__pastagem,na.rm=TRUE),2))
macros_latex <- paste0("\\newcommand{\\",names(macros),"}{",macros,"}")
if (exportar) writeLines(macros_latex,file.path(out,"tabelas","numeros.tex"),useBytes=TRUE)
mostrar_tabela(tibble(macro=names(macros),valor=unname(macros)),"numeros_texto")

# 21. Ambiente e conferências finais ----
ambiente <- sessionInfo()
print(ambiente)
if (exportar) capture.output(ambiente,file=file.path(audit,"sessionInfo.txt"))
if (exportar) writeLines(c("Dependências diretas:",paste(c("arrow","dplyr","tidyr","ggplot2","readr","jsonlite"),
  vapply(c("arrow","dplyr","tidyr","ggplot2","readr","jsonlite"),function(p)as.character(packageVersion(p)),character(1)))),
  file.path(out,"dependencias.txt"))
check(identical(hash_before,tools::md5sum(input_paths)),"Entradas preservadas byte a byte (MD5)")
mostrar_tabela(tibble(arquivo=names(hash_before),md5=unname(hash_before)),"manifesto_entradas",TRUE)
if (exportar) writeLines(log,file.path(audit,"verificacoes_R.txt"),useBytes=TRUE)
cat(paste(macros,names(macros),sep=" = "),sep="\n")
cat("\nAnálise concluída. Objetos disponíveis no Environment.\n")
cat("Para rever: print(p1); print(p2); print(p3); print(p4).\n")
cat("Tabelas: ct, annual, cap_summary, institution; dataframe: sel.\n")
cat("Exportação:", if (exportar) out else "desativada; nenhum produto da análise foi gravado.", "\n")
# Ao modificar filtros apenas para explorar, não confunda o resultado com a
# especificação validada. Reexecute desde o início para voltar à análise original.

