"""Módulo de carregamento, categorização teórica e regras de imputação do Painel (Cap. 1)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
CSV_NAME = "painel_tese_chap1_pt.csv"
DEFAULT_CSV_PATH = str(APP_DIR / CSV_NAME)

THEORETICAL_BLOCKS: List[str] = [
    "[Y] Conversão e Uso da Terra",
    "[X1] Preços e Choques",
    "[X2] Capacidade Produtiva (PAM vs GAEZ)",
    "[X1*X2] Interações e Exposição",
    "[X3] Ambiente Institucional (IBAMA)",
    "[Controles] Clima, Geografia e Biomas",
    "[Flags] Auditoria e Qualidade",
]

# Rótulos amigáveis para exibição em gráficos e tabelas
FRIENDLY_LABELS: Dict[str, str] = {
    "taxa_conversao__agricultura": "Taxa de Conversão Bruta -> Agricultura (prop. 0-1)",
    "taxa_conversao__pastagem": "Taxa de Conversão Bruta -> Pastagem (prop. 0-1)",
    "conversao_ha__agricultura": "Conversão Bruta -> Agricultura (ha)",
    "conversao_ha__pastagem": "Conversão Bruta -> Pastagem (ha)",
    "y_nativa_inicial_ha": "Vegetação Nativa Inicial do Par Anual (ha)",
    "nativa_ha": "Estoque de Vegetação Nativa (ha)",
    "agricultura_ha": "Estoque de Agricultura (ha)",
    "pastagem_ha": "Estoque de Pastagem (ha)",
    "nativa_share": "Proporção de Vegetação Nativa (0-1)",
    "agricultura_share": "Proporção de Agricultura (0-1)",
    "pastagem_share": "Proporção de Pastagem (0-1)",
    "lotacao_cabecas_ha": "Lotação Bovina Aparente (cabeças/ha)",
    "efetivo_bovino": "Efetivo Bovino (cabeças)",
    "efetivo_bovino_lag1": "Efetivo Bovino Defasado t-1 (cabeças)",
    "preco_real_usd2024_media_anual__soja": "Preço Real Soja (USD 2024/t)",
    "preco_real_usd2024_media_anual__milho": "Preço Real Milho (USD 2024/t)",
    "preco_real_usd2024_media_anual__carne_bovina": "Preço Real Carne Bovina (USD 2024/kg)",
    "preco_real_usd2024_media_anual_lag1__soja": "Preço Real Soja t-1 (USD 2024/t)",
    "preco_real_usd2024_media_anual_lag1__milho": "Preço Real Milho t-1 (USD 2024/t)",
    "preco_real_usd2024_media_anual_lag1__carne_bovina": "Preço Real Carne Bovina t-1 (USD 2024/kg)",
    "ln_preco_real_usd2024_media_anual__soja": "ln Preço Real Soja (t)",
    "ln_preco_real_usd2024_media_anual__milho": "ln Preço Real Milho (t)",
    "ln_preco_real_usd2024_media_anual__carne_bovina": "ln Preço Real Carne Bovina (t)",
    "ln_preco_real_usd2024_media_anual_lag1__soja": "ln Preço Real Soja (t-1)",
    "ln_preco_real_usd2024_media_anual_lag1__milho": "ln Preço Real Milho (t-1)",
    "ln_preco_real_usd2024_media_anual_lag1__carne_bovina": "ln Preço Real Carne Bovina (t-1)",
    "dln_preco_real_usd2024_media_anual__soja": "Choque dln Preço Real Soja (t)",
    "dln_preco_real_usd2024_media_anual__milho": "Choque dln Preço Real Milho (t)",
    "dln_preco_real_usd2024_media_anual__carne_bovina": "Choque dln Preço Real Carne Bovina (t)",
    "dln_preco_real_usd2024_media_anual_lag1__soja": "Choque dln Preço Real Soja (t-1)",
    "dln_preco_real_usd2024_media_anual_lag1__milho": "Choque dln Preço Real Milho (t-1)",
    "dln_preco_real_usd2024_media_anual_lag1__carne_bovina": "Choque dln Preço Real Carne Bovina (t-1)",
    "n_autos_observados__ibama_informada": "Total de Autos Observados (IBAMA Informada)",
    "n_autos_observados__ibama_espacial": "Total de Autos Observados (IBAMA Espacial)",
    "n_autos_flora__ibama_informada": "Autos Flora (IBAMA Informada, t)",
    "n_autos_flora__ibama_espacial": "Autos Flora (IBAMA Espacial, t)",
    "n_autos_desmatamento__ibama_informada": "Autos Desmatamento (IBAMA Informada, t)",
    "n_autos_desmatamento__ibama_espacial": "Autos Desmatamento (IBAMA Espacial, t)",
    "n_autos_flora_lag1__ibama_informada": "Autos Flora (IBAMA Informada, t-1)",
    "n_autos_flora_lag1__ibama_espacial": "Autos Flora (IBAMA Espacial, t-1)",
    "n_autos_desmatamento_lag1__ibama_informada": "Autos Desmatamento (IBAMA Informada, t-1)",
    "n_autos_desmatamento_lag1__ibama_espacial": "Autos Desmatamento (IBAMA Espacial, t-1)",
    "multas_flora_reais_observadas__ibama_informada": "Multas Reais Flora (IBAMA Informada, R$ 2024, t)",
    "multas_flora_reais_observadas__ibama_espacial": "Multas Reais Flora (IBAMA Espacial, R$ 2024, t)",
    "multas_desmatamento_reais_observadas__ibama_informada": "Multas Reais Desmatamento (IBAMA Informada, R$ 2024, t)",
    "multas_desmatamento_reais_observadas__ibama_espacial": "Multas Reais Desmatamento (IBAMA Espacial, R$ 2024, t)",
    "multas_flora_reais_observadas_lag1__ibama_informada": "Multas Reais Flora (IBAMA Informada, R$ 2024, t-1)",
    "multas_flora_reais_observadas_lag1__ibama_espacial": "Multas Reais Flora (IBAMA Espacial, R$ 2024, t-1)",
    "multas_desmatamento_reais_observadas_lag1__ibama_informada": "Multas Reais Desmatamento (IBAMA Informada, R$ 2024, t-1)",
    "multas_desmatamento_reais_observadas_lag1__ibama_espacial": "Multas Reais Desmatamento (IBAMA Espacial, R$ 2024, t-1)",
    "precip_mm_anual": "Precipitação Acumulada Anual (mm)",
    "precip_zscore_1981_2000": "Anomalia de Precipitação Z-Score (Ref. 1981-2000)",
    "precip_zscore_1981_2010": "Anomalia de Precipitação Z-Score (Ref. 1981-2010)",
    "precip_zscore_1991_2020": "Anomalia de Precipitação Z-Score (Ref. 1991-2020)",
    "precip_anomaly_1981_2000": "Anomalia de Precipitação (mm, Ref. 1981-2000)",
    "precip_anomaly_1981_2010": "Anomalia de Precipitação (mm, Ref. 1981-2010)",
    "precip_anomaly_1991_2020": "Anomalia de Precipitação (mm, Ref. 1991-2020)",
    "elevation_mean_m": "Elevação Média (m, COP-DEM 90)",
    "biome_amazonia_share_i": "Fração Territorial no Bioma Amazônia (0-1)",
    "biome_cerrado_share_i": "Fração Territorial no Bioma Cerrado (0-1)",
    "biome_pantanal_share_i": "Fração Territorial no Bioma Pantanal (0-1)",
}


def get_friendly_label(col: str) -> str:
    """Retorna um rótulo descritivo amigável ou o próprio nome da coluna."""
    if col in FRIENDLY_LABELS:
        return f"{FRIENDLY_LABELS[col]} [{col}]"
    return col


def resolve_csv_path(custom_path: Optional[str | Path] = None) -> Path:
    """Resolve o caminho do CSV com fallback seguro para caminhos relativos."""
    candidates = []
    if custom_path:
        candidates.append(Path(custom_path))
    candidates.extend([
        Path(DEFAULT_CSV_PATH),
        Path("painel_tese_chap1_pt.csv"),
        Path(__file__).resolve().parent.parent / "painel_tese_chap1_pt.csv",
    ])
    for path in candidates:
        if path.exists() and path.is_file():
            return path.resolve()
    raise FileNotFoundError(
        f"Arquivo 'painel_tese_chap1_pt.csv' não encontrado nos caminhos: "
        f"{[str(c) for c in candidates]}"
    )


def get_column_block(col: str) -> str:
    """Classifica qualquer uma das 296 colunas nos 7 blocos teóricos exigidos."""
    # Bloco 7: [Flags] Auditoria e Qualidade (flags explícitas, contadores diagnósticos e metadados de cobertura)
    if (
        col.startswith((
            "flag_",
            "y_flag_",
            "n_linhas",
            "n_areas_",
            "n_registros_",
            "n_tipo_",
            "n_area_tema_",
            "n_status_",
            "n_cancelados_",
            "meses_",
            "count_",
        ))
        or ("_valores_" in col and "_ausentes" in col)
        or col in {
            "codigo_ibge",
            "ano",
            "y_colecao",
            "y_malha",
            "y_mascara_id",
            "y_area_total_ha",
            "y_area_valida_par_ha",
            "y_area_nao_valida_par_ha",
            "y_cobertura_completa",
            "y_fracao_area_valida_par",
            "area_mapeada_ha",
            "area_nao_observada_ha",
            "area_classe_residual_13_ha",
            "area_valida_ha",
            "area_referencia_ha",
            "fracao_mapeada_referencia",
            "grade_fonte_completa",
            "completude_classes_fora_grade_certificada",
            "geografia_historica_validada",
            "ano_referencia_area",
            "compatibilidade_datas_estoques_validada",
            "fracao_pixels_minima",
            "soma_fracoes",
        }
    ):
        return "[Flags] Auditoria e Qualidade"

    # Bloco 1: [Y] Conversão e Uso da Terra
    if col.startswith((
        "taxa_conversao__",
        "conversao_ha__",
        "nativa_",
        "agricultura_",
        "pastagem_",
        "lotacao_cabecas_ha",
        "efetivo_bovino",
        "native_veg_",
        "y_nativa_inicial_ha",
    )):
        return "[Y] Conversão e Uso da Terra"

    # Bloco 2: [X1] Preços e Choques
    if col.startswith((
        "preco_nominal",
        "preco_real_usd2024",
        "ln_preco",
        "dln_preco",
    )):
        return "[X1] Preços e Choques"

    # Bloco 3: [X2] Capacidade Produtiva (PAM vs GAEZ)
    if col.startswith((
        "capacidade_valor__",
        "capacidade_z__",
        "rendimento_",
    )):
        return "[X2] Capacidade Produtiva (PAM vs GAEZ)"

    # Bloco 4: [X1*X2] Interações e Exposição
    if col.startswith((
        "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__",
        "exposicao_real_x_",
    )):
        return "[X1*X2] Interações e Exposição"

    # Bloco 5: [X3] Ambiente Institucional (IBAMA)
    if col.startswith(("n_autos_", "multas_")):
        return "[X3] Ambiente Institucional (IBAMA)"

    # Bloco 6: [Controles] Clima, Geografia e Biomas
    if col.startswith((
        "precip_",
        "media_",
        "desvio_",
        "elevation_",
        "biome_",
    )):
        return "[Controles] Clima, Geografia e Biomas"

    return "[Flags] Auditoria e Qualidade"


def categorize_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Agrupa todas as colunas originais do DataFrame nos 7 blocos teóricos."""
    blocks: Dict[str, List[str]] = {b: [] for b in THEORETICAL_BLOCKS}
    for col in df.columns:
        if col in {"bioma_dominante", "municipio_nome", "municipio_label"}:
            continue
        block = get_column_block(col)
        blocks[block].append(col)
    return blocks


def _assign_dominant_biome(df: pd.DataFrame) -> pd.Series:
    """Cria a coluna categórica bioma_dominante com base na maior fração municipal."""
    share_cols = {
        "biome_amazonia_share_i": "Amazônia",
        "biome_cerrado_share_i": "Cerrado",
        "biome_pantanal_share_i": "Pantanal",
    }
    dominant_col = df[list(share_cols.keys())].idxmax(axis=1)
    return pd.Categorical(
        dominant_col.map(share_cols),
        categories=["Amazônia", "Cerrado", "Pantanal"],
        ordered=False,
    )


def _load_municipality_names(csv_path: Path) -> Dict[int, str]:
    """Carrega nomes dos 141 municípios buscando na árvore do repositório."""
    try:
        for parent in csv_path.parents:
            for sub in [
                Path("2_INTI/xdata/chap1/processed/territorio_141/h2__biome_share__ibge2019_malha2024__candidato.csv"),
                Path("xdata/chap1/processed/territorio_141/h2__biome_share__ibge2019_malha2024__candidato.csv"),
                Path("2_INTI/xdata/chap1/processed/tabular/h2__biome_share__ibge2019_malha2024__candidato.csv"),
            ]:
                candidate = parent / sub
                if candidate.exists():
                    aux = pd.read_csv(candidate, usecols=["codigo_ibge", "municipio"])
                    return dict(zip(aux["codigo_ibge"].astype(int), aux["municipio"].astype(str)))
    except Exception:
        pass
    return {}


@st.cache_data(show_spinner=False)
def load_raw_panel(csv_path: Optional[str | Path] = None) -> pd.DataFrame:
    """Carrega o painel municipal 2001-2024 (N=3.384, 141 municípios, 296 colunas originais)
    e adiciona a coluna categórica `bioma_dominante` e rótulos municipais."""
    resolved_path = resolve_csv_path(csv_path)
    df = pd.read_csv(resolved_path, low_memory=False)

    # Garantir ordenação canônica de painel
    df["codigo_ibge"] = pd.to_numeric(df["codigo_ibge"], errors="raise").astype("int64")
    df["ano"] = pd.to_numeric(df["ano"], errors="raise").astype("int64")
    df = df.sort_values(["codigo_ibge", "ano"]).reset_index(drop=True)

    # Normalizar colunas booleanas com NA (ex.: flags parciais do IBAMA salvas como object)
    for col in df.columns:
        if col.startswith(("flag_", "y_flag_")) and df[col].dtype == object:
            vals = set(df[col].dropna().astype(str).str.lower().unique())
            if vals <= {"true", "false"}:
                df[col] = (
                    df[col]
                    .astype("string")
                    .str.lower()
                    .map({"true": True, "false": False})
                    .astype("boolean")
                )

    # Desfragmentar DataFrame após conversões de tipo antes de anexar colunas derivadas
    df = df.copy()

    # Coluna categórica exigida: bioma_dominante (Amazônia, Cerrado ou Pantanal)
    df["bioma_dominante"] = _assign_dominant_biome(df)

    # Nome do município (para enriquecer tabelas, rankings e tooltips sem alterar as 296 colunas)
    muni_map = _load_municipality_names(resolved_path)
    if muni_map:
        df["municipio_nome"] = df["codigo_ibge"].map(muni_map).fillna(df["codigo_ibge"].astype(str))
        df["municipio_label"] = df["municipio_nome"] + " (" + df["codigo_ibge"].astype(str) + ")"
    else:
        df["municipio_nome"] = df["codigo_ibge"].astype(str)
        df["municipio_label"] = df["codigo_ibge"].astype(str)

    return df


def get_ibama_variable_columns(df: pd.DataFrame) -> List[str]:
    """Retorna todas as 22 variáveis substantivas do Bloco [X3] Ambiente Institucional (IBAMA)."""
    return [
        c for c in df.columns
        if c.startswith(("n_autos_", "multas_"))
        and ("__ibama_informada" in c or "__ibama_espacial" in c)
    ]


def apply_ibama_imputation(
    df: pd.DataFrame,
    impute_zeros: bool = True,
    apply_log1p: bool = False,
) -> pd.DataFrame:
    """Implementa a Regra Crítica do IBAMA:
    - Quando `impute_zeros=True`, imputa `0.0` nos valores `NaN` das variáveis do IBAMA
      (`n_autos_*` e `multas_*`) APENAS quando a respectiva flag
      `flag_sem_registro_identificado__ibama_informada` (ou `espacial`) for `True`
      (ou, para variáveis `lag1`, quando o ano `t-1` não teve registro identificado,
      indicado pela flag `flag_sem_registro_identificado` defasada / ausência de registro em t-1),
      preservando como `NaN` os missings estruturais reais (onde houve auto lavrado, mas o
      tema ou valor era ausente/parcial).
    - Quando `apply_log1p=True`, aplica `np.log1p(x)` nas variáveis de contagem e multas do IBAMA.
    """
    out = df.copy()
    ibama_cols = get_ibama_variable_columns(out)

    if impute_zeros:
        for assoc in ("informada", "espacial"):
            flag_col = f"flag_sem_registro_identificado__ibama_{assoc}"
            if flag_col not in out.columns:
                continue
            flag_t = out[flag_col].fillna(False).astype(bool)

            # Para variáveis lag1, verificamos se t-1 não teve registro identificado:
            # Em t >= 2002, equivale a shift(1) de flag_sem_registro_identificado;
            # Em t == 2001 (e em todo o painel), flag_contagem_flora_parcial_lag1 é NaN
            # exatamente quando não houve registro identificado em t-1.
            lag_ref_col = f"flag_contagem_flora_parcial_lag1__ibama_{assoc}"
            if lag_ref_col in out.columns:
                flag_t_minus_1 = out[lag_ref_col].isna()
            else:
                flag_t_minus_1 = (
                    out.groupby("codigo_ibge", observed=True)[flag_col]
                    .shift(1)
                    .fillna(flag_t)
                    .astype(bool)
                )

            assoc_cols = [c for c in ibama_cols if c.endswith(f"__ibama_{assoc}")]
            for col in assoc_cols:
                is_lag1 = "_lag1__" in col
                mask_no_record = flag_t_minus_1 if is_lag1 else flag_t
                impute_mask = out[col].isna() & mask_no_record
                out[col] = pd.to_numeric(out[col], errors="coerce").astype("float64")
                out.loc[impute_mask, col] = 0.0

    if apply_log1p:
        for col in ibama_cols:
            s = pd.to_numeric(out[col], errors="coerce").astype("float64")
            out[col] = np.where(s.notna() & (s >= 0), np.log1p(s), np.nan)

    return out


def get_ibama_imputation_audit(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Gera tabela diagnóstica comparando N válido, Missings Totais, Zeros Imputados pela Flag
    e Missings Estruturais Reais remanescentes para todas as variáveis do IBAMA."""
    df_imputed = apply_ibama_imputation(df_raw, impute_zeros=True, apply_log1p=False)
    ibama_cols = get_ibama_variable_columns(df_raw)
    total_n = len(df_raw)
    rows = []
    for col in ibama_cols:
        assoc = "Informada" if "__ibama_informada" in col else "Espacial"
        temporal = "Defasada (t-1)" if "_lag1__" in col else "Contemporânea (t)"
        na_before = int(df_raw[col].isna().sum())
        valid_before = total_n - na_before
        na_after = int(df_imputed[col].isna().sum())
        valid_after = total_n - na_after
        zeros_imputed = na_before - na_after
        rows.append({
            "Variável": col,
            "Associação": assoc,
            "Janela": temporal,
            "N Válido (Original)": valid_before,
            "Missing Total (Original)": na_before,
            "% Missing (Original)": round(100.0 * na_before / total_n, 2),
            "Zeros Imputados (Flag=True)": zeros_imputed,
            "Missing Estrutural Real (Pós-Flag)": na_after,
            "% Missing Estrutural": round(100.0 * na_after / total_n, 2),
            "N Válido (Pós-Imputação)": valid_after,
            "Média (Original)": float(df_raw[col].mean()),
            "Média (Pós-Imputação)": float(df_imputed[col].mean()),
        })
    return pd.DataFrame(rows)


def filter_panel_data(
    df_raw: pd.DataFrame,
    year_range: Tuple[int, int] = (2001, 2024),
    selected_biomes: Optional[List[str]] = None,
    require_y_complete_coverage: bool = False,
    exclude_zero_denominator: bool = False,
    impute_ibama_zeros: bool = True,
    log1p_ibama: bool = False,
) -> pd.DataFrame:
    """Aplica os filtros globais da Sidebar mantendo rastreabilidade das observações."""
    # IMPORTANTE: Aplicar imputação do IBAMA antes de filtrar anos para preservar lag1 consistente
    df = apply_ibama_imputation(
        df_raw,
        impute_zeros=impute_ibama_zeros,
        apply_log1p=log1p_ibama,
    )

    y_min, y_max = year_range
    mask = df["ano"].between(y_min, y_max)

    if selected_biomes:
        mask &= df["bioma_dominante"].isin(selected_biomes)

    if require_y_complete_coverage and "y_cobertura_completa" in df.columns:
        mask &= df["y_cobertura_completa"].fillna(False).astype(bool)

    if exclude_zero_denominator and "y_flag_denominador_zero" in df.columns:
        mask &= ~df["y_flag_denominador_zero"].fillna(False).astype(bool)

    return df.loc[mask].copy().reset_index(drop=True)
