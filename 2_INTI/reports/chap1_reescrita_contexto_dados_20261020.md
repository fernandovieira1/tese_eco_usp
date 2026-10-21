# Capítulo 1 — reescrita de Mato Grosso: Contexto e Dados

## Escopo e formulação vigente

Solicitação: reescrever `chapters/chap1/text/2_mt_descriptive.tex` em cinco
subseções, articulando revisão, descrição e H1; última subseção com dois
parágrafos. O arquivo recebido continha somente o título e `sec:dados`.
`text/main.tex` compila `0_introduction`, `1_literature_review`, a seção de dados
e `3_econometrics_strategy`, usando `library.bib`, `abntex2cite`, `graphicx` e
`placeins`. A estratégia contém texto provisório, sem especificação operacional.

Formulações extraídas da introdução vigente, preservadas como referência:

- **Problema (REF5):** “Como os retornos econômicos esperados e o ambiente
  institucional condicionam a taxa de conversão da vegetação nativa em Mato
  Grosso, e em que medida essa relação varia conforme a capacidade produtiva
  local da terra, as atividades agropecuárias e os biomas?”
- **Objetivo geral (REF6):** “investigar como e com que intensidade os
  determinantes observáveis do retorno econômico esperado e o ambiente
  institucional se relacionam com as taxas de conversão da vegetação nativa em
  Mato Grosso”. Específicos: construir conversão bruta por destino; examinar
  preços × capacidade predeterminada; parametrizar condicionamento institucional
  com limites causais; verificar heterogeneidade entre atividades e biomas.
- **H1 (REF7):** “Elevações nos retornos econômicos esperados dos usos
  agropecuários aumentam a taxa de conversão da vegetação nativa, sendo essa
  resposta, ceteris paribus, amplificada pela capacidade produtiva local da terra
  e modulada pela efetividade do ambiente institucional.”
- A introdução explicita dimensões empíricas, não sub-hipóteses autônomas.
  Heterogeneidade tampouco constitui hipótese separada (REF10). H2 e apropriação
  irregular/especulativa não integram esta revisão.

## Matriz que orientou a redação

Os caminhos de resultados abaixo são relativos a `chapters/chap1/stats/`.

| Subseção da literatura | Argumento relevante | Evidência disponível | Arquivo e localização | Interpretação permitida | Limitação | Destino |
|---|---|---|---|---|---|---|
| 1.1 Expansão agropecuária, retornos privados e custos públicos | Rendas privadas e valor social da vegetação podem divergir (Angelsen) | Aumento de área, produção, rebanho e abate; exportações | `figuras/fig05_lavouras`; `dados/oferta_resumo_2001_2024.csv`, 17 linhas | Dimensionar atividade mercantil e separar margens de expansão | Não mede lucro, externalidades ou bem-estar; áreas de safras podem se sobrepor | 1ª |
| 1.1; complemento de 1.4 | Crescimento produtivo pode coexistir com menor desmatamento (Macedo; VanWey) | Conversão bruta por destino; 91,6% da soma observada para pastagem; queda das taxas entre pontas | `descritiva/resultados_h1/figuras/fig01_conversao`; `dados/conversao_anual.csv`, amostra fixa/2001/2024 | Reconhecer coexistência de crescimento produtivo e redução das taxas; distinguir abertura de reorganização | Coortes diferentes; não estima terra poupada nem substituição pastagem–lavoura | 1ª |
| 1.2 Preços agropecuários e incentivos à conversão | Preços e capacidade modificam incentivos; resposta depende do uso substituído (Berman; Bragança) | Índices reais com movimentos distintos; preços finais acima da base, conversão final abaixo | `descritiva/resultados_h1/figuras/fig03_precos`; `dados/precos_anuais.csv`, 2000/2012/2023 | Contrastar com uma leitura mecânica de H1; distinguir nível, preço relativo e exposição local | USD real internacional não é retorno líquido; sem inferência causal de tendências | 2ª |
| 1.3 Instituições e respostas aos incentivos | Monitoramento e implementação podem conter conversão (Assunção et al.) | Autos Flora, cobertura, média e mediana condicionais | `descritiva/resultados_h1/figuras/fig04_ibama`; `dados/ibama_anual.csv`, 2001–2024 e 2018/2024 | Descrever registros de atuação administrativa e sua assimetria | Autuações endógenas, classificação incompleta, ausências; sem pagamentos ou medida integral de governança | 3ª |
| 1.4 Situação econômica e ambiental de Mato Grosso | Trajetórias e biomas distintos (Simões et al.) | Cobertura por predominância; dispersão municipal da conversão | `descritiva/resultados_h1/tabelas/tab01_cobertura`; `figuras/fig02_distribuicao`; `dados/distribuicao_municipal.csv` | Qualificar médias e delimitar suporte territorial | Município não é polígono de bioma; 39/55/1 municípios fixos; Pantanal não representativo | 4ª |
| 1.4 em articulação com 1.2 | Possibilidades produtivas variam territorialmente | GAEZ alto insumo/sequeiro, mediana e quartis municipais | `descritiva/resultados_h1/tabelas/tab02_capacidade`; `dados/tabela_capacidade.csv` | Descrever cenário físico distinto do rendimento realizado | Matéria seca; terras 2010; não predeterminação garantida; falta capacidade pecuária validada | 4ª |
| Síntese das quatro | Investigar condicionamento dos incentivos, sem equiparar produção a conversão | Resultados anteriores e lacunas de suporte | Seção reescrita; introdução REF5–REF10 e metodologia | Delimitar o que descrição reconhece e o que exige investigação | Estratégia operacional ainda não redigida; H1 não confirmada/rejeitada | 5ª, dois parágrafos |

## Seleção, comparabilidade e fontes

Foram selecionados cinco gráficos: lavouras da v3; conversão, preços, IBAMA e
distribuição municipal da versão original. Todos foram inspecionados como
imagens e tiveram os cálculos relevantes reconstruídos. Duas tabelas originais
(cobertura e GAEZ) foram reutilizadas. Uma tabela derivada reúne seis indicadores
de pecuária/exportações, sem modificar seus valores ou fontes. Os gráficos
separados de rendimento, rebanho, abate e exportações foram dispensados para
evitar repetição: a informação pertinente entra em prosa ou na tabela compacta.

Os nove CSV originais possuem valores equivalentes aos campos correspondentes
da v3: tolerância numérica de 1e-12, mesmas ausências e identificadores. A v3
acrescenta colunas diagnósticas e renomeia `min/max` para `minimo/maximo`.
Os PNG não são byte-idênticos: diferem em dimensões, margens e algumas escolhas
gráficas. Os scripts confirmam a mesma construção estatística; a escolha das
quatro figuras originais preserva o conjunto já integrado às notas e tabelas.
Não houve escolha por resultados mais favoráveis a H1.

Metadados examinados: dicionários original e ampliado, README dos resultados,
scripts `analise_descritiva_h1.R` e `analise_descritiva_h1v3.R`, construção das
transições em `AED/pt/harmonizacao_terra.py` e deflação em
`AED/pt/harmonizacao_economia.py`. Foi lido integralmente o texto vigente da
introdução e da revisão, o principal, a estratégia e o backup da seção anterior
como referência de convenções, sem restaurá-lo sobre a versão recebida.

As fontes bibliográficas mantêm as chaves existentes. Foram conferidos trechos
pertinentes nas páginas dos artigos, sem tratar esse acesso como auditoria
integral de seus dados ou identificação:

- [Angelsen (2010)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2993393/): enquadramento de rendas agrícola/florestal e limites de extrapolar intensificação para conservação.
- [Macedo et al. (2012), artigo em PDF](https://lerf.eco.br/img/publicacoes/2011_2411%20Decoupling%20of%20deforestation%20and%20soy%20production%20in%20the%20southern%20Amazon%20during%20the%20late%202000s.pdf): resumo/trechos sobre produção, desmatamento e terras já abertas; o acesso direto ao PMC encontrou CAPTCHA. Não se reproduziu o percentual de 91% do artigo.
- [VanWey et al. (2013)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3638434/): resumo e introdução sobre duas safras, infraestrutura e mercados.
- [Berman et al. (2023)](https://www.sciencedirect.com/science/article/pii/S0095069623000372): resumo e introdução, preços internacionais, aptidão e diferenças locais; não se transplantaram magnitudes estimadas.
- [Bragança (2018)](https://www.cambridge.org/core/journals/environment-and-development-economics/article/effects-of-croptobeef-relative-prices-on-deforestation-evidence-from-the-tapajos-basin/8F13F6F7944F3204E3B5CCD233CB9B3C): resumo, desenho e resultados sobre preço relativo e substituição de usos.
- [Assunção, Gandour e Rocha (2023)](https://www.aeaweb.org/articles?id=10.1257/app.20200196): resumo editorial sobre DETER, nuvens e fiscalização. A seção não equipara contagem de autos a esse desenho.
- [Simões et al. (2020)](https://www.nature.com/articles/s41597-020-0371-4): resumo indexado da página editorial, mapas 2001–2017; abertura direta redirecionou ao serviço de autenticação. Somente esse alcance sustenta a referência.

## Pendências substantivas preservadas

A introdução ainda declara pendentes conversões brutas já disponíveis nesta
base. Sua especificação econométrica continua anunciada, e a seção seguinte
tem apenas texto provisório. Não foram reescritas. A transição usa o desenho
geral anunciado (painel, ordenação temporal, efeitos fixos e interações), sem
prometer instrumentos, testes ou identificação causal ainda não definidos.

A classificação por predominância não reparte conversão entre biomas; a
compatibilidade histórica das séries municipais permanece limitada. As
amostras fixas não são iguais entre produtos ou à de conversão. Não há medida
validada de capacidade pecuária, predeterminação integral garantida do GAEZ,
medida de efetividade institucional, lucro ou custos sociais. Exportações são
por domicílio fiscal, em FOB nominal; abate é estadual e sob inspeção.

O uso de `reports/` e `thread/` decorre da indicação expressa nesta solicitação,
em exceção à convenção padrão de relatórios em `audit/`. Inventário, snapshots,
cálculos, manifestos, diff e logs permanecem em `audit/reescrita_mt_20261020/`.

## Arquivos entregues e elementos incorporados

- Reescrito: `chapters/chap1/text/2_mt_descriptive.tex`, mantendo título e
  `sec:dados`, com as cinco subseções solicitadas e H1 reproduzida literalmente.
- Criado: `chapters/chap1/stats/tabelas/tab_contexto_oferta_h1.tex`, derivado de
  `stats/dados/oferta_resumo_2001_2024.csv`. O procedimento está em
  `audit/reescrita_mt_20261020/conferir_evidencias.py`.
- Relatório: este arquivo. Continuidade: `thread/chap1_contexto_dados_20261020.md`.
- Compilação principal conferida: `audit/reescrita_mt_20261020/final/main.pdf`.
  O PDF habitual na pasta de texto não foi sobrescrito.

| Elemento no artigo | Arquivo, relativo a `chapters/chap1/stats/` | Rótulo |
|---|---|---|
| Figura 1, lavouras | `figuras/fig05_lavouras.pdf` | `fig:h1-lavouras` |
| Figura 2, conversão | `descritiva/resultados_h1/figuras/fig01_conversao.pdf` | `fig:h1-conversao` |
| Figura 3, preços | `descritiva/resultados_h1/figuras/fig03_precos.pdf` | `fig:h1-precos` |
| Figura 4, IBAMA | `descritiva/resultados_h1/figuras/fig04_ibama.pdf` | `fig:h1-ibama` |
| Figura 5, distribuição municipal | `descritiva/resultados_h1/figuras/fig02_distribuicao.pdf` | `fig:h1-distribuicao` |
| Tabela 1, pecuária/exportações | `tabelas/tab_contexto_oferta_h1.tex` | `tab:h1-oferta-contexto` |
| Tabela 2, cobertura | `descritiva/resultados_h1/tabelas/tab01_cobertura.tex` | `tab:h1-cobertura` |
| Tabela 3, capacidade | `descritiva/resultados_h1/tabelas/tab02_capacidade.tex` | `tab:h1-capacidade` |

A numeração acima corresponde ao PDF conferido; o LaTeX utiliza apenas rótulos
e referências automáticas. O arquivo original `tabelas/numeros.tex` fornece
as macros quantitativas reutilizadas. Não foram modificados gráficos,
tabelas originais, dados, scripts de análise, introdução, revisão,
estratégia ou bibliografia.

## Verificações e resultado

1. **Dados e aritmética:** passaram as conferências de taxas por destino,
   denominadores, agregações anuais, coortes fixas, médias municipais,
   rendimento produção/área, índices de preços e defasagem, contagens IBAMA,
   cobertura territorial, medianas e quartis GAEZ. As pontas de oferta foram
   reconstruídas a partir da base selecionada: rebanho em coorte fixa,
   exportações apenas onde há registro e abate estadual contado uma vez por
   ano. Variações percentuais e unidades da tabela derivada foram conferidas.
   Os valores sem arredondamento estão em `numeros_verificados.json`;
   asserções e resultado, em `conferir_evidencias.py` e `evidencias.log`.
2. **Estrutura e integração:** cinco títulos exatos, sem subsubseções;
   síntese com dois parágrafos de prosa; H1 idêntica à introdução; sete chaves
   bibliográficas existentes; cinco imagens e quatro inputs encontrados;
   todos os oito elementos chamados no texto. Evidência: `estrutura.json`.
   As quatro primeiras subseções retomam explicitamente suas correspondentes
   na revisão. Conectivos acompanhados: conforme 0, contudo 0, também 2,
   ainda 0 e portanto 2 em toda a seção.
3. **Auditoria estática:** `python 2_INTI/audit_thesis.py --chapters chap1
   --skip-compile` retornou **ERROR=0, WARNING=0**. A compilação foi executada
   separadamente sobre o principal real, para usar os caminhos existentes de
   figuras. Log em `auditoria_estatica.log`; relatório do auditor em
   `audit/audit_thesis_20261021T021536_087193Z/report.md` (identificador em UTC).
4. **Compilação e inspeção:** `latexmk -norc -pdf -interaction=nonstopmode
   -halt-on-error -file-line-error`, executado em `chapters/chap1/text/`, com
   saída em `audit/reescrita_mt_20261020/final/`, produziu o principal com
   **30 páginas**. A seção ocupa as páginas **16–26**, renderizadas e
   inspecionadas. Figuras, tabelas, fontes, notas, caracteres e referências
   ficaram legíveis, sem recortes ou sobreposições. Foram ajustadas barreiras
   de flutuação e penalidades de linhas isoladas, restritas à seção.
5. **Avisos separados:** tanto a compilação anterior à edição quanto a final
   têm os dois avisos preexistentes de `babel`/`memoir` sobre comandos
   obsoletos. Nenhuma tem `Overfull` ou referências indefinidas. Avisos
   `Underfull vbox` passaram de 11 para 14, relativos à distribuição vertical
   das páginas, sem impedir a compilação ou comprometer a leitura verificada.
   A primeira extração textual emitiu aviso de fonte `ArialUnicode`; as
   extrações e renderizações finais concluíram sem esse aviso e sem perda
   visual de caracteres. Logs de comparação em `baseline/` e `final/`.
6. **Preservação:** conferência SHA-256 de 95 arquivos originais encontrou
   alteração apenas no `.tex` solicitado. As mudanças locais prévias em R,
   Rmd, script de oferta, backup e resultados humanizados foram preservadas.
   Snapshot, manifesto e diff estão na pasta de auditoria; estado final do
   Git em `git_status_final.txt`. Não foram executadas regressões nem feitos
   commit, merge ou push.

O texto distingue evidência, resultados atribuídos à literatura e interpretação.
Os contrastes de preços, produção e conversão qualificam a leitura agregada;
não constituem confirmação ou rejeição de H1. As pendências substantivas acima
permanecem explícitas e delimitam o desenvolvimento da estratégia econométrica.
