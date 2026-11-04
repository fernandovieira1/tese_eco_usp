import io
import json
import zipfile

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
import nbformat
from nbclient import NotebookClient

from h1lab.data import normalize_flag, outcome_coverage, filter_data, variation
from h1lab.metrics import distribution, density, quality, time_series, concentration
from h1lab.models import calendar_lag, fit_model, prepare_sample, fingerprint
from h1lab.panel_metrics import within_transform, correlation_matrix
from h1lab.economic_metrics import economic_portrait
from h1lab.exports import model_bundle, evidence_bundle


def test_real_data_and_selected_catalog(real_data):
    df, cat, meta = real_data
    assert len(df) == 3384 and len(cat) == 296
    assert cat['selected'].sum() == 176
    assert meta['selection_matches_notebook']
    assert df['codigo_ibge'].nunique() == 141
    assert df['ano'].nunique() == 24
    assert set(df['bioma_dominante']) == {'Amazônia', 'Cerrado', 'Pantanal'}
    assert df.groupby('bioma_dominante')['codigo_ibge'].nunique().sum() == 141
    assert not df.duplicated(['codigo_ibge', 'ano']).any()
    assert cat['definition'].str.len().min() > 5
    assert cat.loc['preco_real_usd2024_media_anual__carne_bovina', 'unit'] == 'US$ de 2024/kg'
    assert cat.loc['preco_real_usd2024_media_anual__soja', 'unit'] == 'US$ de 2024/t'
    assert df[cat.index[cat['selected']]].isna().sum().sum() == 68050


def test_flags_do_not_conflate_false_missing_zero():
    s = normalize_flag(pd.Series(['False', 'True', None, '0', '1.0']))
    assert s.iloc[0] == False and s.iloc[1] == True and pd.isna(s.iloc[2])
    with pytest.raises(ValueError):
        normalize_flag(pd.Series(['desconhecido']))


def test_natural_units_use_full_panel_variation(real_data):
    df, cat, _ = real_data
    price = 'preco_real_usd2024_media_anual_lag1__soja'
    fixed = 'capacidade_valor__soja__pam_1991_2000_min7'
    assert cat.loc[price, 'variation'] == 'Comum por ano'
    assert cat.loc[fixed, 'variation'] == 'Fixa por município'
    assert distribution(df, price, cat.loc[price, 'variation'])['stats']['n_total'] == 24
    assert distribution(df, fixed, cat.loc[fixed, 'variation'])['stats']['n_total'] == 141
    assert cat.loc['precip_mm_anual', 'variation'] == 'Município-ano'
    one_year = df.loc[df['ano'] == 2001]
    assert distribution(one_year, 'precip_mm_anual', cat.loc['precip_mm_anual', 'variation'])['unit'] == 'Município-ano'


def test_density_constant_missing_and_integral():
    assert density(pd.Series([1, 1, 1])).empty
    assert density(pd.Series([np.nan, np.inf])).empty
    result = density(pd.Series(np.random.default_rng(4).normal(size=1000)))
    assert (result['density'] >= 0).all()
    assert .95 < np.trapezoid(result['density'], result['value']) <= 1.01


def test_real_common_cohort_and_weighted_rates(real_data):
    df, _, _ = real_data
    result = economic_portrait(outcome_coverage(df, ['taxa_conversao__agricultura']), reference=df, balanced=True)
    sample = result['sample']
    assert len(sample) == 2280 and sample['codigo_ibge'].nunique() == 95
    for _, row in result['destinations'].iterrows():
        expected = sample[f'conversao_ha__{row.destination}'].sum() / sample['y_nativa_inicial_ha'].sum()
        assert row.weighted_rate == pytest.approx(expected)


def test_series_ratio_common_denominator_and_calendar_grid():
    df = pd.DataFrame({'codigo_ibge': ['1', '2', '1', '2'], 'ano': [2001, 2001, 2003, 2003],
        'bioma_dominante': ['Amazônia'] * 4, 'taxa_conversao__agricultura': [.1, .01, .2, np.nan],
        'conversao_ha__agricultura': [10, 10, 20, np.nan], 'y_nativa_inicial_ha': [100, 1000, 100, 1000], 'y_cobertura_completa': True})
    ts, _ = time_series(df, 'taxa_conversao__agricultura', 'Taxa ponderada pela vegetação inicial', years=[2001, 2002, 2003])
    assert ts.loc[ts['ano'] == 2001, 'value'].item() == pytest.approx(20 / 1100)
    assert pd.isna(ts.loc[ts['ano'] == 2002, 'value'].item())
    assert ts.loc[ts['ano'] == 2003, 'value'].item() == pytest.approx(.2)
    empty, _ = time_series(df, 'taxa_conversao__agricultura', balanced=True, years=[2001, 2002, 2003])
    assert empty['value'].isna().all()


def test_lag_exact_calendar_before_filter(synthetic, filters):
    lag = calendar_lag(synthetic, 'x', 1)
    code = synthetic.iloc[0]['codigo_ibge']
    # 2002 is missing for this municipality: t=2003 must not receive t=2001.
    assert pd.isna(lag.loc[(synthetic.codigo_ibge == code) & (synthetic.ano == 2003)]).all()
    f = dict(filters, years=[2005, 2008])
    sample, _, _, _, _ = prepare_sample(synthetic, f, {'y': 'y', 'xs': ['x'], 'lags': {'x': 1}})
    assert sample['ano'].min() == 2005
    for _, row in sample.iterrows():
        prior = synthetic.loc[(synthetic.codigo_ibge == row.codigo_ibge) & (synthetic.ano == row.ano - 1), 'x']
        assert row.x == pytest.approx(prior.item())


@pytest.mark.parametrize('fe', ['none', 'entity', 'year', 'twoway'])
@pytest.mark.parametrize('cov', ['HC3', 'cluster_entity', 'cluster_year', 'cluster_twoway', 'nonrobust'])
def test_ols_matches_explicit_dummy_regression(synthetic, filters, fe, cov):
    spec = {'y': 'y', 'xs': ['x', 'z'], 'fe': fe, 'cov': cov}
    result = fit_model(synthetic, filters, spec)
    x = sm.add_constant(synthetic[['x', 'z']])
    for key, modes in [('codigo_ibge', ['entity', 'twoway']), ('ano', ['year', 'twoway'])]:
        if fe in modes:
            x = pd.concat([x, pd.get_dummies(synthetic[key], prefix=key, drop_first=True, dtype=float)], axis=1)
    reference = sm.OLS(synthetic['y'], x).fit()
    if cov == 'HC3':
        ref = reference.get_robustcov_results(cov_type='HC3', use_t=True)
    elif cov == 'nonrobust':
        ref = reference
    else:
        keys = {'cluster_entity': ['codigo_ibge'], 'cluster_year': ['ano'], 'cluster_twoway': ['codigo_ibge', 'ano']}[cov]
        g = [pd.factorize(synthetic[k])[0] for k in keys]
        ref = reference.get_robustcov_results(cov_type='cluster', groups=g[0] if len(g) == 1 else np.column_stack(g), use_correction=True, df_correction=True, use_t=True)
    for i, term in enumerate(['const', 'x', 'z']):
        assert result['coefficients'].loc[term, 'coef'] == pytest.approx(np.asarray(ref.params)[i], rel=1e-8)
        with np.errstate(invalid='ignore'):
            np.testing.assert_allclose(result['coefficients'].loc[term, 'se'], np.asarray(ref.bse)[i], rtol=1e-7, equal_nan=True)


def test_twoway_projection_is_correct_unbalanced(synthetic):
    cols = ['x', 'y', 'fixed', 'price']
    result = within_transform(synthetic, cols, mode='twoway')
    effects = sm.add_constant(pd.concat([pd.get_dummies(synthetic.codigo_ibge, drop_first=True, dtype=float), pd.get_dummies(synthetic.ano, drop_first=True, dtype=float)], axis=1))
    expected = synthetic[cols].to_numpy() - effects.to_numpy() @ np.linalg.lstsq(effects, synthetic[cols], rcond=None)[0]
    np.testing.assert_allclose(result[cols], expected, atol=1e-8)
    assert (result[['fixed', 'price']] == 0).all().all()
    assert pd.isna(correlation_matrix(result, cols).loc['fixed', 'x'])


@pytest.mark.parametrize('fe,x', [('entity', 'fixed'), ('year', 'price'), ('twoway', 'fixed'), ('twoway', 'price')])
def test_absorbed_terms_rejected(synthetic, filters, fe, x):
    with pytest.raises(ValueError, match='absorvidos'):
        fit_model(synthetic, filters, {'y': 'y', 'xs': [x], 'fe': fe})


def test_rank_constant_y_cluster_and_log_domain(synthetic, filters):
    duplicate = synthetic.assign(copy=synthetic['x'] * 2)
    with pytest.raises(ValueError, match='Colinearidade'):
        fit_model(duplicate, filters, {'y': 'y', 'xs': ['x', 'copy']})
    with pytest.raises(ValueError, match='Y não varia'):
        fit_model(synthetic.assign(y=1), filters, {'y': 'y', 'xs': ['x']})
    one = dict(filters, municipalities=[synthetic.iloc[0].codigo_ibge])
    with pytest.raises(ValueError, match='dois grupos'):
        fit_model(synthetic, one, {'y': 'y', 'xs': ['x'], 'cov': 'cluster_entity'})
    sample, _, ledger, _, _ = prepare_sample(synthetic, filters, {'y': 'y', 'xs': ['z'], 'transforms': {'z': 'log'}})
    assert len(sample) == int(synthetic.z.gt(0).sum())
    assert ledger.iloc[-1].N == len(sample)


def test_standardization_and_interaction_common_sample(synthetic, filters):
    altered = synthetic.copy()
    altered.loc[:5, 'z'] = np.nan
    sample, terms, _, _, scales = prepare_sample(altered, filters, {'y': 'y', 'xs': ['x', 'z'], 'transforms': {'x': 'zscore'}, 'interactions': [['x', 'z']]})
    assert sample.x.mean() == pytest.approx(0, abs=1e-12)
    assert sample.x.std() == pytest.approx(1)
    assert scales['x']['mean'] == pytest.approx(altered.dropna(subset=['z']).x.mean())
    np.testing.assert_allclose(sample['x × z'], sample.x * sample.z)


def test_zero_quality_denominators_and_gini(real_data):
    df, catalog, _ = real_data
    q = quality(df, catalog)
    for col in ['taxa_conversao__agricultura', 'n_autos_flora__ibama_informada']:
        valid = pd.to_numeric(df[col], errors='coerce').dropna()
        assert q.loc[col, '% zeros entre válidos'] == pytest.approx(100 * valid.eq(0).mean())
    gini, _ = concentration([0, 0, 10, 10])
    assert gini == pytest.approx(.5)
    assert np.isnan(concentration([0, 0])[0])
    assert np.isnan(concentration([-1, 3])[0])


def test_model_export_notebook_runs(tmp_path, synthetic, filters):
    model = fit_model(synthetic, filters, {'y': 'y', 'xs': ['x', 'z'], 'fe': 'twoway', 'cov': 'cluster_entity'})
    packet = model_bundle(model, {'csv_sha256': 'synthetic'}, filters)
    with zipfile.ZipFile(io.BytesIO(packet)) as z:
        z.extractall(tmp_path)
    nb = nbformat.read(tmp_path / 'reproduzir_ols.ipynb', as_version=4)
    NotebookClient(nb, timeout=120, kernel_name='python3', resources={'metadata': {'path': str(tmp_path)}}).execute()
    nbformat.write(nb, tmp_path / 'reproduzir_ols_executado.ipynb')
    assert not any(o.output_type == 'error' for c in nb.cells if c.cell_type == 'code' for o in c.outputs)


def test_evidence_context_and_latex(synthetic, filters):
    entry = {'title': 'Preço × capacidade ≤ p50', 'note': '1% de Δ anual', 'table': pd.DataFrame({'média': [1, 2]}),
        'context': {'filters': filters}, 'figure': None}
    packet = evidence_bundle([entry], {'csv_sha256': 'test'}, filters, 'Nota do autor', 'Ponte H1')
    with zipfile.ZipFile(io.BytesIO(packet)) as z:
        assert json.loads(z.read('evidencia_01_contexto.json'))['filters'] == filters
        tex = z.read('evidencia_01.tex').decode()
        assert r'\times' in tex and r'\leq' in tex and r'\Delta' in tex
        assert 'Nota do autor' in z.read('caderno.md').decode()


def test_fingerprint_invalidates_model(filters):
    a = fingerprint(filters, {'y': 'a', 'xs': ['b']}, 'v1')
    assert a != fingerprint(filters, {'y': 'a', 'xs': ['b']}, 'v2')
    assert a != fingerprint(dict(filters, years=[2002, 2008]), {'y': 'a', 'xs': ['b']}, 'v1')


def test_data_path_resolution_and_fallback():
    from h1lab.data import _resolve_data_path, load_data, APP
    fallback_csv = APP / 'data/painel_tese_chap1_pt.csv'
    fallback_mun = APP / 'data/municipios_referencia.json'
    assert fallback_csv.is_file()
    assert fallback_mun.is_file()
    resolved = _resolve_data_path('non_existent/path.csv', 'data/painel_tese_chap1_pt.csv')
    assert resolved == fallback_csv
    df_fb, cat_fb, meta_fb = load_data(csv=fallback_csv)
    assert len(df_fb) == 3384
    assert meta_fb['csv_sha256'] == '5c17831beb0052639461d176dc4d311fdf5e58c3a072ef79638cc7307cde4dde'

