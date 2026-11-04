"""Descriptive views: distributions, quality, dynamics and associations."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .data import KEYS, numeric, outcome_coverage
from .economic_metrics import economic_portrait, grouped_hypothesis
from .exports import csv_bytes
from .metrics import distribution, density, quality, time_series, relationship_sample, concentration
from .panel_metrics import correlation_matrix, panel_descriptive, calculate_vif
from .ui import COLORS, PALETTE, artifact, axis, chart, context, definition, number, picker, multi_picker, pretty, sample_caption


def overview(df, catalog, meta, filters):
    st.subheader('O território, os usos e a conversão')
    st.write('Comece pelo tamanho e pela composição dos fluxos. Depois examine onde estão concentrados e se a mudança temporal acompanha a mesma amostra municipal.')
    balanced = st.checkbox('Comparar a mesma coorte de municípios em todos os anos', value=True, key='overview_balanced')
    qualified = outcome_coverage(df, ['taxa_conversao__agricultura'], True)
    result = economic_portrait(qualified, reference=df, balanced=balanced)
    # Stock coverage is independent of Y transition coverage.
    stocks = economic_portrait(df, reference=df, balanced=False)
    sample = result['sample']
    if sample.empty:
        st.info('Não há pares válidos para os dois destinos nesta coorte. Amplie o período/território ou desmarque a coorte constante.')
        return
    sample_caption(sample, len(df))
    st.caption('Cobertura completa de Y, denominador positivo e valores válidos para os dois destinos. A coorte constante se refere aos anos do recorte.')
    for _, row in result['destinations'].iterrows():
        cards = st.columns(2)
        cards[0].metric(f"Fluxo bruto · {row['destination']}", f"{number(row['conversion_ha'] / 1e6)} mi ha")
        cards[1].metric(f"Taxa anual ponderada · {row['destination']}", f"{number(row['weighted_rate'] * 100, 3)}%")
    st.info('A soma dos fluxos anuais pode contar a mesma área em episódios distintos. A taxa ponderada é fluxo dividido pelo estoque inicial somado por município-ano; não é uma taxa acumulada do período.')
    annual = result['annual'].copy()
    annual['Taxa anual ponderada (%)'] = 100 * annual['weighted_rate']
    annual['Destino'] = annual['destination'].str.capitalize()
    annual['Fluxo (ha)'] = annual['conversion_ha']
    metric = st.radio('Evolução da conversão', ['Taxa anual ponderada (%)', 'Fluxo (ha)'], horizontal=True, key='overview_metric')
    fig = px.line(annual, x='ano', y=metric, color='Destino', markers=True, color_discrete_sequence=PALETTE,
                  hover_data=['n_entities', 'nobs'])
    chart(fig, 'overview_annual')
    artifact('Conversão por destino e ano', annual.set_index(['ano', 'Destino']),
             result['metadata']['rate_definition'], context(meta, filters, balanced=balanced, require_y=True, metric=metric), 'overview_table', fig)
    left, right = st.columns(2)
    with left:
        st.markdown('**Diferenças entre biomas**')
        by = result['by_biome'].copy()
        by['Taxa anual ponderada (%)'] = by['weighted_rate'] * 100
        fig2 = px.bar(by, x='bioma_dominante', y='Taxa anual ponderada (%)', color='destination', barmode='group', labels={'bioma_dominante': 'Bioma', 'destination': 'Destino'},
            color_discrete_sequence=PALETTE, hover_data=['n_entities', 'n_years', 'nobs'])
        chart(fig2, 'overview_biomes', 360)
        st.caption('Bioma dominante = maior fração municipal. O tamanho das amostras e a composição territorial importam, sobretudo no Pantanal.')
        artifact('Conversão por bioma e destino', by.set_index(['bioma_dominante', 'destination']),
            'Mesma amostra comum dos dois destinos; diferenças não identificam efeitos de bioma.', context(meta, filters, balanced=balanced, require_y=True), 'overview_biome_table', fig2)
    with right:
        st.markdown('**Estoque de usos no último ano**')
        stock = stocks['stocks']
        if len(stock):
            fig3 = px.bar(stock, x='use', y='area_ha', color='use', color_discrete_sequence=PALETTE, hover_data=['n_entities', 'ano'], labels={'use': 'Uso da terra'})
            fig3.update_yaxes(title='Área (ha)')
            chart(fig3, 'overview_stocks', 360)
            st.caption(f"{stocks['metadata']['stock_entities']} municípios em {stocks['metadata']['stock_year']}; amostra própria dos estoques. As três classes não representam necessariamente toda a área de referência.")
            artifact('Estoques dos usos da terra', stock.set_index('use'), stocks['metadata']['stock_definition'], context(meta, filters, stock_sample='cobertura conjunta das três classes'), 'stock_table', fig3)
    st.markdown('**Concentração municipal da conversão**')
    destination = st.selectbox('Destino para o ranking', ['total', 'agricultura', 'pastagem'], key='overview_destination')
    rank = result['concentration'].query('destination == @destination').copy()
    names = df.drop_duplicates('codigo_ibge').set_index('codigo_ibge')['municipio']
    rank['municipio'] = rank['codigo_ibge'].map(names)
    gini, lorenz = concentration(rank['conversion_ha'])
    l, r = st.columns([1.4, 1])
    with l:
        fig4 = px.bar(rank.head(15).iloc[::-1], x='conversion_ha', y='municipio', orientation='h', color='bioma_dominante',
            color_discrete_map=COLORS, hover_data=['observed_years', 'codigo_ibge'])
        fig4.update_xaxes(title='Fluxos brutos somados (ha)')
        fig4.update_yaxes(title='', categoryorder='array', categoryarray=rank.head(15)['municipio'].iloc[::-1].tolist())
        chart(fig4, 'overview_ranking', 480)
    with r:
        if len(lorenz):
            fig5 = px.line(lorenz, x='população', y='valor', labels={'população': 'Fração dos municípios', 'valor': 'Fração da conversão'})
            fig5.add_scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(dash='dash', color='#a6adb4'), name='Igualdade')
            chart(fig5, 'overview_lorenz', 390)
        st.metric('Gini dos fluxos municipais observados', number(gini, 3))
        st.caption('Concentração descritiva da conversão, não desigualdade de renda ou efeito causal. Coberturas temporais diferentes podem afetar o ranking.')
    artifact('Ranking municipal de conversão', rank.set_index('codigo_ibge'), result['metadata']['concentration_definition'],
             context(meta, filters, balanced=balanced, require_y=True, destination=destination), 'ranking_table', fig4)


def distributions(df, catalog, options, meta, filters):
    st.subheader('Conheça a distribuição de cada variável')
    st.write('Compare centro, dispersão, assimetria e extremos. Preços comuns usam um registro por ano; atributos fixos usam um por município na opção automática.')
    blocks = ['Todos os blocos', *sorted(catalog.loc[options, 'block'].unique())]
    group = st.selectbox('Bloco de variáveis', blocks, key='dist_block')
    available = options if group == blocks[0] else [c for c in options if catalog.loc[c, 'block'] == group]
    var = picker('Variável', available, 'dist_var', 'taxa_conversao__agricultura')
    if var is None:
        return
    definition(var, catalog, expanded=True)
    if not catalog.loc[var, 'numeric']:
        counts = df[var].astype('string').fillna('(ausente)').value_counts(dropna=False).rename('N').to_frame()
        st.caption(f'{len(counts)} categorias; o gráfico mostra as 30 mais frequentes e a tabela preserva todas.')
        fig = px.bar(counts.head(30).reset_index(), x=var, y='N')
        chart(fig, 'categorical_chart')
        artifact('Frequências: ' + pretty(var), counts, 'Frequências por município-ano, incluindo ausências.', context(meta, filters, variable=var), 'categorical_table', fig)
        return
    c1, c2 = st.columns(2)
    unit = c1.selectbox('Unidade de observação', ['Automática', 'Município-ano', 'Município', 'Ano'], key='dist_unit',
        help='Município usa a média temporal disponível de cada município; Ano usa a média municipal. A opção automática evita multiplicar valores fixos ou preços comuns.')
    kind = c2.selectbox('Visualização', ['Histograma', 'Densidade (KDE)', 'Boxplot', 'Violino', 'Frequência acumulada', 'Barras por bioma'], key='dist_kind')
    result = distribution(df, var, catalog.loc[var, 'variation'], unit)
    s, sample = result['stats'], result['sample']
    cards = [*st.columns(3), *st.columns(2)]
    for slot, title, value in zip(cards, ['N válido', 'Média', 'Mediana', 'Desvio-padrão', 'Zeros / válidos'],
        [number(s['n_valid'], 0), number(s['mean'], 4), number(s['median'], 4), number(s['sd'], 4), number(s['zero_pct']) + '%']):
        slot.metric(title, value)
    st.caption(f"Unidade efetiva: {result['unit']} · {s['n_missing']} ausentes em {s['n_total']} unidades · Valores na unidade original: {catalog.loc[var, 'unit']}")
    if s['n_valid'] == 0:
        st.info('Não há valores finitos nesta seleção. Consulte a página de qualidade ou amplie o recorte.')
        return
    by = st.checkbox('Comparar biomas', value=result['unit'] != 'Ano', disabled=result['unit'] == 'Ano', key='dist_biomes')
    sample = sample.copy()
    sample['grupo'] = sample['bioma_dominante'] if by and result['unit'] != 'Ano' else 'Todos'
    clean = sample.dropna(subset=['value'])
    if kind == 'Histograma':
        bins = st.slider('Número aproximado de intervalos', 5, 100, 30, key='hist_bins')
        fig = px.histogram(clean, x='value', color='grupo', nbins=bins, barmode='overlay', opacity=.65,
            color_discrete_map=COLORS, marginal=None, labels={'value': axis(var), 'count': 'Frequência'})
    elif kind == 'Densidade (KDE)':
        fig = go.Figure()
        for name, g in clean.groupby('grupo'):
            kde = density(g['value'])
            if kde.empty:
                st.info(f'{name}: densidade indefinida com menos de três valores ou sem variação. Use histograma ou frequências.')
            else:
                fig.add_scatter(x=kde['value'], y=kde['density'], mode='lines', name=name, line=dict(color=COLORS.get(name)), fill='tozeroy', opacity=.6)
        fig.update_xaxes(title=axis(var)); fig.update_yaxes(title='Densidade')
        st.caption('KDE gaussiana, largura de banda de Scott, exibida no domínio observado. É uma suavização: pode distorcer massas em zero e limites naturais.')
    elif kind in ['Boxplot', 'Violino']:
        fn = px.box if kind == 'Boxplot' else px.violin
        args = {'points': 'outliers'} if kind == 'Boxplot' else {'box': True, 'points': False}
        fig = fn(clean, x='grupo', y='value', color='grupo', color_discrete_map=COLORS, labels={'value': axis(var), 'grupo': ''}, **args)
        if kind == 'Violino':
            fig.update_traces(spanmode='hard')
        st.caption('Extremos permanecem nos cálculos. No boxplot, os pontos além dos bigodes não são automaticamente erros.')
    elif kind == 'Frequência acumulada':
        fig = px.ecdf(clean, x='value', color='grupo', color_discrete_map=COLORS, labels={'value': axis(var)})
    else:
        bars = clean.groupby('grupo')['value'].agg(['mean', 'median', 'count']).reset_index()
        fig = px.bar(bars, x='grupo', y='mean', color='grupo', color_discrete_map=COLORS, hover_data=['median', 'count'])
        fig.update_yaxes(title='Média · ' + axis(var)); fig.update_xaxes(title='')
    chart(fig, 'distribution_chart')
    stats_pt = pd.Series(s).rename(index={'n_total': 'N total', 'n_valid': 'N válido', 'n_missing': 'Ausentes', 'missing_pct': '% ausentes',
        'n_zero': 'Zeros', 'zero_pct': '% zeros entre válidos', 'n_negative': 'Negativos', 'negative_pct': '% negativos entre válidos',
        'mean': 'Média', 'median': 'Mediana', 'sd': 'Desvio-padrão', 'min': 'Mínimo', 'max': 'Máximo',
        'iqr': 'Intervalo interquartil', 'skewness': 'Assimetria', 'excess_kurtosis': 'Curtose excedente',
        'n_positive': 'N positivos', 'mean_positive': 'Média apenas dos positivos'}).to_frame('Valor')
    note = f"{pretty(var)}; unidade {catalog.loc[var, 'unit']}; observação {result['unit']}; N válido={s['n_valid']}, ausentes={s['n_missing']}. Zeros calculados entre válidos; sem excluir extremos."
    artifact('Distribuição: ' + pretty(var), stats_pt, note, context(meta, filters, variable=var, unit=result['unit'], kind=kind, by_biome=by), 'dist_table', fig)
    st.markdown('**Variação no painel: entre municípios e dentro deles**')
    panel = panel_descriptive(df, [var])
    st.dataframe(panel.rename(columns={'sd_overall': 'DP total', 'sd_between': 'DP entre municípios', 'sd_within': 'DP dentro do município'}), width='stretch')
    st.caption('Os desvios usam as observações disponíveis. Em painel desbalanceado, não são parcelas aditivas de uma decomposição da variância. Grupos com um único ano não demonstram invariância temporal.')


def quality_view(df, catalog, meta, filters):
    st.subheader('O que está observado — e com que cobertura?')
    st.write('Dados faltantes, valores zero e flags têm significados diferentes. Esta página preserva o recorte completo, antes de qualquer seleção por Y ou por X.')
    q = quality(df, catalog)
    c = st.columns(4)
    c[0].metric('Colunas examinadas', len(q))
    c[1].metric('Células ausentes', number(q['Ausentes'].sum(), 0))
    c[2].metric('Colunas com indisponibilidade', int(q['% indisponível'].gt(0).sum()))
    c[3].metric('Células não finitas', int(q['Não finitos'].sum()))
    top = q.sort_values('% indisponível', ascending=False).head(20).reset_index()
    top['Variável'] = top['variable'].map(pretty)
    fig = px.bar(top.iloc[::-1], x='% indisponível', y='Variável', orientation='h', hover_data=['N válido', 'Ausentes', 'Não finitos'], color_discrete_sequence=PALETTE)
    chart(fig, 'quality_top', 620)
    artifact('Qualidade por variável', q, 'Ausências e não finitos sobre o total de pares; zeros apenas entre valores válidos. Flags não são imputadas.', context(meta, filters), 'quality_table', fig)
    defaults = [v for v in ['taxa_conversao__agricultura', 'taxa_conversao__pastagem', 'n_autos_flora_lag1__ibama_informada', 'precip_mm_anual'] if v in catalog.index]
    cols = multi_picker('Variáveis para examinar a amostra conjunta', catalog.index.tolist(), default=defaults, format_func=pretty, key='quality_columns')
    if cols:
        availability = pd.DataFrame({v: numeric(df, [v])[v].notna() if catalog.loc[v, 'numeric'] else df[v].notna() for v in cols})
        joint = availability.all(axis=1)
        st.metric('Casos completos apenas para as variáveis escolhidas', f'{int(joint.sum())} / {len(df)}')
        by_year = (1 - availability.groupby(df['ano']).mean()) * 100
        heat = px.imshow(by_year.T, aspect='auto', zmin=0, zmax=100, color_continuous_scale=['#f5f6f8', '#b34d45'], labels={'x': 'Ano', 'y': 'Variável', 'color': '% indisponível'})
        chart(heat, 'quality_heatmap', min(650, 180 + 45 * len(cols)))
        support = df.assign(completo=joint).groupby('bioma_dominante').agg(pares=('ano', 'size'), municipios=('codigo_ibge', 'nunique'), completos=('completo', 'sum'))
        st.dataframe(support, width='stretch')
        artifact('Indisponibilidade anual', by_year, 'Percentuais por município-ano e variável; não condicionados à cobertura de Y.', context(meta, filters, columns=cols), 'quality_year_table', heat)
    flags = catalog.index[catalog['flag']].tolist()
    if flags:
        flag = picker('Entenda uma flag', flags, 'quality_flag', 'y_cobertura_completa')
        definition(flag, catalog, expanded=True)
        counts = df[flag].astype('string').fillna('Ausente / desconhecida').value_counts().rename('N').to_frame()
        st.dataframe(counts, width='stretch')
    with st.expander('Dicionário integral e dados do recorte'):
        st.dataframe(catalog, width='stretch')
        st.download_button('Baixar dicionário', csv_bytes(catalog), 'dicionario_variaveis.csv', 'text/csv')
        columns = list(dict.fromkeys([*KEYS, *catalog.index]))
        st.dataframe(df[columns].head(100), width='stretch')
        st.download_button('Baixar dados deste recorte', csv_bytes(df[columns].set_index(KEYS)), 'painel_recorte.csv', 'text/csv')


def series_view(df, catalog, options, meta, filters):
    st.subheader('Trajetórias no tempo e diferenças territoriais')
    var = picker('Variável da série', options, 'series_var', 'taxa_conversao__agricultura')
    if var is None:
        return
    definition(var, catalog)
    aggregations = ['Média', 'Mediana']
    # Only extensive quantities may be added across municipalities.
    unit = catalog.loc[var, 'unit']
    if (unit == 'ha' and not any(s in var for s in ['capacidade', 'rendimento'])) or var.startswith(('conversao_ha__', 'efetivo_bovino', 'n_autos_', 'multas_')):
        aggregations.append('Soma')
    if var.startswith('taxa_conversao__'):
        aggregations.insert(0, 'Taxa ponderada pela vegetação inicial')
    l, r = st.columns(2)
    if 'series_aggregation' in st.session_state and st.session_state['series_aggregation'] not in aggregations:
        st.session_state['series_aggregation'] = aggregations[0]
    aggregation = l.selectbox('Como resumir cada ano', aggregations, key='series_aggregation')
    balanced = r.checkbox('Coorte completa para esta variável', value=True, key='series_balanced')
    by = st.checkbox('Separar por bioma dominante', value=True, key='series_biomes')
    require_y = st.checkbox('Exigir cobertura completa para variáveis de conversão', value=True, key='series_require_y')
    ts, sample = time_series(df, var, aggregation, by, balanced, range(filters['years'][0], filters['years'][1] + 1), require_y)
    sample_caption(sample, len(df))
    if not ts['value'].notna().any():
        st.info('Não há observações suficientes nesta coorte. Amplie o recorte ou use a amostra disponível.')
        return
    ts['Exibição'] = ts['value'] * (100 if var.startswith('taxa_conversao__') else 1)
    displayed_unit = '%' if var.startswith('taxa_conversao__') else unit
    fig = px.line(ts, x='ano', y='Exibição', color='bioma_dominante', markers=True, color_discrete_map=COLORS,
        hover_data=['N municípios', 'N disponíveis'], labels={'Exibição': f'{aggregation} ({displayed_unit})', 'ano': 'Ano'})
    fig.update_traces(connectgaps=False)
    chart(fig, 'series_chart')
    st.caption('Anos sem observações permanecem como lacunas. Na amostra disponível, a composição municipal pode mudar; confira N em cada ano.')
    if catalog.loc[var, 'variation'] == 'Comum por ano':
        st.info('Esta série é comum a todos os municípios. Curvas iguais por bioma não representam evidências territoriais independentes.')
    note = f"{pretty(var)}; {aggregation}; coorte completa={balanced}; cobertura Y exigida={require_y}; tabela na unidade original ({unit}); gráfico em {displayed_unit}."
    artifact('Série temporal: ' + pretty(var), ts.set_index(['bioma_dominante', 'ano']), note,
             context(meta, filters, variable=var, aggregation=aggregation, balanced=balanced, require_y=require_y), 'series_table', fig)
    nfig = px.bar(ts, x='ano', y='N municípios', color='bioma_dominante', barmode='group', color_discrete_map=COLORS)
    chart(nfig, 'series_n', 280)
    with st.expander('Trajetórias de municípios específicos'):
        names = df.drop_duplicates('codigo_ibge').set_index('codigo_ibge')['municipio'].to_dict()
        ids = multi_picker('Escolha até 12 municípios', list(names), format_func=lambda x: f'{names[x]} · {x}', max_selections=12, key='series_municipalities')
        if ids:
            local = sample.loc[sample['codigo_ibge'].isin(ids)].set_index(KEYS)
            grid = pd.MultiIndex.from_product([ids, range(filters['years'][0], filters['years'][1] + 1)], names=KEYS)
            local = local.reindex(grid).reset_index()
            local['municipio'] = local['codigo_ibge'].map(names)
            local_fig = px.line(local, x='ano', y=var, color='municipio', markers=True)
            local_fig.update_yaxes(title=axis(var))
            chart(local_fig, 'series_local')
            st.caption('Valores originais; os filtros de cobertura e coorte da série principal também se aplicam aqui.')


MODES = {'pooled': 'Níveis · município-ano', 'between': 'Entre municípios · médias temporais',
         'entity': 'Dentro do município · retirando médias municipais', 'twoway': 'Dentro do painel · retirando município e ano'}


def relationships(df, catalog, options, meta, filters):
    st.subheader('Como as variáveis se movem juntas?')
    st.write('Separe diferenças persistentes entre municípios de mudanças dentro deles. Correlações e retas descrevem associações; a seleção amostral também pode mudar o resultado.')
    c1, c2 = st.columns(2)
    with c1:
        y = picker('Y · variável que você quer explicar', options, 'relation_y', 'taxa_conversao__agricultura')
    if y is None:
        return
    with c2:
        x = picker('X · variável a comparar', [c for c in options if c != y], 'relation_x', 'rendimento_medio_kg_ha_lag1__Soja (em grão)')
    if x is None:
        return
    definition(y, catalog); definition(x, catalog)
    mode = st.selectbox('Dimensão da associação', list(MODES), format_func=MODES.get, key='relation_mode')
    require_y = st.checkbox('Exigir cobertura completa de Y', value=True, key='relation_require_y')
    base = outcome_coverage(df, [y, x], require_y)
    sample = relationship_sample(base, [x, y], mode)
    sample_caption(sample)
    st.caption(f'Recorte inicial: {len(df)} pares; após cobertura: {len(base)}. A dispersão usa casos completos de X e Y.')
    if len(sample) < 3 or sample[[x, y]].nunique().min() < 2:
        st.info('Amostra insuficiente ou variável constante/absorvida nesta dimensão. Preços comuns são absorvidos por efeitos de ano e atributos fixos por efeitos municipais.')
    else:
        style = st.radio('Forma da dispersão', ['Pontos', 'Médias por intervalos de X (binscatter)'], horizontal=True, key='relation_style')
        plotted = sample
        if style != 'Pontos':
            rows = []
            for biome, g in sample.groupby('bioma_dominante'):
                codes = pd.qcut(g[x], q=min(15, g[x].nunique()), duplicates='drop')
                for _, cell in g.groupby(codes, observed=True):
                    rows.append({x: cell[x].mean(), y: cell[y].mean(), 'bioma_dominante': biome, 'N no intervalo': len(cell)})
            plotted = pd.DataFrame(rows)
        fig = px.scatter(plotted, x=x, y=y, color='bioma_dominante', color_discrete_map=COLORS, opacity=.65,
            hover_data=['municipio', 'ano'] if style == 'Pontos' and 'ano' in plotted else None)
        if st.checkbox('Mostrar reta OLS descritiva na amostra inteira', value=True, key='relation_line'):
            xv = sample[x].to_numpy(float); yv = sample[y].to_numpy(float)
            slope = np.dot(xv - xv.mean(), yv - yv.mean()) / np.dot(xv - xv.mean(), xv - xv.mean())
            grid = np.linspace(xv.min(), xv.max(), 80)
            fig.add_scatter(x=grid, y=yv.mean() + slope * (grid - xv.mean()), name='OLS · amostra inteira', mode='lines', line=dict(color='#24374e'))
        fig.update_xaxes(title=axis(x)); fig.update_yaxes(title=axis(y))
        chart(fig, 'relation_scatter')
        pearson, spearman = sample[x].corr(sample[y]), sample[x].corr(sample[y], method='spearman')
        a, b = st.columns(2); a.metric('Pearson', number(pearson, 3)); b.metric('Spearman', number(spearman, 3))
        st.caption('A reta usa as observações, mesmo quando o gráfico mostra médias por intervalos. Não são exibidos p-valores iid para pares repetidos do painel.')
        summary = pd.DataFrame({'Valor': [len(sample), pearson, spearman]}, index=['N', 'Pearson', 'Spearman'])
        artifact('Associação entre ' + pretty(y) + ' e ' + pretty(x), summary,
            f'Dimensão: {MODES[mode]}; casos completos para X e Y; cobertura de Y exigida={require_y}.',
            context(meta, filters, x=x, y=y, mode=mode, style=style, require_y=require_y), 'relation_table', fig)
    st.markdown('**Matriz de correlações e redundância entre proxies**')
    columns = multi_picker('Variáveis da matriz', options, default=[y, x], format_func=pretty, max_selections=15, key='corr_columns')
    c1, c2 = st.columns(2)
    method = c1.selectbox('Coeficiente', ['pearson', 'spearman'], format_func=str.capitalize, key='corr_method')
    common = c2.checkbox('Usar a mesma amostra em todas as correlações', value=True, key='corr_common', disabled=mode != 'pooled')
    common = common or mode != 'pooled'
    if len(columns) >= 2:
        matrix_base = outcome_coverage(df, columns, require_y)
        matrix_sample = relationship_sample(matrix_base, columns, mode, complete_cases=common)
        corr = correlation_matrix(matrix_sample, columns, method, complete_cases=common)
        n_matrix = corr.attrs['pairwise_n']
        heat = px.imshow(corr, zmin=-1, zmax=1, color_continuous_scale='RdBu_r', aspect='auto', text_auto='.2f', labels={'color': method.capitalize()})
        heat.update_xaxes(tickvals=columns, ticktext=[f'V{i+1}' for i in range(len(columns))])
        heat.update_yaxes(tickvals=columns, ticktext=[f'V{i+1}' for i in range(len(columns))])
        chart(heat, 'corr_heatmap', max(400, len(columns) * 34))
        st.dataframe(pd.DataFrame({'Código': [f'V{i+1}' for i in range(len(columns))], 'Variável': columns, 'Definição': catalog.loc[columns, 'definition'].tolist()}), hide_index=True, width='stretch')
        with st.expander('N de cada par e VIF'):
            st.dataframe(n_matrix, width='stretch')
            st.caption('VIF usa uma amostra conjunta e intercepto; é um diagnóstico de redundância, não um critério automático de escolha científica.')
            vif_base = matrix_sample.copy()
            if mode == 'between':
                vif_base['ano'] = 0
            if len(vif_base):
                st.dataframe(calculate_vif(vif_base, columns), width='stretch')
        artifact('Matriz de correlações', corr, f'{method}; {MODES[mode]}; amostra comum={common}; constantes/absorvidas produzem correlação indefinida.',
            context(meta, filters, columns=columns, mode=mode, common=common, method=method, pairwise_n=n_matrix.to_dict()), 'corr_table', heat)
    with st.expander('Cruzamento guiado por H1 · preços, capacidade e instituições'):
        st.write('Compare a conversão entre regimes de preço dentro de grupos de capacidade. A estratificação por registros institucionais permite explorar uma terceira dimensão, com N explícito em cada célula.')
        if st.checkbox('Abrir o cruzamento de H1', key='show_h1_groups'):
            h1_groups(df, catalog, options, meta, filters, require_y)


def h1_groups(df, catalog, options, meta, filters, require_y):
    capacities = [c for c in options if c.startswith(('capacidade_valor__', 'capacidade_z__'))]
    prices = [c for c in options if c.startswith('preco_real_')]
    institutions = [c for c in options if c.startswith(('n_autos_', 'multas_'))]
    ys = [c for c in options if c.startswith('taxa_conversao__')]
    if not all([capacities, prices, ys]):
        st.info('O catálogo não contém os três blocos necessários a este cruzamento.')
        return
    outcome = picker('Destino da conversão', ys, 'h1_y', 'taxa_conversao__agricultura')
    capacity = picker('Capacidade produtiva', capacities, 'h1_capacity', 'capacidade_valor__soja__gaez_yxHr0_soy')
    price = picker('Preço internacional', prices, 'h1_price', 'preco_real_usd2024_media_anual_lag1__soja')
    if st.session_state.get('h1_institution') not in [None, *institutions]:
        st.session_state['h1_institution'] = None
    institution = st.selectbox('Estratificação institucional', [None, *institutions], format_func=lambda c: 'Sem estratificação' if c is None else pretty(c), key='h1_institution')
    groups = st.slider('Grupos de capacidade', 2, 5, 3, key='h1_n_groups')
    st.dataframe(catalog.loc[[outcome, capacity, price, *([institution] if institution else [])], ['definition', 'unit']], width='stretch')
    base = outcome_coverage(df, [outcome], require_y)
    result = grouped_hypothesis(base, capacity, price, institution, groups, outcome)
    table = result['table'].copy()
    if table.empty:
        st.info('Não há observações completas para este cruzamento. Confira a disponibilidade das proxies escolhidas.')
        return
    table['Taxa média (%)'] = 100 * table['mean_y']
    fig = px.bar(table, x='capacity_group', y='Taxa média (%)', color='price_group', barmode='group',
        facet_col='institution_group' if institution else None, color_discrete_sequence=PALETTE,
        hover_data=['nobs', 'n_entities', 'n_years', 'weighted_rate'],
        labels={'capacity_group': 'Grupo de capacidade', 'price_group': 'Preço', 'institution_group': 'Registro institucional'})
    if institution:
        fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
    chart(fig, 'h1_group_chart', 470)
    details = result['metadata']
    st.caption(f"Mediana do preço: {number(details['price_threshold'], 4)} ({catalog.loc[price, 'unit']}); {details['price_years']} anos na definição dos regimes; {details['actual_groups']} grupos efetivos de capacidade; {details['nobs']} pares completos.")
    st.info('Quantis de capacidade dão um voto a cada município; a mediana do preço dá um voto a cada ano. Empates permanecem juntos. Os grupos institucionais distinguem zero observado e registros positivos; ausência não é zero. Diferenças de composição e fatores não observados podem explicar os contrastes.')
    if table['n_entities'].lt(10).any() or table['n_years'].lt(5).any():
        st.warning('Há células com menos de 10 municípios ou 5 anos. Use os contrastes com atenção ao suporte; estes limites são avisos descritivos, não testes de significância.')
    artifact('H1: conversão por preço, capacidade e registros institucionais', table.set_index(['capacity_group', 'price_group', 'institution_group']),
        details['gap_definition'] + ' Os grupos são definidos no recorte após o filtro de cobertura de Y, antes da seleção conjunta por resultado/instituição; N e limiares estão no contexto.',
        context(meta, filters, require_y=require_y, **details), 'h1_group_table', fig)
