# Dashboard do Capítulo 1 — H1

Aplicação local Streamlit para explorar o painel municipal de Mato Grosso, comparar proxies e estimar especificações candidatas de efeitos fixos. O CSV fornecido é somente lido. Os tratamentos, filtros e interações acontecem em memória; as exportações são downloads solicitados pelo usuário.

## Executar

Nesta máquina, o ambiente `.venv` do próprio dashboard já está instalado e validado. No PowerShell, na pasta `pt_dex`:

```powershell
& '.\.venv\Scripts\python.exe' -m streamlit run app.py
```

Ou execute `iniciar_dashboard.ps1`. O endereço padrão é `http://localhost:8501`.

Para recriar o ambiente com Python 3.12:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m streamlit run app.py
```

O carregamento procura primeiro o caminho absoluto solicitado e depois o CSV junto de `app.py`, com um último fallback relativo ao diretório de execução. A assinatura de data/tamanho do arquivo invalida o cache quando o CSV é atualizado.

## Organização

- `app.py`: filtros globais, indicadores, estado e oito abas, preservando as cinco análises originais.
- `src/data_loader.py`: leitura, tipos, bioma, sete blocos teóricos e tratamento IBAMA.
- `src/panel_metrics.py`: descritivas, projeções within, correlações e VIF.
- `src/econometric_lab.py`: TWFE, comparação de especificações e hierarquia das interações H1-b.
- `src/dashboard_views.py`: controles e resultados das cinco abas.
- `src/presentation.py`: agregação temporal, binscatter e exportação LaTeX.
- `src/economic_metrics.py`: distribuições na unidade natural, retrato econômico, cruzamentos e projeção parcial multivariada.
- `src/economic_views.py`: leitura econômica guiada pelas distribuições e associações observadas.
- `tests/test_dashboard.py`: testes numéricos independentes, dados reais e interface Streamlit.
- `tests/test_economic_analysis.py`: testes da ampliação econômica, suas unidades e seus controles interativos.

## Leitura econômica, univariada e multivariada

As três primeiras abas acrescentam um percurso econômico às análises originais:

- **Retrato econômico:** fluxos por destino, taxas relativas ao estoque nativo inicial, composição entre agricultura e pastagem, diferenças por bioma, concentração municipal e evolução dos estoques. A opção de coorte constante evita atribuir à dinâmica uma troca de municípios entre anos. Os estoques anuais usam sua própria coorte constante, cujo N é mostrado, e a mudança líquida não é chamada de conversão bruta.
- **Distribuições:** histograma, distribuição acumulada, quantis, média, mediana, dispersão, caudas, frequência de zeros e intensidade entre valores positivos. Preços comuns contam uma vez por ano; capacidade fixa, climatologias e geografia contam uma vez por município no modo automático. As médias por município/ano são opções distintas. Log1p é uma escala visual opcional, e valores negativos excluídos do gráfico são contabilizados sem alterar dados ou estatísticas.
- **Relações econômicas:** células de capacidade × preço, opcionalmente separadas por registros do IBAMA; diferenças entre regimes de preços e trajetórias dos grupos; gráficos de regressão parcial e comparação entre relação bruta e ajustada na mesma amostra. A magnitude também aparece como contraste linear entre P25 e P75 de X, em pontos percentuais de Y. No modo TWFE, seu IC 95% vem do modelo completo com cluster municipal.

Os grupos de capacidade são quantis dos municípios, sem separar empates artificialmente; regimes de preço usam a mediana dos anos, sem multiplicar o peso de um preço pelos municípios observados naquele ano. Com Δln, regime alto/baixo se refere ao crescimento do preço, não ao seu nível. Classes institucionais são zero, registros positivos até a mediana e positivos acima da mediana; não recebem rótulos de fiscalização eficaz/ineficaz. A coorte constante dos cruzamentos exige todas as variáveis selecionadas válidas em todos os anos; mesmo nela, municípios podem mudar de classe institucional.

As interpretações são calculadas a partir do recorte ativo. Não pressupõem confirmação de H1-a/H1-b. Hectares, taxas, estoques e participação nos dois destinos têm significados diferentes. O fluxo somado ao longo dos anos pode incluir reconversões e não mede hectares únicos nem perda acumulada do estoque. FWL retira os mesmos efeitos e controles de X e Y em casos completos comuns; as comparações associativas não constituem identificação causal.

As unidades de capacidade foram verificadas no CSV e na construção: `capacidade_valor__*gaez_sx*` mantém o índice 0–10.000; GAEZ yx é kg de matéria seca/ha; PAM é kg/ha; `capacidade_z__*` está em desvios-padrão. Preços da carne estão por kg e soja/milho por tonelada. A transformação sx/10.000 existente em outro derivado da AED não é confundida com a coluna de capacidade em valor neste CSV.

## Convenções analíticas

O recorte inicial exige `y_cobertura_completa=True` e exclui denominador zero. A imputação IBAMA começa desligada. Cada opção pode ser alterada na barra lateral; os resultados antigos do laboratório são ocultados quando a amostra ou a especificação muda.

Bioma dominante é o maior valor entre as três frações municipais. Essa classificação não transforma a conversão municipal em uma medida intrabioma. Empates usam Amazônia, Cerrado, Pantanal nessa ordem e recebem flag; frações incompletas ou inválidas permanecem sem classificação. Na base fornecida há 76 municípios classificados como Amazônia, 61 como Cerrado e quatro como Pantanal.

Zero no IBAMA só substitui NaN quando a flag de ausência de registro identificada é verdadeira. As variáveis `lag1` usam a flag do ano civil anterior, vinculada antes dos filtros. Como o CSV começa em 2001, NaNs defasados daquele ano ficam preservados. Ausências sem essa flag, valores existentes e contagens/somas parciais não são reescritos. O relatório da aba 1 mostra os números antes e depois. `log1p` cria colunas separadas; valores negativos, se existentes, ficam ausentes no log e são auditados.

Os desvios são amostrais (`ddof=1`). Between é o desvio das médias municipais sem ponderação. Within usa `x_it − média_i + média geral`. Em painel desbalanceado, não se deve somar os quadrados desses três desvios como uma identidade de decomposição. Número de municípios com observações repetidas acompanha a tabela.

O ajuste two-way usa projeções alternadas convergidas na amostra efetivamente utilizada, inclusive após filtros e exclusão de extremos. O binscatter calcula quantis por grupo; a reta usa observações individuais. Os filtros de outliers/alavancagem afetam somente o gráfico e não as regressões do laboratório.

As regressões usam `PanelOLS`, efeitos de município e ano, cluster municipal, `debiased=True`, `group_debias=True` e `auto_df=True`. Preços comuns são absorvidos pelo ano e capacidade fixa pelo município. Absorção e colinearidade são informadas; nenhuma estimativa fictícia é atribuída aos termos removidos. Em dependências exatas, preserva-se a primeira regressora identificável na ordem da especificação. Os coeficientes são exibidos nas unidades originais, mesmo com padronização numérica interna.

A interação tripla usa a hierarquia completa `P + C + Z + P×C + P×Z + C×Z + P×C×Z`. As medidas de IBAMA são comparadas em especificações alternativas. O laboratório permite comparar cada proxy de capacidade separadamente ou combinar as selecionadas. Amostra comum é o padrão, e a opção por amostras próprias explicita a mudança de N. R² Within municipal e R² após os dois efeitos fixos são apresentados separadamente. IC e p-valores seguem a distribuição t com graus de liberdade residuais do PanelOLS.

Taxas temporais ponderadas somam conversões e denominadores nos mesmos pares válidos; a alternativa é a média simples das taxas municipais. Áreas são somadas somente nas observações disponíveis. Preços e IBAMA no segundo eixo são médias municipais disponíveis, com suporte amostral visível. As curvas não implicam cobertura comum automaticamente.

O laboratório é de pré-seleção: os textos científicos da tese permanecem inalterados. A endogeneidade da fiscalização, o suporte reduzido do Pantanal, a seleção da PAM e a validade temporal dos cenários GAEZ limitam a interpretação. Os dados não permitem inferir retorno líquido ou efetividade institucional diretamente. Resultados descrevem associações condicionais, sem validação automática de causalidade.

## Testes e auditoria

Na raiz deste dashboard:

```powershell
& '.\.venv\Scripts\python.exe' -X utf8 -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' -m compileall -q app.py src tests
& '.\.venv\Scripts\python.exe' -m pip check
```

Os resultados da entrega, schema, hashes, versões instaladas, fontes técnicas e decisões de continuidade ficam em `2_INTI/audit/dashboard_pt_dex/`. O projeto inteiro `chap1/stats` já é ignorado pelo Git conforme a configuração existente do repositório; nenhuma regra de versionamento foi alterada.

As tabelas `.tex` são fragmentos UTF-8 e usam `\usepackage{booktabs}` no documento de destino. Tabelas com muitas variáveis/modelos podem exigir orientação paisagem ou seleção de menos colunas para publicação.
