"""Interactive OLS specification, diagnostics, FWL and reproducible exports."""
from __future__ import annotations

import hashlib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .exports import model_bundle
from .models import TRANSFORMS, FIXED_EFFECTS, COVARIANCES, fingerprint, fit_model, qq_data
from .ui import COLORS, artifact, axis, chart, context, definition, number, picker, multi_picker, pretty


def model_view(full, df, catalog, options, meta, filters):
    st.subheader('Laboratório OLS · da pergunta à especificação')
    st.write('Escolha um desfecho e uma ou mais explicativas. O app estima associações condicionais, mostra a amostra utilizada e prepara a reprodução em Python.')
    y = picker('Y · variável dependente', options, 'model_y', 'taxa_conversao__agricultura')
    if y is None:
        return
    xs = multi_picker('Xs · variáveis explicativas', [c for c in options if c != y],
        default=[c for c in ['rendimento_medio_kg_ha_lag1__Soja (em grão)'] if c in options and c != y],
        format_func=pretty, max_selections=12, key='model_xs')
    definition(y, catalog)
    if xs:
        with st.expander('Definições dos Xs'):
            st.dataframe(catalog.loc[xs, ['definition', 'unit', 'scope', 'variation']], width='stretch')
    c1, c2 = st.columns(2)
    fe = c1.selectbox('Efeitos fixos', list(FIXED_EFFECTS), format_func=FIXED_EFFECTS.get, key='model_fe')
    cov = c2.selectbox('Erros-padrão', list(COVARIANCES), index=1, format_func=COVARIANCES.get, key='model_cov')
    require_y = st.checkbox('Exigir cobertura completa nas variáveis de conversão', value=True, key='model_require_y')
    transforms, lags = {}, {}
    with st.expander('Transformações e defasagens', expanded=False):
        st.caption('Defasagens são por ano civil exato, calculadas no painel integral antes dos filtros. Uma defasagem adicional em uma coluna lag1 produz t−2. ln(1+x) é restrito a x ≥ 0 e depende da unidade de medida. Zeros não são imputados.')
        for i, var in enumerate([y, *xs]):
            st.markdown(f'**{"Y" if i == 0 else f"X{i}"} · {pretty(var)}**')
            a, b = st.columns([3, 1])
            transforms[var] = a.selectbox('Transformação', list(TRANSFORMS), format_func=TRANSFORMS.get, key=f'transform_{var}')
            lags[var] = int(b.number_input('Defasagem adicional', 0, 5, 0, key=f'lag_{var}', disabled=i == 0))
    interactions = []
    if len(xs) >= 2:
        with st.expander('Adicionar uma interação entre Xs'):
            enabled = st.checkbox('Estimar também o produto de dois Xs', key='model_interaction')
            if enabled:
                a, b = st.columns(2)
                with a:
                    left = picker('Primeiro componente', xs, 'interaction_left')
                with b:
                    right = picker('Segundo componente', [x for x in xs if x != left], 'interaction_right')
                interactions = [[left, right]]
                st.caption('O produto é formado após as transformações. Os termos principais permanecem selecionados. Com efeitos fixos, componentes absorvidos precisam ser considerados ao revisar a especificação.')
    spec = {'y': y, 'xs': xs, 'fe': fe, 'cov': cov, 'require_y': require_y,
            'transforms': transforms, 'lags': lags, 'interactions': interactions}
    current = fingerprint(filters, spec, meta['csv_sha256'])
    st.caption('Casos completos apenas para esta especificação. Sem remoção automática de extremos; preços comuns e atributos fixos podem ser absorvidos. A opção de erros-padrão é uma escolha exploratória a justificar no trabalho.')
    if st.button('Estimar OLS', type='primary', disabled=not xs, key='fit_ols'):
        st.session_state.pop('ols_model', None)
        try:
            with st.spinner('Validando a amostra e estimando o modelo…'):
                result = fit_model(full, filters, spec)
                result['fingerprint'] = current
                st.session_state['ols_model'] = result
        except (ValueError, np.linalg.LinAlgError) as error:
            st.error(str(error))
    model = st.session_state.get('ols_model')
    if model is None:
        st.info('Ajuste a especificação e clique em Estimar OLS. Um X produz regressão simples; vários Xs produzem regressão múltipla.')
        return
    if model['fingerprint'] != current:
        st.info('A especificação ou o recorte mudou. Clique em Estimar OLS para atualizar os resultados.')
        return
    summary = model['summary']
    st.divider()
    st.markdown('**Resultado na amostra comum**')
    cards = [*st.columns(3), *st.columns(2)]
    for col, field in zip(cards, ['N', 'Municípios', 'Anos', 'R2 ajustado', 'RMSE']):
        col.metric(field.replace('R2', 'R²'), number(summary[field], 0 if field in ['N', 'Municípios', 'Anos'] else 4))
    st.caption(f"{FIXED_EFFECTS[fe]} · {COVARIANCES[cov]} · inferência t, com {number(summary['Graus de liberdade da inferência'], 0)} graus de liberdade. R² com efeitos fixos inclui sua contribuição; confira também o R² parcial nas estatísticas completas.")
    for warning in model['warnings']:
        st.warning(warning)
    table = model['coefficients']
    display_table = table.rename(columns={'coef': 'Coeficiente', 'se': 'Erro-padrão', 't': 'Estatística t', 'p': 'p-valor', 'ci_low': 'IC 95% · inferior', 'ci_high': 'IC 95% · superior'})
    st.dataframe(display_table.style.format('{:.5g}'), width='stretch')
    st.caption('P-valores e intervalos dependem da covariância escolhida. Não selecionar variáveis apenas por significância; a OLS pode gerar previsões fora de [0,1] quando Y é uma proporção.')
    chart_table = table.loc[model['terms']].reset_index()
    chart_table['Termo'] = [f'X{i+1}' for i in range(len(chart_table))]
    fig = go.Figure(go.Scatter(x=chart_table['coef'], y=chart_table['Termo'], mode='markers',
        error_x=dict(type='data', symmetric=False, array=chart_table['ci_high'] - chart_table['coef'], arrayminus=chart_table['coef'] - chart_table['ci_low']),
        marker=dict(size=9, color='#13796b'), customdata=chart_table[['term', 'se']],
        hovertemplate='%{customdata[0]}<br>Coeficiente: %{x}<br>Erro-padrão: %{customdata[1]}<extra></extra>'))
    fig.add_vline(x=0, line_dash='dash', line_color='#8494a1')
    fig.update_xaxes(title='Coeficiente e intervalo de 95% · unidades da especificação', tickformat='.2e')
    chart(fig, 'model_coefficients', max(260, 75 + len(chart_table) * 45))
    st.dataframe(chart_table[['Termo', 'term']].rename(columns={'term': 'Variável'}), hide_index=True, width='stretch')
    note = f"OLS exploratória; Y={y}; Xs={xs}; efeitos fixos={fe}; covariância={cov}; N={summary['N']}; municípios={summary['Municípios']}; anos={summary['Anos']}. Transformações e defasagens registradas na configuração."
    artifact('OLS: ' + pretty(y), display_table, note, context(meta, filters, spec=spec, summary=summary), 'model_table', fig)
    st.download_button('Baixar modelo + amostra + notebook Python', model_bundle(model, meta, filters),
        'modelo_ols_h1.zip', 'application/zip', type='primary', key='model_download')
    with st.expander('Amostra, perdas, escalas e estatísticas completas'):
        st.dataframe(model['ledger'], hide_index=True, width='stretch')
        st.dataframe(model['missing'], width='stretch')
        st.json(summary)
        if model['scales']:
            st.json(model['scales'])
        st.dataframe(model['sample'][['codigo_ibge', 'ano', y, *xs]].head(100), width='stretch')
    st.markdown('**Diagnósticos para orientar o próximo notebook**')
    d = model['diagnostics']
    kind = st.radio('Diagnóstico', ['Resíduos × ajustados', 'Observado × ajustado', 'QQ dos resíduos', 'Influência e alavancagem', 'VIF'], horizontal=True, key='model_diagnostic')
    if kind == 'VIF':
        st.dataframe(model['vif'], width='stretch')
        st.caption('VIF condicional aos efeitos fixos escolhidos, na amostra comum. Colinearidade elevada prejudica a precisão; não constitui justificativa científica isolada para excluir um controle.')
    else:
        if kind == 'Resíduos × ajustados':
            diag = px.scatter(d, x='ajustado', y='residuo', color='bioma_dominante', color_discrete_map=COLORS, opacity=.5, hover_data=['municipio', 'ano'])
            diag.add_hline(y=0, line_dash='dash')
        elif kind == 'Observado × ajustado':
            diag = px.scatter(d, x='ajustado', y='observado', color='bioma_dominante', color_discrete_map=COLORS, opacity=.5, hover_data=['municipio', 'ano'])
            lo, hi = min(d['observado'].min(), d['ajustado'].min()), max(d['observado'].max(), d['ajustado'].max())
            diag.add_scatter(x=[lo, hi], y=[lo, hi], mode='lines', name='Igualdade', line=dict(dash='dash'))
        elif kind == 'QQ dos resíduos':
            qq = qq_data(d['residuo_padronizado'])
            diag = px.scatter(qq, x=qq.columns[0], y=qq.columns[1], opacity=.65)
            diag.add_scatter(x=[qq.iloc[:, 0].min(), qq.iloc[:, 0].max()], y=[qq.iloc[:, 0].min(), qq.iloc[:, 0].max()], mode='lines', name='Normal padrão', line=dict(dash='dash'))
        else:
            diag = px.scatter(d, x='alavancagem', y='Cook', color='bioma_dominante', color_discrete_map=COLORS, hover_data=['municipio', 'ano', 'residuo_padronizado'], opacity=.6)
        chart(diag, 'model_diagnostics')
        if kind == 'Influência e alavancagem':
            st.dataframe(d.nlargest(15, 'Cook'), width='stretch')
        st.caption('Diagnósticos do ajuste OLS, sem excluir observações. Cook e resíduos studentizados são indicadores clássicos de influência; não corrigem dependência no painel nem substituem inferência robusta.')
    with st.expander('Relação parcial (FWL) — mantendo os demais Xs e efeitos fixos'):
        term = picker('X de interesse', model['terms'], 'fwl_term')
        if st.checkbox('Calcular a visualização parcial', key='show_fwl'):
            controls = model['design'].drop(columns=term).to_numpy(float)
            yy = model['sample'][y].to_numpy(float)
            xx = model['design'][term].to_numpy(float)
            pair = np.column_stack([yy, xx])
            residual = pair - controls @ np.linalg.lstsq(controls, pair, rcond=None)[0]
            partial = pd.DataFrame({'Y residual': residual[:, 0], 'X residual': residual[:, 1], 'Bioma': model['sample']['bioma_dominante']})
            fwl = px.scatter(partial, x='X residual', y='Y residual', color='Bioma', color_discrete_map=COLORS, opacity=.45)
            grid = np.linspace(partial['X residual'].min(), partial['X residual'].max(), 50)
            fwl.add_scatter(x=grid, y=table.loc[term, 'coef'] * grid, mode='lines', name='Coeficiente do modelo completo')
            chart(fwl, 'fwl_chart')
            st.caption('Mesmos pares município-ano e mesmos controles do modelo completo. A inclinação coincide com o coeficiente OLS; os erros-padrão e p-valores vêm do modelo completo, não de uma regressão iid dos resíduos.')
    with st.expander('Cenário condicional dentro do ajuste'):
        st.caption('Altere um X na escala transformada usada pelo modelo. Mantêm-se os outros Xs e os efeitos fixos do par de referência. Não é previsão causal; combinações novas podem não ter suporte conjunto.')
        if any(c.startswith(('interacao_', 'exposicao_')) for c in xs):
            st.info('Interações e exposições já existentes no painel são regressores independentes neste simulador e não são recalculadas ao alterar seus componentes. O cenário não representa seu efeito marginal total; para impor essas identidades, use o notebook.')
        chosen = picker('X para variar', xs, 'scenario_x')
        if st.session_state.get('scenario_row', 0) >= len(model['sample']):
            st.session_state['scenario_row'] = 0
        reference = st.selectbox('Par de referência', list(range(len(model['sample']))),
            format_func=lambda i: f"{model['sample'].iloc[i]['municipio']} · {model['sample'].iloc[i]['ano']}", key='scenario_row')
        row = model['design'].iloc[[reference]].copy()
        old = float(row[chosen].iloc[0])
        value = st.number_input('Novo valor de X (escala do modelo)', value=old, format='%.6f', key=f'scenario_value_{current}_{chosen}_{reference}')
        row[chosen] = value
        for left, right in interactions:
            row[f'{left} × {right}'] = row[left] * row[right]
        if value < model['sample'][chosen].min() or value > model['sample'][chosen].max():
            st.warning('Valor fora do intervalo marginal observado: extrapolação.')
        prediction = (row.to_numpy() @ np.asarray(model['fit'].params)).item()
        baseline = float(d.iloc[reference]['ajustado'])
        st.metric('Y ajustado no cenário (escala do modelo)', number(prediction, 6), delta=number(prediction - baseline, 6))
        st.caption(f'X original={number(old, 6)}; Y ajustado de referência={number(baseline, 6)}. Logs não são revertidos automaticamente: isso exigiria uma decisão sobre retransformação e viés.')
    with st.expander('Guardar e comparar especificações desta sessão'):
        title = st.text_input('Nome curto do modelo', value=f'OLS {len(xs)} X · {fe}', key='model_name')
        if st.button('Guardar modelo na comparação', key='save_model'):
            saved = st.session_state.setdefault('saved_models', [])
            saved.append({'nome': title, 'spec': spec, 'filters': filters, 'summary': summary,
                'coef': table.copy(), 'sample_hash': hashlib.sha256(model['sample'][['codigo_ibge', 'ano']].to_csv(index=False).encode()).hexdigest()})
        saved = st.session_state.get('saved_models', [])
        if saved:
            st.dataframe(pd.DataFrame([{'Modelo': m['nome'], 'Y': m['spec']['y'], 'N': m['summary']['N'],
                'R2 ajustado': m['summary']['R2 ajustado'], 'Amostra': m['sample_hash'][:10], 'Covariância': m['spec']['cov']} for m in saved]), hide_index=True, width='stretch')
            st.caption('Hashes de amostra diferentes indicam pares diferentes. R² não permite ordenar modelos com Y ou transformação distintos; comparação causal exige desenho próprio.')
            if st.button('Limpar comparação', key='clear_models'):
                st.session_state['saved_models'] = []
                st.rerun()
