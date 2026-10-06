"""Integration checks on actual acquired data and substantive transformations."""
import json,hashlib
from pathlib import Path
import pandas as pd
import numpy as np
import pytest
from data_common import DATA,ROOT,sha256

def read(name):return pd.read_csv(DATA/'processed/tabular'/name,dtype={'codigo_ibge':str},low_memory=False)

def test_checkpoint_originals_unchanged():
    b=pd.read_csv(DATA/'catalog/baseline_repositorio_sha256.csv',dtype=str)
    assert all(sha256(ROOT/r.arquivo)==r.sha256 for r in b.itertuples())

def test_mapbiomas_original_md5():
    m=json.loads((DATA/'raw/tabular/mapbiomas/collection10_1_metadata.json').read_text(encoding='utf-8'))
    expected=m['data']['latestVersion']['files'][0]['dataFile']['md5']
    assert hashlib.md5((DATA/'raw/tabular/mapbiomas/collection10_1_coverage.xlsx').read_bytes()).hexdigest()==expected

def test_pam_yield_and_keys():
    d=read('h1_h2__pam_soja_milho__ibge__municipio_anual.csv')
    assert not d.duplicated(['codigo_ibge','ano','produto']).any()
    assert d.yield_diferenca_kg_ha.abs().max()<1.001
    assert d.loc[d.area_colhida_ha<=0,'yield_calculado_kg_ha'].isna().all()
    assert set(d.produto)=={'Soja (em grão)','Milho (em grão)'}

def test_sidra_missing_symbols_preserved():
    d=read('h1_h2__pam_soja_milho__ibge__municipio_anual.csv')
    for c in ['area_colhida_ha','area_plantada_ha','producao_t','rendimento_medio_kg_ha']:
        symbolic=d[c+'__original'].isin(['...','-','..','X'])
        assert d.loc[symbolic,c].isna().all()

def test_native_vegetation_accounting_and_lag():
    d=read('h2__native_veg__mapbiomas_col10_1__candidato.csv').sort_values(['codigo_ibge','ano'])
    assert d.native_veg_share_it.between(0,1).all()
    np.testing.assert_allclose(d.native_veg_ha_it/d.area_mapeada_ha,d.native_veg_share_it)
    np.testing.assert_allclose(d.groupby('codigo_ibge').native_veg_ha_it.shift(),d.native_veg_ha_lag1,equal_nan=True)
    assert d[d.ano==1985].native_veg_share_lag1.isna().all()

def test_mapbiomas_quarantine_not_silently_matched():
    q=read('mapbiomas_col10_1__MT_sem_correspondencia_IBGE__quarentena.csv')
    assert set(q.municipality)=={'Sonora','Aruanã','Nova Crixás'}
    assert q.codigo_ibge.isna().all()

def test_biome_shares_and_thresholds():
    d=read('h2__biome_share__ibge2019_malha2024__candidato.csv')
    cols=['biome_amazonia_share_i','biome_cerrado_share_i','biome_pantanal_share_i']
    assert len(d)==142 and not d.codigo_ibge.duplicated().any()
    assert d[cols].min().min()>=0 and d[cols].max().max()<=1.000001
    assert d.soma_fracoes.between(.998,1.000001).all()
    for threshold in [70,80,90]:
        assert ((d[f'biome_class_{threshold}']=='misto')==(d[cols].max(axis=1)<threshold/100)).all()

def test_prices_log_difference():
    d=read('h1__prices__worldbank__mensal_robustez.csv').sort_values(['variavel','data'])
    assert not d.duplicated(['variavel','data']).any()
    np.testing.assert_allclose(d.ln_price,np.log(d.preco_nominal),equal_nan=True)
    np.testing.assert_allclose(d.dln_price,d.groupby('variavel').ln_price.diff(),atol=1e-12,equal_nan=True)

def test_ibama_aggregation_reconciles_eligible_events():
    d=read('h1__autos_ibama__eventos_MT.csv');a=read('h1__autos_multas_ibama__municipio_anual_candidato.csv')
    valid=d.flag_codigo_mt & d.ano.notna() & ~d.flag_id_duplicado
    assert d.ano.notna().all()
    assert a.n_autos_ibama_it.sum()==valid.sum()
    np.testing.assert_allclose(a.valor_multas_ibama_it.sum(),d.loc[valid,'valor_multa_nominal'].sum())
    assert not a.duplicated(['codigo_ibge','ano']).any()

def test_gaez_candidates_not_mixed():
    d=read('h1__suitability_yield__gaez_v4_6190__candidatos.csv')
    assert len(d)==142*8
    assert not d.duplicated(['codigo_ibge','variavel_raster']).any()
    assert set(d.nivel_insumo)=={'alto','baixo'}
    assert d.loc[d.variavel_raster.str.startswith('sx'),'valor_medio'].between(0,10000).all()

def test_chirps_anomalies_require_full_climatology():
    d=read('h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv')
    assert d.loc[d['count']<12,'precip_mm_anual'].isna().all()
    for start,end in [(1981,2010),(1991,2020)]:
        name=f'precip_anomaly_{start}_{end}'
        assert d.loc[d[f'count_{start}_{end}']<30,name].isna().all()
        baseline=d[d.ano.between(start,end)].groupby('codigo_ibge')[name].mean().dropna()
        assert (baseline.abs()<1e-7).all()
        np.testing.assert_allclose(d[f'precip_excess_{start}_{end}']-d[f'precip_deficit_{start}_{end}'],d[name],equal_nan=True)

def test_complete_chirps_coverage_and_bounds():
    d=read('h2__precip_mm__chirps_v2__mensal_candidato.csv')
    assert len(d)==142*45*12
    assert not d.duplicated(['codigo_ibge','ano','mes']).any()
    assert (d.precip_mm>=0).all()
    assert d.fracao_pixels_validos.between(0,1).all()
    v=json.loads((DATA/'catalog/validacao_chirps_rasters.json').read_text(encoding='utf-8'))
    assert len(v)==540
    for r in v:
        left,bottom,right,top=r['bbox']
        assert left<=-61.633383 and bottom<=-18.0415982 and right>=-50.2248064 and top>=-7.3490284

def test_dem_coverage():
    d=read('topography__copdem90__municipio_candidato.csv')
    assert len(d)==142 and (d.n_pixels>0).all()
    assert (d.elevation_mean_m>=d.elevation_min_m).all()
    assert (d.elevation_mean_m<=d.elevation_max_m).all()
