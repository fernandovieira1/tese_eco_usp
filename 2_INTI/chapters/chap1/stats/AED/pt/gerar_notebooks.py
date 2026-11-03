"""Gera a AED de cada bloco do dicionário, sem alterar dados ou hipóteses.

Uso, a partir de qualquer diretório:
    python caminho/para/gerar_notebooks.py
    python caminho/para/gerar_notebooks.py --sobrescrever
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import textwrap

import nbformat

from aed_features import feature_code
from harmonizacao_notebooks import celulas_harmonizacao

PASTA = Path(__file__).resolve().parent
DICIONARIO = PASTA.parents[1] / 'HIPOTESES TESE - CHAP1.txt'


def extrair_blocos(caminho):
    texto = Path(caminho).read_text(encoding='utf-8-sig')
    corpo, separador, final = texto.partition('PENDÊNCIAS PARA A BASE EXPLORATÓRIA')
    if not separador:
        raise ValueError('Seção de pendências não encontrada no TXT.')
    pendencias = [s.strip()[1:].strip() for s in final.splitlines() if s.strip().startswith('*')]
    padrao = re.compile(r'^-\s+([A-Za-z0-9_-]+)\s*=\s*(.+)$', re.MULTILINE)
    marcadores = list(padrao.finditer(corpo))
    blocos = []
    for i, marca in enumerate(marcadores):
        fim = marcadores[i + 1].start() if i + 1 < len(marcadores) else len(corpo)
        trecho = corpo[marca.end():fim]
        caminhos = re.findall(r'^\s*(2_INTI[^\r\n]*\.csv)\s*$', trecho, re.MULTILINE)
        notas = []
        for linha in trecho.splitlines():
            s = linha.strip()
            if s.startswith('*'):
                notas.append(s[1:].strip())
        if not caminhos:
            raise ValueError(f'{marca[1]}: nenhum CSV encontrado.')
        blocos.append(dict(nome=marca[1], descricao=marca[2].strip(), caminhos=caminhos, notas=notas))
    nomes = [b['nome'] for b in blocos]
    if not nomes or len(set(nomes)) != len(nomes):
        raise ValueError('Lista de variáveis vazia ou com nomes repetidos.')
    return blocos, pendencias


def perfil(nome):
    """Seleciona medidas explícitas; nunca usa todas as colunas numéricas."""
    p = dict(chave=['codigo_ibge', 'ano'], grupos=[], valores=[], unidades={}, selecao='', aviso='')
    if nome in ('Y_conv', 'x5a_cobertura_terra'):
        p.update(chave=['codigo_ibge', 'ano', 'biome', 'class_id'], grupos=['biome', 'class_id'],
                 valores=['area_ha'], unidades={'area_ha': 'ha de estoque por classe'},
                 aviso='Estes gráficos descrevem estoques por classe e bioma. A construção de Y está na seção Passos 1 e 2; diferença de estoques não é conversão.')
        if nome == 'x5a_cobertura_terra':
            p['selecao'] = """# Classes folha agrícolas e pastagem da legenda local da coleção 10.
# Referência: 2_INTI/xdata/catalog/mapbiomas_legenda_taxonomia.json.
# Não incluir mosaico (21), silvicultura (9) nem categorias-pai sobrepostas.
CLASSES_USOS = [15, 39, 20, 40, 62, 41, 46, 47, 35, 48]
df = df.loc[df['class_id'].isin(CLASSES_USOS)].copy()"""
            p['aviso'] = 'Estoques separados de pastagem e classes agrícolas da legenda local. A composição agregada e a geografia histórica continuam pendentes.'
    elif nome in ('Y_tx-conv', 'x5_cobertura_terra'):
        p.update(valores=['native_veg_ha_lag1', 'native_veg_share_lag1'],
                 unidades={'native_veg_ha_lag1': 'ha no início do período', 'native_veg_share_lag1': 'proporção 0–1'},
                 aviso='Diagnóstico dos denominadores candidatos. A seção Passos 1 e 2 calcula Y_tx-conv com transições e denominador na mesma máscara.' if nome == 'Y_tx-conv' else 'Estoque inicial; o papel como controle permanece em aberto.')
    elif nome in ('x1_psoja-pmilho', 'x1a_pcarne'):
        produtos = ['price_soja', 'price_milho'] if nome == 'x1_psoja-pmilho' else ['price_carne_bovina']
        p.update(chave=['data', 'variavel'], grupos=['variavel'], valores=['preco_nominal'],
                 unidades={'preco_nominal': 'USD/t' if len(produtos) == 2 else 'USD/kg'},
                 selecao=f"df = df.loc[df['variavel'].isin({produtos!r})].copy()",
                 aviso='Preços mundiais em formato longo: o nome do produto está em variavel. Não há município nesta série; não replicar linhas para simular variação local.')
    elif nome in ('x2_prodsoja-prodmilho', 'x2a_hprodsoj-hprodmil'):
        p.update(chave=['codigo_ibge', 'ano', 'produto'], grupos=['produto'],
                 valores=['rendimento_medio_kg_ha'], unidades={'rendimento_medio_kg_ha': 'kg/ha colhido'},
                 aviso='Rendimento observado; não preencher rendimento ausente com zero. A média histórica pré-2001 depende de janela e cobertura definidas.' if nome.startswith('x2a') else 'Soja e milho separados. Rendimento observado nas áreas colhidas não é automaticamente capacidade predeterminada.')
    elif nome in ('x2b_yield-sojamilho', 'x2c_aptid-sojamilho'):
        prefixo = 'yx' if nome.startswith('x2b') else 'sx'
        p.update(chave=['codigo_ibge', 'variavel_raster'], grupos=['variavel_raster'], valores=['valor_medio'],
                 unidades={'valor_medio': 'kg de matéria seca/ha' if prefixo == 'yx' else 'índice 0–10.000'},
                 selecao=f"df = df.loc[df['variavel_raster'].str.startswith({prefixo!r}, na=False)].copy()",
                 aviso='Variantes estáticas por produto e insumo, em sequeiro. Clima 1961–1990 e base de terras 2010; adequação como exposição predeterminada pendente.')
    elif nome in ('x3_infracoes', 'x3a_infracoes', 'x3d_infracoes'):
        col = {'x3_infracoes': 'n_autos_ibama_it', 'x3a_infracoes': 'n_autos_ibama_espacial',
               'x3d_infracoes': 'valor_multas_ibama_it'}[nome]
        p.update(valores=[col], unidades={col: 'R$ nominais autuados' if nome == 'x3d_infracoes' else 'autos'},
                 aviso='Base já anualizada. Falta de linha não foi convertida em zero. As variantes territorialmente informada e espacial não devem ser somadas.')
    elif nome in ('x3b_infracoes', 'x3c_infracoes'):
        p.update(chave=['SEQ_AUTO_INFRACAO'], valores=['valor_multa_nominal'],
                 unidades={'valor_multa_nominal': 'R$ nominais por auto'},
                 aviso='Registros individuais: descritivas por registro, não contagem municipal validada. Ano processado refere-se à lavratura; IDs vazios permanecem sinalizados.')
        if nome == 'x3c_infracoes':
            p['selecao'] = """comparavel = df['codigo_ibge'].notna() & df['codigo_ibge_espacial'].notna()
df['concordancia'] = 'sem correspondência'
df.loc[comparavel, 'concordancia'] = np.where(
    df.loc[comparavel, 'codigo_ibge'].eq(df.loc[comparavel, 'codigo_ibge_espacial']),
    'concordante', 'divergente')
display(df['concordancia'].value_counts(dropna=False).to_frame())"""
            p['grupos'] = ['concordancia']
    elif nome == 'x3e_infracoes':
        p.update(chave=['SEQ_TAD', 'SEQ_HIST_TAD'], valores=['n_registros_historico'],
                 unidades={'n_registros_historico': 'linhas de histórico, não embargos únicos'},
                 aviso='Análise de cobertura do histórico: ano da alteração do registro. Não há medida de embargos únicos pronta; unidades de área ainda precisam ser validadas.')
    elif nome in ('x4_pecuaria', 'x4a_pecuaria'):
        p.update(valores=['efetivo_bovino'], unidades={'efetivo_bovino': 'cabeças (estoque)'},
                 aviso='Efetivo bovino é estoque. A lotação aparente depende da compatibilidade da área de pastagem (classe 15).' if nome.startswith('x4a') else 'Estoque bovino, não produtividade ou rentabilidade.')
    elif nome == 'x6_biomas':
        cols = ['biome_amazonia_share_i', 'biome_cerrado_share_i', 'biome_pantanal_share_i']
        p.update(chave=['codigo_ibge'], valores=cols, unidades={c: 'proporção 0–1' for c in cols},
                 aviso='Frações estáticas. Os limiares de predominância são alternativas; nenhum está escolhido.')
    elif nome.startswith('x7_custo-'):
        p.update(chave=['arquivo_origem', 'aba', 'linha_excel', 'coluna_excel'],
                 valores=['n_celulas'], unidades={'n_celulas': 'células extraídas por aba'},
                 aviso='Custos ainda não construídos. Estatísticas e gráficos abaixo medem apenas cobertura da extração. Não misturar valores numéricos de células com unidades e categorias distintas.')
    elif nome == 'x8_chuva':
        p.update(chave=['codigo_ibge', 'ano', 'mes'], valores=['precip_mm'], unidades={'precip_mm': 'mm/mês'},
                 aviso='Precipitação mensal. A janela produtiva/decisória será definida antes da agregação final.')
    elif nome == 'x8_chuvaa':
        cols = ['precip_mm_anual', 'precip_anomaly_1981_2010', 'precip_anomaly_1991_2020',
                'precip_zscore_1981_2010', 'precip_zscore_1991_2020']
        p.update(valores=cols, unidades={c: 'escore adimensional' if 'zscore' in c else 'mm' for c in cols},
                 aviso='Ano civil e duas referências climáticas candidatas. Anomalia de chuva não mede balanço hídrico.')
    elif nome == 'x9_relevo':
        cols = ['elevation_mean_m', 'elevation_min_m', 'elevation_max_m']
        p.update(chave=['codigo_ibge'], valores=cols, unidades={c: 'm' for c in cols},
                 aviso='Elevação de superfície (DSM). Declividade e rugosidade não estão nesta tabela.')
    else:
        raise ValueError(f'Novo candidato {nome!r}: adicionar perfil explícito antes de gerar sua AED.')
    return p


def codigo(texto):
    return nbformat.v4.new_code_cell(textwrap.dedent(texto).strip() + '\n')


def markdown(texto):
    return nbformat.v4.new_markdown_cell(textwrap.dedent(texto).strip())


def criar_notebook(bloco, pendencias, sha):
    nome = bloco['nome']
    p = perfil(nome)
    notas = '\n'.join('- ' + s for s in bloco['notas'])
    comentarios = '\n'.join('# ' + s for s in bloco['notas'])
    arquivos = '\n'.join('- `' + s + '`' for s in bloco['caminhos'])
    intro = f"# {nome}\n\n{bloco['descricao']}\n\n{p['aviso']}\n\nFonte: `HIPOTESES TESE - CHAP1.txt`.\n\n{arquivos}\n\n**Regras específicas do dicionário**\n\n{notas}"
    intro += ('\n\n**Recorte confirmado pelo autor:** 2001–2024; referência territorial de 141 municípios. '
              'Os dados espaciais são reextraídos na malha IBGE 2023. Boa Esperança do Norte não é somada integralmente a um único município. '
              'Registros e pixels são atribuídos aos territórios anteriores; rendimentos e proporções são recalculados. '
              'Essa referência não resolve automaticamente todas as mudanças municipais anteriores a 2023.')
    cells = [markdown(intro), markdown('## FASE 1: Setup & Load\n\nExecute as células na ordem. As funções abaixo padronizam leitura e gráficos. Os arquivos originais são apenas lidos. Códigos municipais são texto; `ano` identifica o período. O hífen no nome reúne candidatos, não indica subtração.')]
    cells.append(codigo(PASTA.joinpath('aed_support.py').read_text(encoding='utf-8')))
    cells.append(codigo(f"""
RAIZ = encontrar_raiz()
CAMINHOS = {bloco['caminhos']!r}
NOME = {nome!r}
CHAVE = {p['chave']!r}
GRUPOS = {p['grupos']!r}
VALORES = {p['valores']!r}
UNIDADES = {p['unidades']!r}
sns.set_theme(style='whitegrid')
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 20)
# Todas as fontes do bloco são lidas, na ordem em que aparecem no TXT.
bases_brutas = []
for relativo in CAMINHOS:
    caminho = RAIZ / relativo.replace('\\\\', '/')
    ids = None
    if caminho.name == 'termo_de_embargo_coordenadas.csv' and bases_brutas:
        ids = set(bases_brutas[0]['SEQ_TAD'].dropna()) - {{''}}
    base = ler_csv(caminho, ids_embargo=ids)
    bases_brutas.append(base)
    print(caminho.name, '— shape:', base.shape)
    display(base.head())
    base.info()
display(pd.DataFrame(UNIDADES.items(), columns=['coluna analisada', 'significado / unidade']))
"""))
    cells.append(markdown('## FASE 2: Data Cleaning & Wrangling\n\nLimpeza conserva o histórico completo em `df` e as fontes lidas em `bases_brutas`. `painel` contém 2001–2024 quando existe ano validado. Só linhas inteiramente repetidas são retiradas; conflitos de chave e valores ausentes ficam visíveis.'))
    limpeza = comentarios + '\n' + """bases_fontes_limpas = [limpar_base(base) for base in bases_brutas]
# Os CSVs indicados no TXT foram lidos acima; a transformação territorial é explícita.
bases, MUNICIPIOS_141 = aplicar_referencia_141(bases_fontes_limpas, CAMINHOS, RAIZ)
df = bases[0].copy()
""" + p['selecao'] + """
painel = recortar(df)
analise = painel.copy()
print('Diagnóstico da chave na fonte selecionada:')
diagnosticar(df, [v for v in VALORES if v in df], CHAVE)
"""
    if nome.startswith('x7_custo-'):
        limpeza += """
# conteudo pode ser texto, custo, ano, quantidade ou coeficiente: não somar.
analise = df.groupby(['arquivo_origem', 'aba'], observed=True).size().rename('n_celulas').reset_index()
display(df[['aba', 'conteudo']].head(15))
"""
    if nome == 'x3e_infracoes':
        limpeza += """
# Cobertura do histórico por município e ano da alteração; não são novos embargos.
analise = painel.groupby(['codigo_ibge', 'ano'], observed=True).size().rename('n_registros_historico').reset_index()
display(df['DES_STATUS_FORMULARIO'].value_counts(dropna=False).to_frame())
display(df['DAT_EMBARGO'].dt.year.value_counts(dropna=False).sort_index().to_frame())
"""
    if nome == 'x3b_infracoes':
        limpeza += """
for coluna in ['TIPO_INFRACAO', 'DS_SIT_AUTO_AIE', 'SIT_CANCELADO', 'DS_ENQUADRAMENTO_ADMINISTRATIVO']:
    display(df[coluna].value_counts(dropna=False).head(15).to_frame())
display(df[['DAT_HORA_AUTO_INFRACAO', 'DT_FATO_INFRACIONAL']].isna().sum().to_frame('ausencias'))
"""
    if nome in ('x2_prodsoja-prodmilho', 'x2a_hprodsoj-hprodmil'):
        limpeza += """
# Zero de área colhida não autoriza transformar rendimento ausente em zero.
df['situacao_rendimento'] = 'rendimento registrado'
df.loc[df['rendimento_medio_kg_ha'].isna(), 'situacao_rendimento'] = 'rendimento ausente'
df.loc[df['area_colhida_ha'].eq(0), 'situacao_rendimento'] = 'área colhida registrada como zero'
display(pd.crosstab(df['produto'], df['situacao_rendimento']))
display(df['rendimento_medio_kg_ha__original'].value_counts(dropna=False).head(15).to_frame())
"""
    cells.append(codigo(limpeza))
    cells.append(markdown('## FASE 3: Estatística Descritiva Básica\n\n`ausente_na_linha` significa célula sem medida; uma combinação sem linha é outra situação. `zero_registrado` é zero presente no arquivo, ainda sujeito à validação da fonte. Ausência de cultivo não pode ser deduzida apenas de um rendimento vazio. Uma medida ainda não construída permanece explicitamente pendente.'))
    desc = """
diagnosticar(analise, VALORES, [])
display(analise[VALORES].describe().T)
if GRUPOS:
    display(analise.groupby(GRUPOS, observed=True)[VALORES].describe())
lacunas_painel(df, [c for c in GRUPOS if c in df and c != 'concordancia'])
"""
    if nome.startswith('x2a_'):
        desc += """
# Candidata histórica: mostrar o suporte anterior a 2001 antes de escolher a janela.
historico = df.loc[df['ano'].lt(2001)].copy()
display(historico.groupby('produto', observed=True)['rendimento_medio_kg_ha'].describe())
display(historico.groupby(['codigo_ibge', 'produto'], observed=True).agg(
    primeiro_ano=('ano', 'min'), ultimo_ano=('ano', 'max'),
    n_rendimentos=('rendimento_medio_kg_ha', 'count')).head(20))
"""
    if nome == 'x3d_infracoes':
        desc += "\ndisplay(painel[['n_autos_ibama_it', 'n_valores_ausentes']].describe().T)\nprint('Soma de multas pode ser parcial quando n_valores_ausentes > 0.')\n"
    cells.append(codigo(desc))
    cells.append(markdown('## FASE 4: Análise Univariada\n\nHistogramas mostram a distribuição; boxplots destacam extremos sem removê-los. Produtos, classes e cenários aparecem separados. A evolução usa medianas das observações de cada ano e mantém lacunas; ela não substitui a agregação final da fase 6. Fontes estáticas não recebem anos artificiais.'))
    if nome.startswith('x2a_'):
        cells.append(codigo("print('Distribuição dos rendimentos disponíveis antes de 2001; média histórica ainda pendente.')\ngraficos_univariados(historico, VALORES, GRUPOS, UNIDADES)\nprint('Contexto observado 2001–2024; não é a exposição histórica predeterminada.')\ngraficos_tempo(painel, VALORES, GRUPOS, UNIDADES)"))
    else:
        cells.append(codigo('graficos_univariados(analise, VALORES, GRUPOS, UNIDADES)\ngraficos_tempo(analise, VALORES, GRUPOS, UNIDADES)'))
    if nome.startswith('x2a_'):
        cells.append(codigo("""
# O gráfico pré-painel é separado do recorte candidato 2001–2024.
fig, ax = plt.subplots(figsize=(10, 4))
for produto, parte in historico.groupby('produto', observed=True):
    serie = parte.groupby('ano')['rendimento_medio_kg_ha'].median()
    ax.plot(serie.index, serie.to_numpy(dtype=float, na_value=np.nan), label=produto)
ax.set(xlabel='Ano anterior a 2001', ylabel='Mediana observada (kg/ha)', title='Suporte histórico disponível')
ax.legend()
plt.show()
plt.close(fig)
"""))
    cells.append(markdown('## FASE 5: Análise Bivariada\n\nCruze município e ano por medida e grupo disponível. Os mapas de calor mostram até 20 códigos em ordem, apenas para legibilidade; branco significa ausência. Preços globais são comparados entre produtos ou meses. Em dados estáticos, compare municípios; em CONAB, compare cobertura de abas. Essas relações são descritivas, sem interpretação causal.'))
    cells.append(codigo('graficos_bivariados(analise, VALORES, GRUPOS, UNIDADES)'))
    cells.append(markdown('## FASE 6: Feature Engineering (Tratamentos Finais)\n\nA primeira parte preserva as funções e condições da AED inicial. `None` sinaliza uma condição ainda não satisfeita; não é zero. Ao final desta fase, a seção **Passos 1 e 2 — Construção executada das variáveis** aplica o plano autorizado, documenta os parâmetros e exporta os derivados disponíveis. Ela mantém explícitas as medidas adiadas e não define uma especificação econométrica.'))
    cells.append(codigo(comentarios + '\n' + feature_code(nome)))
    cells.append(codigo("""
# A referência espacial de 141 municípios já foi aplicada na fase 2.
# O mapa abaixo serve para OUTRAS mudanças históricas de códigos, depois de validadas.
# Boa Esperança tem mais de uma origem: esse mapa 1:1 não serve para desfazer sua criação.
CORRESPONDENCIA = None
base_harmonizada = df.copy()
if CORRESPONDENCIA is not None:
    if 'ano' not in df:
        raise ValueError('Fonte estática exige correspondência da malha de referência.')
    base_harmonizada = harmonizar_codigos(df, CORRESPONDENCIA, CHAVE)
else:
    print('Referência territorial: 141 municípios, malha IBGE 2023. Outras mudanças históricas ainda exigem validação.')
    print('Não foi produzido painel econométrico final nem escolhida especificação.')
# Desmembramentos não se resolvem renomeando códigos. Não fazer junção muitos-para-muitos.
# Ao combinar fontes, usar validate e indicator e revisar municípios sem correspondência.
"""))
    cells.append(markdown('**Pendências comuns extraídas do TXT**\n\n' + '\n'.join('- ' + s for s in pendencias)))
    cells.append(codigo('\n'.join('# PENDÊNCIA: ' + s for s in pendencias)))
    cells.extend(celulas_harmonizacao(nome))
    # IDs estáveis tornam nova geração idempotente e facilitam a revisão no Git.
    for i, cell in enumerate(cells):
        cell.id = f'fase-cell-{i:02d}'
    nb = nbformat.v4.new_notebook(cells=cells)
    nb.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                   'language_info': {'name': 'python', 'version': '3.12'},
                   'aed': {'variavel': nome, 'dicionario_sha256': sha, 'periodo_confirmado': [2001, 2024],
                           'territorio': 'IBGE_2023_141', 'harmonizacao': 'passos_1_2_v1', **bloco}}
    nbformat.validate(nb)
    for cell in cells:
        if cell.cell_type == 'code':
            compile(cell.source, f'{nome}/{cell.id}', 'exec')
    return nb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sobrescrever', action='store_true', help='Substituir notebooks existentes, inclusive edições manuais e outputs.')
    args = parser.parse_args()
    blocos, pendencias = extrair_blocos(DICIONARIO)
    sha = hashlib.sha256(DICIONARIO.read_bytes()).hexdigest()
    preparados = [(PASTA / (b['nome'] + '.ipynb'), criar_notebook(b, pendencias, sha)) for b in blocos]
    # Validar tudo antes de escrever qualquer notebook.
    conflitos = [str(p.name) for p, nb in preparados if p.exists()
                 and p.read_text(encoding='utf-8') != nbformat.writes(nb) + '\n']
    if conflitos and not args.sobrescrever:
        raise SystemExit('Notebooks diferentes já existem: ' + ', '.join(conflitos)
                         + '. Revise suas edições; --sobrescrever permite regeneração explícita.')
    for caminho, nb in preparados:
        texto = nbformat.writes(nb) + '\n'
        if not caminho.exists() or caminho.read_text(encoding='utf-8') != texto:
            caminho.write_text(texto, encoding='utf-8', newline='\n')
        print(caminho.name)
    print(f'{len(preparados)} notebooks válidos em {PASTA}')


if __name__ == '__main__':
    main()
