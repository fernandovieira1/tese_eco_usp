"""Author-controlled evidence notebook connecting data to the thesis argument."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from .data import ROOT
from .exports import evidence_bundle, csv_bytes, json_text, manifest
from .narrative import H1, BRIDGE
from .panel_metrics import panel_descriptive
from .ui import artifact, context, multi_picker, pretty


def text_view(df, catalog, options, meta, filters):
    st.subheader('Do dado ao argumento do capítulo')
    st.markdown('> **H1** — ' + H1)
    st.markdown(BRIDGE)
    with st.expander('Fontes textuais e escopo desta ponte'):
        st.code('2_INTI/chapters/chap1/text/0_introduction.tex\n2_INTI/chapters/chap1/text/1_literature_review.tex\n2_INTI/chapters/chap1/text/2_mt_descriptive.tex', language=None)
        st.caption('Referências e organização extraídas dos arquivos locais. Não foram modificados enunciados, citekeys ou texto da tese. As notas abaixo são material de trabalho a revisar pelo autor.')
    st.markdown('**Monte uma tabela descritiva para a redação**')
    defaults = [c for c in ['taxa_conversao__agricultura', 'taxa_conversao__pastagem', 'precip_mm_anual', 'efetivo_bovino'] if c in options]
    selected = multi_picker('Variáveis da tabela', options, default=defaults, format_func=pretty, max_selections=25, key='text_variables')
    if selected:
        table = panel_descriptive(df, selected)
        table.insert(0, 'Unidade', catalog.loc[selected, 'unit'])
        table = table[['Unidade', 'n_valid', 'missing_pct', 'mean', 'median', 'sd_overall', 'min', 'max', 'sd_between', 'sd_within']]
        artifact('Estatística descritiva do recorte', table,
            'Observação município-ano; cada variável usa seus casos disponíveis, sem filtro automático por Y. Comparar N antes de interpretar médias. Para preços ou atributos fixos, consultar também a distribuição na unidade natural.',
            context(meta, filters, variables=selected, unit='município-ano', sample='disponível por variável'), 'text_descriptive')
    st.markdown('**Caderno de evidências**')
    entries = st.session_state.get('evidence', [])
    st.caption('Use “Guardar evidência” junto às tabelas e gráficos. Cada item mantém seus próprios filtros, N e configuração. O caderno permanece nesta sessão; baixe o ZIP para preservá-lo.')
    if entries:
        st.dataframe(pd.DataFrame([{'Item': i + 1, 'Evidência': e['title'], 'Nota': e['note']} for i, e in enumerate(entries)]), hide_index=True, width='stretch')
        remove = st.multiselect('Itens para retirar do caderno', list(range(len(entries))), format_func=lambda i: f'{i+1}. {entries[i]["title"]}', key='remove_evidence')
        if st.button('Retirar itens escolhidos', disabled=not remove, key='remove_evidence_button'):
            st.session_state['evidence'] = [e for i, e in enumerate(entries) if i not in remove]
            st.rerun()
    else:
        st.info('O caderno está vazio. Abra a tabela acima ou qualquer gráfico e guarde uma evidência.')
    notes = st.text_area('Notas do autor — observação, interpretação e limite', height=210, key='author_notes',
        placeholder='O que se observa? Em qual amostra e unidade? Como isso conversa com uma dimensão de H1? Que explicações concorrentes e limitações permanecem?')
    st.download_button('Baixar caderno completo (ZIP)', evidence_bundle(entries, meta, filters, notes, BRIDGE),
        'caderno_evidencias_h1.zip', 'application/zip', type='primary', key='evidence_download')
    st.download_button('Baixar manifesto do recorte', json_text(manifest(meta, filters)), 'manifesto_recorte.json', 'application/json', key='manifest_download')
    with st.expander('Conferência antes de levar um resultado ao texto'):
        st.markdown('- Informar período, municípios, biomas, unidade de observação e cobertura.\n'
                    '- Distinguir ausência de informação, zero observado, totais e taxas.\n'
                    '- Comparar tendências em coorte constante ou explicitar a mudança de composição.\n'
                    '- Separar fato descritivo, interpretação econômica e hipótese ainda não testada.\n'
                    '- Justificar proxies, temporalidade e especificação em vez de escolher apenas pelo p-valor.\n'
                    '- Usar os arquivos exportados para revisão e integração manual ao LaTeX.')
