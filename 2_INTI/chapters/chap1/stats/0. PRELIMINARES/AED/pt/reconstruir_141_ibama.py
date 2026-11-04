"""Reassocia pontos IBAMA à malha de 141 municípios de 2023, sem alterar fontes."""
from pathlib import Path
import hashlib
import json

import geopandas as gpd
import numpy as np
import pandas as pd

from aed_support import encontrar_raiz


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    raiz = encontrar_raiz()
    dados = raiz / '2_INTI/xdata/chap1'
    malha_path = dados / 'raw/vector/ibge/MT_Municipios_2023.zip'
    eventos_path = dados / 'processed/tabular/h1__autos_ibama__eventos_MT.csv'
    geo_path = dados / 'processed/tabular/h1__autos_ibama__geocodificacao_candidata.csv'
    destino = dados / 'processed/territorio_141'
    destino.mkdir(parents=True, exist_ok=True)
    municipios = gpd.read_file(malha_path).to_crs(4326)
    assert len(municipios) == 141 and municipios.geometry.is_valid.all()
    assert municipios['CD_MUN'].is_unique and '5101837' not in set(municipios['CD_MUN'])
    cad = municipios[['CD_MUN', 'NM_MUN']].rename(columns={'CD_MUN': 'codigo_ibge', 'NM_MUN': 'municipio'})
    (destino / 'municipios_referencia.json').write_text(cad.sort_values('codigo_ibge').to_json(
        orient='records', force_ascii=False, indent=2), encoding='utf-8')
    eventos = pd.read_csv(eventos_path, dtype='string')
    for campo in ['NUM_LONGITUDE_AUTO', 'NUM_LATITUDE_AUTO']:
        eventos[campo] = pd.to_numeric(eventos[campo].str.replace(',', '.', regex=False), errors='coerce')
    eventos['ano'] = pd.to_numeric(eventos['ano'], errors='raise').astype('Int64')
    eventos['valor_multa_nominal'] = pd.to_numeric(eventos['valor_multa_nominal'], errors='coerce')
    xmin, ymin, xmax, ymax = municipios.total_bounds
    validos = (eventos['NUM_LONGITUDE_AUTO'].between(xmin, xmax)
               & eventos['NUM_LATITUDE_AUTO'].between(ymin, ymax)).fillna(False)
    pontos = eventos.loc[validos].copy()
    pontos = gpd.GeoDataFrame(pontos, geometry=gpd.points_from_xy(
        pontos['NUM_LONGITUDE_AUTO'], pontos['NUM_LATITUDE_AUTO']), crs=4326)
    associado = pontos.sjoin(municipios[['CD_MUN', 'geometry']], how='left', predicate='within')
    assert associado.index.is_unique, 'Um ponto foi associado a dois municípios.'
    geo = pd.DataFrame(associado[['SEQ_AUTO_INFRACAO', 'codigo_ibge', 'ano', 'valor_multa_nominal', 'CD_MUN']])
    geo = geo.rename(columns={'CD_MUN': 'codigo_ibge_espacial'})
    ambos = geo['codigo_ibge'].notna() & geo['codigo_ibge_espacial'].notna()
    geo['diverge_codigo_informado'] = pd.Series(pd.NA, index=geo.index, dtype='boolean')
    geo.loc[ambos, 'diverge_codigo_informado'] = geo.loc[ambos, 'codigo_ibge'].ne(geo.loc[ambos, 'codigo_ibge_espacial'])
    geo['geografia_referencia'] = 'IBGE_2023_141'
    # Sem ID não há contagem validada. Duplicidades de identidade não são contadas duas vezes.
    bons_ids = geo['SEQ_AUTO_INFRACAO'].notna() & ~geo['SEQ_AUTO_INFRACAO'].duplicated(keep=False)
    base = geo.loc[bons_ids & geo['codigo_ibge_espacial'].notna() & geo['ano'].notna()]
    agregado = base.groupby(['codigo_ibge_espacial', 'ano']).agg(
        n_autos_ibama_espacial=('SEQ_AUTO_INFRACAO', 'nunique'),
        valor_multas_ibama_espacial=('valor_multa_nominal', lambda s: s.sum(min_count=1)),
    ).reset_index().rename(columns={'codigo_ibge_espacial': 'codigo_ibge'})
    agregado['geografia_referencia'] = 'IBGE_2023_141'
    assert '5101837' not in set(agregado['codigo_ibge'])
    assert not agregado.duplicated(['codigo_ibge', 'ano']).any()
    assert agregado['n_autos_ibama_espacial'].sum() == len(base)
    saidas = [destino / geo_path.name,
              destino / 'h1__autos_ibama__espacial_municipio_anual_candidato.csv']
    geo.to_csv(saidas[0], index=False, encoding='utf-8')
    agregado.to_csv(saidas[1], index=False, encoding='utf-8')
    anterior = pd.read_csv(geo_path, dtype={'SEQ_AUTO_INFRACAO': 'string', 'codigo_ibge_espacial': 'string'})
    antigos_ben = anterior.loc[anterior['codigo_ibge_espacial'].eq('5101837') & anterior['SEQ_AUTO_INFRACAO'].notna()]
    conferidos = antigos_ben[['SEQ_AUTO_INFRACAO']].merge(
        geo.loc[geo['SEQ_AUTO_INFRACAO'].notna(), ['SEQ_AUTO_INFRACAO', 'codigo_ibge_espacial']],
        on='SEQ_AUTO_INFRACAO', how='left', validate='one_to_one')
    relatorio = dict(referencia='IBGE_2023_141', linhas_eventos=len(eventos),
        pontos_no_bbox=int(validos.sum()), pontos_associados=int(geo['codigo_ibge_espacial'].notna().sum()),
        ids_aptos_contagem=len(base), ids_ausentes=int(geo['SEQ_AUTO_INFRACAO'].isna().sum()),
        antigos_ben_por_destino=conferidos['codigo_ibge_espacial'].value_counts(dropna=False).to_dict(),
        inputs={str(p.relative_to(raiz)): sha(p) for p in [malha_path, eventos_path, geo_path]},
        outputs={str(p.relative_to(raiz)): sha(p) for p in saidas})
    audit = raiz / '2_INTI/audit/aed_chap1_20261013/territorio141_ibama.json'
    audit.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in relatorio.items() if k not in ['inputs', 'outputs']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
