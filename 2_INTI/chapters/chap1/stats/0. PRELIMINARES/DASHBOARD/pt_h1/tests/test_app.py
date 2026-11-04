from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'app.py'
PAGES = ['Visão econômica', 'Explorar variáveis', 'Qualidade e amostra', 'Séries e territórios',
         'Relações e correlações', 'Laboratório OLS', 'Do dado ao texto']


def clean(at):
    assert not at.exception, '\n'.join(e.message for e in at.exception)
    assert not at.error, '\n'.join(e.value for e in at.error)


@pytest.fixture
def app():
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    clean(at)
    return at


@pytest.mark.parametrize('page', PAGES)
def test_every_page_loads(app, page):
    app.radio(key='page').set_value(page).run()
    clean(app)


def test_all_distribution_types_and_natural_units(app):
    app.radio(key='page').set_value('Explorar variáveis').run()
    for kind in ['Histograma', 'Densidade (KDE)', 'Boxplot', 'Violino', 'Frequência acumulada', 'Barras por bioma']:
        app.selectbox(key='dist_kind').set_value(kind).run()
        clean(app)
    app.selectbox(key='dist_var').set_value('preco_real_usd2024_media_anual_lag1__soja').run()
    clean(app)
    assert any('Unidade efetiva: Ano' in c.value for c in app.caption)


def test_empty_filter_and_single_year_do_not_crash(app):
    app.multiselect(key='biomes').set_value([]).run()
    clean(app)
    assert any('recorte está vazio' in i.value for i in app.info)
    app.multiselect(key='biomes').set_value(['Pantanal']).run()
    app.slider(key='years').set_value((2024, 2024)).run()
    clean(app)
    for page in ['Explorar variáveis', 'Qualidade e amostra', 'Séries e territórios', 'Relações e correlações']:
        app.radio(key='page').set_value(page).run()
        clean(app)


def test_model_fit_diagnostics_scenario_and_staleness(app):
    app.radio(key='page').set_value('Laboratório OLS').run()
    app.button(key='fit_ols').click().run()
    clean(app)
    assert len(app.dataframe) >= 4
    for diagnostic in ['Resíduos × ajustados', 'Observado × ajustado', 'QQ dos resíduos', 'Influência e alavancagem', 'VIF']:
        app.radio(key='model_diagnostic').set_value(diagnostic).run()
        clean(app)
    app.checkbox(key='show_fwl').check().run()
    clean(app)
    app.selectbox(key='model_cov').set_value('HC3').run()
    clean(app)
    assert any('recorte mudou' in i.value for i in app.info)
    app.button(key='fit_ols').click().run()
    clean(app)


def test_evidence_roundtrip_in_ui(app):
    app.button(key='overview_table_save').click().run()
    clean(app)
    app.radio(key='page').set_value('Do dado ao texto').run()
    clean(app)
    assert len(app.session_state['evidence']) == 1
    app.text_area(key='author_notes').set_value('Evidência exploratória, sem conclusão causal.').run()
    clean(app)


def test_relationship_modes_and_pairwise(app):
    app.radio(key='page').set_value('Relações e correlações').run()
    for mode in ['between', 'entity', 'twoway', 'pooled']:
        app.selectbox(key='relation_mode').set_value(mode).run()
        clean(app)
    app.checkbox(key='corr_common').uncheck().run()
    clean(app)
    app.radio(key='relation_style').set_value('Médias por intervalos de X (binscatter)').run()
    clean(app)


def test_full_catalog_categorical_and_flags(app):
    app.toggle(key='all_columns').set_value(True).run()
    app.radio(key='page').set_value('Explorar variáveis').run()
    for variable in ['y_malha', 'flag_ano_real_incompleto__carne_bovina']:
        app.selectbox(key='dist_var').set_value(variable).run()
        clean(app)


def test_h1_guided_crossing_and_blocks(app):
    app.radio(key='page').set_value('Relações e correlações').run()
    app.checkbox(key='show_h1_groups').check().run()
    clean(app)
    app.selectbox(key='h1_institution').set_value('n_autos_flora_lag1__ibama_informada').run()
    clean(app)
    app.radio(key='page').set_value('Explorar variáveis').run()
    app.selectbox(key='dist_block').set_value('Preços internacionais').run()
    clean(app)


def test_model_choices_and_notes_persist_across_pages(app):
    app.radio(key='page').set_value('Laboratório OLS').run()
    app.selectbox(key='model_y').set_value('taxa_conversao__pastagem').run()
    app.multiselect(key='model_xs').set_value(['precip_mm_anual']).run()
    app.radio(key='page').set_value('Do dado ao texto').run()
    app.text_area(key='author_notes').set_value('Nota para preservar ao navegar.').run()
    app.radio(key='page').set_value('Laboratório OLS').run()
    clean(app)
    assert app.selectbox(key='model_y').value == 'taxa_conversao__pastagem'
    assert app.multiselect(key='model_xs').value == ['precip_mm_anual']
    app.radio(key='page').set_value('Do dado ao texto').run()
    assert app.text_area(key='author_notes').value == 'Nota para preservar ao navegar.'


def test_catalog_changes_and_y_x_overlap(app):
    app.toggle(key='all_columns').set_value(True).run()
    app.radio(key='page').set_value('Laboratório OLS').run()
    app.multiselect(key='model_xs').set_value(['nativa_ha', 'precip_mm_anual']).run()
    app.selectbox(key='model_y').set_value('precip_mm_anual').run()
    clean(app)
    assert 'precip_mm_anual' not in app.multiselect(key='model_xs').value
    app.toggle(key='all_columns').set_value(False).run()
    clean(app)
    assert 'nativa_ha' not in app.multiselect(key='model_xs').value
    app.radio(key='page').set_value('Séries e territórios').run()
    app.selectbox(key='series_var').set_value('precip_mm_anual').run()
    clean(app)
