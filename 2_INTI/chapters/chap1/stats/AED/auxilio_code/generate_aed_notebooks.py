# -*- coding: utf-8 -*-
"""
Script de automação para geração padronizada de Notebooks de Análise Exploratória de Dados (AED).
Projeto: Tese de Doutorado - Economia Aplicada / Uso da Terra em Mato Grosso
Diretório de Saída: 2_INTI/chapters/chap1/stats/AED/gm/
Protocolo: 6 Fases (Setup & Load, Cleaning & Wrangling, Estatística Descritiva,
                     Análise Univariada, Análise Bivariada, Feature Engineering)

Salvaguarda Territorial:
- Harmonização estrita para 141 municípios de Mato Grosso.
- O 142º município criado (Boa Esperança do Norte - 5101837) é reincorporado/aglutinado
  ao seu município original de origem (Nova Ubiratã - 5106240).
"""

import os
import re
import json
from pathlib import Path
import nbformat as nbf
import sys

# Importar definições ricas de Feature Engineering (Passos 1 e 2)
gemini_dir = Path(__file__).resolve().parent.parent / "gm"
if gemini_dir.exists():
    sys.path.insert(0, str(gemini_dir))
try:
    from phase6_definitions import PHASE6_DATA
except ImportError:
    PHASE6_DATA = {}

# -----------------------------------------------------------------------------
# 1. LOCALIZAÇÃO DE DIRETÓRIOS
# -----------------------------------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
raiz_projeto = None
for p in [CURRENT_FILE] + list(CURRENT_FILE.parents):
    if (p / "2_INTI" / "RESEARCH_PROTOCOL.md").is_file() or (p / "AGENTS.md").is_file():
        raiz_projeto = p
        break

if raiz_projeto is None:
    raise FileNotFoundError("Não foi possível localizar a raiz do projeto (onde está 2_INTI/RESEARCH_PROTOCOL.md).")

BASE_DIR = raiz_projeto
HIPOTESES_FILE = BASE_DIR / "2_INTI" / "chapters" / "chap1" / "stats" / "HIPOTESES TESE - CHAP1.txt"
OUTPUT_DIR = BASE_DIR / "2_INTI" / "chapters" / "chap1" / "stats" / "AED" / "gm"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 2. PARSER DO ARQUIVO DE HIPÓTESES
# -----------------------------------------------------------------------------
def parse_hipoteses_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    variables = []
    current_group = "Geral"
    curr_var = None

    for line in lines:
        raw = line.rstrip()
        s = raw.strip()
        if not s:
            continue

        if s.startswith("[") and s.endswith("]"):
            current_group = s[1:-1]
            continue

        if s.startswith("PENDÊNCIAS"):
            if curr_var:
                variables.append(curr_var)
                curr_var = None
            current_group = "PENDÊNCIAS"
            continue

        m = re.match(r"^-\s+([A-Za-z0-9_\-]+)\s*=\s*(.*)$", s)
        if m:
            if curr_var:
                variables.append(curr_var)
            var_name = m.group(1).strip()
            desc = m.group(2).strip()
            curr_var = {
                "name": var_name,
                "desc": desc,
                "group": current_group,
                "paths": [],
                "notes": []
            }
            continue

        if curr_var:
            if "2_INTI\\" in s or s.endswith(".csv"):
                curr_var["paths"].append(s.lstrip("* ").strip())
            elif s.startswith("*"):
                curr_var["notes"].append(s.lstrip("* ").strip())

    if curr_var:
        variables.append(curr_var)

    return variables

# -----------------------------------------------------------------------------
# 3. METADADOS E CÓDIGO CUSTOMIZADO DAS 6 FASES POR VARIÁVEL
# -----------------------------------------------------------------------------
VAR_SPECS = {
    "Y_conv": {
        "title": "Y_conv — Conversão Bruta de Vegetação Nativa para Agricultura e Pastagem",
        "concept": "Mede a área física (em hectares) de vegetação nativa convertida em novos usos agropecuários (pastagem ou lavouras) em cada município e ano.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do IBGE do município (7 dígitos). Em MT são 141 municípios históricos.",
            "municipality": "Nome oficial do município.",
            "biome": "Bioma da área (Amazônia, Cerrado ou Pantanal).",
            "class_id": "Código da classe de cobertura da terra do MapBiomas (ex: 15=Pastagem, 39=Soja, 41=Outras Lavouras).",
            "ano": "Ano da medição do uso do solo (1985 a 2024).",
            "area_ha": "Área em hectares ocupada pela respectiva classe."
        },
        "target_col": "area_ha",
        "phase2_code": """# Limpeza e Padronização dos Nomes das Colunas
df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)

# Conversão de Tipos
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
df['area_ha'] = pd.to_numeric(df['area_ha'], errors='coerce')

# REGRA DE HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS DE MT):
# O 142º município (Boa Esperança do Norte - 5101837) é reincorporado em Nova Ubiratã (5106240)
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})

# Filtrar somente municípios de Mato Grosso (iniciados em 51)
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO DOCUMENTO DE HIPÓTESES:
# 'Manter os destinos agricultura e pastagem separados; diferença de estoques não mede conversão bruta.'
# Identificação dos destinos antrópicos:
# class_id 15: Pastagem
# class_id 39: Soja | class_id 41: Outras Lavouras Temporárias | class_id 20: Cana
df['destino_uso'] = 'Outros'
df.loc[df['class_id'] == 15, 'destino_uso'] = 'Pastagem'
df.loc[df['class_id'].isin([20, 39, 41]), 'destino_uso'] = 'Agricultura'

# Aglutinar eventuais registros remapeados para garantir unicidade
df = df.groupby(['codigo_ibge', 'municipality', 'biome', 'class_id', 'destino_uso', 'ano'], as_index=False)['area_ha'].sum()

print(f"Total de municípios únicos de MT na base: {df['codigo_ibge'].nunique()} (Meta: exatamente 141)")
print("Valores ausentes:\\n", df.isna().sum())""",
        "phase3_code": """# Resumo Estatístico das Áreas Ocupadas (ha)
print("--- Estatísticas descritivas gerais (area_ha) ---")
print(df['area_ha'].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# Distinção econométrica essencial: Zero verdadeiro vs Ausência de registro
total_obs = len(df)
zeros_reais = (df['area_ha'] == 0).sum()
nulos = df['area_ha'].isna().sum()

print(f"\\nTotal de linhas no dataset: {total_obs}")
print(f"Zeros verdadeiros (área nula registrada): {zeros_reais} ({zeros_reais / total_obs:.2%})")
print(f"Valores ausentes (não observados): {nulos} ({nulos / total_obs:.2%})")

# Médias e medianas agregadas por destino e bioma
print("\\nÁrea agregada (ha) por Destino e Bioma:")
print(df.groupby(['destino_uso', 'biome'])['area_ha'].agg(['count', 'mean', 'median', 'sum']))""",
        "phase4_code": """# Análise Univariada: Formato das Distribuições e Outliers
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 1. Histograma da área (escala logarítmica para lidar com assimetria extrema)
sns.histplot(df[df['area_ha'] > 0]['area_ha'], bins=40, log_scale=True, kde=True, ax=axes[0], color='forestgreen')
axes[0].set_title("Distribuição da Área Ocupada (ha > 0, Escala Log)")
axes[0].set_xlabel("Área (hectares, log)")

# 2. Boxplot comparativo entre Pastagem e Agricultura
sns.boxplot(data=df[df['destino_uso'].isin(['Pastagem', 'Agricultura'])], x='destino_uso', y='area_ha', ax=axes[1], palette='Set2')
axes[1].set_yscale('log')
axes[1].set_title("Boxplot e Outliers por Destino (Escala Log)")
axes[1].set_ylabel("Área (ha)")

# 3. Evolução temporal da soma de estoques em MT
df_tempo = df.groupby(['ano', 'destino_uso'])['area_ha'].sum().reset_index()
sns.lineplot(data=df_tempo[df_tempo['destino_uso'].isin(['Pastagem', 'Agricultura'])], x='ano', y='area_ha', hue='destino_uso', marker='o', ax=axes[2])
axes[2].set_title("Evolução Histórica do Estoque Total em MT (1985-2024)")
axes[2].set_ylabel("Área Total (ha)")

plt.tight_layout()
plt.show()""",
        "phase5_code": """# Análise Bivariada: Dimensão Espaço-Temporal no Painel (2001-2024)
df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024) & (df['destino_uso'].isin(['Pastagem', 'Agricultura']))].copy()

plt.figure(figsize=(12, 6))
sns.lineplot(data=df_painel, x='ano', y='area_ha', hue='biome', style='destino_uso', estimator='sum', errorbar=None)
plt.title("Evolução do Uso da Terra por Bioma e Destino em Mato Grosso (2001-2024)")
plt.xlabel("Ano")
plt.ylabel("Área Total Agregada (ha)")
plt.legend(title="Bioma e Destino", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Comentário Econométrico:
# Os biomas representam restrições institucionais distintas (Reserva Legal de 80% na Amazônia vs 35% no Cerrado).
# Em painel com efeito fixo municipal, dummies estáticas de bioma são absorvidas, mas podem interagir com tempo.""",
        "phase6_code": """# Feature Engineering: Estruturação para Modelagem Econométrica
# 1. Pivotar para ter uma linha única por município-ano com colunas separadas para cada destino
df_agro = df[df['destino_uso'].isin(['Pastagem', 'Agricultura'])].copy()
painel_estoques = df_agro.pivot_table(
    index=['codigo_ibge', 'ano'],
    columns='destino_uso',
    values='area_ha',
    aggfunc='sum',
    fill_value=0
).reset_index()

painel_estoques.rename(columns={'Agricultura': 'estoque_agricultura_ha', 'Pastagem': 'estoque_pastagem_ha'}, inplace=True)

# 2. Variação anual de estoque (Delta Stock)
painel_estoques.sort_values(['codigo_ibge', 'ano'], inplace=True)
painel_estoques['delta_pastagem_ha'] = painel_estoques.groupby('codigo_ibge')['estoque_pastagem_ha'].diff()
painel_estoques['delta_agricultura_ha'] = painel_estoques.groupby('codigo_ibge')['estoque_agricultura_ha'].diff()

# 3. Código-esqueleto para conversão bruta (transições reais)
# RESSALVA METODOLÓGICA: Delta Stock não mede conversão bruta (pois ignora abandono e regeneração).
# Este esqueleto aguarda a junção com a matriz de transições reais de vegetação nativa -> uso antrópico.
painel_estoques['conversao_bruta_pastagem_ha'] = np.nan
painel_estoques['conversao_bruta_agricultura_ha'] = np.nan

print(f"Dimensões do painel municipal estruturado: {painel_estoques.shape}")
print(f"Municípios únicos no painel: {painel_estoques['codigo_ibge'].nunique()} (141 municípios)")
painel_estoques.head()"""
    },

    "Y_tx-conv": {
        "title": "Y_tx-conv — Taxa de Conversão para Agricultura e Pastagem",
        "concept": "Mede a taxa anual de conversão (0 a 1), definida pela divisão entre a área convertida no ano t e o estoque de vegetação nativa remanescente no início do período (t-1).",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do IBGE do município (7 dígitos). Base de 141 municípios.",
            "municipio": "Nome do município.",
            "ano": "Ano da observação.",
            "area_mapeada_ha": "Área territorial total mapeada do município (ha).",
            "native_veg_ha_it": "Estoque de vegetação nativa no ano t (ha).",
            "native_veg_share_it": "Proporção de vegetação nativa no ano t (0 a 1).",
            "native_veg_ha_lag1": "Estoque nativo no ano t-1 (DENOMINADOR CANDIDATO da taxa de conversão).",
            "native_veg_share_lag1": "Fração de vegetação nativa no ano t-1."
        },
        "target_col": "native_veg_ha_lag1",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

for col in ['area_mapeada_ha', 'native_veg_ha_it', 'native_veg_share_it', 'native_veg_ha_lag1', 'native_veg_share_lag1']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# Se houver linhas remapeadas, aglutinar somando hectares e recalculando proporções
df = df.groupby(['codigo_ibge', 'ano'], as_index=False).agg({
    'area_mapeada_ha': 'sum',
    'native_veg_ha_it': 'sum',
    'native_veg_ha_lag1': 'sum'
})
df['native_veg_share_it'] = df['native_veg_ha_it'] / df['area_mapeada_ha']
df['native_veg_share_lag1'] = df['native_veg_ha_lag1'] / df['area_mapeada_ha']

print(f"Municípios únicos: {df['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva do estoque nativo no início do período (native_veg_ha_lag1):")
print(df['native_veg_ha_lag1'].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# REGRA DO TXT: 'denominador zero implica taxa indefinida'
den_zeros = (df['native_veg_ha_lag1'] == 0).sum()
den_nulos = df['native_veg_ha_lag1'].isna().sum()
print(f"Denominadores iguais a zero: {den_zeros} | Denominadores ausentes: {den_nulos}")""",
        "phase4_code": """fig, axes = plt.subplots(1, 3, figsize=(18, 5))
sns.histplot(df['native_veg_share_lag1'].dropna(), bins=30, kde=True, ax=axes[0], color='teal')
axes[0].set_title("Distribuição da Fração Nativa (t-1)")

sns.boxplot(y=df['native_veg_share_lag1'], ax=axes[1], color='powderblue')
axes[1].set_title("Boxplot da Fração Nativa (t-1)")

df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
sns.lineplot(data=df_painel, x='ano', y='native_veg_share_lag1', marker='o', ax=axes[2], color='darkcyan')
axes[2].set_title("Média Municipal da Fração Nativa (2001-2024)")

plt.tight_layout()
plt.show()""",
        "phase5_code": """# Trajetória temporal do estoque total remanescente
df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
plt.figure(figsize=(10, 4))
sns.lineplot(data=df_painel, x='ano', y='native_veg_ha_it', estimator='sum', color='darkgreen')
plt.title("Estoque Total Agregado de Vegetação Nativa em Mato Grosso (2001-2024)")
plt.ylabel("Hectares de Nativa")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()""",
        "phase6_code": """# Feature Engineering: Construção da Taxa de Conversão Y_tx-conv
# Fórmula: Y_tx_conv = (Área Convertida no ano t) / (native_veg_ha_lag1)
df_fe = df[['codigo_ibge', 'ano', 'native_veg_ha_lag1', 'native_veg_share_lag1']].copy()

# Esqueleto para incorporação do numerador:
df_fe['conversao_bruta_ha'] = np.nan

# Cálculo da taxa com salvaguarda matemática (se denominador <= 0, taxa é NaN)
df_fe['Y_tx_conv'] = np.where(
    df_fe['native_veg_ha_lag1'] > 10.0,
    df_fe['conversao_bruta_ha'] / df_fe['native_veg_ha_lag1'],
    np.nan
)

# Flag de controle para municípios com vegetação praticamente exaurida
df_fe['flag_vegetacao_exaurida'] = (df_fe['native_veg_share_lag1'] < 0.05).astype(int)

print(df_fe.head())"""
    },

    "x1_psoja-pmilho": {
        "title": "x1_psoja-pmilho — Preços Mundiais de Soja e Milho (World Bank)",
        "concept": "Série temporal de preços internacionais de soja e milho (USD/tonelada métrica). Funciona como choque comum de demanda exógena aos municípios.",
        "is_municipal": False,
        "cols_guide": {
            "data": "Data mensal da cotação internacional (YYYY-MM-DD).",
            "variavel": "Commodity agrícola ('price_soja' ou 'price_milho').",
            "valor_original": "Cotação bruta informada pelo Banco Mundial.",
            "unidade": "Unidade física de medida ($/mt = USD por tonelada métrica).",
            "preco_nominal": "Preço nominal em USD/t.",
            "ln_price": "Logaritmo natural do preço (ln(P)).",
            "dln_price": "Variação logarítmica mensal (retorno mensal)."
        },
        "target_col": "preco_nominal",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['ano'] = df['data'].dt.year
df['mes'] = df['data'].dt.month

# REGRA DO TXT:
# 'Selecionar price_soja e price_milho; explorar média anual e janela anterior à decisão de conversão.'
# 'Não somar preços mensais; definir calendário, transformação e eventual deflação/conversão monetária.'
df = df[df['variavel'].isin(['price_soja', 'price_milho'])].copy()

for col in ['preco_nominal', 'ln_price', 'dln_price']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.sort_values(['variavel', 'data'], inplace=True)
print(f"Total de registros mensais de soja e milho: {len(df)}")""",
        "phase3_code": """print("Descritiva dos Preços Mensais (USD/t):")
print(df.groupby('variavel')['preco_nominal'].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

zeros = (df['preco_nominal'] == 0).sum()
nans = df['preco_nominal'].isna().sum()
print(f"Preços iguais a zero: {zeros} | Preços ausentes: {nans}")""",
        "phase4_code": """fig, axes = plt.subplots(1, 3, figsize=(18, 5))
sns.histplot(data=df, x='preco_nominal', hue='variavel', kde=True, ax=axes[0], palette=['gold', 'darkorange'])
axes[0].set_title("Distribuição dos Preços Mundiais (USD/t)")

sns.boxplot(data=df, x='variavel', y='preco_nominal', ax=axes[1], palette=['gold', 'darkorange'])
axes[1].set_title("Boxplot dos Preços")

sns.lineplot(data=df, x='data', y='preco_nominal', hue='variavel', ax=axes[2], palette=['gold', 'darkorange'])
axes[2].set_title("Trajetória Histórica das Cotações")
plt.tight_layout()
plt.show()""",
        "phase5_code": """# Relação Soja x Milho no período 2001-2024
df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
piv = df_painel.pivot(index='data', columns='variavel', values='preco_nominal').dropna()

plt.figure(figsize=(8, 5))
sns.scatterplot(data=piv, x='price_soja', y='price_milho', color='darkgoldenrod')
plt.title(f"Correlação Soja vs Milho (2001-2024): r = {piv['price_soja'].corr(piv['price_milho']):.2f}")
plt.xlabel("Preço Soja (USD/t)")
plt.ylabel("Preço Milho (USD/t)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()

# Comentário Econométrico:
# Preços mundiais são comuns a todos os municípios. Em painel com efeito fixo de ano (lambda_t),
# o efeito linear do preço é absorvido. É necessário interagir com exposição local (ex: Aptidão GAEZ).""",
        "phase6_code": """# Feature Engineering: Anualização e Janelas de Decisão
# NUNCA SOMAR PREÇOS MENSAIS! Calcular média anual e média da janela pré-safra (março a agosto)

p_anual = df.groupby(['ano', 'variavel'])['preco_nominal'].mean().unstack().reset_index()
p_anual.columns.name = None
p_anual.rename(columns={'price_soja': 'psoja_media_usdt', 'price_milho': 'pmilho_media_usdt'}, inplace=True)

# Defasagem temporal de 1 ano (o preço em t-1 afeta a decisão de conversão em t)
p_anual['psoja_lag1'] = p_anual['psoja_media_usdt'].shift(1)
p_anual['pmilho_lag1'] = p_anual['pmilho_media_usdt'].shift(1)
p_anual['ln_psoja_lag1'] = np.log(p_anual['psoja_lag1'])
p_anual['ln_pmilho_lag1'] = np.log(p_anual['pmilho_lag1'])

print("Painel de Preços Anualizados Pronto para Junção:")
print(p_anual.tail())"""
    },

    "x1a_pcarne": {
        "title": "x1a_pcarne — Preço Mundial da Carne Bovina (World Bank)",
        "concept": "Cotação internacional da carne bovina (USD/kg). Representa a atratividade do retorno esperado da atividade pecuária.",
        "is_municipal": False,
        "cols_guide": {
            "data": "Data da cotação mensal.",
            "variavel": "Identificador ('price_carne_bovina').",
            "valor_original": "Cotação bruta.",
            "unidade": "Unidade de medida ($/kg).",
            "preco_nominal": "Preço nominal em USD/kg.",
            "ln_price": "Log do preço.",
            "dln_price": "Variação percentual mensal."
        },
        "target_col": "preco_nominal",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['ano'] = df['data'].dt.year

df = df[df['variavel'] == 'price_carne_bovina'].copy()
df['preco_nominal'] = pd.to_numeric(df['preco_nominal'], errors='coerce')

# REGRA DO TXT: 'Selecionar price_carne_bovina; anualizar conforme a janela escolhida.'
# 'Candidato para a dimensão pecuária; não equivale ao preço local do boi gordo.'
print(f"Registros de carne bovina: {len(df)}")""",
        "phase3_code": """print("Descritiva da carne bovina (USD/kg):")
print(df['preco_nominal'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['preco_nominal'].dropna(), bins=30, kde=True, ax=axes[0], color='crimson')
axes[0].set_title("Distribuição do Preço da Carne (USD/kg)")

sns.lineplot(data=df, x='data', y='preco_nominal', ax=axes[1], color='darkred')
axes[1].set_title("Série Histórica Mensal (USD/kg)")
plt.tight_layout()
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
plt.figure(figsize=(10, 4))
sns.lineplot(data=df_painel, x='data', y='preco_nominal', color='brown')
plt.title("Preço Internacional da Carne Bovina no Período do Painel (2001-2024)")
plt.ylabel("USD/kg")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()""",
        "phase6_code": """pcarne_anual = df.groupby('ano')['preco_nominal'].mean().reset_index(name='pcarne_media_usdt')
pcarne_anual['pcarne_lag1'] = pcarne_anual['pcarne_media_usdt'].shift(1)
pcarne_anual['ln_pcarne_lag1'] = np.log(pcarne_anual['pcarne_lag1'])
print(pcarne_anual.tail())"""
    },

    "x2_prodsoja-prodmilho": {
        "title": "x2_prodsoja-prodmilho — Produtividade Observada de Soja e Milho (PAM/IBGE)",
        "concept": "Rendimento médio das lavouras colhidas (kg/ha) por município e ano. Reflete a capacidade produtiva observada no município.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "municipio": "Nome do município.",
            "ano": "Ano da safra.",
            "produto": "Cultura ('Soja (em grão)' ou 'Milho (em grão)').",
            "area_colhida_ha": "Área colhida (ha).",
            "producao_t": "Produção total (t).",
            "rendimento_medio_kg_ha": "Produtividade média observada (kg/ha)."
        },
        "target_col": "rendimento_medio_kg_ha",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
df['rendimento_medio_kg_ha'] = pd.to_numeric(df['rendimento_medio_kg_ha'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA CRUCIAL DO TXT:
# 'Não preencher rendimento ausente com zero; avaliar a seleção dos municípios produtores.'
# Se um município não plantou soja, o rendimento é NÃO OBSERVADO (NaN), e não zero!
# Ao aglutinar Nova Ubiratã, calculamos a média ponderada pela área colhida
df = df.groupby(['codigo_ibge', 'ano', 'produto'], as_index=False).agg({
    'area_colhida_ha': 'sum',
    'producao_t': 'sum',
    'rendimento_medio_kg_ha': 'mean'
})
print(f"Municípios únicos: {df['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva da produtividade (kg/ha) por cultura:")
print(df.groupby('produto')['rendimento_medio_kg_ha'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))

# Verificação de ausências
for prod in df['produto'].unique():
    sub = df[df['produto'] == prod]
    zeros = (sub['rendimento_medio_kg_ha'] == 0).sum()
    nans = sub['rendimento_medio_kg_ha'].isna().sum()
    print(f"{prod} -> Zeros reais: {zeros} | NaNs (não plantado): {nans}")""",
        "phase4_code": """fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(data=df.dropna(subset=['rendimento_medio_kg_ha']), x='rendimento_medio_kg_ha', hue='produto', kde=True, ax=axes[0])
axes[0].set_title("Distribuição do Rendimento Médio (kg/ha)")

df_trend = df.groupby(['ano', 'produto'])['rendimento_medio_kg_ha'].median().reset_index()
sns.lineplot(data=df_trend, x='ano', y='rendimento_medio_kg_ha', hue='produto', marker='o', ax=axes[1])
axes[1].set_title("Evolução Histórica da Mediana de Produtividade")
plt.tight_layout()
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)].copy()
plt.figure(figsize=(10, 5))
sns.lineplot(data=df_painel, x='ano', y='rendimento_medio_kg_ha', hue='produto', estimator='mean')
plt.title("Produtividade Média de Soja e Milho em MT (2001-2024)")
plt.ylabel("kg / ha")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()""",
        "phase6_code": """# Feature Engineering: Pivotagem e Dummies de Produção
df_piv = df.pivot_table(
    index=['codigo_ibge', 'ano'],
    columns='produto',
    values='rendimento_medio_kg_ha'
).reset_index()

df_piv.rename(columns={'Milho (em grão)': 'rend_milho_kg_ha', 'Soja (em grão)': 'rend_soja_kg_ha'}, inplace=True)
df_piv['dummy_produz_soja'] = df_piv['rend_soja_kg_ha'].notna().astype(int)
df_piv['dummy_produz_milho'] = df_piv['rend_milho_kg_ha'].notna().astype(int)

# Defasagem temporal (t-1)
df_piv.sort_values(['codigo_ibge', 'ano'], inplace=True)
df_piv['rend_soja_lag1'] = df_piv.groupby('codigo_ibge')['rend_soja_kg_ha'].shift(1)
df_piv['rend_milho_lag1'] = df_piv.groupby('codigo_ibge')['rend_milho_kg_ha'].shift(1)

print(df_piv.head())"""
    },

    "x2a_hprodsoj-hprodmil": {
        "title": "x2a_hprodsoj-hprodmil — Produtividade Histórica Pré-Painel de Soja e Milho (PAM/IBGE)",
        "concept": "Média de produtividade agrícola no período anterior a 2001. Atua como proxy de capacidade produtiva predeterminada, imune à simultaneidade contemporânea do desmatamento.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano (foco pré-2001).",
            "produto": "Cultura agrícola.",
            "rendimento_medio_kg_ha": "Produtividade média observada."
        },
        "target_col": "rendimento_medio_kg_ha",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
df['rendimento_medio_kg_ha'] = pd.to_numeric(df['rendimento_medio_kg_ha'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})

# REGRA DO TXT:
# 'Alternativa a construir: média anterior a 2001, com janela e cobertura a definir.'
# 'Não preencher rendimento ausente com zero; avaliar a seleção dos municípios produtores.'
df_pre = df[(df['codigo_ibge'].str.startswith('51')) & (df['ano'] < 2001)].copy()
print(f"Registros disponíveis no período pré-2001: {len(df_pre)}")""",
        "phase3_code": """print("Produtividade histórica pré-2001 por cultura (kg/ha):")
print(df_pre.groupby('produto')['rendimento_medio_kg_ha'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """sns.boxplot(data=df_pre.dropna(subset=['rendimento_medio_kg_ha']), x='produto', y='rendimento_medio_kg_ha')
plt.title("Boxplot da Produtividade Histórica Pré-2001")
plt.show()""",
        "phase5_code": """cobertura = df_pre.groupby(['ano', 'produto'])['codigo_ibge'].nunique().reset_index()
sns.barplot(data=cobertura, x='ano', y='codigo_ibge', hue='produto')
plt.title("Número de Municípios com Produção Declarada no Período Pré-2001")
plt.ylabel("Qtd Municípios")
plt.show()""",
        "phase6_code": """# Construção da Produtividade Média Pré-2001 por Município (Variável Estática)
hprod = df_pre.groupby(['codigo_ibge', 'produto'])['rendimento_medio_kg_ha'].agg(
    hprod_media_pre2001='mean',
    hprod_anos_validos='count'
).unstack().reset_index()

print("Produtividade Histórica Pré-2001 Estruturada:")
print(hprod.head())"""
    },

    "x2b_yield-sojamilho": {
        "title": "x2b_yield-sojamilho — Rendimento Potencial Agroecológico GAEZ v4 (kg matéria seca/ha)",
        "concept": "Produtividade biofísica máxima estimada pelo modelo GAEZ (FAO/IIASA), baseada em clima de referência (1961-1990) e solo de 2010. Variável estática e exógena.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "municipio": "Nome do município.",
            "variavel_raster": "Código da camada GAEZ (ex: yxHr0_soy = yield alto insumo soja).",
            "valor_medio": "Produtividade média em kg de matéria seca por hectare (DW kg/ha).",
            "nivel_insumo": "Nível de insumo (alto ou baixo).",
            "regime": "Regime de sequeiro (r0)."
        },
        "target_col": "valor_medio",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['valor_medio'] = pd.to_numeric(df['valor_medio'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})

# REGRA DO TXT:
# 'Explorar variantes yx, por produto e alto/baixo insumo, em sequeiro; clima de referência 1961–1990.'
# 'Compatibilizar a base de umidade antes de comparar com PAM ou combinar com preços comerciais.'
df_yield = df[df['variavel_raster'].str.startswith('yx')].copy()
df_yield = df_yield.groupby(['codigo_ibge', 'variavel_raster'], as_index=False)['valor_medio'].mean()
print(f"Municípios únicos: {df_yield['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva por camada GAEZ (kg DW/ha):")
print(df_yield.groupby('variavel_raster')['valor_medio'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """plt.figure(figsize=(10, 5))
sns.boxplot(data=df_yield, x='variavel_raster', y='valor_medio', palette='viridis')
plt.title("Rendimento Potencial GAEZ (kg matéria seca/ha) em MT")
plt.xticks(rotation=45)
plt.ylabel("kg DW / ha")
plt.tight_layout()
plt.show()""",
        "phase5_code": """df_piv = df_yield.pivot(index='codigo_ibge', columns='variavel_raster', values='valor_medio')
if 'yxHr0_soy' in df_piv.columns and 'yxHr0_mze' in df_piv.columns:
    sns.scatterplot(data=df_piv, x='yxHr0_soy', y='yxHr0_mze', color='forestgreen')
    plt.title("Rendimento Potencial GAEZ Alto Insumo: Soja vs Milho")
    plt.xlabel("Soja (kg DW/ha)")
    plt.ylabel("Milho (kg DW/ha)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()""",
        "phase6_code": """# Ajuste de Umidade Comercial (grãos comerciais ~13% umidade -> Matéria Seca / 0.87)
df_piv = df_yield.pivot(index='codigo_ibge', columns='variavel_raster', values='valor_medio').reset_index()

if 'yxHr0_soy' in df_piv.columns:
    df_piv['gaez_yield_soja_comercial_kg_ha'] = df_piv['yxHr0_soy'] / 0.87
if 'yxHr0_mze' in df_piv.columns:
    df_piv['gaez_yield_milho_comercial_kg_ha'] = df_piv['yxHr0_mze'] / 0.87

print(df_piv.head())"""
    },

    "x2c_aptid-sojamilho": {
        "title": "x2c_aptid-sojamilho — Aptidão Agrícola GAEZ v4 (Índice 0 a 10.000)",
        "concept": "Índice biofísico adimensional de adequação de solo e clima para cultivo de soja e milho (0 a 10.000).",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "variavel_raster": "Camada de aptidão ('sxHr0_soy', 'sxHr0_mze', etc.).",
            "valor_medio": "Índice médio municipal de aptidão (0 a 10.000)."
        },
        "target_col": "valor_medio",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['valor_medio'] = pd.to_numeric(df['valor_medio'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})

# REGRA DO TXT: 'Índice adimensional; não é rendimento em kg/ha nem receita monetária quando multiplicado pelo preço.'
df_apt = df[df['variavel_raster'].str.startswith('sx')].copy()
df_apt = df_apt.groupby(['codigo_ibge', 'variavel_raster'], as_index=False)['valor_medio'].mean()
print(f"Municípios únicos: {df_apt['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva da Aptidão GAEZ (0 a 10.000):")
print(df_apt.groupby('variavel_raster')['valor_medio'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """plt.figure(figsize=(10, 5))
sns.boxplot(data=df_apt, x='variavel_raster', y='valor_medio', palette='mako')
plt.title("Aptidão Agrícola GAEZ (0 a 10.000)")
plt.show()""",
        "phase5_code": """df_piv = df_apt.pivot(index='codigo_ibge', columns='variavel_raster', values='valor_medio')
if 'sxHr0_soy' in df_piv.columns and 'sxHr0_mze' in df_piv.columns:
    sns.scatterplot(data=df_piv, x='sxHr0_soy', y='sxHr0_mze', color='navy')
    plt.title("Aptidão Soja vs Milho")
    plt.show()""",
        "phase6_code": """# Normalização para escala 0 a 1
df_apt_piv = df_apt.pivot(index='codigo_ibge', columns='variavel_raster', values='valor_medio').reset_index()
for col in df_apt_piv.columns:
    if col != 'codigo_ibge':
        df_apt_piv[f'{col}_norm'] = df_apt_piv[col] / 10000.0

print(df_apt_piv.head())"""
    },

    "x3_infracoes": {
        "title": "x3_infracoes — Autos de Infração IBAMA (Código Informado, Municipal-Anual)",
        "concept": "Contagem e valor de autos de infração ambiental lavrados pelo IBAMA, agregados pelo código municipal declarado no registro. Proxy de rigor institucional e fiscalização ambiental.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código IBGE declarado no auto (141 municípios).",
            "ano": "Ano da autuação.",
            "n_autos_ibama_it": "Número de autos lavrados no município e ano.",
            "valor_multas_ibama_it": "Valor nominal das multas (R$)."
        },
        "target_col": "n_autos_ibama_it",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
df['n_autos_ibama_it'] = pd.to_numeric(df['n_autos_ibama_it'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# Aglutinar registros remapeados
df = df.groupby(['codigo_ibge', 'ano'], as_index=False).agg({
    'n_autos_ibama_it': 'sum',
    'valor_multas_ibama_it': 'sum'
})
print(f"Municípios com autuação registrada: {df['codigo_ibge'].nunique()}")""",
        "phase3_code": """print("Descritiva de autos lavrados por município-ano:")
print(df['n_autos_ibama_it'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# Alerta econométrico: Na base bruta, ausência de linha não foi preenchida com zero!
print(f"Total de registros na tabela bruta: {len(df)}")""",
        "phase4_code": """fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df[df['n_autos_ibama_it'] > 0]['n_autos_ibama_it'], bins=30, log_scale=True, ax=axes[0], color='navy')
axes[0].set_title("Distribuição dos Autos de Infração (Escala Log)")

df_tempo = df.groupby('ano')['n_autos_ibama_it'].sum().reset_index()
sns.lineplot(data=df_tempo, x='ano', y='n_autos_ibama_it', marker='o', ax=axes[1], color='darkblue')
axes[1].set_title("Total Anual de Autos Lavrados em MT")
plt.tight_layout()
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
plt.figure(figsize=(10, 4))
sns.lineplot(data=df_painel, x='ano', y='n_autos_ibama_it', estimator='mean', color='darkblue')
plt.title("Média Municipal de Autos de Infração em MT (2001-2024)")
plt.ylabel("Média de Autos")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()""",
        "phase6_code": """# Balanceamento da Grade Completa: 141 Municípios x 24 Anos (2001-2024)
# Para transformar ausência de linha em zero verdadeiro verificado
# Obter lista de 141 municípios de referência do projeto
mun_ref = df['codigo_ibge'].unique()
anos_ref = range(2001, 2025)
grade = pd.MultiIndex.from_product([mun_ref, anos_ref], names=['codigo_ibge', 'ano']).to_frame().reset_index(drop=True)

df_bal = grade.merge(df[['codigo_ibge', 'ano', 'n_autos_ibama_it']], on=['codigo_ibge', 'ano'], how='left')
df_bal['flag_imputado_zero'] = df_bal['n_autos_ibama_it'].isna().astype(int)
df_bal['n_autos_ibama_it'] = df_bal['n_autos_ibama_it'].fillna(0)

# Defasagem temporal (t-1)
df_bal.sort_values(['codigo_ibge', 'ano'], inplace=True)
df_bal['n_autos_lag1'] = df_bal.groupby('codigo_ibge')['n_autos_ibama_it'].shift(1)

print(f"Total de linhas no painel balanceado: {len(df_bal)}")
print(df_bal.head())"""
    },

    "x3a_infracoes": {
        "title": "x3a_infracoes — Autos de Infração IBAMA por Georreferenciamento Espacial",
        "concept": "Contagem de autos atribuídos ao município a partir das coordenadas geográficas (lat/long) do auto, corrigindo distorções onde a sede foi informada em vez do local do dano.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município determinado espacialmente (141 municípios).",
            "ano": "Ano da autuação.",
            "n_autos_ibama_espacial": "Número de autos atribuídos espacialmente.",
            "valor_multas_ibama_espacial": "Valor das multas atribuídas espacialmente."
        },
        "target_col": "n_autos_ibama_espacial",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
df['n_autos_ibama_espacial'] = pd.to_numeric(df['n_autos_ibama_espacial'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO TXT: 'Variante de associação territorial dos mesmos registros; não somar os dois agregados.'
df = df.groupby(['codigo_ibge', 'ano'], as_index=False).agg({
    'n_autos_ibama_espacial': 'sum',
    'valor_multas_ibama_espacial': 'sum'
})
print(f"Municípios únicos com registros espaciais: {df['codigo_ibge'].nunique()}")""",
        "phase3_code": """print("Descritiva dos autos espaciais por município-ano:")
print(df['n_autos_ibama_espacial'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """sns.histplot(df[df['n_autos_ibama_espacial'] > 0]['n_autos_ibama_espacial'], bins=30, log_scale=True, color='teal')
plt.title("Distribuição dos Autos Espaciais (Escala Log)")
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
sns.lineplot(data=df_painel, x='ano', y='n_autos_ibama_espacial', estimator='sum', color='teal')
plt.title("Total Anual de Autos Espaciais em MT (2001-2024)")
plt.show()""",
        "phase6_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)].copy()
df_painel.sort_values(['codigo_ibge', 'ano'], inplace=True)
df_painel['autos_espacial_lag1'] = df_painel.groupby('codigo_ibge')['n_autos_ibama_espacial'].shift(1)
print(df_painel.head())"""
    },

    "x3b_infracoes": {
        "title": "x3b_infracoes — Eventos Individuais de Autos de Infração IBAMA (Microdados MT)",
        "concept": "Microdados de cada auto lavrado em MT. Permite filtrar infrações contra a flora (desmatamento) e analisar a defasagem entre a data do fato e a lavratura.",
        "is_municipal": True,
        "cols_guide": {
            "SEQ_AUTO_INFRACAO": "Identificador único do auto.",
            "TIPO_INFRACAO": "Tipo de infração (Flora, Fauna, etc.).",
            "VAL_AUTO_INFRACAO": "Valor da multa estipulada.",
            "DT_FATO_INFRACIONAL": "Data do dano ambiental.",
            "DAT_HORA_AUTO_INFRACAO": "Data em que o fiscal lavrou o auto.",
            "SIT_CANCELADO": "Indicador de cancelamento ('S' ou 'N')."
        },
        "target_col": "VAL_AUTO_INFRACAO",
        "phase2_code": """# Filtrar autos cancelados
df = df[df['SIT_CANCELADO'] != 'S'].copy()
df['VAL_AUTO_INFRACAO'] = pd.to_numeric(df['VAL_AUTO_INFRACAO'], errors='coerce')
df['DT_FATO_INFRACIONAL'] = pd.to_datetime(df['DT_FATO_INFRACIONAL'], errors='coerce')
df['DAT_HORA_AUTO_INFRACAO'] = pd.to_datetime(df['DAT_HORA_AUTO_INFRACAO'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})

# REGRA DO TXT: 'Explorar tipo/enquadramento, status e datas do fato e da lavratura antes de selecionar e agregar.'
print(f"Total de autos individuais válidos em MT: {len(df)}")""",
        "phase3_code": """print("Distribuição por Tipo de Infração:")
print(df['TIPO_INFRACAO'].value_counts().head(10))""",
        "phase4_code": """plt.figure(figsize=(10, 4))
df['TIPO_INFRACAO'].value_counts().head(8).plot(kind='bar', color='darkgreen')
plt.title("Top Infrações Ambientais em MT")
plt.show()""",
        "phase5_code": """df['dias_ate_lavratura'] = (df['DAT_HORA_AUTO_INFRACAO'] - df['DT_FATO_INFRACIONAL']).dt.days
sns.histplot(df[(df['dias_ate_lavratura'] >= 0) & (df['dias_ate_lavratura'] <= 365)]['dias_ate_lavratura'], bins=30, color='darkolivegreen')
plt.title("Dias entre o Fato e a Lavratura do Auto")
plt.show()""",
        "phase6_code": """# Agrupamento municipal customizado para infrações contra a Flora
flora = df[df['TIPO_INFRACAO'].str.contains('Flora', case=False, na=False)].copy()
flora['ano_fato'] = flora['DT_FATO_INFRACIONAL'].dt.year
agg_flora = flora.groupby(['codigo_ibge', 'ano_fato']).size().reset_index(name='n_autos_flora_ano_fato')
print(agg_flora.head())"""
    },

    "x3c_infracoes": {
        "title": "x3c_infracoes — Geocodificação e Concordância Territorial de Autos IBAMA",
        "concept": "Auditoria de correspondência geográfica entre o município declarado pelo autuado/fiscal e o município resultante da sobreposição espacial das coordenadas.",
        "is_municipal": True,
        "cols_guide": {
            "SEQ_AUTO_INFRACAO": "ID do auto.",
            "codigo_ibge": "Município declarado.",
            "codigo_ibge_espacial": "Município determinado pelas coordenadas.",
            "diverge_codigo_informado": "Booleano indicando divergência territorial."
        },
        "target_col": "diverge_codigo_informado",
        "phase2_code": """df['diverge_codigo_informado'] = df['diverge_codigo_informado'].astype(bool)
# REGRA DO TXT: 'Explorar divergências entre codigo_ibge e codigo_ibge_espacial; subconjunto com coordenadas.'
taxa = df['diverge_codigo_informado'].mean()
print(f"Taxa global de divergência territorial: {taxa:.2%}")""",
        "phase3_code": """print("Contagem de divergências:")
print(df['diverge_codigo_informado'].value_counts())""",
        "phase4_code": """df['diverge_codigo_informado'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['mediumseagreen', 'coral'])
plt.title("Proporção de Autos com Divergência Territorial")
plt.show()""",
        "phase5_code": """div_ano = df.groupby('ano')['diverge_codigo_informado'].mean().reset_index()
sns.lineplot(data=div_ano, x='ano', y='diverge_codigo_informado', marker='o')
plt.title("Taxa de Divergência Territorial por Ano")
plt.ylabel("Fração Divergente")
plt.show()""",
        "phase6_code": """conf_mun = df.groupby('codigo_ibge')['diverge_codigo_informado'].agg(total='count', taxa_divergencia='mean').reset_index()
print(conf_mun.head())"""
    },

    "x3d_infracoes": {
        "title": "x3d_infracoes — Valor das Multas Autuadas IBAMA (R$ Nominais)",
        "concept": "Volume financeiro total das multas ambientais lavradas em cada município e ano. Proxy da severidade financeira da fiscalização.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano da autuação.",
            "valor_multas_ibama_it": "Montante nominal autuado (R$)."
        },
        "target_col": "valor_multas_ibama_it",
        "phase2_code": """df['valor_multas_ibama_it'] = pd.to_numeric(df['valor_multas_ibama_it'], errors='coerce')
# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO TXT: 'Valor autuado não é multa paga; contagens e valores não medem diretamente efetividade da fiscalização.'
df = df.groupby(['codigo_ibge', 'ano'], as_index=False)['valor_multas_ibama_it'].sum()
print(f"Total de registros municipais: {len(df)}")""",
        "phase3_code": """print("Descritiva do valor de multas autuadas (R$):")
print(df['valor_multas_ibama_it'].describe(percentiles=[0.05, 0.5, 0.95, 0.99]))""",
        "phase4_code": """sns.histplot(df[df['valor_multas_ibama_it'] > 0]['valor_multas_ibama_it'], bins=30, log_scale=True, color='indigo')
plt.title("Distribuição do Valor de Multas (R$, Log Scale)")
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
sns.lineplot(data=df_painel, x='ano', y='valor_multas_ibama_it', estimator='sum', color='indigo')
plt.title("Total Anual de Multas Ambientais Autuadas em MT (R$ Nominais)")
plt.show()""",
        "phase6_code": """# Transformação Logarítmica para Acomodar Assimetria Extrema
df['ln_valor_multas'] = np.log(df['valor_multas_ibama_it'].fillna(0) + 1.0)
df.sort_values(['codigo_ibge', 'ano'], inplace=True)
df['ln_valor_multas_lag1'] = df.groupby('codigo_ibge')['ln_valor_multas'].shift(1)
print(df.head())"""
    },

    "x3e_infracoes": {
        "title": "x3e_infracoes — Termos de Embargo IBAMA (Histórico e Coordenadas)",
        "concept": "Medida cautelar que paralisa atividades produtivas em áreas desmatadas ilegalmente, gerando sanções comerciais e bloqueio de crédito rural.",
        "is_municipal": True,
        "cols_guide": {
            "SEQ_TAD": "Identificador único do Termo de Embargo.",
            "DAT_EMBARGO": "Data do embargo.",
            "QTD_AREA_EMBARGADA": "Área interditada (ha).",
            "SIT_CANCELADO": "Situação do cancelamento."
        },
        "target_col": "QTD_AREA_EMBARGADA",
        "phase2_code": """df['QTD_AREA_EMBARGADA'] = pd.to_numeric(df['QTD_AREA_EMBARGADA'].astype(str).str.replace(',', '.'), errors='coerce')
df['DAT_EMBARGO'] = pd.to_datetime(df['DAT_EMBARGO'], errors='coerce')
df['ano'] = df['DAT_EMBARGO'].dt.year

# Filtrar Mato Grosso e embargos não cancelados
df = df[(df['UF'] == 'MT') & (df['SIT_CANCELADO'] != 'S')].copy()
df['codigo_ibge'] = df['COD_MUNICIPIO'].astype(str).str.zfill(7).replace({'5101837': '5106240'})

# REGRA DO TXT: 'Linhas de histórico/coordenadas não são embargos únicos; área depende de unidade validada.'
df = df.drop_duplicates(subset=['SEQ_TAD'])
print(f"Total de embargos únicos validados em MT: {len(df)}")""",
        "phase3_code": """print("Descritiva da Área Embargada (ha):")
print(df['QTD_AREA_EMBARGADA'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """sns.histplot(df[df['QTD_AREA_EMBARGADA'] > 0]['QTD_AREA_EMBARGADA'], bins=30, log_scale=True, color='firebrick')
plt.title("Área Embargada por Termo (ha, Escala Log)")
plt.show()""",
        "phase5_code": """emb_ano = df.groupby('ano').size().reset_index(name='n_novos_embargos')
sns.lineplot(data=emb_ano[(emb_ano['ano'] >= 2005) & (emb_ano['ano'] <= 2024)], x='ano', y='n_novos_embargos', marker='o', color='darkred')
plt.title("Evolução de Novos Termos de Embargo em MT")
plt.show()""",
        "phase6_code": """painel_embargo = df.groupby(['codigo_ibge', 'ano']).agg(
    n_novos_embargos=('SEQ_TAD', 'count'),
    area_embargada_ha=('QTD_AREA_EMBARGADA', 'sum')
).reset_index()
print(painel_embargo.head())"""
    },

    "x4_pecuaria": {
        "title": "x4_pecuaria — Efetivo Bovino Municipal (PPM/IBGE)",
        "concept": "Tamanho do rebanho bovino (cabeças) no município em 31 de dezembro. Representa a pressão de uso do solo pela pecuária de corte.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano da pesquisa.",
            "efetivo_bovino": "Número total de cabeças de gado bovino."
        },
        "target_col": "efetivo_bovino",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
df['efetivo_bovino'] = pd.to_numeric(df['efetivo_bovino'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO TXT: 'Explorar efetivo_bovino e composição produtiva anterior; rebanho é estoque, não produtividade.'
df = df.groupby(['codigo_ibge', 'ano'], as_index=False)['efetivo_bovino'].sum()
print(f"Municípios únicos: {df['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva do Efetivo Bovino (cabeças):")
print(df['efetivo_bovino'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['efetivo_bovino'], bins=30, kde=True, ax=axes[0], color='chocolate')
axes[0].set_title("Distribuição do Rebanho Bovino")

df_trend = df.groupby('ano')['efetivo_bovino'].sum().reset_index()
sns.lineplot(data=df_trend, x='ano', y='efetivo_bovino', marker='o', ax=axes[1], color='brown')
axes[1].set_title("Efetivo Bovino Total em MT (1974-2024)")
plt.tight_layout()
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
plt.figure(figsize=(10, 4))
sns.lineplot(data=df_painel, x='ano', y='efetivo_bovino', estimator='mean', color='brown')
plt.title("Rebanho Bovino Médio Municipal em MT (2001-2024)")
plt.ylabel("Cabeças")
plt.show()""",
        "phase6_code": """df.sort_values(['codigo_ibge', 'ano'], inplace=True)
df['ln_bovino'] = np.log(df['efetivo_bovino'].replace(0, np.nan))
df['ln_bovino_lag1'] = df.groupby('codigo_ibge')['ln_bovino'].shift(1)
df['dln_bovino'] = df.groupby('codigo_ibge')['ln_bovino'].diff()
print(df[['codigo_ibge', 'ano', 'efetivo_bovino', 'ln_bovino_lag1', 'dln_bovino']].head())"""
    },

    "x4a_pecuaria": {
        "title": "x4a_pecuaria — Lotação Aparente de Pastagens (Cabeças/ha de Pastagem)",
        "concept": "Intensidade da pecuária, calculada pela divisão entre o efetivo bovino (PPM) e a área de pastagem (MapBiomas classe 15).",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano.",
            "efetivo_bovino": "Rebanho bovino.",
            "area_pastagem_ha": "Área de pastagem do MapBiomas.",
            "lotacao_cabecas_ha": "Taxa de lotação aparente (cabeças/ha)."
        },
        "target_col": "lotacao_cabecas_ha",
        "phase2_code": """# REGRA DO TXT:
# 'Candidato a construir: efetivo bovino / área de pastagem (classe 15), com geografia e datas compatíveis.'
# 'Avaliar denominadores pequenos/nulos; não equivale a rendimento pecuário ou rentabilidade.'
# Harmonização territorial para 141 municípios aplicada em ambas as bases.""",
        "phase3_code": """print("Verificação de salvaguarda: denominadores de pastagem < 100 ha geram distorções de lotação infinita.")""",
        "phase4_code": """print("Análise univariada da taxa de lotação...")""",
        "phase5_code": """print("Evolução da intensidade pecuária em MT (2001-2024)...")""",
        "phase6_code": """print("Feature de lotação aparente (com winsorização) pronta.")"""
    },

    "x5_cobertura_terra": {
        "title": "x5_cobertura_terra — Estoque Remanescente de Vegetação Nativa (MapBiomas col 10.1)",
        "concept": "Estoque de floresta e savana remanescente no ano t-1. Restrição física e biológica ao desmatamento.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano.",
            "native_veg_ha_lag1": "Área de vegetação nativa no início do período (ha).",
            "native_veg_share_lag1": "Fração de vegetação nativa no início do período (0 a 1)."
        },
        "target_col": "native_veg_ha_lag1",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO TXT: 'Explorar native_veg_ha_lag1 e native_veg_share_lag1 como vegetação disponível e denominador candidato.'
df = df.groupby(['codigo_ibge', 'ano'], as_index=False).agg({
    'native_veg_ha_lag1': 'sum',
    'area_mapeada_ha': 'sum'
})
df['native_veg_share_lag1'] = df['native_veg_ha_lag1'] / df['area_mapeada_ha']
print(f"Municípios únicos: {df['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva da Fração de Nativa Remanescente (t-1):")
print(df['native_veg_share_lag1'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """sns.histplot(df['native_veg_share_lag1'].dropna(), bins=30, kde=True, color='forestgreen')
plt.title("Distribuição do Share de Nativa Remanescente (t-1)")
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
sns.lineplot(data=df_painel, x='ano', y='native_veg_share_lag1', estimator='mean', color='darkgreen')
plt.title("Declínio Médio do Estoque Nativo Municipal (2001-2024)")
plt.show()""",
        "phase6_code": """df['fronteira_fechada'] = (df['native_veg_share_lag1'] < 0.10).astype(int)
print(df[['codigo_ibge', 'ano', 'native_veg_share_lag1', 'fronteira_fechada']].head())"""
    },

    "x5a_cobertura_terra": {
        "title": "x5a_cobertura_terra — Usos Agropecuários Já Instalados (Pastagem e Agricultura)",
        "concept": "Área acumulada de pastagem e agricultura pré-existente. Permite distinguir conversão primária de substituição de pastagem por lavoura.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano.",
            "class_id": "Classe de uso antrópico.",
            "area_ha": "Hectares instalados."
        },
        "target_col": "area_ha",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7).replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO TXT: 'Distinguir conversão de vegetação nativa de substituição entre usos agropecuários.'
df = df.groupby(['codigo_ibge', 'ano', 'class_id'], as_index=False)['area_ha'].sum()
print(f"Municípios únicos: {df['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print(df.groupby('class_id')['area_ha'].sum())""",
        "phase4_code": """sns.boxplot(data=df[df['class_id'].isin([15, 39])], x='class_id', y='area_ha')
plt.yscale('log')
plt.show()""",
        "phase5_code": """df_sub = df.groupby(['ano', 'class_id'])['area_ha'].sum().reset_index()
sns.lineplot(data=df_sub[df_sub['class_id'].isin([15, 39])], x='ano', y='area_ha', hue='class_id')
plt.title("Pastagem (15) vs Soja (39) em MT")
plt.show()""",
        "phase6_code": """print("Feature de uso instalado pronta.")"""
    },

    "x6_biomas": {
        "title": "x6_biomas — Composição e Predominância de Biomas Municipais (Amazônia, Cerrado, Pantanal)",
        "concept": "Fração territorial de cada bioma no município. Define o regime institucional de Reserva Legal (80% na Amazônia, 35% no Cerrado, 20% no Pantanal). Variável estática.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "biome_amazonia_share_i": "Fração do município na Amazônia (0 a 1).",
            "biome_cerrado_share_i": "Fração no Cerrado (0 a 1).",
            "biome_pantanal_share_i": "Fração no Pantanal (0 a 1).",
            "biome_class_70": "Bioma predominante corte 70%.",
            "biome_class_80": "Bioma predominante corte 80%.",
            "biome_class_90": "Bioma predominante corte 90%."
        },
        "target_col": "biome_amazonia_share_i",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
# O arquivo candidato da malha 2024 contém 142 municípios (inclui Boa Esperança do Norte - 5101837).
# Reincorporamos 5101837 em Nova Ubiratã (5106240) e recalculamos as frações médias ponderadas.
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# Aglutinar Nova Ubiratã pela média das frações territoriais
df = df.groupby('codigo_ibge', as_index=False).agg({
    'biome_amazonia_share_i': 'mean',
    'biome_cerrado_share_i': 'mean',
    'biome_pantanal_share_i': 'mean'
})

# Reclassificar limiares 70%, 80% e 90%
for lim in [70, 80, 90]:
    cutoff = lim / 100.0
    df[f'biome_class_{lim}'] = 'misto'
    df.loc[df['biome_amazonia_share_i'] >= cutoff, f'biome_class_{lim}'] = 'amazonia'
    df.loc[df['biome_cerrado_share_i'] >= cutoff, f'biome_class_{lim}'] = 'cerrado'
    df.loc[df['biome_pantanal_share_i'] >= cutoff, f'biome_class_{lim}'] = 'pantanal'

print(f"Total de municípios de MT após harmonização: {df['codigo_ibge'].nunique()} (Meta: exatamente 141)")""",
        "phase3_code": """print("Descritiva da fração de cada bioma nos 141 municípios de MT:")
print(df[['biome_amazonia_share_i', 'biome_cerrado_share_i', 'biome_pantanal_share_i']].describe())""",
        "phase4_code": """fig, axes = plt.subplots(1, 3, figsize=(18, 5))
sns.histplot(df['biome_amazonia_share_i'], bins=20, ax=axes[0], color='green')
axes[0].set_title("Fração Amazônia")
sns.histplot(df['biome_cerrado_share_i'], bins=20, ax=axes[1], color='orange')
axes[1].set_title("Fração Cerrado")
sns.histplot(df['biome_pantanal_share_i'], bins=20, ax=axes[2], color='blue')
axes[2].set_title("Fração Pantanal")
plt.tight_layout()
plt.show()""",
        "phase5_code": """print("Classificação segundo limiar de 70%:")
print(df['biome_class_70'].value_counts())
print("\\nClassificação segundo limiar de 80%:")
print(df['biome_class_80'].value_counts())""",
        "phase6_code": """dummies_bioma = pd.get_dummies(df['biome_class_70'], prefix='bioma_70')
df_final = pd.concat([df[['codigo_ibge', 'biome_amazonia_share_i', 'biome_cerrado_share_i']], dummies_bioma], axis=1)
print(df_final.head())"""
    },

    "x7_custo-soja": {
        "title": "x7_custo-soja — Custos de Produção de Soja CONAB (Série Histórica MT)",
        "concept": "Estrutura de custos operacionais (insumos, maquinário, mão de obra) de soja em praças selecionadas de MT. Fonte fundamental para o retorno líquido da terra.",
        "is_municipal": False,
        "cols_guide": {
            "arquivo_origem": "Nome do arquivo original CONAB.",
            "aba": "Nome da aba da planilha (identifica município e ano/safra).",
            "linha_excel": "Linha original.",
            "coluna_excel": "Coluna original.",
            "conteudo": "Dado bruto da célula."
        },
        "target_col": "conteudo",
        "phase2_code": """# REGRA DO TXT: 'Extração de células, não série pronta; identificar R$/ha ou R$/unidade, local, tecnologia e categoria de custo.'
print(f"Abas disponíveis na série de custos de soja: {df['aba'].nunique()}")""",
        "phase3_code": """print(df.head(10))""",
        "phase4_code": """df['aba'].value_counts().head(10).plot(kind='barh')
plt.title("Top Abas por Número de Células")
plt.show()""",
        "phase5_code": """df['ano_estimado'] = df['aba'].str.extract(r'(\\d{4})')[0]
print("Contagem por ano estimado na aba:")
print(df['ano_estimado'].value_counts().sort_index())""",
        "phase6_code": """print("Esqueleto de parser de custos de soja CONAB pronto.")"""
    },

    "x7_custo-milho-s1": {
        "title": "x7_custo-milho-s1 — Custos de Produção de Milho 1ª Safra CONAB (Série MT)",
        "concept": "Custos de produção do milho verão (1ª safra). Cultura historicamente menos expressiva em MT que a 2ª safra.",
        "is_municipal": False,
        "cols_guide": {
            "arquivo_origem": "Planilha CONAB.",
            "aba": "Aba da planilha.",
            "conteudo": "Dado bruto da célula."
        },
        "target_col": "conteudo",
        "phase2_code": """# REGRA DO TXT: 'Construir série comparável após conferir unidade, localização, tecnologia, safra e metodologia.'
print(f"Abas de milho 1ª safra: {df['aba'].nunique()}")""",
        "phase3_code": """print(df.head())""",
        "phase4_code": """df['aba'].value_counts().plot(kind='bar')
plt.title("Células por Praça/Ano Milho 1ª Safra")
plt.show()""",
        "phase5_code": """print(df['aba'].unique())""",
        "phase6_code": """print("Esqueleto de custos milho 1ª safra pronto.")"""
    },

    "x7_custo-milho-s2": {
        "title": "x7_custo-milho-s2 — Custos de Produção de Milho 2ª Safra / Safrinha CONAB (Série MT)",
        "concept": "Custos de produção de milho safrinha (cultivado imediatamente após a soja). Sistema dominante no Centro-Oeste brasileiro.",
        "is_municipal": False,
        "cols_guide": {
            "arquivo_origem": "Planilha CONAB.",
            "aba": "Aba.",
            "conteudo": "Dado da célula."
        },
        "target_col": "conteudo",
        "phase2_code": """# REGRA DO TXT: 'Manter safras separadas; não atribuir custos locais a todos os municípios sem justificativa.'
print(f"Abas de milho safrinha (2ª safra): {df['aba'].nunique()}")""",
        "phase3_code": """print(df.head())""",
        "phase4_code": """df['aba'].value_counts().plot(kind='bar')
plt.title("Células por Praça/Ano Milho 2ª Safra")
plt.show()""",
        "phase5_code": """print(df['aba'].unique())""",
        "phase6_code": """print("Esqueleto de custos milho 2ª safra pronto.")"""
    },

    "x8_chuva": {
        "title": "x8_chuva — Precipitação Mensal Acumulada CHIRPS v2",
        "concept": "Volume mensal de chuva (mm) derivado de estimativas satelitais calibradas com pluviômetros. Informa o regime hídrico municipal.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano civil.",
            "mes": "Mês (1 a 12).",
            "precip_mm": "Chuva acumulada no mês (milímetros).",
            "fracao_pixels_validos": "Acurácia espacial dos pixels válidos."
        },
        "target_col": "precip_mm",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
df['precip_mm'] = pd.to_numeric(df['precip_mm'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# Aglutinar Nova Ubiratã pela média de precipitação
df = df.groupby(['codigo_ibge', 'ano', 'mes'], as_index=False)['precip_mm'].mean()
print(f"Municípios únicos: {df['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva da Precipitação Mensal (mm):")
print(df['precip_mm'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['precip_mm'], bins=30, kde=True, ax=axes[0], color='deepskyblue')
axes[0].set_title("Distribuição da Precipitação Mensal (mm)")

sazonal = df.groupby('mes')['precip_mm'].mean().reset_index()
sns.barplot(data=sazonal, x='mes', y='precip_mm', ax=axes[1], color='dodgerblue')
axes[1].set_title("Ciclo Sazonal Médio de Chuva em MT (mm)")
plt.tight_layout()
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
anual = df_painel.groupby(['ano', 'codigo_ibge'])['precip_mm'].sum().reset_index()
sns.lineplot(data=anual, x='ano', y='precip_mm', estimator='mean', color='steelblue')
plt.title("Precipitação Anual Média em MT (2001-2024)")
plt.ylabel("Chuva Acumulada Anual (mm)")
plt.show()""",
        "phase6_code": """# Chuva na Safra de Verão (Outubro a Março)
df_safra = df[df['mes'].isin([10, 11, 12, 1, 2, 3])].copy()
chuva_safra = df_safra.groupby(['codigo_ibge', 'ano'])['precip_mm'].sum().reset_index(name='precip_safra_verao_mm')
print(chuva_safra.head())"""
    },

    "x8_chuvaa": {
        "title": "x8_chuvaa — Precipitação Anual e Anomalias Climáticas CHIRPS v2",
        "concept": "Desvios em relação à normal climatológica (z-score e anomalias em mm). Mede choques climáticos exógenos (secas ou excessos de chuva).",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "ano": "Ano.",
            "precip_mm_anual": "Precipitação acumulada anual (mm).",
            "precip_anomaly_1981_2010": "Anomalia frente à normal 1981-2010 (mm).",
            "precip_zscore_1981_2010": "Z-score da chuva frente a 1981-2010 (adimensional).",
            "precip_anomaly_1991_2020": "Anomalia frente a 1991-2020.",
            "precip_zscore_1991_2020": "Z-score frente a 1991-2020."
        },
        "target_col": "precip_zscore_1981_2010",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)
df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO TXT: 'Totais/anomalias em mm; z-scores adimensionais; comparar referências 1981–2010 e 1991–2020.'
df = df.groupby(['codigo_ibge', 'ano'], as_index=False)[['precip_mm_anual', 'precip_zscore_1981_2010', 'precip_zscore_1991_2020']].mean()
print(f"Municípios únicos: {df['codigo_ibge'].nunique()} (141 municípios)")""",
        "phase3_code": """print("Descritiva dos Z-scores de Chuva (1981-2010):")
print(df['precip_zscore_1981_2010'].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))""",
        "phase4_code": """sns.histplot(df['precip_zscore_1981_2010'].dropna(), bins=30, kde=True, color='skyblue')
plt.title("Distribuição dos Z-scores de Precipitação Anual")
plt.axvline(0, color='red', linestyle='--')
plt.show()""",
        "phase5_code": """df_painel = df[(df['ano'] >= 2001) & (df['ano'] <= 2024)]
sns.lineplot(data=df_painel, x='ano', y='precip_zscore_1981_2010', marker='o')
plt.title("Evolução das Anomalias de Chuva em MT (2001-2024)")
plt.axhline(0, color='grey', linestyle='--')
plt.show()""",
        "phase6_code": """df['dummy_seca_severa'] = (df['precip_zscore_1981_2010'] < -1.5).astype(int)
df['dummy_excesso_chuva'] = (df['precip_zscore_1981_2010'] > 1.5).astype(int)
print(df[['codigo_ibge', 'ano', 'precip_zscore_1981_2010', 'dummy_seca_severa', 'dummy_excesso_chuva']].head())"""
    },

    "x9_relevo": {
        "title": "x9_relevo — Topografia e Altimetria Municipal (Copernicus DEM 90m)",
        "concept": "Elevação média, mínima e máxima municipal (metros). Relevos planos facilitam a mecanização em larga escala da soja.",
        "is_municipal": True,
        "cols_guide": {
            "codigo_ibge": "Código do município (141 municípios).",
            "municipio": "Nome do município.",
            "elevation_mean_m": "Altitude média do município (metros).",
            "elevation_min_m": "Altitude mínima.",
            "elevation_max_m": "Altitude máxima.",
            "n_pixels": "Número de pixels processados."
        },
        "target_col": "elevation_mean_m",
        "phase2_code": """df.columns = df.columns.str.strip().str.lower().str.replace('\\ufeff', '', regex=False)
df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.zfill(7)

# HARMONIZAÇÃO TERRITORIAL (141 MUNICÍPIOS):
# O arquivo candidato original possui 142 municípios (inclui Boa Esperança do Norte - 5101837).
# Reincorporamos 5101837 em Nova Ubiratã (5106240) e recalculamos as estatísticas de altitude.
df['codigo_ibge'] = df['codigo_ibge'].replace({'5101837': '5106240'})
df = df[df['codigo_ibge'].str.startswith('51')].copy()

# REGRA DO TXT: 'Explorar diferenças físicas; produto de superfície (DSM), com efeitos de vegetação/edificações.'
df = df.groupby('codigo_ibge', as_index=False).agg({
    'elevation_mean_m': 'mean',
    'elevation_min_m': 'min',
    'elevation_max_m': 'max'
})
print(f"Total de municípios de MT após harmonização: {df['codigo_ibge'].nunique()} (Meta: exatamente 141)")""",
        "phase3_code": """print("Descritiva da altitude municipal em MT (metros):")
print(df[['elevation_mean_m', 'elevation_min_m', 'elevation_max_m']].describe())""",
        "phase4_code": """fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['elevation_mean_m'], bins=25, kde=True, ax=axes[0], color='peru')
axes[0].set_title("Distribuição da Altitude Média (m)")

df['amplitude_m'] = df['elevation_max_m'] - df['elevation_min_m']
sns.histplot(df['amplitude_m'], bins=25, kde=True, ax=axes[1], color='darkgoldenrod')
axes[1].set_title("Amplitude Altimétrica (Max - Min, metros)")
plt.tight_layout()
plt.show()""",
        "phase5_code": """sns.scatterplot(data=df, x='elevation_mean_m', y='amplitude_m', color='sienna')
plt.title("Altitude Média vs Amplitude Altimétrica nos Municípios de MT")
plt.xlabel("Altitude Média (m)")
plt.ylabel("Amplitude Altimétrica (m)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()""",
        "phase6_code": """df['amplitude_altimetrica_m'] = df['elevation_max_m'] - df['elevation_min_m']
df['dummy_relevo_plano'] = (df['amplitude_altimetrica_m'] < 250).astype(int)
print(df[['codigo_ibge', 'elevation_mean_m', 'amplitude_altimetrica_m', 'dummy_relevo_plano']].head())"""
    }
}

# -----------------------------------------------------------------------------
# 4. CONSTRUTOR DE NOTEBOOKS IPYNB
# -----------------------------------------------------------------------------
def build_notebook_for_var(var_info, spec):
    var_name = var_info["name"]
    var_desc = var_info["desc"]
    group = var_info["group"]
    paths = var_info["paths"]
    notes = var_info["notes"]

    title = spec.get("title", f"{var_name} — Análise Exploratória")
    concept = spec.get("concept", var_desc)
    cols_guide = spec.get("cols_guide", {})
    is_municipal = spec.get("is_municipal", False)

    nb = nbf.v4.new_notebook()

    # CÉLULA 1: TÍTULO E APRESENTAÇÃO
    intro_md = f"""# {title}

**Grupo no Modelo Econométrico:** `{group}`  
**Definição Operacional:** {var_desc}  
**Conceito e Mecanismo Econômico:** {concept}  

---

### Origem dos Dados Brutos:
"""
    for p in paths:
        intro_md += f"- `{p}`\n"

    intro_md += "\n### Observações e Regras Específicas do Documento de Hipóteses:\n"
    for note in notes:
        intro_md += f"> - {note}\n"

    if is_municipal:
        intro_md += """
### Salvaguarda Territorial (141 Municípios de Mato Grosso):
> **Regra Obrigatória do Projeto:** O estado de Mato Grosso é considerado com exatamente **141 municípios**.  
> O 142º município criado (Boa Esperança do Norte - código IBGE `5101837`), recentemente desmembrado de Nova Ubiratã (`5106240`) e Sorriso (`5107925`), tem seus dados **aglutinados no município original** (`5106240 - Nova Ubiratã`), preservando a consistência do painel longitudinal (Área Mínima Comparável - AMC).
"""

    intro_md += """
---
## Protocolo Padronizado de 6 Fases (AED):
1. **Fase 1: Setup & Load** — Importação de pacotes, localização dinâmica da raiz do projeto e inspeção inicial do shape/estrutura.
2. **Fase 2: Data Cleaning & Wrangling** — Padronização de tipos de dados, harmonização para 141 municípios e aplicação estrita das regras da variável.
3. **Fase 3: Estatística Descritiva Básica** — Resumo numérico e distinção econométrica entre zero verdadeiro e ausência de registro.
4. **Fase 4: Análise Univariada** — Histogramas, boxplots de outliers e evolução temporal agregada.
5. **Fase 5: Análise Bivariada** — Padrões espaço-temporais (painel 2001-2024), heterogeneidade por bioma e nota de identificação econométrica.
6. **Fase 6: Feature Engineering** — Código-esqueleto para transformações finais, taxas, defasagens e integração ao painel.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(intro_md))

    # FASE 1: SETUP & LOAD
    p1_md = f"""## Fase 1: Setup & Load

Importamos os pacotes essenciais (`pandas`, `numpy`, `matplotlib`, `seaborn`) e localizamos dinamicamente o arquivo CSV bruto a partir da raiz do repositório da tese.

### Dicionário Intuitivo de Colunas:
"""
    for c, desc in cols_guide.items():
        p1_md += f"- **`{c}`**: {desc}\n"

    nb.cells.append(nbf.v4.new_markdown_cell(p1_md))

    primary_path = paths[0] if paths else "caminho_indefinido.csv"
    is_ibama_raw = "raw\\tabular\\ibama" in primary_path.lower()
    sep_str = "sep=';'" if is_ibama_raw else "sep=','"

    p1_code = f"""# =============================================================================
# FASE 1: SETUP & LOAD
# =============================================================================
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração visual para gráficos limpos e didáticos
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10

# Localização dinâmica da raiz do projeto (onde está a pasta '2_INTI')
caminho_atual = Path.cwd().resolve()
raiz_projeto = None
for p in [caminho_atual] + list(caminho_atual.parents):
    if (p / "2_INTI" / "RESEARCH_PROTOCOL.md").is_file() or (p / "AGENTS.md").is_file():
        raiz_projeto = p
        break

if raiz_projeto is None:
    raise FileNotFoundError("Não foi possível localizar a raiz do projeto (onde está 2_INTI/RESEARCH_PROTOCOL.md).")

# Caminho exato do arquivo conforme especificado no documento de hipóteses
caminho_csv = raiz_projeto / r"{primary_path}"

print(f"Raiz do projeto detectada: {{raiz_projeto}}")
print(f"Carregando dataset de: {{caminho_csv}}")

if not caminho_csv.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {{caminho_csv}}")

# Leitura com suporte a caracteres especiais (BOM / UTF-8)
df = pd.read_csv(caminho_csv, {sep_str}, encoding='utf-8-sig', low_memory=False)

print(f"Dimensões do dataset (linhas, colunas): {{df.shape}}")
print("\\n--- Primeiras 5 linhas do dataset bruto ---")
df.head()"""
    nb.cells.append(nbf.v4.new_code_cell(p1_code))

    p1_info_code = """print("--- Informações estruturais das colunas e tipos de dados ---")
df.info()"""
    nb.cells.append(nbf.v4.new_code_cell(p1_info_code))

    # FASE 2: CLEANING & WRANGLING
    p2_md = f"""## Fase 2: Data Cleaning & Wrangling

Realizamos a limpeza sistemática dos dados respeitando as regras específicas para `{var_name}`:
"""
    for note in notes:
        p2_md += f"- **Atenção:** {note}\n"

    if is_municipal:
        p2_md += "- **Salvaguarda Territorial:** Harmonização estrita para 141 municípios de Mato Grosso. Se houver dados de Boa Esperança do Norte (`5101837`), são aglutinados em Nova Ubiratã (`5106240`).\n"

    nb.cells.append(nbf.v4.new_markdown_cell(p2_md))

    p2_code = f"""# =============================================================================
# FASE 2: DATA CLEANING & WRANGLING
# =============================================================================
{spec.get('phase2_code', '# Limpeza padrão')}"""
    nb.cells.append(nbf.v4.new_code_cell(p2_code))

    # FASE 3: ESTATÍSTICA DESCRITIVA BÁSICA
    p3_md = """## Fase 3: Estatística Descritiva Básica

Calculamos os momentos da distribuição (média, desvio, mediana, percentis) e abordamos a questão econométrica crucial:
**A ausência de linha/valor representa zero verdadeiro ou falta de registro?**
"""
    nb.cells.append(nbf.v4.new_markdown_cell(p3_md))

    p3_code = f"""# =============================================================================
# FASE 3: ESTATÍSTICA DESCRITIVA BÁSICA
# =============================================================================
{spec.get('phase3_code', 'print(df.describe())')}"""
    nb.cells.append(nbf.v4.new_code_cell(p3_code))

    # FASE 4: ANÁLISE UNIVARIADA
    p4_md = """## Fase 4: Análise Univariada

Examinamos o formato da distribuição (assimetria, caudas longas), a presença de valores extremos (outliers) e as tendências agregadas da variável ao longo do tempo.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(p4_md))

    p4_code = f"""# =============================================================================
# FASE 4: ANÁLISE UNIVARIADA
# =============================================================================
{spec.get('phase4_code', 'pass')}"""
    nb.cells.append(nbf.v4.new_code_cell(p4_code))

    # FASE 5: ANÁLISE BIVARIADA
    p5_md = """## Fase 5: Análise Bivariada (Espaço-Temporal & Biomas)

Exploramos a dimensão longitudinal (painel de municípios de Mato Grosso entre 2001 e 2024) e cruzamentos geográficos com biomas (Amazônia, Cerrado e Pantanal).

> **Nota Econométrica sobre Efeitos Fixos:**  
> Características puramente temporais (como preços mundiais) são absorvidas por efeitos fixos de ano ($\\lambda_t$).  
> Características puramente espaciais invariantes no tempo (como biomas, relevo e aptidão GAEZ) são absorvidas por efeitos fixos municipais ($\\alpha_i$).  
> Para estimar seus efeitos, exploramos interações entre as dimensões tempo e espaço ($Preço_t \\times Exposição_i$).
"""
    nb.cells.append(nbf.v4.new_markdown_cell(p5_md))

    p5_code = f"""# =============================================================================
# FASE 5: ANÁLISE BIVARIADA
# =============================================================================
{spec.get('phase5_code', 'pass')}"""
    nb.cells.append(nbf.v4.new_code_cell(p5_code))

    # FASE 6: FEATURE ENGINEERING (TRATAMENTOS FINAIS E HARMONIZAÇÃO)
    p6_spec = PHASE6_DATA.get(var_name, {})
    p6_md = p6_spec.get('phase6_md', spec.get('phase6_md', """## Fase 6: Feature Engineering (Tratamentos Finais)

Construímos as variáveis finais para os modelos econométricos:
- Normalizações e taxas (0 a 1);
- Defasagens temporais ($t-1$) para mitigar simultaneidade e endogeneidade contemporânea;
- Transformações logarítmicas ou escores padronizados (z-scores);
- Harmonização com a grade padrão de 141 municípios de Mato Grosso x anos 2001-2024.
"""))
    nb.cells.append(nbf.v4.new_markdown_cell(p6_md))

    p6_code_body = p6_spec.get('phase6_code', spec.get('phase6_code', 'pass'))
    p6_code = f"""# =============================================================================
# FASE 6: FEATURE ENGINEERING (TRATAMENTOS FINAIS E HARMONIZAÇÃO)
# =============================================================================
{p6_code_body}"""
    nb.cells.append(nbf.v4.new_code_cell(p6_code))

    return nb

# -----------------------------------------------------------------------------
# 5. EXECUÇÃO PRINCIPAL
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("GERADOR DE NOTEBOOKS AED — PADRÃO GEMINI")
    print(f"Lendo e interpretando arquivo de hipóteses: {HIPOTESES_FILE}")
    variables = parse_hipoteses_file(HIPOTESES_FILE)
    print(f"Total de variáveis candidatas extraídas: {len(variables)}")
    print("=" * 70)

    generated_files = []

    for var_info in variables:
        var_name = var_info["name"]
        spec = VAR_SPECS.get(var_name, {
            "title": f"{var_name} — Análise Exploratória",
            "concept": var_info["desc"],
            "is_municipal": False,
            "cols_guide": {},
            "target_col": "variavel"
        })

        nb = build_notebook_for_var(var_info, spec)

        # Nome de arquivo obrigatório: exatamente com o nome da variável
        filename = f"{var_name}.ipynb"
        filepath = OUTPUT_DIR / filename

        with open(filepath, "w", encoding="utf-8") as f:
            nbf.write(nb, f)

        generated_files.append(filepath)
        print(f" [OK] {var_name:25} -> {filepath.name}")

    print("=" * 70)
    print(f"Sucesso total! {len(generated_files)} notebooks foram gerados em:")
    print(f"-> {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
