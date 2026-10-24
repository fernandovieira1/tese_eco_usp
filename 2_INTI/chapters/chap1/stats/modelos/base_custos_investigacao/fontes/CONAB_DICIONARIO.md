# Dicionário do complemento

Fonte comum: extratos de células CONAB identificados em FONTES_DRIVE.json. Cobertura efetiva em cobertura_praca_ano.csv. Todos os custos são modais, sujeitos a seleção territorial, tecnologia e revisão; não são renda líquida ou eficácia institucional. Chave relacional: id_serie identifica um par arquivo/aba por hash estável; não é código municipal.

| Campos | Definição, unidade e uso |
|---|---|
| id_serie, arquivo, aba | Identificador de planilha, nome exato do extrato e da aba; relação muitos valores para uma planilha |
| cultura | soja, milho_1a, milho_2a conforme fonte; não é cultura de destino da conversão |
| praca_aba, praca_cabecalho | Localidade reconhecida separadamente no nome e cabeçalho; vazio significa não declarada no cabeçalho |
| conflito_praca, praca_ambigua | Divergência ou praça conjunta; bloqueiam candidato descritivo |
| tecnologia | OGM explícito no cabeçalho/nome; convencional explícita; não declarada. Não há imputação por ausência de OGM |
| cabecalho | Texto completo das primeiras 14 linhas com sistema/intensidade, tipo de relatório e contexto; coordenadas em proveniencia_cabecalhos.csv |
| safra_texto, safra_inicio, safra_fim | Identificação original e anos normalizados; ano único mantém início=fim, sem presumir mês de colheita |
| data_base_texto, data_base, precisao_data_base | Texto original e ISO YYYY-MM-DD ou YYYY-MM; precisão dia ou mês; não é data de publicação |
| ano_data_base, ano_aba, data_fora_ano_aba | Ano extraído da data, ano do nome e indicador de divergência; nenhuma correção da fonte |
| produtividade_texto, produtividade_kg_ha | Produtividade modal declarada; média explícita tem precedência sobre faixa; não é PAM ou GAEZ |
| ex_ant | Presença literal Ex-Ant no cabeçalho; não atesta vintage conhecido |
| elegivel_periodo_2001_2024 | Data-base e início/fim da safra dentro do intervalo; critério conservador de cobertura, não exposição econométrica |
| identidades_ha_ok | Quatro identidades em ha aprovadas em R$0,05 |
| candidato_descritivo_periodo | Cobertura temporal, praça não conflitante/ambígua, identidades em ha e data não divergente do ano da aba; ainda não autorizado como custo municipal |
| conceito | A custeio; B outras despesas/pós-colheita; C financeiras; D variável; E depreciações; F outros fixos; G fixo; H operacional; I renda de fatores; J total |
| rotulo_original, formula_letra_inconsistente | Rótulo preservado; flag para renda de fatores identificada semanticamente como I, mas impressa como (F) |
| unidade, valor, valor_original | BRL_nominal/ha, BRL_nominal/60kg ou participação CV/CT/genérica; número parseado e string intacta; nenhuma deflação ou substituição |
| linha_excel, coluna_excel, rotulo_coluna | Coordenadas 1-based do valor e coluna do rótulo na mesma linha; origem completa via id_serie |
| escala_participacao, participacao_fracao | Escala 1 ou 100 inferida do total da coluna; fração resultante somente quando identificada; vazio não é zero |
| base_participacao | CV ou CT explícito, ou CT inferido pelo total quando coluna genérica; inferência conferida em tabela de validação |
| tipo, teste, residuo, tolerancia, aprovado | Identidade contábil ou conversão de unidade; residual observado menos esperado e aprovação no limite predefinido |
| residuo_fracao | Participação normalizada menos razão dos custos em ha, tolerância 0,001; ausência ou falha fica não aprovada |
| praca, uso | No auxiliar candidato, praça do nome concordante ou sem oposição do cabeçalho; uso restrito a descrição nominal |
| n, missing, zeros, negativos | Contagens dos agregados por cultura/unidade; não descrevem todos os itens de custo ou lacunas de cobertura |
| series, candidatas, ano_min, ano_max | Planilhas totais, filtro aprovado e limites dos anos de safra (máximo usa final da safra) |
| ano, n_agregados, candidata | Na cobertura detalhada, início da safra, número dos dez agregados monetários em ha e aprovação do filtro |

Dados deliberadamente não produzidos: custo municipal observado, margem/lucro, custos reais, custos algodão, médias entre tecnologias, custo zero para ano/praça ausente e correspondência espacial por bioma. São pendências de desenho e mensuração, não valores imputáveis automaticamente.

## Flags e novos produtos

Todas as flags abaixo são repetidas em cada linha de custos_ha_candidatos.csv e custos_ha_estritos.csv; não é necessário descobrir falhas apenas por join.

| Campo | Definição |
|---|---|
| flag_identidades_ok | Oito identidades (quatro por unidade) presentes e aprovadas |
| flag_unidades_ok | Dez verificações de conversão por produtividade presentes e aprovadas |
| flag_participacoes_ok | Todas as dez ou vinte verificações aplicáveis presentes e aprovadas |
| flag_territorio_ok | Ausência de conflito/ambiguidade entre praça da aba e cabeçalho; não equivale a mapeamento municipal |
| flag_verificacao_faltante | Teste esperado ausente, residual não calculável ou escala não identificada; bloqueia estrito |
| n_falhas_unidades, n_falhas_participacoes | Número de verificações não aprovadas na planilha, inclusive não calculáveis |
| estrito | Candidata que passa em todas as verificações acima, sem faltantes |
| motivos_exclusao_estrito | Lista cumulativa dos motivos; não deduzir contagem somando motivos sobrepostos |
| candidato | Em qualidade_por_serie.csv, filtro candidato anterior preservado |
| dimensao, valor, total, candidatas, estritas, candidatas_excluidas | Contagens marginais; dimensão é cultura, praça, tecnologia ou início da safra |
| residuo_decimal, falha_tolerancia | Recálculo independente com Decimal e tolerância original de R$0,02 |
| produtividade_confirmada, celula_produtividade | Produtividade e referência conferidas diretamente nas células |
| cabecalho_ha, cabecalho_saca | Evidência textual da unidade nas colunas monetárias usadas |
| n_itens_anteriores, envelope_arredondamento, classificacao | Diagnóstico exploratório permissivo de arredondamento acumulado, sem mudar aprovação estrita; compatibilidade não estabelece causa |
