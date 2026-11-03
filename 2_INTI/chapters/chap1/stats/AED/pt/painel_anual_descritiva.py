"""Estatísticas do painel: unidades de observação explícitas, sem imputação."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


ROTULOS = {
    'conversao_ha__agricultura': 'Conversão para agricultura (ha)',
    'conversao_ha__pastagem': 'Conversão para pastagem (ha)',
    'taxa_conversao__agricultura': 'Taxa de conversão para agricultura (proporção)',
    'taxa_conversao__pastagem': 'Taxa de conversão para pastagem (proporção)',
    'preco_real_usd2024_media_anual__soja': 'Preço real da soja (USD 2024/t)',
    'preco_real_usd2024_media_anual__milho': 'Preço real do milho (USD 2024/t)',
    'preco_real_usd2024_media_anual__carne_bovina': 'Preço real da carne (USD 2024/kg)',
    'rendimento_medio_kg_ha__Soja (em grão)': 'Rendimento observado da soja (kg/ha)',
    'rendimento_medio_kg_ha__Milho (em grão)': 'Rendimento observado do milho (kg/ha)',
    'efetivo_bovino': 'Rebanho bovino (cabeças)',
    'lotacao_cabecas_ha': 'Lotação aparente (cabeças/ha)',
    'precip_mm_anual': 'Chuva anual (mm)',
    'precip_zscore_1981_2000': 'Anomalia padronizada da chuva (ref. 1981–2000)',
    'n_autos_desmatamento__ibama_informada': 'Autos de desmatamento — município informado (contagem)',
    'multas_desmatamento_reais_observadas__ibama_informada': 'Multas observadas de desmatamento (R$ dez. 2024)',
    'elevation_mean_m': 'Elevação média da superfície (m)',
}


def papel_coluna(c):
    if c in {'codigo_ibge', 'ano'}:
        return 'chave'
    if c in {'y_colecao', 'y_malha', 'y_mascara_id', 'ano_referencia_area'}:
        return 'metadado'
    qualidade = ('flag_', 'y_flag_', 'meses_', 'count_', 'n_linhas', 'n_areas_',
                 'n_registros_', 'n_tipo_', 'n_area_tema_', 'n_status_', 'n_cancelados_',
                 'fracao_pixels', 'fracao_mapeada', 'y_fracao_', 'y_area_', 'media_', 'desvio_')
    if c.startswith(qualidade) or 'valores_' in c and c.split('__')[0].endswith('_ausentes'):
        return 'qualidade/referência'
    if c in {'y_cobertura_completa', 'grade_fonte_completa', 'geografia_historica_validada',
             'completude_classes_fora_grade_certificada', 'compatibilidade_datas_estoques_validada',
             'soma_fracoes', 'area_mapeada_ha', 'area_valida_ha', 'area_referencia_ha',
             'area_nao_observada_ha', 'area_classe_residual_13_ha'}:
        return 'qualidade/referência'
    return 'medida'


def unidade_observacao(c):
    # Repetir um preço em 141 municípios não cria 141 preços independentes.
    if c.startswith(('preco_', 'ln_preco_', 'dln_preco_', 'flag_ano_nominal_', 'flag_ano_real_')):
        return 'ano'
    if c.startswith(('capacidade_', 'biome_', 'elevation_', 'media_', 'desvio_', 'count_')):
        return 'município'
    if c.startswith(('flag_cobertura_historica_', 'flag_geografia_historica_',
                     'flag_desvio_capacidade_', 'flag_capacidade_', 'flag_temporalidade_',
                     'flag_umidade_comercial_')) or c in {'soma_fracoes', 'flag_ordem_invalida'}:
        return 'município'
    return 'município–ano'


def unidade_medida(c, original=''):
    if c.startswith(('flag_', 'y_flag_')):
        return 'booleano (True/False; NA preservado)'
    if c.startswith(('n_', 'meses_', 'count_')):
        return 'contagem'
    if c.startswith(('ln_', 'dln_', 'capacidade_z', 'interacao_', 'exposicao_')):
        return 'adimensional (transformação/interação indicada no nome)'
    if c.startswith('capacidade_valor'):
        return 'índice 0–10.000' if 'gaez_sx' in c else ('kg matéria seca/ha' if 'gaez_yx' in c else 'kg/ha')
    if c.startswith('preco_'):
        return ('USD 2024' if '_real_' in c else 'USD nominal') + ('/kg' if 'carne_bovina' in c else '/t')
    if 'multas_' in c:
        return 'R$ dez. 2024' if '_reais_' in c else 'R$ nominal'
    if c.startswith('rendimento_'):
        return 'kg/ha'
    if c.startswith('efetivo_bovino'):
        return 'cabeças'
    if c.startswith('lotacao_'):
        return 'cabeças/ha'
    if 'zscore' in c:
        return 'desvios-padrão'
    if c.startswith(('precip_', 'media_', 'desvio_')):
        return 'mm'
    if c.startswith('elevation_'):
        return 'm'
    if 'share' in c or c.startswith(('taxa_', 'fracao_')):
        return 'proporção (0–1)'
    if '_ha' in c:
        return 'ha'
    return original


def catalogar(painel, rastreabilidade):
    rastros = rastreabilidade.set_index('coluna_painel')
    linhas = []
    for c in painel:
        r = rastros.loc[c].to_dict() if c in rastros.index else {}
        linhas.append({**r, 'coluna_painel': c, 'papel': papel_coluna(c),
                       'unidade_observacao': unidade_observacao(c),
                       'unidade': unidade_medida(c, r.get('unidade', '')),
                       'tipo_python': str(painel[c].dtype),
                       'n_presentes_grade': int(painel[c].notna().sum()),
                       'n_ausentes_grade': int(painel[c].isna().sum())})
    return pd.DataFrame(linhas)


def normalizar_tipos(painel):
    """Pivôs mistos podem guardar números como object; não os perder na AED."""
    resultado = painel.copy()
    for c in resultado:
        if papel_coluna(c) == 'medida':
            resultado[c] = pd.to_numeric(resultado[c], errors='raise')
        elif papel_coluna(c) == 'qualidade/referência':
            valores = set(resultado[c].dropna().astype(str).str.lower().unique())
            if valores and valores <= {'true', 'false'}:
                resultado[c] = resultado[c].astype('string').str.lower().map(
                    {'true': True, 'false': False}).astype('boolean')
    return resultado


def amostra_medida(painel, coluna, catalogo):
    unidade = catalogo.set_index('coluna_painel').loc[coluna, 'unidade_observacao']
    chave = {'ano': ['ano'], 'município': ['codigo_ibge'],
             'município–ano': ['codigo_ibge', 'ano']}[unidade]
    # Só removemos repetições esperadas depois de confirmar igualdade, incluindo NA.
    if painel.groupby(chave, observed=True)[coluna].nunique(dropna=False).gt(1).any():
        raise ValueError(f'{coluna}: valores incompatíveis com a unidade {unidade}.')
    return painel[chave + [coluna]].drop_duplicates(chave).copy()


def descrever_medidas(painel, catalogo):
    linhas = []
    for _, meta in catalogo.loc[catalogo.papel.eq('medida')].iterrows():
        c = meta.coluna_painel
        amostra = amostra_medida(painel, c, catalogo)
        # Falhar em texto inesperado é melhor que omitir silenciosamente uma medida.
        s = pd.to_numeric(amostra[c], errors='raise').astype(float)
        v = s.dropna()
        q = v.quantile([.01, .05, .25, .5, .75, .95, .99])
        iqr = q.loc[.75] - q.loc[.25]
        linhas.append({'variavel': c, 'unidade': meta.unidade,
                       'unidade_observacao': meta.unidade_observacao,
                       'n_oportunidades': len(s), 'n_validos': len(v), 'n_ausentes': int(s.isna().sum()),
                       'pct_ausentes': 100 * s.isna().mean(), 'n_zeros': int(v.eq(0).sum()),
                       'n_negativos': int(v.lt(0).sum()), 'media': v.mean(), 'desvio_padrao': v.std(ddof=1),
                       'minimo': v.min(), 'p01': q.loc[.01], 'p05': q.loc[.05], 'p25': q.loc[.25],
                       'mediana': q.loc[.5], 'p75': q.loc[.75], 'p95': q.loc[.95], 'p99': q.loc[.99],
                       'maximo': v.max(), 'assimetria': v.skew(), 'curtose_excesso': v.kurt(),
                       'iqr': iqr, 'n_fora_1_5_iqr': int(((v < q.loc[.25] - 1.5 * iqr) |
                                                                      (v > q.loc[.75] + 1.5 * iqr)).sum())})
    return pd.DataFrame(linhas)


def resumo_por_fonte(descritiva, catalogo, nome):
    selecionadas = catalogo.loc[catalogo.notebooks.fillna('').str.split(';').apply(
        lambda itens: nome in [x.strip().removesuffix('.ipynb') for x in itens]), 'coluna_painel']
    return descritiva.loc[descritiva.variavel.isin(selecionadas)].reset_index(drop=True)


def cobertura_colunas(painel):
    return pd.DataFrame({'coluna': painel.columns, 'presentes': painel.notna().sum().to_numpy(),
                         'ausentes': painel.isna().sum().to_numpy(),
                         'pct_ausentes': 100 * painel.isna().mean().to_numpy()}).sort_values(
                             ['pct_ausentes', 'coluna'], ascending=[False, True]).reset_index(drop=True)


def frequencias_qualidade(painel, catalogo):
    colunas = catalogo.loc[catalogo.papel.isin(['qualidade/referência', 'metadado']), 'coluna_painel']
    linhas = []
    for c in colunas:
        s = painel[c]
        valores = set(s.dropna().astype(str).str.lower().unique())
        binaria = bool(valores) and valores <= {'true', 'false'}
        linhas.append({'coluna': c, 'n_validos': int(s.notna().sum()), 'n_ausentes': int(s.isna().sum()),
                       'n_valores_distintos': s.nunique(),
                       'n_true': int(s.astype('string').str.lower().eq('true').sum()) if binaria else pd.NA,
                       'n_false': int(s.astype('string').str.lower().eq('false').sum()) if binaria else pd.NA})
    return pd.DataFrame(linhas)


def variacao_painel(painel, colunas):
    linhas = []
    for c in colunas:
        sub = painel[['codigo_ibge', 'ano', c]].dropna()
        medias = sub.groupby('codigo_ibge')[c].mean()
        dentro = sub[c] - sub.groupby('codigo_ibge')[c].transform('mean')
        linhas.append({'variavel': c, 'n_observacoes': len(sub), 'n_municipios': len(medias),
                       'dp_total': sub[c].std(), 'dp_medias_municipais': medias.std(),
                       'dp_desvios_da_media_municipal': dentro.std(),
                       'municipios_com_variacao_temporal': int(sub.groupby('codigo_ibge')[c].nunique().gt(1).sum())})
    return pd.DataFrame(linhas)


def resumo_agrupado(painel, colunas, grupo):
    longo = painel[[grupo] + list(colunas)].melt(id_vars=grupo, var_name='variavel', value_name='valor')
    return longo.groupby([grupo, 'variavel'], observed=True).valor.agg(
        n_validos='count', media='mean', desvio_padrao='std', minimo='min',
        p25=lambda s: s.quantile(.25), mediana='median', p75=lambda s: s.quantile(.75), maximo='max').reset_index()


def resumo_y(painel, apenas_balanceados=False):
    ys = ['conversao_ha__agricultura', 'conversao_ha__pastagem',
          'taxa_conversao__agricultura', 'taxa_conversao__pastagem']
    validos = painel[ys + ['y_nativa_inicial_ha']].notna().all(axis=1)
    n_anos = validos.groupby(painel.codigo_ibge).sum()
    base = painel.loc[painel.codigo_ibge.isin(n_anos[n_anos.eq(24)].index)] if apenas_balanceados else painel
    linhas = []
    for ano, sub in base.groupby('ano'):
        for destino in ['agricultura', 'pastagem']:
            area, taxa = f'conversao_ha__{destino}', f'taxa_conversao__{destino}'
            ok = sub[[area, taxa, 'y_nativa_inicial_ha']].notna().all(axis=1) & sub.y_nativa_inicial_ha.gt(0)
            observados = sub.loc[ok]
            soma = observados[area].sum(min_count=1)
            denominador = observados.y_nativa_inicial_ha.sum(min_count=1)
            linhas.append({'ano': ano, 'destino': destino, 'n_municipios_grade': len(sub),
                           'n_validos': len(observados), 'n_ausentes': len(sub) - len(observados),
                           'n_zeros': int(observados[area].eq(0).sum()),
                           'conversao_observada_ha': soma, 'nativa_inicial_mesma_amostra_ha': denominador,
                           'taxa_media_simples': observados[taxa].mean(),
                           'taxa_razao_das_somas': soma / denominador if denominador > 0 else np.nan})
    return pd.DataFrame(linhas)


def histograma(painel, coluna, catalogo):
    s = amostra_medida(painel, coluna, catalogo)[coluna].dropna()
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.histplot(s, bins=30, ax=ax, color='#286c8e')
    ax.set(xlabel=ROTULOS.get(coluna, coluna), ylabel='Frequência', title=f'Distribuição — {len(s):,} valores observados')
    fig.tight_layout()
    return fig


def boxplot(painel, coluna, catalogo):
    s = amostra_medida(painel, coluna, catalogo)[coluna].dropna()
    fig, ax = plt.subplots(figsize=(9, 2.8))
    sns.boxplot(x=s, ax=ax, color='#6daac2', whis=1.5)
    ax.set(xlabel=ROTULOS.get(coluna, coluna), title='Boxplot — extremos preservados')
    fig.tight_layout()
    return fig


def serie_temporal(painel, coluna, catalogo):
    dados = amostra_medida(painel, coluna, catalogo)
    fig, ax = plt.subplots(figsize=(10, 4))
    if 'ano' not in dados:
        raise ValueError('Atributo fixo não tem série temporal própria.')
    if 'codigo_ibge' in dados:
        resumo = dados.groupby('ano')[coluna].agg(mediana='median', p25=lambda s: s.quantile(.25),
                                                p75=lambda s: s.quantile(.75))
        ax.plot(resumo.index, resumo.mediana, label='Mediana dos municípios observados')
        ax.fill_between(resumo.index, resumo.p25, resumo.p75, alpha=.2, label='P25–P75; não é intervalo de confiança')
    else:
        ax.plot(dados.ano, dados[coluna], marker='o', markersize=3, label='Série anual comum aos municípios')
    ax.set(xlabel='Ano', ylabel=ROTULOS.get(coluna, coluna), xlim=(2001, 2024))
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig


def mapa_cobertura(painel, colunas):
    tabela = painel.groupby('ano')[colunas].agg(lambda s: 100 * s.notna().mean()).T
    tabela.index = [ROTULOS.get(c, c) for c in tabela.index]
    fig, ax = plt.subplots(figsize=(13, max(4, len(colunas) * .38)))
    sns.heatmap(tabela, vmin=0, vmax=100, cmap='YlGnBu', ax=ax, cbar_kws={'label': '% dos 141 municípios com valor'})
    ax.set(xlabel='Ano', ylabel='', title='Cobertura das medidas principais')
    ax.tick_params(axis='x', labelrotation=45)
    fig.tight_layout()
    return fig


def grafico_correlacao(matriz, titulo):
    matriz = matriz.rename(index=ROTULOS, columns=ROTULOS)
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(matriz, cmap='vlag', vmin=-1, vmax=1, center=0, annot=True, fmt='.2f', square=True, ax=ax)
    ax.set_title(titulo)
    fig.tight_layout()
    return fig


def diagnosticar_amostras(painel, cenarios):
    linhas = []
    for nome, colunas in cenarios.items():
        valido = painel[colunas].notna().all(axis=1)
        por_municipio = valido.groupby(painel.codigo_ibge).sum()
        linhas.append({'cenario_descritivo': nome, 'n_variaveis': len(colunas), 'n_pares_completos': int(valido.sum()),
                       'n_municipios_com_algum_par': int(por_municipio.gt(0).sum()),
                       'n_municipios_com_24_anos': int(por_municipio.eq(24).sum()),
                       'colunas_exigidas': '; '.join(colunas)})
    return pd.DataFrame(linhas)
