"""Run with: python -m streamlit run app.py"""
from __future__ import annotations

import hashlib
import pandas as pd
import streamlit as st

from src.data_loader import apply_ibama_treatment, categorize_columns, flag_mask, ibama_columns, load_panel
from src.dashboard_views import binscatter, diagnosis, laboratory, proxies, temporal
from src.economic_views import economic_overview, economic_relations, univariate_view


def main():
    st.set_page_config(page_title="H1 · Conversão, retornos e instituições", page_icon="🌿", layout="wide")
    st.markdown("""<style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1650px;}
    [data-testid="stMetric"] {background: rgba(18,130,117,.07); border: 1px solid rgba(18,130,117,.18); border-radius: 10px; padding: 16px;}
    [data-testid="stMetricValue"] {color: #128275;}
    .eyebrow {color: #128275; font-size: .78rem; letter-spacing: .16em; font-weight: 700;}
    </style>""", unsafe_allow_html=True)
    try:
        raw = load_panel()
    except (OSError, ValueError) as error:
        st.error(f"Não foi possível carregar o painel: {error}")
        st.stop()
    with st.sidebar:
        st.markdown("### Recorte da análise")
        st.caption("Capítulo 1 · Mato Grosso · H1")
        years = st.slider("Intervalo de anos", int(raw.ano.min()), int(raw.ano.max()),
                          (int(raw.ano.min()), int(raw.ano.max())), key="years")
        available = [b for b in ["Amazônia", "Cerrado", "Pantanal"] if b in raw.bioma_dominante.unique()]
        biomes = st.multiselect("Biomas dominantes", available, available, key="biomes")
        quality = st.toggle("Exigir cobertura completa de Y", True, key="quality")
        denominator = st.toggle("Excluir denominador zero", True, key="denominator")
        st.divider()
        st.markdown("**Tratamento do IBAMA**")
        impute = st.toggle("Imputar zeros pela flag", False, key="impute",
                            help="Somente NaN com flag_sem_registro_identificado=True. Defasagens usam a flag do ano t−1.")
        logs = st.toggle("Disponibilizar log(1 + IBAMA)", False, key="log_ibama",
                          help="Cria colunas derivadas e preserva os valores em nível. Nenhum arquivo de dados é alterado.")
        st.caption("Os tratamentos ocorrem antes dos filtros de ano e bioma, preservando o calendário das defasagens.")
    treated, treatment_audit = apply_ibama_treatment(raw, impute_zeros=impute, log1p=logs)
    keep = treated.ano.between(*years) & treated.bioma_dominante.isin(biomes)
    if quality:
        keep &= flag_mask(treated.y_cobertura_completa)
    if denominator:
        keep &= flag_mask(treated.y_flag_denominador_zero, False)
    df = treated.loc[keep].copy()
    st.markdown('<div class="eyebrow">TESE USP / CAPÍTULO 1 / LABORATÓRIO EXPLORATÓRIO</div>', unsafe_allow_html=True)
    st.title("Conversão, retornos e instituições")
    st.write("Como a pressão econômica se relaciona com a conversão da vegetação nativa, "
             "e como essa relação varia com a capacidade produtiva e o ambiente institucional?")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Observações no recorte", f"{len(df):,}", f"de {len(raw):,} na base", delta_color="off")
    c2.metric("Municípios", df.codigo_ibge.nunique())
    c3.metric("Anos observados", df.ano.nunique(), f"{years[0]}–{years[1]}", delta_color="off")
    c4.metric("Y agricultura válido", f"{df.taxa_conversao__agricultura.notna().sum():,}")
    if df.empty:
        st.warning("O recorte está vazio. Amplie os anos, selecione um bioma ou reveja os filtros de qualidade.")
        return
    balanced = len(df) == df.codigo_ibge.nunique() * df.ano.nunique()
    st.caption(f"Painel {'balanceado' if balanced else 'desbalanceado'} após filtros · "
               "Bioma dominante = maior fração da área municipal; não representa conversão medida dentro de cada bioma. "
               "A classificação não impõe limiar de predominância.")
    blocks = categorize_columns(df)
    institutions = ibama_columns(df)
    if logs:
        institutions = ["log1p__" + c for c in institutions] + institutions
    prices = [c for c in df if c.startswith(("preco_", "ln_preco", "dln_preco"))]
    analytical = [c for block, cols in blocks.items() if not block.startswith("[Flags]") for c in cols
                  if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
    reference = treated.loc[treated.ano.between(*years) & treated.bioma_dominante.isin(biomes)].copy()
    tabs = st.tabs(["Retrato econômico", "Distribuições", "Relações econômicas", "Diagnóstico e flags",
                    "Dinâmica e biomas", "Proxies e VIF", "Binscatter e Within", "Laboratório H1"])
    # A fingerprint prevents stale regressions from surviving changes in data or filters.
    fingerprint = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()[:16]
    context = f"{years[0]}–{years[1]}; biomas={','.join(biomes)}; cobertura={quality}; denom_zero_excluido={denominator}; zeros_IBAMA={impute}; log1p={logs}; dados={fingerprint}"
    views = [lambda: economic_overview(df, reference), lambda: univariate_view(df, blocks),
             lambda: economic_relations(df, reference, analytical, institutions),
             lambda: diagnosis(df, raw, blocks, treatment_audit), lambda: temporal(df, prices, institutions),
             lambda: proxies(df, blocks, institutions), lambda: binscatter(df, analytical),
             lambda: laboratory(df, institutions, context)]
    for tab, render in zip(tabs, views):
        with tab:
            render()


if __name__ == "__main__":
    main()
