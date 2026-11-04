"""Exploratory TWFE comparisons for H1; no causal identification is implied."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import warnings

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from .panel_metrics import within_transform


COEFFICIENT_COLUMNS = [
    "model", "term", "coefficient", "std_error", "t_stat", "p_value", "ci_lower",
    "ci_upper", "nobs", "n_entities", "r2_within", "r2_twfe", "status",
]
INTERACTION_PREFIX = "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__"


def interaction_components(interaction: str) -> tuple[str, str]:
    """Resolve the exact price and fixed capacity encoded in the source name."""
    if not interaction.startswith(INTERACTION_PREFIX):
        raise ValueError("A hierarquia H1-b requer uma interação preço × capacidade identificável.")
    suffix = interaction[len(INTERACTION_PREFIX):]
    crop = suffix.split("__", 1)[0]
    return f"ln_preco_real_usd2024_media_anual_lag1__{crop}", f"capacidade_z__{suffix}"


def build_h1b_specification(
    df: pd.DataFrame,
    interaction: str,
    institutional: str,
    controls: Sequence[str] = (),
) -> tuple[pd.DataFrame, list[str], dict[str, str]]:
    """Build a full P*C*Z hierarchy, without modifying source columns or data.

    P and C are included and later reported as absorbed when appropriate.
    The partial effect with respect to P*C is beta_PC + beta_PCZ*Z only
    conditional on the other included interactions; beta_PCZ is not a causal
    enforcement estimate. An institutional log must be created before this.
    """
    price, capacity = interaction_components(interaction)
    required = [price, capacity, interaction, institutional, *controls]
    missing = sorted(set(required).difference(df.columns))
    if missing:
        raise ValueError(f"Colunas ausentes para a interação: {', '.join(missing)}")
    result = df.copy()
    price_z = f"produto__{price}__X__{institutional}"
    capacity_z = f"produto__{capacity}__X__{institutional}"
    triple = f"tripla__{interaction}__X__{institutional}"
    result[price_z] = pd.to_numeric(result[price], errors="coerce") * pd.to_numeric(result[institutional], errors="coerce")
    result[capacity_z] = pd.to_numeric(result[capacity], errors="coerce") * pd.to_numeric(result[institutional], errors="coerce")
    result[triple] = pd.to_numeric(result[interaction], errors="coerce") * pd.to_numeric(result[institutional], errors="coerce")
    terms = list(dict.fromkeys([price, capacity, institutional, interaction, price_z, capacity_z, triple, *controls]))
    labels = {price_z: f"P × Z: {institutional}", capacity_z: f"C × Z: {capacity} | {institutional}",
              triple: f"P × C × Z: {interaction} | {institutional}"}
    return result, terms, labels


def _connected_components(df: pd.DataFrame, entity_col: str, time_col: str) -> int:
    """Count components in the municipality/year incidence graph for FE rank."""
    parent: dict[tuple[str, object], tuple[str, object]] = {}

    def find(node: tuple[str, object]) -> tuple[str, object]:
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for entity, year in df[[entity_col, time_col]].itertuples(index=False, name=None):
        a, b = find(("i", entity)), find(("t", year))
        if a != b:
            parent[b] = a
    return len({find(node) for node in parent})


def fit_twfe(
    df: pd.DataFrame,
    dependent: str,
    regressors: Sequence[str],
    name: str = "Modelo",
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
) -> dict:
    """Fit municipality+year FE with municipality-clustered standard errors.

    Complete cases are selected before any projection. Absorbed and linearly
    dependent terms are diagnosed on exactly that sample, retaining the first
    independent terms in user order. All requested terms remain in the output.
    Regressors are centered/scaled internally for numerical stability; reported
    coefficients and SEs are returned to their original units.
    """
    regressors = list(dict.fromkeys(regressors))
    if not regressors:
        raise ValueError("Selecione pelo menos uma regressora.")
    if dependent in regressors or any(c in (entity_col, time_col) for c in regressors):
        raise ValueError("Y e chaves do painel não podem integrar a lista de regressoras.")
    required = [entity_col, time_col, dependent, *regressors]
    missing = sorted(set(required).difference(df.columns))
    if missing:
        raise ValueError(f"Colunas ausentes: {', '.join(missing)}")
    work = df[required].copy()
    for col in [dependent, *regressors]:
        work[col] = pd.to_numeric(work[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    work[time_col] = pd.to_numeric(work[time_col], errors="coerce")
    work = work.dropna().copy()
    if work.duplicated([entity_col, time_col]).any():
        raise ValueError("Há chaves município–ano duplicadas na amostra.")
    nobs = len(work)
    n_entities, n_years = work[entity_col].nunique(), work[time_col].nunique()
    if nobs < 5 or n_entities < 2 or n_years < 2:
        raise ValueError("TWFE exige observações válidas em pelo menos dois municípios e dois anos.")
    components = _connected_components(work, entity_col, time_col)
    if components != 1:
        raise ValueError("O painel filtrado possui componentes município–ano desconectados; amplie o recorte para estimar com graus de liberdade válidos.")
    transformed = within_transform(work, [dependent, *regressors], "twoway", entity_col, time_col)
    y_norm = np.linalg.norm(transformed[dependent].to_numpy())
    if y_norm <= 1e-11 * max(np.linalg.norm(work[dependent].to_numpy()), np.finfo(float).tiny):
        raise ValueError("Y não possui variação identificável após os dois efeitos fixos.")
    absorbed, collinear, retained = [], [], []
    basis: list[np.ndarray] = []
    for col in regressors:
        raw = work[col].to_numpy(dtype=float)
        vector = transformed[col].to_numpy(dtype=float)
        norm = np.linalg.norm(vector)
        scale = max(np.linalg.norm(raw - raw.mean()), np.finfo(float).tiny)
        if norm <= 1e-10 * scale or np.ptp(raw) == 0:
            absorbed.append(col)
            continue
        remainder = vector / norm
        # Reorthogonalization avoids a spurious independent column at high VIF.
        for _ in range(2):
            for q in basis:
                remainder = remainder - q * (q @ remainder)
        residual_norm = np.linalg.norm(remainder)
        if residual_norm <= 1e-9:
            collinear.append(col)
        else:
            retained.append(col)
            basis.append(remainder / residual_norm)
    if not retained:
        raise ValueError("Todas as regressoras são absorvidas ou colineares após os efeitos fixos.")
    expected_df = nobs - n_entities - n_years + 1 - len(retained)
    if expected_df <= 0:
        raise ValueError("A amostra não deixa graus de liberdade residuais após efeitos fixos e regressoras.")
    indexed = work.set_index([entity_col, time_col]).sort_index()
    scales = indexed[retained].std(ddof=0)
    x = (indexed[retained] - indexed[retained].mean()) / scales
    notices = []
    if n_entities < 30:
        notices.append(f"Apenas {n_entities} clusters; a aproximação assintótica exige cautela.")
    singleton_count = int((work.groupby(entity_col)[time_col].transform("size") == 1).sum())
    if singleton_count:
        notices.append(f"{singleton_count} observações de municípios singleton mantidas; não identificam variação within.")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = PanelOLS(indexed[dependent], x, entity_effects=True, time_effects=True,
                         drop_absorbed=True, check_rank=True)
        result = model.fit(cov_type="clustered", cluster_entity=True, debiased=True,
                           auto_df=True, group_debias=True)
        notices.extend(str(w.message) for w in caught)
    extra_absorbed = [c for c in retained if c not in result.params.index]
    absorbed.extend(extra_absorbed)
    estimated = list(result.params.index)
    ci = result.conf_int(level=0.95)
    rows = []
    for col in regressors:
        row = {"model": name, "term": col, "nobs": int(result.nobs), "n_entities": n_entities,
               "r2_within": float(result.rsquared_within), "r2_twfe": float(result.rsquared)}
        if col in estimated:
            row.update(coefficient=float(result.params[col] / scales[col]),
                       std_error=float(result.std_errors[col] / scales[col]),
                       t_stat=float(result.tstats[col]), p_value=float(result.pvalues[col]),
                       ci_lower=float(ci.loc[col, "lower"] / scales[col]),
                       ci_upper=float(ci.loc[col, "upper"] / scales[col]), status="estimated")
        else:
            row.update({key: np.nan for key in ["coefficient", "std_error", "t_stat", "p_value", "ci_lower", "ci_upper"]})
            row["status"] = "absorbed" if col in absorbed else "collinear"
        rows.append(row)
    diagnostics = {
        "model": name, "status": "ok", "message": "",
        "nobs": int(result.nobs), "n_entities": n_entities, "n_years": n_years,
        "df_resid": int(result.df_resid), "r2_within": float(result.rsquared_within),
        "r2_twfe": float(result.rsquared), "dropped_absorbed": "; ".join(absorbed),
        "dropped_collinear": "; ".join(collinear), "warnings": " | ".join(notices),
        "sample_mode": "própria", "n_input": len(df), "n_missing_dropped": len(df) - nobs,
        "covariance": "Cluster município; debiased=True; group_debias=True; auto_df=True",
        "ci_reference": "t com graus de liberdade residuais (padrão PanelOLS)",
    }
    return {"coefficients": pd.DataFrame(rows, columns=COEFFICIENT_COLUMNS),
            "diagnostics": diagnostics, "result": result, "scales": scales,
            "sample_index": indexed.index}


def horse_race(
    df: pd.DataFrame,
    dependent: str,
    specifications: Mapping[str, Sequence[str]],
    common_sample: bool = True,
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estimate candidates on a common sample by default; report every failure."""
    work = df.copy()
    if common_sample and specifications:
        union = list(dict.fromkeys([dependent, *[c for cols in specifications.values() for c in cols]]))
        missing = set(union).difference(work.columns)
        if missing:
            raise ValueError(f"Colunas ausentes na comparação: {', '.join(sorted(missing))}")
        work[union] = work[union].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
        work = work.dropna(subset=[entity_col, time_col, *union]).copy()
    tables, diagnostics = [], []
    for name, regressors in specifications.items():
        try:
            fitted = fit_twfe(work, dependent, regressors, name, entity_col, time_col)
            tables.append(fitted["coefficients"])
            diagnostic = fitted["diagnostics"]
        except (ValueError, RuntimeError, np.linalg.LinAlgError, ZeroDivisionError) as error:
            diagnostic = {"model": name, "status": "error", "message": str(error),
                          "nobs": 0, "n_entities": 0, "n_years": 0, "df_resid": np.nan,
                          "r2_within": np.nan, "r2_twfe": np.nan,
                          "dropped_absorbed": "", "dropped_collinear": "", "warnings": ""}
        diagnostic["sample_mode"] = "comum" if common_sample else "própria"
        diagnostic["n_global_input"] = len(df)
        diagnostic["n_common_sample"] = len(work) if common_sample else np.nan
        diagnostics.append(diagnostic)
    coefficients = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame(columns=COEFFICIENT_COLUMNS)
    return coefficients, pd.DataFrame(diagnostics)
