"""Pure descriptive calculations with explicit observational units and coverage."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from .data import KEYS, numeric, outcome_coverage
from .economic_metrics import _stats
from .panel_metrics import within_transform


def distribution(df, variable, variation, unit='Automática'):
    out = df[[*KEYS, 'municipio', 'bioma_dominante', variable]].copy()
    out[variable] = numeric(out, [variable])[variable]
    if unit == 'Automática':
        unit = {'Comum por ano': 'Ano', 'Fixa por município': 'Município'}.get(variation, 'Município-ano')
    if unit == 'Ano':
        sample = out.groupby('ano', as_index=False).agg(value=(variable, 'mean'), n_valid=(variable, 'count'))
        sample['bioma_dominante'] = 'Todos'
    elif unit == 'Município':
        sample = out.groupby('codigo_ibge', as_index=False).agg(value=(variable, 'mean'),
            municipio=('municipio', 'first'), bioma_dominante=('bioma_dominante', 'first'), n_valid=(variable, 'count'))
    else:
        sample = out.rename(columns={variable: 'value'})
    return {'sample': sample, 'stats': _stats(sample['value']), 'unit': unit}


def density(values):
    x = pd.to_numeric(values, errors='coerce').replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(x) < 3 or len(np.unique(x)) < 2 or np.ptp(x) <= 1e-12 * max(np.max(np.abs(x)), np.finfo(float).tiny):
        return pd.DataFrame(columns=['value', 'density'])
    # Scott bandwidth; restrict visual support to the observed domain. No trimming.
    grid = np.linspace(x.min(), x.max(), 240)
    return pd.DataFrame({'value': grid, 'density': gaussian_kde(x)(grid)})


def quality(df, catalog):
    rows = []
    for col in catalog.index:
        s = df[col]
        finite = numeric(df, [col])[col] if catalog.loc[col, 'numeric'] else s
        n = int(finite.notna().sum())
        zeros = int(finite.eq(0).fillna(False).sum()) if catalog.loc[col, 'numeric'] else 0
        rows.append({'variable': col, 'bloco': catalog.loc[col, 'block'], 'N total': len(df),
            'N válido': n, 'Ausentes': int(s.isna().sum()),
            'Não finitos': int(s.notna().sum()) - n,
            '% indisponível': 100 * (len(df) - n) / len(df) if len(df) else np.nan,
            'Zeros': zeros, '% zeros entre válidos': 100 * zeros / n if n else np.nan,
            'Valores distintos': finite.nunique(dropna=True)})
    return pd.DataFrame(rows).set_index('variable')


def balanced_sample(df, variables, years):
    clean = df.copy()
    clean[list(variables)] = numeric(clean, variables)
    clean = clean.dropna(subset=list(variables))
    available = clean.groupby('codigo_ibge')['ano'].agg(set)
    ids = available.index[available.map(lambda y: set(years).issubset(y))]
    return clean.loc[clean['codigo_ibge'].isin(ids)].copy()


def time_series(df, variable, aggregation='Média', by_biome=False, balanced=False, years=None, require_y=True):
    target_years = sorted(df['ano'].unique()) if years is None else list(years)
    base = outcome_coverage(df, [variable], require_y)
    cols = [variable]
    if aggregation == 'Taxa ponderada pela vegetação inicial':
        if not variable.startswith('taxa_conversao__'):
            raise ValueError('Ponderação disponível apenas para a taxa de conversão.')
        flux = variable.replace('taxa_conversao__', 'conversao_ha__')
        cols += [flux, 'y_nativa_inicial_ha']
    base[cols] = numeric(base, cols)
    if aggregation == 'Taxa ponderada pela vegetação inicial':
        base = base.loc[base['y_nativa_inicial_ha'].gt(0) & base[flux].ge(0)]
    if balanced:
        base = balanced_sample(base, cols, target_years)
    groups = ['bioma_dominante', 'ano'] if by_biome else ['ano']
    rows = []
    for keys, g in base.groupby(groups, observed=True):
        keys = keys if isinstance(keys, tuple) else (keys,)
        record = dict(zip(groups, keys))
        valid = g.dropna(subset=cols)
        if aggregation == 'Média':
            value = valid[variable].mean()
        elif aggregation == 'Mediana':
            value = valid[variable].median()
        elif aggregation == 'Soma':
            value = valid[variable].sum(min_count=1)
        elif aggregation == 'Taxa ponderada pela vegetação inicial':
            value = valid[flux].sum(min_count=1) / valid['y_nativa_inicial_ha'].sum(min_count=1) if len(valid) else np.nan
        else:
            raise ValueError('Agregação desconhecida.')
        rows.append({**record, 'value': value, 'N municípios': valid['codigo_ibge'].nunique(),
                     'N disponíveis': len(g), 'mediana': valid[variable].median(),
                     'p25': valid[variable].quantile(.25), 'p75': valid[variable].quantile(.75)})
    result = pd.DataFrame(rows, columns=[*groups, 'value', 'N municípios', 'N disponíveis', 'mediana', 'p25', 'p75'])
    # Keep missing years explicit, so lines never bridge absent calendar observations.
    if by_biome:
        grid = pd.MultiIndex.from_product([sorted(df['bioma_dominante'].unique()), target_years], names=groups)
        result = result.set_index(groups).reindex(grid).reset_index()
    else:
        result = result.set_index('ano').reindex(target_years).rename_axis('ano').reset_index()
        result['bioma_dominante'] = 'Todos'
    return result, base


def relationship_sample(df, columns, mode='pooled', complete_cases=True):
    base = df.copy()
    base[columns] = numeric(base, columns)
    if mode == 'between':
        if complete_cases:
            base = base.dropna(subset=columns)
        out = base.groupby('codigo_ibge', as_index=False).agg(
            {**{c: 'mean' for c in columns}, 'municipio': 'first', 'bioma_dominante': 'first'})
        return out
    return within_transform(base, columns, mode=mode, complete_cases=complete_cases)


def concentration(values):
    x = np.sort(np.asarray(values, dtype=float))
    x = x[np.isfinite(x)]
    if not len(x) or (x < 0).any() or x.sum() <= 0:
        return np.nan, pd.DataFrame(columns=['população', 'valor'])
    n = len(x)
    gini = 2 * np.dot(np.arange(1, n + 1), x) / (n * x.sum()) - (n + 1) / n
    return gini, pd.DataFrame({'população': np.arange(n + 1) / n, 'valor': np.r_[0., x.cumsum() / x.sum()]})
