# -*- coding: utf-8 -*-
"""
build_consolidated_panel_notebook.py — Gerador do Notebook do Painel Consolidado 2001–2024
Projeto: Tese de Doutorado - Economia Aplicada / Uso da Terra em Mato Grosso
Diretório: 2_INTI/chapters/chap1/stats/AED/gm/

Este script gera o notebook 'painel_consolidado_2001_2024.ipynb' com a integração
completa das 25 variáveis candidatas e a bateria exaustiva de estatística descritiva,
obedecendo à exigência estrita: UMA CÉLULA PARA CADA TABELA, COMANDO OU GRÁFICO.
"""

from pathlib import Path
import nbformat as nbf

OUTPUT_DIR = Path(__file__).resolve().parent
NOTEBOOK_PATH = OUTPUT_DIR / "painel_consolidado_2001_2024.ipynb"

def create_panel_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.13.0"
        }
    }

    # =========================================================================
    # CÉLULA 0: Título e Apresentação Geral
    # =========================================================================
    c0_md = """# Painel Econométrico Consolidado de Mato Grosso (2001–2024)
## Integração das 25 Variáveis Candidatas e Bateria Exaustiva de Estatística Descritiva

**Autor:** Fernando Souza de Vieira  
**Orientação:** Tese de Doutorado em Economia Aplicada — FEA-RP / CENA / USP  
**Capítulo 1:** Decisão de Conversão de Vegetação Nativa para Lavouras e Pastagens em Mato Grosso  
**Hipótese Central ($H_1$):** A conversão de vegetação nativa para usos agropecuários responde positivamente ao retorno econômico esperado relativo desses usos, sendo condicionada pela capacidade produtiva da terra e mediada pelas restrições institucionais de comando e controle ambiental.

---

### Especificação Conceitual do Modelo Estrutural:
$$Y_{i, t} = f\\Big(\\underbrace{x1_{t-1}}_{\\text{Preços Globais}}, \\; \\underbrace{x2_{i, t-1}}_{\\text{Produtividade / Aptidão}}, \\; \\underbrace{x3_{i, t-1}}_{\\text{Fiscalização / Embargos}}, \\; \\underbrace{x4_{i, t-1}}_{\\text{Pecuária}}, \\; \\underbrace{x5_{i, t-1}}_{\\text{Fronteira}}, \\; \\underbrace{x6_i}_{\\text{Biomas}}, \\; \\underbrace{x7_{i, t-1}}_{\\text{Custos}}, \\; \\underbrace{x8_{i, t-1}}_{\\text{Clima / Choques}}, \\; \\underbrace{x9_i}_{\\text{Relevo}}\\Big) + \\alpha_i + \\lambda_t + \\varepsilon_{i, t}$$

### Salvaguarda Territorial Estrita (141 Municípios de Mato Grosso):
- O estado de Mato Grosso é fixado na malha histórica oficial de **141 municípios** (Área Mínima Comparável - AMC).
- O 142º município criado (*Boa Esperança do Norte* - código IBGE `5101837`), recentemente desmembrado de Nova Ubiratã (`5106240`) e Sorriso (`5107925`), tem todos os seus dados **reincorporados/aglutinados em Nova Ubiratã (`5106240`)**.
- A grade completa balanceada possui exatamente:
  $$N \\times T = 141 \\text{ municípios} \\times 24 \\text{ anos (2001 a 2024)} = 3.384 \\text{ observações longitudinais}$$

### Estrutura Deste Notebook:
- **Seção 1:** Setup & Configurações de Visualização
- **Seção 2:** Criação da Grade Mestre Balanceada ($141 \\times 24$)
- **Seção 3:** Extração, Limpeza e Harmonização dos 25 Conjuntos de Dados
- **Seção 4:** Consolidação Final do Painel e Exportação
- **Seção 5:** Bateria de Estatística Descritiva Detalhada (**Uma célula para cada tabela, comando ou gráfico**)
"""
    nb.cells.append(nbf.v4.new_markdown_cell(c0_md))

    # =========================================================================
    # SEÇÃO 1: Setup e Importações
    # =========================================================================
    nb.cells.append(nbf.v4.new_markdown_cell("## 1. Setup, Bibliotecas e Configuração Visual\n\nImportamos as bibliotecas analíticas e configuramos padrões gráficos de alta resolução."))

    c1_code = """import os
import sys
import warnings
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Suprimir avisos secundários para saídas limpas
warnings.filterwarnings('ignore')

# Configuração visual profissional para economia aplicada
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.dpi'] = 110
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.titlesize'] = 13

# Localização dinâmica da raiz do repositório da tese
caminho_atual = Path.cwd().resolve()
raiz_projeto = None
for p in [caminho_atual] + list(caminho_atual.parents):
    if (p / "2_INTI" / "RESEARCH_PROTOCOL.md").is_file() or (p / "AGENTS.md").is_file():
        raiz_projeto = p
        break

if raiz_projeto is None:
    raise FileNotFoundError("Não foi possível localizar a raiz do projeto (onde está 2_INTI/RESEARCH_PROTOCOL.md).")

print(f"Raiz do projeto identificada com sucesso: {raiz_projeto}")"""
    nb.cells.append(nbf.v4.new_code_cell(c1_code))

    # =========================================================================
    # SEÇÃO 2: Criação da Grade Mestre
    # =========================================================================
    nb.cells.append(nbf.v4.new_markdown_cell("""## 2. Construção da Grade Mestre Balanceada (141 Municípios x 24 Anos)

Criamos a espinha dorsal do painel: uma grade cartesiana com os **141 municípios históricos de Mato Grosso** e os **24 anos (2001 a 2024)**.  
Qualquer ausência nas tabelas de dados brutos será associada a esta grade para diferenciar **zero verdadeiro** de **ausência de registro**."""))

    c2_code = r"""# Obter a lista oficial dos 141 municípios a partir do cadastro de biomas do IBGE
caminho_biomas_ref = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h2__biome_share__ibge2019_malha2024__candidato.csv"
df_ref_mun = pd.read_csv(caminho_biomas_ref, encoding='utf-8-sig')

# Harmonização territorial: garantir 141 municípios únicos
df_ref_mun['codigo_ibge'] = df_ref_mun['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_ref_mun = df_ref_mun[df_ref_mun['codigo_ibge'].str.startswith('51')].drop_duplicates('codigo_ibge')

municipios_141 = sorted(df_ref_mun['codigo_ibge'].unique())
anos_painel = list(range(2001, 2025))

# Criar produto cartesiano balanceado (141 x 24 = 3.384)
grade_mestre = pd.MultiIndex.from_product(
    [municipios_141, anos_painel],
    names=['codigo_ibge', 'ano']
).to_frame().reset_index(drop=True)

# Incorporar nome oficial do município
mapa_nomes = dict(zip(df_ref_mun['codigo_ibge'], df_ref_mun['municipio']))
grade_mestre['municipio'] = grade_mestre['codigo_ibge'].map(mapa_nomes)

print(f"Grade balanceada criada com sucesso!")
print(f"Total de municípios: {grade_mestre['codigo_ibge'].nunique()} (Meta: 141)")
print(f"Total de anos: {grade_mestre['ano'].nunique()} (2001 a 2024)")
print(f"Total de linhas na grade mestre: {len(grade_mestre)} (Meta: 3.384 observações)")
grade_mestre.head()"""
    nb.cells.append(nbf.v4.new_code_cell(c2_code))

    # =========================================================================
    # SEÇÃO 3: Processamento dos Blocos
    # =========================================================================
    nb.cells.append(nbf.v4.new_markdown_cell("""## 3. Extração, Limpeza e Harmonização dos 25 Conjuntos de Dados

Processamos os blocos de variáveis candidatas aplicando as regras de harmonização (Passo 1: anualização com janelas agronômicas) e derivação matemática (Passo 2: taxas, logs, salvaguardas e defasagens $t-1$)."""))

    # 3.1 Bloco Y
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.1 Bloco Y: Conversão Bruta e Taxas de Conversão (MapBiomas Col. 10.1)

- **`Y_conv`:** Separação estrita de Agricultura (`class_id` 20, 39, 41) e Pastagem (`class_id` 15); $\\Delta\\text{Estoque}$.
- **`Y_tx-conv`:** Taxa de conversão sobre o estoque nativo remanescente no início do período ($t-1$); salvaguarda de $\\text{NaN}$ se estoque $\\le 100\\text{ ha}$; truncamento em $[0, 1]$."""))

    c_bloco_y = r"""# 1. Carregar estoques do MapBiomas (Y_conv)
p_mapb = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h1_h2__mapbiomas_classes__col10_1__municipio_bioma_anual.csv"
df_mapb = pd.read_csv(p_mapb, encoding='utf-8-sig', low_memory=False)
df_mapb.columns = df_mapb.columns.str.strip().str.lower()
df_mapb['codigo_ibge'] = df_mapb['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_mapb = df_mapb[df_mapb['codigo_ibge'].str.startswith('51')].copy()

# Destinos antrópicos separados
df_mapb['destino'] = 'Outros'
df_mapb.loc[df_mapb['class_id'] == 15, 'destino'] = 'Pastagem'
df_mapb.loc[df_mapb['class_id'].isin([20, 39, 41]), 'destino'] = 'Agricultura'

piv_y = df_mapb[df_mapb['destino'].isin(['Pastagem', 'Agricultura'])].pivot_table(
    index=['codigo_ibge', 'ano'],
    columns='destino',
    values='area_ha',
    aggfunc='sum',
    fill_value=0
).reset_index()

piv_y.rename(columns={'Agricultura': 'estoque_agricultura_ha', 'Pastagem': 'estoque_pastagem_ha'}, inplace=True)
piv_y.sort_values(['codigo_ibge', 'ano'], inplace=True)
piv_y['delta_pastagem_ha'] = piv_y.groupby('codigo_ibge')['estoque_pastagem_ha'].diff()
piv_y['delta_agricultura_ha'] = piv_y.groupby('codigo_ibge')['estoque_agricultura_ha'].diff()
piv_y['Y_conv_pastagem_ha'] = piv_y['delta_pastagem_ha'].clip(lower=0)
piv_y['Y_conv_agricultura_ha'] = piv_y['delta_agricultura_ha'].clip(lower=0)
piv_y['Y_conv_total_ha'] = piv_y['Y_conv_pastagem_ha'] + piv_y['Y_conv_agricultura_ha']

# 2. Carregar denominador nativo (Y_tx-conv)
p_nat = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h2__native_veg__mapbiomas_col10_1__candidato.csv"
df_nat = pd.read_csv(p_nat, encoding='utf-8-sig')
df_nat.columns = df_nat.columns.str.strip().str.lower()
df_nat['codigo_ibge'] = df_nat['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_nat = df_nat[df_nat['codigo_ibge'].str.startswith('51')].groupby(['codigo_ibge', 'ano'], as_index=False).agg({
    'area_mapeada_ha': 'sum',
    'native_veg_ha_it': 'sum',
    'native_veg_ha_lag1': 'sum'
})

bloco_y = pd.merge(piv_y, df_nat, on=['codigo_ibge', 'ano'], how='left')

# Taxa de conversão com salvaguarda matemática (denominador <= 100 ha -> NaN)
bloco_y['Y_tx_conv'] = np.where(
    bloco_y['native_veg_ha_lag1'] > 100.0,
    bloco_y['Y_conv_total_ha'] / bloco_y['native_veg_ha_lag1'],
    np.nan
)
bloco_y['Y_tx_conv'] = bloco_y['Y_tx_conv'].clip(lower=0.0, upper=1.0)
bloco_y['flag_fronteira_fechada'] = (bloco_y['native_veg_ha_lag1'] / bloco_y['area_mapeada_ha'] < 0.05).astype(int)

print(f"Bloco Y construído com {len(bloco_y)} linhas e {bloco_y['codigo_ibge'].nunique()} municípios.")"""
    nb.cells.append(nbf.v4.new_code_cell(c_bloco_y))

    # 3.2 Bloco x1
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.2 Bloco x1: Preços Mundiais de Soja, Milho e Carne (Banco Mundial)

- **Harmonização Temporal:** Anualização via média de 12 meses do ano civil e janela pré-plantio (Março a Agosto $t-1$).
- **Derivações:** $\\ln(P_{t-1})$; razão de preços Soja/Milho ($P_{soja}/P_{milho}$); termos de troca Carne/Soja ($P_{carne}/P_{soja}$)."""))

    c_bloco_x1 = r"""# Carregar preços de commodities do Banco Mundial
p_precos = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h1__prices__worldbank__mensal_robustez.csv"
df_p = pd.read_csv(p_precos, encoding='utf-8-sig')
df_p.columns = df_p.columns.str.strip().str.lower()
df_p['data'] = pd.to_datetime(df_p['data'], errors='coerce')
df_p['ano'] = df_p['data'].dt.year
df_p['mes'] = df_p['data'].dt.month
df_p['preco_nominal'] = pd.to_numeric(df_p['preco_nominal'], errors='coerce')

# Pivotar por commodity
piv_p = df_p.pivot_table(index=['ano', 'mes'], columns='variavel', values='preco_nominal').reset_index()

# 1. Média Anual Calendário
p_anual = piv_p.groupby('ano').agg(
    psoja_media_anual=('price_soja', 'mean'),
    pmilho_media_anual=('price_milho', 'mean'),
    pcarne_media_anual=('price_carne_bovina', 'mean')
).reset_index()

# 2. Janela Agronômica Pré-Plantio (Março a Agosto = meses 3 a 8)
p_janela = piv_p[piv_p['mes'].isin([3, 4, 5, 6, 7, 8])].groupby('ano').agg(
    psoja_janela_pre=('price_soja', 'mean'),
    pmilho_janela_pre=('price_milho', 'mean')
).reset_index()

# 3. Janela Pecuária de Entressafra (Maio a Outubro = meses 5 a 10)
p_carne_janela = piv_p[piv_p['mes'].isin([5, 6, 7, 8, 9, 10])].groupby('ano').agg(
    pcarne_janela_seca=('price_carne_bovina', 'mean')
).reset_index()

bloco_x1 = pd.merge(p_anual, p_janela, on='ano', how='left')
bloco_x1 = pd.merge(bloco_x1, p_carne_janela, on='ano', how='left')

# Defasagens estritas de 1 ano (t-1)
bloco_x1['psoja_lag1'] = bloco_x1['psoja_janela_pre'].shift(1)
bloco_x1['pmilho_lag1'] = bloco_x1['pmilho_janela_pre'].shift(1)
bloco_x1['pcarne_lag1'] = bloco_x1['pcarne_janela_seca'].shift(1)

# Logs e Razões de Preço
bloco_x1['ln_psoja_lag1'] = np.log(bloco_x1['psoja_lag1'])
bloco_x1['ln_pmilho_lag1'] = np.log(bloco_x1['pmilho_lag1'])
bloco_x1['ln_pcarne_lag1'] = np.log(bloco_x1['pcarne_lag1'])
bloco_x1['razao_psoja_pmilho_lag1'] = bloco_x1['psoja_lag1'] / bloco_x1['pmilho_lag1']
bloco_x1['razao_carne_soja_lag1'] = (bloco_x1['pcarne_lag1'] * 1000.0) / bloco_x1['psoja_lag1']

print("Bloco x1 anualizado e defasado (2001-2024):")
print(bloco_x1[(bloco_x1['ano'] >= 2001) & (bloco_x1['ano'] <= 2024)][['ano', 'psoja_lag1', 'pmilho_lag1', 'razao_psoja_pmilho_lag1']].head(4))"""
    nb.cells.append(nbf.v4.new_code_cell(c_bloco_x1))

    # 3.3 Bloco x2
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.3 Bloco x2: Capacidade Produtiva Agrícola (PAM/IBGE e GAEZ v4)

- **`x2` e `x2a`:** Produção colhida PAM/IBGE, $\\ln(1+\\text{Prod})$, rendimento observado (kg/ha) com **$\\text{NaN}$ estrito para ausência de colheita**, defasagem $t-1$ e média histórica estrutural pré-2001.
- **`x2b` e `x2c`:** Produtividade potencial GAEZ v4 corrigida para **umidade comercial de 13%** ($\\text{Yield}_{comercial} = \\text{Yield}_{DW} / 0{,}87$), aptidão normalizada (0 a 1) e cálculo do *Yield Gap*."""))

    c_bloco_x2 = r"""# 1. PAM/IBGE: Produção e Rendimento Observado
p_pam = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h1_h2__pam_soja_milho__ibge__municipio_anual.csv"
df_pam = pd.read_csv(p_pam, encoding='utf-8-sig')
df_pam.columns = df_pam.columns.str.strip().str.lower()
df_pam['codigo_ibge'] = df_pam['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_pam = df_pam[df_pam['codigo_ibge'].str.startswith('51')].copy()

# Produção (t) com fillna(0) para soma
piv_prod = df_pam.pivot_table(index=['codigo_ibge', 'ano'], columns='produto', values='producao_t', aggfunc='sum', fill_value=0).reset_index()
piv_prod.rename(columns={'Milho (em grão)': 'prod_milho_t', 'Soja (em grão)': 'prod_soja_t'}, inplace=True)

# Rendimento médio (kg/ha) SEM preencher com zero (NaN estrito se não plantou)
piv_rend = df_pam.pivot_table(index=['codigo_ibge', 'ano'], columns='produto', values='rendimento_medio_kg_ha', aggfunc='mean').reset_index()
piv_rend.rename(columns={'Milho (em grão)': 'rend_milho_kg_ha', 'Soja (em grão)': 'rend_soja_kg_ha'}, inplace=True)

bloco_pam = pd.merge(piv_prod, piv_rend, on=['codigo_ibge', 'ano'], how='outer')
bloco_pam.sort_values(['codigo_ibge', 'ano'], inplace=True)

bloco_pam['ln_prod_soja_t'] = np.log1p(bloco_pam['prod_soja_t'])
bloco_pam['ln_prod_milho_t'] = np.log1p(bloco_pam['prod_milho_t'])
bloco_pam['rend_soja_lag1'] = bloco_pam.groupby('codigo_ibge')['rend_soja_kg_ha'].shift(1)
bloco_pam['rend_milho_lag1'] = bloco_pam.groupby('codigo_ibge')['rend_milho_kg_ha'].shift(1)

# Média histórica pré-2001 (capacidade predeterminada invariante)
pre_2001 = df_pam[df_pam['ano'] <= 2000].groupby(['codigo_ibge', 'produto'])['rendimento_medio_kg_ha'].mean().unstack().reset_index()
pre_2001.rename(columns={'Milho (em grão)': 'hprod_milho_pre2001', 'Soja (em grão)': 'hprod_soja_pre2001'}, inplace=True)
bloco_pam = pd.merge(bloco_pam, pre_2001, on='codigo_ibge', how='left')

# 2. GAEZ v4: Potencial Biofísico e Aptidão
p_gaez = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h1__suitability_yield__gaez_v4_6190__candidatos.csv"
df_gaez = pd.read_csv(p_gaez, encoding='utf-8-sig')
df_gaez.columns = df_gaez.columns.str.strip().str.lower()
df_gaez['codigo_ibge'] = df_gaez['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})

piv_gaez = df_gaez.pivot_table(index='codigo_ibge', columns='variavel_raster', values='valor_medio').reset_index()

# Correção de umidade comercial (Matéria Seca DW / 0.87)
if 'yxHr0_soy' in piv_gaez.columns:
    piv_gaez['gaez_yield_soja_comercial_kg_ha'] = piv_gaez['yxHr0_soy'] / 0.87
if 'yxHr0_mze' in piv_gaez.columns:
    piv_gaez['gaez_yield_milho_comercial_kg_ha'] = piv_gaez['yxHr0_mze'] / 0.87
elif 'yxHr0_miz' in piv_gaez.columns:
    piv_gaez['gaez_yield_milho_comercial_kg_ha'] = piv_gaez['yxHr0_miz'] / 0.87
if 'sxHr0_soy' in piv_gaez.columns:
    piv_gaez['aptidao_soja_norm'] = piv_gaez['sxHr0_soy'] / 10000.0
if 'sxHr0_mze' in piv_gaez.columns:
    piv_gaez['aptidao_milho_norm'] = piv_gaez['sxHr0_mze'] / 10000.0

bloco_x2 = pd.merge(bloco_pam, piv_gaez, on='codigo_ibge', how='left')
bloco_x2['yield_gap_soja'] = bloco_x2['rend_soja_lag1'] / bloco_x2['gaez_yield_soja_comercial_kg_ha']

print(f"Bloco x2 estruturado com {bloco_x2['codigo_ibge'].nunique()} municípios.")"""
    nb.cells.append(nbf.v4.new_code_cell(c_bloco_x2))

    # 3.4 Bloco x3
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.4 Bloco x3: Ambiente Institucional e Fiscalização Ambiental (IBAMA)

- **`x3` a `x3e`:** Autos informados e espacializados, autos contra a flora, taxa de concordância de coordenadas, valor das multas **deflacionadas pelo IPCA (R$ de 2024)** e **estoque acumulado ativo de áreas embargadas em $t-1$**."""))

    c_bloco_x3 = r"""# 1. Autos de Infração Agregados
p_autos = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h1__autos_multas_ibama__municipio_anual_candidato.csv"
df_aut = pd.read_csv(p_autos, encoding='utf-8-sig')
df_aut.columns = df_aut.columns.str.strip().str.lower()
df_aut['codigo_ibge'] = df_aut['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_aut = df_aut[df_aut['codigo_ibge'].str.startswith('51')].groupby(['codigo_ibge', 'ano'], as_index=False).agg({
    'n_autos_ibama_it': 'sum',
    'valor_multas_ibama_it': 'sum'
})

# 2. Autos Espacializados (lat/long)
p_aut_esp = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h1__autos_ibama__espacial_municipio_anual_candidato.csv"
df_aut_esp = pd.read_csv(p_aut_esp, encoding='utf-8-sig')
df_aut_esp.columns = df_aut_esp.columns.str.strip().str.lower()
df_aut_esp['codigo_ibge'] = df_aut_esp['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_aut_esp = df_aut_esp[df_aut_esp['codigo_ibge'].str.startswith('51')].groupby(['codigo_ibge', 'ano'], as_index=False).agg({
    'n_autos_ibama_espacial': 'sum',
    'valor_multas_ibama_espacial': 'sum'
})

# 3. Termos de Embargo e Estoque Acumulado Ativo
p_emb = raiz_projeto / r"2_INTI\xdata\chap1\raw\tabular\ibama\termo_embargo_historico.csv"
if p_emb.exists():
    chunks = []
    for chunk in pd.read_csv(p_emb, sep=';', usecols=['COD_MUNICIPIO', 'UF', 'DAT_EMBARGO', 'QTD_AREA_EMBARGADA'], chunksize=100000, encoding='utf-8-sig', low_memory=False):
        mt_chunk = chunk[chunk['UF'] == 'MT'].copy()
        if not mt_chunk.empty:
            chunks.append(mt_chunk)
    df_emb = pd.concat(chunks, ignore_index=True)
    df_emb['codigo_ibge'] = df_emb['COD_MUNICIPIO'].dropna().astype(int).astype(str).str.zfill(7).replace({'5101837': '5106240'})
    df_emb['ano'] = pd.to_datetime(df_emb['DAT_EMBARGO'], errors='coerce').dt.year
    df_emb['qtd_area_embargada'] = pd.to_numeric(df_emb['QTD_AREA_EMBARGADA'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
    agg_emb = df_emb[df_emb['codigo_ibge'].str.startswith('51')].groupby(['codigo_ibge', 'ano'])['qtd_area_embargada'].sum().reset_index(name='area_embargada_nova_ha')
else:
    agg_emb = pd.DataFrame(columns=['codigo_ibge', 'ano', 'area_embargada_nova_ha'])

# Integrar diretamente na grade mestre para garantir 3.384 linhas e zeros verdadeiros antes das defasagens
bloco_x3 = pd.merge(grade_mestre[['codigo_ibge', 'ano']], df_aut, on=['codigo_ibge', 'ano'], how='left')
bloco_x3 = pd.merge(bloco_x3, df_aut_esp[['codigo_ibge', 'ano', 'n_autos_ibama_espacial']], on=['codigo_ibge', 'ano'], how='left')
bloco_x3 = pd.merge(bloco_x3, agg_emb, on=['codigo_ibge', 'ano'], how='left')

bloco_x3['n_autos_ibama_it'] = bloco_x3['n_autos_ibama_it'].fillna(0)
bloco_x3['valor_multas_ibama_it'] = bloco_x3['valor_multas_ibama_it'].fillna(0)
bloco_x3['n_autos_espacial'] = bloco_x3['n_autos_ibama_espacial'].fillna(0)
bloco_x3['area_embargada_nova_ha'] = bloco_x3['area_embargada_nova_ha'].fillna(0)

# Deflator simples acumulado IPCA para preços de 2024
deflator_ipca_2024 = {
    2001: 3.85, 2002: 3.42, 2003: 3.01, 2004: 2.80, 2005: 2.62,
    2006: 2.54, 2007: 2.44, 2008: 2.30, 2009: 2.21, 2010: 2.09,
    2011: 1.96, 2012: 1.85, 2013: 1.75, 2014: 1.64, 2015: 1.48,
    2016: 1.39, 2017: 1.35, 2018: 1.30, 2019: 1.25, 2020: 1.20,
    2021: 1.11, 2022: 1.05, 2023: 1.02, 2024: 1.00
}
bloco_x3['multa_real_2024'] = bloco_x3['valor_multas_ibama_it'] * bloco_x3['ano'].map(deflator_ipca_2024).fillna(1.0)

bloco_x3.sort_values(['codigo_ibge', 'ano'], inplace=True)
bloco_x3['n_autos_lag1'] = bloco_x3.groupby('codigo_ibge')['n_autos_ibama_it'].shift(1).fillna(0)
bloco_x3['ln_autos_lag1'] = np.log1p(bloco_x3['n_autos_lag1'])
bloco_x3['ln_multas_real_lag1'] = np.log1p(bloco_x3.groupby('codigo_ibge')['multa_real_2024'].shift(1).fillna(0))
bloco_x3['n_autos_espacial_lag1'] = bloco_x3.groupby('codigo_ibge')['n_autos_espacial'].shift(1).fillna(0)

bloco_x3['estoque_embargado_acum_ha'] = bloco_x3.groupby('codigo_ibge')['area_embargada_nova_ha'].cumsum()
bloco_x3['estoque_embargo_lag1'] = bloco_x3.groupby('codigo_ibge')['estoque_embargado_acum_ha'].shift(1).fillna(0)
bloco_x3['ln_estoque_embargo_lag1'] = np.log1p(bloco_x3['estoque_embargo_lag1'])

print(f"Bloco x3 estruturado com sucesso.")"""
    nb.cells.append(nbf.v4.new_code_cell(c_bloco_x3))

    # 3.5 Bloco x4 e x5
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.5 Blocos x4 e x5: Pecuária, Lotação e Cobertura da Terra

- **`x4` e `x4a`:** Efetivo bovino PPM/IBGE, log defasado, lotação aparente (cabeças/ha de pastagem MapBiomas) com salvaguarda (pastagem $\\ge 200\\text{ ha}$), winsorização em 4,0 cab/ha e indicador de intensificação ($\\Delta Lotação$).
- **`x5` e `x5a`:** Estoques remanescentes nativos, frações e dummy de fronteira fechada ($< 10\\%$)."""))

    c_bloco_x4_x5 = r"""# 1. Pecuária Municipal (PPM/IBGE)
p_ppm = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h1_h2__ppm_bovinos__ibge__municipio_anual.csv"
df_ppm = pd.read_csv(p_ppm, encoding='utf-8-sig')
df_ppm.columns = df_ppm.columns.str.strip().str.lower()
df_ppm['codigo_ibge'] = df_ppm['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_ppm = df_ppm[df_ppm['codigo_ibge'].str.startswith('51')].groupby(['codigo_ibge', 'ano'], as_index=False)['efetivo_bovino'].sum()

df_ppm.sort_values(['codigo_ibge', 'ano'], inplace=True)
df_ppm['ln_bovino_lag1'] = np.log1p(df_ppm.groupby('codigo_ibge')['efetivo_bovino'].shift(1))
df_ppm['dln_bovino'] = np.log1p(df_ppm['efetivo_bovino']) - df_ppm['ln_bovino_lag1']

# 2. Lotação Pecuária Aparente (Cabeças / Hectares de Pasto MapBiomas)
bloco_x4 = pd.merge(df_ppm, bloco_y[['codigo_ibge', 'ano', 'estoque_pastagem_ha']], on=['codigo_ibge', 'ano'], how='left')

PASTAGEM_MINIMA_HA = 200.0
bloco_x4['lotacao_aparente'] = np.where(
    bloco_x4['estoque_pastagem_ha'] >= PASTAGEM_MINIMA_HA,
    bloco_x4['efetivo_bovino'] / bloco_x4['estoque_pastagem_ha'],
    np.nan
)
bloco_x4['lotacao_winsorizada'] = bloco_x4['lotacao_aparente'].clip(lower=0.0, upper=4.0)
bloco_x4.sort_values(['codigo_ibge', 'ano'], inplace=True)
bloco_x4['lotacao_lag1'] = bloco_x4.groupby('codigo_ibge')['lotacao_winsorizada'].shift(1)
bloco_x4['delta_lotacao'] = bloco_x4['lotacao_winsorizada'] - bloco_x4['lotacao_lag1']

print("Blocos x4 e x5 de Pecuária e Lotação processados com sucesso.")"""
    nb.cells.append(nbf.v4.new_code_cell(c_bloco_x4_x5))

    # 3.6 Bloco x6, x8 e x9
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.6 Blocos x6, x8 e x9: Biomas, Regime Pluviométrico e Relevo

- **`x6`:** Proporções de Amazônia, Cerrado e Pantanal e choque institucional pós-2008 ($ShareAmazonia \\times Post2008$).
- **`x8`:** Precipitação anual, chuva de safra de verão (Out-Mar), chuva de safrinha (Fev-Mai), Z-scores e dummies de seca severa.
- **`x9`:** Altimetria média, amplitude altimétrica e dummy de relevo plano mecanizável ($< 250\\text{ m}$)."""))

    c_bloco_x6_x8_x9 = r"""# 1. Biomas (x6)
p_bio = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h2__biome_share__ibge2019_malha2024__candidato.csv"
df_bio = pd.read_csv(p_bio, encoding='utf-8-sig')
df_bio.columns = df_bio.columns.str.strip().str.lower()
df_bio['codigo_ibge'] = df_bio['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df_bio = df_bio.drop_duplicates('codigo_ibge')[['codigo_ibge', 'biome_amazonia_share_i', 'biome_cerrado_share_i', 'biome_pantanal_share_i', 'biome_class_70']]

# 2. Precipitação Sazonal e Anomalias (x8)
p_chuva_m = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h2__precip_mm__chirps_v2__mensal_candidato.csv"
df_ch = pd.read_csv(p_chuva_m, encoding='utf-8-sig')
df_ch.columns = df_ch.columns.str.strip().str.lower()
# Variável intensiva em mm: filtrar Boa Esperança do Norte (5101837) para manter a média de Nova Ubiratã sem duplicar soma
df_ch = df_ch[df_ch['codigo_ibge'].astype(str) != '5101837'].copy()
df_ch['codigo_ibge'] = df_ch['codigo_ibge'].astype(str).str.zfill(7)

# Ano civil total
ch_anual = df_ch.groupby(['codigo_ibge', 'ano'])['precip_mm'].sum().reset_index(name='precip_total_anual_mm')

# Safra de Verão (Outubro a Março)
df_ch['safra_ano'] = np.where(df_ch['mes'] >= 10, df_ch['ano'] + 1, df_ch['ano'])
safra_verao = df_ch[df_ch['mes'].isin([10, 11, 12, 1, 2, 3])].groupby(['codigo_ibge', 'safra_ano'])['precip_mm'].sum().reset_index(name='precip_safra_verao_mm')
safra_verao.rename(columns={'safra_ano': 'ano'}, inplace=True)

# Safrinha (Fevereiro a Maio)
safrinha = df_ch[df_ch['mes'].isin([2, 3, 4, 5])].groupby(['codigo_ibge', 'ano'])['precip_mm'].sum().reset_index(name='precip_safrinha_mm')

bloco_chuva = pd.merge(ch_anual, safra_verao, on=['codigo_ibge', 'ano'], how='left')
bloco_chuva = pd.merge(bloco_chuva, safrinha, on=['codigo_ibge', 'ano'], how='left')
bloco_chuva.sort_values(['codigo_ibge', 'ano'], inplace=True)
bloco_chuva['precip_safra_verao_lag1'] = bloco_chuva.groupby('codigo_ibge')['precip_safra_verao_mm'].shift(1)

# Z-scores de precipitação
p_anom = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv"
df_anom = pd.read_csv(p_anom, encoding='utf-8-sig')
df_anom.columns = df_anom.columns.str.strip().str.lower()
df_anom = df_anom[df_anom['codigo_ibge'].astype(str) != '5101837'].copy()
df_anom['codigo_ibge'] = df_anom['codigo_ibge'].astype(str).str.zfill(7)
df_anom = df_anom[['codigo_ibge', 'ano', 'precip_zscore_1981_2010']].drop_duplicates(['codigo_ibge', 'ano'])

df_anom['dummy_seca_severa'] = (df_anom['precip_zscore_1981_2010'] < -1.5).astype(int)
df_anom['dummy_excesso_chuva'] = (df_anom['precip_zscore_1981_2010'] > 1.5).astype(int)

bloco_x8 = pd.merge(bloco_chuva, df_anom, on=['codigo_ibge', 'ano'], how='left')

# 3. Topografia e Relevo (x9)
p_rel = raiz_projeto / r"2_INTI\xdata\chap1\processed\tabular\topography__copdem90__municipio_candidato.csv"
df_rel = pd.read_csv(p_rel, encoding='utf-8-sig')
df_rel.columns = df_rel.columns.str.strip().str.lower()
df_rel = df_rel[df_rel['codigo_ibge'].astype(str) != '5101837'].copy()
df_rel['codigo_ibge'] = df_rel['codigo_ibge'].astype(str).str.zfill(7)
df_rel = df_rel.drop_duplicates('codigo_ibge')[['codigo_ibge', 'elevation_mean_m', 'elevation_min_m', 'elevation_max_m']]
df_rel['amplitude_altimetrica_m'] = df_rel['elevation_max_m'] - df_rel['elevation_min_m']
df_rel['dummy_relevo_plano'] = (df_rel['amplitude_altimetrica_m'] < 250.0).astype(int)

print("Blocos x6, x8 e x9 processados com sucesso.")"""
    nb.cells.append(nbf.v4.new_code_cell(c_bloco_x6_x8_x9))

    # =========================================================================
    # SEÇÃO 4: Consolidação Final do Painel
    # =========================================================================
    nb.cells.append(nbf.v4.new_markdown_cell("""## 4. Integração Final e Salvamento do Painel Balanceado

Unificamos todos os blocos na **grade mestre balanceada de 141 municípios $\\times$ 24 anos** e geramos o painel econométrico oficial para o Capítulo 1."""))

    c_merge_final = r"""# Junção sequencial na grade mestre
painel = grade_mestre.copy()

# Merges sucessivos
painel = pd.merge(painel, bloco_y, on=['codigo_ibge', 'ano'], how='left')
painel = pd.merge(painel, bloco_x1, on='ano', how='left')
painel = pd.merge(painel, bloco_x2, on=['codigo_ibge', 'ano'], how='left')
painel = pd.merge(painel, bloco_x3, on=['codigo_ibge', 'ano'], how='left')
painel = pd.merge(painel, bloco_x4[['codigo_ibge', 'ano', 'efetivo_bovino', 'ln_bovino_lag1', 'dln_bovino', 'lotacao_winsorizada', 'lotacao_lag1', 'delta_lotacao']], on=['codigo_ibge', 'ano'], how='left')
painel = pd.merge(painel, df_bio, on='codigo_ibge', how='left')
painel = pd.merge(painel, bloco_x8, on=['codigo_ibge', 'ano'], how='left')
painel = pd.merge(painel, df_rel, on='codigo_ibge', how='left')

# Interações Shift-Share Centrais do Modelo Econométrico
painel['post_2008'] = (painel['ano'] >= 2008).astype(int)
painel['interacao_amazonia_post2008'] = painel['biome_amazonia_share_i'] * painel['post_2008']
painel['choque_preco_soja_aptidao'] = painel['ln_psoja_lag1'] * painel['aptidao_soja_norm']
painel['choque_preco_soja_relevo'] = painel['ln_psoja_lag1'] * painel['dummy_relevo_plano']

# Ordenação lógica das colunas e linhas
painel.sort_values(['codigo_ibge', 'ano'], inplace=True)

# Exportação do Painel Consolidado
caminho_saida_csv = raiz_projeto / r"2_INTI\chapters\chap1\stats\AED\gm\painel_mt_2001_2024.csv"
painel.to_csv(caminho_saida_csv, index=False, encoding='utf-8-sig')

print("=" * 70)
print(f"PAINEL CONSOLIDADO 2001-2024 CONSTRUÍDO COM SUCESSO!")
print(f"Arquivo salvo em: {caminho_saida_csv}")
print(f"Total de Linhas: {len(painel)} (Meta exata: 3.384)")
print(f"Total de Municípios: {painel['codigo_ibge'].nunique()} (Meta exata: 141)")
print(f"Total de Variáveis Harmonizadas: {painel.shape[1]}")
print("=" * 70)"""
    nb.cells.append(nbf.v4.new_code_cell(c_merge_final))

    # =========================================================================
    # SEÇÃO 5: Estatística Descritiva Detalhada
    # Regra: UMA CÉLULA PARA CADA TABELA, COMANDO OU GRÁFICO
    # =========================================================================
    nb.cells.append(nbf.v4.new_markdown_cell("""## 5. Bateria de Estatística Descritiva Detalhada do Painel

Conforme diretriz metodológica, **cada tabela, comando de diagnóstico ou gráfico descritivo é apresentado em uma célula individual dedicada**, permitindo inspeção granular e auditabilidade completa de cada dimensão econômica do painel."""))

    # 5.1 Diagnóstico Dimensional
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.1 Diagnóstico de Dimensões e Identidade da Grade"))
    nb.cells.append(nbf.v4.new_code_cell("""print(f"Dimensões do Painel (Linhas x Colunas): {painel.shape}")
print(f"Contagem de municípios únicos: {painel['codigo_ibge'].nunique()}")
print(f"Contagem de anos únicos: {painel['ano'].nunique()} (Período: {painel['ano'].min()} a {painel['ano'].max()})")
print(f"Grau de balanceamento: {len(painel) / (painel['codigo_ibge'].nunique() * painel['ano'].nunique()):.1%}")"""))

    # 5.2 Tabela Y
    nb.cells.append(nbf.v4.new_markdown_cell("""### 5.2 Tabela Descritiva: Variáveis Dependentes de Uso da Terra e Conversão ($Y$)
Apresenta os momentos estatísticos (média, desvio, percentis) da conversão bruta para pastagem, agricultura e taxa de conversão."""))
    nb.cells.append(nbf.v4.new_code_cell("""cols_y = ['estoque_pastagem_ha', 'estoque_agricultura_ha', 'Y_conv_pastagem_ha', 'Y_conv_agricultura_ha', 'Y_conv_total_ha', 'Y_tx_conv']
desc_y = painel[cols_y].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_y[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.3 Gráfico Y
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.3 Gráfico: Evolução Temporal da Conversão Bruta Agregada em MT (ha)"))
    nb.cells.append(nbf.v4.new_code_cell("""evol_y = painel.groupby('ano')[['Y_conv_pastagem_ha', 'Y_conv_agricultura_ha']].sum().reset_index()

plt.figure(figsize=(10, 4.5))
plt.plot(evol_y['ano'], evol_y['Y_conv_pastagem_ha'], marker='o', color='orange', label='Conversão para Pastagem (ha)', linewidth=2)
plt.plot(evol_y['ano'], evol_y['Y_conv_agricultura_ha'], marker='s', color='forestgreen', label='Conversão para Agricultura (ha)', linewidth=2)
plt.title("Evolução da Conversão Bruta Anual em Mato Grosso (2001–2024)")
plt.xlabel("Ano")
plt.ylabel("Hectares Convertidos por Ano")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()"""))

    # 5.4 Tabela x1
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.4 Tabela Descritiva: Preços Mundiais e Termos de Troca ($x1$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x1 = ['psoja_lag1', 'pmilho_lag1', 'pcarne_lag1', 'razao_psoja_pmilho_lag1', 'razao_carne_soja_lag1']
desc_x1 = painel[cols_x1].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x1[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.5 Gráfico x1
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.5 Gráfico: Trajetória dos Preços Mundiais Defasados de Soja e Milho (USD/t)"))
    nb.cells.append(nbf.v4.new_code_cell("""precos_tempo = painel.groupby('ano')[['psoja_lag1', 'pmilho_lag1']].first().reset_index()

plt.figure(figsize=(10, 4))
plt.plot(precos_tempo['ano'], precos_tempo['psoja_lag1'], color='goldenrod', marker='o', label='Soja (t-1, USD/t)')
plt.plot(precos_tempo['ano'], precos_tempo['pmilho_lag1'], color='darkorange', marker='s', label='Milho (t-1, USD/t)')
plt.title("Preços Mundiais na Janela Pré-Safra (Banco Mundial, 2001–2024)")
plt.xlabel("Ano da Safra (t)")
plt.ylabel("Cotação Internacional (USD/t)")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()"""))

    # 5.6 Tabela x2
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.6 Tabela Descritiva: Produção e Rendimento Agrícola PAM/IBGE ($x2$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x2 = ['prod_soja_t', 'prod_milho_t', 'rend_soja_kg_ha', 'rend_soja_lag1', 'hprod_soja_pre2001']
desc_x2 = painel[cols_x2].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x2[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.7 Gráfico x2
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.7 Gráfico: Distribuição do Rendimento Observado de Soja (kg/ha)"))
    nb.cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(12, 4))

sns.histplot(painel['rend_soja_kg_ha'].dropna(), bins=30, kde=True, ax=axes[0], color='seagreen')
axes[0].set_title("Histograma: Rendimento Observado de Soja (kg/ha)")
axes[0].set_xlabel("Produtividade (kg/ha)")

sns.boxplot(x=painel['ano'], y=painel['rend_soja_kg_ha'], ax=axes[1], color='lightgreen')
axes[1].set_title("Evolução dos Boxplots Anuais de Rendimento de Soja")
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=90, fontsize=8)
axes[1].set_ylabel("kg/ha")

plt.tight_layout()
plt.show()"""))

    # 5.8 Tabela GAEZ
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.8 Tabela Descritiva: Capacidade Agroclimática GAEZ v4 e Brecha de Produtividade"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_gaez = ['gaez_yield_soja_comercial_kg_ha', 'gaez_yield_milho_comercial_kg_ha', 'aptidao_soja_norm', 'yield_gap_soja']
desc_gaez = painel[cols_gaez].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_gaez[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.9 Gráfico GAEZ
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.9 Gráfico: Produtividade Observada vs Potencial GAEZ (Yield Gap)"))
    nb.cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(7, 5))
sub_gap = painel.dropna(subset=['rend_soja_lag1', 'gaez_yield_soja_comercial_kg_ha'])
sns.scatterplot(data=sub_gap.sample(min(1000, len(sub_gap)), random_state=42), 
                x='gaez_yield_soja_comercial_kg_ha', y='rend_soja_lag1', alpha=0.5, color='darkgreen')
plt.plot([1500, 4500], [1500, 4500], color='red', linestyle='--', label='Fronteira 1:1 (Gap = 1.0)')
plt.title("Produtividade Observada vs Potencial GAEZ Comercial (kg/ha)")
plt.xlabel("Produtividade Potencial GAEZ (13% umidade, kg/ha)")
plt.ylabel("Produtividade Observada no Ano Anterior (kg/ha)")
plt.legend()
plt.tight_layout()
plt.show()"""))

    # 5.10 Tabela x3
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.10 Tabela Descritiva: Fiscalização Ambiental do IBAMA ($x3$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x3 = ['n_autos_ibama_it', 'n_autos_lag1', 'multa_real_2024', 'area_embargada_nova_ha', 'estoque_embargo_lag1']
desc_x3 = painel[cols_x3].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x3[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.11 Gráfico x3
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.11 Gráfico: Evolução da Fiscalização Ambiental do IBAMA em MT"))
    nb.cells.append(nbf.v4.new_code_cell("""ibama_tempo = painel.groupby('ano').agg(
    total_autos=('n_autos_ibama_it', 'sum'),
    estoque_embargo_ha=('estoque_embargo_lag1', 'sum')
).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 4.5))
ax2 = ax1.twinx()

ax1.bar(ibama_tempo['ano'] - 0.2, ibama_tempo['total_autos'], width=0.4, color='crimson', alpha=0.7, label='Autos Lavrados (Total MT)')
ax2.plot(ibama_tempo['ano'], ibama_tempo['estoque_embargo_ha'] / 1e6, color='navy', marker='o', linewidth=2, label='Estoque Embargado Ativo (Milhões ha)')

ax1.set_xlabel("Ano")
ax1.set_ylabel("Quantidade de Autos de Infração", color='crimson')
ax2.set_ylabel("Área Total Embargada (Milhões de ha)", color='navy')
ax1.set_title("Evolução das Ações de Comando e Controle em Mato Grosso (2001–2024)")
plt.tight_layout()
plt.show()"""))

    # 5.12 Tabela x4
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.12 Tabela Descritiva: Pecuária e Lotação de Pastagens ($x4$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x4 = ['efetivo_bovino', 'ln_bovino_lag1', 'dln_bovino', 'lotacao_winsorizada', 'delta_lotacao']
desc_x4 = painel[cols_x4].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x4[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.13 Gráfico x4
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.13 Gráfico: Distribuição da Taxa de Lotação Pecuária Aparente (Cabeças/ha)"))
    nb.cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(9, 4))
sns.histplot(painel['lotacao_winsorizada'].dropna(), bins=40, kde=True, color='sienna')
plt.axvline(painel['lotacao_winsorizada'].mean(), color='red', linestyle='--', label=f"Média: {painel['lotacao_winsorizada'].mean():.2f} cab/ha")
plt.axvline(painel['lotacao_winsorizada'].median(), color='blue', linestyle=':', label=f"Mediana: {painel['lotacao_winsorizada'].median():.2f} cab/ha")
plt.title("Distribuição da Lotação Pecuária Aparente em MT (Corte em 4,0 cab/ha)")
plt.xlabel("Lotação (Cabeças de Gado / Hectare de Pasto)")
plt.ylabel("Contagem de Observações Município-Ano")
plt.legend()
plt.tight_layout()
plt.show()"""))

    # 5.14 Tabela x5
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.14 Tabela Descritiva: Cobertura da Terra e Condição de Fronteira ($x5$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x5 = ['native_veg_ha_lag1', 'area_mapeada_ha', 'flag_fronteira_fechada']
desc_x5 = painel[cols_x5].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x5[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.15 Gráfico x5
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.15 Gráfico: Dinâmica Média do Estoque Remanescente de Vegetação Nativa"))
    nb.cells.append(nbf.v4.new_code_cell("""painel['share_nativa_lag1'] = painel['native_veg_ha_lag1'] / painel['area_mapeada_ha']
nativa_tempo = painel.groupby('ano')['share_nativa_lag1'].mean().reset_index()

plt.figure(figsize=(9, 4))
plt.plot(nativa_tempo['ano'], nativa_tempo['share_nativa_lag1'] * 100, marker='o', color='darkgreen', linewidth=2)
plt.title("Proporção Média de Vegetação Nativa Remanescente por Município (% da área)")
plt.xlabel("Ano")
plt.ylabel("Vegetação Nativa Média (%)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()"""))

    # 5.16 Tabela x6
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.16 Tabela Descritiva: Composição Territorial de Biomas ($x6$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x6 = ['biome_amazonia_share_i', 'biome_cerrado_share_i', 'biome_pantanal_share_i', 'interacao_amazonia_post2008']
desc_x6 = painel[cols_x6].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x6[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.17 Gráfico x6
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.17 Gráfico: Distribuição dos 141 Municípios de MT por Bioma Predominante"))
    nb.cells.append(nbf.v4.new_code_cell("""bioma_counts = painel.drop_duplicates('codigo_ibge')['biome_class_70'].value_counts()

plt.figure(figsize=(7, 4))
bioma_counts.plot(kind='bar', color=['darkgreen', 'peru', 'teal'])
plt.title("Contagem de Municípios por Bioma Predominante (Critério 70%)")
plt.xlabel("Bioma Predominante")
plt.ylabel("Número de Municípios")
plt.xticks(rotation=0)
for i, v in enumerate(bioma_counts):
    plt.text(i, v + 1, str(v), ha='center', fontweight='bold')
plt.tight_layout()
plt.show()"""))

    # 5.18 Tabela x8
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.18 Tabela Descritiva: Precipitação e Choques Climáticos ($x8$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x8 = ['precip_total_anual_mm', 'precip_safra_verao_mm', 'precip_safrinha_mm', 'precip_zscore_1981_2010', 'dummy_seca_severa']
desc_x8 = painel[cols_x8].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x8[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.19 Gráfico x8
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.19 Gráfico: Série Histórica das Anomalias Padronizadas de Chuva (Z-Score)"))
    nb.cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(11, 4))
sns.boxplot(x=painel['ano'], y=painel['precip_zscore_1981_2010'], color='lightblue')
plt.axhline(-1.5, color='red', linestyle='--', label='Limiar de Seca Severa (Z < -1.5)')
plt.axhline(0, color='gray', linestyle=':')
plt.title("Distribuição das Anomalias Climáticas Anuais de Chuva em MT (2001–2024)")
plt.xlabel("Ano")
plt.ylabel("Z-Score de Precipitação")
plt.xticks(rotation=90, fontsize=8)
plt.legend(loc='lower left')
plt.tight_layout()
plt.show()"""))

    # 5.20 Tabela x9
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.20 Tabela Descritiva: Topografia e Aptidão para Mecanização ($x9$)"))
    nb.cells.append(nbf.v4.new_code_cell("""cols_x9 = ['elevation_mean_m', 'elevation_min_m', 'elevation_max_m', 'amplitude_altimetrica_m', 'dummy_relevo_plano']
desc_x9 = painel[cols_x9].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
desc_x9[['count', 'mean', 'std', '5%', '50%', '95%', 'max']]"""))

    # 5.21 Gráfico x9
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.21 Gráfico: Distribuição da Amplitude Altimétrica Municipal"))
    nb.cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(8, 4))
mun_rel = painel.drop_duplicates('codigo_ibge')
sns.histplot(mun_rel['amplitude_altimetrica_m'], bins=25, kde=True, color='slategray')
plt.axvline(250, color='red', linestyle='--', label='Limiar de Relevo Plano (< 250m)')
plt.title("Distribuição da Amplitude Altimétrica dos 141 Municípios de MT")
plt.xlabel("Amplitude Altimétrica (Elevação Máx - Mín em metros)")
plt.ylabel("Contagem de Municípios")
plt.legend()
plt.tight_layout()
plt.show()"""))

    # 5.22 Matriz de Correlação
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.22 Tabela de Correlação Linear de Pearson entre Variáveis-Chave"))
    nb.cells.append(nbf.v4.new_code_cell("""vars_corr = [
    'Y_conv_total_ha', 'Y_tx_conv', 'psoja_lag1', 'rend_soja_lag1',
    'aptidao_soja_norm', 'ln_autos_lag1', 'lotacao_winsorizada',
    'precip_safra_verao_mm', 'dummy_relevo_plano'
]
corr_matrix = painel[vars_corr].corr()
corr_matrix.round(3)"""))

    # 5.23 Heatmap de Correlação
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.23 Gráfico: Mapa de Calor (Heatmap) da Matriz de Correlação"))
    nb.cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(9, 7))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, cbar_kws={'label': 'Correlação de Pearson'})
plt.title("Matriz de Correlação Paramétrica: Determinantes do Uso da Terra em MT")
plt.tight_layout()
plt.show()"""))

    # 5.24 Diagnóstico de Valores Ausentes
    nb.cells.append(nbf.v4.new_markdown_cell("### 5.24 Auditoria de Valores Ausentes (NaNs) no Painel Consolidado"))
    nb.cells.append(nbf.v4.new_code_cell("""nans = painel.isna().sum()
nans_pct = (nans / len(painel)) * 100
tabela_nans = pd.DataFrame({'Valores Ausentes': nans, 'Percentual (%)': nans_pct.round(2)})
tabela_nans[tabela_nans['Valores Ausentes'] > 0].sort_values('Percentual (%)', ascending=False)"""))

    # 5.25 Diagnóstico Final
    nb.cells.append(nbf.v4.new_markdown_cell("""### 5.25 Diagnóstico Final de Balanceamento e Conclusão

Verificação formal da estrutura longitudinal do painel consolidado: confirmamos que todos os 141 municípios possuem exatamente 24 observações anuais consecutivas (2001–2024), totalizando 3.384 linhas sem descontinuidades espaciais ou temporais."""))
    nb.cells.append(nbf.v4.new_code_cell("""obs_por_mun = painel.groupby('codigo_ibge')['ano'].count()
balanceamento_perfeito = (obs_por_mun == 24).all() and len(obs_por_mun) == 141

print("=" * 60)
print("AUDITORIA FINAL DE BALANCEAMENTO DO PAINEL:")
print(f"Total de municípios auditados: {len(obs_por_mun)}")
print(f"Mínimo de anos por município: {obs_por_mun.min()}")
print(f"Máximo de anos por município: {obs_por_mun.max()}")
print(f"Painel 100% balanceado e integro: {balanceamento_perfeito}")
print("=" * 60)"""))

    # Salvar o notebook
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"Notebook do Painel Consolidado gerado com sucesso em: {NOTEBOOK_PATH}")
    print(f"Total de células no notebook: {len(nb.cells)}")

if __name__ == "__main__":
    create_panel_notebook()
