"""Canonical data and literal dictionary; no writes, imputation or hidden filters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

APP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in APP.parents if (p / '2_INTI/RESEARCH_PROTOCOL.md').is_file())
CSV = ROOT / '2_INTI/xdata/chap1/processed/harmonizacao/painel_notebook/paineis/painel_tese_chap1_pt.csv'
DICIO = ROOT / '2_INTI/chapters/chap1/stats/EDA/aed_chap1_pt_DICIO.ipynb'
MUNICIPIOS = ROOT / '2_INTI/xdata/chap1/processed/territorio_141/municipios_referencia.json'
SELECTION = APP / 'config/selection.json'
KEYS = ['codigo_ibge', 'ano']
BIOMES = ['Amazônia', 'Cerrado', 'Pantanal']
BIOME_COLUMNS = ['biome_amazonia_share_i', 'biome_cerrado_share_i', 'biome_pantanal_share_i']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dictionary(path=DICIO):
    nb = json.loads(Path(path).read_text(encoding='utf-8'))
    # The canonical dictionary is stored as Python comment cells, not markdown.
    text = '\n'.join(''.join(c['source']) for c in nb['cells'])
    rows = {}
    for name, definition in re.findall(r'^#\d+\s*-\s*([^:\n]+):\s*(.+)$', text, re.M):
        parts = definition.split('|')
        rows.setdefault(name.strip(), {'definition': parts[0].strip(),
            'unit': parts[1].strip() if len(parts) > 1 else '',
            'scope': '|'.join(parts[2:]).strip()})
    return rows


def normalize_flag(series):
    tokens = series.astype('string').str.strip().str.lower()
    mapping = {'true': True, 'false': False, '1': True, '0': False, '1.0': True, '0.0': False}
    absent = series.isna() | tokens.isin(['', 'nan', 'none', '<na>'])
    if (~absent & ~tokens.isin(mapping)).any():
        raise ValueError(f'Flag inválida: {series.name}')
    return tokens.map(mapping).mask(absent).astype('boolean')


def block(name, is_flag=False):
    if is_flag:
        return 'Qualidade e cobertura'
    if name.startswith(('interacao_', 'exposicao_')):
        return 'Preços × capacidade e biomas'
    if 'preco' in name:
        return 'Preços internacionais'
    if 'ibama' in name:
        return 'Instituições · IBAMA'
    if name.startswith(('capacidade_', 'rendimento_')):
        return 'Capacidade e produtividade'
    if name.startswith(('conversao_', 'taxa_conversao_', 'y_')):
        return 'Conversão de vegetação nativa'
    if name.startswith(('precip_', 'media_', 'desvio_', 'count_', 'meses_', 'fracao_pixels_')):
        return 'Clima e precipitação'
    if name.startswith(('biome_', 'elevation_', 'soma_fracoes')):
        return 'Biomas e relevo'
    if any(s in name for s in ['bovino', 'lotacao']):
        return 'Pecuária'
    return 'Estoques e uso da terra'


def variation(series, df):
    """Classify on the full panel, never infer time invariance from a one-year filter."""
    if series.notna().sum() == 0:
        return 'Sem observações'
    if series.nunique() <= 1:
        return 'Constante'
    if series.groupby(df['ano']).nunique().le(1).all():
        return 'Comum por ano'
    if series.groupby(df['codigo_ibge']).nunique().le(1).all():
        return 'Fixa por município'
    return 'Município-ano'


def load_data(csv=CSV):
    raw = pd.read_csv(csv, encoding='utf-8-sig', low_memory=False)
    if raw.columns.duplicated().any():
        raise ValueError('Nomes de coluna duplicados.')
    for key in KEYS:
        values = pd.to_numeric(raw[key], errors='coerce')
        if not np.isfinite(values).all() or not values.eq(np.floor(values)).all():
            raise ValueError(f'Chave inválida: {key}.')
        raw[key] = values.astype('int64')
    raw['codigo_ibge'] = raw['codigo_ibge'].astype('string')
    if not raw['codigo_ibge'].str.fullmatch(r'\d{7}').all() or raw.duplicated(KEYS).any():
        raise ValueError('Código IBGE inválido ou par município-ano duplicado.')
    definitions = dictionary()
    selection = json.loads(SELECTION.read_text(encoding='utf-8'))
    missing = set(selection['columns']) - set(raw.columns)
    if missing:
        raise ValueError(f'O painel não contém as colunas selecionadas: {sorted(missing)}')
    if set(raw.columns) - set(definitions):
        raise ValueError('O dicionário não cobre todas as colunas do painel.')
    rows = []
    for col in raw:
        entry = definitions[col]
        is_flag = entry['unit'].startswith('booleano')
        if is_flag:
            raw[col] = normalize_flag(raw[col])
        numeric = pd.api.types.is_numeric_dtype(raw[col]) and col not in KEYS
        rows.append({'variable': col, **entry, 'block': block(col, is_flag),
                     'selected': col in selection['columns'], 'numeric': numeric,
                     'flag': is_flag, 'variation': variation(raw[col], raw),
                     'dtype': str(raw[col].dtype)})
    catalog = pd.DataFrame(rows).set_index('variable')
    df = raw.sort_values(KEYS, kind='stable').reset_index(drop=True).copy(deep=True)
    names = pd.DataFrame(json.loads(MUNICIPIOS.read_text(encoding='utf-8')))
    lookup = names.set_index(names['codigo_ibge'].astype('string'))['municipio']
    df['municipio'] = df['codigo_ibge'].map(lookup).fillna(df['codigo_ibge'])
    shares = df[BIOME_COLUMNS].apply(pd.to_numeric, errors='coerce')
    # Spatial sums can exceed one by ~1e-14 in the source. Match pt_dex's
    # numerical tolerance without modifying or renormalizing source shares.
    valid = np.isfinite(shares).all(axis=1) & shares.ge(-1e-10).all(axis=1) & shares.le(1 + 1e-10).all(axis=1) & shares.sum(axis=1).gt(0)
    df['bioma_dominante'] = shares.idxmax(axis=1).map(dict(zip(BIOME_COLUMNS, BIOMES))).where(valid, 'Não classificado')
    df['empate_biomas'] = (shares.eq(shares.max(axis=1), axis=0).sum(axis=1) > 1) & valid
    nb_path = ROOT / selection['notebook']
    nb = json.loads(nb_path.read_text(encoding='utf-8'))
    code = '\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code')
    text_hashes = {p: sha256(ROOT / p) for p in selection.get('text_sources_sha256', {})}
    meta = {'csv': str(Path(csv).relative_to(ROOT)), 'csv_sha256': sha256(csv),
            'dictionary_sha256': sha256(DICIO), 'selection_sha256': sha256(SELECTION),
            'notebook_code_sha256': hashlib.sha256(code.encode()).hexdigest(),
            'selection_matches_notebook': hashlib.sha256(code.encode()).hexdigest() == selection['code_sha256'],
            'text_sources_sha256': text_hashes,
            'text_bridge_matches_sources': text_hashes == selection.get('text_sources_sha256', {}),
            'rows': len(df), 'source_columns': len(raw.columns), 'selected_columns': len(selection['columns']),
            'biome_rule': 'Maior fração; tolerância de domínio 1e-10 sem alterar frações; empates seguem Amazônia, Cerrado, Pantanal. Não representa exclusividade territorial.',
            'treatment': 'Sem imputação, winsorização ou exclusão de outliers; não finitos viram ausências apenas nos cálculos.'}
    return df, catalog, meta


def filter_data(df, filters):
    lo, hi = filters['years']
    mask = df['ano'].between(lo, hi) & df['bioma_dominante'].isin(filters['biomes'])
    if filters.get('municipalities'):
        mask &= df['codigo_ibge'].isin(filters['municipalities'])
    return df.loc[mask].copy()


def outcome_coverage(df, variables, required=True):
    """Y quality is an analysis-level decision, never an invisible global filter."""
    if required and any(v.startswith(('taxa_conversao__', 'conversao_ha__')) for v in variables):
        if 'y_cobertura_completa' not in df:
            raise ValueError('A flag de cobertura de Y não está disponível.')
        return df.loc[normalize_flag(df['y_cobertura_completa']).eq(True).fillna(False)].copy()
    return df.copy()


def numeric(df, columns):
    return df[list(columns)].apply(pd.to_numeric, errors='coerce').astype(float).replace([np.inf, -np.inf], np.nan)
