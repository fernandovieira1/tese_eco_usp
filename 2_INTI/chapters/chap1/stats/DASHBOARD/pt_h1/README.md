# H1 · Laboratório de dados

Dashboard principal de exploração do painel municipal do Capítulo 1. Integra a atenção à amostra e aos efeitos fixos do `pt_dex` com distribuições e comparações territoriais do `pt_gravity`. Os dois aplicativos anteriores permanecem preservados.

## Iniciar

Na raiz do repositório, usando o ambiente `.venv` existente:

```powershell
& '.\2_INTI\chapters\chap1\stats\DASHBOARD\pt_h1\iniciar_dashboard.ps1'
```

Abra **http://127.0.0.1:8503**. O processo inicia em segundo plano, apenas na interface local, com logs em `2_INTI/audit/dashboard_h1_runtime/`. Se a porta estiver ocupada, confira o servidor existente ou passe `-Port 8504`. Use `-Foreground` para acompanhar a execução no terminal. O script informa o PID da instância criada.

Execução direta, se preferir:

```powershell
& '.\.venv\Scripts\python.exe' -m streamlit run '.\2_INTI\chapters\chap1\stats\DASHBOARD\pt_h1\app.py' --server.address=127.0.0.1 --server.port=8503
```

Dependências e versões verificadas estão em `requirements.txt`. Não é necessário instalar scikit-learn, Kaleido ou um ambiente dentro da pasta do dashboard. O navegador exporta SVG pela câmera do gráfico; downloads HTML preservam a interatividade e incluem Plotly.

## Roteiro de exploração

1. **Visão econômica**: fluxos brutos para agricultura e pastagem, taxas ponderadas, coorte municipal constante, estoques no último ano, diferenças por bioma, ranking e Lorenz/Gini.
2. **Explorar variáveis**: definição literal do dicionário, unidade, relação com H1, estatísticas, quantis, assimetria, curtose, histograma, KDE, boxplot, violino, ECDF e barras. A unidade automática usa uma observação por ano para séries comuns e uma por município para atributos fixos verificados no painel integral. A média municipal ou anual explícita pode resumir variáveis que variam em ambas as dimensões.
3. **Qualidade e amostra**: todas as 296 colunas, ausências, não finitos, zeros, disponibilidade anual, casos completos para combinações escolhidas, suporte por bioma, flags, dicionário e dados do recorte.
4. **Séries e territórios**: agregação adequada à variável, média/mediana, soma apenas para grandezas extensivas, taxa ponderada com denominador comum, coorte constante ou disponível, N por ano, trajetória de municípios específicos e lacunas anuais explícitas.
5. **Relações e correlações**: escolha de Y/X, dispersão, binscatter, reta descritiva, Pearson/Spearman, N de cada par, amostra comum ou por pares, dimensões pooled/between/within/two-way, VIF e cruzamento guiado de preço × capacidade × registros IBAMA.
6. **Laboratório OLS**: um ou vários Xs, níveis/log/log1p/z, defasagens por ano civil, interação opcional, efeitos fixos municipais/anuais, erros clássicos/HC3/cluster municipal/ano/duas dimensões, coeficientes e IC, perdas de amostra, resíduos, QQ, influência, VIF, FWL, cenários condicionais, comparação de especificações e notebook reproduzível.
7. **Do dado ao texto**: ponte com os argumentos locais da introdução e literatura, tabela descritiva, notas do autor e caderno de evidências com CSV, LaTeX, gráficos HTML e manifestos individuais.

Os filtros globais são exclusivamente de período, bioma dominante e município. Desmarcar todos os biomas produz um recorte vazio; deixar municípios em branco significa todos os municípios dos biomas selecionados. A qualidade de Y é uma decisão visível em cada análise. A distribuição univariada preserva os casos disponíveis; a visão econômica exige cobertura completa de Y, denominador positivo e suporte comum dos dois destinos.

## Dados, catálogo e rastreabilidade

Fonte canônica lida preferencialmente em seu local original no repositório local:

`2_INTI/xdata/chap1/processed/harmonizacao/painel_notebook/paineis/painel_tese_chap1_pt.csv`

Para ambientes em nuvem ou de deploy (como Streamlit Community Cloud) nos quais a pasta `2_INTI/xdata/` é omitida pelo `.gitignore`, o carregador recorre automaticamente à cópia idêntica em `data/` (`painel_tese_chap1_pt.csv` e `municipios_referencia.json`), preservando a rastreabilidade e integridade via SHA-256.

Snapshot validado: 3.384 pares, 141 municípios, 2001–2024, 296 colunas de origem. A interface acrescenta apenas nome municipal, bioma dominante e indicador de empate. As chaves são código IBGE textual de sete dígitos e ano inteiro; os arquivos não são regravados.

O catálogo padrão contém as **176 colunas** da união das subseções **Colunas Selecionadas**, registrada em `config/selection.json`, com a lista de cada dataframe de origem. O catálogo completo pode ser ativado na barra lateral. As 176 incluem flags e metadados; a lista numérica elegível para OLS exclui flags e identificadores. A página de qualidade sempre examina todas as 296 colunas, inclusive a flag de cobertura de Y que não está entre as 176.

As definições, unidades e escalas são extraídas das células comentadas de `stats/EDA/aed_chap1_pt_DICIO.ipynb`. O catálogo é validado contra o painel. O hash das células de código de `aed_chap1_pt_ANALISE.ipynb` indica se a seleção versionada continua correspondendo ao notebook verificado. Se o código mudar, o app exibe aviso: revise a seleção, os dataframes de origem e o hash no JSON; não atualize apenas o hash para suprimir o aviso.

O cache inclui caminho, tamanho e data de modificação do painel, dicionário, cadastro municipal, seleção, notebook, textos e módulo de leitura. Manifestos de download registram SHA-256, filtros, configuração, versões e código. Mudanças nos textos geram aviso para revisão da ponte argumentativa. O caderno conserva **o contexto próprio de cada evidência**, mesmo quando o recorte global muda. Escolhas analíticas e notas são preservadas ao navegar entre páginas. Não há salvamento silencioso na tese; baixe os pacotes para persistir a sessão.

## Convenções científicas e limites

- Não há imputação de zeros, winsorização, exclusão automática de outliers ou seleção de variáveis por p-valor. Não finitos são tratados como indisponíveis nos cálculos e contados na qualidade.
- Frações permanecem frações no cálculo e nos CSV. Apenas gráficos explicitamente rotulados em `%` multiplicam por 100. Carne bovina está em US$/kg; soja e milho em US$/t. O app não constrói razões de preços em unidades incompatíveis.
- Fluxo bruto anual não é variação líquida de estoque. A soma dos fluxos ao longo dos anos não representa necessariamente área física única. A taxa ponderada é soma de fluxos/soma de vegetação inicial nos mesmos pares, uma taxa anual ponderada por exposição.
- Bioma dominante é a maior fração municipal, sem implicar exclusividade. A validação do domínio usa tolerância numérica de 1e-10, como no pt_dex: frações podem exceder 1 por arredondamento da soma espacial, sem serem alteradas ou renormalizadas. Empates usam Amazônia, Cerrado, Pantanal, nessa ordem, e são informados. N pequenos, especialmente no Pantanal, limitam comparações.
- A coorte completa exige os anos solicitados para as variáveis em análise; não usa apenas os anos que sobreviveram a uma exclusão. As séries mantêm lacunas explícitas.
- Dentro de município e município+ano: projeção por efeitos fixos na **mesma amostra**. Para painéis desbalanceados, o cálculo two-way usa projeções alternadas até convergência, não uma única subtração de médias. Variáveis absorvidas são zeradas dentro da tolerância e não produzem correlações numéricas espúrias.
- OLS com efeitos fixos usa dummies explícitas. Especificações sem posto completo, com Xs constantes/absorvidos, Y sem variação, graus de liberdade insuficientes ou um único cluster são bloqueadas com mensagem. Nenhum regressor é descartado silenciosamente. Isso inclui componentes de interações absorvidos: revise a especificação de maneira consciente; as interações já construídas no painel podem ser selecionadas diretamente.
- Cluster utiliza correções de amostra finita e graus de liberdade da inferência clusterizada, com t; poucos clusters geram aviso. HC3 não corrige por si só dependência serial/espacial. Covariância cluster em duas dimensões pode produzir diagonal negativa/erros-padrão indefinidos; o app avisa e essa inferência deve ser revista.
- VIF e condição são diagnósticos, não escolhas automáticas de método. FWL usa a amostra e os controles do modelo completo; a inferência vem dele.
- Cenários alteram um X transformado e mantêm os demais valores do par escolhido. Alterações fora da faixa marginal geram aviso; estar dentro das faixas não garante suporte conjunto. Logs não são automaticamente revertidos.
- PAM observada e GAEZ potencial são conceitos diferentes. IBAMA representa registros administrativos, com endogeneidade e cobertura próprias, não uma medida direta de eficácia. Descrição, correlação e OLS não confirmam H1 nem identificam causalidade.
- O app prepara o trabalho em notebooks. Não escolhe a especificação final, estratégia de identificação, modelo para proporções/contagens ou testes sofisticados pelo autor. Não inclui mapas geográficos por não introduzir outra malha sem validação territorial; comparações são por bioma e município.

## Reprodução em notebook próprio

O ZIP de cada modelo contém a matriz efetivamente estimada, amostra transformada, especificação, coeficientes, diagnósticos, perdas e `reproduzir_ols.ipynb`. Extraia o pacote e execute o notebook na pasta extraída: ele refaz o ajuste e confere coeficientes/erros-padrão. Isso reproduz o modelo exportado; alterar filtros, transformações ou defasagens exige partir novamente do painel integral.

Dentro do repositório:

```python
from pathlib import Path
import sys

raiz = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / '2_INTI/RESEARCH_PROTOCOL.md').is_file())
sys.path.insert(0, str(raiz / '2_INTI/chapters/chap1/stats/DASHBOARD/pt_h1'))
from h1lab.data import load_data
from h1lab.models import fit_model

painel, catalogo, fonte = load_data()
filtros = {'years': [2001, 2024],
           'biomes': ['Amazônia', 'Cerrado', 'Pantanal'], 'municipalities': []}
especificacao = {'y': 'taxa_conversao__agricultura',
                'xs': ['rendimento_medio_kg_ha_lag1__Soja (em grão)'],
                'fe': 'none', 'cov': 'cluster_entity', 'require_y': True}
resultado = fit_model(painel, filtros, especificacao)
resultado['coefficients']
```

O exemplo é uma especificação demonstrativa, não a especificação recomendada da tese. Para ampliar o modelo, confira as definições e a adequação científica das variáveis.

## Validação e origem dos componentes

`h1lab/panel_metrics.py`, `economic_metrics.py` e `presentation.py` reutilizam cálculos já testados do `pt_dex`. As novas camadas de catálogo, métricas, OLS, exportações e interface são independentes dos apps antigos. O `pt_gravity` orientou as comparações territoriais, distribuição e concentração.

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
& '.\.venv\Scripts\python.exe' -m pytest '.\2_INTI\chapters\chap1\stats\DASHBOARD\pt_h1\tests' -q
```

Testes numéricos usam painel sintético desbalanceado, regressão explícita independente com dummies, covariâncias, limites de domínio e dados reais. Testes `AppTest` exercitam páginas, controles, regressões, gráficos, estados vazios e evidências. O notebook exportado é executado de ponta a ponta. Logs e relatório desta entrega: `2_INTI/audit/dashboard_h1_20261017/`.

Documentação primária de apoio: [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest) e [statsmodels: covariâncias robustas](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html).
