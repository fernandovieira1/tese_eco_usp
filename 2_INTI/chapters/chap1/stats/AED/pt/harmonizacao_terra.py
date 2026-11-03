"""Estoques, lotação e conversão: funções puras, sem alterar os dados de entrada.

As classes seguem a legenda da Coleção 10.1 e o conjunto de vegetação nativa
já usado no projeto. Estoques não permitem recuperar as transições de Y.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


CHAVES = ["codigo_ibge", "ano"]
NATIVAS = frozenset({3, 4, 5, 6, 49, 11, 12, 50})
AGRICULTURA = frozenset({39, 20, 40, 62, 41, 46, 47, 35, 48})
PASTAGEM = frozenset({15})
PAIS = frozenset({1, 10, 14, 18, 19, 36, 22, 26})
FOLHAS = NATIVAS | AGRICULTURA | PASTAGEM | {9, 21, 23, 24, 30, 75, 25, 29, 32, 33, 31, 27}
LEGENDA_URL = "https://doi.org/10.58053/MapBiomas/SJZOLT"


def _base(df, chaves=CHAVES):
    out = df.copy()
    if "codigo_ibge" in chaves:
        out["codigo_ibge"] = out["codigo_ibge"].astype("string").str.replace(r"\.0$", "", regex=True)
        if not out["codigo_ibge"].str.fullmatch(r"\d{7}").fillna(False).all():
            raise ValueError("Código municipal ausente ou diferente de sete dígitos.")
    if "ano" in chaves:
        ano = pd.to_numeric(out["ano"], errors="raise")
        if ano.isna().any() or not np.equal(ano, np.floor(ano)).all():
            raise ValueError("Ano ausente ou não inteiro.")
        out["ano"] = ano.astype(int)
    if out[chaves].isna().any().any() or out.duplicated(chaves).any():
        raise ValueError(f"Chave ausente ou repetida: {chaves}.")
    return out


def _municipios(municipios):
    if isinstance(municipios, pd.DataFrame):
        out = municipios.copy()
    else:
        values = list(municipios)
        out = pd.DataFrame(values) if values and isinstance(values[0], dict) else pd.DataFrame({"codigo_ibge": values})
    return _base(out, ["codigo_ibge"])


def _nao_negativo(serie, nome, permite_na=True):
    values = pd.to_numeric(serie, errors="raise")
    if (not permite_na and values.isna().any()) or (values.dropna() < 0).any() or np.isinf(values.dropna()).any():
        raise ValueError(f"{nome}: valor ausente, negativo ou infinito incompatível.")
    return values


def defasar_ano_exato(base, colunas, n=1):
    """Busca o ano t-n; uma lacuna nunca transforma t-2 em t-1."""
    out = _base(base)
    if not isinstance(n, int) or n < 1:
        raise ValueError("A defasagem deve ser um inteiro positivo.")
    lag = out[CHAVES + list(colunas)].copy()
    lag["ano"] += n
    lag = lag.rename(columns={c: f"{c}_lag{n}" for c in colunas})
    return out.merge(lag, on=CHAVES, how="left", validate="one_to_one")


def construir_usos(classes, municipios, ano_inicio=2001, ano_fim=2024, ano_referencia=2000):
    """Soma folhas disjuntas e verifica a grade histórica antes da agregação.

    classes: codigo_ibge, ano, biome, class_id, area_ha, incluindo a história
    anterior ao painel. A grade esperada conserva cada par bioma/classe que
    existe na história do município. Não prova que uma classe jamais registrada
    tem área zero: os resultados conservam essa limitação em flags e attrs.
    """
    ref = _municipios(municipios)
    keys = CHAVES + ["biome", "class_id"]
    src = _base(classes, keys)
    src["class_id"] = pd.to_numeric(src["class_id"], errors="raise")
    if not np.equal(src.class_id, np.floor(src.class_id)).all():
        raise ValueError("class_id deve ser inteiro.")
    src["class_id"] = src["class_id"].astype(int)
    if src.duplicated(keys).any():
        raise ValueError("Classes repetidas depois da conversão dos códigos para inteiro.")
    if set(src.class_id) & PAIS:
        raise ValueError("A tabela contém classes agregadas; não somar pais e filhos.")
    unknown = set(src.class_id) - FOLHAS - {0, 13}
    if unknown:
        raise ValueError(f"Classes sem tratamento explícito: {sorted(unknown)}")
    src["area_ha"] = _nao_negativo(src.area_ha, "Área")
    if not set(src.codigo_ibge) <= set(ref.codigo_ibge):
        raise ValueError("Há municípios fora da referência; harmonizar antes da soma.")
    expected = src[["codigo_ibge", "biome", "class_id"]].drop_duplicates().groupby("codigo_ibge").size()
    counts = src.groupby(CHAVES).agg(n_linhas_fonte=("area_ha", "size"), n_areas_validas=("area_ha", "count"))
    counts["n_linhas_esperadas"] = counts.index.get_level_values(0).map(expected)
    counts["grade_fonte_completa"] = counts.n_linhas_fonte.eq(counts.n_linhas_esperadas) & counts.n_areas_validas.eq(counts.n_linhas_esperadas)
    sums = src.groupby(CHAVES).area_ha.sum(min_count=1).rename("area_mapeada_ha").to_frame()
    sums = sums.join(counts)
    for name, ids in {"nativa_ha": NATIVAS, "agricultura_ha": AGRICULTURA, "pastagem_ha": PASTAGEM}.items():
        group = src.loc[src.class_id.isin(ids)].groupby(CHAVES).area_ha
        # Sem qualquer linha de um uso, sua área fica ausente: não inventar zero.
        sums[name] = group.sum(min_count=1)
        sums[f"n_linhas_{name}"] = group.size().reindex(sums.index, fill_value=0)
    for name, ids in {"area_nao_observada_ha": {0, 27}, "area_classe_residual_13_ha": {13}}.items():
        group = src.loc[src.class_id.isin(ids)].groupby(CHAVES).area_ha.sum(min_count=1)
        # Estas colunas são parcelas do total registrado, não uma imputação de uso.
        sums[name] = group.reindex(sums.index, fill_value=0)
    sums["area_valida_ha"] = sums.area_mapeada_ha - sums.area_nao_observada_ha - sums.area_classe_residual_13_ha
    values = ["area_mapeada_ha", "nativa_ha", "agricultura_ha", "pastagem_ha", "area_valida_ha"]
    sums.loc[~sums.grade_fonte_completa, values] = np.nan
    out = sums.reset_index()
    # A área de 2000 fornece um denominador territorial fixo, anterior ao painel.
    fixed = out.loc[out.ano.eq(ano_referencia), ["codigo_ibge", "area_mapeada_ha"]].rename(columns={"area_mapeada_ha": "area_referencia_ha"})
    out = out.merge(fixed, on="codigo_ibge", how="left", validate="many_to_one")
    for uso in ["nativa", "agricultura", "pastagem"]:
        out[f"{uso}_share"] = out[f"{uso}_ha"] / out.area_referencia_ha.where(out.area_referencia_ha.gt(0))
    out["fracao_mapeada_referencia"] = out.area_mapeada_ha / out.area_referencia_ha.where(out.area_referencia_ha.gt(0))
    out["flag_area_mapeada_variavel"] = ~np.isclose(out.area_mapeada_ha, out.area_referencia_ha, rtol=1e-5, atol=1e-4, equal_nan=False)
    lag_cols = ["nativa_ha", "agricultura_ha", "pastagem_ha", "nativa_share", "agricultura_share", "pastagem_share"]
    out = defasar_ano_exato(out, lag_cols)
    grid = pd.MultiIndex.from_product([ref.codigo_ibge, range(ano_inicio, ano_fim + 1)], names=CHAVES).to_frame(index=False)
    out = grid.merge(out, on=CHAVES, how="left", validate="one_to_one")
    out["grade_fonte_completa"] = out.grade_fonte_completa.eq(True)
    out["flag_sem_registro_uso"] = out.n_linhas_fonte.isna()
    out["flag_classe_residual_13"] = out.area_classe_residual_13_ha.gt(0)
    out["flag_area_nao_observada"] = out.area_nao_observada_ha.gt(0)
    out["completude_classes_fora_grade_certificada"] = False
    out["geografia_historica_validada"] = False
    out["ano_referencia_area"] = ano_referencia
    out.attrs = {"fontes": [LEGENDA_URL], "classes_nativas": sorted(NATIVAS), "classes_agricultura": sorted(AGRICULTURA),
                 "classes_pastagem": [15], "unidade_area": "ha", "unidade_share": "proporcao",
                 "pendencias": ["Tabela municipal da fonte: correspondência geométrica histórica não certificada pela igualdade de códigos.",
                    "Grade de bioma/classe congelada na história disponível; classes nunca registradas não têm zero certificado.",
                    "Classe residual 13 preservada separadamente, sem alterar o conjunto nativo candidato existente."]}
    return out


def construir_lotacao(rebanho, usos):
    """Cabeças por hectare de pastagem, preservando zeros/ausências distintos."""
    herd = _base(rebanho)
    herd["efetivo_bovino"] = _nao_negativo(herd.efetivo_bovino, "Rebanho")
    land = _base(usos)
    land["pastagem_ha"] = _nao_negativo(land.pastagem_ha, "Pastagem")
    out = land.merge(herd[CHAVES + ["efetivo_bovino"]], on=CHAVES, how="left", validate="one_to_one")
    out["lotacao_cabecas_ha"] = out.efetivo_bovino / out.pastagem_ha.where(out.pastagem_ha.gt(0))
    out["flag_pastagem_zero"] = out.pastagem_ha.eq(0)
    out["flag_rebanho_ausente"] = out.efetivo_bovino.isna()
    out["flag_pastagem_ausente"] = out.pastagem_ha.isna()
    out["flag_bovinos_sem_pastagem"] = out.efetivo_bovino.gt(0) & out.pastagem_ha.eq(0)
    out["compatibilidade_datas_estoques_validada"] = False
    out.attrs = dict(usos.attrs)
    out.attrs["interpretacao_lotacao"] = "Lotação aparente, não produtividade de carne nem lucro; datas e territórios devem ser compatíveis."
    return out


def construir_transicoes(transicoes, cobertura, tolerancia_ha=1e-4):
    """Converte matriz REAL de transições em hectares por destino.

    Exige todas as transições observadas (inclusive permanências), com áreas em
    ha. cobertura registra a máscara, coleção, malha, área válida do par, área
    nativa inicial da MESMA máscara e cobertura_completa. Somente um par completo
    autoriza zero quando não houve transição para determinado destino.
    """
    meta = ["colecao", "malha", "mascara_id"]
    keys = CHAVES + ["classe_origem", "classe_destino"]
    src = _base(transicoes, keys)
    cov = _base(cobertura)
    for col in meta:
        if col not in src or col not in cov or src[col].isna().any() or cov[col].isna().any():
            raise ValueError(f"Metadado obrigatório ausente: {col}.")
    if not cov.cobertura_completa.isin([True, False]).all():
        raise ValueError("cobertura_completa deve ser booleana explícita.")
    src["area_ha"] = _nao_negativo(src.area_ha, "Transição", permite_na=False)
    for col in ["classe_origem", "classe_destino"]:
        ids = pd.to_numeric(src[col], errors="raise")
        if not np.equal(ids, np.floor(ids)).all() or not set(ids) <= FOLHAS - {27}:
            raise ValueError("Transições devem usar folhas válidas, excluindo não observado.")
        src[col] = ids.astype(int)
    checked = src.merge(cov[CHAVES + meta], on=CHAVES, how="left", suffixes=("", "_ref"), validate="many_to_one")
    if any(not checked[c].eq(checked[c + "_ref"]).all() for c in meta):
        raise ValueError("Coleção, malha ou máscara de transições e denominador divergem.")
    for col in ["nativa_inicial_ha", "area_valida_par_ha"]:
        cov[col] = _nao_negativo(cov[col], col, permite_na=False)
    total = src.groupby(CHAVES).area_ha.sum().reindex(pd.MultiIndex.from_frame(cov[CHAVES]), fill_value=0)
    native = src.loc[src.classe_origem.isin(NATIVAS)].groupby(CHAVES).area_ha.sum().reindex(total.index, fill_value=0)
    if not np.allclose(total.to_numpy(), cov.area_valida_par_ha, rtol=1e-8, atol=tolerancia_ha):
        raise ValueError("Matriz incompleta: soma das transições difere da área válida do par.")
    if not np.allclose(native.to_numpy(), cov.nativa_inicial_ha, rtol=1e-8, atol=tolerancia_ha):
        raise ValueError("Denominador nativo incompatível com as classes de origem.")
    outputs = []
    for destino, ids in [("agricultura", AGRICULTURA), ("pastagem", PASTAGEM)]:
        rows = src.loc[src.classe_origem.isin(NATIVAS) & src.classe_destino.isin(ids)]
        sums = rows.groupby(CHAVES).area_ha.sum().rename("conversao_ha")
        out = cov.merge(sums.reset_index(), on=CHAVES, how="left", validate="one_to_one")
        out["destino"] = destino
        # Zero só depois de conferir a matriz completa e sua área total.
        out["conversao_ha"] = out.conversao_ha.fillna(0).where(out.cobertura_completa)
        outputs.append(out)
    result = pd.concat(outputs, ignore_index=True)
    result.attrs = {"classes_nativas": sorted(NATIVAS), "classes_agricultura": sorted(AGRICULTURA), "fonte_legenda": LEGENDA_URL,
                    "definicao": "Transição direta t-1→t na mesma máscara; não é diferença de estoques."}
    return construir_taxas(result, tolerancia_ha=tolerancia_ha)


def construir_taxas(conversao, tolerancia_ha=1e-4):
    """Taxa em proporção: conversão por destino / vegetação inicial compatível."""
    out = _base(conversao, CHAVES + ["destino"])
    if not set(out.destino) <= {"agricultura", "pastagem"}:
        raise ValueError("Manter agricultura e pastagem separadas.")
    for col in ["conversao_ha", "nativa_inicial_ha"]:
        out[col] = _nao_negativo(out[col], col)
    if out.groupby(CHAVES).nativa_inicial_ha.nunique().gt(1).any():
        raise ValueError("Destinos têm denominadores diferentes.")
    total = out.groupby(CHAVES).conversao_ha.sum(min_count=1)
    den = out.groupby(CHAVES).nativa_inicial_ha.first()
    if total.gt(den + tolerancia_ha).any():
        raise ValueError("Conversão por destinos excede o estoque nativo inicial.")
    out["flag_denominador_zero"] = out.nativa_inicial_ha.eq(0)
    out["flag_denominador_ausente"] = out.nativa_inicial_ha.isna()
    out["taxa_conversao"] = out.conversao_ha / out.nativa_inicial_ha.where(out.nativa_inicial_ha.gt(0))
    if "cobertura_completa" in out:
        out.loc[~out.cobertura_completa.eq(True), ["conversao_ha", "taxa_conversao"]] = np.nan
    out.attrs = dict(conversao.attrs)
    return out
