"""H1 · Laboratório de dados, descriptive evidence and exploratory OLS."""
from pathlib import Path
import os

# Avoid oversubscription in local interactive linear algebra. Explicit settings win.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import streamlit as st

from h1lab.data import CSV, DICIO, MUNICIPIOS, SELECTION, ROOT, load_data, filter_data
from h1lab.views import overview, distributions, quality_view, series_view, relationships
from h1lab.model_view import model_view
from h1lab.text_view import text_view

st.set_page_config(page_title='H1 · Laboratório de dados', page_icon='🌿', layout='wide', initial_sidebar_state='expanded')
# Detach persistent analysis controls from Streamlit's inactive-page cleanup.
# Buttons/downloads are deliberately excluded; an estimate is never retriggered.
persisted_controls = {'dist_block', 'dist_var', 'dist_unit', 'dist_kind', 'dist_biomes', 'hist_bins',
    'quality_columns', 'quality_flag', 'series_var', 'series_aggregation', 'series_balanced', 'series_biomes',
    'series_require_y', 'series_municipalities', 'relation_y', 'relation_x', 'relation_mode',
    'relation_require_y', 'relation_style', 'relation_line', 'corr_columns', 'corr_method', 'corr_common',
    'show_h1_groups', 'h1_y', 'h1_capacity', 'h1_price', 'h1_institution', 'h1_n_groups',
    'model_y', 'model_xs', 'model_fe', 'model_cov', 'model_require_y', 'model_interaction',
    'interaction_left', 'interaction_right', 'model_name', 'model_diagnostic', 'fwl_term', 'show_fwl',
    'scenario_x', 'scenario_row', 'text_variables', 'author_notes'}
for state_key in list(st.session_state):
    if state_key in persisted_controls or state_key.startswith(('transform_', 'lag_', 'scenario_value_')):
        st.session_state[state_key] = st.session_state[state_key]
st.markdown('''<style>
.block-container {padding-top: 3.8rem; padding-bottom: 3rem; padding-left: 2.5rem; padding-right: 2.5rem; max-width: 1540px;}
[data-testid="stSidebar"] {background: #f1f4f3; border-right: 1px solid #dce4e1;}
[data-testid="stMetric"] {background: #f5f7f7; padding: 14px 18px; border-radius: 10px; border: 1px solid #e3e9e7;}
[data-testid="stMetricValue"] {font-size: 1.6rem; color: #123e39;}
[data-testid="stMetricLabel"] p {white-space: normal;}
h1, h2, h3 {letter-spacing: -.025em;}
.h1-kicker {color: #13796b; font-size: .78rem; letter-spacing: .17em; font-weight: 700; margin-bottom: .4rem;}
.h1-title {font-size: 2.3rem; font-weight: 750; color: #183248; line-height: 1.13; margin: 0 0 .5rem;}
.h1-subtitle {color: #5a6d7e; font-size: 1rem; margin-bottom: 1.5rem;}
</style>''', unsafe_allow_html=True)


@st.cache_data(show_spinner='Lendo o painel canônico e o dicionário…')
def cached_data(stamps):
    return load_data()


try:
    notebook = ROOT / '2_INTI/chapters/chap1/stats/EDA/aed_chap1_pt_ANALISE.ipynb'
    files = [CSV, DICIO, MUNICIPIOS, SELECTION, notebook, Path(__file__).parent / 'h1lab/data.py']
    files += [ROOT / f'2_INTI/chapters/chap1/text/{name}' for name in ['0_introduction.tex', '1_literature_review.tex', '2_mt_descriptive.tex']]
    full, catalog, meta = cached_data(tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in files))
except (ValueError, FileNotFoundError, KeyError) as error:
    st.error(f'Não foi possível validar o painel: {error}')
    st.stop()

PAGES = ['Visão econômica', 'Explorar variáveis', 'Qualidade e amostra', 'Séries e territórios',
         'Relações e correlações', 'Laboratório OLS', 'Do dado ao texto']
with st.sidebar:
    st.markdown('### H1 · Capítulo 1')
    st.caption('Mato Grosso | Tese USP')
    page = st.radio('Navegação', PAGES, key='page')
    st.divider()
    st.markdown('**Recorte dos dados**')
    years = st.slider('Período', int(full['ano'].min()), int(full['ano'].max()), (int(full['ano'].min()), int(full['ano'].max())), key='years')
    biomes = st.multiselect('Biomas dominantes', sorted(full['bioma_dominante'].unique()), default=sorted(full['bioma_dominante'].unique()), key='biomes')
    names = full.drop_duplicates('codigo_ibge').sort_values('municipio').set_index('codigo_ibge')['municipio'].to_dict()
    municipalities = st.multiselect('Municípios (vazio = todos)', list(names), format_func=lambda x: names[x], key='municipalities')
    all_columns = st.toggle('Catálogo completo de variáveis', value=False, key='all_columns', help='Desativado: as 176 colunas de Colunas Selecionadas. Ativado: todas as colunas de origem. Chaves nunca são regressores; flags ficam na exploração e na qualidade.')
    st.caption('Filtros globais apenas de período e território. Cobertura, casos completos e transformações são explicitados em cada análise.')
    st.caption(f"Fonte: {meta['rows']:,} pares · {meta['source_columns']} colunas · {meta['selected_columns']} selecionadas".replace(',', '.'))
    with st.expander('Fonte e rastreabilidade'):
        st.code(meta['csv'], language=None)
        st.caption('SHA-256: ' + meta['csv_sha256'])
        st.caption(meta['treatment'])
    st.caption(f"Evidências guardadas nesta sessão: {len(st.session_state.get('evidence', []))}")

filters = {'years': list(years), 'biomes': biomes, 'municipalities': municipalities}
df = filter_data(full, filters)
active_catalog = catalog if all_columns else catalog.loc[catalog['selected']]
options = active_catalog.index[(active_catalog['numeric']) & (~active_catalog['flag'])].tolist()
explore_options = [c for c in active_catalog.index if c not in ['codigo_ibge', 'ano']]

st.markdown('<div class="h1-kicker">TERRITÓRIO · INCENTIVOS · INSTITUIÇÕES</div><div class="h1-title">H1 · Laboratório de dados</div><div class="h1-subtitle">Explore o painel, compreenda as associações e prepare a evidência do capítulo.</div>', unsafe_allow_html=True)
st.caption(f"RECORTE ATUAL  ·  {len(df):,} pares município-ano  ·  {df['codigo_ibge'].nunique()} municípios  ·  {years[0]}–{years[1]}  ·  {', '.join(biomes) or 'Nenhum bioma'}".replace(',', '.', 1))
if not meta['selection_matches_notebook']:
    st.warning('O código do notebook de análise mudou desde a definição do catálogo selecionado. O app usa config/selection.json; confira a seleção antes de apresentá-la como equivalente ao notebook atual.')
if df.empty:
    st.info('O recorte está vazio. Selecione ao menos um bioma ou amplie municípios e período.')
    st.stop()
if int(df['empate_biomas'].sum()):
    st.caption('Há empates na maior fração de bioma: a classificação segue a ordem Amazônia, Cerrado, Pantanal.')

if page == PAGES[0]:
    overview(df, catalog, meta, filters)
elif page == PAGES[1]:
    distributions(df, catalog, explore_options, meta, filters)
elif page == PAGES[2]:
    quality_view(df, catalog, meta, filters)
elif page == PAGES[3]:
    series_view(df, catalog, options, meta, filters)
elif page == PAGES[4]:
    relationships(df, catalog, options, meta, filters)
elif page == PAGES[5]:
    model_view(full, df, catalog, options, meta, filters)
else:
    if not meta['text_bridge_matches_sources']:
        st.warning('Os textos do capítulo mudaram desde a preparação desta ponte. Confira os argumentos, referências REF e a nomenclatura de H1 antes de usar as notas na redação.')
    text_view(df, catalog, options, meta, filters)

st.divider()
st.caption('Exploração descritiva e OLS orientadas por H1. As associações exibidas não identificam causalidade. Dados, hipóteses e textos originais são preservados.')
