"""Células de tratamentos finais; decisões científicas continuam explícitas."""

from textwrap import dedent


_COMMON = '''
# `features` guarda uma tabela candidata em memória; os CSVs não são alterados.
features = None

def recorte_2001_2024(base):
    if "ano" not in base.columns:
        return base.copy()
    return base.loc[pd.to_numeric(base["ano"], errors="coerce").between(2001, 2024)].copy()

def abrir_colunas(base, indice, categoria, valor):
    # pivot exige uma medida por chave; não calcula médias para esconder duplicatas.
    chave = indice + [categoria]
    if base[chave].isna().any().any() or base.duplicated(chave).any():
        print("Pivô pendente: resolver chaves ausentes ou duplicadas:", chave)
        return None
    assert_unique(base, chave)
    return base.pivot(index=indice, columns=categoria, values=valor).reset_index()

def deflacionar(base, indice, coluna_valor, chaves, indice_base):
    # indice deve conter `indice_precos`, positivo, na frequência e moeda corretas.
    # indice_base é o nível do índice na data-base escolhida (não presumir 100).
    if indice_base <= 0:
        raise ValueError("O índice da data-base deve ser positivo.")
    assert_unique(indice, chaves)
    out = base.merge(indice[chaves + ["indice_precos"]], on=chaves,
                     how="left", validate="many_to_one")
    out[coluna_valor + "_real"] = (
        out[coluna_valor] * indice_base / out["indice_precos"].where(out["indice_precos"] > 0)
    )
    return out
'''


_TRANSITIONS = '''
def construir_conversao(transicoes, classes_nativas, mapa_destinos):
    # Insumo futuro: transições reais entre duas datas, na mesma máscara espacial.
    # classe_origem/destino: IDs da legenda; area_ha: área que mudou de classe.
    # mapa_destinos: {ID: "agricultura" ou "pastagem"}; categorias não sobrepostas.
    if not classes_nativas or not mapa_destinos:
        raise ValueError("Conferir classes nativas e destinos na legenda da coleção.")
    if not set(mapa_destinos.values()) <= {"agricultura", "pastagem"}:
        raise ValueError("Manter os destinos agricultura e pastagem separados.")
    chaves = ["codigo_ibge", "ano"] + (["biome"] if "biome" in transicoes else [])
    obrigatorias = chaves + ["classe_origem", "classe_destino", "area_ha"]
    if transicoes[obrigatorias].isna().any().any():
        raise ValueError("Validar chaves e áreas ausentes antes da soma.")
    if (transicoes["area_ha"] < 0).any():
        raise ValueError("Área de transição negativa.")
    assert_unique(transicoes, chaves + ["classe_origem", "classe_destino"])
    uso = transicoes.loc[
        transicoes["classe_origem"].isin(classes_nativas)
        & transicoes["classe_destino"].isin(mapa_destinos)
    ].copy()
    uso["destino"] = uso["classe_destino"].map(mapa_destinos)
    # Uma classe de destino pertence a somente um destino.
    return (uso.groupby(chaves + ["destino"], observed=True)["area_ha"]
            .sum(min_count=1).rename("area_conv_ha").reset_index())

TRANSICOES_VALIDADAS = None  # DataFrame de transições; estoques não substituem esse insumo.
CLASSES_NATIVAS = None      # Lista definida pela legenda oficial.
MAPA_DESTINOS = None        # Dicionário com agricultura e pastagem separadas.
if TRANSICOES_VALIDADAS is not None and CLASSES_NATIVAS and MAPA_DESTINOS:
    conversao = construir_conversao(TRANSICOES_VALIDADAS, CLASSES_NATIVAS, MAPA_DESTINOS)
    indice = ["codigo_ibge", "ano"] + (["biome"] if "biome" in conversao else [])
    features = abrir_colunas(recorte_2001_2024(conversao), indice, "destino", "area_conv_ha")
    display(features.head() if features is not None else "Pivô pendente.")
else:
    print("Esqueleto inicial da AED. A seção Passos 1 e 2 abaixo executa a construção com as transições disponíveis.")
    print("Diferença entre estoques não mede conversão bruta; destinos ficam separados.")
'''


_RATE = '''
def construir_taxas(conversao_municipal, denominador, compatibilidade_validada=False):
    # Numerador: uma linha por município, ano e destino; area_conv_ha em hectares.
    # Denominador: vegetação no início do período, já presente na fonte candidata.
    if not compatibilidade_validada:
        raise ValueError("Validar geografia, datas e máscara das duas medidas.")
    chaves = ["codigo_ibge", "ano"]
    assert_unique(conversao_municipal, chaves + ["destino"])
    assert_unique(denominador, chaves)
    if conversao_municipal[chaves + ["destino"]].isna().any().any():
        raise ValueError("Numerador contém chave ausente.")
    if not set(conversao_municipal["destino"].dropna()) <= {"agricultura", "pastagem"}:
        raise ValueError("Separar os destinos agricultura e pastagem.")
    out = conversao_municipal.merge(
        denominador[chaves + ["native_veg_ha_lag1"]], on=chaves,
        how="left", validate="many_to_one", indicator=True,
    )
    den = out["native_veg_ha_lag1"]
    num = out["area_conv_ha"]
    out["taxa_conv"] = num / den.where(den > 0)
    out["flag_taxa_fora_0_1"] = out["taxa_conv"].notna() & ~out["taxa_conv"].between(0, 1)
    # Não limitar em 1: inconsistências precisam aparecer na conferência.
    out["flag_denominador_nulo"] = den.eq(0)
    out["flag_denominador_ausente"] = den.isna()
    return out

CONVERSAO_MUNICIPAL_VALIDADA = None
COMPATIBILIDADE_VALIDADA = False
if CONVERSAO_MUNICIPAL_VALIDADA is not None and COMPATIBILIDADE_VALIDADA:
    taxas = construir_taxas(CONVERSAO_MUNICIPAL_VALIDADA, df, True)
    display(taxas[["_merge", "flag_denominador_nulo", "flag_taxa_fora_0_1"]].value_counts())
    features = abrir_colunas(recorte_2001_2024(taxas), ["codigo_ibge", "ano"], "destino", "taxa_conv")
    display(features.head() if features is not None else "Pivô pendente.")
else:
    print("Esqueleto inicial: este CSV contém o denominador candidato. A taxa executada está na seção Passos 1 e 2 abaixo.")
    print("Denominador zero mantém a taxa ausente; não vira taxa zero.")
'''


_PRICE = '''
# Média de ano civil é uma descrição candidata; a janela decisória permanece em aberto.
mensal = df.copy()
mensal["data"] = pd.to_datetime(mensal["data"], errors="coerce")
mensal["ano"] = mensal["data"].dt.year.astype("Int64")
mensal["mes"] = mensal["data"].dt.month.astype("Int64")
chave_mensal = ["variavel", "ano", "mes"]
if mensal[chave_mensal].isna().any().any() or mensal.duplicated(chave_mensal).any():
    print("Anualização pendente: revisar datas ou meses duplicados.")
else:
    anual = (mensal.groupby(["variavel", "ano"], observed=True)
             .agg(preco_media_anual=("preco_nominal", "mean"),
                  meses_registrados=("mes", "nunique"),
                  meses_validos=("preco_nominal", "count")).reset_index())
    completa = anual["meses_registrados"].eq(12) & anual["meses_validos"].eq(12)
    anual.loc[~completa, "preco_media_anual"] = np.nan
    # Não somar preços. USD/t e USD/kg seguem em colunas separadas.
    features = abrir_colunas(recorte_2001_2024(anual), ["ano"], "variavel", "preco_media_anual")
    display(anual.loc[~completa].head())
    display(features.head() if features is not None else "Pivô pendente.")

JANELA_ANTERIOR_DECISAO = None  # Definir meses e data de decisão antes de usar defasagens.
INDICE_DEFLATOR = None          # DataFrame por data ou ano, na moeda apropriada.
INDICE_NA_DATA_BASE = None
# Após escolher moeda, índice e data-base: deflacionar(mensal, indice, "preco_nominal", ["data"], nivel).
# Preços comuns são absorvidos por efeitos fixos de ano; exposição local exige escolha própria.
'''


_PAM = '''
# Produto em coluna própria: o hífen do nome do notebook não significa subtração.
features = abrir_colunas(painel, ["codigo_ibge", "ano"], "produto", "rendimento_medio_kg_ha")
display(features.head() if features is not None else "Pivô pendente.")
# Rendimento ausente permanece ausente. Produtividade observada não é capacidade predeterminada.
'''


_HISTORICAL = '''
def produtividade_historica(base, inicio, fim, minimo_anos, geografia_validada=False):
    if not geografia_validada:
        raise ValueError("Conferir códigos e limites no período histórico.")
    if inicio > fim or fim >= 2001 or not 1 <= minimo_anos <= fim - inicio + 1:
        raise ValueError("Usar janela anterior a 2001 e cobertura mínima compatível.")
    assert_unique(base, ["codigo_ibge", "ano", "produto"])
    historico = base.loc[base["ano"].between(inicio, fim)].copy()
    # Não preencher rendimento ausente com zero: não cultivo e ausência são distintos.
    resumo = (historico.groupby(["codigo_ibge", "produto"], observed=True)
              .agg(media_historica_kg_ha=("rendimento_medio_kg_ha", "mean"),
                   anos_validos=("rendimento_medio_kg_ha", "count"),
                   anos_registrados=("ano", "nunique")).reset_index())
    resumo["fracao_anos_validos"] = resumo["anos_validos"] / (fim - inicio + 1)
    resumo.loc[resumo["anos_validos"] < minimo_anos, "media_historica_kg_ha"] = np.nan
    # Inclui municípios/produtos conhecidos sem registro na janela, sem criar valor zero.
    universo = base[["codigo_ibge", "produto"]].drop_duplicates()
    return universo.merge(resumo, how="left", on=["codigo_ibge", "produto"], validate="one_to_one")

JANELA_HISTORICA = None  # Ex.: (ano_inicial, ano_final), com ano_final <= 2000.
MINIMO_ANOS_VALIDOS = None
GEOGRAFIA_HISTORICA_VALIDADA = False
if JANELA_HISTORICA is not None and MINIMO_ANOS_VALIDOS is not None and GEOGRAFIA_HISTORICA_VALIDADA:
    historica = produtividade_historica(df, *JANELA_HISTORICA, MINIMO_ANOS_VALIDOS, True)
    display(historica.head())
    features = abrir_colunas(historica, ["codigo_ibge"], "produto", "media_historica_kg_ha")
else:
    print("Exposição histórica pendente: definir janela, cobertura e geografia.")
    print("Anos anteriores a 2001 estão preservados em df; não preencher rendimento ausente com zero.")
'''


_GAEZ = '''
# Cada raster já identifica produto, insumo e regime; preservar todas as alternativas.
gaez = df.loc[df["variavel_raster"].astype("string").str.startswith("{prefix}", na=False)].copy()
features = abrir_colunas(gaez, ["codigo_ibge"], "variavel_raster", "valor_medio")
display(features.head() if features is not None else "Pivô pendente.")
display(gaez[["variavel_raster", "nivel_insumo", "periodo_climatico", "regime", "unidade"]].drop_duplicates())
# Cenário 1961–1990 e base de terras de 2010 exigem avaliação temporal.
FATOR_CONVERSAO_UMIDADE = None
# yx: kg de matéria seca/ha. sx: índice de 0 a 10.000, sem unidade monetária.
# Comparar yx com PAM exige base de umidade compatível; não converter sx em produtividade.
'''


_AUTOS = '''
# A fonte já tem uma linha por município e ano: não anualizar nem preencher ausências com zero.
colunas = ["codigo_ibge", "ano", "{value}"]
features = painel[colunas].copy()
if features.duplicated(["codigo_ibge", "ano"]).any():
    print("Chave municipal anual duplicada: revisar antes de juntar ao painel.")
    features = None
else:
    assert_unique(features, ["codigo_ibge", "ano"])
    display(features.head())

def comparar_associacoes(informada, espacial):
    chaves = ["codigo_ibge", "ano"]
    assert_unique(informada, chaves)
    assert_unique(espacial, chaves)
    out = informada[chaves + ["n_autos_ibama_it"]].merge(
        espacial[chaves + ["n_autos_ibama_espacial"]], on=chaves,
        how="outer", validate="one_to_one", indicator=True,
    )
    out["diferenca_contagens"] = out["n_autos_ibama_espacial"] - out["n_autos_ibama_it"]
    return out

OUTRA_ASSOCIACAO_TERRITORIAL = None  # Carregar e validar antes de comparar_associacoes(...).
# Não somar agregados informados e espaciais: são associações dos mesmos registros.
# Contagem e valor autuado não medem diretamente efetividade institucional.
'''


_EVENTS = '''
def contar_autos(eventos, coluna_data, tipos, status, cancelamento):
    # Todas as seleções são explícitas; data do fato e lavratura têm significados distintos.
    if coluna_data not in {"DT_FATO_INFRACIONAL", "DAT_HORA_AUTO_INFRACAO"}:
        raise ValueError("Escolher data do fato ou data da lavratura.")
    if eventos["SEQ_AUTO_INFRACAO"].isna().any():
        raise ValueError("Há autos sem identidade: validar antes de contar.")
    assert_unique(eventos, ["SEQ_AUTO_INFRACAO"])
    uso = eventos.loc[
        eventos["TIPO_INFRACAO"].isin(tipos)
        & eventos["DS_SIT_AUTO_AIE"].isin(status)
        & eventos["SIT_CANCELADO"].isin(cancelamento)
    ].copy()
    uso["ano"] = pd.to_datetime(uso[coluna_data], errors="coerce").dt.year.astype("Int64")
    if uso[["codigo_ibge", "ano"]].isna().any().any():
        raise ValueError("A seleção contém autos sem município ou data válidos.")
    return (uso.groupby(["codigo_ibge", "ano"], observed=True)["SEQ_AUTO_INFRACAO"]
            .nunique().rename("n_autos_selecionados").reset_index())

DATA_CONTAGEM = None
TIPOS_PERTINENTES = None
STATUS_PERTINENTES = None
CANCELAMENTO_PERTINENTE = None
if all(x is not None for x in [DATA_CONTAGEM, TIPOS_PERTINENTES, STATUS_PERTINENTES, CANCELAMENTO_PERTINENTE]):
    features = recorte_2001_2024(contar_autos(
        df, DATA_CONTAGEM, TIPOS_PERTINENTES, STATUS_PERTINENTES, CANCELAMENTO_PERTINENTE,
    ))
    display(features.head())
else:
    print("Contagem específica pendente: validar IDs, enquadramento, status e data de referência.")
# Um status observado hoje não prova o status na data do evento.
'''


_GEOCODING = '''
# Conferência das duas localizações; ausência em uma associação não vira concordância.
geocod = painel.copy()
ambos = geocod["codigo_ibge"].notna() & geocod["codigo_ibge_espacial"].notna()
geocod["concordancia_codigo"] = pd.Series(pd.NA, index=geocod.index, dtype="boolean")
geocod.loc[ambos, "concordancia_codigo"] = (
    geocod.loc[ambos, "codigo_ibge"].astype("string")
    == geocod.loc[ambos, "codigo_ibge_espacial"].astype("string")
)
display(geocod.groupby("ano", observed=True)["concordancia_codigo"].agg(["count", "mean"]))
display(geocod["concordancia_codigo"].value_counts(dropna=False))
ASSOCIACAO_TERRITORIAL_ESCOLHIDA = None
print("Escolha territorial pendente; correspondência espacial não é medida independente de fiscalização.")
'''


_FINES = '''
# Valor nominal autuado; não é multa paga. Ausência de valor permanece identificável.
features = painel[["codigo_ibge", "ano", "valor_multas_ibama_it", "n_valores_ausentes"]].copy()
if features.duplicated(["codigo_ibge", "ano"]).any():
    print("Revisar chave duplicada antes de usar os valores.")
    features = None
else:
    assert_unique(features, ["codigo_ibge", "ano"])
    features["flag_soma_parcial"] = features["n_valores_ausentes"].gt(0)
    display(features.head())
INDICE_DEFLATOR = None      # Índice em R$, compatível com a frequência e o conceito escolhido.
INDICE_NA_DATA_BASE = None
if features is not None and INDICE_DEFLATOR is not None and INDICE_NA_DATA_BASE is not None:
    features = deflacionar(features, INDICE_DEFLATOR, "valor_multas_ibama_it", ["ano"], INDICE_NA_DATA_BASE)
else:
    print("Deflação pendente: escolher índice e data-base; valores continuam nominais.")
# Defasagens não eliminam a resposta da fiscalização à conversão.
'''


_EMBARGO = '''
# Histórico e coordenadas têm várias linhas por embargo; uma linha não é um embargo.
historico, coordenadas = bases[0].copy(), bases[1].copy()
cobertura_ids = (historico[["SEQ_TAD"]].dropna().drop_duplicates().merge(
    coordenadas[["SEQ_TAD"]].dropna().drop_duplicates(), on="SEQ_TAD", how="outer",
    validate="one_to_one", indicator=True,
))
display(cobertura_ids["_merge"].value_counts())

def contar_embargos(identidades_validadas):
    # Insumo manualmente validado: SEQ_TAD, codigo_ibge, data_embargo e elegivel.
    # elegivel resume a regra de status/data de referência decidida e documentada.
    base = identidades_validadas.copy()
    if base[["SEQ_TAD", "codigo_ibge", "data_embargo", "elegivel"]].isna().any().any():
        raise ValueError("Identidade, município, data ou elegibilidade não resolvidos.")
    assert_unique(base, ["SEQ_TAD"])
    base["ano"] = pd.to_datetime(base["data_embargo"], errors="coerce").dt.year.astype("Int64")
    if base["ano"].isna().any() or not base["elegivel"].isin([True, False]).all():
        raise ValueError("Conferir datas e elegibilidade booleana.")
    uso = base.loc[base["elegivel"].eq(True)]
    return (uso.groupby(["codigo_ibge", "ano"], observed=True)["SEQ_TAD"]
            .nunique().rename("n_embargos").reset_index())

IDENTIDADES_VALIDADAS = None
DATA_REFERENCIA_STATUS = None
if IDENTIDADES_VALIDADAS is not None and DATA_REFERENCIA_STATUS is not None:
    features = recorte_2001_2024(contar_embargos(IDENTIDADES_VALIDADAS))
    display(features.head())
else:
    print("Embargos pendentes: vincular SEQ_TAD, datas, status e município, com uma linha por identidade.")
    print("Não contar linhas do histórico/polígonos/pontos nem somar áreas sem unidade validada.")
# Resolver divergências em COD_MUNICIPIO, DAT_EMBARGO e status; não escolher última linha em silêncio.
'''


_CATTLE = '''
features = painel[["codigo_ibge", "ano", "efetivo_bovino"]].copy()
if features.duplicated(["codigo_ibge", "ano"]).any():
    print("Revisar chave municipal anual antes de usar o rebanho.")
    features = None
else:
    assert_unique(features, ["codigo_ibge", "ano"])
    display(features.head())
JANELA_COMPOSICAO_ANTERIOR = None
# Rebanho é estoque de cabeças. Uma exposição anterior precisa de janela e cobertura definidas.
'''


_STOCKING = '''
def construir_lotacao(rebanho, classes, compatibilidade_validada=False, limiar_area_pequena=None):
    if not compatibilidade_validada:
        raise ValueError("Validar mesma geografia, máscara e referência temporal.")
    chave = ["codigo_ibge", "ano"]
    assert_unique(rebanho, chave)
    # Classe 15 é a pastagem indicada no TXT; biomas devem formar partes sem sobreposição.
    pasto = classes.loc[pd.to_numeric(classes["class_id"], errors="coerce").eq(15)].copy()
    assert_unique(pasto, chave + ["biome"])
    pasto = (pasto.groupby(chave, observed=True)["area_ha"]
             .agg(lambda s: s.sum(min_count=len(s))).rename("pastagem_ha").reset_index())
    out = rebanho[chave + ["efetivo_bovino"]].merge(
        pasto, on=chave, how="outer", validate="one_to_one", indicator=True,
    )
    out["lotacao_cabecas_ha"] = out["efetivo_bovino"] / out["pastagem_ha"].where(out["pastagem_ha"] > 0)
    out["flag_pastagem_nula"] = out["pastagem_ha"].eq(0)
    if limiar_area_pequena is not None:
        if limiar_area_pequena < 0:
            raise ValueError("O limiar de área não pode ser negativo.")
        out["flag_pastagem_pequena"] = out["pastagem_ha"].lt(limiar_area_pequena)
    return out

COMPATIBILIDADE_VALIDADA = False
LIMIAR_AREA_PEQUENA_HA = None
if COMPATIBILIDADE_VALIDADA:
    features = recorte_2001_2024(construir_lotacao(bases[0], bases[1], True, LIMIAR_AREA_PEQUENA_HA))
    display(features.head())
else:
    print("Lotação pendente: validar geografia e datas do rebanho e da pastagem.")
# Cabeças/ha é lotação aparente; não mede diretamente produtividade nem rentabilidade.
'''


_NATIVE = '''
features = painel[["codigo_ibge", "ano", "native_veg_ha_lag1", "native_veg_share_lag1"]].copy()
if features.duplicated(["codigo_ibge", "ano"]).any():
    print("Revisar chave municipal anual antes de usar o denominador.")
    features = None
else:
    assert_unique(features, ["codigo_ibge", "ano"])
    display(features.head())
# As defasagens já estão na fonte: não deslocar novamente nem descartar história em df.
# Papel como denominador/controle depende da especificação; não adicionar controle automaticamente.
'''


_LAND_USES = '''
def compor_usos(classes, mapa_classes, legenda_validada=False):
    if not legenda_validada or not mapa_classes:
        raise ValueError("Definir classes pela legenda e validar ausência de sobreposição.")
    chave = ["codigo_ibge", "ano", "biome", "class_id"]
    assert_unique(classes, chave)
    uso = classes.loc[classes["class_id"].isin(mapa_classes)].copy()
    uso["uso"] = uso["class_id"].map(mapa_classes)
    # Não somar uma categoria-pai e suas subclasses. Ausências impedem soma completa.
    out = (uso.groupby(["codigo_ibge", "ano", "biome", "uso"], observed=True)["area_ha"]
           .agg(lambda s: s.sum(min_count=len(s))).rename("area_instalada_ha").reset_index())
    return out

MAPA_CLASSES_SEM_SOBREPOSICAO = None
LEGENDA_VALIDADA = False
if MAPA_CLASSES_SEM_SOBREPOSICAO is not None and LEGENDA_VALIDADA:
    usos = compor_usos(df, MAPA_CLASSES_SEM_SOBREPOSICAO, True)
    features = abrir_colunas(recorte_2001_2024(usos), ["codigo_ibge", "ano", "biome"], "uso", "area_instalada_ha")
    display(features.head() if features is not None else "Pivô pendente.")
else:
    print("Composição de usos pendente: conferir legenda e classes sem sobreposição.")
# Estoques instalados e substituição entre usos não são conversão bruta de vegetação nativa.
'''


_BIOMES = '''
fracao_biomas = ["biome_amazonia_share_i", "biome_cerrado_share_i", "biome_pantanal_share_i"]
features = df[["codigo_ibge"] + fracao_biomas].copy()
if features.duplicated(["codigo_ibge"]).any():
    print("Revisar municípios duplicados antes de usar as frações.")
    features = None
comparacoes = []
for limiar in (70, 80, 90):
    coluna = f"biome_class_{limiar}"
    contagem = df[coluna].value_counts(dropna=False).rename("municipios").reset_index()
    contagem.columns = ["classe_bioma", "municipios"]
    contagem["limiar_percentual"] = limiar
    comparacoes.append(contagem)
display(pd.concat(comparacoes, ignore_index=True))
display(pd.crosstab(df["biome_class_70"], df["biome_class_90"], dropna=False))
LIMIAR_PREDOMINANCIA = None  # Nenhum dos três limiares foi escolhido.
# Biomas mistos são parte da amostra. Níveis estáticos são absorvidos por efeitos fixos municipais.
'''


_COSTS = '''
def construir_serie_custos(celulas, mapa_validado):
    # Uma linha do mapa identifica uma célula de valor e explica seu significado.
    chave = ["arquivo_origem", "aba", "linha_excel", "coluna_excel"]
    metadados = ["ano", "safra", "localidade", "tecnologia", "categoria_custo", "unidade", "moeda", "metodologia"]
    if mapa_validado[chave + metadados].isna().any().any():
        raise ValueError("Completar ano/safra, local, tecnologia, custo e unidade de cada célula.")
    assert_unique(celulas, chave)
    assert_unique(mapa_validado, chave)
    out = mapa_validado.merge(celulas[chave + ["conteudo"]], on=chave,
                             how="left", validate="one_to_one", indicator=True)
    if not out["_merge"].eq("both").all():
        raise ValueError("O mapa aponta células não encontradas na extração.")
    # `conteudo` segue a extração. A regra numérica precisa ser fornecida no mapa.
    if "valor_custo_validado" not in out:
        raise ValueError("Adicionar valor_custo_validado após conferir separador decimal e unidade.")
    out["valor_custo_validado"] = pd.to_numeric(out["valor_custo_validado"], errors="raise")
    if out["valor_custo_validado"].isna().any():
        raise ValueError("Há custos ausentes no mapa validado.")
    assert_unique(out, metadados)
    return out

MAPA_CELULAS_VALIDADO = None
# O ano do painel deve ser mapeado explicitamente a cada safra; não extrair ano da aba.
if MAPA_CELULAS_VALIDADO is not None:
    features = recorte_2001_2024(construir_serie_custos(df, MAPA_CELULAS_VALIDADO))
    display(features.head())
else:
    print("Série de custos pendente: mapear células, unidades, localidades, tecnologias e safras.")
# Manter safras separadas; não replicar custo local para todos os municípios.
# Margem/retorno líquido requer compatibilidade adicional de preços, rendimento e custos.
'''


_RAIN = '''
# Soma de ano civil é candidata exploratória; janela produtiva/decisória continua em aberto.
mensal = df.copy()
chave = ["codigo_ibge", "ano", "mes"]
if mensal[chave].isna().any().any() or mensal.duplicated(chave).any():
    print("Soma anual pendente: revisar chaves mensais ausentes/duplicadas.")
elif not mensal["mes"].between(1, 12).all():
    print("Soma anual pendente: meses fora de 1 a 12.")
else:
    anual = (mensal.groupby(["codigo_ibge", "ano"], observed=True)
             .agg(precip_mm_anual=("precip_mm", lambda s: s.sum(min_count=12)),
                  meses_registrados=("mes", "nunique"),
                  meses_validos=("precip_mm", "count"),
                  fracao_pixels_minima=("fracao_pixels_validos", "min")).reset_index())
    completa = anual["meses_registrados"].eq(12) & anual["meses_validos"].eq(12)
    anual.loc[~completa, "precip_mm_anual"] = np.nan
    features = recorte_2001_2024(anual)
    display(features.head())
JANELA_PRODUTIVA_OU_DECISORIA = None
LIMIAR_PIXELS_VALIDOS = None
# Chuva é acumulada por soma; anos incompletos não equivalem a pouca chuva.
'''


_ANOMALIES = '''
referencias = ["1981_2010", "1991_2020"]
colunas = ["codigo_ibge", "ano", "precip_mm_anual", "count"]
for referencia in referencias:
    colunas += [f"precip_anomaly_{referencia}", f"precip_zscore_{referencia}", f"count_{referencia}"]
features = painel[colunas].copy()
if features.duplicated(["codigo_ibge", "ano"]).any():
    print("Revisar chave anual antes de usar anomalias.")
    features = None
else:
    assert_unique(features, ["codigo_ibge", "ano"])
    features["flag_ano_incompleto"] = features["count"].isna() | features["count"].ne(12)
    # Cobertura inválida não permite comparar totais anuais e anomalias.
    medidas = [c for c in colunas if c.startswith("precip_")]
    features.loc[features["flag_ano_incompleto"], medidas] = np.nan
    display(features.head())
    display(features[[f"precip_zscore_{r}" for r in referencias]].corr())
REFERENCIA_ESCOLHIDA = None
COBERTURA_MINIMA_REFERENCIA = None
# Anomalias em mm e escores sem unidade ficam separados; não representam balanço hídrico.
'''


_RELIEF = '''
features = df[["codigo_ibge", "elevation_mean_m", "elevation_min_m", "elevation_max_m"]].copy()
if features.duplicated(["codigo_ibge"]).any():
    print("Revisar municípios duplicados antes de usar elevações.")
    features = None
else:
    assert_unique(features, ["codigo_ibge"])
    display(features.head())
# Elevação é estática e medida em metros. DSM inclui efeitos de vegetação/edificações.
# Declividade e rugosidade exigem os rasters; não derivar essas medidas dos três resumos.
'''


def feature_code(name: str) -> str:
    """Retorna código executável de Fase 6 para o nome literal do TXT."""
    sources = {
        "Y_conv": _TRANSITIONS,
        "Y_tx-conv": _RATE,
        "x1_psoja-pmilho": _PRICE,
        "x1a_pcarne": _PRICE,
        "x2_prodsoja-prodmilho": _PAM,
        "x2a_hprodsoj-hprodmil": _HISTORICAL,
        "x2b_yield-sojamilho": _GAEZ.replace("{prefix}", "yx"),
        "x2c_aptid-sojamilho": _GAEZ.replace("{prefix}", "sx"),
        "x3_infracoes": _AUTOS.replace("{value}", "n_autos_ibama_it"),
        "x3a_infracoes": _AUTOS.replace("{value}", "n_autos_ibama_espacial"),
        "x3b_infracoes": _EVENTS,
        "x3c_infracoes": _GEOCODING,
        "x3d_infracoes": _FINES,
        "x3e_infracoes": _EMBARGO,
        "x4_pecuaria": _CATTLE,
        "x4a_pecuaria": _STOCKING,
        "x5_cobertura_terra": _NATIVE,
        "x5a_cobertura_terra": _LAND_USES,
        "x6_biomas": _BIOMES,
        "x7_custo-soja": _COSTS,
        "x7_custo-milho-s1": _COSTS,
        "x7_custo-milho-s2": _COSTS,
        "x8_chuva": _RAIN,
        "x8_chuvaa": _ANOMALIES,
        "x9_relevo": _RELIEF,
    }
    if name not in sources:
        raise ValueError(f"Fase 6 não mapeada: {name!r}. Revisar novo candidato antes de gerar.")
    return dedent(_COMMON).strip() + "\n\n" + dedent(sources[name]).strip() + "\n"
