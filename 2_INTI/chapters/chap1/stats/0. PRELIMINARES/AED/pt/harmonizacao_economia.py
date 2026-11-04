"""Derivadas econômicas e climáticas candidatas, sem gravações ao importar.

As funções retornam DataFrames; ``attrs['metadados']`` registra as escolhas.
Um indicador calculável não é, por isso, uma exposição exógena ou causal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


FONTES_DEFLATORES = {
    "cpi": {
        "arquivo": "bls_fred_CPIAUCNS_1960_2024.csv",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCNS&cosd=1960-01-01&coed=2024-12-31",
        "documentacao": "https://fred.stlouisfed.org/series/CPIAUCNS",
        "descricao": "BLS CPI-U, todos os itens, média urbana EUA, mensal, sem ajuste sazonal; 1982-84=100.",
        "moeda": "USD",
    },
    "ipca": {
        "arquivo": "ibge_sidra_1737_ipca_2266_1994_2024.json",
        "url": "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/199401-202412?formato=json",
        "documentacao": "https://sidra.ibge.gov.br/tabela/1737",
        "descricao": "IBGE IPCA Brasil, número-índice mensal, variável 2266; dezembro de 1993=100.",
        "moeda": "BRL",
    },
}


def _chave(base, colunas):
    if base[colunas].isna().any().any() or base.duplicated(colunas).any():
        raise ValueError(f"Chave ausente ou duplicada: {colunas}")


def _numero(serie):
    return pd.to_numeric(serie, errors="coerce").replace([np.inf, -np.inf], np.nan)


def _produto(serie):
    nomes = {
        "price_soja": "soja", "Soja (em grão)": "soja", "soja": "soja",
        "price_milho": "milho", "Milho (em grão)": "milho", "milho": "milho",
        "price_carne_bovina": "carne_bovina", "carne_bovina": "carne_bovina",
    }
    produto = serie.map(nomes)
    if produto.isna().any():
        raise ValueError(f"Produto sem mapeamento explícito: {serie[produto.isna()].unique()}")
    return produto


def _metadados(base, **itens):
    base.attrs["metadados"] = itens
    return base


def _lag_calendario(base, grupos, colunas, lag=1):
    """O ano anterior é t-1, mesmo quando faltam linhas na série."""
    _chave(base, grupos + ["ano"])
    anterior = base[grupos + ["ano"] + colunas].copy()
    anterior["ano"] += lag
    anterior = anterior.rename(columns={c: f"{c}_lag{lag}" for c in colunas})
    return base.merge(anterior, on=grupos + ["ano"], how="left", validate="one_to_one")


def _z_fixo(base, grupos, coluna):
    """Padronização entre municípios, em cada cenário; desvio amostral."""
    agrupado = base.groupby(grupos, observed=True)[coluna]
    media, desvio = agrupado.transform("mean"), agrupado.transform("std")
    base["capacidade_media_referencia"] = media
    base["capacidade_desvio_referencia"] = desvio
    base["n_municipios_referencia"] = agrupado.transform("count")
    base["capacidade_z"] = (base[coluna] - media) / desvio.where(desvio > 0)
    base["flag_desvio_capacidade_nulo"] = desvio.isna() | desvio.le(0)
    return base


def carregar_deflator(caminho, fonte="cpi"):
    """Lê somente o cache: data mensal e indice_precos; não usa rede."""
    caminho = Path(caminho)
    if fonte == "cpi":
        dados = pd.read_csv(caminho)
        out = dados.rename(columns={"observation_date": "data", "CPIAUCNS": "indice_precos"})
    elif fonte == "ipca":
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
        linhas = [r for r in dados if r.get("D2C") == "2266"]
        if not linhas or any(r.get("D1C") != "1" for r in linhas):
            raise ValueError("A resposta SIDRA não contém apenas o IPCA Brasil esperado.")
        out = pd.DataFrame({"data": [r["D3C"] + "01" for r in linhas],
                            "indice_precos": [r["V"] for r in linhas]})
        out["data"] = pd.to_datetime(out["data"], format="%Y%m%d", errors="raise")
    else:
        raise ValueError("Fonte deve ser cpi ou ipca.")
    out = out[["data", "indice_precos"]].copy()
    out["data"] = pd.to_datetime(out["data"], errors="raise").dt.to_period("M").dt.to_timestamp()
    out["indice_precos"] = _numero(out["indice_precos"])
    _chave(out, ["data"])
    if out["indice_precos"].isna().any() or out["indice_precos"].le(0).any():
        raise ValueError("O índice precisa ter níveis mensais positivos, não taxas de inflação.")
    return _metadados(out.sort_values("data").reset_index(drop=True), **FONTES_DEFLATORES[fonte])


def obter_deflatores(destino):
    """Aquisição explícita e idempotente; preserva caches existentes."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    manifesto = {"obtido_em_utc": datetime.now(timezone.utc).isoformat(), "fontes": {}}
    for fonte, info in FONTES_DEFLATORES.items():
        caminho = destino / info["arquivo"]
        existia = caminho.exists()
        if not existia:
            req = Request(info["url"], headers={"User-Agent": "Mozilla/5.0 thesis research"})
            with urlopen(req, timeout=30) as resposta:
                conteudo = resposta.read()
            # Nunca sobrescrever um arquivo de origem já existente.
            with caminho.open("xb") as arquivo:
                arquivo.write(conteudo)
        tabela = carregar_deflator(caminho, fonte)
        manifesto["fontes"][fonte] = {
            **info, "sha256": hashlib.sha256(caminho.read_bytes()).hexdigest(),
            "linhas": len(tabela), "inicio": str(tabela.data.min().date()),
            "fim": str(tabela.data.max().date()), "cache_preexistente": existia,
        }
    caminho_manifesto = destino / "manifesto_deflatores.json"
    if not caminho_manifesto.exists():
        caminho_manifesto.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifesto


def anualizar_precos(df, deflator=None, ano_inicial=2000, ano_final=2024, ano_base=2024):
    """Média dos preços mensais; deflação mês a mês antes da média anual."""
    if ano_base != 2024:
        raise ValueError("Os nomes das colunas usam USD2024; outra base exige versão explícita.")
    base = df.copy()
    base["data"] = pd.to_datetime(base["data"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    base["produto"] = _produto(base["variavel"])
    _chave(base, ["produto", "data"])
    if "moeda" in base and not base["moeda"].dropna().eq("USD").all():
        raise ValueError("Esta função espera preços em USD.")
    base["ano"], base["mes"] = base.data.dt.year, base.data.dt.month
    base["preco_nominal"] = _numero(base["preco_nominal"])
    base["flag_preco_zero"] = base.preco_nominal.eq(0)
    base["flag_preco_negativo"] = base.preco_nominal.lt(0)
    base["flag_preco_ausente"] = base.preco_nominal.isna()
    # Estes preços spot devem ser positivos; zero/negativo bloqueia o ano e fica contado.
    base["preco_nominal"] = base["preco_nominal"].where(base["preco_nominal"] > 0)
    base["preco_real_usd2024"] = np.nan
    indice_base = None
    if deflator is not None:
        moeda_indice = deflator.attrs.get("metadados", {}).get("moeda")
        if moeda_indice is not None and moeda_indice != "USD":
            raise ValueError("Preços em USD exigem deflator compatível com USD, não IPCA/BRL.")
        indice = deflator[["data", "indice_precos"]].copy()
        indice["data"] = pd.to_datetime(indice["data"], errors="coerce").dt.to_period("M").dt.to_timestamp()
        indice["indice_precos"] = _numero(indice["indice_precos"])
        _chave(indice, ["data"])
        if indice["indice_precos"].dropna().le(0).any():
            raise ValueError("Índice de preços não positivo.")
        referencia = indice.loc[indice.data.dt.year.eq(ano_base), "indice_precos"]
        if len(referencia) != 12 or referencia.count() != 12:
            raise ValueError("A base monetária exige os 12 índices mensais de 2024.")
        indice_base = float(referencia.mean())
        base = base.merge(indice, on="data", how="left", validate="many_to_one")
        base["preco_real_usd2024"] = base.preco_nominal * indice_base / base.indice_precos
    anual = base.groupby(["produto", "ano"], observed=True).agg(
        meses_registrados=("mes", "nunique"), meses_nominais_validos=("preco_nominal", "count"),
        meses_reais_validos=("preco_real_usd2024", "count"),
        meses_preco_zero=("flag_preco_zero", "sum"),
        meses_preco_negativo=("flag_preco_negativo", "sum"),
        meses_preco_ausente=("flag_preco_ausente", "sum"),
        preco_nominal_media_anual=("preco_nominal", "mean"),
        preco_real_usd2024_media_anual=("preco_real_usd2024", "mean"),
    ).reset_index()
    anual["flag_ano_nominal_incompleto"] = anual.meses_registrados.ne(12) | anual.meses_nominais_validos.ne(12)
    anual["flag_ano_real_incompleto"] = anual.meses_registrados.ne(12) | anual.meses_reais_validos.ne(12)
    nominal, real = "preco_nominal_media_anual", "preco_real_usd2024_media_anual"
    anual.loc[anual.flag_ano_nominal_incompleto, nominal] = np.nan
    anual.loc[anual.flag_ano_real_incompleto, real] = np.nan
    for coluna in (nominal, real):
        anual["ln_" + coluna] = np.log(anual[coluna].where(anual[coluna] > 0))
    anual = _lag_calendario(anual, ["produto"], [nominal, real, "ln_" + nominal, "ln_" + real])
    for coluna in (nominal, real):
        anual["dln_" + coluna] = anual["ln_" + coluna] - anual["ln_" + coluna + "_lag1"]
    anual = _lag_calendario(anual, ["produto"], ["dln_" + nominal, "dln_" + real])
    anual["unidade_nominal"] = np.where(anual.produto.eq("carne_bovina"), "USD/kg", "USD/t")
    anual["unidade_real"] = np.where(anual.produto.eq("carne_bovina"), "USD2024/kg", "USD2024/t")
    anual = anual.loc[anual.ano.between(ano_inicial, ano_final)].sort_values(["produto", "ano"]).reset_index(drop=True)
    return _metadados(anual, janela="ano civil; lag1 usa o ano civil anterior", meses_minimos=12,
        formula_real="preco_mensal * media_CPI_U_2024 / CPI_U_mensal; depois media anual",
        indice_base_2024=indice_base, deflator="CPI-U BLS/FRED CPIAUCNS" if deflator is not None else None,
        interpretacao="Poder de compra geral em USD; não custo de insumos nem preço local esperado.",
        nao_positivos="Preços spot zero/negativos ficam contados e bloqueiam o ano até conferência; bruto não é alterado.",
        log="log da média anual; dln é diferença entre logs de médias anuais consecutivas")


def produtividade_historica(df, inicio=1991, fim=2000, minimo_anos=7, geografia_validada=False):
    """Baseline candidato: média dos rendimentos registrados em pelo menos 7/10 anos."""
    if not inicio <= fim < 2001 or not 1 <= minimo_anos <= fim - inicio + 1:
        raise ValueError("Janela deve terminar antes de 2001, com mínimo de anos compatível.")
    base = df.copy()
    base["produto"] = _produto(base["produto"])
    base["ano"] = pd.to_numeric(base["ano"], errors="raise").astype(int)
    _chave(base, ["codigo_ibge", "ano", "produto"])
    universo = base[["codigo_ibge", "produto"]].drop_duplicates()
    historico = base.loc[base.ano.between(inicio, fim)].copy()
    historico["rendimento_medio_kg_ha"] = _numero(historico["rendimento_medio_kg_ha"])
    valido = historico.rendimento_medio_kg_ha.ge(0)
    if "area_colhida_ha" in historico:
        valido &= _numero(historico.area_colhida_ha).gt(0)
    historico["rendimento_valido"] = historico.rendimento_medio_kg_ha.where(valido)
    resumo = historico.groupby(["codigo_ibge", "produto"], observed=True).agg(
        media_historica_kg_ha=("rendimento_valido", "mean"),
        anos_validos=("rendimento_valido", "count"), anos_registrados=("ano", "nunique"),
    ).reset_index()
    out = universo.merge(resumo, on=["codigo_ibge", "produto"], how="left", validate="one_to_one")
    out[["anos_validos", "anos_registrados"]] = out[["anos_validos", "anos_registrados"]].fillna(0).astype(int)
    out["fracao_anos_validos"] = out.anos_validos / (fim - inicio + 1)
    out["flag_cobertura_historica_insuficiente"] = out.anos_validos.lt(minimo_anos)
    out.loc[out.flag_cobertura_historica_insuficiente, "media_historica_kg_ha"] = np.nan
    out["flag_geografia_historica_pendente"] = not geografia_validada
    out["cenario_capacidade"] = f"pam_{inicio}_{fim}_min{minimo_anos}"
    out["capacidade_valor"] = out.media_historica_kg_ha
    out["capacidade_unidade"] = "kg/ha"
    out["fonte_capacidade"] = "PAM"
    out = _z_fixo(out, ["produto", "cenario_capacidade"], "capacidade_valor")
    return _metadados(out, inicio=inicio, fim=fim, minimo_anos=minimo_anos, media="aritmética entre anos válidos",
        justificativa=f"Janela pré-painel; mínimo de {minimo_anos}/{fim-inicio+1} anos evita baseline de um único registro.",
        limites="Corte 7/10 é regra operacional candidata; seleção de produtores e geografia histórica permanecem relevantes.",
        geografia_validada=bool(geografia_validada), padronizacao="z entre municípios com baseline válido, por produto; ddof=1")


def preparar_gaez(df):
    """Mantém cada raster como cenário; sx/10000 e z entre municípios."""
    out = df.copy()
    _chave(out, ["codigo_ibge", "variavel_raster"])
    rasters = out.variavel_raster.astype(str)
    out["produto"] = np.select([rasters.str.endswith("_mze"), rasters.str.endswith("_soy")], ["milho", "soja"], default="")
    if out.produto.eq("").any() or not rasters.str.startswith(("sx", "yx")).all():
        raise ValueError("Raster GAEZ fora dos produtos/tipos esperados.")
    out["tipo_capacidade"] = np.where(rasters.str.startswith("sx"), "aptidao", "rendimento_potencial")
    out["valor_medio"] = _numero(out["valor_medio"])
    sx = out.tipo_capacidade.eq("aptidao")
    valido = out.valor_medio.ge(0) & (~sx | out.valor_medio.le(10000))
    out["flag_capacidade_fora_dominio"] = ~valido
    out["capacidade_valor"] = out.valor_medio.where(valido)
    out["aptidao_0_1"] = (out.valor_medio / 10000).where(sx & valido)
    out["capacidade_unidade"] = np.where(sx, "indice 0-10000", "kg materia seca/ha")
    out["cenario_capacidade"] = "gaez_" + rasters
    out["fonte_capacidade"] = "GAEZ"
    out["flag_temporalidade_pendente"] = True
    out["flag_umidade_comercial_pendente"] = ~sx
    out = _z_fixo(out, ["produto", "cenario_capacidade"], "capacidade_valor")
    return _metadados(out, sx="índice dividido por 10000, não probabilidade", referencia="clima 1961-1990; terras 2010",
        padronizacao="z entre municípios no mesmo raster; ddof=1; não ponderado por área municipal",
        limites="Nem exogeneidade nem compatibilidade temporal/umidade são presumidas; nenhum cenário escolhido por ajuste.")


def anualizar_chuva(df, limiar_fracao_pixels=0.95, ano_inicial=1981, ano_final=2024):
    """Soma meses completos e calcula referências históricas com cobertura integral."""
    if not 0 <= limiar_fracao_pixels <= 1:
        raise ValueError("Cobertura de pixels deve ficar entre 0 e 1.")
    base = df.copy()
    _chave(base, ["codigo_ibge", "ano", "mes"])
    if not base.mes.between(1, 12).all() or not (base.mes % 1 == 0).all():
        raise ValueError("Mês inválido.")
    base["precip_mm"] = _numero(base["precip_mm"])
    base["flag_precip_invalida"] = base.precip_mm.isna() | base.precip_mm.lt(0)
    base["precip_mm"] = base.precip_mm.where(~base.flag_precip_invalida)
    if "fracao_pixels_validos" not in base:
        base["fracao_pixels_validos"] = np.nan
    base["fracao_pixels_validos"] = _numero(base["fracao_pixels_validos"])
    espacial = base.fracao_pixels_validos.between(limiar_fracao_pixels, 1)
    base["precip_mm"] = base.precip_mm.where(espacial)
    anual = base.groupby(["codigo_ibge", "ano"], observed=True).agg(
        precip_mm_anual=("precip_mm", lambda s: s.sum(min_count=12)),
        meses_registrados=("mes", "nunique"), meses_validos=("precip_mm", "count"),
        fracao_pixels_minima=("fracao_pixels_validos", "min"),
        meses_cobertura_conhecida=("fracao_pixels_validos", "count"),
    ).reset_index()
    anual["flag_ano_incompleto"] = anual.meses_registrados.ne(12) | anual.meses_validos.ne(12)
    anual.loc[anual.flag_ano_incompleto, "precip_mm_anual"] = np.nan
    referencias = [(1981, 2000), (1981, 2010), (1991, 2020)]
    for inicio, fim in referencias:
        sufixo = f"{inicio}_{fim}"
        ref = anual.loc[anual.ano.between(inicio, fim)].groupby("codigo_ibge")["precip_mm_anual"].agg(
            media="mean", desvio="std", count="count")
        ref.loc[ref["count"].ne(fim - inicio + 1), ["media", "desvio"]] = np.nan
        ref = ref.rename(columns={c: f"{c}_{sufixo}" for c in ref}).reset_index()
        anual = anual.merge(ref, on="codigo_ibge", how="left", validate="many_to_one")
        anomalia = f"precip_anomaly_{sufixo}"
        anual[anomalia] = anual.precip_mm_anual - anual[f"media_{sufixo}"]
        anual[f"precip_zscore_{sufixo}"] = anual[anomalia] / anual[f"desvio_{sufixo}"].where(anual[f"desvio_{sufixo}"] > 0)
        anual[f"precip_deficit_{sufixo}"] = (-anual[anomalia]).clip(lower=0)
        anual[f"precip_excess_{sufixo}"] = anual[anomalia].clip(lower=0)
    anual = anual.loc[anual.ano.between(ano_inicial, ano_final)].reset_index(drop=True)
    return _metadados(anual, meses_minimos=12, limiar_fracao_pixels=limiar_fracao_pixels,
        referencia_principal="1981-2000: baseline histórico de 20 anos anterior ao painel, não normal climatológica de 30 anos",
        alternativas=["1981-2010", "1991-2020"], cobertura_referencia="todos os anos completos; std(ddof=1)>0 para z",
        interpretacao="Chuva realizada no ano; anomalia não é balanço hídrico nem necessariamente informação esperada.")


def criar_interacoes(precos, pam=None, gaez=None, ano_inicial=2001, ano_final=2024):
    """Cenários alternativos de preço anterior × capacidade, sem promessa causal."""
    capacidades = []
    for tabela in (pam, gaez):
        if tabela is not None:
            capacidades.append(tabela.copy())
    if not capacidades:
        raise ValueError("Fornecer pelo menos uma tabela de capacidade.")
    capacidade = pd.concat(capacidades, ignore_index=True)
    chaves = ["codigo_ibge", "produto", "cenario_capacidade"]
    _chave(capacidade, chaves)
    valores = ["preco_nominal_media_anual_lag1", "preco_real_usd2024_media_anual_lag1",
               "ln_preco_nominal_media_anual_lag1", "ln_preco_real_usd2024_media_anual_lag1",
               "dln_preco_nominal_media_anual_lag1", "dln_preco_real_usd2024_media_anual_lag1"]
    precos_uso = precos.loc[precos.ano.between(ano_inicial, ano_final), ["produto", "ano"] + valores].copy()
    _chave(precos_uso, ["produto", "ano"])
    # Produto é a chave comum; o cruzamento município×ano é deliberado, por cenário.
    out = capacidade.merge(precos_uso, on="produto", how="inner", validate="many_to_many")
    _chave(out, ["codigo_ibge", "ano", "produto", "cenario_capacidade"])
    for coluna in valores:
        out[f"interacao_{coluna}_capacidade_z"] = out[coluna] * out.capacidade_z
    out["flag_interacao_real_ausente"] = out["interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z"].isna()
    return _metadados(out, janela_preco="ano civil t-1; dln_lag1 compara t-1 com t-2", capacidade="fixa por município/produto/cenário",
        interpretacao="Interações candidatas de heterogeneidade, não receita, margem, instrumento validado ou efeito causal.",
        cenarios="PAM e cada raster GAEZ são alternativas separadas; não seleção por significância")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obter-deflatores", type=Path, required=True, help="Diretório de novos insumos brutos; cache não é sobrescrito.")
    args = parser.parse_args()
    print(json.dumps(obter_deflatores(args.obter_deflatores), ensure_ascii=False, indent=2))
