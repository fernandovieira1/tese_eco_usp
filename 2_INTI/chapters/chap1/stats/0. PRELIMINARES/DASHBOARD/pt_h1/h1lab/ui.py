"""Shared, Portuguese UI components; evidence retains its own sample context."""
from __future__ import annotations

import copy
import hashlib
import textwrap

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .exports import csv_bytes, json_text, manifest
from .narrative import QUESTIONS
from .presentation import booktabs, label

COLORS = {'Amazônia': '#13796b', 'Cerrado': '#c48727', 'Pantanal': '#597fc4', 'Todos': '#13796b', 'Não classificado': '#8993a4'}
PALETTE = ['#13796b', '#c48727', '#597fc4', '#9b5b81', '#567b7e']


def pretty(name):
    return label(name)


def axis(name):
    return '<br>'.join(textwrap.wrap(pretty(name), width=56))


def number(value, digits=2):
    if pd.isna(value):
        return '—'
    return f'{value:,.{digits}f}'.replace(',', '§').replace('.', ',').replace('§', '.')


def chart(fig, key, height=440):
    fig.update_layout(template='plotly_white', height=height,
        margin=dict(l=24, r=18, t=32, b=40), colorway=PALETTE,
        font=dict(family='Arial, sans-serif', color='#213347', size=13),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#ffffff',
        legend=dict(orientation='h', y=-.24, title_text=''), hovermode='closest')
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor='#e9edf0', automargin=True)
    st.plotly_chart(fig, width='stretch', key=key,
        config={'displaylogo': False, 'toImageButtonOptions': {'format': 'svg', 'filename': key}})
    return fig


def picker(text, options, key, default=None):
    if not options:
        st.info('Não há variáveis disponíveis nesta seleção.')
        return None
    if key in st.session_state and st.session_state[key] not in options:
        st.session_state[key] = default if default in options else options[0]
    return st.selectbox(text, options, index=options.index(default) if default in options else 0,
                        format_func=pretty, key=key)


def multi_picker(text, options, key, default=None, **kwargs):
    if key in st.session_state:
        valid = [c for c in st.session_state[key] if c in options]
        if valid != st.session_state[key]:
            st.session_state[key] = valid
    return st.multiselect(text, options, default=default or [], key=key, **kwargs)


def definition(var, catalog, expanded=False):
    row = catalog.loc[var]
    with st.expander('Definição, unidade e relação com H1', expanded=expanded):
        st.markdown(f"**{row['definition']}**")
        st.caption(f"Unidade: {row['unit']} · Escala: {row['scope']} · Variação no painel integral: {row['variation']}")
        st.code(var, language=None)
        question, interpretation = QUESTIONS[row['block']]
        st.markdown(f'**{question}** {interpretation}')


def artifact(title, table, note, context, key, figure=None):
    with st.expander('Tabela, downloads e caderno de evidências'):
        st.caption(note)
        display_table = table.copy()
        display_table.attrs = {}
        st.dataframe(display_table, width='stretch')
        cols = st.columns(4 if figure is not None else 3)
        cols[0].download_button('Baixar CSV', csv_bytes(table), f'{key}.csv', 'text/csv', key=f'{key}_csv')
        cols[1].download_button('Baixar LaTeX', booktabs(table, title, note), f'{key}.tex', 'text/plain', key=f'{key}_tex')
        if figure is not None:
            cols[2].download_button('Gráfico interativo', figure.to_html(include_plotlyjs=True), f'{key}.html', 'text/html', key=f'{key}_html')
        if cols[-1].button('Guardar evidência', key=f'{key}_save'):
            entries = st.session_state.setdefault('evidence', [])
            digest = hashlib.sha256((title + note + json_text(context) + table.to_csv()).encode()).hexdigest()
            if any(e['id'] == digest for e in entries):
                st.info('Esta evidência já está no caderno.')
            else:
                entries.append({'id': digest, 'title': title, 'table': table.copy(), 'note': note,
                    'context': copy.deepcopy(context), 'figure': figure.to_html(include_plotlyjs=True) if figure is not None else None})
                st.success('Evidência guardada nesta sessão. Baixe o caderno para preservá-la.')


def sample_caption(df, before=None):
    text = f"{len(df):,} observações · {df['codigo_ibge'].nunique()} municípios".replace(',', '.')
    if 'ano' in df:
        text += f" · {df['ano'].nunique()} anos"
    if before is not None:
        text += f' · {before - len(df):,} observações removidas nesta análise'.replace(',', '.')
    st.caption(text)


def context(meta, filters, **configuration):
    return {'source': meta, 'filters': filters, 'analysis': configuration}
