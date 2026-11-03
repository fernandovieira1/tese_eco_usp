"""Medidas administrativas IBAMA: funções puras, sem leitura ou gravação.

``construir_instituicoes`` recebe os eventos originais, a associação espacial
reextraída na malha 2023 e o cadastro de municípios. Retorna tabelas nomeadas;
cada DataFrame traz o contrato e as ressalvas em ``attrs['metadados']``.

Flora inclui, por exemplo, transporte florestal. A seleção desmatamento usa
somente a categoria estruturada INFRACAO_AREA. As seleções se sobrepõem e não
devem ser somadas. Nenhuma delas mede eficácia ou esforço de fiscalização.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import unicodedata

import numpy as np
import pandas as pd


TEMAS = {
    "flora": {
        "campo": "TIPO_INFRACAO",
        "categorias": ("flora",),
        "interpretacao": "Autos classificados como Flora; inclui atividades além da conversão.",
    },
    "desmatamento": {
        "campo": "INFRACAO_AREA",
        "categorias": ("desmatamento", "desmatamento e queimada"),
        "interpretacao": "Autos com categoria de área Desmatamento ou Desmatamento e Queimada.",
    },
}

RESSALVAS = [
    "Contagens de autos registrados, não de infrações ocorridas nem de esforço/eficácia de fiscalização.",
    "Datas anuais são de lavratura; data do fato e status atual não filtram a série.",
    "Flora e desmatamento são seleções alternativas que podem se sobrepor; não somar.",
    "Município-ano sem registro não recebe zero. Zero temático exige registros com campo temático completo.",
    "Positivos com tema incompleto são limites inferiores observados e permanecem sinalizados.",
    "Status/cancelamento atual não reconstrói a situação no ano da lavratura.",
    "Código informado e coordenadas são associações alternativas dos mesmos eventos.",
    "Defasagens exatas organizam o tempo, mas não eliminam endogeneidade nem provam precedência causal.",
]


def _exigir(base: pd.DataFrame, colunas: Iterable[str]) -> None:
    faltam = sorted(set(colunas) - set(base.columns))
    if faltam:
        raise ValueError(f"Colunas obrigatórias ausentes: {faltam}")


def _texto(serie: pd.Series) -> pd.Series:
    return serie.astype("string").str.strip().replace("", pd.NA)


def _normalizar(serie: pd.Series) -> pd.Series:
    def normalizar_valor(valor):
        if pd.isna(valor):
            return pd.NA
        valor = unicodedata.normalize("NFKD", str(valor))
        return " ".join("".join(c for c in valor if not unicodedata.combining(c)).casefold().split())
    return _texto(serie).map(normalizar_valor).astype("string")


def _codigos(serie: pd.Series) -> pd.Series:
    # Não inferir município de origem nem completar códigos de seis dígitos.
    return _texto(serie).str.replace(r"\.0$", "", regex=True)


def _datas(serie: pd.Series) -> pd.Series:
    return pd.to_datetime(serie, errors="coerce", format="mixed")


def _referencia(municipios: pd.DataFrame | Iterable[str]) -> set[str]:
    serie = municipios["codigo_ibge"] if isinstance(municipios, pd.DataFrame) else pd.Series(list(municipios))
    valores = _codigos(serie)
    if valores.isna().any() or valores.duplicated().any() or not valores.str.fullmatch(r"\d{7}").all():
        raise ValueError("Cadastro territorial deve ter códigos únicos de sete dígitos, sem ausências.")
    if "5101837" in set(valores):
        raise ValueError("Boa Esperança do Norte não pertence à referência de 141 municípios de 2023.")
    return set(valores)


def _metadados(tabela: pd.DataFrame, metadados: dict) -> pd.DataFrame:
    tabela.attrs["metadados"] = metadados
    return tabela


def preparar_autos(
    eventos: pd.DataFrame,
    geocodificacao: pd.DataFrame,
    municipios_referencia: pd.DataFrame | Iterable[str],
) -> pd.DataFrame:
    """Valida identidades e associações; preserva ausências e status atuais.

    Linhas totalmente idênticas podem ser retiradas. Identidades repetidas com
    conteúdo conflitante interrompem a execução. IDs ausentes continuam apenas
    nos diagnósticos, nunca são contados como se fossem autos identificados.
    """
    _exigir(eventos, ["SEQ_AUTO_INFRACAO", "DAT_HORA_AUTO_INFRACAO", "codigo_ibge",
                     "TIPO_INFRACAO", "INFRACAO_AREA"])
    _exigir(geocodificacao, ["SEQ_AUTO_INFRACAO", "codigo_ibge_espacial", "geografia_referencia"])
    codigos_validos = _referencia(municipios_referencia)
    if not geocodificacao["geografia_referencia"].eq("IBGE_2023_141").all():
        raise ValueError("Usar geocodificação reextraída em IBGE_2023_141, não a malha de 142 municípios.")
    base = eventos.drop_duplicates().copy()
    base["SEQ_AUTO_INFRACAO"] = _texto(base["SEQ_AUTO_INFRACAO"])
    ids = base.loc[base["SEQ_AUTO_INFRACAO"].notna(), "SEQ_AUTO_INFRACAO"]
    if ids.duplicated().any():
        raise ValueError("Um ID de auto tem linhas conflitantes; resolver antes da contagem.")
    base["data_lavratura"] = _datas(base["DAT_HORA_AUTO_INFRACAO"])
    base["ano"] = base["data_lavratura"].dt.year.astype("Int64")
    base["mes_lavratura"] = base["data_lavratura"].dt.to_period("M").dt.to_timestamp()
    base["codigo_ibge_informado"] = _codigos(base["codigo_ibge"])
    base["flag_codigo_informado_valido"] = base["codigo_ibge_informado"].isin(codigos_validos)
    geo = geocodificacao[["SEQ_AUTO_INFRACAO", "codigo_ibge_espacial"]].copy()
    geo["SEQ_AUTO_INFRACAO"] = _texto(geo["SEQ_AUTO_INFRACAO"])
    geo["codigo_ibge_espacial"] = _codigos(geo["codigo_ibge_espacial"])
    geo = geo.loc[geo["SEQ_AUTO_INFRACAO"].notna()].drop_duplicates()
    if geo["SEQ_AUTO_INFRACAO"].duplicated().any():
        raise ValueError("Um auto tem associações espaciais conflitantes.")
    # Somente o ID é chave: códigos e anos da tabela auxiliar não substituem a fonte.
    base = base.drop(columns=["codigo_ibge_espacial"], errors="ignore").merge(
        geo, on="SEQ_AUTO_INFRACAO", how="left", validate="many_to_one")
    base["flag_codigo_espacial_valido"] = base["codigo_ibge_espacial"].isin(codigos_validos)
    for tema, regra in TEMAS.items():
        normal = _normalizar(base[regra["campo"]])
        base[f"tema_{tema}"] = normal.isin(regra["categorias"]).astype("boolean").mask(normal.isna())
    if "valor_multa_nominal" in base:
        valor = pd.to_numeric(base["valor_multa_nominal"], errors="coerce")
    elif "VAL_AUTO_INFRACAO" in base:
        texto = _texto(base["VAL_AUTO_INFRACAO"])
        decimal_virgula = texto.str.contains(",", regex=False, na=False)
        texto = texto.mask(decimal_virgula, texto.str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
        valor = pd.to_numeric(texto, errors="coerce")
    else:
        valor = pd.Series(np.nan, index=base.index)
    base["flag_valor_negativo"] = valor.lt(0).fillna(False)
    base["valor_multa_nominal"] = valor.where(valor.ge(0) & np.isfinite(valor))
    base["flag_id_ausente"] = base["SEQ_AUTO_INFRACAO"].isna()
    base["flag_data_lavratura_ausente"] = base["data_lavratura"].isna()
    base["flag_status_atual_ausente"] = (_texto(base["DS_SIT_AUTO_AIE"]).isna()
                                            if "DS_SIT_AUTO_AIE" in base else True)
    base["flag_data_fato_ausente"] = (_datas(base["DT_FATO_INFRACIONAL"]).isna()
                                         if "DT_FATO_INFRACIONAL" in base else True)
    base["flag_cancelado_atual"] = (_normalizar(base["SIT_CANCELADO"]).eq("s").fillna(False)
                                        if "SIT_CANCELADO" in base else False)
    meta = {
        "fonte": "IBAMA; autos de infração", "data_anual": "DAT_HORA_AUTO_INFRACAO (lavratura)",
        "geografia": "IBGE_2023_141", "n_municipios_referencia": len(codigos_validos),
        "n_linhas_origem": len(eventos), "n_duplicatas_identicas_retiradas": len(eventos) - len(base),
        "n_ids_ausentes": int(base["flag_id_ausente"].sum()),
        "n_datas_lavratura_invalidas": int(base["flag_data_lavratura_ausente"].sum()),
        "selecao_tematica": TEMAS, "filtro_status": "nenhum; informação atual apenas diagnóstica",
        "ressalvas": RESSALVAS,
    }
    return _metadados(base, meta)


def deflacionar_autos(
    autos: pd.DataFrame,
    ipca: pd.DataFrame,
    mes_base: str = "2024-12",
) -> pd.DataFrame:
    """Converte R$ nominais para R$ do mês-base com nível mensal de IPCA.

    ipca deve ter data e indice_precos (nível, não variação percentual). Meses
    sem índice permanecem ausentes. A função não baixa dados nem interpola.
    """
    _exigir(autos, ["data_lavratura", "valor_multa_nominal"])
    _exigir(ipca, ["data", "indice_precos"])
    indice = ipca[["data", "indice_precos"]].copy()
    indice["mes_lavratura"] = _datas(indice["data"]).dt.to_period("M").dt.to_timestamp()
    indice["indice_precos"] = pd.to_numeric(indice["indice_precos"], errors="coerce")
    if (indice["mes_lavratura"].isna().any() or indice["mes_lavratura"].duplicated().any()
            or indice["indice_precos"].isna().any() or not indice["indice_precos"].gt(0).all()
            or not np.isfinite(indice["indice_precos"]).all()):
        raise ValueError("IPCA precisa de meses únicos e níveis positivos, sem ausências.")
    base_mes = pd.Period(mes_base, freq="M").to_timestamp()
    escolhido = indice.loc[indice["mes_lavratura"].eq(base_mes), "indice_precos"]
    if len(escolhido) != 1:
        raise ValueError("Mês-base não encontrado no IPCA.")
    resultado = autos.drop(columns=["indice_precos", "valor_multa_real", "flag_ipca_ausente"], errors="ignore").copy()
    resultado["mes_lavratura"] = _datas(resultado["data_lavratura"]).dt.to_period("M").dt.to_timestamp()
    resultado = resultado.merge(indice[["mes_lavratura", "indice_precos"]], on="mes_lavratura",
                                how="left", validate="many_to_one")
    resultado["flag_ipca_ausente"] = resultado["indice_precos"].isna()
    resultado["valor_multa_real"] = resultado["valor_multa_nominal"] * float(escolhido.iloc[0]) / resultado["indice_precos"]
    return _metadados(resultado, {**autos.attrs.get("metadados", {}), "deflacao": {
        "indice": "IPCA", "moeda": "BRL", "mes_base": str(pd.Period(mes_base, freq="M")),
        "metodo": "valor nominal por auto × índice do mês-base / índice do mês da lavratura",
        "n_eventos_sem_indice": int(resultado["flag_ipca_ausente"].sum()),
    }})


def adicionar_defasagens_calendario(
    tabela: pd.DataFrame,
    colunas: Iterable[str],
    defasagens: Iterable[int] = (1,),
) -> pd.DataFrame:
    """Busca t-k por chave; uma lacuna anual não vira a observação anterior."""
    colunas = list(colunas)
    _exigir(tabela, ["codigo_ibge", "ano", *colunas])
    if tabela[["codigo_ibge", "ano"]].isna().any().any() or tabela.duplicated(["codigo_ibge", "ano"]).any():
        raise ValueError("Defasagens exigem chave município-ano única e completa.")
    resultado = tabela.copy()
    anos = pd.to_numeric(resultado["ano"], errors="coerce")
    if anos.isna().any() or not anos.eq(anos.round()).all():
        raise ValueError("Ano deve ser inteiro.")
    resultado["ano"] = anos.astype("Int64")
    for k in defasagens:
        if not isinstance(k, int) or k < 1:
            raise ValueError("Defasagens devem ser inteiros positivos.")
        novas = {coluna: f"{coluna}_lag{k}" for coluna in colunas}
        if set(novas.values()) & set(resultado.columns):
            raise ValueError("Uma coluna de defasagem já existe; não sobrescrever.")
        anterior = tabela[["codigo_ibge", "ano", *colunas]].copy()
        anterior["ano"] = pd.to_numeric(anterior["ano"], errors="raise").astype("Int64") + k
        resultado = resultado.merge(anterior.rename(columns=novas), on=["codigo_ibge", "ano"],
                                    how="left", validate="one_to_one")
    return _metadados(resultado, {**tabela.attrs.get("metadados", {}), "defasagens": "correspondência exata de ano"})


def _agregar_associacao(autos: pd.DataFrame, associacao: str) -> pd.DataFrame:
    codigo = "codigo_ibge_informado" if associacao == "informada" else "codigo_ibge_espacial"
    flag = "flag_codigo_informado_valido" if associacao == "informada" else "flag_codigo_espacial_valido"
    uso = autos.loc[~autos["flag_data_lavratura_ausente"] & autos[flag]].copy()
    linhas = []
    for (municipio, ano), registros in uso.groupby([codigo, "ano"], observed=True, sort=True):
        grupo = registros.loc[~registros["flag_id_ausente"]]
        # Registros sem ID não têm identidade suficiente para uma contagem.
        sem_id = int(registros["flag_id_ausente"].sum())
        if grupo.empty:
            continue
        linha = {"codigo_ibge": municipio, "ano": int(ano), "n_autos_observados": len(grupo),
                 "n_registros_sem_id": sem_id,
                 "n_tipo_ausente": int(grupo["tema_flora"].isna().sum()),
                 "n_area_tema_ausente": int(grupo["tema_desmatamento"].isna().sum()),
                 "n_status_atual_ausente": int(grupo["flag_status_atual_ausente"].sum()),
                 "n_cancelados_atuais": int(grupo["flag_cancelado_atual"].sum())}
        for tema in TEMAS:
            predicado = grupo[f"tema_{tema}"]
            selecionados = grupo.loc[predicado.fillna(False)]
            n = len(selecionados)
            parcial = bool(predicado.isna().any() or sem_id > 0)
            # Zero só significa nenhum auto desse tema entre registros classificados.
            contagem = pd.NA if n == 0 and parcial else n
            linha[f"n_autos_{tema}"] = contagem
            linha[f"flag_contagem_{tema}_parcial"] = parcial
            for medida, coluna in [("nominais", "valor_multa_nominal"), ("reais", "valor_multa_real")]:
                valores = selecionados[coluna]
                if n == 0:
                    valor = np.nan if parcial or (medida == "reais" and not autos.attrs.get("metadados", {}).get("deflacao")) else 0.0
                else:
                    valor = valores.sum(min_count=1)
                linha[f"multas_{tema}_{medida}_observadas"] = valor
                linha[f"n_{tema}_valores_{medida}_ausentes"] = int(valores.isna().sum())
            linha[f"flag_soma_{tema}_parcial"] = bool(parcial or selecionados["valor_multa_real"].isna().any()
                                                       or not autos.attrs.get("metadados", {}).get("deflacao"))
            linha[f"flag_soma_nominal_{tema}_parcial"] = bool(parcial or selecionados["valor_multa_nominal"].isna().any())
        linhas.append(linha)
    colunas_minimas = ["codigo_ibge", "ano", "n_autos_observados", "n_registros_sem_id", "n_tipo_ausente", "n_area_tema_ausente",
                       "n_status_atual_ausente", "n_cancelados_atuais"]
    for tema in TEMAS:
        colunas_minimas += [f"n_autos_{tema}", f"flag_contagem_{tema}_parcial",
                           f"multas_{tema}_nominais_observadas", f"n_{tema}_valores_nominais_ausentes",
                           f"multas_{tema}_reais_observadas", f"n_{tema}_valores_reais_ausentes",
                           f"flag_soma_{tema}_parcial", f"flag_soma_nominal_{tema}_parcial"]
    saida = pd.DataFrame(linhas, columns=colunas_minimas)
    for coluna in saida:
        if coluna == "ano" or coluna.startswith("n_"):
            saida[coluna] = pd.to_numeric(saida[coluna], errors="raise").astype("Int64")
        elif coluna.startswith("flag_"):
            saida[coluna] = saida[coluna].astype("boolean")
        elif coluna.startswith("multas_"):
            saida[coluna] = pd.to_numeric(saida[coluna], errors="raise").astype("Float64")
    return _metadados(saida, {**autos.attrs.get("metadados", {}), "associacao": associacao,
        "unidade_contagens": "autos únicos registrados", "unidade_nominais": "R$ nominais autuados",
        "unidade_reais": "R$ do mês-base do IPCA", "n_ids_geografia_valida": int((~uso["flag_id_ausente"]).sum()),
        "zero_tematico": "zero apenas entre registros identificados de tema conhecido; não certifica completude da fonte",
    })


def _qualidade(autos: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for ano, grupo in autos.loc[autos["ano"].notna()].groupby("ano", observed=True, sort=True):
        id_valido = ~grupo["flag_id_ausente"]
        comparaveis = id_valido & grupo["flag_codigo_informado_valido"] & grupo["flag_codigo_espacial_valido"]
        divergentes = comparaveis & grupo["codigo_ibge_informado"].ne(grupo["codigo_ibge_espacial"]).fillna(False)
        n_comp = int(comparaveis.sum())
        n_identificados = int(id_valido.sum())
        n_sem_espacial = int((id_valido & ~grupo["flag_codigo_espacial_valido"]).sum())
        linhas.append({"ano": int(ano), "n_registros": len(grupo), "n_ids_ausentes": int((~id_valido).sum()),
                       "n_ids_com_codigo_informado_valido": int((id_valido & grupo["flag_codigo_informado_valido"]).sum()),
                       "n_ids_com_espacial_valido": int((id_valido & grupo["flag_codigo_espacial_valido"]).sum()),
                       "n_ids_sem_espacial_valido": n_sem_espacial,
                       "fracao_sem_associacao_espacial": n_sem_espacial / n_identificados if n_identificados else np.nan,
                       "n_comparaveis": n_comp, "n_divergentes": int(divergentes.sum()),
                       "taxa_divergencia": int(divergentes.sum()) / n_comp if n_comp else np.nan,
                       "n_tipo_ausente": int(grupo["tema_flora"].isna().sum()),
                       "n_area_tema_ausente": int(grupo["tema_desmatamento"].isna().sum()),
                       "fracao_tipo_preenchido": float(grupo["tema_flora"].notna().mean()),
                       "fracao_area_tema_preenchido": float(grupo["tema_desmatamento"].notna().mean()),
                       "n_status_atual_ausente": int(grupo["flag_status_atual_ausente"].sum()),
                       "n_data_fato_ausente": int(grupo["flag_data_fato_ausente"].sum())})
    return _metadados(pd.DataFrame(linhas), {"papel": "qualidade da mensuração, não regressor institucional independente",
                                           "ressalvas": RESSALVAS})


def diagnosticar_pendencias(
    historico_embargos: pd.DataFrame | None = None,
    coordenadas_embargos: pd.DataFrame | None = None,
    custos: Mapping[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """Manifesto de bloqueios; perfis opcionais não viram medidas finais."""
    linhas = [{"candidato": "x3e_infracoes", "situacao": "adiado",
               "motivo": "Reconstruir identidade, data original, trajetória de status e localização; validar unidade de área e sobreposição.",
               "medida_final_construida": False, "n_linhas": pd.NA, "n_ids_distintos_cadastrados": pd.NA,
               "n_ids_datas_embargo_conflitantes": pd.NA, "n_linhas_coordenadas": pd.NA}]
    if historico_embargos is not None:
        _exigir(historico_embargos, ["SEQ_TAD", "DAT_EMBARGO"])
        h = historico_embargos.copy()
        h["SEQ_TAD"] = _texto(h["SEQ_TAD"])
        h["data_embargo_diagnostico"] = _datas(h["DAT_EMBARGO"])
        conflitos = h.groupby("SEQ_TAD", observed=True)["data_embargo_diagnostico"].nunique()
        linhas[0].update(n_linhas=len(h), n_ids_distintos_cadastrados=int(h["SEQ_TAD"].nunique()),
                         n_ids_datas_embargo_conflitantes=int(conflitos.gt(1).sum()))
    if coordenadas_embargos is not None:
        linhas[0]["n_linhas_coordenadas"] = len(coordenadas_embargos)
    for nome in ("x7_custo-soja", "x7_custo-milho-s1", "x7_custo-milho-s2"):
        tabela = (custos or {}).get(nome)
        linhas.append({"candidato": nome, "situacao": "adiado", "medida_final_construida": False,
                       "motivo": "Validar célula, unidade, moeda, local, tecnologia, categoria e safra; não extrapolar custos locais a todos os municípios.",
                       "n_linhas": len(tabela) if tabela is not None else pd.NA,
                       "n_ids_distintos_cadastrados": pd.NA, "n_ids_datas_embargo_conflitantes": pd.NA,
                       "n_linhas_coordenadas": pd.NA})
    return _metadados(pd.DataFrame(linhas), {"papel": "manifesto de pendências; contagem de linhas/IDs é apenas diagnóstico"})


def construir_instituicoes(
    eventos: pd.DataFrame,
    geocodificacao: pd.DataFrame,
    municipios_referencia: pd.DataFrame | Iterable[str],
    *,
    ipca: pd.DataFrame | None = None,
    mes_base: str = "2024-12",
    ano_inicio: int = 2001,
    ano_fim: int = 2024,
) -> dict[str, pd.DataFrame]:
    """Interface do fluxo: agrega dados reais e devolve cinco tabelas.

    Informada e espacial contêm a grade município-ano, conservando NA quando
    não há autos identificados. Completar chaves não completa dados. As lags1 são
    construídas com toda a história disponível ANTES do corte 2001–2024.
    Ausência de IPCA permite contagens e valores nominais, mas não valores reais.
    """
    if ano_inicio > ano_fim:
        raise ValueError("Intervalo de anos inválido.")
    codigos_referencia = sorted(_referencia(municipios_referencia))
    autos = preparar_autos(eventos, geocodificacao, codigos_referencia)
    if ipca is not None:
        autos = deflacionar_autos(autos, ipca, mes_base)
    else:
        autos["valor_multa_real"] = np.nan
        autos["flag_ipca_ausente"] = True
    tabelas = {}
    colunas_lag = ["n_autos_flora", "n_autos_desmatamento",
                   "multas_flora_reais_observadas", "multas_desmatamento_reais_observadas",
                   "flag_contagem_flora_parcial", "flag_contagem_desmatamento_parcial",
                   "flag_soma_flora_parcial", "flag_soma_desmatamento_parcial"]
    for associacao in ("informada", "espacial"):
        historico = _agregar_associacao(autos, associacao)
        # Incluir o ano auxiliar preserva lag1 mesmo sem registro no ano corrente.
        grade = pd.MultiIndex.from_product(
            [codigos_referencia, range(ano_inicio - 1, ano_fim + 1)],
            names=["codigo_ibge", "ano"]).to_frame(index=False)
        tabela = grade.merge(historico, on=["codigo_ibge", "ano"], how="left", validate="one_to_one")
        tabela.attrs["metadados"] = historico.attrs["metadados"]
        tabela["flag_sem_registro_identificado"] = tabela["n_autos_observados"].isna()
        tabela = adicionar_defasagens_calendario(tabela, colunas_lag)
        tabela = tabela.loc[tabela["ano"].between(ano_inicio, ano_fim)].reset_index(drop=True)
        tabela.attrs["metadados"]["periodo_saida"] = [ano_inicio, ano_fim]
        tabelas[f"instituicoes_{associacao}"] = tabela
    qualidade = _qualidade(autos)
    if "ano" in qualidade:
        qualidade = qualidade.loc[qualidade["ano"].between(ano_inicio, ano_fim)].reset_index(drop=True)
    tabelas["qualidade_geocodificacao"] = qualidade
    perfil = autos.loc[autos["ano"].between(ano_inicio, ano_fim)].copy()
    perfil["tipo_diagnostico"] = _texto(perfil["TIPO_INFRACAO"]).fillna("<ausente>")
    perfil["area_diagnostico"] = _texto(perfil["INFRACAO_AREA"]).fillna("<ausente>")
    perfil = (perfil.groupby(["ano", "tipo_diagnostico", "area_diagnostico"], observed=True, dropna=False)
              .agg(n_registros=("SEQ_AUTO_INFRACAO", "size"), n_ids_validos=("SEQ_AUTO_INFRACAO", "count"))
              .reset_index())
    tabelas["perfil_temas"] = _metadados(perfil, {"papel": "cobertura dos campos estruturados, incluindo IDs ausentes",
                                                 "selecao_tematica": TEMAS})
    tabelas["pendencias_instituicoes"] = diagnosticar_pendencias()
    return tabelas
