"""Leitura, catálogo teórico e tratamentos explícitos do painel H1.

O CSV de origem nunca é escrito. Ausência de registro IBAMA é convertida em
zero somente quando a flag correspondente é explicitamente verdadeira. Para
variáveis defasadas, a flag também é defasada por ano civil exato, antes dos
filtros da interface; não há inferência sobre o ano anterior ao início do CSV.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import re

import numpy as np
import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
CSV_NAME = "painel_tese_chap1_pt.csv"
DEFAULT_CSV = APP_DIR / CSV_NAME
BIOMES = ("Amazônia", "Cerrado", "Pantanal")
BIOME_COLUMNS = (
    "biome_amazonia_share_i", "biome_cerrado_share_i", "biome_pantanal_share_i"
)
BLOCKS = (
    "[Y] Conversão e Uso da Terra",
    "[X1] Preços e Choques",
    "[X2] Capacidade Produtiva (PAM vs GAEZ)",
    "[X1*X2] Interações e Exposição",
    "[X3] Ambiente Institucional (IBAMA)",
    "[Controles] Clima, Geografia e Biomas",
    "[Flags] Auditoria e Qualidade",
)
BOOLEAN_COLUMNS = {
    "y_cobertura_completa", "grade_fonte_completa",
    "completude_classes_fora_grade_certificada", "geografia_historica_validada",
    "compatibilidade_datas_estoques_validada",
}
IBAMA_SOURCES = ("ibama_informada", "ibama_espacial")


def normalize_flag(series: pd.Series) -> pd.Series:
    """Parse flags as nullable Boolean; never interpret the string 'False' as True."""
    if pd.api.types.is_bool_dtype(series.dtype):
        return series.astype("boolean")
    tokens = series.astype("string").str.strip().str.lower()
    mapping = {"true": True, "false": False, "1": True, "0": False,
               "1.0": True, "0.0": False}
    absent = series.isna() | tokens.isin(["", "nan", "none", "<na>"])
    invalid = ~absent & ~tokens.isin(mapping)
    if invalid.any():
        examples = series.loc[invalid].astype(str).unique()[:4].tolist()
        raise ValueError(f"Flag {series.name!r} contém valores não booleanos: {examples}")
    return tokens.map(mapping).mask(absent).astype("boolean")


def flag_mask(series: pd.Series, value: bool = True) -> pd.Series:
    """Return a strict filter: missing/unknown flags never satisfy either value."""
    return normalize_flag(series).eq(value).fillna(False).astype(bool)


def validate_panel_keys(df: pd.DataFrame) -> None:
    """Require one observation per municipality and calendar year."""
    missing = {"codigo_ibge", "ano"}.difference(df.columns)
    if missing:
        raise ValueError(f"Chaves obrigatórias ausentes: {sorted(missing)}")
    if df[["codigo_ibge", "ano"]].isna().any().any():
        raise ValueError("codigo_ibge e ano não podem conter valores ausentes.")
    numeric_keys = {}
    for name in ("codigo_ibge", "ano"):
        numeric = pd.to_numeric(df[name], errors="coerce")
        if not np.isfinite(numeric).all() or not numeric.eq(np.floor(numeric)).all():
            raise ValueError(f"A chave {name} deve conter apenas inteiros finitos.")
        numeric_keys[name] = numeric
    if pd.DataFrame(numeric_keys).duplicated().any():
        raise ValueError("Há chaves codigo_ibge × ano duplicadas; a carga foi interrompida.")


def add_calendar_ibama_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Attach t-1 flags by exact key; a missing calendar year stays unknown.

    Existing lag flags are retained: load_panel computes them on the full panel,
    so subsequently removing a year must not erase its information for t+1.
    """
    validate_panel_keys(df)
    out = df.copy(deep=True)
    for source in IBAMA_SOURCES:
        current = f"flag_sem_registro_identificado__{source}"
        lagged = f"flag_sem_registro_identificado_lag1__{source}"
        if lagged in out:
            out[lagged] = normalize_flag(out[lagged])
            continue
        if current not in out:
            continue
        codes = pd.to_numeric(out["codigo_ibge"])
        years = pd.to_numeric(out["ano"])
        keys = pd.MultiIndex.from_arrays([codes, years + 1])
        lookup = pd.Series(normalize_flag(out[current]).array, index=keys)
        requested = pd.MultiIndex.from_arrays([codes, years])
        out[lagged] = pd.array(lookup.reindex(requested).to_numpy(), dtype="boolean")
    return out


def add_dominant_biome(df: pd.DataFrame) -> pd.DataFrame:
    """Argmax of valid shares; ties follow BIOMES order and are explicitly flagged.

    A row with any missing/out-of-domain share or no positive total is left
    unclassified. Dominance does not imply that the municipality has one biome.
    """
    missing = set(BIOME_COLUMNS).difference(df.columns)
    if missing:
        raise ValueError(f"Frações de bioma ausentes: {sorted(missing)}")
    out = df.copy(deep=True)
    shares = out[list(BIOME_COLUMNS)].apply(pd.to_numeric, errors="coerce")
    invalid = (
        ~np.isfinite(shares).all(axis=1)
        | shares.lt(-1e-10).any(axis=1)
        | shares.gt(1 + 1e-10).any(axis=1)
        | shares.sum(axis=1).le(0)
    )
    valid = ~invalid
    names = pd.Series(pd.NA, index=out.index, dtype="string")
    names.loc[valid] = shares.loc[valid].idxmax(axis=1).map(dict(zip(BIOME_COLUMNS, BIOMES)))
    maxima = shares.max(axis=1)
    ties = shares.eq(maxima, axis=0).to_numpy()
    out["bioma_dominante"] = pd.Categorical(names, categories=BIOMES)
    out["flag_bioma_dominante_empate"] = pd.array(valid & (ties.sum(axis=1) > 1), dtype="boolean")
    out["flag_bioma_dominante_invalido"] = pd.array(invalid, dtype="boolean")
    return out


def resolve_csv_path(path: str | Path | None = None) -> Path:
    """Use the requested absolute default, then the app-relative or cwd CSV."""
    if path is not None:
        explicit = Path(path).expanduser()
        if not explicit.is_file():
            raise FileNotFoundError(f"CSV não encontrado: {explicit}")
        return explicit.resolve()
    for candidate in (DEFAULT_CSV, APP_DIR / CSV_NAME, Path(CSV_NAME)):
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"Não foi encontrado {CSV_NAME} no caminho padrão ou junto de app.py.")


@st.cache_data(show_spinner="Carregando e validando o painel municipal…")
def _load_panel_cached(path: str, mtime_ns: int, size: int) -> pd.DataFrame:
    """File metadata participates in the cache key to avoid stale CSV reads."""
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    source_columns = df.columns.tolist()
    validate_panel_keys(df)
    for key in ("codigo_ibge", "ano"):
        df[key] = pd.to_numeric(df[key], errors="raise").astype("int64")
    for col in df.columns:
        if col.startswith(("flag_", "y_flag_")) or col in BOOLEAN_COLUMNS:
            df[col] = normalize_flag(df[col])
    df = df.sort_values(["codigo_ibge", "ano"], kind="stable").reset_index(drop=True)
    df = add_calendar_ibama_flags(df)
    df = add_dominant_biome(df)
    df.attrs.update({
        "source_path": path,
        "source_columns": source_columns,
        "source_shape": (len(df), len(source_columns)),
        "csv_size": size,
        "csv_mtime_ns": mtime_ns,
        "biome_rule": "Maior fração; empates: Amazônia, Cerrado, Pantanal; incompletos: ausente.",
        "ibama_lag_rule": "Flag do ano civil t-1 construída no painel integral, sem extrapolar cobertura.",
    })
    return df


def load_panel(path: str | Path | None = None) -> pd.DataFrame:
    """Load the full panel, validate keys, type flags and derive auditable metadata."""
    resolved = resolve_csv_path(path)
    stat = resolved.stat()
    return _load_panel_cached(str(resolved), stat.st_mtime_ns, stat.st_size)


def _column_classification(name: str) -> tuple[str, str]:
    if name in {"codigo_ibge", "ano"}:
        return BLOCKS[6], "Chave do painel; metadado de identificação, não regressor."
    if name.startswith(("flag_", "y_flag_")) or name in BOOLEAN_COLUMNS:
        return BLOCKS[6], "Flag de qualidade, cobertura ou comparabilidade."
    if name.startswith(("interacao_", "exposicao_real_x_")):
        return BLOCKS[3], "Interação ou exposição econômica construída."
    base_name = name.removeprefix("log1p__")
    if base_name.startswith(("n_autos_", "multas_")) and "__ibama_" in base_name:
        return BLOCKS[4], "Medida institucional; variantes e defasagens preservadas."
    if name.startswith(("preco_nominal", "preco_real_usd2024", "ln_preco", "dln_preco")):
        return BLOCKS[1], "Preço ou transformação/defasagem de preço."
    if name.startswith(("capacidade_valor__", "capacidade_z__", "rendimento_")):
        return BLOCKS[2], "Capacidade produtiva ou rendimento observado."
    if name.startswith(("taxa_conversao__", "conversao_ha__", "nativa_", "native_veg_",
                        "agricultura_", "pastagem_", "efetivo_bovino")) or name in {
        "lotacao_cabecas_ha", "y_nativa_inicial_ha",
    }:
        return BLOCKS[0], "Resultado de conversão ou estoque/intensidade de uso da terra."
    if name.startswith(("precip_", "media_", "desvio_", "elevation_", "biome_")) or name == "bioma_dominante":
        return BLOCKS[5], "Controle climático, geográfico ou classificação de bioma."
    return BLOCKS[6], "Diagnóstico auxiliar, contagem de cobertura ou metadado da fonte."


def categorize_columns(columns: Iterable[str] | pd.DataFrame) -> dict[str, list[str]]:
    """Assign every source/derived column once to one of the seven theoretical blocks.

    Identification keys and coverage-only auxiliaries belong to the audit block;
    they must not silently become candidate regressors. column_catalog documents
    this distinction for inspection and export.
    """
    names = columns.columns if isinstance(columns, pd.DataFrame) else columns
    groups: dict[str, list[str]] = {block: [] for block in BLOCKS}
    for name in names:
        groups[_column_classification(str(name))[0]].append(str(name))
    return groups


def column_catalog(df: pd.DataFrame) -> pd.DataFrame:
    """Human-readable inventory including the reason for classification."""
    return pd.DataFrame([
        {"variavel": col, "bloco": _column_classification(col)[0],
         "criterio": _column_classification(col)[1], "tipo": str(df[col].dtype),
         "n_missing": int(df[col].isna().sum())}
        for col in df.columns
    ])


def ibama_columns(df: pd.DataFrame, include_logs: bool = False) -> list[str]:
    """Only analytical counts/fines, excluding flags and coverage diagnostics."""
    cols = []
    for col in df.columns:
        if col.startswith("log1p__") and not include_logs:
            continue
        base = col.removeprefix("log1p__")
        if base.startswith(("n_autos_", "multas_")) and any(base.endswith(f"__{s}") for s in IBAMA_SOURCES):
            cols.append(col)
    return cols


def apply_ibama_treatment(
    df: pd.DataFrame, impute_zeros: bool = True, log1p: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return a treated copy and variable-level audit, keeping structural NaNs.

    log1p=True adds `log1p__<original>` columns; original-scale columns remain
    available. Negative counts/fines are retained in original scale and become
    missing in logarithms, with their count reported explicitly in the audit.
    This operation does not alter any partial observed sum/count or source flag.
    """
    out = add_calendar_ibama_flags(df)
    records = []
    for col in ibama_columns(out):
        source = next(s for s in IBAMA_SOURCES if col.endswith(f"__{s}"))
        is_lagged = bool(re.search(r"_lag1(?=__)", col))
        flag = f"flag_sem_registro_identificado{'_lag1' if is_lagged else ''}__{source}"
        reference = out[flag] if flag in out else pd.Series(pd.NA, index=out.index, dtype="boolean")
        numeric = pd.to_numeric(out[col], errors="raise").astype(float)
        eligible = numeric.isna() & flag_mask(reference)
        before = int(numeric.isna().sum())
        if impute_zeros:
            numeric = numeric.mask(eligible, 0.0)
        out[col] = numeric
        negative = numeric.lt(0)
        log_name = f"log1p__{col}" if log1p else None
        if log1p:
            out[log_name] = np.log1p(numeric.where(~negative))
        records.append({
            "variavel": col, "flag_referencia": flag,
            "n_missing_antes": before, "n_elegiveis_zero": int(eligible.sum()),
            "n_imputados_zero": int(eligible.sum()) if impute_zeros else 0,
            "n_missing_depois": int(numeric.isna().sum()),
            "n_sem_flag_referencia": int(normalize_flag(reference).isna().sum()),
            "n_negativos": int(negative.sum()), "variavel_log1p": log_name,
        })
    out.attrs["ibama_impute_zeros"] = bool(impute_zeros)
    out.attrs["ibama_log1p"] = bool(log1p)
    return out, pd.DataFrame.from_records(records, columns=[
        "variavel", "flag_referencia", "n_missing_antes", "n_elegiveis_zero",
        "n_imputados_zero", "n_missing_depois", "n_sem_flag_referencia",
        "n_negativos", "variavel_log1p",
    ])


def filter_panel(
    df: pd.DataFrame,
    year_range: tuple[int, int] | None = None,
    biomes: Iterable[str] | None = None,
    require_complete_y: bool = False,
    exclude_zero_denominator: bool = False,
) -> pd.DataFrame:
    """Apply explicit global filters after full-panel calendar flags are attached."""
    prepared = add_calendar_ibama_flags(df)
    mask = pd.Series(True, index=prepared.index)
    if year_range is not None:
        start, end = year_range
        if start > end:
            raise ValueError("Ano inicial deve ser menor ou igual ao ano final.")
        mask &= prepared["ano"].between(start, end)
    if biomes is not None:
        mask &= prepared["bioma_dominante"].isin(list(biomes))
    if require_complete_y:
        mask &= flag_mask(prepared["y_cobertura_completa"], True)
    if exclude_zero_denominator:
        mask &= flag_mask(prepared["y_flag_denominador_zero"], False)
    return prepared.loc[mask].copy()
