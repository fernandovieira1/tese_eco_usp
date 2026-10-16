"""Descriptive and exploratory metrics with explicit panel sample conventions."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def _numeric(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    missing = set(columns).difference(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {', '.join(sorted(missing))}")
    return df.loc[:, list(columns)].apply(pd.to_numeric, errors="coerce").astype(float).replace([np.inf, -np.inf], np.nan)


def panel_descriptive(
    df: pd.DataFrame,
    columns: Sequence[str] | None = None,
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
) -> pd.DataFrame:
    """Return sample SDs (ddof=1); between gives each municipality equal weight.

    Within SD is that of x_it - mean_i(x) + mean(x), on each variable's
    available observations. These three SDs do not form an additive variance
    decomposition in an unbalanced panel. A zero within SD cannot establish
    invariance in municipalities with only one observed year.
    """
    if entity_col not in df or time_col not in df:
        raise ValueError("As chaves de município e ano são necessárias.")
    if columns is None:
        columns = [c for c in df.select_dtypes(include=["number", "bool"]) if c not in (entity_col, time_col)]
    values = _numeric(df, list(dict.fromkeys(columns)))
    rows = []
    for col in values:
        x = values[col]
        valid = x.notna() & df[entity_col].notna() & df[time_col].notna()
        observed = x.loc[valid]
        ids = df.loc[valid, entity_col]
        means = observed.groupby(ids, observed=True).mean()
        within = observed - observed.groupby(ids, observed=True).transform("mean")
        normalized = within + observed.mean()
        sd = float(normalized.std(ddof=1)) if len(observed) > 1 else np.nan
        tolerance = 1e-12 * max(float(observed.abs().max()) if len(observed) else 0.0, np.finfo(float).tiny)
        invariant = bool(len(observed) > 1 and within.abs().max() <= tolerance)
        if invariant:
            sd = 0.0
        observed_years = df.loc[valid].groupby(entity_col, observed=True)[time_col].nunique()
        rows.append({
            "variable": col, "n_valid": int(valid.sum()),
            "missing_pct": 100.0 * (1 - valid.mean()) if len(df) else np.nan,
            "mean": observed.mean(), "median": observed.median(),
            "min": observed.min(), "max": observed.max(),
            "sd_overall": observed.std(ddof=1), "sd_between": means.std(ddof=1),
            "sd_within": sd, "time_invariant": invariant,
            "n_entities": len(means), "n_entities_repeated": int((observed_years > 1).sum()),
        })
    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(columns=["n_valid", "missing_pct", "mean", "median", "min", "max", "sd_overall", "sd_between", "sd_within", "time_invariant", "n_entities", "n_entities_repeated"]).rename_axis("variable")
    return result.set_index("variable")


def within_transform(
    df: pd.DataFrame,
    columns: Sequence[str],
    mode: str = "pooled",
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
    complete_cases: bool = True,
    tolerance: float = 1e-11,
    max_iter: int = 10_000,
) -> pd.DataFrame:
    """Residualize on entity or entity+year dummies; preserve other columns.

    The two-way operation uses alternating orthogonal projections, which is
    also correct for an unbalanced sample. A single x - mean_i - mean_t +
    mean pass is generally wrong when filters or missingness unbalance it.
    By default all selected variables use the same complete-case sample.
    With complete_cases=False each variable is projected on its own sample.
    Residual columns below the convergence tolerance relative to their input
    scale are set to exact zero. Otherwise floating-point noise in an absorbed
    proxy could generate spurious correlations or VIFs when reused downstream.
    """
    mode = {"within": "entity", "double": "twoway", "two_way": "twoway"}.get(mode, mode)
    if mode not in {"pooled", "entity", "twoway"}:
        raise ValueError("mode deve ser pooled, entity ou twoway.")
    columns = list(dict.fromkeys(columns))
    if any(c in (entity_col, time_col) for c in columns):
        raise ValueError("As chaves do painel não podem ser transformadas.")
    if tolerance <= 0 or max_iter < 1:
        raise ValueError("Tolerância e número de iterações devem ser positivos.")
    result = df.copy()
    result[columns] = _numeric(df, columns)
    keys = [] if mode == "pooled" else [entity_col] + ([time_col] if mode == "twoway" else [])
    for key in keys:
        if key not in result:
            raise ValueError(f"Chave ausente: {key}")
    if complete_cases:
        result = result.dropna(subset=columns + keys).copy()
    iterations = 0
    max_group_mean = 0.0
    absorbed_columns = []
    if mode != "pooled" and len(result) and columns:
        # Work by position; even a caller's duplicated dataframe index is safe.
        numeric = result[columns].to_numpy(dtype=float, copy=True)
        key_valid = result[keys].notna().all(axis=1).to_numpy()
        groups = [pd.factorize(result[key], sort=False)[0] for key in keys]
        # Shared samples are processed together; individual samples separately.
        batches = [list(range(len(columns)))] if complete_cases else [[j] for j in range(len(columns))]
        for batch in batches:
            valid = key_valid & np.isfinite(numeric[:, batch]).all(axis=1)
            if not valid.any():
                continue
            block = numeric[np.ix_(valid, batch)].copy()
            # Rescale per variable for a unit-invariant convergence criterion.
            scale = np.max(np.abs(block), axis=0)
            scale[scale == 0] = 1.0
            block /= scale
            codes = [g[valid] for g in groups]
            converged = False
            for iteration in range(1, max_iter + 1):
                before = block.copy()
                for group in codes:
                    _, compact = np.unique(group, return_inverse=True)
                    counts = np.bincount(compact)
                    sums = np.zeros((len(counts), len(batch)))
                    np.add.at(sums, compact, block)
                    block -= (sums / counts[:, None])[compact]
                if mode == "entity" or np.max(np.abs(block - before)) <= tolerance:
                    converged = True
                    break
            if not converged:
                raise RuntimeError(f"Projeção two-way não convergiu em {max_iter} iterações.")
            iterations = max(iterations, iteration)
            numerical_zero = np.max(np.abs(block), axis=0) <= tolerance
            if numerical_zero.any():
                block[:, numerical_zero] = 0.0
                absorbed_columns.extend(columns[batch[j]] for j in np.flatnonzero(numerical_zero))
            for group in codes:
                group_means = pd.DataFrame(block).groupby(group).mean().to_numpy()
                max_group_mean = max(max_group_mean, float(np.max(np.abs(group_means))))
            numeric[np.ix_(valid, batch)] = block * scale
            numeric[np.ix_(~valid, batch)] = np.nan
        result[columns] = numeric
    result.attrs.update({"transformation": mode, "iterations": iterations, "converged": True,
                         "max_scaled_group_mean": max_group_mean, "complete_cases": complete_cases,
                         "absorbed_columns": absorbed_columns,
                         "n_input": len(df), "n_output": len(result)})
    return result


def correlation_matrix(
    df: pd.DataFrame,
    columns: Sequence[str],
    method: str = "pearson",
    complete_cases: bool = True,
) -> pd.DataFrame:
    """Correlation matrix; attrs['pairwise_n'] makes sample size auditable."""
    if method not in {"pearson", "spearman"}:
        raise ValueError("Escolha pearson ou spearman.")
    values = _numeric(df, list(dict.fromkeys(columns)))
    if complete_cases:
        values = values.dropna()
    result = values.corr(method=method, min_periods=3)
    available = values.notna().astype(int)
    result.attrs["pairwise_n"] = available.T.dot(available)
    result.attrs["nobs"] = len(values)
    result.attrs["complete_cases"] = complete_cases
    return result


def calculate_vif(
    df: pd.DataFrame,
    columns: Sequence[str],
    mode: str = "pooled",
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
) -> pd.DataFrame:
    """VIF on a joint sample, with constants/absorbed terms explicitly reported.

    Auxiliary regressions include an intercept. Centering and normalization
    improve numerical stability without changing VIF. Exact dependencies
    produce infinity; a time-invariant variable after FE has undefined VIF.
    """
    columns = list(dict.fromkeys(columns))
    transformed = within_transform(df, columns, mode, entity_col, time_col)
    values = _numeric(transformed, columns).dropna()
    rows = []
    active = []
    standardized = {}
    for col in columns:
        centered = values[col].to_numpy() - values[col].mean()
        norm = np.linalg.norm(centered)
        raw_scale = np.linalg.norm(pd.to_numeric(df[col], errors="coerce").fillna(0).to_numpy(dtype=float))
        if len(values) < 3:
            rows.append({"variable": col, "vif": np.nan, "nobs": len(values), "status": "amostra insuficiente"})
        elif norm <= 1e-11 * max(raw_scale, np.finfo(float).tiny):
            rows.append({"variable": col, "vif": np.nan, "nobs": len(values), "status": "constante/absorvida"})
        else:
            active.append(col)
            standardized[col] = centered / norm
    for col in active:
        others = [standardized[c] for c in active if c != col]
        y = standardized[col]
        if not others:
            vif, status = 1.0, "única variável identificável"
        else:
            x = np.column_stack(others)
            residual = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
            unexplained = float(residual @ residual)
            vif = np.inf if unexplained <= 1e-12 else max(1.0, 1.0 / unexplained)
            status = "colinearidade perfeita" if np.isinf(vif) else "ok"
        rows.append({"variable": col, "vif": vif, "nobs": len(values), "status": status})
    return pd.DataFrame(rows, columns=["variable", "vif", "nobs", "status"])
