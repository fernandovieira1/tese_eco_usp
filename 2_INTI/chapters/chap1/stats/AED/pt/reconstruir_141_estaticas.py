"""Reextrai medidas estáticas nos 141 municípios da malha IBGE 2023.

Mantém os métodos documentados em xdata/catalog/linhagem_dados_h1_h2.md:
GAEZ: centros de pixels, média ponderada por cos(latitude).
Copernicus: centros de pixels, média simples, mínimo e máximo.
Biomas: áreas de interseção em EPSG:5880, sem normalizar frações.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window, from_bounds
from shapely import make_valid


RAIZ = next(p for p in Path(__file__).resolve().parents
            if (p / '2_INTI/RESEARCH_PROTOCOL.md').is_file())
DADOS = RAIZ / '2_INTI/xdata/chap1'
DESTINO = DADOS / 'processed/territorio_141'
AUDITORIA = RAIZ / '2_INTI/audit/aed_chap1_20261013/territorio141_estaticas.json'
MALHA = DADOS / 'raw/vector/ibge/MT_Municipios_2023.zip'
BIOMAS = DADOS / 'raw/vector/ibge/Biomas_250mil_2019.zip'
REFERENCIA = 'IBGE_2023_141_municipios'


def sha256(caminho):
    digest = hashlib.sha256()
    with caminho.open('rb') as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b''):
            digest.update(bloco)
    return digest.hexdigest()


def registro(caminho):
    return {'arquivo': caminho.relative_to(RAIZ).as_posix(),
            'bytes': caminho.stat().st_size, 'sha256': sha256(caminho)}


def janela_intersecao(dataset, limites):
    left = max(dataset.bounds.left, limites[0])
    bottom = max(dataset.bounds.bottom, limites[1])
    right = min(dataset.bounds.right, limites[2])
    top = min(dataset.bounds.top, limites[3])
    if left >= right or bottom >= top:
        return None
    parcial = from_bounds(left, bottom, right, top, dataset.transform)
    col0 = max(0, math.floor(parcial.col_off))
    row0 = max(0, math.floor(parcial.row_off))
    col1 = min(dataset.width, math.ceil(parcial.col_off + parcial.width))
    row1 = min(dataset.height, math.ceil(parcial.row_off + parcial.height))
    return Window(col0, row0, col1 - col0, row1 - row0)


def pixels_municipais(dataset, municipios):
    """Retorna valores válidos e rótulos 1..141 sem reprojetar o raster."""
    geometrias = municipios.to_crs(dataset.crs)
    janela = janela_intersecao(dataset, geometrias.total_bounds)
    if janela is None:
        return None
    transformacao = dataset.window_transform(janela)
    imagem = dataset.read(1, window=janela, masked=True)
    limites = rasterio.windows.bounds(janela, dataset.transform)
    candidatos = geometrias.sindex.query(__import__('shapely').box(*limites), predicate='intersects')
    formas = [(geometrias.geometry.iloc[i], int(i) + 1) for i in candidatos]
    if not formas:
        return None
    labels = rasterize(formas, out_shape=imagem.shape, transform=transformacao,
                       fill=0, dtype='uint16', all_touched=False)
    validos = (labels > 0) & ~np.ma.getmaskarray(imagem) & np.isfinite(imagem.data)
    linhas, _ = np.nonzero(validos)
    return (labels[validos].astype(np.int64), imagem.data[validos].astype(np.float64),
            linhas, transformacao)


def salvar(tabela, nome, log, chaves):
    if tabela[chaves].isna().any().any() or tabela.duplicated(chaves).any():
        raise ValueError(f'Chaves ausentes ou repetidas em {nome}')
    if tabela.codigo_ibge.nunique() != 141 or tabela.codigo_ibge.eq('5101837').any():
        raise ValueError(f'Universo territorial incorreto em {nome}')
    tabela['geografia_referencia'] = REFERENCIA
    destino = DESTINO / nome
    tabela.to_csv(destino, index=False, encoding='utf-8-sig')
    log['saidas'].append({**registro(destino), 'linhas': len(tabela),
                          'municipios': int(tabela.codigo_ibge.nunique()), 'chaves': chaves})
    print(nome, len(tabela), 'linhas; 141 municípios', flush=True)


def gaez(municipios, log):
    linhas = []
    arquivos = sorted((DADOS / 'raw/raster/gaez_v4_6190').glob('*.tif'))
    esperados = {f'{medida}{insumo}r0_{produto}' for medida in ('sx', 'yx')
                 for insumo in ('H', 'L') for produto in ('mze', 'soy')}
    if {p.stem for p in arquivos} != esperados:
        raise ValueError('Conferir as oito variantes GAEZ locais.')
    for arquivo in arquivos:
        log['entradas'].append(registro(arquivo))
        with rasterio.open(arquivo) as ds:
            if ds.crs.to_epsg() != 4326 or ds.transform.b != 0 or ds.transform.d != 0:
                raise ValueError('GAEZ: o peso de latitude exige a grade geográfica documentada.')
            labels, valores, rows, transform = pixels_municipais(ds, municipios)
            latitudes = transform.f + (rows + 0.5) * transform.e
            pesos = np.cos(np.deg2rad(latitudes))
            n = np.bincount(labels, minlength=142)
            numerador = np.bincount(labels, weights=valores * pesos, minlength=142)
            denominador = np.bincount(labels, weights=pesos, minlength=142)
            if (denominador[1:] <= 0).any():
                raise ValueError(f'Município sem pixels GAEZ: {arquivo.name}')
            medias = numerador[1:] / denominador[1:]
            if (medias < 0).any() or (arquivo.stem.startswith('sx') and (medias > 10000).any()):
                raise ValueError(f'Média GAEZ fora do domínio: {arquivo.name}')
            for i, municipio in municipios.iterrows():
                linhas.append({'codigo_ibge': municipio.CD_MUN, 'municipio': municipio.NM_MUN,
                    'variavel_raster': arquivo.stem, 'valor_medio': float(medias[i]),
                    'n_pixels_validos': int(n[i + 1]),
                    'nivel_insumo': 'alto' if arquivo.stem[2] == 'H' else 'baixo',
                    'periodo_climatico': '1961-1990', 'regime': 'sequeiro',
                    'unidade': 'indice 0-10000' if arquivo.stem.startswith('sx') else 'kg materia seca/ha'})
    tabela = pd.DataFrame(linhas).sort_values(['variavel_raster', 'codigo_ibge'])
    salvar(tabela, 'h1__suitability_yield__gaez_v4_6190__candidatos.csv', log,
           ['codigo_ibge', 'variavel_raster'])


def biomas(municipios, log):
    fonte = gpd.read_file('zip://' + str(BIOMAS)).to_crs(5880)
    mun = municipios.to_crs(5880)
    for nome, geo in [('municipios', mun), ('biomas', fonte)]:
        for indice in geo.index[~geo.is_valid]:
            original = geo.at[indice, 'geometry']
            corrigida = make_valid(original)
            log['reparos_geometrias'].append({'fonte': nome, 'indice': int(indice),
                'area_antes_m2': float(original.area), 'area_depois_m2': float(corrigida.area)})
            geo.at[indice, 'geometry'] = corrigida
        if not geo.is_valid.all():
            raise ValueError(f'Geometria inválida após correção: {nome}')
    coluna = next(c for c in fonte.columns if c.lower() == 'bioma')
    inter = gpd.overlay(mun[['CD_MUN', 'geometry']], fonte[[coluna, 'geometry']],
                        how='intersection', keep_geom_type=True)
    inter['area_m2'] = inter.area
    areas = inter.groupby(['CD_MUN', coluna]).area_m2.sum().unstack(fill_value=0)
    totais = mun.set_index('CD_MUN').area
    fracao = areas.div(totais, axis=0)
    tabela = municipios[['CD_MUN', 'NM_MUN']].rename(
        columns={'CD_MUN': 'codigo_ibge', 'NM_MUN': 'municipio'}).set_index('codigo_ibge')
    for nome, sufixo in [('Amazônia', 'amazonia'), ('Cerrado', 'cerrado'), ('Pantanal', 'pantanal')]:
        tabela[f'biome_{sufixo}_share_i'] = fracao[nome].reindex(tabela.index)
    colunas = [c for c in tabela if c.endswith('_share_i')]
    if tabela[colunas].isna().any().any() or (tabela[colunas] < -1e-8).any().any():
        raise ValueError('Frações de biomas ausentes ou negativas.')
    tabela['soma_fracoes'] = tabela[colunas].sum(axis=1)
    if tabela.soma_fracoes.gt(1 + 1e-6).any():
        raise ValueError('Sobreposição de biomas excede a tolerância geométrica.')
    predominante = tabela[colunas].idxmax(axis=1).str.replace('biome_', '', regex=False).str.replace('_share_i', '', regex=False)
    for limiar in (70, 80, 90):
        tabela[f'biome_class_{limiar}'] = predominante.where(tabela[colunas].max(axis=1) >= limiar / 100, 'misto')
    log['checagens']['soma_fracoes_biomas_min_max'] = [float(tabela.soma_fracoes.min()), float(tabela.soma_fracoes.max())]
    salvar(tabela.reset_index(), 'h2__biome_share__ibge2019_malha2024__candidato.csv', log, ['codigo_ibge'])


def relevo(municipios, log):
    soma = np.zeros(142, dtype=np.float64)
    contagem = np.zeros(142, dtype=np.int64)
    minimo = np.full(142, np.inf)
    maximo = np.full(142, -np.inf)
    arquivos = sorted((DADOS / 'raw/raster/copdem90').glob('*.tif'))
    if len(arquivos) != 101:
        raise ValueError('Conferir os 101 tiles Copernicus locais antes de reextrair.')
    for i, arquivo in enumerate(arquivos, 1):
        log['entradas'].append(registro(arquivo))
        with rasterio.open(arquivo) as ds:
            pixels = pixels_municipais(ds, municipios)
            if pixels is None:
                continue
            labels, valores, _, _ = pixels
            soma += np.bincount(labels, weights=valores, minlength=142)
            contagem += np.bincount(labels, minlength=142)
            np.minimum.at(minimo, labels, valores)
            np.maximum.at(maximo, labels, valores)
        if i % 10 == 0:
            print(f'Relevo: {i}/{len(arquivos)} tiles', flush=True)
    if (contagem[1:] == 0).any():
        raise ValueError('Há município sem cobertura de relevo.')
    tabela = municipios[['CD_MUN', 'NM_MUN']].rename(columns={'CD_MUN': 'codigo_ibge', 'NM_MUN': 'municipio'}).copy()
    tabela['elevation_mean_m'] = soma[1:] / contagem[1:]
    tabela['elevation_min_m'] = minimo[1:]
    tabela['elevation_max_m'] = maximo[1:]
    tabela['n_pixels'] = contagem[1:]
    if not ((tabela.elevation_min_m <= tabela.elevation_mean_m) & (tabela.elevation_mean_m <= tabela.elevation_max_m)).all():
        raise ValueError('Média fora do intervalo mínimo-máximo.')
    salvar(tabela, 'topography__copdem90__municipio_candidato.csv', log, ['codigo_ibge'])


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    AUDITORIA.parent.mkdir(parents=True, exist_ok=True)
    municipios = gpd.read_file('zip://' + str(MALHA)).sort_values('CD_MUN').reset_index(drop=True)
    municipios['CD_MUN'] = municipios['CD_MUN'].astype(str)
    if len(municipios) != 141 or municipios.CD_MUN.duplicated().any() or municipios.CD_MUN.eq('5101837').any():
        raise ValueError('A malha deve ter exatamente os 141 municípios anteriores a Boa Esperança do Norte.')
    if not municipios.is_valid.all():
        raise ValueError('Malha original contém geometrias inválidas.')
    log = {'inicio_utc': datetime.now(timezone.utc).isoformat(), 'geografia_referencia': REFERENCIA,
           'metodos': {'gaez': 'centro do pixel; média ponderada por cos(latitude); nodata excluído',
                       'relevo': 'centro do pixel; média simples/mínimo/máximo; nodata excluído',
                       'biomas': 'interseção EPSG:5880 / área municipal inteira; sem renormalização'},
           'observacao_nome_arquivo': 'Basenames mantidos para substituir a fonte no notebook; geografia_referencia identifica malha2023 mesmo no basename biomas que menciona2024.',
           'entradas': [registro(MALHA), registro(BIOMAS)], 'saidas': [],
           'reparos_geometrias': [], 'checagens': {'municipios': len(municipios), 'codigo_5101837_presente': False}}
    gaez(municipios, log)
    biomas(municipios, log)
    relevo(municipios, log)
    log['fim_utc'] = datetime.now(timezone.utc).isoformat()
    log['script'] = registro(Path(__file__).resolve())
    AUDITORIA.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Auditoria:', AUDITORIA, flush=True)


if __name__ == '__main__':
    main()
