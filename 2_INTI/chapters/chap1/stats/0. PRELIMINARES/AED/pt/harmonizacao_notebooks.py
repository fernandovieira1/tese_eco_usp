"""Seções curtas e específicas da construção executável dos 25 candidatos."""
import nbformat


EXPLICACOES = {
    'Y_conv': (
        'Conversão bruta por destino',
        'Selecionamos pixels que eram nativos em t−1 e passaram para agricultura ou pastagem em t. '
        'Somamos suas áreas em hectares, mantendo os dois destinos separados. É necessário observar '
        'as duas datas na mesma coleção, máscara e malha. Usamos mapas 10.1, pixels na grade original '
        'e os 141 territórios de 2023. Ano t identifica o intervalo dos mapas t−1 a t. '
        'A diferença de estoques não mede esse fluxo.',
        'C_destino = soma(area_pixel_ha × indicador(nativo_t−1 e destino_t))',
        'A área sem classificação é medida diretamente. Qualquer lacuna real mantém Y ausente; '
        'diferenças numéricas entre grandes somas não são confundidas com pixels ausentes. '
        'Zero só é aceito depois de verificar a matriz completa. O dado registra mudança entre mapas '
        'anuais e não informa a data exata da decisão ou sua causa.'),
    'Y_tx-conv': (
        'Taxas de conversão por destino',
        'Dividimos cada conversão bruta pela vegetação nativa no início do mesmo intervalo. '
        'O numerador e o denominador vêm dos mesmos pixels válidos nos dois mapas. Para 2001, '
        'usamos o mapa inicial de 2000. A máscara e o denominador acompanham cada município–ano.',
        'taxa_destino = conversao_destino_ha / nativa_inicial_ha; taxa_pct = 100 × taxa_destino',
        'Denominador zero torna a taxa indefinida. Taxas inconsistentes não são cortadas em 1. '
        'A taxa mede a fração convertida do estoque disponível, não o efeito acumulado sobre toda a vegetação histórica. '
        'Cobertura incompleta mantém área convertida e taxa ausentes, sem extrapolar os pixels observados.'),
    'x1_psoja-pmilho': (
        'Preços anuais, defasagens e exposição econômica',
        'Preservamos soja e milho separados. Deflacionamos os preços mensais em USD quando o índice oficial está disponível, '
        'calculamos a média de 12 meses válidos e ligamos o ano t ao preço de t−1. '
        'Logs são calculados somente para preços positivos. As interações usam capacidade fixa, em cenários separados.',
        'P_real_m = P_nominal_m × indice_base / indice_m; P_anual = media(12 meses); Z = log(P_anual_t−1) × capacidade_z',
        'O preço anterior é uma exposição conhecida antes do intervalo anual, não uma expectativa observada. '
        'Preço × capacidade não é lucro líquido nem choque exógeno por definição.'),
    'x1a_pcarne': (
        'Preço da carne na janela anterior',
        'Calculamos médias anuais e ligamos o preço do ano anterior ao ano do painel. '
        'Mantemos a unidade USD/kg e distinguimos valor nominal e real. Não multiplicamos cabeças por preço por kg.',
        'preco_previo_t = media_dos_12_meses_do_ano_t−1; ln_preco = log(preco), se preco > 0',
        'Preço internacional de carne não equivale ao preço local do boi. A exposição pecuária predeterminada '
        'continua uma decisão distinta; lotação contemporânea não a substitui.'),
    'x2_prodsoja-prodmilho': (
        'Rendimento observado e conferência das unidades',
        'Separamos soja e milho, preservamos o rendimento informado e conferimos produção e área colhida. '
        'A recomposição por produção/área usa toneladas para kg. Defasagens ligam anos exatos.',
        'rendimento_calculado_kg_ha = 1000 × producao_t / area_colhida_ha, quando area_colhida_ha > 0',
        'Rendimento ausente não vira zero. Produtividade observada pode responder a preços, clima e uso de insumos; '
        'não é automaticamente uma capacidade anterior à decisão.'),
    'x2a_hprodsoj-hprodmil': (
        'Capacidade histórica anterior ao painel',
        'Aplicamos a janela discutida de 1991–2000, com pelo menos 7 anos de rendimento válido por município e cultura. '
        'Calculamos a média dos anos válidos e guardamos a cobertura. A padronização usa uma única referência fixa.',
        'cap_hist = media(rendimentos validos de 1991 a 2000), se n_anos >= 7; z = (cap_hist − media_fixa) / desvio_fixo',
        'Não cultivo e falta de registro não são rendimento zero. Os códigos históricos ainda exigem '
        'validação territorial; a tabela sinaliza essa limitação e a seleção de produtores históricos.'),
    'x2b_yield-sojamilho': (
        'Capacidade potencial GAEZ por cenário',
        'Mantemos os rasters yx separados por cultura e nível de insumo. Padronizamos cada cenário entre municípios '
        'uma única vez e construímos exposições aos preços prévios. Não misturamos alto e baixo insumo.',
        'capacidade_z = (rendimento_potencial − media_do_cenario) / desvio_do_cenario; Z = log(P_t−1) × capacidade_z',
        'A unidade original é kg de matéria seca/ha. Sem parâmetro validado de umidade, não calculamos receita comercial. '
        'A base de terras de 2010 impede presumir capacidade predeterminada sem auditoria.'),
    'x2c_aptid-sojamilho': (
        'Aptidão reescalada e exposição aos preços',
        'Dividimos sx por 10.000 para facilitar leitura e padronizamos cada cenário fixo. '
        'Os produtos e os níveis de insumo permanecem identificados nas interações.',
        'aptidao_0_1 = sx / 10000; Z = log(P_t−1) × aptidao_padronizada',
        'Reescalar não transforma aptidão em probabilidade, kg/ha ou receita. '
        'Os cenários são alternativas, não controles para inclusão simultânea automática.'),
    'x3_infracoes': (
        'Autos pelo município informado',
        'Conferimos o agregado original e construímos contagens temáticas a partir de identidades únicas. '
        'Flora e desmatamento são seleções alternativas. Usamos ano de lavratura e mantemos status desconhecidos visíveis.',
        'n_autos_tema = numero_de_IDs_distintos_do_tema_no_municipio_ano',
        'Sem registros não se presume zero. Cobertura temática parcial é sinalizada. '
        'Autos descrevem registros administrativos, não eficácia institucional.'),
    'x3a_infracoes': (
        'Autos pela localização espacial',
        'Associamos identidades às coordenadas já reprocessadas na malha de 141 municípios. '
        'Construímos as mesmas seleções temáticas para comparar com o município informado.',
        'n_autos_espacial = numero_de_IDs_distintos_localizados_no_territorio_de_referencia',
        'A amostra geocodificada tem cobertura própria. Não somamos a contagem espacial à informada, '
        'pois ambas podem representar os mesmos autos.'),
    'x3b_infracoes': (
        'Seleção temática e agregação dos eventos',
        'A categoria Flora fornece uma seleção ampla; o campo de tema de área identifica registros de desmatamento. '
        'Conferimos IDs, datas e localização antes de contar. Situação atual não é tratada como situação histórica.',
        'evento elegivel → ID unico → ano de lavratura → contagem por municipio e tema',
        'As duas seleções não são somáveis. Datas do fato ausentes não são preenchidas silenciosamente '
        'com lavratura; cada data mede um momento diferente.'),
    'x3c_infracoes': (
        'Qualidade da associação territorial',
        'Comparamos códigos somente quando as duas localizações estão disponíveis. '
        'Calculamos divergência entre os casos comparáveis e medimos separadamente a falta de localização.',
        'taxa_divergencia = n_codigos_diferentes / n_eventos_comparaveis',
        'Denominador zero deixa a taxa ausente. Este é um diagnóstico de mensuração, '
        'não uma variável adicional de fiscalização.'),
    'x3d_infracoes': (
        'Valores autuados em moeda constante',
        'Usamos o valor de cada auto, a data de lavratura e o IPCA mensal disponível. '
        'Depois somamos por município, ano e seleção temática, conservando a informação sobre valores ausentes.',
        'valor_real_auto = valor_nominal_auto × IPCA_base / IPCA_mes; total = soma_dos_valores_validos',
        'Soma parcial não é total completo; o indicador permanece visível. '
        'Multa autuada não significa multa paga, nem efeito dissuasório identificado.'),
    'x3e_infracoes': (
        'Diagnóstico dos embargos e exclusão temporária',
        'Documentamos identidades, datas e cobertura do histórico. O plano mantém esta fonte fora do painel principal '
        'até reconstruir emissão e trajetória de situação com unidades verificadas.',
        'um embargo deve corresponder a uma identidade; alteracoes e coordenadas nao sao novos embargos',
        'Não criamos contagem anual final ou área embargada a partir de linhas do histórico. '
        'O arquivo de pendências registra os insumos necessários para liberar o cálculo.'),
    'x4_pecuaria': (
        'Rebanho e defasagem de calendário',
        'Preservamos o estoque bovino anual e juntamos o valor do ano anterior pelo código e pelo ano. '
        'Não somamos estoques ao longo dos anos.',
        'rebanho_lag1(i,t) = rebanho(i,t−1)',
        'Rebanho mede cabeças, não produtividade. Mesmo o rebanho anterior pode refletir incentivos passados; '
        'a defasagem não garante exogeneidade.'),
    'x4a_pecuaria': (
        'Lotação aparente de pastagens',
        'Somamos a pastagem da classe 15 sem sobrepor biomas e dividimos o estoque bovino pela área. '
        'Conservamos numerador, denominador e indicadores de ausência para conferir a razão.',
        'lotacao_cabecas_ha = efetivo_bovino / pastagem_ha, se pastagem_ha > 0',
        'Pastagem nula gera medida indefinida. Denominadores pequenos ficam visíveis. '
        'Cabeças/ha não mede produção de carne, ganho de peso ou lucro.'),
    'x5_cobertura_terra': (
        'Vegetação disponível no início do período',
        'Reutilizamos as colunas de estoque e participação que já representam o ano anterior. '
        'Registramos denominador nulo ou ausente sem deslocar a série outra vez.',
        'nativa_inicial_ha = native_veg_ha_lag1 (ja defasada na fonte)',
        'O denominador candidato só pode formar a taxa após conferir a máscara das transições. '
        'Não é incluído automaticamente como controle adicional à taxa.'),
    'x5a_cobertura_terra': (
        'Áreas e participações dos usos instalados',
        'Agrupamos classes sem sobreposição para agricultura e pastagem. '
        'Conferimos a presença dos estratos esperados antes de somar e produzimos participações e defasagens exatas.',
        'area_uso = soma(classes_folha_do_uso); participacao = area_uso / area_referencia_2000',
        'Área colhida de soja e milho pode usar o mesmo terreno em sucessão. '
        'Estoques instalados e seus saldos não substituem as transições de vegetação nativa.'),
    'x6_biomas': (
        'Frações de bioma e heterogeneidade',
        'Preservamos as frações de Amazônia, Cerrado e Pantanal, incluindo municípios mistos. '
        'Geramos interações com exposição econômica para Cerrado e Pantanal; Amazônia é a referência.',
        'interacao_bioma = exposicao_preco_capacidade × fracao_do_bioma',
        'As frações são estáticas e seus níveis são absorvidos por efeitos fixos municipais. '
        'Não incluir a exposição e todas as frações interagidas sem conferir redundância.'),
    'x7_custo-soja': (
        'Custos de soja: insumos para construção posterior',
        'Registramos cobertura das células e os campos necessários para uma série comparável: '
        'localidade, tecnologia, safra, categoria de custo, moeda e unidade.',
        'custo comparavel requer celula identificada + unidade + local + tecnologia + safra',
        'Conforme o plano, a fonte fica fora do painel principal. Não misturamos R$/ha com R$/saca '
        'nem atribuímos o custo de poucas localidades a todos os municípios.'),
    'x7_custo-milho-s1': (
        'Custos de milho de primeira safra: cobertura e pendências',
        'Mantemos primeira safra separada. Documentamos a cobertura observada e a necessidade de mapear '
        'as células antes de interpretar números como custos.',
        'serie futura: localidade × tecnologia × primeira_safra × ano × categoria × unidade',
        'As abas identificadas terminam em 2013. Não prolongamos a série até 2024 por preenchimento '
        'nem criamos uma margem sem preços e quantidades compatíveis.'),
    'x7_custo-milho-s2': (
        'Custos de milho de segunda safra: cobertura e pendências',
        'Mantemos segunda safra e tecnologias identificadas. A documentação separa cobertura de células '
        'da existência de uma série de custos pronta.',
        'serie futura: localidade × tecnologia × segunda_safra × ano × categoria × unidade',
        'Os custos unitários de duas safras não devem ser somados como se fossem custo de uma mesma área. '
        'A fonte permanece fora do painel principal nesta etapa.'),
    'x8_chuva': (
        'Precipitação anual e cobertura',
        'Somamos os acumulados dos 12 meses distintos e válidos. Guardamos a cobertura de pixels e meses. '
        'A janela principal é o ano civil; a escolha de estação agrícola exigiria outra definição.',
        'precip_mm_anual = soma(precip_mm dos 12 meses validos)',
        'Ano incompleto não é ano seco. Milímetros são acumulados ao longo do tempo, '
        'enquanto a agregação espacial preserva a média municipal do raster.'),
    'x8_chuvaa': (
        'Anomalias e escores da chuva',
        'Após validar o total anual, calculamos média e desvio da referência 1981–2000. '
        'Mantemos 1981–2010 e 1991–2020 como alternativas retrospectivas, claramente nomeadas.',
        'anomalia = chuva_anual − media_referencia; z = anomalia / desvio_referencia, se desvio > 0',
        '1981–2000 tem 20 anos e não é uma normal de 30 anos. As referências posteriores não eram '
        'integralmente conhecidas em 2001. Anomalia de chuva não é balanço hídrico.'),
    'x9_relevo': (
        'Elevação estática e interpretação',
        'Preservamos média, mínimo e máximo, em metros, na malha fixa. '
        'Conferimos ordem e unicidade dos resumos, mantendo os atributos em tabela municipal.',
        'elevation_min_m <= elevation_mean_m <= elevation_max_m',
        'O produto é de superfície (DSM). Declividade e rugosidade dependem de vizinhanças dos pixels; '
        'não são calculadas por diferença entre os três resumos.'),
}


def celulas_harmonizacao(nome):
    titulo, processo, formula, limite = EXPLICACOES[nome]
    texto = (
        f'### Passos 1 e 2 — Construção executada das variáveis\n\n'
        f'**{titulo}.** {processo}\n\n'
        f'**Fórmula/regra:** `{formula}`.\n\n'
        f'**Interpretação e limite:** {limite}\n\n'
        'Os parâmetros e funções ficam em `harmonizacao.py` e nos módulos `harmonizacao_*`. '
        'A execução abaixo aplica as regras, mostra a cobertura e salva os derivados em '
        '`2_INTI/xdata/chap1/processed/harmonizacao/`, sem alterar as fontes. '
        'As tabelas preservam ausências e motivos; não selecionam uma especificação econométrica.'
    )
    codigo = f'''# {titulo}.
# Regra: {formula}
# As seis fases anteriores inspecionam as fontes; esta seção constrói as saídas.
import sys
PASTA_CODIGO = RAIZ / "2_INTI/chapters/chap1/stats/AED/pt"
if str(PASTA_CODIGO) not in sys.path:
    sys.path.insert(0, str(PASTA_CODIGO))
from harmonizacao import construir_variavel
from harmonizacao_comum import exportar_resultado, resumo_cobertura

# bases contém as cópias limpas, já na referência territorial de 141 municípios.
resultado_construcao = construir_variavel(NOME, RAIZ, bases=bases)
tabelas_derivadas = resultado_construcao["tabelas"]
features_construidas = tabelas_derivadas.get(resultado_construcao["principal"])
print("Situação:", resultado_construcao["status"])
display(pd.DataFrame(resultado_construcao["dicionario"]))
display(pd.Series(resultado_construcao["parametros"], name="regra aplicada").to_frame())
for pendencia in resultado_construcao["pendencias"]:
    print("Limitação:", pendencia)
'''
    saida = '''# Conferimos linhas e ausências antes de salvar. NA não vira zero.
for nome_tabela, tabela in tabelas_derivadas.items():
    print(nome_tabela, "— linhas:", len(tabela), "colunas:", len(tabela.columns))
    display(tabela.head(8))
display(resumo_cobertura(tabelas_derivadas))

# Cada notebook usa uma pasta própria; os CSVs de origem são somente leitura.
PASTA_DERIVADOS = exportar_resultado(resultado_construcao, RAIZ)
print("Derivados e manifesto salvos em:", PASTA_DERIVADOS)
'''
    cells = [nbformat.v4.new_markdown_cell(texto), nbformat.v4.new_code_cell(codigo),
             nbformat.v4.new_code_cell(saida)]
    if nome.startswith('Y_'):
        cells.append(nbformat.v4.new_markdown_cell(
            '#### Conferência das transições construídas\n\n'
            'A tabela mostra quantos municípios têm medida válida em cada ano e destino. '
            'Os gráficos usam apenas essas observações: a média municipal dá o mesmo peso a cada município '
            'e pode variar com a cobertura. Não representa uma taxa estadual ponderada nem efeito causal. '
            'As fases anteriores continuam como diagnóstico dos estoques de origem.'))
        medida = 'conversao_ha' if nome == 'Y_conv' else 'taxa_conversao'
        unidade = 'ha por município' if nome == 'Y_conv' else 'proporção do estoque nativo inicial'
        rotulo = 'Conversão (ha)' if nome == 'Y_conv' else 'Taxa (proporção)'
        cells.append(nbformat.v4.new_code_cell(f'''# Usamos o Y efetivamente construído, mantendo os destinos separados.
if "taxas" in tabelas_derivadas:
    y = tabelas_derivadas["taxas"].copy()
    MEDIDA_Y = "{medida}"
    cobertura_y = y.groupby(["ano", "destino"], observed=True).agg(
        municipios=("codigo_ibge", "nunique"),
        medidas_validas=(MEDIDA_Y, "count"),
        media_municipal=(MEDIDA_Y, "mean"),
    ).reset_index()
    display(cobertura_y)
    display(y.groupby("destino", observed=True)[MEDIDA_Y].describe())
    fig, axes = plt.subplots(1, 3, figsize=(17, 4))
    sns.histplot(data=y, x=MEDIDA_Y, hue="destino", element="step", ax=axes[0])
    sns.boxplot(data=y, x="destino", y=MEDIDA_Y, ax=axes[1])
    sns.lineplot(data=cobertura_y, x="ano", y="media_municipal", hue="destino", ax=axes[2])
    axes[0].set_xlabel("{unidade}")
    axes[0].set_ylabel("Observações")
    axes[1].set_ylabel("{rotulo}")
    axes[2].set_ylabel("{rotulo} — média municipal")
    axes[2].set_title("Municípios com medida válida; consultar cobertura")
    axes[2].set_xlim(2001, 2024)
    axes[2].set_xticks([2001, 2005, 2010, 2015, 2020, 2024])
    for ax in axes:
        ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.show()
else:
    print("Os gráficos de Y aguardam a aquisição completa das transições.")
'''))
    return cells
