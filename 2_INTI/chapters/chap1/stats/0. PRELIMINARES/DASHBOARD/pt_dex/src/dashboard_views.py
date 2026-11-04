"""The five analytical views of the chapter 1 exploratory dashboard."""
from __future__ import annotations

import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from .data_loader import apply_ibama_treatment, flag_mask, ibama_columns
from .econometric_lab import build_h1b_specification, horse_race, interaction_components
from .panel_metrics import calculate_vif, correlation_matrix, panel_descriptive, within_transform
from .presentation import (COLORS, INTERACTION_PREFIX, MODES, annual_conversion, binscatter_data,
                           booktabs, comparison_table, label, style_figure)

Y_COLUMNS = ["taxa_conversao__agricultura", "taxa_conversao__pastagem",
             "conversao_ha__agricultura", "conversao_ha__pastagem"]


def numeric_columns(df, columns):
    return [c for c in columns if c in df and pd.api.types.is_numeric_dtype(df[c])]


def download_table(frame, stem, caption, note=""):
    left, right = st.columns(2)
    left.download_button("Exportar CSV", frame.to_csv(index=True).encode("utf-8-sig"),
                         file_name=stem + ".csv", mime="text/csv", key=stem + "_csv")
    right.download_button("Exportar LaTeX (booktabs)", booktabs(frame, caption, note).encode("utf-8"),
                          file_name=stem + ".tex", mime="text/plain", key=stem + "_tex")


def diagnosis(df, raw, blocks, treatment_audit):
    st.subheader("Variação disponível e qualidade da amostra")
    st.caption("As estatísticas abaixo usam o recorte da barra lateral. Os diagnósticos da base integral são identificados separadamente.")
    chosen = st.multiselect("Blocos da tabela descritiva", list(blocks), default=list(blocks)[:1], key="diag_blocks")
    columns = numeric_columns(df, [c for b in chosen for c in blocks[b] if c not in ["codigo_ibge", "ano"]])
    if columns:
        desc = panel_descriptive(df, columns)
        desc["bloco"] = [next(b for b, cs in blocks.items() if c in cs) for c in desc.index]
        names = {"n_valid": "N válido", "missing_pct": "% Missing", "mean": "Média", "median": "Mediana",
                 "min": "Mín", "max": "Máx", "sd_overall": "DP Overall", "sd_between": "DP Between",
                 "sd_within": "DP Within", "time_invariant": "Invariante no tempo", "bloco": "Bloco"}
        view = desc.rename(columns=names)
        st.dataframe(view.style.format(precision=5).apply(
            lambda row: ["background-color: #e1f2ea" if bool(row["Invariante no tempo"]) else ""] * len(row), axis=1),
            width="stretch", height=420)
        st.caption("DP amostral (ddof=1). Between: DP das médias municipais, cada município com peso igual. "
                   "Within: DP de x_it − média_i + média geral. Verde: sem variação temporal observada; "
                   "isso não garante identificação em efeitos fixos. Os três DPs não formam uma soma aditiva de variâncias.")
        download_table(view, "descritiva_painel", "Estatística descritiva do painel municipal",
                       "Recorte ativo; desvio amostral ddof=1. Between usa médias municipais sem ponderação; within é x_it - média_i + média geral.")
        heat_variable = st.selectbox("Ausências no mapa", ["Média das variáveis selecionadas"] + columns, format_func=label, key="heat_variable")
        missing_cols = columns if heat_variable == "Média das variáveis selecionadas" else [heat_variable]
        heat = df[["codigo_ibge", "ano"]].copy()
        heat["Ausências (%)"] = 100 * df[missing_cols].isna().mean(axis=1)
        grid = heat.pivot(index="codigo_ibge", columns="ano", values="Ausências (%)")
        fig = go.Figure(go.Heatmap(z=grid.to_numpy(), x=grid.columns.astype(str), y=grid.index.astype(str),
                                 colorscale="YlOrRd", zmin=0, zmax=100, colorbar=dict(title="% NA"),
                                 hovertemplate="Município %{y}<br>Ano %{x}<br>Ausências %{z:.1f}%<extra></extra>"))
        fig.update_layout(xaxis_title="Ano", yaxis_title="Código IBGE", title="Ausências por município e ano")
        st.plotly_chart(style_figure(fig, 520), width="stretch", key="missing_heatmap")
        st.caption("Células vazias: pares removidos pelos filtros; células vermelhas: observações presentes com valores ausentes.")
    else:
        st.info("Selecione um bloco com variáveis numéricas para decompor a variação.")

    st.markdown("**PAM versus GAEZ: cobertura e perda de observações**")
    proxies = [c for c in raw if c.startswith("capacidade_z__")]
    coverage = pd.DataFrame([{"Proxy": c, "NA base integral": raw[c].isna().sum(), "NA no recorte": df[c].isna().sum(),
                              "N com Y agricultura": df[[c, Y_COLUMNS[0]]].dropna().shape[0],
                              "N com Y pastagem": df[[c, Y_COLUMNS[1]]].dropna().shape[0],
                              "Municípios válidos": df.loc[df[c].notna(), "codigo_ibge"].nunique()} for c in proxies]).set_index("Proxy")
    st.dataframe(coverage, width="stretch")
    st.markdown("**IBAMA: cenário de imputação pela flag**")
    _, scenario = apply_ibama_treatment(raw, impute_zeros=True)
    scenario = scenario.copy()
    scenario["NA no recorte ativo"] = [int(df[c].isna().sum()) for c in scenario["variavel"]]
    st.dataframe(scenario, width="stretch", hide_index=True)
    st.caption("O cenário usa a base integral antes dos filtros. Zero é atribuído somente a NaN com flag de ausência de registro identificada; "
               "NaN sem essa evidência continua ausente. Em lag1, usa-se o município e o ano exato t−1. "
               "O ano 2000 não está neste CSV: NaNs de lag1 em 2001 não são preenchidos por inferência.")
    with st.expander("Auditoria do tratamento efetivamente aplicado"):
        st.dataframe(treatment_audit, width="stretch", hide_index=True)
    with st.expander("Flags, cobertura e dicionário completo", expanded=False):
        flags = [c for c in df if pd.api.types.is_bool_dtype(df[c])]
        rows = [{"Flag": c, "True": int(flag_mask(df[c]).sum()), "False": int(flag_mask(df[c], False).sum()),
                 "Ausente": int(df[c].isna().sum())} for c in flags]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        source_columns = set(raw.attrs.get("source_columns", []))
        dictionary = pd.DataFrame([{"Variável": c, "Bloco": b, "Tipo": str(df[c].dtype),
                                    "Origem": "CSV" if c in source_columns else "Derivada em memória"}
                                   for b, cols in blocks.items() for c in cols])
        st.dataframe(dictionary, width="stretch", hide_index=True)
        st.download_button("Baixar dicionário dos blocos", dictionary.to_csv(index=False).encode("utf-8-sig"),
                           "dicionario_dashboard.csv", "text/csv", key="dictionary_download")


def temporal(df, prices, institutions):
    st.subheader("Conversão, incentivos e heterogeneidade territorial")
    c1, c2, c3 = st.columns(3)
    destinations = c1.multiselect("Destino da conversão", ["agricultura", "pastagem"], ["agricultura", "pastagem"], key="time_destinations")
    metric = c2.selectbox("Medida de conversão", ["Taxa (%)", "Área convertida (ha)"], key="time_metric")
    aggregation = c3.selectbox("Agregação da taxa", ["Ponderada pelo estoque nativo inicial", "Média municipal simples"],
                              disabled=metric != "Taxa (%)", key="time_aggregation")
    secondary = st.selectbox("Série do eixo direito: preço, choque ou IBAMA", prices + institutions,
                             index=next((i for i, c in enumerate(prices) if c == "dln_preco_real_usd2024_media_anual_lag1__soja"), 0),
                             format_func=label, key="time_secondary")
    if not destinations:
        st.info("Selecione ao menos um destino para visualizar as séries.")
        return
    values = annual_conversion(df, destinations, metric, aggregation.startswith("Ponderada"))
    for biome in df["bioma_dominante"].dropna().unique():
        panel = values.loc[values["bioma"] == str(biome)]
        group = df.loc[df["bioma_dominante"] == biome]
        right = group.groupby("ano")[secondary].agg(["mean", "count"])
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for i, dest in enumerate(destinations):
            series = panel.loc[panel["destino"] == dest]
            fig.add_trace(go.Scatter(x=series["ano"], y=series["valor"], name=dest.capitalize(), mode="lines+markers",
                                     line=dict(color=["#128275", "#d89430"][i % 2]), customdata=series[["N municípios válidos"]],
                                     hovertemplate="%{x}: %{y:.5g}<br>N municípios = %{customdata[0]}<extra>%{fullData.name}</extra>"), secondary_y=False)
        fig.add_trace(go.Scatter(x=right.index, y=right["mean"], name=label(secondary), mode="lines",
                                 line=dict(color="#666b83", dash="dot"), customdata=right[["count"]],
                                 hovertemplate="%{x}: %{y:.5g}<br>N municípios = %{customdata[0]}<extra>%{fullData.name}</extra>"), secondary_y=True)
        fig.update_layout(title=f"{biome} · {group['codigo_ibge'].nunique()} municípios")
        fig.update_yaxes(title_text=metric, secondary_y=False)
        fig.update_yaxes(title_text="Média da série selecionada", secondary_y=True)
        st.plotly_chart(style_figure(fig), width="stretch", key="time_" + str(biome))
    st.caption("Taxa ponderada = soma das conversões / soma do estoque nativo inicial, somente para pares com Y válido. "
               "Área: soma dos municípios observados, sem extrapolação. Eixo direito: média dos valores disponíveis; "
               "preços comuns não são somados entre municípios. Curvas podem ter coberturas diferentes. "
               "Preços de soja/milho: USD/t; carne bovina: USD/kg; multas reais: R$ de dezembro de 2024; Δln é adimensional.")
    with st.expander("Suporte amostral das curvas"):
        st.dataframe(values, width="stretch", hide_index=True)
    shape = st.radio("Distribuição por bioma", ["Violino", "Boxplot"], horizontal=True, key="distribution")
    display = df.melt(id_vars=["bioma_dominante"], value_vars=["taxa_conversao__" + d for d in destinations], var_name="Destino", value_name="Taxa (%)")
    display["Taxa (%)"] *= 100
    display["Destino"] = display["Destino"].str.replace("taxa_conversao__", "", regex=False)
    fn = px.violin if shape == "Violino" else px.box
    kwargs = {"box": True, "points": False} if shape == "Violino" else {"points": "outliers"}
    fig = fn(display.dropna(), x="bioma_dominante", y="Taxa (%)", color="bioma_dominante", facet_col="Destino",
             color_discrete_map=COLORS, labels={"bioma_dominante": "Bioma dominante"}, **kwargs)
    st.plotly_chart(style_figure(fig), width="stretch", key="biome_distribution")


def proxies(df, blocks, institutions):
    st.subheader("Batalha de proxies e colinearidade")
    pool = [c for c in df if c.startswith(("capacidade_", "rendimento_", "precip_", "media_", "desvio_"))] + institutions
    defaults = [c for c in pool if c.startswith("capacidade_z__soja__")]
    chosen = st.multiselect("Proxies a comparar", pool, defaults, format_func=label, max_selections=24, key="proxy_columns")
    a, b, c = st.columns(3)
    method = a.selectbox("Correlação", ["Pearson", "Spearman"], key="corr_method")
    representation = b.selectbox("Variação analisada", ["Nível (Pooled)", "Média por município", "Within Município", "Double Demeaned (Município + Ano)"], key="corr_mode")
    common = c.checkbox("Amostra comum na correlação", True, key="corr_common")
    if len(chosen) < 2:
        st.info("Selecione pelo menos duas proxies.")
        return
    data = df.copy()
    if representation == "Média por município":
        data = df.groupby("codigo_ibge")[chosen].mean().reset_index()
    elif representation in MODES and MODES[representation] != "pooled":
        data = within_transform(df, chosen, mode=MODES[representation], complete_cases=True)
        common = True
        st.caption("Transformações within usam a mesma amostra completa de todas as proxies selecionadas.")
    corr = correlation_matrix(data, chosen, method=method.lower(), complete_cases=common)
    # Pairwise sample counts are shown below; DataFrames inside attrs are not
    # JSON-serializable metadata for Arrow/Plotly, so remove them from this view.
    corr.attrs = {}
    readable = corr.rename(index=label, columns=label)
    fig = px.imshow(readable, zmin=-1, zmax=1, color_continuous_scale="RdBu_r", aspect="auto", text_auto=".2f")
    fig.update_layout(coloraxis_colorbar_title="Correlação")
    st.plotly_chart(style_figure(fig, min(800, 330 + 18 * len(chosen))), width="stretch", key="correlations")
    valid = data[chosen].replace([np.inf, -np.inf], np.nan).notna().astype(int)
    st.caption(f"N de casos completos para VIF: {int(valid.all(axis=1).sum()):,}. "
               "VIF usa intercepto e a amostra comum; constantes e colinearidade perfeita são sinalizadas. "
               "Proxies fixas repetidas por ano não criam informação temporal; use médias municipais para compará-las entre municípios.")
    st.dataframe(calculate_vif(data, chosen), width="stretch", hide_index=True)
    with st.expander("N de pares válidos e matriz numérica"):
        counts = valid.T @ valid if not common else pd.DataFrame(int(valid.all(axis=1).sum()), index=chosen, columns=chosen)
        st.dataframe(counts, width="stretch")
        st.dataframe(corr, width="stretch")
        st.download_button("Baixar correlações", corr.to_csv().encode("utf-8-sig"), "correlacoes.csv", "text/csv", key="corr_download")
    st.caption("GAEZ sx é índice de aptidão; yx é rendimento potencial sob cenário. PAM 1991–2000 mede rendimento histórico observado. "
               "As climatologias 1981–2010 e 1991–2020 incorporam anos posteriores ao início do painel. "
               "As duas localizações do IBAMA são alternativas de atribuição dos registros e não devem ser somadas.")


def binscatter(df, analytical):
    st.subheader("Relações no nível e dentro dos municípios")
    a, b = st.columns(2)
    y = a.selectbox("Y do binscatter", Y_COLUMNS, format_func=label, key="bins_y")
    default_x = next((c for c in analytical if c.startswith(INTERACTION_PREFIX) and "soja__gaez_sxHr0" in c), analytical[0])
    x = b.selectbox("X do binscatter", analytical, index=analytical.index(default_x), format_func=label, key="bins_x")
    a, b, c = st.columns(3)
    mode = a.selectbox("Transformação do gráfico", list(MODES), index=1, key="bins_mode")
    bins = b.slider("Número de quantis Q", 5, 50, 20, key="bins_count")
    stratify = c.checkbox("Separar por bioma", True, key="bins_stratify")
    with st.expander("Sensibilidade a extremos e alavancagem"):
        trim = st.slider("Ocultar maiores desvios absolutos de X ou Y (%)", 0.0, 10.0, 0.0, 0.5, key="bins_trim")
        leverage = st.checkbox("Ocultar alavancagem h > 4/N (OLS com intercepto e X)", False, key="bins_leverage")
        st.caption("Exclusão aplicada apenas a este gráfico. Os efeitos fixos são recalculados na amostra retida. "
                   "O corte percentual vale separadamente para X e Y, logo a perda conjunta pode ser maior.")
    points, lines, summary, removed = binscatter_data(df, y, x, MODES[mode], bins, stratify, trim, leverage)
    if points.empty:
        st.info("Não há variação ou observações suficientes para formar bins nessa seleção.")
    else:
        fig = px.scatter(points, x="x", y="y", color="Grupo", size="N no bin", size_max=18,
                         color_discrete_map=COLORS, hover_data=["N no bin"], labels={"x": label(x), "y": label(y)})
        for group, chunk in lines.groupby("Grupo"):
            fig.add_trace(go.Scatter(x=chunk["x"], y=chunk["y"], mode="lines", name="OLS · " + group,
                                     line=dict(color=COLORS.get(group, "#555")), showlegend=True))
        st.plotly_chart(style_figure(fig, 510), width="stretch", key="binscatter_chart")
        st.download_button("Baixar médias dos bins", points.to_csv(index=False).encode("utf-8-sig"), "binscatter.csv", "text/csv", key="bins_download")
    st.dataframe(summary, width="stretch", hide_index=True)
    st.caption(f"{removed} observações excluídas pelos filtros de extremos. Bins por quantis distintos, calculados dentro de cada grupo. "
               "A reta OLS é ajustada nas observações individuais, sem ponderar igualmente bins de tamanhos diferentes. "
               "Double Demeaned remove município e ano por projeções convergidas na amostra conjunta; "
               "os grupos são exibidos após essa transformação. Taxas permanecem em proporção 0–1. "
               "Inferência clusterizada está disponível no laboratório.")


def laboratory(df, institutions, context):
    st.subheader("Pré-seleção econométrica · H1, H1-a e H1-b")
    st.write("Compare alternativas de preço × capacidade, acrescente instituições e examine o condicionamento da resposta. "
             "Todas as regressões incluem efeitos fixos de município e ano, com erros-padrão clusterizados por município.")
    interaction_options = [c for c in df if c.startswith(INTERACTION_PREFIX)]
    defaults = [c for c in interaction_options if "soja__gaez_sxHr0" in c or "soja__pam_" in c]
    inst_default = next((c for c in institutions if "n_autos_flora_lag1__ibama_informada" in c), institutions[0])
    climates = [c for c in df if c.startswith("precip_")]
    with st.form("econometric_form"):
        y = st.selectbox("Variável dependente Y", Y_COLUMNS, format_func=label, key="lab_y")
        interactions = st.multiselect("Interações Preço × Capacidade", interaction_options, defaults, format_func=label, key="lab_interactions", max_selections=10)
        inst = st.multiselect("Variáveis institucionais X3", institutions, [inst_default], format_func=label, key="lab_ibama", max_selections=4)
        controls = st.multiselect("Controles climáticos", climates, ["precip_zscore_1981_2000"], format_func=label, key="lab_controls", max_selections=8)
        a, b = st.columns(2)
        strategy = a.selectbox("Comparação de proxies", ["Uma proxy por especificação", "Combinar proxies selecionadas"], key="lab_strategy")
        common = b.checkbox("Mesma amostra em todos os modelos", True, key="lab_common")
        triple = st.checkbox("Incluir interação tripla Preço × Capacidade × IBAMA (H1-b)", True, key="lab_triple")
        run = st.form_submit_button("Executar comparação", key="lab_run", type="primary")
    settings = (context, y, tuple(interactions), tuple(inst), tuple(controls), strategy, common, triple)
    st.caption("H1-a: preço × capacidade. H1-b: a interação tripla inclui também os termos de ordem inferior "
               "IBAMA, preço × IBAMA e capacidade × IBAMA; preço comum e capacidade fixa são absorvidos pelos efeitos fixos. "
               "Cada medida do IBAMA gera uma alternativa; as versões informada/espacial não são somadas.")
    if run:
        if not interactions:
            st.warning("Selecione pelo menos uma interação Preço × Capacidade.")
            st.session_state.pop("lab_result", None)
        else:
            work = df.copy()
            specifications, definitions = {}, []
            sets = [[c] for c in interactions] if strategy.startswith("Uma") else [interactions]
            counter = 1
            for exposure_set in sets:
                base = list(controls)
                for exposure in exposure_set:
                    components = interaction_components(exposure)
                    # The helper returns the price and capacity identifiers; their main
                    # effects are included explicitly and transparently absorbed.
                    if isinstance(components, dict):
                        price, capacity = components["price"], components["capacity"]
                    else:
                        price, capacity = components
                    base.extend([price, capacity, exposure])
                model = f"M{counter:02d} · H1-a"
                specifications[model] = list(dict.fromkeys(base))
                definitions.append({"Modelo": model, "Exposições": " | ".join(exposure_set), "Instituição": "—", "Tripla": False})
                counter += 1
                for institutional in inst:
                    regs = list(base) + [institutional]
                    if triple:
                        for exposure in exposure_set:
                            work, extra, _ = build_h1b_specification(work, exposure, institutional, controls=controls)
                            regs.extend(extra)
                    model = f"M{counter:02d} · {'H1-b' if triple else 'H1 + X3'}"
                    specifications[model] = list(dict.fromkeys(regs))
                    definitions.append({"Modelo": model, "Exposições": " | ".join(exposure_set), "Instituição": institutional, "Tripla": triple})
                    counter += 1
            with st.spinner("Estimando efeitos fixos e covariâncias clusterizadas…"):
                coefficients, diagnostics = horse_race(work, y, specifications, common_sample=common)
            st.session_state["lab_result"] = {"settings": settings, "coefficients": coefficients,
                                               "diagnostics": diagnostics, "definitions": pd.DataFrame(definitions)}
    saved = st.session_state.get("lab_result")
    if not saved:
        st.info("Escolha as candidatas e execute a comparação. Os resultados são exploratórios; seleção por significância não valida uma especificação.")
        return
    if saved["settings"] != settings:
        st.info("Os filtros ou a especificação mudaram. Execute novamente para atualizar os resultados.")
        return
    coefs, diagnostics = saved["coefficients"], saved["diagnostics"]
    table = comparison_table(coefs, diagnostics)
    st.dataframe(table, width="stretch", height=450)
    st.caption("Células: coeficiente (erro-padrão clusterizado). R² Within município segue a definição do PanelOLS; "
               "R² Within município + ano usa a projeção nos dois efeitos. Valores negativos do primeiro são possíveis. "
               "Absorvidas e colineares não recebem coeficientes ou inferência artificiais.")
    download_table(table, "horse_race_twfe", "Comparação exploratória de efeitos fixos",
                   f"Y={y}; EF município e ano; EP cluster município; IC 95%; amostra {'comum' if common else 'própria por modelo'}. Filtros: {context}.")
    estimated = coefs.loc[coefs["status"] == "estimated"].copy() if not coefs.empty else pd.DataFrame()
    if not estimated.empty:
        focus = st.checkbox("Forest plot: apenas preço × capacidade e interações triplas", True, key="forest_focus")
        if focus:
            estimated = estimated.loc[estimated["term"].str.contains("interacao_|tripla|triple", regex=True)]
        if not estimated.empty:
            estimated["Rótulo"] = estimated["term"].map(lambda term: "<br>".join(textwrap.wrap(label(term), width=68)))
            estimated["erro_mais"] = estimated["ci_upper"] - estimated["coefficient"]
            estimated["erro_menos"] = estimated["coefficient"] - estimated["ci_lower"]
            fig = px.scatter(estimated, x="coefficient", y="Rótulo", color="model", error_x="erro_mais", error_x_minus="erro_menos",
                             hover_data=["term", "std_error", "t_stat", "p_value", "nobs", "n_entities"],
                             labels={"coefficient": "Coeficiente e IC 95% clusterizado", "model": "Modelo"})
            fig.add_vline(x=0, line_dash="dash", line_color="#8b8b8b")
            st.plotly_chart(style_figure(fig, max(380, min(1000, 100 + 65 * estimated["term"].nunique()))), width="stretch", key="forest_plot")
    with st.expander("Coeficientes, IC 95%, diagnósticos e composição dos modelos", expanded=True):
        st.dataframe(saved["definitions"], width="stretch", hide_index=True)
        st.dataframe(diagnostics, width="stretch", hide_index=True)
        st.dataframe(coefs, width="stretch", hide_index=True)
        st.download_button("Baixar coeficientes e inferência", coefs.to_csv(index=False).encode("utf-8-sig"), "coeficientes_twfe.csv", "text/csv", key="coef_download")
        st.download_button("Baixar diagnósticos", diagnostics.to_csv(index=False).encode("utf-8-sig"), "diagnosticos_twfe.csv", "text/csv", key="diag_download")
    st.info("Interpretação: associações condicionais. Autuações podem responder à conversão e defasagens não garantem exogeneidade. "
            "Com poucos municípios (especialmente no Pantanal), a inferência clusterizada é frágil. "
            "A validade temporal do GAEZ e a seleção da PAM permanecem questões científicas a avaliar.")
