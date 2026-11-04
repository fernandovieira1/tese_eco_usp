"""Dashboard Econométrico e EDA em Painel — Capítulo 1 (Tese de Doutorado USP).

Problema de Pesquisa:
Como os retornos econômicos esperados e o ambiente institucional condicionam a taxa de conversão
bruta da vegetação nativa em Mato Grosso (2001–2024, N=3.384, 141 municípios, 296 colunas), e como
essa relação varia conforme a capacidade produtiva local da terra, atividades agropecuárias
(agricultura vs. pastagem) e biomas (Amazônia, Cerrado e Pantanal)?
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.api as sm
import streamlit as st

from src.data_loader import (
    DEFAULT_CSV_PATH,
    THEORETICAL_BLOCKS,
    categorize_columns,
    filter_panel_data,
    get_friendly_label,
    get_ibama_imputation_audit,
    get_ibama_variable_columns,
    load_raw_panel,
)
from src.econometric_lab import (
    SpecificationConfig,
    export_horse_race_to_latex,
    run_horse_race,
)
from src.panel_metrics import (
    compute_correlation_matrix,
    compute_lorenz_curves,
    compute_missing_summary_by_year,
    compute_multivariate_regimes_h1,
    compute_municipal_pca_typology,
    compute_municipal_ranking,
    compute_panel_descriptive_table,
    compute_sample_loss_comparison,
    compute_structural_land_transition,
    compute_univariate_deep_profile,
    compute_vif_table,
    export_descriptive_to_latex,
    transform_within,
)

# ---------------------------------------------------------------------------
# Configuração da Página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Cap. 1 Tese USP | Laboratório Econométrico e EDA em Painel (MT 2001–2024)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BIOME_COLORS = {
    "Amazônia": "#1b7837",
    "Cerrado": "#d95f02",
    "Pantanal": "#2b5c8f",
    "Mato Grosso (Total)": "#333333",
}


def _inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        .thesis-banner {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: #ffffff;
            padding: 1.15rem 1.5rem;
            border-radius: 0.6rem;
            margin-bottom: 1rem;
            border-left: 6px solid #eab308;
        }
        .thesis-banner h2 {
            margin: 0 0 0.35rem 0;
            font-size: 1.35rem;
            color: #ffffff;
        }
        .thesis-banner p {
            margin: 0.15rem 0;
            font-size: 0.9rem;
            color: #e2e8f0;
            line-height: 1.4;
        }
        .hypothesis-box {
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-left: 4px solid #0284c7;
            padding: 0.75rem 1rem;
            border-radius: 0.4rem;
            font-size: 0.88rem;
            color: #1e293b;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Carregamento e Sidebar de Filtros Globais
# ---------------------------------------------------------------------------
def main() -> None:
    _inject_custom_css()

    try:
        df_raw = load_raw_panel(DEFAULT_CSV_PATH)
    except Exception as exc:
        st.error(f"Erro ao carregar a base de dados do painel: {exc}")
        st.stop()

    blocks_map = categorize_columns(df_raw)

    # Sidebar — Filtros Globais
    with st.sidebar:
        st.markdown("## ⚙️ Filtros Globais do Painel")
        st.caption("Unidade: `codigo_ibge` × `ano` (141 municípios de MT, 2001–2024)")

        min_year = int(df_raw["ano"].min())
        max_year = int(df_raw["ano"].max())
        year_range = st.slider(
            "Intervalo de Anos (`ano`)",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1,
        )

        all_biomes = ["Amazônia", "Cerrado", "Pantanal"]
        selected_biomes = st.multiselect(
            "Bioma Dominante (`bioma_dominante`)",
            options=all_biomes,
            default=all_biomes,
            help="Classificado pela maior fração territorial entre Amazônia, Cerrado e Pantanal.",
        )
        if not selected_biomes:
            st.warning("Selecione ao menos um bioma. Exibindo todos por padrão.")
            selected_biomes = all_biomes

        st.markdown("---")
        st.markdown("### 🛡️ Qualidade e Cobertura de $Y$")
        require_y_complete = st.toggle(
            "Apenas cobertura completa (`y_cobertura_completa == True`)",
            value=False,
            help="Filtra os 2.772 pares município-ano onde a área válida de transição MapBiomas cobre 100% do município (remove 612 pares incompletos).",
        )
        exclude_zero_denom = st.toggle(
            "Excluir denominador zero (`y_flag_denominador_zero == False`)",
            value=True,
            help="Garante exclusão de observações onde a vegetação nativa inicial do par anual seja igual a zero.",
        )

        st.markdown("---")
        st.markdown("### 🏛️ Regra Crítica do IBAMA ($X_3$)")
        impute_ibama_zeros = st.toggle(
            "Imputar 0.0 quando `flag_sem_registro_identificado == True`",
            value=True,
            help=(
                "Imputa 0.0 somente quando o município-ano não teve nenhum auto lavrado identificado "
                "(flag=True). Preserva como NaN os missings estruturais reais (autos lavrados sem "
                "classificação temática ou sem valor válido)."
            ),
        )
        log1p_ibama = st.toggle(
            "Aplicar transformação `np.log1p` no IBAMA",
            value=False,
            help="Transforma contagens de autos e valores de multas por ln(1 + x) para reduzir assimetria à direita.",
        )

        st.markdown("---")
        st.markdown("### 📦 Resumo dos 7 Blocos Teóricos")
        for b_name, b_cols in blocks_map.items():
            st.caption(f"• **{b_name}**: `{len(b_cols)}` cols")

    # Aplicar filtros globais
    df = filter_panel_data(
        df_raw=df_raw,
        year_range=year_range,
        selected_biomes=selected_biomes,
        require_y_complete_coverage=require_y_complete,
        exclude_zero_denominator=exclude_zero_denom,
        impute_ibama_zeros=impute_ibama_zeros,
        log1p_ibama=log1p_ibama,
    )

    # Cabeçalho Principal
    st.markdown(
        """
        <div class="thesis-banner">
            <h2>📊 Capítulo 1 — Retornos Esperados, Capacidade Produtiva, Instituições e Conversão da Vegetação Nativa em Mato Grosso</h2>
            <p><b>Problema de Pesquisa:</b> Como os retornos econômicos esperados e o ambiente institucional condicionam a taxa de conversão bruta da vegetação nativa em Mato Grosso (2001–2024), e como essa relação varia conforme a capacidade produtiva local da terra, atividades agropecuárias (agricultura vs. pastagem) e biomas (Amazônia, Cerrado e Pantanal)?</p>
            <p><b>H1-a (Preços × Capacidade Produtiva):</b> Choques favoráveis de preços agrícolas geram maior pressão de conversão onde a capacidade produtiva predeterminada da terra é mais elevada. &nbsp;|&nbsp;
            <b>H1-b (Condicionamento Institucional):</b> O monitoramento, a fiscalização e as autuações do IBAMA condicionam/amortecem a sensibilidade da taxa de conversão ao retorno econômico esperado.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPIs da Amostra Ativa
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    n_obs_active = len(df)
    n_muni_active = int(df["codigo_ibge"].nunique())
    n_years_active = int(df["ano"].nunique())
    n_y_valid = int(df["taxa_conversao__agricultura"].notna().sum())
    pct_y_valid = (100.0 * n_y_valid / n_obs_active) if n_obs_active > 0 else 0.0
    n_ibama_valid = int(df["n_autos_desmatamento__ibama_informada"].notna().sum())

    k1.metric("Observações Ativas (N)", f"{n_obs_active:,}", f"de {len(df_raw):,} totais")
    k2.metric("Municípios (`codigo_ibge`)", f"{n_muni_active}", "Ref. IBGE 141")
    k3.metric("Janela Temporal (`ano`)", f"{year_range[0]}–{year_range[1]}", f"{n_years_active} anos")
    k4.metric("Pares Válidos em Y (Taxas)", f"{n_y_valid:,}", f"{pct_y_valid:.1f}% da amostra")
    k5.metric(
        "IBAMA Desmat. Válidos",
        f"{n_ibama_valid:,}",
        "Com zeros da flag" if impute_ibama_zeros else "Sem imputação",
    )
    k6.metric(
        "Escala IBAMA ($X_3$)",
        "ln(1 + x)" if log1p_ibama else "Nível Original",
        f"{len(selected_biomes)} bioma(s)",
    )

    # -----------------------------------------------------------------------
    # 7 Abas Analíticas (5 Originais + 2 de Intuição Econômica Univariada/Multivariada)
    # -----------------------------------------------------------------------
    tabs = st.tabs([
        "1️⃣ Diagnóstico do Painel & Flags",
        "2️⃣ Dinâmica Temporal & Biomas",
        "3️⃣ Batalha de Proxies & VIF (X2/X3)",
        "4️⃣ Binscatter Econométrico (Within)",
        "5️⃣ Laboratório Econométrico (H1, H1-a, H1-b)",
        "6️⃣ Análise Univariada & Concentração Espacial",
        "7️⃣ Análise Multivariada & Intuição Econômica da Tese",
    ])

    # =======================================================================
    # ABA 1: Diagnóstico do Painel, Decomposição (Between/Within) e Auditoria de Flags
    # =======================================================================
    with tabs[0]:
        st.subheader("1. Decomposição de Variância (Overall, Between e Within) por Bloco Teórico")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Por que decompor Between vs. Within?</b> Em modelos de Efeitos Fixos Municipais ($\alpha_i$),
            toda variável <b>invariante no tempo</b> ($\text{DP Within} = 0$, como aptidão GAEZ, produtividade histórica PAM 1991–2000,
            frações de bioma e altitude) tem seu nível absorvido por $\alpha_i$. Já variáveis que variam apenas no tempo
            ($\text{DP Between} = 0$, como preços internacionais em USD) são absorvidas pelos Efeitos Fixos de Ano ($\gamma_t$).
            Por isso, a identificação de <b>H1-a</b> requer a interação $X_{1,t-1} \times X_{2,i}$, que varia simultaneamente entre municípios e anos!
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_f1, col_f2, col_f3 = st.columns([2.2, 1.3, 1.2])
        with col_f1:
            selected_blocks_tab1 = st.multiselect(
                "Selecione os Blocos Teóricos para a Tabela Descritiva:",
                options=THEORETICAL_BLOCKS,
                default=THEORETICAL_BLOCKS[:6],
                key="tab1_blocks",
            )
        with col_f2:
            structure_filter = st.selectbox(
                "Filtrar por Estrutura de Variação no Painel:",
                options=[
                    "Todas as variáveis dos blocos selecionados",
                    "Apenas Variação Município × Ano (DP Within > 0 e DP Between > 0)",
                    "Apenas Invariantes no Tempo (DP Within = 0 — absorvidas por FE Município)",
                    "Apenas Choques Macro Anuais (DP Between = 0 — absorvidas por FE Ano)",
                ],
                key="tab1_struct_filter",
            )
        with col_f3:
            search_var_tab1 = st.text_input(
                "Buscar variável por nome (substring):",
                value="",
                placeholder="ex.: soja, gaez, ibama, taxa...",
                key="tab1_search",
            )

        cols_for_desc = []
        for b in selected_blocks_tab1:
            cols_for_desc.extend(blocks_map.get(b, []))
        if search_var_tab1.strip():
            q = search_var_tab1.strip().lower()
            cols_for_desc = [c for c in cols_for_desc if q in c.lower()]

        desc_df = compute_panel_descriptive_table(df, cols_for_desc)

        if not desc_df.empty:
            if "Apenas Variação Município × Ano" in structure_filter:
                desc_df = desc_df.loc[desc_df["Estrutura no Painel"] == "Variação Município × Ano"]
            elif "Invariantes no Tempo" in structure_filter:
                desc_df = desc_df.loc[desc_df["Estrutura no Painel"].str.contains("Invariante no Tempo|Constante", regex=True)]
            elif "Choques Macro Anuais" in structure_filter:
                desc_df = desc_df.loc[desc_df["Estrutura no Painel"].str.contains("Invariante entre Municípios", regex=True)]

        c_info1, c_info2, c_info3 = st.columns(3)
        n_time_inv = int((desc_df["DP Within"].fillna(0) <= 1e-10).sum()) if not desc_df.empty else 0
        n_space_inv = int(
            desc_df["Estrutura no Painel"].str.contains("Invariante entre Municípios", na=False).sum()
        ) if not desc_df.empty else 0
        c_info1.info(f"**Variáveis exibidas na tabela:** `{len(desc_df)}` (de 296 colunas totais)")
        c_info2.warning(f"**Invariantes no Tempo (`DP Within = 0`):** `{n_time_inv}` variáveis na seleção")
        c_info3.success(f"**Séries Macro Anuais (`DP Between = 0`):** `{n_space_inv}` variáveis na seleção")

        st.dataframe(
            desc_df,
            width="stretch",
            height=420,
            column_config={
                "% Missing": st.column_config.ProgressColumn(
                    "% Missing", min_value=0.0, max_value=100.0, format="%.1f%%"
                ),
                "Média": st.column_config.NumberColumn(format="%.4f"),
                "Mediana": st.column_config.NumberColumn(format="%.4f"),
                "Min": st.column_config.NumberColumn(format="%.4f"),
                "Max": st.column_config.NumberColumn(format="%.4f"),
                "DP Overall": st.column_config.NumberColumn(format="%.4f"),
                "DP Between": st.column_config.NumberColumn(format="%.4f"),
                "DP Within": st.column_config.NumberColumn(format="%.4f"),
                "Razão Within/Overall": st.column_config.NumberColumn(format="%.3f"),
            },
        )

        # Exportação LaTeX booktabs
        latex_desc_str = export_descriptive_to_latex(desc_df)
        dl_col1, dl_col2 = st.columns([1, 3])
        with dl_col1:
            st.download_button(
                label="📥 Baixar Tabela Descritiva em LaTeX (booktabs .tex)",
                data=latex_desc_str.encode("utf-8"),
                file_name="tabela_descritiva_painel_chap1.tex",
                mime="text/plain",
                width="stretch",
            )
        with dl_col2:
            with st.expander("📄 Visualizar Código LaTeX (`booktabs`) da Tabela Descritiva"):
                st.code(latex_desc_str, language="latex")

        st.markdown("---")
        st.subheader("2. Comparativo de Perda Amostral: PAM vs. GAEZ e Regra Crítica do IBAMA")
        sample_loss_df = compute_sample_loss_comparison(df_raw)

        col_sl1, col_sl2 = st.columns([1.35, 1.0])
        with col_sl1:
            st.dataframe(
                sample_loss_df,
                width="stretch",
                height=430,
                column_config={
                    "% Cobertura": st.column_config.ProgressColumn(
                        "% Cobertura", min_value=0.0, max_value=100.0, format="%.1f%%"
                    ),
                    "% Perda Amostral": st.column_config.NumberColumn(format="%.1f%%"),
                },
            )
        with col_sl2:
            fig_loss = px.bar(
                sample_loss_df.iloc[::-1],
                x="N Missing",
                y="Medida / Cenário",
                color="% Cobertura",
                orientation="h",
                text="N Missing",
                color_continuous_scale="RdYlGn",
                title="Observações Ausentes (Missings em N=3.384) por Proxy Candidata",
            )
            fig_loss.update_layout(height=430, margin=dict(l=10, r=20, t=45, b=20))
            st.plotly_chart(fig_loss, width="stretch")

        with st.expander("🔍 Auditoria Completa das 22 Variáveis do IBAMA (Antes vs. Depois da Imputação pela Flag)", expanded=False):
            ibama_audit_df = get_ibama_imputation_audit(df_raw)
            st.dataframe(ibama_audit_df, width="stretch")

        st.markdown("---")
        st.subheader("3. Heatmaps de Missings por Ano e Município")
        hm_mode = st.radio(
            "Modo de Visualização do Mapa de Missings:",
            options=[
                "Heatmap Variável × Ano (% de Missings nos Municípios por Ano)",
                "Heatmap Município × Ano (Inspeção de Variável Específica na Grade 141 × 24)",
            ],
            horizontal=True,
            key="tab1_hm_mode",
        )

        if hm_mode.startswith("Heatmap Variável"):
            default_hm_vars = [
                "taxa_conversao__agricultura",
                "taxa_conversao__pastagem",
                "capacidade_z__soja__pam_1991_2000_min7",
                "capacidade_z__milho__pam_1991_2000_min7",
                "capacidade_z__soja__gaez_yxHr0_soy",
                "capacidade_z__milho__gaez_yxHr0_mze",
                "rendimento_medio_kg_ha__Soja (em grão)",
                "rendimento_medio_kg_ha__Milho (em grão)",
                "n_autos_desmatamento__ibama_informada",
                "n_autos_flora__ibama_informada",
                "n_autos_desmatamento__ibama_espacial",
                "multas_desmatamento_reais_observadas__ibama_informada",
                "lotacao_cabecas_ha",
                "precip_mm_anual",
            ]
            available_hm_vars = [c for c in default_hm_vars if c in df.columns]
            all_substantive = [c for b in THEORETICAL_BLOCKS[:6] for c in blocks_map[b]]
            selected_hm_vars = st.multiselect(
                "Variáveis para o Heatmap de Missings por Ano:",
                options=all_substantive,
                default=available_hm_vars,
                key="tab1_hm_vars",
            )
            if selected_hm_vars:
                miss_year_df = compute_missing_summary_by_year(df, selected_hm_vars)
                fig_hm_year = px.imshow(
                    miss_year_df,
                    labels=dict(x="Ano", y="Variável", color="% Missing"),
                    color_continuous_scale="YlOrRd",
                    zmin=0,
                    zmax=100,
                    aspect="auto",
                    text_auto=".0f",
                    title="Porcentagem de Municípios com Valor Ausente (% Missing) por Ano (2001–2024)",
                )
                fig_hm_year.update_layout(height=max(380, 28 * len(selected_hm_vars)))
                st.plotly_chart(fig_hm_year, width="stretch")
        else:
            all_substantive = [c for b in THEORETICAL_BLOCKS[:6] for c in blocks_map[b]]
            target_muni_var = st.selectbox(
                "Escolha a variável para inspecionar na grade Município (`codigo_ibge`) × `ano`:",
                options=all_substantive,
                index=all_substantive.index("n_autos_desmatamento__ibama_informada")
                if "n_autos_desmatamento__ibama_informada" in all_substantive
                else 0,
                key="tab1_muni_hm_var",
            )
            piv = df.pivot(index="municipio_nome", columns="ano", values=target_muni_var)
            miss_grid = piv.isna().astype(int)
            fig_muni_hm = px.imshow(
                miss_grid,
                labels=dict(x="Ano", y="Município", color="Status (1=Missing, 0=Válido)"),
                color_continuous_scale=[[0.0, "#10b981"], [1.0, "#ef4444"]],
                zmin=0,
                zmax=1,
                aspect="auto",
                title=f"Mapa de Cobertura Municipal × Anual: {target_muni_var} (Verde = Válido | Vermelho = Missing)",
            )
            fig_muni_hm.update_layout(height=620)
            st.plotly_chart(fig_muni_hm, width="stretch")

    # =======================================================================
    # ABA 2: Dinâmica Temporal e Heterogeneidade por Bioma e Destino
    # =======================================================================
    with tabs[1]:
        st.subheader("1. Séries Temporais em Duplo Eixo: Conversão Bruta × Preços Agrícolas e Fiscalização IBAMA")
        c_ts1, c_ts2, c_ts3, c_ts4 = st.columns([1.2, 1.5, 1.6, 1.1])

        with c_ts1:
            y_metric_mode = st.selectbox(
                "Medida de Conversão ($Y$, Eixo Esquerdo):",
                options=[
                    "Taxa Média de Conversão (% a.a.)",
                    "Taxa Ponderada (Razão das Somas, % a.a.)",
                    "Área Convertida Total Observada (mil ha)",
                    "Mediana Municipal da Taxa (% a.a.)",
                ],
                key="tab2_y_mode",
            )
        with c_ts2:
            price_candidates = blocks_map["[X1] Preços e Choques"]
            default_price = (
                "preco_real_usd2024_media_anual_lag1__soja"
                if "preco_real_usd2024_media_anual_lag1__soja" in price_candidates
                else price_candidates[0]
            )
            selected_price_col = st.selectbox(
                "Série de Preço / Choque ($X_1$, Eixo Direito):",
                options=price_candidates,
                index=price_candidates.index(default_price),
                format_func=get_friendly_label,
                key="tab2_price_col",
            )
        with c_ts3:
            ibama_candidates = blocks_map["[X3] Ambiente Institucional (IBAMA)"]
            default_ibama = (
                "n_autos_desmatamento__ibama_informada"
                if "n_autos_desmatamento__ibama_informada" in ibama_candidates
                else ibama_candidates[0]
            )
            selected_ibama_col = st.selectbox(
                "Série Institucional IBAMA ($X_3$, Eixo Direito):",
                options=ibama_candidates,
                index=ibama_candidates.index(default_ibama),
                format_func=get_friendly_label,
                key="tab2_ibama_col",
            )
        with c_ts4:
            biome_view_ts = st.selectbox(
                "Recorte Territorial:",
                options=["Mato Grosso (Total)"] + selected_biomes,
                key="tab2_biome_view",
            )

        sub_ts = (
            df.copy()
            if biome_view_ts == "Mato Grosso (Total)"
            else df.loc[df["bioma_dominante"] == biome_view_ts].copy()
        )

        # Agregar série anual
        ts_rows = []
        for ano_val, grp in sub_ts.groupby("ano", observed=True):
            row_item = {"ano": int(ano_val)}
            for dest in ("agricultura", "pastagem"):
                t_col = f"taxa_conversao__{dest}"
                a_col = f"conversao_ha__{dest}"
                valid_mask = grp[[t_col, a_col, "y_nativa_inicial_ha"]].notna().all(axis=1) & (
                    grp["y_nativa_inicial_ha"] > 0
                )
                g_ok = grp.loc[valid_mask]
                if len(g_ok) == 0:
                    row_item[f"y_{dest}"] = np.nan
                elif y_metric_mode.startswith("Taxa Média"):
                    row_item[f"y_{dest}"] = 100.0 * float(g_ok[t_col].mean())
                elif y_metric_mode.startswith("Taxa Ponderada"):
                    denom = float(g_ok["y_nativa_inicial_ha"].sum())
                    row_item[f"y_{dest}"] = (
                        100.0 * float(g_ok[a_col].sum()) / denom if denom > 0 else np.nan
                    )
                elif y_metric_mode.startswith("Área Convertida"):
                    row_item[f"y_{dest}"] = float(g_ok[a_col].sum()) / 1000.0
                else:
                    row_item[f"y_{dest}"] = 100.0 * float(g_ok[t_col].median())

            row_item["price_val"] = float(pd.to_numeric(grp[selected_price_col], errors="coerce").mean())
            ib_s = pd.to_numeric(grp[selected_ibama_col], errors="coerce").dropna()
            row_item["ibama_mean"] = float(ib_s.mean()) if len(ib_s) > 0 else np.nan
            row_item["ibama_sum"] = float(ib_s.sum()) if len(ib_s) > 0 else np.nan
            ts_rows.append(row_item)

        ts_df = pd.DataFrame(ts_rows).sort_values("ano")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig_dual_price = make_subplots(specs=[[{"secondary_y": True}]])
            fig_dual_price.add_trace(
                go.Scatter(
                    x=ts_df["ano"],
                    y=ts_df["y_agricultura"],
                    name="Conversão -> Agricultura",
                    mode="lines+markers",
                    line=dict(color="#16a34a", width=2.8),
                ),
                secondary_y=False,
            )
            fig_dual_price.add_trace(
                go.Scatter(
                    x=ts_df["ano"],
                    y=ts_df["y_pastagem"],
                    name="Conversão -> Pastagem",
                    mode="lines+markers",
                    line=dict(color="#ca8a04", width=2.8),
                ),
                secondary_y=False,
            )
            fig_dual_price.add_trace(
                go.Scatter(
                    x=ts_df["ano"],
                    y=ts_df["price_val"],
                    name=f"Preço/Choque: {selected_price_col}",
                    mode="lines+markers",
                    line=dict(color="#1d4ed8", width=2.2, dash="dot"),
                ),
                secondary_y=True,
            )
            fig_dual_price.update_layout(
                title=f"Conversão Bruta vs. {selected_price_col} ({biome_view_ts})",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                height=430,
            )
            fig_dual_price.update_yaxes(title_text=y_metric_mode, secondary_y=False)
            fig_dual_price.update_yaxes(title_text=selected_price_col, secondary_y=True)
            st.plotly_chart(fig_dual_price, width="stretch")

        with col_p2:
            fig_dual_ibama = make_subplots(specs=[[{"secondary_y": True}]])
            fig_dual_ibama.add_trace(
                go.Scatter(
                    x=ts_df["ano"],
                    y=ts_df["y_agricultura"],
                    name="Conversão -> Agricultura",
                    mode="lines+markers",
                    line=dict(color="#16a34a", width=2.8),
                ),
                secondary_y=False,
            )
            fig_dual_ibama.add_trace(
                go.Scatter(
                    x=ts_df["ano"],
                    y=ts_df["y_pastagem"],
                    name="Conversão -> Pastagem",
                    mode="lines+markers",
                    line=dict(color="#ca8a04", width=2.8),
                ),
                secondary_y=False,
            )
            fig_dual_ibama.add_trace(
                go.Bar(
                    x=ts_df["ano"],
                    y=ts_df["ibama_mean"],
                    name=f"Média Municipal: {selected_ibama_col}",
                    marker_color="rgba(220, 38, 38, 0.35)",
                ),
                secondary_y=True,
            )
            fig_dual_ibama.update_layout(
                title=f"Conversão Bruta vs. Fiscalização IBAMA ({biome_view_ts})",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                height=430,
            )
            fig_dual_ibama.update_yaxes(title_text=y_metric_mode, secondary_y=False)
            fig_dual_ibama.update_yaxes(title_text=f"Média Municipal ({selected_ibama_col})", secondary_y=True)
            st.plotly_chart(fig_dual_ibama, width="stretch")

        st.markdown("---")
        st.subheader("2. Evolução Estratificada por Bioma Dominante (Amazônia, Cerrado e Pantanal)")
        bio_ts_rows = []
        for (ano_val, bio_val), grp in df.groupby(["ano", "bioma_dominante"], observed=True):
            for dest, label_dest in [("agricultura", "Agricultura"), ("pastagem", "Pastagem")]:
                t_col = f"taxa_conversao__{dest}"
                a_col = f"conversao_ha__{dest}"
                s_t = pd.to_numeric(grp[t_col], errors="coerce").dropna()
                s_a = pd.to_numeric(grp[a_col], errors="coerce").dropna()
                bio_ts_rows.append({
                    "ano": int(ano_val),
                    "Bioma Dominante": str(bio_val),
                    "Destino": label_dest,
                    "Taxa Média (% a.a.)": 100.0 * float(s_t.mean()) if len(s_t) > 0 else np.nan,
                    "Área Convertida (mil ha)": float(s_a.sum()) / 1000.0 if len(s_a) > 0 else np.nan,
                })
        bio_ts_df = pd.DataFrame(bio_ts_rows)

        fig_bio_facet = px.line(
            bio_ts_df,
            x="ano",
            y="Taxa Média (% a.a.)",
            color="Bioma Dominante",
            facet_col="Destino",
            markers=True,
            color_discrete_map=BIOME_COLORS,
            title="Taxa Média Anual de Conversão Bruta (% da Vegetação Nativa Inicial) por Bioma e Destino",
        )
        fig_bio_facet.update_layout(height=390, hovermode="x unified")
        st.plotly_chart(fig_bio_facet, width="stretch")

        st.markdown("---")
        st.subheader("3. Distribuição da Conversão por Bioma Dominante (Boxplots e Violinos)")
        d_col1, d_col2, d_col3 = st.columns([1.3, 1.3, 1.4])
        with d_col1:
            dist_plot_type = st.radio(
                "Tipo de Gráfico de Distribuição:",
                options=["Violin Plot (com Boxplot interno)", "Boxplot Clássico"],
                horizontal=True,
                key="tab2_dist_type",
            )
        with d_col2:
            dist_measure = st.selectbox(
                "Unidade da Conversão:",
                options=[
                    "Taxa de Conversão (% da vegetação nativa inicial)",
                    "Área Convertida Bruta (hectares)",
                ],
                key="tab2_dist_measure",
            )
        with d_col3:
            trim_p99 = st.checkbox(
                "Aparar apenas na visualização acima do Percentil 99 (evitar achatamento visual)",
                value=True,
                key="tab2_trim99",
            )

        if dist_measure.startswith("Taxa"):
            m_cols = ["taxa_conversao__agricultura", "taxa_conversao__pastagem"]
            scale_mult = 100.0
            y_label_dist = "Taxa de Conversão (% a.a.)"
        else:
            m_cols = ["conversao_ha__agricultura", "conversao_ha__pastagem"]
            scale_mult = 1.0
            y_label_dist = "Área Convertida (ha)"

        long_dist = df[["codigo_ibge", "municipio_nome", "ano", "bioma_dominante"] + m_cols].melt(
            id_vars=["codigo_ibge", "municipio_nome", "ano", "bioma_dominante"],
            value_vars=m_cols,
            var_name="Variável",
            value_name="Valor",
        ).dropna(subset=["Valor"])
        long_dist["Valor"] = pd.to_numeric(long_dist["Valor"], errors="coerce") * scale_mult
        long_dist["Destino"] = long_dist["Variável"].map(
            lambda x: "Agricultura" if "agricultura" in x else "Pastagem"
        )

        if trim_p99 and not long_dist.empty:
            q99 = long_dist.groupby("Destino")["Valor"].transform(lambda s: s.quantile(0.99))
            long_dist = long_dist.loc[long_dist["Valor"] <= q99]

        if dist_plot_type.startswith("Violin"):
            fig_dist = px.violin(
                long_dist,
                x="bioma_dominante",
                y="Valor",
                color="Destino",
                box=True,
                points="outliers",
                hover_data=["municipio_nome", "ano"],
                color_discrete_map={"Agricultura": "#16a34a", "Pastagem": "#ca8a04"},
                title=f"Distribuição de {y_label_dist} por Bioma Dominante e Destino Agropecuário",
            )
        else:
            fig_dist = px.box(
                long_dist,
                x="bioma_dominante",
                y="Valor",
                color="Destino",
                points="outliers",
                hover_data=["municipio_nome", "ano"],
                color_discrete_map={"Agricultura": "#16a34a", "Pastagem": "#ca8a04"},
                title=f"Boxplot de {y_label_dist} por Bioma Dominante e Destino Agropecuário",
            )
        fig_dist.update_layout(
            xaxis_title="Bioma Dominante",
            yaxis_title=y_label_dist,
            boxmode="group" if not dist_plot_type.startswith("Violin") else None,
            violinmode="group" if dist_plot_type.startswith("Violin") else None,
            height=450,
        )
        st.plotly_chart(fig_dist, width="stretch")

    # =======================================================================
    # ABA 3: Batalha de Proxies, Colinearidade e VIF (X2 e X3)
    # =======================================================================
    with tabs[2]:
        st.subheader("Batalha de Proxies, Matriz de Correlação e Diagnóstico de Multicolinearidade (VIF)")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Objetivo desta aba:</b> Selecionar de forma fundamentada quais proxies de <b>Capacidade Produtiva ($X_2$)</b>,
            <b>Ambiente Institucional IBAMA ($X_3$)</b> e <b>Anomalias Climáticas (CHIRPS)</b> devem entrar nas especificações econométricas,
            evitando colinearidade severa ($\text{VIF} \ge 10$) e perda amostral desnecessária.
            </div>
            """,
            unsafe_allow_html=True,
        )

        PROXY_PRESETS = {
            "1. Batalha X2 — Capacidade Produtiva: 8 Variantes GAEZ (sxHr0, sxLr0, yxHr0, yxLr0) vs. PAM (1991-2000)": [
                "capacidade_z__soja__pam_1991_2000_min7",
                "capacidade_z__milho__pam_1991_2000_min7",
                "capacidade_z__soja__gaez_sxHr0_soy",
                "capacidade_z__soja__gaez_sxLr0_soy",
                "capacidade_z__soja__gaez_yxHr0_soy",
                "capacidade_z__soja__gaez_yxLr0_soy",
                "capacidade_z__milho__gaez_sxHr0_mze",
                "capacidade_z__milho__gaez_sxLr0_mze",
                "capacidade_z__milho__gaez_yxHr0_mze",
                "capacidade_z__milho__gaez_yxLr0_mze",
                "rendimento_medio_kg_ha__Soja (em grão)",
                "rendimento_medio_kg_ha__Milho (em grão)",
            ],
            "2. Batalha X1*X2 — Interações ln(Preço Real t-1) × Capacidade Z (GAEZ vs. PAM)": [
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__pam_1991_2000_min7",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__milho__pam_1991_2000_min7",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_sxHr0_soy",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_sxLr0_soy",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_yxHr0_soy",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_yxLr0_soy",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__milho__gaez_sxHr0_mze",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__milho__gaez_sxLr0_mze",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__milho__gaez_yxHr0_mze",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__milho__gaez_yxLr0_mze",
            ],
            "3. Batalha X3 — IBAMA: Informada vs. Espacial, Flora vs. Desmatamento, Autos vs. Multas Reais": [
                "n_autos_observados__ibama_informada",
                "n_autos_observados__ibama_espacial",
                "n_autos_flora__ibama_informada",
                "n_autos_flora__ibama_espacial",
                "n_autos_desmatamento__ibama_informada",
                "n_autos_desmatamento__ibama_espacial",
                "multas_flora_reais_observadas__ibama_informada",
                "multas_flora_reais_observadas__ibama_espacial",
                "multas_desmatamento_reais_observadas__ibama_informada",
                "multas_desmatamento_reais_observadas__ibama_espacial",
                "n_autos_desmatamento_lag1__ibama_informada",
                "n_autos_desmatamento_lag1__ibama_espacial",
                "multas_desmatamento_reais_observadas_lag1__ibama_informada",
                "multas_desmatamento_reais_observadas_lag1__ibama_espacial",
            ],
            "4. Batalha de Anomalias Climáticas CHIRPS (1981-2000 vs. 1981-2010 vs. 1991-2020)": [
                "precip_mm_anual",
                "precip_anomaly_1981_2000",
                "precip_zscore_1981_2000",
                "precip_deficit_1981_2000",
                "precip_excess_1981_2000",
                "precip_anomaly_1981_2010",
                "precip_zscore_1981_2010",
                "precip_deficit_1981_2010",
                "precip_excess_1981_2010",
                "precip_anomaly_1991_2020",
                "precip_zscore_1991_2020",
                "precip_deficit_1991_2020",
                "precip_excess_1991_2020",
            ],
            "5. Especificação Candidata Integrada (Interações GAEZ High Input + IBAMA + Clima)": [
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_yxHr0_soy",
                "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__milho__gaez_yxHr0_mze",
                "n_autos_desmatamento_lag1__ibama_informada",
                "multas_desmatamento_reais_observadas_lag1__ibama_informada",
                "precip_zscore_1981_2010",
                "lotacao_cabecas_ha",
                "nativa_share_lag1",
            ],
        }

        c_pr1, c_pr2, c_pr3 = st.columns([2.2, 1.0, 1.2])
        with c_pr1:
            chosen_preset = st.selectbox(
                "Escolha a Arena da Batalha de Proxies:",
                options=list(PROXY_PRESETS.keys()),
                key="tab3_preset",
            )
        with c_pr2:
            corr_method = st.radio(
                "Método de Correlação:",
                options=["pearson", "spearman"],
                format_func=lambda m: "Pearson (Linear)" if m == "pearson" else "Spearman (Postos)",
                horizontal=True,
                key="tab3_corr_method",
            )
        with c_pr3:
            vif_demean = st.selectbox(
                "Transformação para Cálculo do VIF:",
                options=["pooled", "within_entity", "double_demeaned"],
                format_func=lambda x: {
                    "pooled": "Nível (Pooled OLS)",
                    "within_entity": "Within Município (FE_i)",
                    "double_demeaned": "Double-Demeaned (FE_i + FE_t)",
                }[x],
                key="tab3_vif_demean",
            )

        all_numeric_candidates = [c for b in THEORETICAL_BLOCKS[:6] for c in blocks_map[b]]
        preset_cols = [c for c in PROXY_PRESETS[chosen_preset] if c in df.columns]
        selected_proxy_cols = st.multiselect(
            "Variáveis incluídas na Matriz de Correlação e no Cálculo de VIF (adicione ou remova livremente):",
            options=all_numeric_candidates,
            default=preset_cols,
            key="tab3_vars",
        )

        if len(selected_proxy_cols) >= 2:
            corr_mat = compute_correlation_matrix(df, selected_proxy_cols, method=corr_method)
            vif_df = compute_vif_table(df, selected_proxy_cols, demean_mode=vif_demean)

            col_c1, col_c2 = st.columns([1.35, 1.0])
            with col_c1:
                fig_corr = px.imshow(
                    corr_mat,
                    text_auto=".2f",
                    color_continuous_scale="RdBu_r",
                    zmin=-1.0,
                    zmax=1.0,
                    aspect="auto",
                    title=f"Matriz de Correlação ({corr_method.capitalize()})",
                )
                fig_corr.update_layout(height=max(460, 36 * len(selected_proxy_cols)))
                st.plotly_chart(fig_corr, width="stretch")

            with col_c2:
                st.markdown("#### Diagnóstico de Multicolinearidade (VIF)")
                st.dataframe(
                    vif_df,
                    width="stretch",
                    height=260,
                )
                vif_plot_df = vif_df.copy()
                vif_plot_df["VIF_Plot"] = vif_plot_df["VIF"].replace(np.inf, np.nan).clip(upper=50.0)
                fig_vif = px.bar(
                    vif_plot_df.dropna(subset=["VIF_Plot"]).iloc[::-1],
                    x="VIF_Plot",
                    y="Variável",
                    color="Diagnóstico",
                    orientation="h",
                    text="VIF",
                    color_discrete_map={
                        "Baixa Colinearidade (VIF < 5)": "#16a34a",
                        "Atenção / Moderada (5 <= VIF < 10)": "#eab308",
                        "Alta Multicolinearidade (VIF >= 10)": "#dc2626",
                        "Colinearidade Perfeita / Extrema (VIF > 100)": "#7f1d1d",
                    },
                    title="VIF (Variance Inflation Factor — truncado em 50 para escala visual)",
                )
                fig_vif.add_vline(x=5.0, line_dash="dash", line_color="#eab308", annotation_text="VIF=5")
                fig_vif.add_vline(x=10.0, line_dash="dash", line_color="#dc2626", annotation_text="VIF=10")
                fig_vif.update_layout(height=280, showlegend=False)
                st.plotly_chart(fig_vif, width="stretch")
        else:
            st.info("Selecione ao menos 2 variáveis para calcular a matriz de correlação e o VIF.")

    # =======================================================================
    # ABA 4: Visualizador Binscatter Econométrico e Relações Within
    # =======================================================================
    with tabs[3]:
        st.subheader("Visualizador Binscatter Econométrico: Nível (Pooled), Within Município e Double-Demeaned")
        st.markdown(
            """
            <div class="hypothesis-box">
            <b>O que o Binscatter Econométrico faz?</b> Agrupa as observações $(X_{it}, Y_{it})$ em $Q$ quantis de $X$
            e plota a média de $Y$ contra a média de $X$ em cada bin, sobrepondo a reta de regressão OLS. Quando selecionado o modo
            <b>Double-Demeaned (Município + Ano)</b>, tanto $Y$ quanto $X$ são residualizados em relação aos efeitos fixos de município e ano
            (Teorema de Frisch-Waugh-Lovell), revelando a inclinação exata do estimador Two-Way Fixed Effects!
            </div>
            """,
            unsafe_allow_html=True,
        )

        b_col1, b_col2, b_col3, b_col4 = st.columns([1.4, 1.8, 1.2, 1.0])
        y_vars_all = blocks_map["[Y] Conversão e Uso da Terra"]
        x_vars_all = [
            c for b in [
                "[X1*X2] Interações e Exposição",
                "[X3] Ambiente Institucional (IBAMA)",
                "[X2] Capacidade Produtiva (PAM vs GAEZ)",
                "[X1] Preços e Choques",
                "[Controles] Clima, Geografia e Biomas",
                "[Y] Conversão e Uso da Terra",
            ]
            for c in blocks_map[b]
        ]

        with b_col1:
            bin_y = st.selectbox(
                "Variável Dependente ($Y$):",
                options=y_vars_all,
                index=y_vars_all.index("taxa_conversao__agricultura")
                if "taxa_conversao__agricultura" in y_vars_all
                else 0,
                format_func=get_friendly_label,
                key="tab4_y",
            )
        with b_col2:
            default_bin_x = "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_yxHr0_soy"
            bin_x = st.selectbox(
                "Variável Explicativa ($X$):",
                options=x_vars_all,
                index=x_vars_all.index(default_bin_x) if default_bin_x in x_vars_all else 0,
                format_func=get_friendly_label,
                key="tab4_x",
            )
        with b_col3:
            bin_mode = st.selectbox(
                "Transformação Econométrica:",
                options=["double_demeaned", "within_entity", "pooled"],
                format_func=lambda m: {
                    "pooled": "1. Nível (Pooled)",
                    "within_entity": "2. Within Município (Demeaned)",
                    "double_demeaned": "3. Double-Demeaned (Município + Ano)",
                }[m],
                key="tab4_mode",
            )
        with b_col4:
            n_bins = st.slider(
                "Quantis ($Q$ bins):",
                min_value=5,
                max_value=50,
                value=20,
                step=1,
                key="tab4_q",
            )

        b_opt1, b_opt2, b_opt3 = st.columns([1.2, 1.4, 1.4])
        with b_opt1:
            stratify_biome_bin = st.checkbox(
                "Estratificar curvas e bins por Bioma Dominante",
                value=False,
                key="tab4_strat_biome",
            )
        with b_opt2:
            hide_outliers = st.checkbox(
                "Ocultar top outliers / pontos de alta alavancagem",
                value=False,
                key="tab4_hide_outliers",
            )
        with b_opt3:
            outlier_pct = st.slider(
                "Corte simétrico de caudas (% em cada cauda de X/Y) se filtro ativo:",
                min_value=0.5,
                max_value=5.0,
                value=1.0,
                step=0.5,
                disabled=not hide_outliers,
                key="tab4_outlier_pct",
            )

        # Preparar par (Y, X) válido antes de aplicar Within/Double-Demeaned (FWL exato na amostra comum)
        pair_df = df[["codigo_ibge", "ano", "bioma_dominante", bin_y, bin_x]].copy()
        pair_df[bin_y] = pd.to_numeric(pair_df[bin_y], errors="coerce")
        pair_df[bin_x] = pd.to_numeric(pair_df[bin_x], errors="coerce")
        pair_df = pair_df.dropna(subset=[bin_y, bin_x]).reset_index(drop=True)

        if len(pair_df) < 10:
            st.warning("Amostra válida insuficiente para construir o Binscatter.")
        else:
            dm_pair = transform_within(
                pair_df,
                columns=[bin_y, bin_x],
                mode=bin_mode,
                add_grand_mean=False,
            )

            if hide_outliers:
                alpha_tail = outlier_pct / 100.0
                qx_low, qx_high = dm_pair[bin_x].quantile([alpha_tail, 1.0 - alpha_tail])
                qy_low, qy_high = dm_pair[bin_y].quantile([alpha_tail, 1.0 - alpha_tail])
                dm_pair = dm_pair.loc[
                    dm_pair[bin_x].between(qx_low, qx_high)
                    & dm_pair[bin_y].between(qy_low, qy_high)
                ].reset_index(drop=True)

            x_std = float(dm_pair[bin_x].std(ddof=1))
            if x_std <= 1e-10:
                st.error(
                    f"A variável `{bin_x}` possui variância zero após a transformação `{bin_mode}` "
                    "(ex.: variável invariante no tempo absorvida pelo Efeito Fixo de Município ou variável macro absorvida pelo Efeito Fixo de Ano). "
                    "Altere a transformação para 'Nível (Pooled)' ou escolha uma variável que varie entre municípios e anos (como [X1*X2])."
                )
            else:
                fig_bin = go.Figure()
                groups_iter = (
                    [(b, dm_pair.loc[dm_pair["bioma_dominante"] == b]) for b in selected_biomes]
                    if stratify_biome_bin
                    else [("Mato Grosso (Total)", dm_pair)]
                )

                ols_summary_rows = []
                for g_name, g_df in groups_iter:
                    if len(g_df) < max(5, n_bins):
                        continue
                    g_work = g_df.copy()
                    try:
                        g_work["bin"] = pd.qcut(g_work[bin_x], q=n_bins, labels=False, duplicates="drop")
                    except ValueError:
                        g_work["bin"] = pd.cut(g_work[bin_x], bins=n_bins, labels=False)

                    binned = (
                        g_work.groupby("bin", observed=True)
                        .agg(
                            x_mean=(bin_x, "mean"),
                            y_mean=(bin_y, "mean"),
                            y_se=(bin_y, lambda s: s.std(ddof=1) / np.sqrt(len(s)) if len(s) > 1 else 0.0),
                            n_obs=(bin_y, "count"),
                        )
                        .reset_index()
                    )

                    color_g = BIOME_COLORS.get(g_name, "#1d4ed8")
                    fig_bin.add_trace(
                        go.Scatter(
                            x=binned["x_mean"],
                            y=binned["y_mean"],
                            error_y=dict(
                                type="data",
                                array=1.96 * binned["y_se"],
                                visible=not stratify_biome_bin,
                                thickness=1.2,
                                color="rgba(100,116,139,0.45)",
                            ),
                            mode="markers",
                            marker=dict(size=10, color=color_g, line=dict(width=1, color="#ffffff")),
                            name=f"Bins ({g_name})",
                            customdata=binned[["n_obs"]],
                            hovertemplate=(
                                f"<b>{g_name}</b><br>"
                                "Média X no Bin: %{x:.5f}<br>"
                                "Média Y no Bin: %{y:.5f}<br>"
                                "N no Bin: %{customdata[0]}<extra></extra>"
                            ),
                        )
                    )

                    # Ajuste OLS sobre os microdados (mesma inclinação da regressão linear)
                    X_ols = sm.add_constant(g_work[bin_x].to_numpy(dtype="float64"))
                    y_ols = g_work[bin_y].to_numpy(dtype="float64")
                    ols_res = sm.OLS(y_ols, X_ols).fit()
                    b0, b1 = float(ols_res.params[0]), float(ols_res.params[1])
                    se1 = float(ols_res.bse[1])
                    t1 = float(ols_res.tvalues[1])
                    p1 = float(ols_res.pvalues[1])
                    r2 = float(ols_res.rsquared)

                    x_grid = np.linspace(float(binned["x_mean"].min()), float(binned["x_mean"].max()), 100)
                    y_hat = b0 + b1 * x_grid
                    fig_bin.add_trace(
                        go.Scatter(
                            x=x_grid,
                            y=y_hat,
                            mode="lines",
                            line=dict(color=color_g, width=2.6),
                            name=f"OLS {g_name} (β={b1:.4g}, p={p1:.3f})",
                        )
                    )

                    ols_summary_rows.append({
                        "Grupo / Bioma": g_name,
                        "Transformação": bin_mode,
                        "N Observações": len(g_work),
                        "Quantis Efetivos": len(binned),
                        "Inclinação OLS (β)": b1,
                        "Erro-Padrão": se1,
                        "Estatística t": t1,
                        "p-valor": p1,
                        "R²": r2,
                    })

                fig_bin.update_layout(
                    title=f"Binscatter Econométrico ({n_bins} Quantis) — {bin_y} vs. {bin_x} [{bin_mode}]",
                    xaxis_title=f"{bin_x} ({bin_mode})",
                    yaxis_title=f"{bin_y} ({bin_mode})",
                    height=500,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                )
                st.plotly_chart(fig_bin, width="stretch")

                if ols_summary_rows:
                    st.markdown("#### Parâmetros da Reta de Ajuste OLS sobre os Dados Transformados")
                    st.dataframe(pd.DataFrame(ols_summary_rows), width="stretch")

    # =======================================================================
    # ABA 5: Laboratório de Pré-Seleção Econométrica (Teste de H1, H1-a e H1-b)
    # =======================================================================
    with tabs[4]:
        st.subheader("Laboratório de Pré-Seleção Econométrica — Modelos Two-Way FE (H1, H1-a e H1-b)")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Equação Estrutural de Pré-Seleção (Two-Way Fixed Effects):</b><br>
            $$Y_{it} = \alpha_i + \gamma_t + \beta_1 (X_{1,t-1} \times X_{2,i}) + \beta_2 X_{3,i,t-1} + \beta_3 (X_{1,t-1} \times X_{2,i} \times X_{3,i,t-1}) + \mathbf{Z}_{it}'\boldsymbol{\delta} + \varepsilon_{it}$$
            onde $\alpha_i$ são efeitos fixos municipais (`codigo_ibge`), $\gamma_t$ são efeitos fixos de ano (`ano`), e os erros-padrão são
            clusterizados ao nível de município. <b>H1-a</b> prevê $\beta_1 > 0$ (maior pressão de conversão onde a capacidade produtiva é mais alta)
            e <b>H1-b</b> avalia se o condicionamento institucional modifica/amortece essa resposta ($\beta_3 \neq 0$, tipicamente $\beta_3 < 0$).
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Controles de especificação
        lab_c1, lab_c2 = st.columns([1.2, 1.8])
        with lab_c1:
            dep_candidates = [
                "taxa_conversao__agricultura",
                "taxa_conversao__pastagem",
                "conversao_ha__agricultura",
                "conversao_ha__pastagem",
            ] + [
                c for c in blocks_map["[Y] Conversão e Uso da Terra"]
                if c not in {
                    "taxa_conversao__agricultura",
                    "taxa_conversao__pastagem",
                    "conversao_ha__agricultura",
                    "conversao_ha__pastagem",
                }
            ]
            lab_dep_var = st.selectbox(
                "1. Variável Dependente ($Y_{it}$):",
                options=dep_candidates,
                index=0,
                format_func=get_friendly_label,
                key="tab5_dep",
            )

            fe_col1, fe_col2 = st.columns(2)
            with fe_col1:
                use_entity_fe = st.checkbox("EF Município (`codigo_ibge`)", value=True, key="tab5_fe_i")
            with fe_col2:
                use_time_fe = st.checkbox("EF Ano (`ano`)", value=True, key="tab5_fe_t")

            std_x3_triple = st.checkbox(
                r"Padronizar $X_3$ (Z-score) na interação tripla $X_1 \times X_2 \times X_3$",
                value=True,
                help="Padronizar X3 na interação tripla preserva a interpretação de β1 como o efeito de Preço × Capacidade avaliado na média de fiscalização do IBAMA.",
                key="tab5_std_x3",
            )

        with lab_c2:
            x1x2_candidates = blocks_map["[X1*X2] Interações e Exposição"]
            default_x1x2 = [
                c for c in [
                    "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_yxHr0_soy",
                    "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__milho__gaez_yxHr0_mze",
                ]
                if c in x1x2_candidates
            ]
            lab_x1x2_vars = st.multiselect(
                r"2. Proxies de Retorno Esperado: Interações Preço × Capacidade ($X_1 \times X_2$ — Teste de H1-a):",
                options=x1x2_candidates,
                default=default_x1x2,
                key="tab5_x1x2",
            )

            x3_candidates = blocks_map["[X3] Ambiente Institucional (IBAMA)"]
            default_x3 = [
                c for c in ["n_autos_desmatamento_lag1__ibama_informada"]
                if c in x3_candidates
            ]
            lab_x3_vars = st.multiselect(
                "3. Variáveis de Fiscalização / Autuação do IBAMA ($X_3$ — Ambiente Institucional):",
                options=x3_candidates,
                default=default_x3,
                format_func=get_friendly_label,
                key="tab5_x3",
            )

        lab_c3, lab_c4 = st.columns([1.5, 1.5])
        with lab_c3:
            include_triple_h1b = st.checkbox(
                r"4. Incluir Interação Tripla ($X_1 \times X_2 \times X_3$) para testar Condicionamento Institucional (H1-b)",
                value=True,
                key="tab5_inc_triple",
            )
            triple_pairs_available = [
                (x12, x3) for x12 in lab_x1x2_vars for x3 in lab_x3_vars
            ]
            selected_triple_pairs = []
            if include_triple_h1b and triple_pairs_available:
                pair_labels = {f"{x12}  ×  {x3}": (x12, x3) for x12, x3 in triple_pairs_available}
                chosen_labels = st.multiselect(
                    r"Pares ($X_1 \times X_2$, $X_3$) para Interação Tripla H1-b:",
                    options=list(pair_labels.keys()),
                    default=list(pair_labels.keys()),
                    key="tab5_triple_pairs",
                )
                selected_triple_pairs = [pair_labels[k] for k in chosen_labels]

        with lab_c4:
            control_candidates = (
                blocks_map["[Controles] Clima, Geografia e Biomas"]
                + [
                    c for c in blocks_map["[Y] Conversão e Uso da Terra"]
                    if c in {"lotacao_cabecas_ha", "efetivo_bovino_lag1", "nativa_share_lag1", "pastagem_share_lag1", "agricultura_share_lag1"}
                ]
                + [
                    c for c in blocks_map["[X2] Capacidade Produtiva (PAM vs GAEZ)"]
                    if c.startswith("rendimento_")
                ]
            )
            default_controls = [
                c for c in ["precip_zscore_1981_2010", "lotacao_cabecas_ha"]
                if c in control_candidates
            ]
            lab_controls = st.multiselect(
                r"5. Controles Climáticos e Agropecuários ($\mathbf{Z}_{it}$):",
                options=control_candidates,
                default=default_controls,
                format_func=get_friendly_label,
                key="tab5_controls",
            )

        # Construção da bateria Horse Race (Progressão de Especificações)
        specs_to_run = []
        if lab_x1x2_vars:
            # (1) Baseline H1-a: Apenas Preço × Capacidade
            specs_to_run.append(
                SpecificationConfig(
                    name="(1) Baseline H1-a (X1×X2)",
                    dep_var=lab_dep_var,
                    x1x2_vars=lab_x1x2_vars,
                    x3_vars=[],
                    triple_interactions=[],
                    control_vars=[],
                    entity_effects=use_entity_fe,
                    time_effects=use_time_fe,
                    standardize_x3_in_triple=std_x3_triple,
                )
            )
        if lab_x1x2_vars and lab_controls:
            # (2) H1-a + Controles Climáticos/Agro
            specs_to_run.append(
                SpecificationConfig(
                    name="(2) H1-a + Controles",
                    dep_var=lab_dep_var,
                    x1x2_vars=lab_x1x2_vars,
                    x3_vars=[],
                    triple_interactions=[],
                    control_vars=lab_controls,
                    entity_effects=use_entity_fe,
                    time_effects=use_time_fe,
                    standardize_x3_in_triple=std_x3_triple,
                )
            )
        if lab_x3_vars:
            # (3) H1-a + IBAMA Direto (X3) + Controles
            specs_to_run.append(
                SpecificationConfig(
                    name="(3) + IBAMA Direto (X3)",
                    dep_var=lab_dep_var,
                    x1x2_vars=lab_x1x2_vars,
                    x3_vars=lab_x3_vars,
                    triple_interactions=[],
                    control_vars=lab_controls,
                    entity_effects=use_entity_fe,
                    time_effects=use_time_fe,
                    standardize_x3_in_triple=std_x3_triple,
                )
            )
        if selected_triple_pairs:
            # (4) Modelo Completo H1-b: Interação Tripla (X1 × X2 × X3) + Controles
            specs_to_run.append(
                SpecificationConfig(
                    name="(4) Completo H1-b (Tripla X1×X2×X3)",
                    dep_var=lab_dep_var,
                    x1x2_vars=lab_x1x2_vars,
                    x3_vars=lab_x3_vars,
                    triple_interactions=selected_triple_pairs,
                    control_vars=lab_controls,
                    entity_effects=use_entity_fe,
                    time_effects=use_time_fe,
                    standardize_x3_in_triple=std_x3_triple,
                )
            )

        # Opção extra: Comparar o modelo completo no destino alternativo (Agricultura vs. Pastagem)
        include_alt_dest_spec = st.checkbox(
            "Adicionar coluna comparativa com o Destino Alternativo (Agricultura vs. Pastagem) no Horse Race",
            value=True,
            key="tab5_alt_dest",
        )
        if include_alt_dest_spec and (lab_x1x2_vars or lab_x3_vars):
            alt_map = {
                "taxa_conversao__agricultura": "taxa_conversao__pastagem",
                "taxa_conversao__pastagem": "taxa_conversao__agricultura",
                "conversao_ha__agricultura": "conversao_ha__pastagem",
                "conversao_ha__pastagem": "conversao_ha__agricultura",
            }
            alt_y = alt_map.get(lab_dep_var)
            if alt_y and alt_y in df.columns:
                specs_to_run.append(
                    SpecificationConfig(
                        name=f"({len(specs_to_run)+1}) Destino Alt.: {alt_y.split('__')[-1].capitalize()}",
                        dep_var=alt_y,
                        x1x2_vars=lab_x1x2_vars,
                        x3_vars=lab_x3_vars,
                        triple_interactions=selected_triple_pairs,
                        control_vars=lab_controls,
                        entity_effects=use_entity_fe,
                        time_effects=use_time_fe,
                        standardize_x3_in_triple=std_x3_triple,
                    )
                )

        if not specs_to_run:
            st.warning(r"Selecione ao menos uma proxy em (2) $X_1 \times X_2$ ou (3) IBAMA $X_3$ para estimar os modelos.")
        else:
            try:
                long_reg_df, wide_reg_df, raw_reg_results = run_horse_race(df, specs_to_run)

                st.markdown("### 📋 Tabela Comparativa de Regressões Efeitos Fixos (Horse Race)")
                st.caption(
                    "Erros-padrão clusterizados por município (`codigo_ibge`) entre parênteses. "
                    "Significância: * p<0.10, ** p<0.05, *** p<0.01."
                )
                st.dataframe(wide_reg_df, width="stretch", height=420)

                # Exportação LaTeX e CSV
                latex_reg_str = export_horse_race_to_latex(raw_reg_results)
                ex_c1, ex_c2, ex_c3 = st.columns([1.1, 1.1, 2.0])
                with ex_c1:
                    st.download_button(
                        label="📥 Baixar Tabela de Regressões em LaTeX (.tex)",
                        data=latex_reg_str.encode("utf-8"),
                        file_name="tabela_regressoes_fe_h1_chap1.tex",
                        mime="text/plain",
                        width="stretch",
                    )
                with ex_c2:
                    st.download_button(
                        label="📥 Baixar Coeficientes e IC 95% (.csv)",
                        data=long_reg_df.to_csv(index=False).encode("utf-8"),
                        file_name="coeficientes_horse_race_chap1.csv",
                        mime="text/csv",
                        width="stretch",
                    )
                with ex_c3:
                    with st.expander("📄 Visualizar Código LaTeX (`booktabs`) das Regressões"):
                        st.code(latex_reg_str, language="latex")

                st.markdown("---")
                st.markdown(r"### 🌲 Forest Plot dos Coeficientes Estimados ($\hat{\beta}$ e IC 95% Clusterizado)")
                if not long_reg_df.empty:
                    fp_df = long_reg_df.copy()
                    fp_df["err_plus"] = fp_df["IC 95% Sup"] - fp_df["Coeficiente"]
                    fp_df["err_minus"] = fp_df["Coeficiente"] - fp_df["IC 95% Inf"]

                    fig_forest = px.scatter(
                        fp_df,
                        x="Coeficiente",
                        y="Variável",
                        color="Especificação",
                        error_x="err_plus",
                        error_x_minus="err_minus",
                        hover_data=[
                            "Variável Dependente",
                            "Erro-Padrão (Cluster)",
                            "Estatística t",
                            "p-valor",
                            "N",
                            "R² Within",
                        ],
                        title="Estimativas Ponto e Intervalo de Confiança 95% (Clusterizado por Município)",
                    )
                    fig_forest.add_vline(x=0.0, line_dash="dash", line_color="#dc2626", line_width=1.8)
                    fig_forest.update_traces(marker=dict(size=10))
                    fig_forest.update_layout(
                        height=max(380, 48 * fp_df["Variável"].nunique()),
                        xaxis_title="Coeficiente Estimado (β̂) e IC 95%",
                        yaxis_title="Variável Explicativa",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                    )
                    st.plotly_chart(fig_forest, width="stretch")

                with st.expander("🔎 Tabela Numérica Detalhada (Coeficientes, EP Cluster, t, p-valor, IC 95%, N, R² Within)"):
                    st.dataframe(
                        long_reg_df,
                        width="stretch",
                        column_config={
                            "Coeficiente": st.column_config.NumberColumn(format="%.6f"),
                            "Erro-Padrão (Cluster)": st.column_config.NumberColumn(format="%.6f"),
                            "Estatística t": st.column_config.NumberColumn(format="%.3f"),
                            "p-valor": st.column_config.NumberColumn(format="%.4f"),
                            "IC 95% Inf": st.column_config.NumberColumn(format="%.6f"),
                            "IC 95% Sup": st.column_config.NumberColumn(format="%.6f"),
                            "R² Within": st.column_config.NumberColumn(format="%.4f"),
                        },
                    )
            except Exception as reg_exc:
                st.error(f"Erro na estimação econométrica: {reg_exc}")

    # =======================================================================
    # ABA 6: Análise Univariada, Concentração Espacial & Intuição Econômica
    # =======================================================================
    with tabs[5]:
        st.subheader("1. Radiografia Univariada Profunda: Margem Extensiva vs. Intensiva, Assimetria e Biomas")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Intuição Econômica da Análise Univariada na Tese (Cap. 1):</b><br>
            • <b>Margem Extensiva ($X_{it} = 0$) vs. Margem Intensiva ($X_{it} > 0$):</b> Nas decisões privadas de conversão de vegetação nativa
            (<i>Angelsen, 2010; Lubowski et al., 2008</i>) e nos registros de autuação do IBAMA, zeros observados refletem soluções de canto
            (municípios-ano onde o retorno líquido esperado não superou o custo/risco de abertura ou onde não houve infração autuada). Separar a
            fração de zeros $\Pr(X_{it}=0)$ da distribuição condicional aos positivos $\mathbb{E}[X_{it} \mid X_{it} > 0]$ evita confundir inatividade
            local com baixa intensidade de conversão.<br>
            • <b>Assimetria Positiva Extrema ($\text{Skewness} \gg 0$) e Razão $P_{90}/P_{50}$:</b> A conversão bruta (especialmente para lavoura) e as multas
            ambientais possuem cauda direita longa: poucos municípios de fronteira ativa respondem por grande parte da área convertida, exigindo
            erros-padrão clusterizados por município e comparação entre <b>taxas proporcionais</b> (`taxa_conversao__*`) e <b>fluxos absolutos em ha</b> (`conversao_ha__*`).
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_econ_vars = [c for b in THEORETICAL_BLOCKS[:6] for c in blocks_map[b]]
        u_col1, u_col2, u_col3 = st.columns([2.0, 1.1, 1.1])
        with u_col1:
            uni_var = st.selectbox(
                "Selecione a Variável para Radiografia Univariada e Interpretação Econômica:",
                options=all_econ_vars,
                index=all_econ_vars.index("taxa_conversao__agricultura")
                if "taxa_conversao__agricultura" in all_econ_vars
                else 0,
                format_func=get_friendly_label,
                key="tab6_uni_var",
            )
        with u_col2:
            uni_scale_mode = st.selectbox(
                "Escala de Visualização nos Gráficos:",
                options=[
                    "Nível Original (Amostra Completa)",
                    "Apenas Positivos Estritos (X > 0 — Margem Intensiva)",
                    "Transformação ln(1 + X) (Para X >= 0)",
                ],
                key="tab6_scale_mode",
            )
        with u_col3:
            uni_trim99 = st.checkbox(
                "Cortar top 1% (> P99) apenas no histograma visual",
                value=False,
                key="tab6_trim99",
            )

        uni_profile_single = compute_univariate_deep_profile(df, [uni_var])
        if not uni_profile_single.empty:
            r_u = uni_profile_single.iloc[0]
            uk1, uk2, uk3, uk4, uk5, uk6 = st.columns(6)
            uk1.metric(
                "Margem Inativa (% Zeros)",
                f"{r_u['% Zeros (X=0)']:.1f}%",
                f"Positivos: {r_u['% Positivos (X>0)']:.1f}%",
            )
            uk2.metric(
                "Média Geral vs. (X > 0)",
                f"{r_u['Média Geral']:.4g}",
                f"Se X>0: {r_u['Média Positivos (X>0)']:.4g}" if pd.notna(r_u["Média Positivos (X>0)"]) else "N/A",
            )
            uk3.metric(
                "Mediana (P50) vs. P90",
                f"{r_u['Mediana (P50)']:.4g}",
                f"P90: {r_u['P90']:.4g}",
            )
            uk4.metric(
                "Assimetria (Skewness)",
                f"{r_u['Assimetria (Skew)']:.2f}" if pd.notna(r_u["Assimetria (Skew)"]) else "--",
                f"Curtose: {r_u['Curtose (Excesso)']:.1f}" if pd.notna(r_u["Curtose (Excesso)"]) else "--",
            )
            uk5.metric(
                "Coef. Variação (DP/|Média|)",
                f"{r_u['CV (DP/|Média|)']:.2f}" if pd.notna(r_u["CV (DP/|Média|)"]) else "--",
                f"IQR: {r_u['IQR (P75-P25)']:.4g}",
            )
            uk6.metric(
                "Gini Municipal (Espacial)",
                f"{r_u['Gini Municipal']:.3f}" if pd.notna(r_u["Gini Municipal"]) else "N/A",
                f"Top 20% Munis: {r_u['Top 20% Munis (%)']:.1f}%" if pd.notna(r_u["Top 20% Munis (%)"]) else "",
            )

        # Preparar série para o Histograma + Boxplot marginal e ECDF por Bioma
        u_plot_df = df[["codigo_ibge", "municipio_label", "ano", "bioma_dominante", uni_var]].copy()
        u_plot_df["val"] = pd.to_numeric(u_plot_df[uni_var], errors="coerce").astype("float64")
        u_plot_df = u_plot_df.dropna(subset=["val"])

        if uni_scale_mode.startswith("Apenas Positivos"):
            u_plot_df = u_plot_df.loc[u_plot_df["val"] > 0]
        elif uni_scale_mode.startswith("Transformação ln"):
            u_plot_df = u_plot_df.loc[u_plot_df["val"] >= 0].copy()
            u_plot_df["val"] = np.log1p(u_plot_df["val"])

        if uni_trim99 and len(u_plot_df) > 10:
            q99_u = float(u_plot_df["val"].quantile(0.99))
            u_plot_df = u_plot_df.loc[u_plot_df["val"] <= q99_u]

        ug1, ug2 = st.columns(2)
        with ug1:
            fig_uhist = px.histogram(
                u_plot_df,
                x="val",
                color="bioma_dominante",
                marginal="box",
                nbins=45,
                barmode="overlay",
                opacity=0.72,
                color_discrete_map=BIOME_COLORS,
                hover_data=["municipio_label", "ano"],
                title=f"Distribuição e Boxplot Marginal por Bioma: {uni_var}",
            )
            fig_uhist.update_layout(
                xaxis_title=f"{uni_var} ({uni_scale_mode})",
                yaxis_title="Frequência (Município-Ano)",
                height=430,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_uhist, width="stretch")

        with ug2:
            fig_ecdf = px.ecdf(
                u_plot_df,
                x="val",
                color="bioma_dominante",
                color_discrete_map=BIOME_COLORS,
                title=f"Função de Distribuição Acumulada Empírica (ECDF) por Bioma: {uni_var}",
            )
            fig_ecdf.update_layout(
                xaxis_title=f"{uni_var} ({uni_scale_mode})",
                yaxis_title="Probabilidade Acumulada F(x)",
                height=430,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_ecdf, width="stretch")

        st.markdown("#### 📋 Tabela Univariada Completa: Margens ($X=0$ vs. $X>0$), Assimetria, Quantis ($P_1$ a $P_{99}$) e Concentração")
        default_uni_table_cols = [
            "taxa_conversao__agricultura",
            "taxa_conversao__pastagem",
            "conversao_ha__agricultura",
            "conversao_ha__pastagem",
            "nativa_share",
            "agricultura_share",
            "pastagem_share",
            "lotacao_cabecas_ha",
            "efetivo_bovino",
            "preco_real_usd2024_media_anual__soja",
            "preco_real_usd2024_media_anual__milho",
            "preco_real_usd2024_media_anual__carne_bovina",
            "capacidade_valor__soja__pam_1991_2000_min7",
            "capacidade_valor__soja__gaez_yxHr0_soy",
            "capacidade_valor__milho__gaez_yxHr0_mze",
            "rendimento_medio_kg_ha__Soja (em grão)",
            "rendimento_medio_kg_ha__Milho (em grão)",
            "n_autos_desmatamento__ibama_informada",
            "n_autos_flora__ibama_informada",
            "multas_desmatamento_reais_observadas__ibama_informada",
            "precip_mm_anual",
            "precip_zscore_1981_2010",
            "elevation_mean_m",
        ]
        avail_uni_cols = [c for c in default_uni_table_cols if c in df.columns]
        selected_uni_cols = st.multiselect(
            "Variáveis exibidas na Tabela de Momentos e Quantis Univariados:",
            options=all_econ_vars,
            default=avail_uni_cols,
            key="tab6_uni_table_cols",
        )
        if selected_uni_cols:
            full_uni_df = compute_univariate_deep_profile(df, selected_uni_cols)
            st.dataframe(full_uni_df, width="stretch", height=380)

        st.markdown("---")
        st.subheader("2. Concentração Espacial Municipal: Curva de Lorenz, Índice de Gini e Lei de Pareto")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Achado Empírico Central para o Capítulo 1:</b> A conversão bruta de vegetação nativa para <b>agricultura</b> é
            espacialmente muito mais concentrada ($\text{Gini} \approx 0,75$; os <b>Top 20% dos municípios respondem por ~80,1% de toda a área convertida para lavoura</b>,
            liderados por <i>Ipiranga do Norte, Tabaporã, Sorriso, Feliz Natal e Porto dos Gaúchos</i>) do que a conversão para <b>pastagem</b>
            ($\text{Gini} \approx 0,53$; Top 20% = ~54,9%, liderados pela fronteira amazônica em <i>Colniza, Paranatinga, Aripuanã e Juara</i>).
            Já as <b>autuações e multas de desmatamento do IBAMA</b> também seguem forte concentração de Pareto (Top 20% = ~69,1% dos autos e ~75,3% do valor real das multas).
            </div>
            """,
            unsafe_allow_html=True,
        )

        lorenz_default = [
            c for c in [
                "conversao_ha__agricultura",
                "conversao_ha__pastagem",
                "n_autos_desmatamento__ibama_informada",
                "multas_desmatamento_reais_observadas__ibama_informada",
                "efetivo_bovino",
                "y_nativa_inicial_ha",
            ]
            if c in df.columns
        ]
        lor_c1, lor_c2 = st.columns([2.5, 1.0])
        with lor_c1:
            lorenz_cols = st.multiselect(
                "Variáveis para comparar na Curva de Lorenz Municipal:",
                options=all_econ_vars,
                default=lorenz_default,
                key="tab6_lorenz_cols",
            )
        with lor_c2:
            lorenz_agg = st.radio(
                "Agregação por Município:",
                options=["sum", "mean"],
                format_func=lambda m: "Soma Acumulada no Período" if m == "sum" else "Média Anual do Município",
                key="tab6_lorenz_agg",
            )

        if lorenz_cols:
            curves_df, gini_summary_df = compute_lorenz_curves(df, lorenz_cols, agg_mode=lorenz_agg)
            lc1, lc2 = st.columns([1.25, 1.15])
            with lc1:
                fig_lor = px.line(
                    curves_df,
                    x="% Acumulado de Municípios",
                    y="% Acumulado do Valor Estadual",
                    color="Variável",
                    title="Curva de Lorenz Municipal — Desigualdade Espacial em Mato Grosso",
                )
                fig_lor.add_trace(
                    go.Scatter(
                        x=[0, 100],
                        y=[0, 100],
                        mode="lines",
                        line=dict(color="#64748b", dash="dash", width=1.5),
                        name="Igualdade Perfeita (45°)",
                    )
                )
                fig_lor.update_layout(height=430, hovermode="x unified")
                st.plotly_chart(fig_lor, width="stretch")
            with lc2:
                st.markdown("#### Tabela de Desigualdade Espacial (Gini e Partições de Pareto)")
                st.dataframe(gini_summary_df, width="stretch", height=380)

        st.markdown("---")
        st.subheader("3. Ranking Municipal (Top 15 Municípios e Tabela Completa de Pareto dos 141 Municípios)")
        rk_c1, rk_c2, rk_c3 = st.columns([2.0, 1.0, 1.0])
        with rk_c1:
            rank_var = st.selectbox(
                "Variável para o Ranking Municipal:",
                options=all_econ_vars,
                index=all_econ_vars.index("conversao_ha__pastagem")
                if "conversao_ha__pastagem" in all_econ_vars
                else 0,
                format_func=get_friendly_label,
                key="tab6_rank_var",
            )
        with rk_c2:
            rank_mode = st.radio(
                "Critério de Ordenação:",
                options=["sum", "mean"],
                format_func=lambda m: "Soma no Período" if m == "sum" else "Média Anual",
                horizontal=True,
                key="tab6_rank_mode",
            )
        with rk_c3:
            top_k_munis = st.slider("Nº de Municípios no Gráfico:", min_value=10, max_value=35, value=15, step=5, key="tab6_topk")

        rank_df = compute_municipal_ranking(df, rank_var, rank_by=rank_mode)
        if not rank_df.empty:
            metric_col_rk = "Soma no Período" if rank_mode == "sum" else "Média Anual"
            rk_plot_col, rk_tbl_col = st.columns([1.2, 1.2])
            with rk_plot_col:
                top_slice = rank_df.head(top_k_munis).iloc[::-1]
                fig_rk = px.bar(
                    top_slice,
                    x=metric_col_rk,
                    y="municipio_label",
                    color="Bioma Dominante",
                    orientation="h",
                    color_discrete_map=BIOME_COLORS,
                    hover_data=["Posição", "% do Total Estadual", "% Acumulado (Pareto)", "Anos Válidos"],
                    title=f"Top {top_k_munis} Municípios em {rank_var} ({metric_col_rk})",
                )
                fig_rk.update_layout(
                    yaxis_title="Município (Código IBGE)",
                    xaxis_title=metric_col_rk,
                    height=470,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                )
                st.plotly_chart(fig_rk, width="stretch")
            with rk_tbl_col:
                st.markdown("#### Ranking Completo dos 141 Municípios")
                st.dataframe(rank_df.drop(columns=["municipio_label"]), width="stretch", height=430)

    # =======================================================================
    # ABA 7: Análise Multivariada & Mecanismos Econômicos da Tese (H1, H1-a, H1-b)
    # =======================================================================
    with tabs[6]:
        st.subheader("1. O Paradoxo Estoque vs. Fluxo em Mato Grosso (2001–2024): Conversão Bruta, Substituição Pasto-Lavoura e Intensificação")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Intuição Econômica Fundamental para a Tese (Diálogo com Angelsen, 2010; Bragança, 2018; Simões et al., 2020; VanWey et al., 2013):</b><br>
            Ao cruzar simultaneamente <b>fluxos de conversão bruta</b> (`conversao_ha__*`), <b>estoques de uso da terra</b> (`*_share`),
            <b>lotação bovina</b> (`lotacao_cabecas_ha`) e <b>preços relativos internacionais</b> (Soja/Carne e Milho/Carne), emerge o mecanismo estrutural central de Mato Grosso:<br>
            1. <b>Abertura Pioneira via Pastagem:</b> Entre 2001 e 2024, cerca de <b>91,6% de toda a área de vegetação nativa convertida diretamente</b> foi destinada a
               <b>pastagens</b> (~9,03 milhões de ha vs. ~825 mil ha convertidos diretamente para agricultura).<br>
            2. <b>Substituição de Pastagens por Lavouras (<i>Pasture-to-Cropland</i>):</b> Apesar de receber 9,03 milhões de ha de novas aberturas sobre vegetação nativa,
               a participação média das pastagens no território municipal ficou praticamente <b>estacionária</b> (~30,0% em 2001 $\rightarrow$ ~30,7% em 2024), enquanto a
               <b>área de agricultura mais que dobrou</b> (~6,4% $\rightarrow$ ~15,2% do território!). Isso demonstra que grande parte da expansão da soja/milho ocorreu
               absorvendo áreas de pastagem já convertidas.<br>
            3. <b>Intensificação Pecuária Endógena:</b> Para acomodar o crescimento do rebanho bovino enquanto cedia terras de maior aptidão para a lavoura, a pecuária
               mato-grossense elevou a <b>lotação média em +77%</b> (de ~1,08 cab/ha em 2001 para ~1,91 cab/ha em 2024).
            </div>
            """,
            unsafe_allow_html=True,
        )

        ann_trans_df, biome_trans_df = compute_structural_land_transition(df)

        mt_c1, mt_c2 = st.columns(2)
        with mt_c1:
            fig_stocks = make_subplots(specs=[[{"secondary_y": True}]])
            fig_stocks.add_trace(
                go.Scatter(
                    x=ann_trans_df["ano"],
                    y=ann_trans_df["Nativa Share Médio (%)"],
                    name="Estoque Vegetação Nativa (%)",
                    mode="lines+markers",
                    line=dict(color="#15803d", width=2.8),
                ),
                secondary_y=False,
            )
            fig_stocks.add_trace(
                go.Scatter(
                    x=ann_trans_df["ano"],
                    y=ann_trans_df["Pastagem Share Médio (%)"],
                    name="Estoque Pastagem (%)",
                    mode="lines+markers",
                    line=dict(color="#ca8a04", width=2.8),
                ),
                secondary_y=False,
            )
            fig_stocks.add_trace(
                go.Scatter(
                    x=ann_trans_df["ano"],
                    y=ann_trans_df["Agricultura Share Médio (%)"],
                    name="Estoque Agricultura (%)",
                    mode="lines+markers",
                    line=dict(color="#0284c7", width=2.8),
                ),
                secondary_y=False,
            )
            fig_stocks.add_trace(
                go.Scatter(
                    x=ann_trans_df["ano"],
                    y=ann_trans_df["Lotação Bovina Média (cab/ha)"],
                    name="Lotação Bovina (cab/ha — Eixo Dir.)",
                    mode="lines+markers",
                    line=dict(color="#dc2626", width=2.4, dash="dot"),
                ),
                secondary_y=True,
            )
            fig_stocks.update_layout(
                title="Transição de Estoques de Uso da Terra (%) vs. Intensificação Pecuária (cab/ha)",
                hovermode="x unified",
                height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            fig_stocks.update_yaxes(title_text="Participação Média Municipal (%)", secondary_y=False)
            fig_stocks.update_yaxes(title_text="Lotação Bovina (cabeças/ha)", secondary_y=True)
            st.plotly_chart(fig_stocks, width="stretch")

        with mt_c2:
            fig_rel = make_subplots(specs=[[{"secondary_y": True}]])
            fig_rel.add_trace(
                go.Bar(
                    x=ann_trans_df["ano"],
                    y=ann_trans_df["% Agricultura na Conversão Bruta Total"],
                    name="% Lavoura na Conversão Bruta Total (Eixo Esq.)",
                    marker_color="rgba(22, 163, 74, 0.45)",
                ),
                secondary_y=False,
            )
            fig_rel.add_trace(
                go.Scatter(
                    x=ann_trans_df["ano"],
                    y=ann_trans_df["Índice Relativo Soja/Carne (Ano Inicial=100)"],
                    name="Preço Relativo Soja/Carne (2001=100)",
                    mode="lines+markers",
                    line=dict(color="#1d4ed8", width=2.6),
                ),
                secondary_y=True,
            )
            fig_rel.add_trace(
                go.Scatter(
                    x=ann_trans_df["ano"],
                    y=ann_trans_df["Índice Relativo Milho/Carne (Ano Inicial=100)"],
                    name="Preço Relativo Milho/Carne (2001=100)",
                    mode="lines+markers",
                    line=dict(color="#9333ea", width=2.2, dash="dash"),
                ),
                secondary_y=True,
            )
            fig_rel.update_layout(
                title="Preços Relativos Crop-to-Beef (Soja/Carne) vs. Fração Agrícola na Conversão Bruta",
                hovermode="x unified",
                height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            fig_rel.update_yaxes(title_text="% Agricultura na Conversão Bruta Total", secondary_y=False)
            fig_rel.update_yaxes(title_text="Índice de Preço Relativo (Ano Inicial = 100)", secondary_y=True)
            st.plotly_chart(fig_rel, width="stretch")

        st.markdown("#### Balanço Estrutural Multivariado por Bioma (2001 vs. 2024): Estoques, Fluxos Brutos e Lotação Pecuária")
        st.dataframe(biome_trans_df, width="stretch")

        st.markdown("---")
        st.subheader("2. Análise Multivariada de Regimes para H1-a e H1-b: Por Que os Efeitos Fixos São Indispensáveis?")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Duas Pegadinhas Econométricas nos Dados Brutos que Justificam o Desenho de Efeitos Fixos da Tese:</b><br>
            1. <b>Confundimento Temporal e Espacial em H1-a (Pooled vs. Within FE):</b> Nos dados brutos sem efeitos fixos de ano, os anos de menor preço real da soja
               (2001–2005) coincidem com o pico histórico de abertura pré-PPCDAm/pré-Moratória da Soja; além disso, no modelo agroclimático GAEZ, a Amazônia úmida tem menor
               rendimento potencial de matéria seca ($\bar{z} = -0,51$) que o Cerrado ($\bar{z} = +0,55$) e o Pantanal ($\bar{z} = +1,31$ no clima GAEZ, mas $-0,80$ na PAM!).
               Quando removemos os efeitos fixos de município e ano (<b>Média Ajustada por FE / Within</b>), emerge o efeito previsto por <b>H1-a</b>: choques positivos de
               preço elevam a pressão de conversão nos municípios de maior capacidade produtiva!<br>
            2. <b>Viés de Simultaneidade / Seleção Espacial na Fiscalização (H1-b):</b> No corte transversal bruto, municípios com <b>Fiscalização Ativa do IBAMA</b> têm
               taxa média de conversão maior do que municípios sem autuação — porque o IBAMA direciona operações justamente para onde o desmatamento está ocorrendo
               (<i>Assunção et al., 2023</i>). A avaliação de <b>H1-b</b> requer comparar a inclinação intra-município da resposta ao choque econômico ($X_1 \times X_2$)
               condicionada à fiscalização defasada ($X_{3,t-1}$).
            </div>
            """,
            unsafe_allow_html=True,
        )

        rg_c1, rg_c2, rg_c3, rg_c4 = st.columns(4)
        with rg_c1:
            rg_y = st.selectbox(
                "Variável Dependente ($Y$):",
                options=[
                    "taxa_conversao__agricultura",
                    "taxa_conversao__pastagem",
                    "conversao_ha__agricultura",
                    "conversao_ha__pastagem",
                ],
                key="tab7_rg_y",
            )
        with rg_c2:
            cap_opts = [
                c for c in blocks_map["[X2] Capacidade Produtiva (PAM vs GAEZ)"]
                if c.startswith("capacidade_z__")
            ]
            rg_cap = st.selectbox(
                "Medida de Capacidade Produtiva ($X_2$):",
                options=cap_opts,
                index=cap_opts.index("capacidade_z__soja__gaez_yxHr0_soy")
                if "capacidade_z__soja__gaez_yxHr0_soy" in cap_opts
                else 0,
                key="tab7_rg_cap",
            )
        with rg_c3:
            p_opts = blocks_map["[X1] Preços e Choques"]
            def_p_rg = (
                "dln_preco_real_usd2024_media_anual_lag1__soja"
                if "dln_preco_real_usd2024_media_anual_lag1__soja" in p_opts
                else p_opts[0]
            )
            rg_price = st.selectbox(
                "Choque / Nível de Preço ($X_1$):",
                options=p_opts,
                index=p_opts.index(def_p_rg),
                key="tab7_rg_price",
            )
        with rg_c4:
            ib_opts = blocks_map["[X3] Ambiente Institucional (IBAMA)"]
            def_ib_rg = (
                "n_autos_desmatamento_lag1__ibama_informada"
                if "n_autos_desmatamento_lag1__ibama_informada" in ib_opts
                else ib_opts[0]
            )
            rg_ibama = st.selectbox(
                "Medida Institucional IBAMA ($X_3$):",
                options=ib_opts,
                index=ib_opts.index(def_ib_rg),
                key="tab7_rg_ibama",
            )

        h1a_regime_df, h1b_regime_df = compute_multivariate_regimes_h1(
            df, y_col=rg_y, cap_col=rg_cap, price_col=rg_price, ibama_col=rg_ibama
        )

        if not h1a_regime_df.empty:
            within_col_name = [c for c in h1a_regime_df.columns if c.startswith("Média Ajustada por FE")][0]
            pooled_col_name = [c for c in h1a_regime_df.columns if c.startswith("Média Bruta Pooled")][0]

            rc_plot1, rc_plot2 = st.columns(2)
            with rc_plot1:
                fig_h1a_reg = px.bar(
                    h1a_regime_df,
                    x="Tercil de Capacidade Produtiva (X2)",
                    y=within_col_name,
                    color="Regime de Preço / Choque (X1)",
                    barmode="group",
                    text_auto=".4f",
                    color_discrete_sequence=["#0284c7", "#eab308"],
                    title=f"Teste Visual H1-a (Ajustado por FE Município+Ano): {rg_y}",
                )
                fig_h1a_reg.update_layout(height=390, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
                st.plotly_chart(fig_h1a_reg, width="stretch")

            with rc_plot2:
                if not h1b_regime_df.empty:
                    fig_h1b_reg = px.bar(
                        h1b_regime_df,
                        x="Tercil de Capacidade (X2)",
                        y=within_col_name,
                        color="Regime de Preço (X1)",
                        facet_col="Regime Institucional IBAMA (X3)",
                        barmode="group",
                        color_discrete_sequence=["#0284c7", "#eab308"],
                        title=f"Condicionamento Institucional H1-b (Por Regime de Fiscalização IBAMA)",
                    )
                    fig_h1b_reg.update_layout(height=390, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
                    st.plotly_chart(fig_h1b_reg, width="stretch")

            with st.expander("📊 Ver Tabelas Multivariadas de Regimes (Comparação Pooled Bruto vs. Ajustado por Efeitos Fixos)", expanded=True):
                t_col_a, t_col_b = st.columns(2)
                with t_col_a:
                    st.markdown("**Tabela H1-a (Capacidade $X_2$ × Preço $X_1$)**")
                    st.dataframe(h1a_regime_df, width="stretch")
                with t_col_b:
                    st.markdown("**Tabela H1-b (Capacidade $X_2$ × Preço $X_1$ × IBAMA $X_3$)**")
                    st.dataframe(h1b_regime_df, width="stretch")

        st.markdown("---")
        st.subheader("3. Tipologia Espacial-Econômica dos 141 Municípios: Gráfico de Bolhas 4D e Biplot de PCA")
        st.markdown(
            r"""
            <div class="hypothesis-box">
            <b>Análise Multivariada do Perfil Municipal (141 Municípios):</b><br>
            • À esquerda, o <b>Gráfico de Bolhas 4D</b> cruza quatro dimensões simultaneamente (Eixo X, Eixo Y, Tamanho da Bolha e Bioma Dominante) para localizar
            cada município no espaço econômico-ambiental.<br>
            • À direita, o <b>Biplot de Componentes Principais (PCA)</b> sintetiza 11 indicadores estruturais da tese em dois eixos ortogonais ($PC_1$ e $PC_2$),
            mostrando como os vetores de conversão, aptidão GAEZ, estoque nativo, lotação pecuária, clima e autuações do IBAMA separam os municípios da
            <b>Fronteira Florestal Amazônica</b>, do <b>Polo Agrícola Consolidado do Cerrado/Transição</b> e do <b>Pantanal</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        muni_agg_cols = [
            "taxa_conversao__agricultura",
            "taxa_conversao__pastagem",
            "conversao_ha__agricultura",
            "conversao_ha__pastagem",
            "capacidade_z__soja__gaez_yxHr0_soy",
            "capacidade_z__milho__gaez_yxHr0_mze",
            "capacidade_valor__soja__pam_1991_2000_min7",
            "nativa_share",
            "agricultura_share",
            "pastagem_share",
            "lotacao_cabecas_ha",
            "efetivo_bovino",
            "n_autos_desmatamento__ibama_informada",
            "multas_desmatamento_reais_observadas__ibama_informada",
            "precip_mm_anual",
            "elevation_mean_m",
        ]
        avail_muni_cols = [c for c in muni_agg_cols if c in df.columns]
        muni_4d = (
            df.groupby(["codigo_ibge", "municipio_nome", "municipio_label", "bioma_dominante"], observed=True)[avail_muni_cols]
            .mean()
            .reset_index()
        )

        b4_c1, b4_c2, b4_c3 = st.columns(3)
        with b4_c1:
            bx_col = st.selectbox(
                "Eixo X (Bolhas 4D):",
                options=avail_muni_cols,
                index=avail_muni_cols.index("capacidade_z__soja__gaez_yxHr0_soy")
                if "capacidade_z__soja__gaez_yxHr0_soy" in avail_muni_cols
                else 0,
                format_func=get_friendly_label,
                key="tab7_bx",
            )
        with b4_c2:
            by_col = st.selectbox(
                "Eixo Y (Bolhas 4D):",
                options=avail_muni_cols,
                index=avail_muni_cols.index("agricultura_share")
                if "agricultura_share" in avail_muni_cols
                else 1,
                format_func=get_friendly_label,
                key="tab7_by",
            )
        with b4_c3:
            bsize_col = st.selectbox(
                "Tamanho da Bolha (4ª Dimensão):",
                options=[c for c in avail_muni_cols if not c.startswith("capacidade_z")],
                index=0,
                format_func=get_friendly_label,
                key="tab7_bsize",
            )

        pca_scores_df, pca_loadings_df, pca_var_exp = compute_municipal_pca_typology(df)

        mv_col1, mv_col2 = st.columns(2)
        with mv_col1:
            plot_4d = muni_4d.dropna(subset=[bx_col, by_col, bsize_col]).copy()
            plot_4d["_size_clean"] = plot_4d[bsize_col].clip(lower=0.0) + 1e-6
            fig_4d = px.scatter(
                plot_4d,
                x=bx_col,
                y=by_col,
                size="_size_clean",
                color="bioma_dominante",
                hover_name="municipio_label",
                hover_data=[bx_col, by_col, bsize_col],
                size_max=34,
                color_discrete_map=BIOME_COLORS,
                trendline="ols",
                title=f"Espaço Multivariado 4D dos Municípios: {by_col} vs. {bx_col}",
            )
            fig_4d.update_layout(
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_4d, width="stretch")

        with mv_col2:
            if not pca_scores_df.empty:
                fig_pca = px.scatter(
                    pca_scores_df,
                    x="PC1",
                    y="PC2",
                    color="bioma_dominante",
                    hover_name="municipio_label",
                    color_discrete_map=BIOME_COLORS,
                    title=(
                        f"Biplot PCA dos 141 Municípios "
                        f"(PC1: {pca_var_exp['PC1']:.1f}% | PC2: {pca_var_exp['PC2']:.1f}% da Variância)"
                    ),
                )
                # Adicionar vetores das cargas fatoriais (Loadings) reescalados para o Biplot
                scale_arrow = 3.2
                for _, lrow in pca_loadings_df.iterrows():
                    lx = float(lrow["Carga PC1"]) * scale_arrow
                    ly = float(lrow["Carga PC2"]) * scale_arrow
                    fig_pca.add_annotation(
                        x=lx,
                        y=ly,
                        ax=0,
                        ay=0,
                        xref="x",
                        yref="y",
                        axref="x",
                        ayref="y",
                        text=f"<b>{lrow['Indicador']}</b>",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=1.8,
                        arrowcolor="#334155",
                        font=dict(size=10, color="#0f172a"),
                    )
                fig_pca.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
                fig_pca.add_vline(x=0, line_dash="dot", line_color="#94a3b8")
                fig_pca.update_layout(
                    xaxis_title=f"Componente Principal 1 ({pca_var_exp['PC1']:.1f}%)",
                    yaxis_title=f"Componente Principal 2 ({pca_var_exp['PC2']:.1f}%)",
                    height=500,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                )
                st.plotly_chart(fig_pca, width="stretch")

        if not pca_loadings_df.empty:
            with st.expander("📐 Ver Cargas Fatoriais (Loadings) do PCA e Interpretação dos Componentes Principais"):
                st.dataframe(pca_loadings_df, width="stretch")


if __name__ == "__main__":
    main()

