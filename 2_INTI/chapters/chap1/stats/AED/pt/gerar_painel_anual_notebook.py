"""Gera o notebook integrado; cada saída tem sua própria célula."""
from pathlib import Path
import argparse
import json
import nbformat

from gerar_notebooks import extrair_blocos
from harmonizacao_notebooks import EXPLICACOES
from painel_anual_descritiva import ROTULOS

PASTA = Path(__file__).resolve().parent
RAIZ = next(p for p in PASTA.parents if (p / '2_INTI/RESEARCH_PROTOCOL.md').exists())
DESTINO = PASTA / 'painel_anual_2001_2024.ipynb'


def gerar():
    from painel_anual_fontes import carregar_fontes, preparar_blocos
    fontes, _ = carregar_fontes(RAIZ)
    blocos = preparar_blocos(fontes)
    candidatos, _ = extrair_blocos(RAIZ / '2_INTI/chapters/chap1/stats/HIPOTESES TESE - CHAP1.txt')
    cells = []

    def md(texto):
        cells.append(nbformat.v4.new_markdown_cell(texto))

    def code(texto, tipo='comando'):
        compile(texto, '<celula_painel>', 'exec')
        cells.append(nbformat.v4.new_code_cell(texto, metadata={'painel_operacao': tipo}))

    def tabela(texto):
        code(f'display({texto})', 'tabela')

    def grafico(texto):
        code(texto + '\nplt.show()\nplt.close(fig)', 'grafico')

    md('# Painel anual 2001–2024 — construção e estatística descritiva\n\n'
       '**Unidade:** município–ano. **Território:** 141 municípios na referência IBGE 2023. '
       '**Grade:** 141 × 24 = 3.384 linhas; a grade completa não significa medidas completas.\n\n'
       'Este notebook monta o painel a partir dos CSVs anuais e estáticos já produzidos pelos 25 notebooks '
       'de variáveis. Não é necessário executar novamente aquisições ou autenticar no Earth Engine. '
       'As fontes são lidas e conferidas por SHA-256; o painel anterior e os 25 notebooks são preservados.\n\n'
       '**Execute de cima para baixo no VS Code.** Cada tabela, comando de construção e gráfico tem sua própria célula. '
       'Os comentários explicam a operação; as funções auxiliares ficam nos arquivos Python desta pasta.\n\n'
       'São 25 candidatas inventariadas, com medidas e diagnósticos compartilhados. Embargos e as três séries CONAB '
       'permanecem adiados. O diagnóstico de geocodificação é anual e aparece como tabela auxiliar. '
       'Nenhuma ausência vira zero e nenhuma série é interpolada. A análise é descritiva; não estima efeitos causais.')
    md('## 1. Ambiente e fontes\n\nUse o mesmo kernel dos notebooks de AED. Dependências: pandas, numpy, '
       'matplotlib, seaborn e nbformat. Os caminhos são encontrados a partir da raiz do repositório.')
    code('from pathlib import Path\nimport sys\nimport json\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom IPython.display import display')
    code('RAIZ = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "2_INTI/RESEARCH_PROTOCOL.md").exists())\nPASTA_CODIGO = RAIZ / "2_INTI/chapters/chap1/stats/AED/pt"\nsys.path.insert(0, str(PASTA_CODIGO))')
    code('from painel_anual_fontes import carregar_fontes, preparar_blocos, construir_grade, rastrear_colunas\nfrom construir_painel import juntar\nfrom harmonizacao_comum import validar_tabela, hash_arquivo\nfrom painel_anual_descritiva import (catalogar, normalizar_tipos, descrever_medidas, resumo_por_fonte, cobertura_colunas,\n    frequencias_qualidade, variacao_painel, resumo_agrupado, resumo_y, histograma, boxplot,\n    serie_temporal, mapa_cobertura, grafico_correlacao, diagnosticar_amostras, ROTULOS)')
    code('pd.set_option("display.max_rows", 320)\npd.set_option("display.max_columns", 30)\npd.set_option("display.max_colwidth", 100)\npd.set_option("display.float_format", lambda x: f"{x:,.4f}")\nsns.set_theme(style="whitegrid", palette="colorblind")')
    code('# Conferimos os 25 manifestos e os hashes das tabelas antes de usar os valores.\nfontes, inventario = carregar_fontes(RAIZ)')
    tabela('inventario')
    md('## 2. Construção do painel\n\nA chave é `codigo_ibge` + `ano`. Primeiro criamos a grade completa; '
       'depois usamos junções à esquerda. Séries comuns usam apenas `ano`; atributos fixos usam apenas '
       '`codigo_ibge`. Cada junção exige uma linha por chave e impede multiplicar observações. '
       'Campos compartilhados entre notebooks entram uma única vez. As variáveis originais de cada fonte ficam em `fontes`.')
    code('blocos = preparar_blocos(fontes)')
    code('painel = construir_grade(fontes)')
    tabela('painel.head()')
    for i, bloco in enumerate(blocos):
        md(f'### Junção {i+1}: {bloco["nome"]}\n\nChaves: `{", ".join(bloco["chaves"])}`.')
        code(f'# Uma linha da grade continua sendo um município em um ano.\npainel = juntar(painel, blocos[{i}]["tabela"], blocos[{i}]["chaves"])')
    code('# Pivôs com números e flags podem produzir object; restauramos tipos sem mudar valores.\npainel = normalizar_tipos(painel)')
    code('validar_tabela(painel, ["codigo_ibge", "ano"])')
    code('assert len(painel) == 3384 and painel.codigo_ibge.nunique() == 141\nassert set(painel.ano) == set(range(2001, 2025))\nassert painel.groupby("codigo_ibge").ano.nunique().eq(24).all()\nassert "5101837" not in set(painel.codigo_ibge.astype(str))')
    code('rastreabilidade = rastrear_colunas(fontes, blocos)')
    code('catalogo = catalogar(painel, rastreabilidade)')
    md('### Conferência com o painel produzido anteriormente\n\nA reconstrução deve coincidir com o painel anterior. '
       'A leitura preserva os números do CSV; a conferência exige igualdade dos valores, mesmo que os tipos Python tenham sido organizados.')
    code('painel_anterior = pd.read_csv(RAIZ / "2_INTI/xdata/chap1/processed/harmonizacao/painel_candidato_2001_2024_141.csv", dtype={"codigo_ibge": "string", "y_colecao": "string", "y_malha": "string", "y_mascara_id": "string"}, float_precision="round_trip")')
    code('# A mesma representação de NA e booleanos permite comparar os valores exatamente.\npainel_anterior = normalizar_tipos(painel_anterior)')
    code('pd.testing.assert_frame_equal(\n    painel.sort_values(["codigo_ibge", "ano"]).reset_index(drop=True),\n    painel_anterior.sort_values(["codigo_ibge", "ano"]).reset_index(drop=True),\n    check_dtype=False, check_like=True, check_exact=True)')
    md('## 3. Estrutura, tipos e rastreabilidade\n\n`painel` é o DataFrame integrado. Ele inclui medidas, alternativas, '
       'identificadores e indicadores de qualidade. As 296 colunas atuais não são 296 regressoras recomendadas.')
    code('painel.shape')
    tabela('painel.head(8)')
    code('painel.info(verbose=True, show_counts=True)')
    tabela('painel.dtypes.rename("tipo").to_frame()')
    tabela('catalogo')
    tabela('painel.groupby("ano").agg(linhas=("codigo_ibge", "size"), municipios=("codigo_ibge", "nunique"))')
    tabela('painel.groupby("codigo_ibge").agg(n_anos=("ano", "nunique"), primeiro_ano=("ano", "min"), ultimo_ano=("ano", "max"))')
    md('## 4. Cobertura, ausências e qualidade\n\nAusência de registro, ano incompleto e denominador indefinido '
       'continuam ausentes. Zero observado é descrito separadamente. Indicadores de qualidade não entram '
       'automaticamente nas estatísticas de medidas substantivas.')
    code('cobertura = cobertura_colunas(painel)')
    tabela('cobertura')
    code('PRINCIPAIS = [c for c in ROTULOS if c in painel.columns]')
    tabela('painel.groupby("ano")[PRINCIPAIS].count()')
    tabela('painel.groupby("codigo_ibge")[PRINCIPAIS].count()')
    grafico('fig = mapa_cobertura(painel, PRINCIPAIS)')
    tabela('frequencias_qualidade(painel, catalogo)')
    md('## 5. Estatística descritiva completa das medidas\n\nCada coluna é resumida em sua unidade de observação: '
       'preços têm até **24 anos**, atributos fixos têm até **141 municípios**, e medidas anuais municipais têm '
       'até **3.384 pares**. Essa contagem não é o número de observações estatisticamente independentes.\n\n'
       'Apresentamos oportunidades, valores válidos, ausências, zeros, negativos, média, desvio-padrão amostral, '
       'mínimo, P1/P5/P25/mediana/P75/P95/P99, máximo, assimetria e curtose excedente. '
       'A regra de 1,5 × IQR sinaliza extremos; não remove nem winsoriza dados. Valores negativos podem ser legítimos '
       'em anomalias e transformações. A formatação arredonda apenas a exibição.')
    code('descritiva = descrever_medidas(painel, catalogo)')
    code('assert set(descritiva.variavel) == set(catalogo.loc[catalogo.papel.eq("medida"), "coluna_painel"])')
    code('assert all(not resumo_por_fonte(descritiva, catalogo, nome).empty for nome in inventario.loc[inventario.papel_painel.str.startswith("incluída"), "nome"])')
    tabela('descritiva')
    tabela('descritiva[["variavel", "unidade_observacao", "n_oportunidades", "n_validos", "n_ausentes", "n_zeros", "n_negativos"]]')
    tabela('descritiva[["variavel", "unidade", "p25", "p75", "iqr", "n_fora_1_5_iqr"]]')
    md('## 6. As 25 candidatas: resultados e pendências\n\nCada subseção mostra a contribuição daquela candidata. '
       'As mesmas medidas podem aparecer em mais de uma subseção quando os notebooks compartilham fontes. '
       'Isso não duplica colunas no painel. As tabelas adiadas são diagnósticos, não valores anuais estimados.')
    for i, bloco in enumerate(candidatos, 1):
        nome = bloco['nome']
        titulo, processo, formula, limite = EXPLICACOES[nome]
        md(f'### {i}. {nome}\n\n[{nome}.ipynb]({nome}.ipynb) — **{titulo}**.\n\n{processo}\n\n**Limite:** {limite}')
        if nome == 'x3c_infracoes':
            tabela('fontes["x3c_infracoes"]["tabelas"]["qualidade_geocodificacao"]')
            tabela('fontes["x3c_infracoes"]["tabelas"]["qualidade_geocodificacao"].drop(columns="ano").describe().T')
        elif fontes[nome]['manifesto']['status'].startswith('adiada'):
            tabela(f'fontes[{nome!r}]["tabelas"]["pendencias"]')
            if 'cobertura_celulas' in fontes[nome]['tabelas']:
                tabela(f'fontes[{nome!r}]["tabelas"]["cobertura_celulas"]')
        else:
            tabela(f'resumo_por_fonte(descritiva, catalogo, {nome!r})')
    md('## 7. Distribuições e evolução temporal\n\nCada medida principal tem histograma e boxplot próprios, '
       'sem misturar unidades. As séries municipais mostram mediana e P25–P75 dos municípios observados em cada ano; '
       'a composição pode mudar. A faixa não é intervalo de confiança. Atributos fixos não recebem tendência artificial.')
    for c, rotulo in ROTULOS.items():
        md(f'### {rotulo}\n\nColuna: `{c}`.')
        grafico(f'fig = histograma(painel, {c!r}, catalogo)')
        grafico(f'fig = boxplot(painel, {c!r}, catalogo)')
        if not c.startswith('elevation_'):
            grafico(f'fig = serie_temporal(painel, {c!r}, catalogo)')
    md('## 8. Comparações por ano, município e geografia\n\nOs resumos municipais abaixo excluem preços globais '
       'e atributos fixos para não repetir estatísticas sem variação temporal. As frações de bioma são mantidas '
       'como medidas contínuas. Para uma comparação descritiva adicional, o rótulo de 80% identifica municípios '
       'com essa predominância; os demais são mistos. A conversão pertence ao município inteiro, não à parcela do bioma.')
    code('MUNICIPAIS = catalogo.loc[catalogo.coluna_painel.isin(PRINCIPAIS) & catalogo.unidade_observacao.eq("município–ano"), "coluna_painel"].tolist()')
    code('resumo_anos = resumo_agrupado(painel, MUNICIPAIS, "ano")')
    tabela('resumo_anos')
    code('resumo_municipios = resumo_agrupado(painel, MUNICIPAIS, "codigo_ibge")')
    tabela('resumo_municipios.pivot(index="codigo_ibge", columns="variavel", values="media")')
    code('FRACOES_BIOMAS = ["biome_amazonia_share_i", "biome_cerrado_share_i", "biome_pantanal_share_i"]')
    code('geografia = painel[["codigo_ibge"] + FRACOES_BIOMAS].drop_duplicates("codigo_ibge").copy()')
    tabela('geografia')
    code('geografia["grupo_bioma_80"] = geografia[FRACOES_BIOMAS].idxmax(axis=1).map({"biome_amazonia_share_i": "Amazônia ≥80%", "biome_cerrado_share_i": "Cerrado ≥80%", "biome_pantanal_share_i": "Pantanal ≥80%"}).where(geografia[FRACOES_BIOMAS].max(axis=1).ge(.8), "Misto (<80%)")\ngeografia.loc[geografia[FRACOES_BIOMAS].isna().any(axis=1), "grupo_bioma_80"] = "Sem cobertura"')
    tabela('geografia.groupby("grupo_bioma_80").size().rename("n_municipios").to_frame()')
    code('painel_geografia = painel.merge(geografia[["codigo_ibge", "grupo_bioma_80"]], on="codigo_ibge", how="left", validate="many_to_one")')
    code('resumo_biomas = resumo_agrupado(painel_geografia, MUNICIPAIS, "grupo_bioma_80")')
    tabela('resumo_biomas')
    grafico('fig, ax = plt.subplots(figsize=(10, 5))\nsns.boxplot(data=painel_geografia, x="grupo_bioma_80", y="taxa_conversao__agricultura", ax=ax, color="#6daac2")\nax.set(xlabel="Classificação municipal por fração de bioma", ylabel="Taxa de conversão para agricultura (proporção)")\nfig.tight_layout()')
    md('## 9. Conversão: cobertura e duas formas de resumir taxas\n\nA soma de hectares abaixo cobre somente '
       'os municípios observados; não é um total estadual completo. A média simples de taxas dá o mesmo peso '
       'a cada município. A razão das somas usa a área nativa inicial como peso. Numerador e denominador '
       'usam exatamente a mesma amostra válida. Agricultura e pastagem permanecem separadas.\n\n'
       'Também mostramos o subconjunto com Y observado nos 24 anos. Ele estabiliza a composição, mas pode '
       'selecionar municípios diferentes dos excluídos; não substitui automaticamente a amostra principal.')
    code('conversao_ano = resumo_y(painel)')
    tabela('conversao_ano')
    code('conversao_balanceada = resumo_y(painel, apenas_balanceados=True)')
    tabela('conversao_balanceada')
    grafico('fig, ax = plt.subplots(figsize=(10, 4))\nsns.lineplot(data=conversao_ano, x="ano", y="n_validos", hue="destino", marker="o", ax=ax)\nax.set(xlabel="Ano", ylabel="Municípios com Y válido", ylim=(0, 145), xlim=(2001, 2024))\nfig.tight_layout()')
    grafico('fig, ax = plt.subplots(figsize=(10, 4))\nsns.lineplot(data=conversao_ano, x="ano", y="taxa_razao_das_somas", hue="destino", ax=ax)\nax.set(xlabel="Ano", ylabel="Conversão / nativa inicial — mesma amostra (proporção)", title="Amostra observada; composição pode variar", xlim=(2001, 2024))\nfig.tight_layout()')
    grafico('fig, ax = plt.subplots(figsize=(10, 4))\nsns.lineplot(data=conversao_balanceada, x="ano", y="taxa_razao_das_somas", hue="destino", ax=ax)\nax.set(xlabel="Ano", ylabel="Conversão / nativa inicial (proporção)", title="Somente municípios com Y completo nos 24 anos", xlim=(2001, 2024))\nfig.tight_layout()')
    md('## 10. Variação do painel e associação descritiva\n\nO desvio das médias municipais descreve diferenças '
       'entre municípios; o desvio de `x_it − média_i` descreve variação dentro deles. Em amostra incompleta, '
       'essas colunas não formam uma decomposição aditiva simples da variância. Atributos fixos têm variação '
       'interna nula; preços globais variam somente no tempo.\n\n'
       'As correlações abaixo usam uma amostra comum e apenas medidas municipais selecionadas. Informamos sua '
       'cobertura. A segunda matriz retira a média de cada município nessa amostra; não retira efeitos de ano '
       'e não representa identificação causal. Não calculamos p-valores supondo independência das linhas.')
    code('variacao = variacao_painel(painel, descritiva.variavel.tolist())')
    tabela('variacao')
    code('COLUNAS_CORRELACAO = ["taxa_conversao__agricultura", "taxa_conversao__pastagem", "efetivo_bovino", "lotacao_cabecas_ha", "precip_mm_anual", "rendimento_medio_kg_ha__Soja (em grão)", "rendimento_medio_kg_ha__Milho (em grão)"]')
    code('amostra_correlacao = painel[["codigo_ibge", "ano"] + COLUNAS_CORRELACAO].dropna(subset=COLUNAS_CORRELACAO).copy()')
    tabela('pd.DataFrame({"n_pares": [len(amostra_correlacao)], "n_municipios": [amostra_correlacao.codigo_ibge.nunique()], "n_anos": [amostra_correlacao.ano.nunique()], "ano_min": [amostra_correlacao.ano.min()], "ano_max": [amostra_correlacao.ano.max()]})')
    tabela('amostra_correlacao.groupby("ano").size().rename("n_pares_completos").to_frame()')
    code('correlacao_niveis = amostra_correlacao[COLUNAS_CORRELACAO].corr()')
    tabela('correlacao_niveis')
    grafico('fig = grafico_correlacao(correlacao_niveis, "Correlação de Pearson — amostra comum, níveis")')
    code('desvios_municipais = amostra_correlacao[COLUNAS_CORRELACAO] - amostra_correlacao.groupby("codigo_ibge")[COLUNAS_CORRELACAO].transform("mean")')
    code('correlacao_interna = desvios_municipais.corr()')
    tabela('correlacao_interna')
    grafico('fig = grafico_correlacao(correlacao_interna, "Correlação após retirar médias municipais — mesma amostra")')
    md('## 11. Cobertura conjunta e seleção da amostra\n\nEstes conjuntos são diagnósticos de disponibilidade, '
       'não especificações econométricas escolhidas. Evitamos excluir linhas por ausência em qualquer uma das '
       '296 colunas, pois elas incluem alternativas e diagnósticos. A comparação entre pares com e sem Y '
       'ajuda a descrever seleção; não identifica a causa das ausências.')
    code('CENARIOS = {\n    "Y nos dois destinos": ["taxa_conversao__agricultura", "taxa_conversao__pastagem"],\n    "Y + chuva": ["taxa_conversao__agricultura", "taxa_conversao__pastagem", "precip_mm_anual"],\n    "Y + chuva + rendimentos + rebanho/lotação": COLUNAS_CORRELACAO,\n    "Y + chuva + autos desmatamento informados": ["taxa_conversao__agricultura", "taxa_conversao__pastagem", "precip_mm_anual", "n_autos_desmatamento__ibama_informada"],\n    "Y + exposição PAM soja": ["taxa_conversao__agricultura", "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__pam_1991_2000_min7"],\n}')
    code('cobertura_conjunta = diagnosticar_amostras(painel, CENARIOS)')
    tabela('cobertura_conjunta')
    code('comparacao_ausencias = painel.assign(situacao_y=np.where(painel[["taxa_conversao__agricultura", "taxa_conversao__pastagem"]].notna().all(axis=1), "Y observado", "Y ausente"))')
    tabela('resumo_agrupado(comparacao_ausencias, ["efetivo_bovino", "precip_mm_anual", "rendimento_medio_kg_ha__Soja (em grão)", "n_autos_desmatamento__ibama_informada"], "situacao_y")')
    md('## 12. Salvar os resultados\n\nO painel reconstruído e as tabelas descritivas ficam em uma subpasta própria '
       '`processed/harmonizacao/painel_notebook/`. Reexecutar estas células atualiza somente essas saídas. '
       'Os CSVs das 25 fontes e o painel anterior não são sobrescritos. Tabelas extensas ficam completas nos CSVs, '
       'mesmo quando a interface do Jupyter limita a exibição.')
    code('PASTA_SAIDA = RAIZ / "2_INTI/xdata/chap1/processed/harmonizacao/painel_notebook"\nPASTA_SAIDA.mkdir(parents=True, exist_ok=True)')
    exports = {'painel_2001_2024_141': 'painel', 'inventario_25_fontes': 'inventario',
               'dicionario_painel': 'catalogo', 'cobertura_colunas': 'cobertura',
               'descritiva_medidas': 'descritiva', 'descritiva_por_ano': 'resumo_anos',
               'descritiva_por_municipio': 'resumo_municipios', 'descritiva_grupos_bioma': 'resumo_biomas',
               'conversao_por_ano': 'conversao_ano', 'conversao_amostra_balanceada': 'conversao_balanceada',
               'variacao_dentro_entre': 'variacao', 'cobertura_conjunta': 'cobertura_conjunta'}
    for nome, var in exports.items():
        code(f'{var}.to_csv(PASTA_SAIDA / "{nome}.csv", index=False, encoding="utf-8", na_rep="")')
    code('manifesto_notebook = {"periodo": [2001, 2024], "municipios": 141, "linhas": len(painel), "colunas": len(painel.columns), "candidatas_inventariadas": len(inventario), "n_medidas_descritas": len(descritiva), "hash_painel": hash_arquivo(PASTA_SAIDA / "painel_2001_2024_141.csv"), "pronto_para_inferencia_causal": False, "regra": "Ausências preservadas; estatísticas conforme unidade de observação; diagnósticos não definem modelo."}')
    code('(PASTA_SAIDA / "manifesto_notebook.json").write_text(json.dumps(manifesto_notebook, ensure_ascii=False, indent=2), encoding="utf-8")')
    tabela('pd.Series(manifesto_notebook, name="valor").to_frame()')
    md('## 13. Limites para a próxima etapa econométrica\n\n'
       '- A grade é completa, mas a amostra utilizável depende das variáveis escolhidas. A cobertura de Y e das instituições deve acompanhar cada estimativa.\n'
       '- Preços comuns a todos os municípios são absorvidos por efeitos fixos anuais; atributos fixos, por efeitos fixos municipais. As interações mantêm outra variação, sem garantir exogeneidade.\n'
       '- Autos e multas podem responder à conversão. Município informado e localização espacial são alternativas; Flora e Desmatamento não devem ser somados.\n'
       '- GAEZ usa base de terras de 2010; capacidade histórica PAM tem cobertura seletiva e ressalvas territoriais. Defasagens não resolvem esses problemas sozinhas.\n'
       '- O ano civil não descreve automaticamente o calendário da decisão agrícola. As transições de Y indicam mudança entre mapas, não a data exata da decisão.\n'
       '- Outliers, ausência, composição da amostra e dependência espacial/temporal requerem decisões explícitas. Este notebook não altera hipóteses nem escolhe estimador, controles ou estratégia causal.')
    nb = nbformat.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'},
        'painel_aed': {'versao': 1, 'periodo': [2001, 2024], 'municipios': 141,
                       'fontes': 25, 'uma_saida_por_celula': True}})
    for i, cell in enumerate(nb.cells):
        cell.id = f'painel-{i:03d}'
    nbformat.validate(nb)
    return nb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sobrescrever', action='store_true', help='Substitui somente o notebook integrado, incluindo outputs.')
    args = parser.parse_args()
    if DESTINO.exists() and not args.sobrescrever:
        raise FileExistsError('Notebook já existe; use --sobrescrever para regenerar conscientemente.')
    nb = gerar()
    nbformat.write(nb, DESTINO)
    print(json.dumps({'notebook': str(DESTINO), 'celulas': len(nb.cells)}, ensure_ascii=True))


if __name__ == '__main__':
    main()
