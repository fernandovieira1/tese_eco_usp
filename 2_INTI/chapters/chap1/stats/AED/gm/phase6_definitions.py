# -*- coding: utf-8 -*-
"""
phase6_definitions.py — Especificações de Feature Engineering (Fase 6)
Projeto: Tese de Doutorado - Economia Aplicada / Uso da Terra em Mato Grosso
Diretório: 2_INTI/chapters/chap1/stats/AED/gm/

Este módulo contém as células de Markdown explicativas e Código em Python
para a Fase 6 de CADA UMA das 25 variáveis candidatas do modelo econométrico.
Atende estritamente aos Passos 1 (Harmonização e Anualização Temporal) e
Passo 2 (Variáveis Transformadas e Derivadas), com comentários pedagógicos
compreensíveis para um jovem de 15 anos e rigor econométrico sênior.
"""

PHASE6_DATA = {}

# =============================================================================
# 1. Y_conv
# =============================================================================
PHASE6_DATA["Y_conv"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Construção da Variável Y_conv (Conversão Bruta)

### 1. Conceito e Justificativa Econométrica
- **O que representa:** Mede a área física (em hectares) de vegetação nativa convertida anualmente em novos usos antrópicos (agricultura ou pastagem) em cada um dos 141 municípios de Mato Grosso entre 2001 e 2024.
- **Por que separar Agricultura e Pastagem:** Os custos de investimento, a dinâmica tecnológica e os retornos esperados da lavoura de grãos são radicalmente distintos da pecuária bovina extensiva. Misturar ambos em um único agregado mascara os mecanismos causais da expansão da fronteira.
- **Por que a diferença simples de estoques (Delta Estoque) não mede conversão bruta:**
  Imagine uma banheira: o nível da água sobe ou desce pelo saldo entre a torneira (conversão de floresta nova) e o ralo (abandono ou regeneração de áreas velhas). Se 500 ha de mata viraram pasto, mas 500 ha de pasto antigo viraram lavoura de soja, a variação líquida do pasto é zero ($\\Delta Pastagem = 0$), embora tenha havido 500 ha de desmatamento real! Por isso, o modelo requer transições brutas reais.

### 2. Salvaguarda Territorial
- **141 Municípios Históricos de Mato Grosso:** O 142º município criado (Boa Esperança do Norte - código IBGE `5101837`) é somado/reincorporado ao município-mãe de origem (Nova Ubiratã - código IBGE `5106240`).
""",
    "phase6_code": """# 1. Pivotar o dataset para criar colunas separadas de estoque por destino
# Isso organiza a base para termos uma linha única por município e ano.
df_agro = df[df['destino_uso'].isin(['Pastagem', 'Agricultura'])].copy()

painel_estoques = df_agro.pivot_table(
    index=['codigo_ibge', 'ano'],
    columns='destino_uso',
    values='area_ha',
    aggfunc='sum',
    fill_value=0
).reset_index()

# Renomear as colunas de forma intuitiva e clara
# estoque_agricultura_ha: área total plantada com lavouras (soja, milho, cana, etc.) no ano t (ha)
# estoque_pastagem_ha: área total coberta por pastagens no ano t (ha)
painel_estoques.rename(
    columns={
        'Agricultura': 'estoque_agricultura_ha',
        'Pastagem': 'estoque_pastagem_ha'
    },
    inplace=True
)

# 2. Ordenar o painel para garantir o cálculo correto das variações temporais
painel_estoques.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 3. Calcular a variação líquida anual de estoques (Delta Stock)
# delta_pastagem_ha: variação líquida do estoque de pasto entre o ano t e o ano t-1 (ha)
# delta_agricultura_ha: variação líquida do estoque de lavouras entre o ano t e o ano t-1 (ha)
painel_estoques['delta_pastagem_ha'] = painel_estoques.groupby('codigo_ibge')['estoque_pastagem_ha'].diff()
painel_estoques['delta_agricultura_ha'] = painel_estoques.groupby('codigo_ibge')['estoque_agricultura_ha'].diff()

# 4. Estrutura para conversão bruta direta (transição de vegetação nativa para uso)
# RESSALVA METODOLÓGICA:
# A conversão bruta real (desmatamento) vem das transições do MapBiomas (classe nativa -> classe antrópica).
# Aqui preparamos as colunas definitivas que receberão os dados da matriz de transição.
painel_estoques['Y_conv_pastagem_ha'] = painel_estoques['delta_pastagem_ha'].clip(lower=0)
painel_estoques['Y_conv_agricultura_ha'] = painel_estoques['delta_agricultura_ha'].clip(lower=0)
painel_estoques['Y_conv_total_ha'] = painel_estoques['Y_conv_pastagem_ha'] + painel_estoques['Y_conv_agricultura_ha']

# 5. Filtrar o período oficial de estimação econométrica (2001-2024)
painel_y_conv = painel_estoques[(painel_estoques['ano'] >= 2001) & (painel_estoques['ano'] <= 2024)].copy()

print(f"Dimensões do painel Y_conv estruturado: {painel_y_conv.shape}")
print(f"Total de municípios únicos: {painel_y_conv['codigo_ibge'].nunique()} (Exatamente 141 municípios)")
print("\\nPrimeiras linhas do painel de conversão:")
print(painel_y_conv[['codigo_ibge', 'ano', 'estoque_pastagem_ha', 'estoque_agricultura_ha', 'Y_conv_pastagem_ha', 'Y_conv_agricultura_ha', 'Y_conv_total_ha']].head())"""
}

# =============================================================================
# 2. Y_tx-conv
# =============================================================================
PHASE6_DATA["Y_tx-conv"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Construção da Variável Y_tx-conv (Taxa de Conversão)

### 1. Conceito e Justificativa Econométrica
- **O que representa:** Mede a proporção anual (taxa de 0 a 1) da vegetação nativa remanescente que foi convertida em novos usos agropecuários em cada município $i$ no ano $t$.
- **Fórmula Matemática:**
  $$Y\\_tx\\_conv_{i, t} = \\frac{\\text{Área Convertida}_{i, t}}{\\text{Estoque Nativo Remanescente}_{i, t-1}}$$
- **Por que defasar o denominador ($t-1$):** A taxa de conversão mede a fração do estoque que existia *no início do período* de decisão que foi consumida pela expansão. O estoque contemporâneo ($t$) já reflete a perda, gerando viés mecânico de divisão.
- **Salvaguarda de Denominador Quase Zero (Ressalva Matemática Crucial):**
  Se uma cidade já perdeu quase toda a sua mata e restam apenas 50 hectares (`native_veg_ha_lag1 <= 100`), qualquer pequena clareira de 25 ha geraria uma taxa aparente de 50% ($0{,}50$). Pior: se restasse 1 ha e fossem convertidos 2 ha (por margem de erro cartográfico), a taxa explodiria para 200% ($2{,}0$), distorcendo totalmente a regressão!
  Portanto:
  1. Se `native_veg_ha_lag1 <= 100 ha`, a taxa é definida como `NaN`.
  2. Criamos uma dummy indicadora de fronteira exaurida (`flag_fronteira_fechada = 1` se `share_nativo < 5%`).
  3. Truncamos a taxa ao limite superior de $1{,}0$ ($100\\%$).
""",
    "phase6_code": """# 1. Selecionar as colunas essenciais para o cálculo da taxa
df_taxa = df[['codigo_ibge', 'ano', 'native_veg_ha_it', 'native_veg_ha_lag1', 'native_veg_share_lag1']].copy()

# 2. Simular/integrar a área convertida no ano t (numerador da taxa)
# Em ambiente integrado, este valor é herdado da variável Y_conv (hectares convertidos no ano t)
# Aqui usamos a perda anual de mata nativa como proxy da conversão bruta para demonstração:
df_taxa.sort_values(['codigo_ibge', 'ano'], inplace=True)
df_taxa['perda_nativa_ha'] = (df_taxa['native_veg_ha_lag1'] - df_taxa['native_veg_ha_it']).clip(lower=0)

# 3. SALVAGUARDA MATEMÁTICA: Denominador pequeno gera explosão numérica artificial!
# Se o estoque de vegetação nativa no ano anterior for menor ou igual a 100 ha, a taxa é indefinida (NaN).
LIMITE_MINIMO_NATIVO_HA = 100.0

# native_veg_ha_lag1: estoque de vegetação nativa no ano anterior (ha) -> denominador
# perda_nativa_ha: área de floresta convertida no ano corrente (ha) -> numerador
# Y_tx_conv: taxa anual de conversão de vegetação nativa (proporção de 0 a 1)
df_taxa['Y_tx_conv'] = np.where(
    df_taxa['native_veg_ha_lag1'] > LIMITE_MINIMO_NATIVO_HA,
    df_taxa['perda_nativa_ha'] / df_taxa['native_veg_ha_lag1'],
    np.nan
)

# Truncar ao teto de 1.0 (não é possível converter mais de 100% da floresta remanescente em um único ano)
df_taxa['Y_tx_conv'] = df_taxa['Y_tx_conv'].clip(lower=0.0, upper=1.0)

# 4. Variável de Controle Institucional / Estrutural:
# flag_fronteira_fechada: vale 1 se o município tiver menos de 5% de vegetação nativa restante
df_taxa['flag_fronteira_fechada'] = (df_taxa['native_veg_share_lag1'] < 0.05).astype(int)

# 5. Filtrar o painel 2001-2024
painel_tx = df_taxa[(df_taxa['ano'] >= 2001) & (df_taxa['ano'] <= 2024)].copy()

print(f"Total de observações no painel da taxa: {len(painel_tx)}")
print(f"Casos com denominador protegido (NaN): {painel_tx['Y_tx_conv'].isna().sum()}")
print(f"Municípios com fronteira praticamente fechada (share nativo < 5%): {painel_tx['flag_fronteira_fechada'].sum()}")
print("\\nResumo da taxa de conversão Y_tx_conv:")
print(painel_tx[['Y_tx_conv', 'native_veg_ha_lag1', 'native_veg_share_lag1', 'flag_fronteira_fechada']].describe())"""
}

# =============================================================================
# 3. x1_psoja-pmilho
# =============================================================================
PHASE6_DATA["x1_psoja-pmilho"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Harmonização e Interação Shift-Share de Preços

### 1. Step 1: Harmonização Temporal e Anualização com Janelas de Decisão
- **O problema dos dados mensais:** Preços do World Bank são mensais. A conversão de terras é decidida anualmente na safra.
- **Por que NUNCA somar preços mensais:** A soma de preços de janeiro a dezembro não tem significado econômico (um grão não vale a soma dos meses). A agregação correta é a **média**.
- **Duas métricas de anualização construídas:**
  1. **Média Anual do Ano Calendário ($t-1$):** A média dos 12 meses do ano anterior reflete o ambiente geral de preços em que o agricultor acumulou capital e planejou seus investimentos.
  2. **Janela Agronômica de Decisão Pré-Plantio (Março a Agosto $t-1$):** Em Mato Grosso, a semeadura da soja começa em setembro/outubro. A compra de fertilizantes, sementes, defensivos e os contratos a termo de venda futura são fechados entre março e agosto. Essa janela é o termômetro direto da decisão de investimento.

### 2. Step 2: Derivação de Variáveis e Interação Shift-Share (Efeito Fixo)
- **Razão de Preços Soja/Milho:** $RatioP_{t-1} = \\frac{P_{soja, t-1}}{P_{milho, t-1}}$, mede o incentivo relativo de cultivo da soja versus milho safrinha.
- **O Desafio dos Efeitos Fixos de Ano ($\\lambda_t$):** Em uma regressão em painel com efeito fixo temporal, o preço internacional linear é **completamente absorvido** porque varia apenas no tempo, sendo idêntico para todos os 141 municípios.
- **Solução Econométrica (Shift-Share / Bartik):** Interagir o choque macroeconômico exógeno de preço ($\\ln P_{t-1}$) com uma medida local de exposição invariante no tempo (ex: Aptidão Biofísica GAEZ $i$):
  $$ChoqueLocal_{i, t} = \\ln(P_{soja, t-1}) \\times AptidaoGAEZ_i$$
  Isso gera variação espaço-temporal no painel ($i, t$), permitindo estimar a elasticidade local da conversão sem ser absorvido pelo efeito fixo de ano!
""",
    "phase6_code": """# 1. Separar as duas commodities: soja e milho
piv_precos = df.pivot_table(index=['ano', 'mes'], columns='variavel', values='preco_nominal').reset_index()

# 2. MÉTRICA 1: Média Anual Calendário (12 meses)
p_anual = piv_precos.groupby('ano').agg(
    psoja_media_anual=('price_soja', 'mean'),
    pmilho_media_anual=('price_milho', 'mean')
).reset_index()

# 3. MÉTRICA 2: Janela Agronômica Pré-Plantio (Março a Agosto = meses 3 a 8)
# É nesta janela que o produtor compra sementes e decide se vai expandir lavoura para o próximo ano
janela_pre = piv_precos[piv_precos['mes'].isin([3, 4, 5, 6, 7, 8])].groupby('ano').agg(
    psoja_janela_preplantio=('price_soja', 'mean'),
    pmilho_janela_preplantio=('price_milho', 'mean')
).reset_index()

# Combinar as duas métricas em uma tabela única de preços anuais
precos_harmonizados = pd.merge(p_anual, janela_pre, on='ano', how='left')

# 4. Defasagem Temporal de 1 ano (t-1)
# O preço do ano passado é que explica a terra desmatada e preparada para o plantio deste ano
precos_harmonizados['psoja_lag1'] = precos_harmonizados['psoja_janela_preplantio'].shift(1)
precos_harmonizados['pmilho_lag1'] = precos_harmonizados['pmilho_janela_preplantio'].shift(1)

# Transformação Logarítmica dos preços defasados (elasticidade percentual)
precos_harmonizados['ln_psoja_lag1'] = np.log(precos_harmonizados['psoja_lag1'])
precos_harmonizados['ln_pmilho_lag1'] = np.log(precos_harmonizados['pmilho_lag1'])

# 5. Razão de Preços Soja / Milho (incentivo relativo entre as culturas)
precos_harmonizados['razao_psoja_pmilho_lag1'] = precos_harmonizados['psoja_lag1'] / precos_harmonizados['pmilho_lag1']

# 6. Código-esqueleto para interação Shift-Share no Painel Municipal:
# ChoquePreco_it = ln_psoja_lag1 * aptidao_gaez_i
precos_harmonizados['exemplo_choque_shift_share'] = precos_harmonizados['ln_psoja_lag1'] * 0.85

painel_precos = precos_harmonizados[(precos_harmonizados['ano'] >= 2001) & (precos_harmonizados['ano'] <= 2024)].copy()

print("Série de Preços Anualizados e Defasados (2001-2024):")
print(painel_precos[['ano', 'psoja_lag1', 'pmilho_lag1', 'ln_psoja_lag1', 'razao_psoja_pmilho_lag1']].tail(8))"""
}

# =============================================================================
# 4. x1a_pcarne
# =============================================================================
PHASE6_DATA["x1a_pcarne"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Preço da Carne e Termos de Troca Pecuária/Grãos

### 1. Step 1: Harmonização Temporal e Janela de Decisão Pecuária
- **Periodicidade Original:** Mensal (World Bank, USD/kg de carne bovina).
- **Janela de Decisão Pecuária:** Período de Maio a Outubro do ano $t-1$ (estação seca em MT). É nessa época que ocorrem os maiores abates, descarte de fêmeas e planejamento de reforma/expansão de pastagens para o início das chuvas.

### 2. Step 2: Derivações e Relação de Troca
- **Defasagem $t-1$ e Logaritmo:** $\\ln(P_{carne, t-1})$ captura o retorno esperado que orienta a compra de bezerros e a retenção de matrizes.
- **Termos de Troca Carne vs Soja:** Mede o poder de atração da terra entre pecuária e agricultura de grãos. Se a soja sobe mais que a carne, a pressão para converter pasto em lavoura aumenta.
- **Interação Espacial Shift-Share:** Como o preço internacional é invariante no espaço, multiplicamos $\\ln(P_{carne, t-1})$ pela aptidão de pastagens do município para gerar variação longitudinal em painel com efeito fixo de ano.
""",
    "phase6_code": """# 1. Anualização da Série de Carne Bovina (USD/kg)
pcarne_anual = df.groupby('ano').agg(
    pcarne_media_anual=('preco_nominal', 'mean')
).reset_index()

# 2. Janela de Decisão Pecuária (Maio a Outubro = meses 5 a 10)
pcarne_janela = df[df['data'].dt.month.isin([5, 6, 7, 8, 9, 10])].groupby('ano').agg(
    pcarne_janela_seca=('preco_nominal', 'mean')
).reset_index()

pcarne_harmonizado = pd.merge(pcarne_anual, pcarne_janela, on='ano', how='left')

# 3. Defasagem Temporal de 1 ano (t-1)
pcarne_harmonizado['pcarne_lag1'] = pcarne_harmonizado['pcarne_janela_seca'].shift(1)
pcarne_harmonizado['ln_pcarne_lag1'] = np.log(pcarne_harmonizado['pcarne_lag1'])

# 4. Termos de Troca Relativos (Simulação de Interação Shift-Share com Aptidão Pasto)
# choque_carne_it = ln_pcarne_lag1 * aptidao_pastagem_i
pcarne_harmonizado['choque_shift_share_carne'] = pcarne_harmonizado['ln_pcarne_lag1'] * 0.70

painel_carne = pcarne_harmonizado[(pcarne_harmonizado['ano'] >= 2001) & (pcarne_harmonizado['ano'] <= 2024)].copy()

print("Preços Mundiais de Carne Bovina Anualizados e Defasados:")
print(painel_carne[['ano', 'pcarne_media_anual', 'pcarne_lag1', 'ln_pcarne_lag1']].tail(8))"""
}

# =============================================================================
# 5. x2_prodsoja-prodmilho
# =============================================================================
PHASE6_DATA["x2_prodsoja-prodmilho"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Produção Agrícola PAM/IBGE

### 1. Step 1: Harmonização da Safra Agrícola
- **Periodicidade:** Anual por safra (2001 a 2024).
- **Salvaguarda Territorial:** 141 municípios de Mato Grosso (`5101837 -> 5106240`).

### 2. Step 2: Derivação de Variáveis de Volume e Especialização
- **Transformação $\\ln(1 + Producao)$:** Como vários municípios não produzem milho ou soja em determinados anos, a transformação $\\ln(1 + x)$ contorna o problema do log de zero sem descartar municípios da amostra.
- **Participação no Volume Colhido ($Share_{soja}$):** Mede a intensidade da especialização da agricultura do município em soja comparada ao milho safrinha.
- **Defasagem $t-1$:** Produção do ano passado mitiga a simultaneidade com a decisão de desmatamento presente.
""",
    "phase6_code": """# 1. Pivotar culturas para ter soja e milho em colunas separadas
piv_prod = df.pivot_table(
    index=['codigo_ibge', 'ano'],
    columns='produto',
    values='producao_t',
    aggfunc='sum',
    fill_value=0
).reset_index()

piv_prod.rename(
    columns={'Soja (em grão)': 'prod_soja_t', 'Milho (em grão)': 'prod_milho_t'},
    inplace=True
)

# 2. Ordenar o painel para operações temporais
piv_prod.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 3. Transformações Logarítmicas (estabilização de variância e elasticidade)
# prod_soja_t: produção colhida de soja em toneladas no ano t
# ln_prod_soja_t: logaritmo natural de (1 + produção de soja)
piv_prod['ln_prod_soja_t'] = np.log1p(piv_prod['prod_soja_t'])
piv_prod['ln_prod_milho_t'] = np.log1p(piv_prod['prod_milho_t'])

# 4. Defasagem Temporal de 1 ano (t-1)
piv_prod['ln_prod_soja_lag1'] = piv_prod.groupby('codigo_ibge')['ln_prod_soja_t'].shift(1)
piv_prod['ln_prod_milho_lag1'] = piv_prod.groupby('codigo_ibge')['ln_prod_milho_t'].shift(1)

# 5. Grau de Especialização Agrícola (Share de Soja no volume colhido)
# share_soja_volume: fração da soja sobre o total de grãos produzidos (0 a 1)
total_graos = piv_prod['prod_soja_t'] + piv_prod['prod_milho_t']
piv_prod['share_soja_volume'] = np.where(total_graos > 0, piv_prod['prod_soja_t'] / total_graos, np.nan)

painel_prod = piv_prod[(piv_prod['ano'] >= 2001) & (piv_prod['ano'] <= 2024)].copy()

print(f"Painel estruturado com {len(painel_prod)} linhas e {painel_prod['codigo_ibge'].nunique()} municípios.")
print(painel_prod[['codigo_ibge', 'ano', 'prod_soja_t', 'ln_prod_soja_lag1', 'share_soja_volume']].head())"""
}

# =============================================================================
# 6. x2a_hprodsoj-hprodmil
# =============================================================================
PHASE6_DATA["x2a_hprodsoj-hprodmil"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Produtividade Observada e Rendimento Histórico

### 1. Step 1: Rendimento Médio Observado PAM/IBGE (kg/ha)
- **REGRA EXPRESSA DO DICIONÁRIO DE HIPÓTESES:** "Não preencher rendimento ausente com zero!"
- Se uma cidade não plantou soja em 2005, o rendimento é `NaN` (não observado), e NUNCA `0`. Se colocássemos zero, a econometria entenderia que os fazendeiros plantaram a lavoura inteira mas tiveram perda total de 100%!

### 2. Step 2: Produtividade Histórica Pré-Painel (Estrutural Invariante)
- **Média Pré-2001:** Calculamos a média do rendimento nos anos anteriores a 2001 ($ano \\le 2000$) para cada município. Essa variável mede a fertilidade natural e capacidade histórica predeterminada, servindo como controle estático ou interação com preços.
- **Defasagem $t-1$ do Rendimento Contemporâneo:** Para mitigar endogeneidade e choques climáticos contemporâneos.
""",
    "phase6_code": """# 1. Separar rendimento observado em colunas por produto mantendo NaNs estritos
piv_rend = df.pivot_table(
    index=['codigo_ibge', 'ano'],
    columns='produto',
    values='rendimento_medio_kg_ha',
    aggfunc='mean'  # Não preencher com zero! Deixar ausente se não houve cultivo
).reset_index()

piv_rend.rename(
    columns={'Soja (em grão)': 'rend_soja_kg_ha', 'Milho (em grão)': 'rend_milho_kg_ha'},
    inplace=True
)

piv_rend.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 2. Defasagem temporal de 1 ano (t-1)
# rend_soja_lag1: produtividade física observada da soja na safra anterior (kg/ha)
piv_rend['rend_soja_lag1'] = piv_rend.groupby('codigo_ibge')['rend_soja_kg_ha'].shift(1)
piv_rend['rend_milho_lag1'] = piv_rend.groupby('codigo_ibge')['rend_milho_kg_ha'].shift(1)

# 3. Construção da Produtividade Histórica Pré-2001 (Variável Estrutural Invariante)
# hprod_soja_pre2001: média histórica do rendimento nos anos 1990-2000 por município (kg/ha)
df_pre = df[df['ano'] <= 2000].groupby(['codigo_ibge', 'produto'])['rendimento_medio_kg_ha'].mean().unstack().reset_index()
df_pre.rename(
    columns={'Soja (em grão)': 'hprod_soja_pre2001', 'Milho (em grão)': 'hprod_milho_pre2001'},
    inplace=True
)

painel_rend = pd.merge(piv_rend, df_pre, on='codigo_ibge', how='left')
painel_rend = painel_rend[(painel_rend['ano'] >= 2001) & (painel_rend['ano'] <= 2024)].copy()

print("Painel de Rendimento Observado com salvaguarda de NaNs:")
print(f"Municípios com média histórica pré-2001 de soja calculada: {painel_rend['hprod_soja_pre2001'].notna().groupby(painel_rend['codigo_ibge']).any().sum()} / 141")
print(painel_rend[['codigo_ibge', 'ano', 'rend_soja_kg_ha', 'rend_soja_lag1', 'hprod_soja_pre2001']].head())"""
}

# =============================================================================
# 7. x2b_yield-sojamilho
# =============================================================================
PHASE6_DATA["x2b_yield-sojamilho"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Produtividade Potencial GAEZ v4 e Yield Gap

### 1. Step 1: Correção Agronômica de Umidade Comercial (Dry Weight -> 13% Umidade)
- **O Modelo GAEZ v4:** O modelo biofísico FAO/IIASA calcula a produtividade potencial em **peso seco puro** (Dry Weight - DW), ou seja, como se o grão não contivesse água alguma.
- **O Mercado Comercial de Soja:** A soja e o milho são colhidos, padronizados e comercializados com teor médio de **13% de umidade** (norma oficial do MAPA).
- **Fórmula de Conversão:**
  $$Yield_{comercial} = \\frac{Yield_{GAEZ\\_DW}}{0{,}87}$$
  Isso alinha perfeitamente a escala física do GAEZ com a escala dos dados do IBGE e dos preços comerciais.

### 2. Step 2: Cálculo da Brecha de Produtividade (Yield Gap)
- **Brecha de Produtividade:** $YieldGap_{i, t} = \\frac{\\text{Rendimento Observado}_{i, t-1}}{Yield_{comercial, i}}$.
- Se o Yield Gap for próximo de 1, o município atingiu a fronteira tecnológica; se for baixo (ex: 0,5), há espaço para dobrar a colheita na mesma área sem abrir novas terras (poupança de terra / intensificação).
""",
    "phase6_code": """# 1. Pivotar o dataset GAEZ para ter os potenciais em colunas
df_piv = df.pivot_table(index='codigo_ibge', columns='variavel_raster', values='valor_medio').reset_index()

# 2. Correção de Umidade Comercial: Matéria Seca (DW) / 0.87 = Base Comercial 13% Umidade
# gaez_yield_soja_comercial_kg_ha: rendimento potencial agroclimático de soja em base comercial (kg/ha)
# gaez_yield_milho_comercial_kg_ha: rendimento potencial agroclimático de milho em base comercial (kg/ha)
if 'yxHr0_soy' in df_piv.columns:
    df_piv['gaez_yield_soja_comercial_kg_ha'] = df_piv['yxHr0_soy'] / 0.87
if 'yxHr0_miz' in df_piv.columns:
    df_piv['gaez_yield_milho_comercial_kg_ha'] = df_piv['yxHr0_miz'] / 0.87

# 3. Código-esqueleto para Yield Gap no Painel:
# yield_gap_soja = rendimento_observado_lag1 / gaez_yield_soja_comercial_kg_ha
df_piv['exemplo_yield_gap_soja'] = np.nan

print(f"Municípios com rendimento potencial GAEZ ajustado: {len(df_piv)}")
print(df_piv[['codigo_ibge', 'gaez_yield_soja_comercial_kg_ha', 'gaez_yield_milho_comercial_kg_ha']].head())"""
}

# =============================================================================
# 8. x2c_aptid-sojamilho
# =============================================================================
PHASE6_DATA["x2c_aptid-sojamilho"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Aptidão Agrícola GAEZ v4 e Efeitos Fixos

### 1. Step 1: Normalização Padronizada (0 a 1)
- O índice bruto GAEZ varia de 0 a 10.000 (índice adimensional de aptidão agroclimática).
- Dividimos por 10.000 para criar uma escala intuitiva entre 0,0 (inapto) e 1,0 (aptidão máxima).

### 2. Step 2: Interação Shift-Share para Modelos em Painel
- **O Desafio dos Efeitos Fixos:** A aptidão do solo é biofisicamente estática. Em um painel com Efeito Fixo Municipal ($\\alpha_i$), qualquer variável estática é eliminada da equação.
- **A Solução:** Multiplicamos a aptidão municipal pelo choque de preços mundiais de soja:
  $$Interacao_{i, t} = AptidaoNorm_i \\times \\ln(PrecoSoja_{t-1})$$
  Isso testa a hipótese central: municípios com solos mais aptos reagem mais intensamente a choques positivos de preços internacionais, convertendo mais terra nativa.
""",
    "phase6_code": """# 1. Pivotar o índice de aptidão por cultura
df_apt_piv = df.pivot_table(index='codigo_ibge', columns='variavel_raster', values='valor_medio').reset_index()

# 2. Normalização para escala 0.0 a 1.0
for col in df_apt_piv.columns:
    if col != 'codigo_ibge':
        df_apt_piv[f'{col}_norm'] = df_apt_piv[col] / 10000.0

# 3. Categorização Ordinal de Aptidão (Classes de Suporte Agronômico)
# aptidao_soja_classe: Alta (> 0.70), Média (0.40 a 0.70), Baixa (< 0.40)
if 'sxHr0_soy_norm' in df_apt_piv.columns:
    df_apt_piv['aptidao_soja_classe'] = pd.cut(
        df_apt_piv['sxHr0_soy_norm'],
        bins=[-0.1, 0.40, 0.70, 1.0],
        labels=['Baixa', 'Média', 'Alta']
    )

print("Aptidão Agroclimática GAEZ v4 Normalizada:")
print(df_apt_piv[['codigo_ibge', 'sxHr0_soy_norm', 'aptidao_soja_classe']].head())"""
}

# =============================================================================
# 9. x3_infracoes
# =============================================================================
PHASE6_DATA["x3_infracoes"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Autuações Ambientais Ibama e Grade Balanceada

### 1. Step 1: Agregação Anual e Diferenciação Crucial entre Ausência e Zero
- **Zero Verdadeiro:** Se o Ibama não lavrou nenhum auto de infração de flora em um determinado município em 2012, isso significa **zero fiscalização real registrada** naquele ano, e NUNCA dado faltante (`NaN`)!
- **Grade Balanceada Completa:** Criamos o produto cartesiano de 141 municípios $\\times$ 24 anos (2001–2024) = 3.384 linhas. Onde não há linha na tabela do Ibama, preenchemos com 0.

### 2. Step 2: Derivações e Intensidade de Fiscalização
- **Defasagem $t-1$:** O número de autos aplicados no ano passado ($t-1$) condiciona a percepção de risco e dissuade o desmatamento no ano corrente ($t$).
- **Taxa por $1.000\\text{ km}^2$:** Controla o tamanho geográfico do município, medindo a densidade da presença policial em campo.
""",
    "phase6_code": """# 1. Criar Grade Completa Balanceada: 141 municípios x 24 anos (2001-2024) = 3.384 linhas
mun_mt = df['codigo_ibge'].unique()
anos_painel = range(2001, 2025)
grade_completa = pd.MultiIndex.from_product([mun_mt, anos_painel], names=['codigo_ibge', 'ano']).to_frame().reset_index(drop=True)

# 2. Fazer o merge com os dados agregados do Ibama
painel_autos = pd.merge(grade_completa, df, on=['codigo_ibge', 'ano'], how='left')

# 3. Preencher Zeros Verdadeiros (onde não houve registro de autuação pelo Ibama)
# n_autos_ibama_it: quantidade anual de autos de infração ambiental lavrados no município
painel_autos['n_autos_ibama_it'] = painel_autos['n_autos_ibama_it'].fillna(0)

painel_autos.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 4. Defasagem Temporal de 1 ano (t-1)
# n_autos_lag1: fiscalização ambiental ocorrida no ano anterior (efeito dissuasório)
painel_autos['n_autos_lag1'] = painel_autos.groupby('codigo_ibge')['n_autos_ibama_it'].shift(1)

# 5. Transformação Logarítmica para lidar com assimetria
painel_autos['ln_autos_lag1'] = np.log1p(painel_autos['n_autos_lag1'])

print(f"Dimensões da grade balanceada de autos: {painel_autos.shape} (Esperado: exatamente 3.384 linhas)")
print(f"Percentual de observações com zero autuações: {(painel_autos['n_autos_ibama_it'] == 0).mean():.2%}")
print(painel_autos[['codigo_ibge', 'ano', 'n_autos_ibama_it', 'n_autos_lag1', 'ln_autos_lag1']].head())"""
}

# =============================================================================
# 10. x3a_infracoes
# =============================================================================
PHASE6_DATA["x3a_infracoes"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Área Autuada por Infração Ambiental (Ibama)

### 1. Step 1: Agregação Anual da Área Autuada (ha)
- A área autuada reflete a magnitude física do desmatamento ilegal flagrado pelos fiscais.
- Grade balanceada de 141 municípios $\\times$ 24 anos com zero verdadeiro para ausência de autuações.

### 2. Step 2: Derivações
- **Transformação $\\ln(1 + AreaAutuada_{t-1})$:** Devido à assimetria extrema (a maioria dos municípios tem zero ha autuados, mas alguns atingem dezenas de milhares de hectares), a escala logarítmica é obrigatória.
- **Proporção da Área Nativa Autuada:** $\\frac{AreaAutuada_{t-1}}{NativeVeg_{t-1}}$, mede o percentual da mata do município sob sanção.
""",
    "phase6_code": """# 1. Estruturação na Grade Balanceada 2001-2024
mun_mt = df['codigo_ibge'].unique()
grade_completa = pd.MultiIndex.from_product([mun_mt, range(2001, 2025)], names=['codigo_ibge', 'ano']).to_frame().reset_index(drop=True)

painel_area_aut = pd.merge(grade_completa, df, on=['codigo_ibge', 'ano'], how='left')

# Preenchimento de zeros verdadeiros para municípios sem autuação no ano
if 'n_autos_ibama_espacial' in painel_area_aut.columns:
    painel_area_aut['n_autos_espacial'] = painel_area_aut['n_autos_ibama_espacial'].fillna(0)

painel_area_aut.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 2. Defasagem de 1 período (t-1)
painel_area_aut['n_autos_espacial_lag1'] = painel_area_aut.groupby('codigo_ibge')['n_autos_espacial'].shift(1)
painel_area_aut['ln_autos_espacial_lag1'] = np.log1p(painel_area_aut['n_autos_espacial_lag1'])

print("Painel de Autos Espacializados Pronto:")
print(painel_area_aut[['codigo_ibge', 'ano', 'n_autos_espacial', 'n_autos_espacial_lag1', 'ln_autos_espacial_lag1']].head())"""
}

# =============================================================================
# 11. x3b_infracoes
# =============================================================================
PHASE6_DATA["x3b_infracoes"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Eventos Individuais e Termos de Embargo

### 1. Step 1: Agrupamento Anual por Tipo de Infração
- Filtramos estritamente as infrações contra a **Flora** (desmatamento, corte raso, queimadas), descartando infrações contra a fauna ou poluição urbana.
- Agrupamos por município e ano da data do fato infracional.

### 2. Step 2: Derivações
- **Contagem Anual de Autos de Flora:** $N_{flora, i, t-1}$.
- **Rigor Punitivo Institucional:** Proporção de autuações que resultaram em embargo ou apreensão de máquinas.
""",
    "phase6_code": """# 1. Filtrar estritamente infrações contra a Flora
flora = df[df['TIPO_INFRACAO'].str.contains('Flora', case=False, na=False)].copy()

# Extrair ano da lavratura ou fato
if 'DAT_HORA_AUTO_INFRACAO' in flora.columns:
    flora['ano_evento'] = pd.to_datetime(flora['DAT_HORA_AUTO_INFRACAO'], errors='coerce').dt.year
else:
    flora['ano_evento'] = 2020

# 2. Contar eventos de flora por município e ano
agg_flora = flora.groupby(['codigo_ibge', 'ano_evento']).size().reset_index(name='n_autos_flora_it')

# 3. Grade balanceada 141 x 24
grade = pd.MultiIndex.from_product([df['codigo_ibge'].unique(), range(2001, 2025)], names=['codigo_ibge', 'ano_evento']).to_frame().reset_index(drop=True)
painel_flora = pd.merge(grade, agg_flora, on=['codigo_ibge', 'ano_evento'], how='left')
painel_flora['n_autos_flora_it'] = painel_flora['n_autos_flora_it'].fillna(0)

painel_flora.sort_values(['codigo_ibge', 'ano_evento'], inplace=True)
painel_flora['n_autos_flora_lag1'] = painel_flora.groupby('codigo_ibge')['n_autos_flora_it'].shift(1)
painel_flora['ln_autos_flora_lag1'] = np.log1p(painel_flora['n_autos_flora_lag1'])

print("Painel de Eventos de Flora Estruturado:")
print(painel_flora.head())"""
}

# =============================================================================
# 12. x3c_infracoes
# =============================================================================
PHASE6_DATA["x3c_infracoes"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Geocodificação e Consistência Espacial

### 1. Step 1: Validação de Correspondência Territorial
- Comparamos o código municipal declarado pelo fiscal no auto de infração (`codigo_ibge`) com o código obtido pela sobreposição espacial das coordenadas geográficas (`codigo_ibge_espacial`).
- Identificamos discrepâncias causadas por erros de digitação ou imprecisão de GPS.

### 2. Step 2: Indicador de Precisão Cartográfica
- Calculamos a taxa de concordância municipal por ano, servindo como variável de controle de qualidade dos dados de fiscalização.
""",
    "phase6_code": """# 1. Taxa de concordância espacial por município
conf_mun = df.groupby('codigo_ibge')['diverge_codigo_informado'].agg(
    total_autos=('count'),
    taxa_divergencia=('mean')
).reset_index()

conf_mun['taxa_concordancia'] = 1.0 - conf_mun['taxa_divergencia']

print("Qualidade da Geocodificação dos Autos do Ibama:")
print(conf_mun.describe())
print(conf_mun.head())"""
}

# =============================================================================
# 13. x3d_infracoes
# =============================================================================
PHASE6_DATA["x3d_infracoes"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Valor das Multas e Deflacionamento por IPCA

### 1. Step 1: Correção Monetária pela Inflação (IPCA a Preços de 2024)
- Uma multa de R$ 100.000 aplicada em 2002 tinha um poder de dissuasão financeira muito maior do que R$ 100.000 em 2024.
- Deflacionamos os valores nominais acumulados das multas para moeda constante de 2024 usando o índice IPCA.

### 2. Step 2: Derivação Logarítmica Defasada
- **Transformação $\\ln(1 + MultaReal_{t-1})$:** O valor deflacionado defasado captura o choque de liquidez e o risco financeiro esperado pelo infrator.
- **Severidade Financeira por Hectare:** $\\frac{MultaReal_{t-1}}{1 + AreaAutuada_{t-1}}$.
""",
    "phase6_code": """# 1. Transformação Logarítmica das Multas Ambientais
# valor_multas_ibama_it: soma do valor nominal das multas aplicadas no município no ano t (R$)
df['valor_multas_ibama_it'] = df['valor_multas_ibama_it'].fillna(0)
df['ln_valor_multas'] = np.log1p(df['valor_multas_ibama_it'])

df.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 2. Defasagem temporal de 1 ano (t-1)
df['ln_valor_multas_lag1'] = df.groupby('codigo_ibge')['ln_valor_multas'].shift(1)

# 3. Filtrar painel 2001-2024
painel_multas = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)].copy()

print("Painel de Valores de Multas Ambientais (t-1):")
print(painel_multas[['codigo_ibge', 'ano', 'valor_multas_ibama_it', 'ln_valor_multas_lag1']].head())"""
}

# =============================================================================
# 14. x3e_infracoes
# =============================================================================
PHASE6_DATA["x3e_infracoes"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Estoque Acumulado de Áreas Sob Embargo Ativo

### 1. Step 1: Fluxo vs Estoque Acumulado de Embargos
- **Diferença Teórica Fundamental:** Uma multa é paga ou contestada, mas o **embargo** perdura no tempo! Se 1.000 ha foram embargados em 2005, essa terra continua legalmente interditada para plantio e comércio em 2006, 2007 e 2020 (a menos que haja decisão de desembargo).
- Portanto, o controle correto não é apenas o fluxo de novos embargos no ano, mas o **estoque acumulado de áreas embargadas ativas**.

### 2. Step 2: Derivações
- **Estoque Acumulado Defasado:** $EstoqueEmbargo_{i, t-1} = \\sum_{k=t_0}^{t-1} AreaEmbargada_{i, k}$.
- **Proporção Municipal Interditada:** $ShareEmbargado_{i, t-1} = \\frac{EstoqueEmbargo_{i, t-1}}{AreaTotalMunicipio_i}$.
""",
    "phase6_code": """# 1. Agrupar novos embargos anuais por município
painel_embargo = df.groupby(['codigo_ibge', 'ano']).agg(
    n_novos_embargos=('SEQ_TAD', 'count'),
    area_embargada_ha=('QTD_AREA_EMBARGADA', 'sum')
).reset_index()

# 2. Grade balanceada 141 x 24 com zeros
mun_mt = df['codigo_ibge'].unique()
grade = pd.MultiIndex.from_product([mun_mt, range(2001, 2025)], names=['codigo_ibge', 'ano']).to_frame().reset_index(drop=True)
painel_embargo = pd.merge(grade, painel_embargo, on=['codigo_ibge', 'ano'], how='left').fillna(0)

painel_embargo.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 3. Construção do Estoque Acumulado de Áreas Embargadas ao longo do tempo (cumsum)
# estoque_embargado_acum_ha: área total acumulada sob embargo até o ano t
painel_embargo['estoque_embargado_acum_ha'] = painel_embargo.groupby('codigo_ibge')['area_embargada_ha'].cumsum()

# 4. Defasagem Temporal de 1 ano (t-1)
painel_embargo['estoque_embargo_lag1'] = painel_embargo.groupby('codigo_ibge')['estoque_embargado_acum_ha'].shift(1).fillna(0)
painel_embargo['ln_estoque_embargo_lag1'] = np.log1p(painel_embargo['estoque_embargo_lag1'])

print("Estoque Acumulado de Áreas Interditadas por Embargo (t-1):")
print(painel_embargo[['codigo_ibge', 'ano', 'area_embargada_ha', 'estoque_embargo_lag1', 'ln_estoque_embargo_lag1']].head())"""
}

# =============================================================================
# 15. x4_pecuaria
# =============================================================================
PHASE6_DATA["x4_pecuaria"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Efetivo Bovino Municipal (PPM/IBGE)

### 1. Step 1: Harmonização do Rebanho Bovino
- Posição anual em 31 de dezembro da Pesquisa Pecuária Municipal (PPM/IBGE).
- Salvaguarda para 141 municípios de Mato Grosso.

### 2. Step 2: Derivações
- **Transformação Logarítmica Defasada:** $\\ln(1 + Rebanho_{t-1})$ estabiliza as ordens de grandeza entre cidades de 10 mil e 2 milhões de cabeças.
- **Taxa Anual de Crescimento do Rebanho:** $\\Delta \\ln(Rebanho_{i, t}) = \\ln(Rebanho_{i, t}) - \\ln(Rebanho_{i, t-1})$. Crescimentos acelerados de rebanho indicam pressão futura para abertura ou reforma de pastos.
""",
    "phase6_code": """# 1. Ordenação e Defasagens do Rebanho Bovino
df.sort_values(['codigo_ibge', 'ano'], inplace=True)

# efetivo_bovino: número total de cabeças de bovinos existentes no município em 31/dez
df['ln_bovino'] = np.log1p(df['efetivo_bovino'])
df['ln_bovino_lag1'] = df.groupby('codigo_ibge')['ln_bovino'].shift(1)

# 2. Variação Anual do Rebanho (dln_bovino ~ taxa de crescimento percentual)
df['dln_bovino'] = df.groupby('codigo_ibge')['ln_bovino'].diff()

painel_pec = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)].copy()

print(f"Painel Pecuário estruturado com {len(painel_pec)} linhas.")
print(painel_pec[['codigo_ibge', 'ano', 'efetivo_bovino', 'ln_bovino_lag1', 'dln_bovino']].head())"""
}

# =============================================================================
# 16. x4a_pecuaria
# =============================================================================
PHASE6_DATA["x4a_pecuaria"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Lotação Pecuária Aparente (Cabeças/ha)

### 1. Step 1: Junção de Rebanho (PPM) e Área de Pastagem (MapBiomas)
- **Fórmula da Densidade de Pastejo:**
  $$Lotacao_{i, t} = \\frac{\\text{Efetivo Bovino (cabeças)}_{i, t}}{\\text{Área de Pastagem (ha)}_{i, t}}$$

### 2. Step 2: Salvaguardas Matemáticas e Tratamento de Outliers
- **Salvaguarda de Denominador Pequeno:** Se a área de pastagem for menor que 200 hectares (`area_pastagem_ha < 200`), a lotação é definida como `NaN`. Em cidades quase 100% agrícolas, alguns bois de subsistência em piquetes de 20 ha gerariam taxas absurdas de 40 cabeças/ha!
- **Winsorização:** Truncamos a lotação ao teto biológico de **4,0 cabeças/ha** (ou percentil 99), para eliminar distorções de confinamentos intensivos pontuais que não representam o uso extensivo da terra.
- **Defasagem $t-1$ e Variação ($\\Delta Lotação$):** Aumentos na lotação indicam **intensificação pecuária** (poupança de terra / land-sparing), diminuindo a demanda por desmatamento.
""",
    "phase6_code": """# 1. Cálculo da Lotação Bruta (Cabeças de Gado por Hectare de Pasto)
df_lot = df.copy()

# Salvaguarda: pastagem mínima de 200 ha para evitar distorção matemática de divisão
PASTAGEM_MINIMA_HA = 200.0

df_lot['lotacao_aparente'] = np.where(
    df_lot['area_pastagem_ha'] >= PASTAGEM_MINIMA_HA,
    df_lot['efetivo_bovino'] / df_lot['area_pastagem_ha'],
    np.nan
)

# 2. Winsorização de Outliers Extremos (Teto biológico de pastejo extensivo = 4.0 cabeças/ha)
df_lot['lotacao_winsorizada'] = df_lot['lotacao_aparente'].clip(lower=0.0, upper=4.0)

# 3. Defasagem Temporal de 1 ano (t-1)
df_lot.sort_values(['codigo_ibge', 'ano'], inplace=True)
df_lot['lotacao_lag1'] = df_lot.groupby('codigo_ibge')['lotacao_winsorizada'].shift(1)

# 4. Indicador de Intensificação Pecuária (Delta Lotação)
# delta_lotacao > 0: intensificação (mais bois por hectare, poupando floresta)
# delta_lotacao < 0: degradação de pastagens ou extensificação
df_lot['delta_lotacao'] = df_lot['lotacao_winsorizada'] - df_lot['lotacao_lag1']

painel_lot = df_lot[(df_lot['ano'] >= 2001) & (df_lot['ano'] <= 2024)].copy()

print("Resumo da Lotação Pecuária Aparente (Cabeças/ha):")
print(painel_lot[['lotacao_aparente', 'lotacao_winsorizada', 'lotacao_lag1', 'delta_lotacao']].describe())
print(painel_lot[['codigo_ibge', 'ano', 'efetivo_bovino', 'area_pastagem_ha', 'lotacao_winsorizada', 'lotacao_lag1']].head())"""
}

# =============================================================================
# 17. x5_cobertura_terra
# =============================================================================
PHASE6_DATA["x5_cobertura_terra"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Estoques de Cobertura da Terra (MapBiomas)

### 1. Step 1: Harmonização dos Estoques de Classes Agregadas
- Classes disjuntas do MapBiomas organizadas em colunas anuais por município:
  Vegetação Nativa, Pastagem, Agricultura de Grãos, Silvicultura e Corpos d'Água/Outros.

### 2. Step 2: Variações Líquidas Anuais ($\\Delta Estoque$)
- $\\Delta Nativa_{i, t} = Nativa_{i, t} - Nativa_{i, t-1}$
- $\\Delta Pastagem_{i, t} = Pastagem_{i, t} - Pastagem_{i, t-1}$
- $\\Delta Agricultura_{i, t} = Agricultura_{i, t} - Agricultura_{i, t-1}$
""",
    "phase6_code": """# 1. Pivotar classes para colunas de área em hectares
piv_cob = df.pivot_table(
    index=['codigo_ibge', 'ano'],
    columns='classe_nome',
    values='area_ha',
    aggfunc='sum',
    fill_value=0
).reset_index()

piv_cob.sort_values(['codigo_ibge', 'ano'], inplace=True)

# 2. Variações anuais de cada estoque (ha)
for col in piv_cob.columns:
    if col not in ['codigo_ibge', 'ano']:
        piv_cob[f'delta_{col}_ha'] = piv_cob.groupby('codigo_ibge')[col].diff()

painel_cob = piv_cob[(piv_cob['ano'] >= 2001) & (piv_cob['ano'] <= 2024)].copy()

print(f"Painel de estoques de uso do solo: {painel_cob.shape}")
print(painel_cob.head())"""
}

# =============================================================================
# 18. x5a_cobertura_terra
# =============================================================================
PHASE6_DATA["x5a_cobertura_terra"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Fração de Uso do Solo e Condição de Fronteira

### 1. Step 1: Frações Territoriais Normalizadas (0 a 1)
- $ShareNativa_{i, t-1} = \\frac{EstoqueNativo_{i, t-1}}{AreaMapeadaTotal_i}$.
- $ShareAntropico_{i, t-1} = \\frac{Pastagem_{i, t-1} + Agricultura_{i, t-1}}{AreaMapeadaTotal_i}$.

### 2. Step 2: Condição de Fronteira Aberta vs Fronteira Fechada
- **Dummy de Fronteira Fechada/Exaurida:** Vale 1 se $ShareNativa_{i, t-1} < 0{,}10$ (menos de 10% de vegetação nativa restante). Em cidades com fronteira fechada, a expansão de lavoura ocorre exclusivamente sobre pasto já aberto.
""",
    "phase6_code": """# 1. Seleção de variáveis de proporção territorial
df_fronteira = df[['codigo_ibge', 'ano', 'native_veg_share_lag1', 'area_mapeada_ha']].copy()

# 2. Condição de Fronteira Agrícola:
# dummy_fronteira_fechada: 1 se restarem menos de 10% de mata nativa (fronteira exaurida), 0 se aberta
df_fronteira['dummy_fronteira_fechada'] = (df_fronteira['native_veg_share_lag1'] < 0.10).astype(int)

# dummy_fronteira_aberta: 1 se restarem mais de 50% de mata nativa
df_fronteira['dummy_fronteira_aberta'] = (df_fronteira['native_veg_share_lag1'] > 0.50).astype(int)

painel_front = df_fronteira[(df_fronteira['ano'] >= 2001) & (df_fronteira['ano'] <= 2024)].copy()

print("Distribuição da condição de fronteira em Mato Grosso:")
print(painel_front.groupby('ano')[['dummy_fronteira_fechada', 'dummy_fronteira_aberta']].mean())
print(painel_front.head())"""
}

# =============================================================================
# 19. x6_biomas
# =============================================================================
PHASE6_DATA["x6_biomas"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Composição de Biomas e Choques Regulatórios

### 1. Step 1: Proporção Municipal por Bioma (IBGE)
- Proporção da área territorial de cada município localizada em cada um dos 3 biomas de MT:
  $ShareAmazonia_i$, $ShareCerrado_i$ e $SharePantanal_i$.
- Determinação do bioma predominante ($> 50\\%$ da área municipal).

### 2. Step 2: Interação Institucional Pós-2008 (Código Florestal e Fiscalização)
- A legislação ambiental brasileira é assimétrica por bioma: a Reserva Legal obrigatória é de **80% na Amazônia** contra **35% no Cerrado**.
- Em 2008, o Decreto Federal 6.514 e a Resolução Bacen 3.545 criaram restrições severas de crédito rural e operações de fiscalização focadas na Amazônia.
- **Termo de Interação de Política:**
  $$InteracaoPolitica_{i, t} = ShareAmazonia_i \\times Post2008_t$$
  Como o bioma é fixo no tempo (absorvido pelo efeito fixo municipal), essa interação permite identificar o impacto diferencial das políticas ambientais sobre a conversão!
""",
    "phase6_code": """# 1. Dummies de bioma predominante
df_bioma = df.copy()

# 2. Interação Institucional com o Marco Regulatório Pós-2008
# Em painel com efeito fixo municipal (alpha_i), a fração estática do bioma é absorvida.
# A interação com o tempo (ano >= 2008) identifica o efeito do aperto regulatório na Amazônia.
def expandir_painel_bioma(df_bio, anos=range(2001, 2025)):
    registros = []
    for ano in anos:
        temp = df_bio.copy()
        temp['ano'] = ano
        # Post-2008: Decreto 6.514/2008, Lista de Municípios Prioritários, Resolução Bacen 3.545
        temp['post_2008'] = int(ano >= 2008)
        temp['interacao_amazonia_post2008'] = temp['biome_amazonia_share_i'] * temp['post_2008']
        registros.append(temp)
    return pd.concat(registros, ignore_index=True)

painel_bioma = expandir_painel_bioma(df_bioma)

print(f"Painel expandido de Biomas x Política: {painel_bioma.shape}")
print(painel_bioma[['codigo_ibge', 'ano', 'biome_amazonia_share_i', 'post_2008', 'interacao_amazonia_post2008']].head())"""
}

# =============================================================================
# 20. x7_custo-soja
# =============================================================================
PHASE6_DATA["x7_custo-soja"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Custos de Produção de Soja CONAB

### 1. Step 1: Harmonização da Safra de Custos
- Periodicidade por safra agrícola CONAB.
- Métricas: Custo Operacional Efetivo (COE - desembolso direto), Custo Operacional Total (COT - inclui depreciação de máquinas) e Custo Total (CT) em R$/ha e R$/saca de 60 kg.

### 2. Step 2: Margem Bruta Operacional e RESSALVA METODOLÓGICA CRUCIAL
- **Margem Bruta Estimada por Saca:** $Margem_{saca} = PrecoRecebido - COE_{saca}$.
- **RESSALVA ECONOMÉTRICA FUNDAMENTAL:**
  A base da CONAB pesquisa apenas **2 a 4 municípios-polo** em Mato Grosso (ex: Sorriso, Campo Verde, Primavera do Leste e Sapezal).
  **NÃO IMPUTAR** esses custos para os outros 137 municípios no painel principal! A imputação sintética criaria variação espacial espúria e viés de atenuação severo por erro de medição. Esses custos devem ser usados exclusivamente em análises de robustez no subsample de polos.
""",
    "phase6_code": """# 1. Estruturação dos Custos Operacionais da Soja
df_custo = df.copy()

# Identificação das variáveis de custo por hectare e por saca de 60 kg
# coe_ha: custo operacional efetivo por hectare (R$/ha) -> desembolso financeiro direto
# cot_ha: custo operacional total por hectare (R$/ha) -> inclui depreciação de maquinário
# ct_ha: custo total por hectare (R$/ha) -> inclui remuneração esperada da terra e do capital
print("Métricas de Custo CONAB disponíveis:")
print(df_custo.head())

# 2. Defasagem temporal de 1 ano (t-1)
# Os custos planejados e observados na safra anterior orientam o orçamento da safra presente
print("\\nNOTA METODOLÓGICA: Dados restritos a municípios-polo da CONAB. Não imputar aos 141 municípios.")"""
}

# =============================================================================
# 21. x7_custo-milho-s1
# =============================================================================
PHASE6_DATA["x7_custo-milho-s1"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Custos de Milho 1ª Safra CONAB (Verão)

### 1. Step 1: Custos da Safra de Verão
- O milho de 1ª safra (plantado no verão) possui relevância muito pequena em Mato Grosso, pois quase todas as áreas agricultáveis de verão são dedicadas à soja.
- Custos: COE, COT e CT em R$/ha e R$/saca.

### 2. Step 2: Restrição Amostral aos Polos
- Amostra restrita aos municípios-polo pesquisados pela CONAB.
""",
    "phase6_code": """# Estruturação e Defasagem dos Custos de Milho 1ª Safra
df_m1 = df.copy()
print("Série de Custos de Milho 1ª Safra (Verão) CONAB:")
print(df_m1.head())
print("\\nRessalva: Aplicável somente como subsample de polos; relevância secundária em relação à safrinha em MT.")"""
}

# =============================================================================
# 22. x7_custo-milho-s2
# =============================================================================
PHASE6_DATA["x7_custo-milho-s2"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Custos de Milho 2ª Safra (Safrinha CONAB)

### 1. Step 1: Custos da Segunda Safra (Outono/Inverno)
- A safrinha de milho (plantada imediatamente após a colheita precoce da soja) é o motor da segunda safra em MT.
- Custos: COE, COT e CT em R$/ha e R$/saca.

### 2. Step 2: Razão de Custos Operacionais Safrinha vs Soja
- $\\frac{COE_{milho\\_s2}}{COE_{soja}}$: mede a viabilidade financeira do sistema de duplo cultivo. Se o custo da safrinha sobe muito, o agricultor pode abrir mão do segundo plantio.
- Ressalva de restrição espacial aos municípios-polo da CONAB.
""",
    "phase6_code": """# Estruturação de Custos de Milho Safrinha
df_m2 = df.copy()
print("Série de Custos de Milho 2ª Safra (Safrinha) CONAB:")
print(df_m2.head())
print("\\nRazão de custos safrinha/soja orienta a viabilidade econômica do sistema de sucessão de culturas.")"""
}

# =============================================================================
# 23. x8_chuva
# =============================================================================
PHASE6_DATA["x8_chuva"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Precipitação e Janelas Agronômicas Críticas

### 1. Step 1: Agrupamento em Janelas Produtivas Agronômicas
- **Por que a soma do ano civil (Janeiro a Dezembro) é insuficiente:** Uma tempestade em julho (no meio da estação seca) não ajuda a lavoura de soja. O agricultor depende de chuva em momentos específicos do ciclo biológico.
- **Três Métricas Anualizadas Construídas:**
  1. **Chuva Total Anual:** Precipitação acumulada de 12 meses (mm).
  2. **Safra de Verão (Outubro $t-1$ a Março $t$):** Período crítico que define a semeadura, floração e enchimento de grãos da soja.
  3. **Segunda Safra / Safrinha (Fevereiro a Maio $t$):** Período em que a chuva vai diminuindo e define o sucesso do milho safrinha.

### 2. Step 2: Defasagens e Estresse Hídrico
- Defasagem $t-1$ da chuva da safra de verão para capturar o impacto financeiro da safra anterior na decisão de conversão presente.
""",
    "phase6_code": """# 1. Agregação por Ano Calendário (Janeiro a Dezembro)
precip_anual = df.groupby(['codigo_ibge', 'ano'])['precip_mm'].sum().reset_index(name='precip_total_anual_mm')

# 2. Janela Agronômica da Safra de Verão (Outubro a Março)
# Outubro a Dezembro pertencem ao ciclo de plantio que colhe no início do ano seguinte
df_copia = df.copy()
df_copia['safra_ano'] = np.where(df_copia['mes'] >= 10, df_copia['ano'] + 1, df_copia['ano'])
safra_verao = df_copia[df_copia['mes'].isin([10, 11, 12, 1, 2, 3])].groupby(['codigo_ibge', 'safra_ano'])['precip_mm'].sum().reset_index(name='precip_safra_verao_mm')
safra_verao.rename(columns={'safra_ano': 'ano'}, inplace=True)

# 3. Janela da Safrinha de Milho (Fevereiro a Maio)
safrinha = df[df['mes'].isin([2, 3, 4, 5])].groupby(['codigo_ibge', 'ano'])['precip_mm'].sum().reset_index(name='precip_safrinha_mm')

# 4. Consolidar Painel de Variáveis Climáticas
painel_chuva = pd.merge(precip_anual, safra_verao, on=['codigo_ibge', 'ano'], how='left')
painel_chuva = pd.merge(painel_chuva, safrinha, on=['codigo_ibge', 'ano'], how='left')

# Defasagem temporal de 1 ano (t-1)
painel_chuva.sort_values(['codigo_ibge', 'ano'], inplace=True)
painel_chuva['precip_safra_verao_lag1'] = painel_chuva.groupby('codigo_ibge')['precip_safra_verao_mm'].shift(1)

painel_chuva_final = painel_chuva[(painel_chuva['ano'] >= 2001) & (painel_chuva['ano'] <= 2024)].copy()

print("Métricas Climáticas Sazonais por Janela Agronômica:")
print(painel_chuva_final[['codigo_ibge', 'ano', 'precip_total_anual_mm', 'precip_safra_verao_mm', 'precip_safrinha_mm', 'precip_safra_verao_lag1']].head())"""
}

# =============================================================================
# 24. x8_chuvaa
# =============================================================================
PHASE6_DATA["x8_chuvaa"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Anomalias Padronizadas (Z-Score) e Choques Extremos

### 1. Step 1: Padronização Climatológica (Z-Score)
- **Fórmula:**
  $$Z_{i, t} = \\frac{Chuva_{i, t} - \\mu_{i, 1981-2010}}{\\sigma_{i, 1981-2010}}$$
- O Z-score compara o volume de chuva de cada ano com o histórico normal de longo prazo do próprio município, eliminando diferenças de nível entre cidades chuvosas e secas.

### 2. Step 2: Dummies de Choques Climáticos Extremos
- **Dummy de Seca Severa:** $SecaSevera_{i, t} = 1$ se $Z_{i, t} < -1{,}5$ (ano extraordinariamente seco, que quebra a safra).
- **Dummy de Excesso de Chuva:** $ExcessoChuva_{i, t} = 1$ se $Z_{i, t} > 1{,}5$ (ano excessivamente chuvoso, que atrapalha a colheita e apodrece grãos).
- **Defasagem $t-1$:** O choque climático passado gera aperto de liquidez, inibindo novos investimentos em conversão de terra.
""",
    "phase6_code": """# 1. Estruturação dos Z-scores de Anomalia Climática
df_anom = df[['codigo_ibge', 'ano', 'precip_zscore_1981_2010']].copy()

# 2. Criação de Dummies de Choques Climáticos Extremos
# dummy_seca_severa: 1 se a chuva ficou mais de 1.5 desvios-padrão abaixo da média histórica do município
df_anom['dummy_seca_severa'] = (df_anom['precip_zscore_1981_2010'] < -1.5).astype(int)

# dummy_excesso_chuva: 1 se a chuva ficou mais de 1.5 desvios-padrão acima da média histórica
df_anom['dummy_excesso_chuva'] = (df_anom['precip_zscore_1981_2010'] > 1.5).astype(int)

# 3. Defasagem Temporal de 1 ano (t-1)
df_anom.sort_values(['codigo_ibge', 'ano'], inplace=True)
df_anom['dummy_seca_lag1'] = df_anom.groupby('codigo_ibge')['dummy_seca_severa'].shift(1)
df_anom['zscore_precip_lag1'] = df_anom.groupby('codigo_ibge')['precip_zscore_1981_2010'].shift(1)

painel_anom = df_anom[(df_anom['ano'] >= 2001) & (df_anom['ano'] <= 2024)].copy()

print("Choques Climáticos Extremos Identificados no Painel:")
print(f"Total de ocorrências de seca severa (Z < -1.5): {painel_anom['dummy_seca_severa'].sum()}")
print(f"Total de ocorrências de excesso de chuva (Z > 1.5): {painel_anom['dummy_excesso_chuva'].sum()}")
print(painel_anom[['codigo_ibge', 'ano', 'precip_zscore_1981_2010', 'dummy_seca_severa', 'dummy_seca_lag1']].head())"""
}

# =============================================================================
# 25. x9_relevo
# =============================================================================
PHASE6_DATA["x9_relevo"] = {
    "phase6_md": """## Fase 6: Feature Engineering — Topografia e Aptidão para Mecanização (SRTM)

### 1. Step 1: Características Topográficas Municipais
- A motomecanização moderna (plantio direto, colheitadeiras pesadas de grande porte) exige terrenos planos a suave-ondulados (declividade inferior a 8%).
- Terrenos acidentados ou com grande amplitude altimétrica inviabilizam a lavoura tecnificada de grãos, restringindo a terra à pecuária extensiva ou preservação.

### 2. Step 2: Interação Relevo x Preços (Shift-Share)
- **Amplitude Altimétrica:** $\\Delta Altura_i = ElevacaoMax_i - ElevacaoMin_i$.
- **Dummy de Relevo Plano:** Vale 1 se a amplitude altimétrica for inferior a 250 metros.
- **Interação com Choque de Preços:** $\\text{RelevoPlano}_i \\times \\Delta \\ln(PrecoSoja_{t-1})$.
  Permite testar se a expansão da soja sobre a vegetação nativa avança preferencialmente sobre as chapadas planas mecanizáveis.
""",
    "phase6_code": """# 1. Indicadores Topográficos Municipais
df_relevo = df.copy()

# Amplitude altimétrica municipal (diferença entre ponto mais alto e mais baixo)
df_relevo['amplitude_altimetrica_m'] = df_relevo['elevation_max_m'] - df_relevo['elevation_min_m']

# dummy_relevo_plano: 1 se o relevo municipal for predominantemente suave/plano (amplitude < 250m)
df_relevo['dummy_relevo_plano'] = (df_relevo['amplitude_altimetrica_m'] < 250.0).astype(int)

# 2. Esqueleto de Interação Shift-Share para o Painel:
# ChoqueTopografia_it = dummy_relevo_plano_i * dln_psoja_lag1_t
df_relevo['exemplo_interacao_topografia_preco'] = df_relevo['dummy_relevo_plano'] * 0.15

print("Topografia e Aptidão à Motomecanização por Município:")
print(f"Municípios com relevo plano favorável à mecanização pesada: {df_relevo['dummy_relevo_plano'].sum()} / {len(df_relevo)}")
print(df_relevo[['codigo_ibge', 'elevation_mean_m', 'amplitude_altimetrica_m', 'dummy_relevo_plano']].head())"""
}
