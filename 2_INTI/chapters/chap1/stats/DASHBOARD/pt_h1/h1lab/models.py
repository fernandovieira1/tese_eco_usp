"""Exploratory OLS, on an explicit joint sample, with optional dummy fixed effects."""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from .data import KEYS, filter_data, numeric, normalize_flag
from .panel_metrics import calculate_vif

TRANSFORMS = {'level': 'Nível original', 'log': 'ln(x), exige x > 0',
              'log1p': 'ln(1+x), exige x ≥ 0', 'zscore': 'Padronizar (z) na amostra comum'}
FIXED_EFFECTS = {'none': 'Sem efeitos fixos', 'entity': 'Município', 'year': 'Ano', 'twoway': 'Município + ano'}
COVARIANCES = {'HC3': 'Robustos HC3', 'cluster_entity': 'Cluster por município',
               'cluster_year': 'Cluster por ano', 'cluster_twoway': 'Cluster por município e ano',
               'nonrobust': 'Clássicos (homocedásticos)'}


def fingerprint(filters, spec, source_hash):
    return hashlib.sha256(json.dumps([filters, spec, source_hash], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def calendar_lag(df, column, lag):
    if lag == 0:
        return df[column].copy()
    if not isinstance(lag, int) or lag < 0:
        raise ValueError('Defasagem deve ser um inteiro não negativo.')
    if df.duplicated(KEYS).any():
        raise ValueError('Chaves duplicadas impedem a defasagem.')
    lookup = pd.Series(df[column].to_numpy(), index=pd.MultiIndex.from_arrays([df['codigo_ibge'], df['ano'] + lag]))
    target = pd.MultiIndex.from_frame(df[KEYS])
    return pd.Series(lookup.reindex(target).to_numpy(), index=df.index)


def prepare_sample(full, filters, spec):
    y, xs = spec['y'], spec['xs']
    if not xs or y in xs or len(xs) != len(set(xs)):
        raise ValueError('Escolha ao menos um X distinto de Y e sem repetição.')
    columns = [y, *xs]
    if any(c in KEYS for c in columns):
        raise ValueError('Identificadores não podem ser usados como variáveis de regressão.')
    work = full.copy()
    work[columns] = numeric(work, columns)
    quality = pd.Series(True, index=work.index)
    for col in columns:
        lag = int(spec.get('lags', {}).get(col, 0))
        work[col] = pd.to_numeric(calendar_lag(full, col, lag), errors='coerce').astype(float)
        if spec.get('require_y', True) and col.startswith(('conversao_ha__', 'taxa_conversao__')):
            flag = calendar_lag(full, 'y_cobertura_completa', lag)
            quality &= normalize_flag(flag).eq(True).fillna(False)
        method = spec.get('transforms', {}).get(col, 'level')
        if method not in TRANSFORMS:
            raise ValueError(f'Transformação desconhecida: {method}')
        if method == 'log':
            work[col] = np.log(work[col].where(work[col].gt(0)))
        elif method == 'log1p':
            work[col] = np.log1p(work[col].where(work[col].ge(0)))
    base = filter_data(work, filters)
    ledger = [{'etapa': 'Recorte territorial e temporal', 'N': len(base)}]
    base = base.loc[quality.reindex(base.index)]
    ledger.append({'etapa': 'Cobertura de Y (quando exigida)', 'N': len(base)})
    base[columns] = numeric(base, columns)
    missing = base[columns].isna().sum().rename('Indisponíveis antes da amostra comum').to_frame()
    base = base.dropna(subset=columns).copy()
    ledger.append({'etapa': 'Valores finitos e domínio das transformações: amostra comum', 'N': len(base)})
    scales = {}
    for col in columns:
        if spec.get('transforms', {}).get(col) == 'zscore':
            mean, sd = base[col].mean(), base[col].std(ddof=1)
            if not np.isfinite(sd) or sd <= 0:
                raise ValueError(f'Não há variação para padronizar {col}.')
            base[col] = (base[col] - mean) / sd
            scales[col] = {'mean': mean, 'sd': sd}
    terms = list(xs)
    for left, right in spec.get('interactions', []):
        if left not in xs or right not in xs or left == right:
            raise ValueError('Interações exigem dois Xs distintos e seus termos principais selecionados.')
        name = f'{left} × {right}'
        if name in terms:
            raise ValueError('Interação repetida.')
        base[name] = base[left] * base[right]
        terms.append(name)
    if len(base) and not np.isfinite(base[terms].to_numpy(float)).all():
        raise ValueError('A interação gerou valores não finitos; revise as unidades.')
    return base.reset_index(drop=True), terms, pd.DataFrame(ledger), missing, scales


def fit_model(full, filters, spec):
    sample, terms, ledger, missing, scales = prepare_sample(full, filters, spec)
    if len(sample) < 4:
        raise ValueError('Há menos de quatro observações válidas na amostra comum.')
    y = sample[spec['y']].astype(float)
    if y.nunique() < 2:
        raise ValueError('Y não varia na amostra comum; a regressão não é informativa.')
    design = pd.DataFrame({'const': np.ones(len(sample))})
    fe = spec.get('fe', 'none')
    if fe not in FIXED_EFFECTS:
        raise ValueError('Efeitos fixos desconhecidos.')
    for key, modes in [('codigo_ibge', ['entity', 'twoway']), ('ano', ['year', 'twoway'])]:
        if fe in modes:
            dummies = pd.get_dummies(sample[key].astype('string'), prefix=f'FE_{key}', drop_first=True, dtype=float)
            design = pd.concat([design, dummies], axis=1)
    # Check term identifiability after projecting on the complete FE design.
    effects = design.to_numpy(float)
    targets = np.column_stack([y.to_numpy(), sample[terms].to_numpy(float)])
    residuals = targets - effects @ np.linalg.lstsq(effects, targets, rcond=None)[0]
    residual_y = residuals[:, 0]
    if np.linalg.norm(residual_y) <= 1e-10 * max(np.linalg.norm(y), np.finfo(float).tiny):
        raise ValueError('Y é absorvida pelos efeitos fixos escolhidos.')
    unidentified = []
    for i, term in enumerate(terms):
        x = sample[term].to_numpy(float)
        residual = residuals[:, i + 1]
        if np.linalg.norm(residual) <= 1e-10 * max(np.linalg.norm(x), np.finfo(float).tiny):
            unidentified.append(term)
    if unidentified:
        raise ValueError('Xs constantes ou absorvidos pelos efeitos fixos: ' + '; '.join(unidentified) + '. Revise a especificação. Preços comuns são absorvidos por ano; atributos fixos, por município.')
    design = pd.concat([design, sample[terms].astype(float)], axis=1)
    norms = np.linalg.norm(design, axis=0)
    normalized = design.to_numpy(float) / np.where(norms > 0, norms, 1)
    rank = np.linalg.matrix_rank(normalized)
    if rank != design.shape[1]:
        raise ValueError('Colinearidade exata ou efeitos fixos redundantes: o desenho não tem posto completo. Remova proxies equivalentes ou revise a conectividade do painel.')
    if len(sample) <= rank + 1:
        raise ValueError('Graus de liberdade insuficientes para este número de Xs e efeitos fixos.')
    classical = sm.OLS(y, design, missing='raise').fit()
    if classical.model.rank != rank:
        raise ValueError('As escalas numéricas causaram perda de posto na estimação. Padronize os Xs ou revise unidades antes de estimar.')
    cov = spec.get('cov', 'HC3')
    messages, clusters = [], {}
    if cov == 'HC3':
        result = classical.get_robustcov_results(cov_type='HC3', use_t=True)
    elif cov == 'nonrobust':
        result = classical
        messages.append('Erros clássicos pressupõem homocedasticidade e ausência de dependência nos resíduos.')
    elif cov.startswith('cluster_'):
        cluster_keys = {'cluster_entity': ['codigo_ibge'], 'cluster_year': ['ano'], 'cluster_twoway': KEYS}.get(cov)
        if cluster_keys is None:
            raise ValueError('Covariância desconhecida.')
        groups = []
        for key in cluster_keys:
            codes, unique = pd.factorize(sample[key], sort=True)
            clusters[key] = len(unique)
            if len(unique) < 2:
                raise ValueError(f'Cluster em {key} exige pelo menos dois grupos.')
            if len(unique) < 30:
                messages.append(f'{len(unique)} clusters em {key}: aproximações assintóticas frágeis; verificar inferência em notebook.')
            groups.append(codes)
        groups = groups[0] if len(groups) == 1 else np.column_stack(groups)
        result = classical.get_robustcov_results(cov_type='cluster', groups=groups,
            use_correction=True, df_correction=True, use_t=True)
    else:
        raise ValueError('Covariância desconhecida.')
    # Nonrobust results preserve pandas wrappers; robust results return arrays.
    # Invalid two-way covariance diagonals are reported explicitly below.
    with np.errstate(invalid='ignore'):
        intervals = np.asarray(result.conf_int())
        standard_errors = np.asarray(result.bse)
        all_coef = pd.DataFrame({'term': design.columns, 'coef': np.asarray(result.params), 'se': standard_errors,
            't': np.asarray(result.tvalues), 'p': np.asarray(result.pvalues),
            'ci_low': intervals[:, 0], 'ci_high': intervals[:, 1]}).set_index('term')
    if not np.isfinite(all_coef['se']).all():
        messages.append('A covariância produziu erros-padrão indefinidos; os coeficientes podem ser exibidos, mas essa inferência não é utilizável.')
    condition = float(np.linalg.cond(normalized))
    if condition > 1e6:
        messages.append('Desenho mal condicionado, mesmo após ajuste das escalas: comparar proxies e VIF.')
    influence = classical.get_influence()
    diagnostics = sample[KEYS + ['municipio', 'bioma_dominante']].copy()
    diagnostics['observado'] = y.to_numpy()
    diagnostics['ajustado'] = classical.fittedvalues.to_numpy()
    diagnostics['residuo'] = classical.resid.to_numpy()
    diagnostics['residuo_padronizado'] = influence.resid_studentized_internal
    diagnostics['alavancagem'] = influence.hat_matrix_diag
    diagnostics['Cook'] = influence.cooks_distance[0]
    mode = {'none': 'pooled', 'entity': 'entity', 'twoway': 'twoway'}.get(fe, 'pooled')
    vif_input = sample.copy()
    if fe == 'year':
        vif_input[terms] = vif_input[terms] - vif_input.groupby('ano')[terms].transform('mean')
    vif = calculate_vif(vif_input, terms, mode=mode)
    sse = float(np.square(classical.resid).sum())
    within_r2 = 1 - sse / float(residual_y @ residual_y)
    summary = {'N': len(sample), 'Municípios': sample['codigo_ibge'].nunique(), 'Anos': sample['ano'].nunique(),
        'R2': classical.rsquared, 'R2 ajustado': classical.rsquared_adj,
        'R2 parcial aos efeitos fixos': within_r2, 'RMSE': np.sqrt(sse / len(sample)),
        'Graus de liberdade residuais': classical.df_resid,
        'Graus de liberdade da inferência': getattr(result, 'df_resid_inference', result.df_resid),
        'Condição (colunas normalizadas)': condition, 'clusters': clusters}
    return {'spec': spec, 'sample': sample, 'terms': terms, 'coefficients': all_coef.loc[['const', *terms]],
        'all_coefficients': all_coef, 'summary': summary, 'ledger': ledger, 'missing': missing,
        'scales': scales, 'diagnostics': diagnostics, 'vif': vif, 'warnings': messages,
        'fit': result, 'design': design}


def qq_data(residuals):
    theoretical, ordered = stats.probplot(np.asarray(residuals), dist='norm', fit=False)
    return pd.DataFrame({'Quantil normal teórico': theoretical, 'Resíduo ordenado': ordered})
