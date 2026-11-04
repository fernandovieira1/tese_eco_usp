"""Economic exploration on explicit samples and units, without changing sources.

These are descriptive views of the existing H1 variables, not new measures of
net returns, enforcement effectiveness, or causal effects. Rates remain fractions
in the API. In particular, a sum of annual fluxes divided by a sum of annual
initial stocks is an exposure-weighted annual rate, never an accumulated rate.
"""
from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np
import pandas as pd

from .panel_metrics import within_transform


ENTITY = "codigo_ibge"
TIME = "ano"
BIOME = "bioma_dominante"
DENOMINATOR = "y_nativa_inicial_ha"
DESTINATIONS = ("agricultura", "pastagem")
PRICE_LOW = "Baixo (≤ mediana)"
PRICE_HIGH = "Alto (> mediana)"


def _require(df: pd.DataFrame, columns: Sequence[str]) -> None:
    missing = set(columns).difference(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {', '.join(sorted(missing))}")


def _panel(df: pd.DataFrame) -> pd.DataFrame:
    _require(df, [ENTITY, TIME])
    if df[[ENTITY, TIME]].isna().any().any():
        raise ValueError("As chaves do painel não podem conter valores ausentes.")
    if df.duplicated([ENTITY, TIME]).any():
        raise ValueError("Há pares município × ano duplicados.")
    out = df.copy(deep=True).reset_index(drop=True)
    if BIOME not in out:
        out[BIOME] = "Não classificado"
    else:
        out[BIOME] = out[BIOME].astype("string").fillna("Não classificado")
    return out


def _number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype(float).replace([np.inf, -np.inf], np.nan)


def _stats(values: pd.Series) -> dict:
    values = _number(values)
    observed = values.dropna()
    positive = observed[observed.gt(0)]
    quantiles = observed.quantile([.01, .05, .25, .75, .95, .99])
    return {
        "n_total": len(values), "n_valid": len(observed),
        "n_missing": int(values.isna().sum()),
        "missing_pct": 100 * values.isna().mean() if len(values) else np.nan,
        "n_zero": int(observed.eq(0).sum()),
        "zero_pct": 100 * observed.eq(0).mean() if len(observed) else np.nan,
        "n_negative": int(observed.lt(0).sum()),
        "negative_pct": 100 * observed.lt(0).mean() if len(observed) else np.nan,
        "mean": observed.mean(), "median": observed.median(), "sd": observed.std(ddof=1),
        "min": observed.min(), "max": observed.max(),
        **{f"p{int(p * 100):02d}": quantiles.loc[p] for p in quantiles.index},
        "iqr": quantiles.loc[.75] - quantiles.loc[.25],
        "skewness": observed.skew(), "excess_kurtosis": observed.kurt(),
        "n_positive": len(positive), "mean_positive": positive.mean(),
    }


def _distribution_groups(sample: pd.DataFrame, column: str) -> pd.DataFrame:
    rows = []
    if column in sample:
        for name, group in sample.groupby(column, observed=True, sort=True, dropna=False):
            rows.append({column: name, **_stats(group["value"]),
                         "n_entities": group[ENTITY].nunique() if ENTITY in group else np.nan,
                         "n_years": group[TIME].nunique() if TIME in group else np.nan})
    return pd.DataFrame(rows)


def _fixed_lookup(df: pd.DataFrame, variable: str, key: str) -> pd.Series:
    values = df.groupby(key, observed=True)[variable]
    if values.nunique(dropna=True).gt(1).any():
        scope = "município" if key == ENTITY else "ano"
        raise ValueError(f"{variable} deve ter no máximo um valor observado por {scope} nesta análise.")
    # first() selects the first nonmissing value: repeated missing rows do not
    # erase a legitimate time-invariant municipal/annual observation.
    return values.first()


def univariate_summary(
    df: pd.DataFrame, variable: str, unit: str = "auto",
) -> dict:
    """Summarize one variable with a deliberate statistical observation unit.

    Auto uses one observation per year for common price series, and one per
    municipality for *verified* fixed capacity/geography/climate-normal columns.
    Explicit municipality/year modes summarize means of available observations.
    No municipality-year is upweighted merely because its fixed value repeats.
    Missing/zero percentages refer to the returned unit, with raw counts also
    reported in metadata. A positive-part mean is separate from the full mean.
    """
    if unit not in {"auto", "municipality_year", "municipality", "year"}:
        raise ValueError("Unidade deve ser auto, municipality_year, municipality ou year.")
    if variable in {ENTITY, TIME, BIOME}:
        raise ValueError("Selecione uma variável numérica de análise, além das chaves e da classificação do painel.")
    _require(df, [variable])
    out = _panel(df)
    out[variable] = _number(out[variable])
    requested = unit
    warnings = []
    if unit == "auto":
        if variable.startswith(("preco_nominal", "preco_real", "ln_preco", "dln_preco")):
            _fixed_lookup(out, variable, TIME)
            unit = "year"
        elif variable.startswith(("capacidade_valor__", "capacidade_z__", "biome_", "elevation_", "media_", "desvio_")):
            if out.groupby(ENTITY, observed=True)[variable].nunique().le(1).all():
                unit = "municipality"
            else:
                unit = "municipality_year"
                warnings.append("A variável não é fixa no recorte; foi preservada a unidade município-ano.")
        else:
            unit = "municipality_year"
    if unit == "municipality_year":
        sample = out[[ENTITY, TIME, BIOME, variable]].rename(columns={variable: "value"})
        aggregation = "Cada par município-ano disponível recebe peso igual."
    elif unit == "municipality":
        sample = out.groupby(ENTITY, observed=True, sort=True).agg(
            value=(variable, "mean"), bioma_dominante=(BIOME, "first"),
            observed_years=(TIME, "nunique"), valid_years=(variable, "count"),
        ).reset_index()
        aggregation = ("Um valor fixo por município, sem multiplicar os municípios pelo número de anos."
                       if requested == "auto" else
                       "Média temporal de cada município; cada município recebe peso igual.")
    else:
        sample = out.groupby(TIME, observed=True, sort=True).agg(
            value=(variable, "mean"), n_entities=(ENTITY, "nunique"),
            n_valid_entities=(variable, "count"),
        ).reset_index()
        aggregation = ("Um preço comum por ano; cada ano recebe peso igual."
                       if requested == "auto" else
                       "Média municipal disponível por ano; cada ano recebe peso igual.")
    stats = _stats(sample["value"])
    stats["variable"] = variable
    return {
        "sample": sample, "stats": stats,
        "by_biome": _distribution_groups(sample, BIOME),
        "annual": _distribution_groups(sample, TIME),
        "metadata": {"variable": variable, "unit": unit, "requested_unit": requested,
                     "unit_label": {"year": "ano", "municipality": "município",
                                    "municipality_year": "município-ano"}[unit],
                     "aggregation": aggregation, "warnings": warnings,
                     "input_nobs": len(out), "input_missing": int(out[variable].isna().sum()),
                     "input_entities": out[ENTITY].nunique(), "input_years": out[TIME].nunique(),
                     "zero_denominator": "Observações válidas; missings não entram na frequência de zeros."},
    }


def _destination_rows(group: pd.DataFrame, keys: dict | None = None) -> list[dict]:
    total = sum(group[f"conversao_ha__{d}"].sum() for d in DESTINATIONS)
    rows = []
    for destination in DESTINATIONS:
        rate = group[f"taxa_conversao__{destination}"]
        flux = group[f"conversao_ha__{destination}"].sum(min_count=1)
        denom = group[DENOMINATOR].sum(min_count=1)
        rows.append({**(keys or {}), "destination": destination,
                     "nobs": len(group), "n_entities": group[ENTITY].nunique(),
                     "n_years": group[TIME].nunique(), "conversion_ha": flux,
                     "denominator_ha_year": denom,
                     "weighted_rate": flux / denom if denom > 0 else np.nan,
                     "mean_rate": rate.mean(), "median_rate": rate.median(),
                     "zero_pct": 100 * rate.eq(0).mean() if len(group) else np.nan,
                     "share_two_destinations": flux / total if total > 0 else np.nan})
    return rows


def _destination_groups(sample: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    rows = []
    for keys, group in sample.groupby(list(columns), observed=True, sort=True, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        rows.extend(_destination_rows(group, dict(zip(columns, keys))))
    return pd.DataFrame(rows, columns=[*columns, *_destination_rows(sample.iloc[:0])[0]])


def economic_portrait(
    df: pd.DataFrame, reference: pd.DataFrame | None = None, balanced: bool = False,
) -> dict:
    """Common-destination flow sample, exposure rates, concentration and stocks.

    ``reference`` is the pre-quality-filter panel within the selected period and
    biome universe. It defines target years and sample attrition, never restores
    removed observations. Balanced means complete common-outcome coverage in
    every target year. Stocks are always a same-year cross section of ``df`` at
    the final target year, independently of the flow sample; their own N is shown.
    ``stocks_annual`` holds a separate, constant municipal cohort with valid
    stocks in every target year, so changes cannot come from sample composition.
    """
    out = _panel(df)
    ref = _panel(reference) if reference is not None else out
    columns = [DENOMINATOR] + [f"{prefix}__{d}" for d in DESTINATIONS
                              for prefix in ("conversao_ha", "taxa_conversao")]
    _require(out, columns)
    for column in columns:
        out[column] = _number(out[column])
    valid = out[columns].notna().all(axis=1) & out[DENOMINATOR].gt(0)
    valid &= out[columns[1:]].ge(0).all(axis=1)
    sample = out.loc[valid].copy()
    target_years = sorted(ref[TIME].unique().tolist())
    before_balance = len(sample)
    if balanced:
        target_set = set(target_years)
        available = sample.groupby(ENTITY, observed=True)[TIME].agg(set)
        eligible = available.map(lambda years: target_set.issubset(years))
        sample = sample.loc[sample[ENTITY].isin(eligible.index[eligible])].copy()
    sample["conversion_total_ha"] = sum(sample[f"conversao_ha__{d}"] for d in DESTINATIONS)
    concentration_rows, summary_rows = [], []
    for destination in (*DESTINATIONS, "total"):
        flux = "conversion_total_ha" if destination == "total" else f"conversao_ha__{destination}"
        municipal = sample.groupby(ENTITY, observed=True).agg(
            conversion_ha=(flux, "sum"), observed_years=(TIME, "nunique"),
            bioma_dominante=(BIOME, "first"),
        ).reset_index().sort_values(["conversion_ha", ENTITY], ascending=[False, True], kind="stable")
        n = len(municipal)
        total = municipal["conversion_ha"].sum()
        municipal["destination"] = destination
        municipal["rank"] = np.arange(1, n + 1)
        municipal["rank_fraction"] = municipal["rank"] / n if n else np.nan
        municipal["cumulative_share"] = municipal["conversion_ha"].cumsum() / total if total > 0 else np.nan
        concentration_rows.append(municipal)
        top_n = math.ceil(.1 * n)
        summary_rows.append({"destination": destination, "n_entities": n, "top_n": top_n,
                             "top10_share": municipal["conversion_ha"].head(top_n).sum() / total if total > 0 else np.nan})
    stock_columns = ["nativa_ha", "agricultura_ha", "pastagem_ha", "area_referencia_ha"]
    stock_year = max(target_years) if target_years else None
    stocks, stocks_annual = [], []
    stock_n = stock_series_n = 0
    if stock_year is not None and set(stock_columns).issubset(out.columns):
        stock_available = out.loc[out[TIME].isin(target_years), [ENTITY, TIME, *stock_columns]].copy()
        stock_available[stock_columns] = stock_available[stock_columns].apply(_number)
        stock_valid = stock_available[stock_columns].notna().all(axis=1)
        stock_valid &= stock_available[stock_columns].ge(0).all(axis=1)
        stock_valid &= stock_available["area_referencia_ha"].gt(0)
        stock_available = stock_available.loc[stock_valid]
        stock_sample = stock_available.loc[stock_available[TIME].eq(stock_year)]
        stock_n = len(stock_sample)
        denominator = stock_sample["area_referencia_ha"].sum(min_count=1)
        for use in ("nativa", "agricultura", "pastagem"):
            area = stock_sample[f"{use}_ha"].sum(min_count=1)
            stocks.append({"use": use, "ano": stock_year, "area_ha": area,
                           "reference_ha": denominator,
                           "share_reference": area / denominator if denominator > 0 else np.nan,
                           "n_entities": stock_n})
        # This cohort is selected from the already filtered panel. Reference
        # only defines the requested years; it must never resurrect rows that
        # the user's quality/biome/year filters excluded.
        target_set = set(target_years)
        covered = stock_available.groupby(ENTITY, observed=True)[TIME].agg(set)
        complete = covered.map(lambda years: target_set.issubset(years))
        cohort = stock_available.loc[stock_available[ENTITY].isin(complete.index[complete])]
        stock_series_n = int(cohort[ENTITY].nunique())
        for year, year_sample in cohort.groupby(TIME, observed=True, sort=True):
            denominator = year_sample["area_referencia_ha"].sum(min_count=1)
            for use in ("nativa", "agricultura", "pastagem"):
                area = year_sample[f"{use}_ha"].sum(min_count=1)
                stocks_annual.append({"use": use, "ano": year, "area_ha": area,
                                      "reference_ha": denominator,
                                      "share_reference": area / denominator if denominator > 0 else np.nan,
                                      "n_entities": stock_series_n})
    return {
        "sample": sample, "destinations": pd.DataFrame(_destination_rows(sample)),
        "by_biome": _destination_groups(sample, [BIOME]),
        "annual": _destination_groups(sample, [TIME]),
        "annual_by_biome": _destination_groups(sample, [BIOME, TIME]),
        "concentration": pd.concat(concentration_rows, ignore_index=True),
        "concentration_summary": pd.DataFrame(summary_rows),
        "stocks": pd.DataFrame(stocks, columns=["use", "ano", "area_ha", "reference_ha", "share_reference", "n_entities"]),
        "stocks_annual": pd.DataFrame(stocks_annual, columns=["use", "ano", "area_ha", "reference_ha", "share_reference", "n_entities"]),
        "metadata": {"n_input": len(out), "n_reference": len(ref), "n_common": len(sample),
                     "n_invalid_common": int((~valid).sum()), "n_removed_balance": before_balance - len(sample),
                     "balanced": bool(balanced), "target_years": target_years,
                     "n_entities": sample[ENTITY].nunique(), "n_years": sample[TIME].nunique(),
                     "stock_year": stock_year, "stock_entities": stock_n,
                     "stock_series_n_entities": stock_series_n,
                     "stock_series_n_years": len(target_years) if stock_series_n else 0,
                     "rate_definition": "Soma dos fluxos / soma dos estoques iniciais anuais; taxa anual ponderada por exposição, não acumulada.",
                     "composition_definition": "Participação apenas entre conversão para agricultura e pastagem na mesma amostra.",
                     "stock_definition": "Estoque no último ano do recorte, com cobertura comum das três classes e área de referência; não soma anos.",
                     "stock_series_definition": "Série anual de estoques na mesma coorte municipal em todos os anos do recorte, com cobertura conjunta das três classes e área de referência válida; respeita os filtros globais. Mudanças de área não identificam transições ou efeitos causais.",
                     "concentration_definition": "Fluxos brutos observados somados por município; top 10% arredondado para cima. Coberturas temporais diferentes podem afetar o ranking."},
    }


def _outcome_summary(group: pd.DataFrame, y: str) -> dict:
    observed = group[y].dropna()
    row = {"nobs": len(observed), "n_entities": group[ENTITY].nunique(),
           "n_years": group[TIME].nunique(), "mean_y": observed.mean(),
           "median_y": observed.median(),
           "zero_pct": 100 * observed.eq(0).mean() if len(observed) else np.nan,
           "conversion_ha": np.nan, "weighted_rate": np.nan, "n_weighted": 0}
    if y.startswith("taxa_conversao__"):
        flux_column = y.replace("taxa_conversao__", "conversao_ha__", 1)
        if flux_column in group and DENOMINATOR in group:
            flux, denominator = _number(group[flux_column]), _number(group[DENOMINATOR])
            valid = flux.notna() & flux.ge(0) & denominator.gt(0) & denominator.notna()
            denom = denominator.loc[valid].sum(min_count=1)
            row["conversion_ha"] = flux.loc[valid].sum(min_count=1)
            row["weighted_rate"] = row["conversion_ha"] / denom if denom > 0 else np.nan
            row["n_weighted"] = int(valid.sum())
    return row


def grouped_hypothesis(
    df: pd.DataFrame, capacity: str, price: str, institution: str | None = None,
    group_count: int = 3, y: str = "taxa_conversao__agricultura",
) -> dict:
    """Descriptive H1 cells and high-minus-low-price gaps, without causal claims.

    Capacity quantiles give each municipality one vote; tied values stay
    together. Price regimes use the median across unique years, not repeated
    panel rows. Institutions use observed zero and low/high positive readings,
    and never interpret a missing administrative record as zero here.
    """
    if not 2 <= int(group_count) <= 10:
        raise ValueError("Escolha entre 2 e 10 grupos de capacidade.")
    if len({y, capacity, price, *([institution] if institution else [])}) != 3 + bool(institution):
        raise ValueError("Selecione variáveis distintas para resultado, capacidade, preço e instituição.")
    needed = [y, capacity, price, *([institution] if institution else [])]
    _require(df, needed)
    out = _panel(df)
    for variable in needed:
        out[variable] = _number(out[variable])
    municipal_capacity = _fixed_lookup(out, capacity, ENTITY)
    annual_price = _fixed_lookup(out, price, TIME)
    valid_capacity = municipal_capacity.dropna()
    cap_map = pd.Series(pd.NA, index=municipal_capacity.index, dtype="string")
    if valid_capacity.nunique() <= 1:
        cap_map.loc[valid_capacity.index] = "C1 — capacidade única"
        capacity_groups = ["C1 — capacidade única"] if len(valid_capacity) else []
    else:
        codes = pd.qcut(valid_capacity, q=int(group_count), labels=False, duplicates="drop")
        unique_codes = sorted(codes.dropna().unique().tolist())
        code_labels = {code: f"C{j + 1}" + (" — único intervalo" if len(unique_codes) == 1 else " — menor" if j == 0 else " — maior" if j == len(unique_codes) - 1 else " — intermediária")
                       for j, code in enumerate(unique_codes)}
        cap_map.loc[codes.index] = codes.map(code_labels).astype("string")
        capacity_groups = list(code_labels.values())
    threshold = annual_price.dropna().median()
    out["capacity_group"] = out[ENTITY].map(cap_map)
    out["price_group"] = pd.Series(pd.NA, index=out.index, dtype="string")
    out.loc[out[price].notna() & out[price].le(threshold), "price_group"] = PRICE_LOW
    out.loc[out[price].notna() & out[price].gt(threshold), "price_group"] = PRICE_HIGH
    valid = out[needed].notna().all(axis=1) & out["capacity_group"].notna()
    # Rates with a negative reading are invalid outcomes, rather than zero.
    if y.startswith("taxa_conversao__"):
        valid &= out[y].ge(0)
    if institution:
        valid &= out[institution].ge(0)
    sample = out.loc[valid].copy()
    institution_median = np.nan
    sample["institution_group"] = "Sem estratificação"
    if institution:
        positive = sample.loc[sample[institution].gt(0), institution]
        institution_median = positive.median()
        sample.loc[sample[institution].eq(0), "institution_group"] = "Registro igual a zero"
        sample.loc[sample[institution].gt(0) & sample[institution].le(institution_median), "institution_group"] = "Registro positivo ≤ mediana"
        sample.loc[sample[institution].gt(institution_median), "institution_group"] = "Registro positivo > mediana"
    group_columns = ["capacity_group", "price_group", "institution_group"]
    metrics = list(_outcome_summary(sample.iloc[:0], y))
    rows = []
    for keys, group in sample.groupby(group_columns, observed=True, sort=True):
        rows.append({**dict(zip(group_columns, keys)), **_outcome_summary(group, y)})
    table = pd.DataFrame(rows, columns=[*group_columns, *metrics])
    annual_columns = [TIME, "capacity_group", "institution_group"]
    annual_rows = []
    for keys, group in sample.groupby(annual_columns, observed=True, sort=True):
        annual_rows.append({**dict(zip(annual_columns, keys)), **_outcome_summary(group, y)})
    gap_rows = []
    for keys, group in table.groupby(["capacity_group", "institution_group"], observed=True, sort=True):
        lookup = group.set_index("price_group")
        low = lookup.loc[PRICE_LOW] if PRICE_LOW in lookup.index else {}
        high = lookup.loc[PRICE_HIGH] if PRICE_HIGH in lookup.index else {}
        record = dict(zip(["capacity_group", "institution_group"], keys))
        for metric in ("mean_y", "weighted_rate"):
            record[f"low_{metric}"] = low.get(metric, np.nan)
            record[f"high_{metric}"] = high.get(metric, np.nan)
            record[f"gap_{metric}"] = record[f"high_{metric}"] - record[f"low_{metric}"]
        record.update(n_low=low.get("nobs", 0), n_high=high.get("nobs", 0))
        gap_rows.append(record)
    gaps = pd.DataFrame(gap_rows, columns=["capacity_group", "institution_group", "low_mean_y", "high_mean_y",
                                         "gap_mean_y", "low_weighted_rate", "high_weighted_rate", "gap_weighted_rate",
                                         "n_low", "n_high"])
    return {
        "sample": sample, "table": table, "gaps": gaps,
        "annual": pd.DataFrame(annual_rows, columns=[*annual_columns, *metrics]),
        "metadata": {"y": y, "capacity": capacity, "price": price, "institution": institution,
                     "n_input": len(out), "nobs": len(sample), "n_excluded": len(out) - len(sample),
                     "n_missing_inputs": int(out[needed].isna().any(axis=1).sum()),
                     "capacity_groups": capacity_groups, "requested_groups": int(group_count),
                     "actual_groups": len(capacity_groups),
                     "capacity_entities": len(valid_capacity), "price_years": int(annual_price.notna().sum()),
                     "price_threshold": threshold, "institution_positive_median": institution_median,
                     "price_low_label": PRICE_LOW, "price_high_label": PRICE_HIGH,
                     "capacity_definition": "Quantis dos valores municipais observados no recorte, sem quebrar empates.",
                     "price_definition": "Mediana de um preço por ano no recorte, antes da exclusão por resultado/instituição ausente.",
                     "institution_definition": "Zero observado e positivos abaixo/acima da mediana dos pares utilizados; não mede efetividade.",
                     "gap_definition": "Diferença descritiva entre regimes de preço; não é diferenças-em-diferenças, efeito causal ou teste de H1."},
    }


def multivariate_partial(
    df: pd.DataFrame, y: str, x: str, controls: Sequence[str] = (), mode: str = "twoway",
) -> dict:
    """FWL partial association on one complete-case sample for every projection.

    Both outcome and exposure are projected on the same controls after the
    selected fixed effects. The partial slope is a descriptive point estimate;
    no iid confidence bands are attached to dependent panel observations.
    """
    controls = list(dict.fromkeys(controls))
    if y == x or y in controls or x in controls:
        raise ValueError("Y, X e controles devem ser variáveis distintas.")
    out = _panel(df)
    selected = [y, x, *controls]
    _require(out, selected)
    for column in selected:
        out[column] = _number(out[column])
    common = out.dropna(subset=selected).copy()
    if len(common) < 3:
        raise ValueError("São necessários ao menos três pares completos na amostra conjunta.")
    transformed = within_transform(common, selected, mode=mode)
    n = len(transformed)
    # The intercept covers pooled estimates and harmless numerical centering
    # after FE. Unit-normalized controls prevent large nominal monetary units
    # from hiding smaller but linearly independent controls in an SVD.
    design_columns = [np.ones(n)]
    absorbed = []
    for column in controls:
        values = transformed[column].to_numpy(dtype=float)
        centered = values - values.mean()
        norm = np.linalg.norm(centered)
        original = np.linalg.norm(common[column].to_numpy(dtype=float))
        if norm <= 1e-11 * max(original, np.finfo(float).tiny):
            absorbed.append(column)
        else:
            design_columns.append(centered / norm)
    design = np.column_stack(design_columns)
    rank = int(np.linalg.matrix_rank(design))
    if n - rank < 2:
        raise ValueError("A amostra é insuficiente para residualizar estes controles e estimar uma relação parcial.")
    residuals = {}
    for variable, residual_name in ((x, "x_partial"), (y, "y_partial")):
        values = transformed[variable].to_numpy(dtype=float)
        residuals[residual_name] = values - design @ np.linalg.lstsq(design, values, rcond=None)[0]
    rx, ry = residuals["x_partial"], residuals["y_partial"]
    original_x_norm = np.linalg.norm(common[x].to_numpy(dtype=float))
    if np.linalg.norm(rx) <= 1e-11 * max(original_x_norm, np.finfo(float).tiny):
        raise ValueError("X não tem variação identificável depois dos efeitos e controles selecionados.")
    original_y_norm = np.linalg.norm(common[y].to_numpy(dtype=float))
    if np.linalg.norm(ry) <= 1e-11 * max(original_y_norm, np.finfo(float).tiny):
        ry = np.zeros_like(ry)
    sample = common.copy()
    sample["x_partial"], sample["y_partial"] = rx, ry
    slope = float(rx @ ry / (rx @ rx))
    correlation = float(np.corrcoef(rx, ry)[0, 1]) if np.linalg.norm(ry) > 0 else np.nan
    return {"sample": sample, "slope": slope, "correlation": correlation, "nobs": n,
            "metadata": {"y": y, "x": x, "controls": controls, "mode": mode,
                         "n_input": len(out), "n_excluded": len(out) - n,
                         "n_entities": common[ENTITY].nunique(), "n_years": common[TIME].nunique(),
                         "controls_rank_with_intercept": rank, "absorbed_controls": absorbed,
                         "collinear_controls": len(design_columns) - rank,
                         "definition": "Resíduos de Y e X em relação aos mesmos efeitos e controles, estimados na mesma amostra completa.",
                         "inference": "Inclinação associativa, sem IC iid; inferência clusterizada pertence ao laboratório econométrico."}}
