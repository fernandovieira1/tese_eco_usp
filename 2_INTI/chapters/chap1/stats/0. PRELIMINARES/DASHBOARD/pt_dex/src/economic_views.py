"""Economic interpretation of observed distributions and panel associations."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .dashboard_views import download_table
from .economic_metrics import economic_portrait, grouped_hypothesis, multivariate_partial, univariate_summary
from .econometric_lab import fit_twfe
from .presentation import COLORS, INTERACTION_PREFIX, MODES, label, style_figure

DESTINATION_COLORS = {"agricultura": "#128275", "pastagem": "#d89430", "total": "#496bb4"}
RATE_COLUMNS = ["taxa_conversao__agricultura", "taxa_conversao__pastagem"]


def fmt(value, digits=2):
    if value is None or pd.isna(value) or not np.isfinite(float(value)):
        return "indisponível"
    return f"{value:,.{digits}f}".replace(",", "@COMMA@").replace(".", ",").replace("@COMMA@", ".")


def show_table(frame, stem, caption, note=""):
    st.dataframe(frame, width="stretch", hide_index=True)
    download_table(frame, stem, caption, note)


def variable_unit(variable):
    if variable.startswith("log1p__"):
        return "log(1+x) na unidade original de " + variable_unit(variable.removeprefix("log1p__"))
    if variable.startswith(("capacidade_z__", "precip_zscore_")):
        return "desvios-padrão (z)"
    if variable.startswith("dln_preco"):
        return "variação logarítmica (Δln)"
    if variable.startswith("ln_preco"):
        return "log do preço na unidade original"
    if variable.startswith("preco_"):
        currency = "USD de 2024" if "real_usd2024" in variable else "USD nominais"
        return currency + ("/kg" if "carne_bovina" in variable else "/t")
    if variable.startswith("taxa_conversao__"):
        return "% do estoque nativo inicial"
    if variable.startswith("capacidade_valor__"):
        if "gaez_sx" in variable:
            return "índice de aptidão GAEZ (0–10.000)"
        return "kg de matéria seca/ha" if "gaez_yx" in variable else "kg/ha"
    if variable.startswith("rendimento_"):
        return "kg/ha"
    if variable.startswith("multas_"):
        return "R$ de dezembro de 2024" if "reais" in variable else "R$ nominais"
    if variable.startswith("n_autos_"):
        return "autos registrados"
    if variable.startswith(("precip_", "media_", "desvio_")):
        return "mm"
    if variable.startswith("elevation_"):
        return "metros"
    if variable.startswith("efetivo_bovino"):
        return "cabeças"
    if variable == "lotacao_cabecas_ha":
        return "cabeças/ha de pastagem"
    if "share" in variable:
        return "fração da área de referência"
    if "ha" in variable and not variable.startswith((INTERACTION_PREFIX, "exposicao_")):
        return "hectares"
    if variable.startswith((INTERACTION_PREFIX, "exposicao_")):
        return "exposição: ln preço × capacidade z (× fração de bioma, quando indicada)"
    return "unidade original indicada no nome da variável"


def variable_meaning(variable):
    """Scientific meaning follows the chapter's documented variable definitions."""
    if variable.startswith("taxa_conversao"):
        return ("Taxa de abertura de áreas nativas para o destino escolhido, em proporção do estoque nativo inicial. "
                "A distribuição permite distinguir uma pressão disseminada de episódios intensos em poucos pares município–ano.")
    if variable.startswith("conversao_ha"):
        return "Fluxo bruto em hectares: mede a escala territorial da conversão. Uma grande área convertida pode coexistir com uma taxa relativamente baixa em municípios extensos."
    if variable.startswith(("capacidade_", "rendimento_")):
        return ("Capacidade predeterminada e rendimento observado têm interpretações distintas. PAM histórica reflete a produção nas áreas colhidas; "
                "GAEZ sx mede aptidão e yx rendimento potencial sob um cenário. Sua distribuição ajuda a localizar o suporte para H1-a.")
    if variable.startswith(("preco_", "ln_preco", "dln_preco")):
        return ("Preços são comuns aos municípios em cada ano. Sua variação temporal encontra capacidades locais diferentes. "
                "Δln é variação logarítmica, não uma surpresa exógena por definição; nível e crescimento do preço respondem a perguntas diferentes.")
    if "ibama_" in variable:
        return ("Contagens e valores autuados descrevem registros administrativos, não multas pagas ou efetividade diretamente. "
                "Concentração pode refletir pressão de conversão, direcionamento da fiscalização e cobertura dos registros.")
    if variable.startswith(("nativa_", "agricultura_", "pastagem_", "native_veg_", "efetivo_", "lotacao_")):
        return ("Estoques e intensidade produtiva caracterizam a estrutura de uso da terra. Variações líquidas desses estoques não recuperam "
                "as conversões brutas entre usos. Lotação do rebanho também não equivale à produtividade potencial da terra.")
    if variable.startswith("precip_"):
        return "Chuva e anomalias caracterizam condições produtivas e variação climática. Comparar referências climáticas ajuda a distinguir o nível local de um desvio em relação ao seu histórico."
    if variable.startswith((INTERACTION_PREFIX, "exposicao_")):
        return "A exposição combina preço e capacidade local. Valores negativos de uma interação com capacidade padronizada podem decorrer de capacidade abaixo da média; não significam retorno econômico líquido negativo."
    return "A escala, a unidade de observação e a heterogeneidade territorial devem orientar a interpretação econômica desta distribuição."


def economic_overview(df, reference):
    st.subheader("Que transformação do território os dados revelam?")
    st.write("Compare a escala da conversão, a pressão sobre a vegetação disponível e a composição dos destinos. "
             "As perguntas abaixo conectam os padrões observados às hipóteses da tese.")
    balanced = st.checkbox("Usar os mesmos municípios em todos os anos do recorte", True, key="econ_balanced")
    portrait = economic_portrait(df, reference=reference, balanced=balanced)
    sample = portrait["sample"]
    if sample.empty:
        st.info("Não há municípios com suporte comum para esse recorte. Desative a coorte constante ou amplie a seleção.")
        return
    years = sorted(reference.ano.unique())
    destinations = portrait["destinations"]
    st.caption(f"Base comparável dos dois destinos: {len(sample):,} pares, {sample.codigo_ibge.nunique()} municípios; "
               f"janela {min(years)}–{max(years)}. {'Coorte com Y válido em todos os anos.' if balanced else 'Suporte disponível; composição municipal pode mudar entre anos.'}")
    indexed = destinations.set_index("destination")
    total = float(destinations.conversion_ha.sum())
    pasture_share = indexed.loc["pastagem", "share_two_destinations"]
    columns = st.columns(4)
    columns[0].metric("Fluxo bruto somado · agricultura", f"{fmt(indexed.loc['agricultura', 'conversion_ha'] / 1e6, 3)} Mha")
    columns[1].metric("Fluxo bruto somado · pastagem", f"{fmt(indexed.loc['pastagem', 'conversion_ha'] / 1e6, 3)} Mha")
    columns[2].metric("Pastagem entre os dois destinos", f"{fmt(100 * pasture_share, 1)}%")
    columns[3].metric("Taxa ponderada · dois destinos", f"{fmt(100 * destinations.weighted_rate.sum(), 3)}%")
    if total > 0:
        leading = destinations.loc[destinations.conversion_ha.idxmax()]
        st.info(f"**O que aparece no recorte:** {leading.destination} responde por {fmt(100 * leading.share_two_destinations, 1)}% "
                "do fluxo bruto observado para esses dois destinos. **Pergunta econômica:** os incentivos associados aos diferentes usos "
                "geram pressão direta sobre a vegetação ou também reorganizam áreas já convertidas? Separar agricultura e pastagem é decisivo para essa leitura.")
    else:
        st.info("Não há fluxo positivo observado neste suporte. Esse resultado não permite identificar uma decisão ativa de conservação.")
    st.caption("Mha = milhões de hectares. A soma dos fluxos no período não é uma contagem de hectares únicos: pode incluir reconversões. "
               "A taxa ponderada divide a soma dos fluxos pela soma dos estoques iniciais dos mesmos pares; não é a perda acumulada do estoque no período.")
    rates = portrait["annual"].copy()
    rates["Taxa (%)"] = 100 * rates.weighted_rate
    rates["Fluxo (mil ha)"] = rates.conversion_ha / 1e3
    left, right = st.columns(2)
    fig = px.line(rates, x="ano", y="Fluxo (mil ha)", color="destination", markers=True,
                  color_discrete_map=DESTINATION_COLORS, hover_data=["n_entities", "nobs"], labels={"destination": "Destino", "ano": "Ano"},
                  title="Escala territorial da abertura de áreas")
    left.plotly_chart(style_figure(fig), width="stretch", key="econ_annual_area")
    fig = px.line(rates, x="ano", y="Taxa (%)", color="destination", markers=True,
                  color_discrete_map=DESTINATION_COLORS, hover_data=["n_entities", "denominator_ha_year"], labels={"destination": "Destino", "ano": "Ano"},
                  title="Pressão relativa ao estoque nativo inicial")
    right.plotly_chart(style_figure(fig), width="stretch", key="econ_annual_rate")
    st.caption("Se área e taxa seguem caminhos diferentes, examine o tamanho e a composição dos estoques disponíveis. "
               "Uma queda de hectares convertidos não implica necessariamente queda proporcional da pressão sobre a vegetação remanescente.")

    by_biome = portrait["by_biome"].copy()
    by_biome["Taxa ponderada (%)"] = 100 * by_biome.weighted_rate
    by_biome["Participação no fluxo (%)"] = 100 * by_biome.share_two_destinations
    left, right = st.columns(2)
    fig = px.bar(by_biome, x="bioma_dominante", y="Taxa ponderada (%)", color="destination", barmode="group",
                 color_discrete_map=DESTINATION_COLORS, hover_data=["n_entities", "nobs"],
                 labels={"bioma_dominante": "Bioma dominante", "destination": "Destino"}, title="Onde a pressão relativa é maior?")
    left.plotly_chart(style_figure(fig, 380), width="stretch", key="econ_biome_rate")
    fig = px.bar(by_biome, x="bioma_dominante", y="Participação no fluxo (%)", color="destination",
                 color_discrete_map=DESTINATION_COLORS, hover_data=["conversion_ha", "n_entities"],
                 labels={"bioma_dominante": "Bioma dominante", "destination": "Destino"}, title="Qual destino predomina em cada território?")
    right.plotly_chart(style_figure(fig, 380), width="stretch", key="econ_biome_destination")
    support = sample.groupby("bioma_dominante", observed=True).codigo_ibge.nunique()
    st.caption("Suporte municipal por bioma dominante: " + "; ".join(f"{b}: {n}" for b, n in support.items()) + ". "
               "Valores de poucos municípios descrevem esse grupo e não autorizam generalização para todo o bioma.")

    st.markdown("**A conversão está disseminada ou concentrada em poucos municípios?**")
    focus = st.selectbox("Destino para a concentração territorial", ["agricultura", "pastagem", "total"], key="econ_concentration_destination")
    ranked = portrait["concentration"].query("destination == @focus").copy()
    concentration = portrait["concentration_summary"].query("destination == @focus")
    if not concentration.empty and pd.notna(concentration.iloc[0].top10_share):
        row = concentration.iloc[0]
        st.write(f"Os **{int(row.top_n)} municípios de maior fluxo** (aproximadamente 10% dos {int(row.n_entities)} observados) "
                 f"concentram **{fmt(100 * row.top10_share, 1)}%** da conversão para {focus}. "
                 "Isso ajuda a avaliar se resultados médios podem ser dominados por poucos territórios.")
    if not ranked.empty:
        ranked["Municípios acumulados (%)"] = 100 * ranked.rank_fraction
        ranked["Conversão acumulada (%)"] = 100 * ranked.cumulative_share
        fig = px.line(ranked, x="Municípios acumulados (%)", y="Conversão acumulada (%)", markers=True,
                      hover_data=["codigo_ibge", "conversion_ha", "observed_years"], title="Municípios ordenados do maior para o menor fluxo")
        fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode="lines", line=dict(dash="dot", color="#aaa"), name="Distribuição uniforme"))
        left, right = st.columns(2)
        left.plotly_chart(style_figure(fig, 370), width="stretch", key="econ_concentration")
        top = ranked.head(12).sort_values("conversion_ha")
        fig = px.bar(top, x="conversion_ha", y=top.codigo_ibge.astype(str), color="bioma_dominante", orientation="h",
                     color_discrete_map=COLORS, hover_data=["observed_years"], labels={"conversion_ha": "Fluxo somado (ha)", "y": "Código IBGE", "bioma_dominante": "Bioma"})
        right.plotly_chart(style_figure(fig, 370), width="stretch", key="econ_ranking")
        with st.expander("Ranking e cobertura de cada município"):
            show_table(ranked, "economia_concentracao", "Concentração municipal da conversão", "Fluxos observados; anos válidos por município informados.")

    stocks = portrait.get("stocks_annual", portrait["stocks"])
    st.markdown("**O que os estoques revelam sobre a estrutura produtiva?**")
    if not stocks.empty:
        stock_view = stocks.copy()
        stock_view["Área (Mha)"] = stock_view.area_ha / 1e6
        fig = px.line(stock_view, x="ano", y="Área (Mha)", color="use", markers=True,
                      color_discrete_map={"nativa": "#128275", "agricultura": "#496bb4", "pastagem": "#d89430"},
                      hover_data=["n_entities"], labels={"use": "Uso", "ano": "Ano"}, title="Estoques no suporte municipal documentado")
        st.plotly_chart(style_figure(fig, 370), width="stretch", key="econ_stocks")
        changes = []
        for use, chunk in stocks.groupby("use"):
            chunk = chunk.sort_values("ano")
            first, last = chunk.iloc[0], chunk.iloc[-1]
            changes.append({"Uso": use, "Ano inicial": int(first.ano), "Ano final": int(last.ano),
                            "Estoque inicial (ha)": first.area_ha, "Estoque final (ha)": last.area_ha,
                            "Mudança líquida (ha)": last.area_ha - first.area_ha,
                            "Mudança líquida (%)": 100 * (last.area_ha / first.area_ha - 1) if first.area_ha else np.nan,
                            "Municípios iniciais": int(first.n_entities), "Municípios finais": int(last.n_entities)})
        st.dataframe(pd.DataFrame(changes), hide_index=True, width="stretch")
        st.caption("Estoque é uma fotografia anual, não somado ao longo dos anos. A mudança líquida agrícola pode reunir conversão direta, "
                   "substituição entre usos já abertos e outros fluxos; estes saldos não identificam a transição pastagem → agricultura. "
                   "Os estoques de uso da terra e o denominador das transições têm máscaras/finalidades distintas.")
        st.caption(f"Série de estoques: {portrait['metadata'].get('stock_series_n_entities', 0)} municípios com os três estoques e a área de referência "
                   "válidos em todos os anos. Esse suporte é construído separadamente da coorte dos fluxos e é mantido constante.")
    else:
        st.info("Não há municípios com estoques comparáveis em todos os anos selecionados. Reduza a janela ou reveja os filtros para comparar estoques no tempo.")
    with st.expander("Tabelas econômicas e critérios da amostra"):
        view = destinations.rename(columns={"destination": "Destino", "conversion_ha": "Fluxo bruto (ha)", "nobs": "N pares", "n_entities": "Municípios"})
        show_table(view, "economia_destinos", "Conversão por destino no recorte", "Taxas em proporção; dados observados, sem extrapolação de ausências.")
        st.dataframe(by_biome, width="stretch", hide_index=True)
        st.dataframe(stocks, width="stretch", hide_index=True)
        st.json(portrait["metadata"], expanded=False)


def univariate_view(df, blocks):
    st.subheader("O que é típico, raro ou economicamente expressivo?")
    st.write("A média pode esconder assimetria, concentração e heterogeneidade. Examine a distribuição de cada medida e compare os biomas no seu próprio suporte.")
    analytical_blocks = {b: [c for c in cols if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
                         for b, cols in blocks.items() if not b.startswith("[Flags]")}
    analytical_blocks = {b: cols for b, cols in analytical_blocks.items() if cols}
    a, b = st.columns([1, 2])
    block = a.selectbox("Família econômica", list(analytical_blocks), key="uni_block")
    choices = analytical_blocks[block]
    default = choices.index(RATE_COLUMNS[0]) if RATE_COLUMNS[0] in choices else 0
    variable = b.selectbox("Variável para análise univariada", choices, index=default, format_func=label, key="uni_variable")
    unit_options = {"Automática (unidade natural)": "auto", "Município–ano": "municipality_year",
                    "Média por município": "municipality", "Média por ano": "year"}
    a, b, c = st.columns(3)
    unit = a.selectbox("Unidade da distribuição", list(unit_options), key="uni_unit")
    transform = b.selectbox("Escala visual", ["Nível", "log(1 + x), somente não negativos"], key="uni_transform")
    group = c.checkbox("Comparar biomas", True, key="uni_by_biome")
    try:
        result = univariate_summary(df, variable, unit=unit_options[unit])
    except ValueError as error:
        st.info(str(error))
        return
    stats = result["stats"]
    st.write(variable_meaning(variable))
    meta = result["metadata"]
    effective_unit = meta.get("unit", meta.get("effective_unit", unit_options[unit]))
    unit_names = {"municipality_year": "pares município–ano", "municipality": "municípios", "year": "anos"}
    st.caption(f"Distribuição calculada sobre {unit_names.get(effective_unit, effective_unit)}. "
               "Na unidade automática, preços comuns contam uma vez por ano e atributos fixos uma vez por município. "
               "Médias por município ou por ano dão peso igual a essas unidades, não aos pares originais.")
    multiplier = 100 if variable.startswith("taxa_conversao__") else 1
    suffix = " (%)" if multiplier == 100 else ""
    units = variable_unit(variable)
    st.caption(f"Unidade dos valores em nível: {units}. As tabelas de exportação mantêm a unidade original do CSV; taxas em proporção 0–1.")
    a, b, c, d = st.columns(4)
    a.metric("Mediana" + suffix, fmt(stats["median"] * multiplier, 4))
    b.metric("Média" + suffix, fmt(stats["mean"] * multiplier, 4))
    c.metric("P95" + suffix, fmt(stats["p95"] * multiplier, 4))
    d.metric("Zeros entre valores válidos", f"{fmt(stats['zero_pct'], 1)}%")
    if stats["n_valid"] == 0:
        st.info("Não há valores válidos para esta variável no recorte.")
        return
    if pd.notna(stats["mean"]) and stats["mean"] > stats["median"]:
        st.info(f"A média ({fmt(stats['mean'] * multiplier, 4)}) supera a mediana ({fmt(stats['median'] * multiplier, 4)}). "
                "Observe a cauda superior e o P95: valores altos podem ter peso importante no retrato agregado. "
                "A mediana caracteriza a unidade típica sob a ponderação escolhida.")
    else:
        st.info("Compare média, mediana e quantis para separar o comportamento típico dos extremos. "
                "Um valor médio pequeno pode coexistir com episódios relevantes em determinados municípios ou anos.")
    if stats["n_zero"] > 0 and stats["n_positive"] > 0:
        st.write(f"Há **{int(stats['n_zero'])} zeros** e **{int(stats['n_positive'])} valores positivos**. "
                 f"A média entre os positivos é **{fmt(stats['mean_positive'] * multiplier, 4)}**{suffix}. "
                 "Essa separação distingue a ocorrência observada da intensidade quando há valor positivo; não identifica o motivo de um zero.")
    display = result["sample"].dropna(subset=["value"]).copy()
    display["Valor"] = display.value * multiplier
    axis = label(variable) + " · " + units
    if transform != "Nível":
        excluded = int(display.value.lt(0).sum())
        display = display.loc[display.value.ge(0)].copy()
        display["Valor"] = np.log1p(display.value)
        axis = "log(1 + x) na unidade original"
        st.caption(f"Escala visual log1p: {excluded} valores negativos excluídos apenas destes gráficos. Estatísticas e tabelas permanecem na escala original.")
    if display.empty:
        st.info("A escala escolhida não tem valores representáveis neste recorte.")
    else:
        color = "bioma_dominante" if group and "bioma_dominante" in display and display.bioma_dominante.notna().any() else None
        bins = st.slider("Classes do histograma", 10, 80, 30, key="uni_hist_bins")
        a, b = st.columns(2)
        fig = px.histogram(display, x="Valor", color=color, nbins=bins, histnorm="percent", barmode="overlay", opacity=.65,
                           color_discrete_map=COLORS, labels={"Valor": axis, "bioma_dominante": "Bioma"}, title="Distribuição e caudas")
        fig.update_layout(yaxis_title="Percentual dentro de cada grupo")
        a.plotly_chart(style_figure(fig), width="stretch", key="uni_histogram")
        fig = px.ecdf(display, x="Valor", color=color, ecdfnorm="percent", color_discrete_map=COLORS,
                      labels={"Valor": axis, "bioma_dominante": "Bioma"}, title="Qual parcela está abaixo de cada valor?")
        fig.update_layout(yaxis_title="Percentual acumulado")
        b.plotly_chart(style_figure(fig), width="stretch", key="uni_ecdf")
    quantiles = pd.DataFrame({"Quantil": ["Mín", "P1", "P5", "P25", "P50", "P75", "P95", "P99", "Máx"],
                              "Valor" + suffix: [stats[k] * multiplier for k in ["min", "p01", "p05", "p25", "median", "p75", "p95", "p99", "max"]]})
    st.dataframe(quantiles, width="stretch", hide_index=True)
    by_biome = result["by_biome"]
    if not by_biome.empty:
        st.markdown("**Valores típicos e dispersão por bioma**")
        view = by_biome[["bioma_dominante", "n_valid", "mean", "median", "p25", "p75", "p95", "zero_pct"]].copy()
        for col in ["mean", "median", "p25", "p75", "p95"]:
            view[col] *= multiplier
        view = view.rename(columns={"bioma_dominante": "Bioma", "n_valid": "N válido", "mean": "Média" + suffix, "median": "Mediana" + suffix,
                                    "p25": "P25" + suffix, "p75": "P75" + suffix, "p95": "P95" + suffix, "zero_pct": "Zeros (%)"})
        st.dataframe(view, width="stretch", hide_index=True)
    st.caption(f"N válido: {stats['n_valid']} de {stats['n_total']}; ausentes na unidade escolhida: {stats['n_missing']}. "
               "Histogramas e ECDF são descritivos; observações repetidas do mesmo município não são amostras independentes para inferência.")
    with st.expander("Tabela completa, unidades e exportação"):
        show_table(pd.DataFrame([stats]), "univariada_estatisticas", label(variable), f"Unidade observacional: {effective_unit}; unidade de medida: {units}; taxas exportadas em proporção 0–1.")
        st.json(meta, expanded=False)


def economic_relations(df, reference, analytical, institutions):
    st.subheader("Como os incentivos se encontram com as condições locais?")
    st.write("Use os cruzamentos para formular intuições sobre H1-a e H1-b. Depois verifique se a relação permanece "
             "quando diferenças municipais, anos comuns e controles observados são removidos.")
    a, b = st.columns(2)
    y = a.selectbox("Destino a explicar", RATE_COLUMNS, format_func=label, key="rel_y")
    capacities = [c for c in df if c.startswith("capacidade_z__")]
    default_c = next((i for i, c in enumerate(capacities) if "soja__gaez_sxHr0" in c), 0)
    capacity = b.selectbox("Capacidade produtiva para o cruzamento", capacities, index=default_c, format_func=label, key="rel_capacity")
    prices = [c for c in df if c.startswith(("ln_preco_real_", "dln_preco_real_"))]
    default_p = next((i for i, c in enumerate(prices) if c == "ln_preco_real_usd2024_media_anual_lag1__soja"), 0)
    a, b = st.columns(2)
    price = a.selectbox("Preço ou variação de preço", prices, index=default_p, format_func=label, key="rel_price")
    inst = b.selectbox("Estratificação institucional (H1-b)", ["(Sem estratificação)"] + institutions,
                       format_func=label, key="rel_institution")
    a, b = st.columns(2)
    group_count = a.slider("Grupos ordenados de capacidade", 2, 4, 3, key="rel_group_count")
    balanced = b.checkbox("Mesmos municípios com as variáveis válidas em todos os anos", True, key="rel_balanced")
    base = economic_portrait(df, reference, balanced=balanced)["sample"]
    if balanced and not base.empty:
        required = [y, capacity, price] + ([] if inst.startswith("(") else [inst])
        valid = base[required].replace([np.inf, -np.inf], np.nan).notna().all(axis=1)
        if not inst.startswith("("):
            valid &= base[inst].ge(0)
        counts = base.loc[valid].groupby("codigo_ibge").ano.nunique()
        ids = counts.index[counts.eq(reference.ano.nunique())]
        base = base.loc[base.codigo_ibge.isin(ids)].copy()
    if base.empty:
        st.info("Não há suporte na coorte escolhida para os cruzamentos. Desative a exigência de todos os anos para examinar a cobertura disponível.")
    else:
        try:
            result = grouped_hypothesis(base, capacity, price, None if inst.startswith("(") else inst, group_count, y)
        except ValueError as error:
            st.info(str(error))
        else:
            table = result["table"].copy()
            if table.empty:
                st.info("Não há observações conjuntas válidas para as variáveis do cruzamento.")
            else:
                table["Média da taxa (%)"] = 100 * table.mean_y
                table["Taxa ponderada (%)"] = 100 * table.weighted_rate
                st.caption(f"Suporte conjunto: {len(result['sample']):,} pares e {result['sample'].codigo_ibge.nunique()} municípios. "
                           f"Capacidade em {variable_unit(capacity)}; preço em {variable_unit(price)}. "
                           "Grupos de capacidade ficam fixos no recorte; a classe de registros IBAMA de um município pode mudar de ano.")
                st.markdown("**H1-a: anos de preços diferentes se associam a respostas distintas por capacidade?**")
                for institution_group, chunk in table.groupby("institution_group", observed=True, sort=False):
                    matrix = chunk.pivot(index="capacity_group", columns="price_group", values="Média da taxa (%)")
                    counts = chunk.pivot(index="capacity_group", columns="price_group", values="nobs").reindex(index=matrix.index, columns=matrix.columns)
                    fig = px.imshow(matrix, text_auto=".3f", aspect="auto", color_continuous_scale="YlGnBu",
                                    labels={"x": "Condição do preço", "y": "Grupo de capacidade", "color": "Taxa média (%)"},
                                    title=f"{institution_group} · {label(y)}")
                    fig.update_traces(customdata=counts.to_numpy(), hovertemplate="Capacidade: %{y}<br>Preço: %{x}<br>Taxa média: %{z:.4f}%<br>N pares: %{customdata}<extra></extra>")
                    st.plotly_chart(style_figure(fig, 340), width="stretch", key="rel_heat_" + str(institution_group))
                st.caption("Cortes de capacidade são calculados com um valor por município; cortes de preços com um valor por ano. "
                           "Empates permanecem juntos. O mapa mostra médias simples das taxas; a tabela inclui taxas ponderadas, N pares, municípios e anos. "
                           "A comparação de anos de preço alto e baixo também incorpora mudanças históricas.")
                if price.startswith("dln_"):
                    st.caption("Nesta seleção, baixo/alto classifica a variação logarítmica do preço em relação à sua mediana, "
                               "não o nível do preço nem necessariamente queda/aumento em relação a zero.")
                gaps = result["gaps"].copy()
                if not gaps.empty:
                    gaps["Diferença na média (p.p.)"] = 100 * gaps.gap_mean_y
                    fig = px.bar(gaps, x="capacity_group", y="Diferença na média (p.p.)", color="institution_group", barmode="group",
                                 hover_data=["n_low", "n_high"], labels={"capacity_group": "Capacidade", "institution_group": "Registro IBAMA"},
                                 title="Taxa no indicador de preço alto menos taxa no indicador baixo")
                    fig.add_hline(y=0, line_color="#777")
                    st.plotly_chart(style_figure(fig, 380), width="stretch", key="rel_gaps")
                    valid_gaps = gaps.dropna(subset=["gap_mean_y"])
                    if not valid_gaps.empty:
                        low, high = valid_gaps.gap_mean_y.min() * 100, valid_gaps.gap_mean_y.max() * 100
                        st.info(f"**Leitura do recorte:** os contrastes alto − baixo variam de {fmt(low, 4)} a {fmt(high, 4)} pontos percentuais "
                                "entre os grupos observados. A previsão H1-a interessa à diferença da resposta entre capacidades, não somente "
                                "à maior conversão em um grupo. Um gradiente contrário também é informativo e deve ser confrontado com tempo, estoques e composição da amostra.")
                annual = result["annual"].copy()
                if not annual.empty:
                    annual["Taxa média (%)"] = 100 * annual.mean_y
                    fig = px.line(annual, x="ano", y="Taxa média (%)", color="capacity_group", line_dash="institution_group", markers=True,
                                  hover_data=["nobs", "n_entities"], labels={"capacity_group": "Capacidade", "institution_group": "Registro IBAMA", "ano": "Ano"},
                                  title="Trajetórias por capacidade: contraste de nível ou mudança conjunta?")
                    st.plotly_chart(style_figure(fig, 400), width="stretch", key="rel_annual")
                if not inst.startswith("("):
                    st.write("**H1-b:** compare o contraste entre preços dentro de cada grupo de registros do IBAMA. "
                             "Menor contraste em um grupo é um padrão descritivo a investigar; contagens e multas podem responder à própria conversão. "
                             "Zero observado/imputado e intensidade positiva são apresentados separadamente quando há suporte.")
                with st.expander("Células, cobertura, cortes e tabelas para exportação"):
                    show_table(table, "cruzamentos_h1", "Conversão, capacidade, preços e registros institucionais", "Taxas originais em proporção; colunas (%) explicitamente multiplicadas por 100.")
                    st.dataframe(gaps, width="stretch", hide_index=True)
                    st.json(result["metadata"], expanded=False)
    st.divider()
    partial_relationship(df, analytical, institutions)


def partial_relationship(df, analytical, institutions):
    st.subheader("A associação muda quando comparamos condições semelhantes?")
    a, b = st.columns(2)
    y = a.selectbox("Y da relação parcial", RATE_COLUMNS, format_func=label, key="partial_y")
    choices = [c for c in analytical if c not in RATE_COLUMNS]
    default = next((i for i, c in enumerate(choices) if c.startswith(INTERACTION_PREFIX) and "soja__gaez_sxHr0" in c), 0)
    x = b.selectbox("X de interesse", choices, index=default, format_func=label, key="partial_x")
    control_choices = [c for c in analytical if c not in [x, y] and not c.startswith(("taxa_conversao__", "conversao_ha__"))]
    a, b = st.columns([2, 1])
    controls = a.multiselect("Condições observadas a retirar de X e Y", control_choices, ["precip_zscore_1981_2000"] if x != "precip_zscore_1981_2000" else [],
                            format_func=label, max_selections=10, key="partial_controls")
    selected_mode = b.selectbox("Comparação territorial e temporal", list(MODES), index=2, key="partial_mode")
    try:
        result = multivariate_partial(df, y, x, controls=controls, mode=MODES[selected_mode])
    except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
        st.info(f"Relação parcial indisponível: {error}")
        return
    sample = result["sample"]
    if sample.empty or not np.isfinite(result["slope"]):
        st.info("X não possui variação identificável após retirar os efeitos e controles selecionados, ou a amostra é insuficiente.")
        return
    # Metric helpers return their own index. Match keys, never filtered row
    # labels, so all comparisons and clustered inference use the same sample.
    common = df.merge(sample[["codigo_ibge", "ano"]], on=["codigo_ibge", "ano"], how="inner", validate="one_to_one")
    raw_x = pd.to_numeric(common[x], errors="coerce")
    iqr = float(raw_x.quantile(.75) - raw_x.quantile(.25))
    projected_pp = 100 * result["slope"] * iqr
    a, b, c = st.columns(3)
    a.metric("Pares na mesma amostra", int(result["nobs"]))
    b.metric("Correlação parcial", fmt(result["correlation"], 3))
    c.metric("Contraste linear P75 − P25 de X", f"{fmt(projected_pp, 4)} p.p.")
    st.caption(f"P25 de X = {fmt(raw_x.quantile(.25), 4)}; P75 = {fmt(raw_x.quantile(.75), 4)}. "
               "O contraste é β × (P75−P25) na distribuição original de X da amostra conjunta; "
               "resume escala econômica da associação linear, sem representar uma previsão causal ou garantir suporte para todas as combinações.")
    display = sample.copy()
    display["Resíduo de Y (p.p.)"] = 100 * display.y_partial
    fig = px.scatter(display, x="x_partial", y="Resíduo de Y (p.p.)", color="bioma_dominante", opacity=.38,
                     color_discrete_map=COLORS, hover_data=["codigo_ibge", "ano"],
                     labels={"x_partial": "Parte de X não explicada por controles e efeitos", "bioma_dominante": "Bioma"})
    xx = np.linspace(display.x_partial.min(), display.x_partial.max(), 80)
    fig.add_trace(go.Scatter(x=xx, y=100 * result["slope"] * xx, mode="lines", line=dict(color="#383b48"), name="Associação parcial"))
    st.plotly_chart(style_figure(fig, 470), width="stretch", key="partial_scatter")
    comparisons = []
    for title, mode, cond in [("Associação bruta", "pooled", []), (selected_mode + " · sem controles", MODES[selected_mode], []),
                               (selected_mode + " · com controles", MODES[selected_mode], controls)]:
        try:
            fit = multivariate_partial(common, y, x, cond, mode)
            comparisons.append({"Comparação": title, "N": fit["nobs"], "Inclinação": fit["slope"],
                                "Correlação parcial": fit["correlation"], "Contraste P75−P25 (p.p.)": 100 * fit["slope"] * iqr})
        except (ValueError, RuntimeError, np.linalg.LinAlgError):
            comparisons.append({"Comparação": title, "N": len(common), "Inclinação": np.nan, "Correlação parcial": np.nan, "Contraste P75−P25 (p.p.)": np.nan})
    comparison = pd.DataFrame(comparisons).drop_duplicates("Comparação")
    st.dataframe(comparison, width="stretch", hide_index=True)
    st.write("**Como interpretar:** mudanças no sinal ou na magnitude ao retirar efeitos e controles mostram que a associação bruta "
             "também reflete diferenças entre territórios, anos ou variáveis observadas. Todas as linhas acima usam os mesmos pares; "
             "a diferença não decorre de trocar a amostra.")
    if MODES[selected_mode] == "twoway":
        try:
            fitted = fit_twfe(common, y, [x, *controls], name="Associação parcial TWFE")
            coeff = fitted["coefficients"].set_index("term").loc[x]
            if coeff.status == "estimated":
                lo, hi = 100 * coeff.ci_lower * iqr, 100 * coeff.ci_upper * iqr
                st.write(f"Para o contraste P75−P25, o **IC 95% clusterizado por município** vai de **{fmt(lo, 4)} a {fmt(hi, 4)} p.p.** "
                         f"O modelo completo usa {fitted['diagnostics']['n_entities']} clusters. "
                         "O intervalo é calculado no modelo completo, com os graus de liberdade dos efeitos fixos.")
                if fitted["diagnostics"].get("warnings"):
                    st.caption(fitted["diagnostics"]["warnings"])
        except (ValueError, RuntimeError, np.linalg.LinAlgError, ZeroDivisionError) as error:
            st.caption(f"Inferência clusterizada indisponível neste recorte: {error}")
    st.caption("O gráfico retira de X e Y os mesmos efeitos e controles por projeção linear na mesma amostra (Frisch–Waugh–Lovell). "
               "Controles não eliminam automaticamente seleção, causalidade reversa ou variáveis omitidas. "
               "Use o laboratório para comparar explicitamente especificações e interações institucionais completas.")
    with st.expander("Exportar comparação e verificar a projeção"):
        show_table(comparison, "relacao_parcial", "Associações brutas e parciais na mesma amostra", f"Y={y}; X={x}; controles={', '.join(controls)}")
        st.json(result["metadata"], expanded=False)
