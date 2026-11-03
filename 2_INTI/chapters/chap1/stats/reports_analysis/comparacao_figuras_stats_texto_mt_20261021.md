# Comparação das figuras disponíveis em `stats` com a seção de Mato Grosso

**Data:** 21/10/2026. **Texto conferido:** `../../text/2_mt_descriptive.tex`.
**Escopo:** inventário recursivo dos arquivos visuais em `stats`, leitura das
chamadas LaTeX, inspeção dos PNG e dos PDF renderizados e comparação dos dados
subjacentes às versões alternativas. A comparação usa o estado atual dos
arquivos; não altera o artigo, as figuras, os dados ou os scripts.

## 1. Resultado principal

O texto incorpora **cinco figuras**, todas existentes, com legenda, rótulo e
chamada em prosa. Elas cobrem **cinco dos nove temas gráficos descritivos de
H1**: lavouras, conversão, preços, autuações e distribuição municipal da
conversão. Os quatro temas restantes — rendimento, rebanho, abate e
exportações — já aparecem, em parte, na prosa e na tabela de oferta. Portanto,
a ausência desses quatro gráficos não equivale à ausência de seus indicadores.

A seleção utiliza `fig05_lavouras.pdf` de `stats/figuras/` e quatro PDF de
`stats/descritiva/resultados_h1/figuras/`. Não utiliza diretamente as versões
em `resultados_h1_humanizado/`, os gráficos da replicação de Simões nem as
capturas de dashboards. Não foi encontrado caminho de figura inexistente ou
rótulo de figura sem chamada no texto.

Há duas oportunidades de conteúdo adicional: **quantidades físicas exportadas**,
que não constam da tabela incorporada, e **mapas de uso e cobertura em 2001 e
2017**, que acrescentariam localização espacial à caracterização municipal.
São possibilidades de seleção editorial, não exigências de incluir tudo.

## 2. Inventário e critérios de contagem

Foram localizados **117 arquivos visuais do projeto**, dos quais **58 PNG/PDF**
e **59 GeoTIFF**. Os PNG/PDF correspondem a 39 apresentações em arquivo PNG,
19 delas também exportadas em PDF. Pares de formatos e versões do mesmo tema
não foram tratados como evidências independentes.

| Conjunto, relativo a `stats/` | Apresentações/versões | Arquivos PNG/PDF | PDF efetivamente chamados |
|---|---:|---:|---:|
| `figuras/` | 9 | 18 | 1 |
| `descritiva/resultados_h1/figuras/` | 4 | 8 | 4 |
| `descritiva/resultados_h1_humanizado/figuras/` | 4 | 8 | 0 |
| `descritiva/simoes2020/outputs/figures/` | 6 | 8 | 0 |
| `DASHBOARD/pt_h1/*/previews/` | 16 capturas de tabelas | 16 | 0 |
| **Total** | **39** | **58** | **5** |

A varredura também encontrou **874 imagens/ícones em dependências instaladas**,
principalmente `.venv/` e `node_modules/`. Foram identificados no inventário
integral, mas excluídos da comparação científica: são ativos de bibliotecas,
interfaces ou testes de terceiros. Os 59 TIFF foram classificados separadamente
como dados/mapas geoespaciais, e não como 59 gráficos prontos para publicação.
Não foram procuradas figuras incorporadas somente em HTML ou notebooks, sem
arquivo de imagem exportado; esses formatos ficam fora desta contagem.

## 3. Correspondência exata das figuras chamadas no texto

Linhas referentes à versão conferida do `.tex`. A ordem abaixo é a ordem de
inclusão na seção, não a numeração embutida nos nomes dos arquivos. As outras
seções anteriores do principal não contêm `includegraphics` no estado lido.

| Ordem | Arquivo relativo a `stats/` | Rótulo LaTeX | Linha da inclusão | Linha(s) da chamada em prosa | Destino |
|---:|---|---|---:|---|---|
| 1 | `figuras/fig05_lavouras.pdf` | `fig:h1-lavouras` | 20 | 16 | Expansão agropecuária e transformação da cobertura vegetal |
| 2 | `descritiva/resultados_h1/figuras/fig01_conversao.pdf` | `fig:h1-conversao` | 41 | 37 e 106 | Expansão; retomada na heterogeneidade |
| 3 | `descritiva/resultados_h1/figuras/fig03_precos.pdf` | `fig:h1-precos` | 62 | 58 | Preços agropecuários e incentivos à conversão |
| 4 | `descritiva/resultados_h1/figuras/fig04_ibama.pdf` | `fig:h1-ibama` | 84 | 80 | Instituições ambientais e respostas aos incentivos |
| 5 | `descritiva/resultados_h1/figuras/fig02_distribuicao.pdf` | `fig:h1-distribuicao` | 110 | 106 | Heterogeneidade econômica e ambiental de Mato Grosso |

Os quatro `input` também foram identificados: macros em `numeros.tex`, tabela
de oferta, tabela de cobertura e tabela GAEZ. Eles não introduzem outras
figuras. Os três rótulos de tabela são `tab:h1-oferta-contexto`,
`tab:h1-cobertura` e `tab:h1-capacidade`.

## 4. Comparação dos nove temas descritivos de H1

| Tema e arquivos disponíveis em `figuras/` | Conteúdo efetivamente inspecionado | Situação no texto | Avaliação e ganho de eventual inclusão |
|---|---|---|---|
| `fig01_conversao.{pdf,png}` | Taxa agregada de conversão para agricultura/pastagem, 2001–2024; amostra disponível e fixa | **Figura incluída por outra versão**, em `resultados_h1`; discussão e definição do denominador nas linhas 35–49 | Tema atendido. São razões entre somas de áreas; não estoque de vegetação nem perda líquida. A versão da pasta principal seria uma substituição visual, não um tema novo. |
| `fig02_distribuicao.{pdf,png}` | Distribuição das médias temporais municipais por predominância de bioma; 39/55/1 municípios fixos | **Figura incluída por outra versão**, em `resultados_h1`; linhas 106–118 | Tema atendido. A versão original separa os pontos de modo ordenado; as alternativas espalham os pontos horizontalmente. As alturas representam o mesmo objeto e a posição horizontal não é coordenada geográfica. O único município pantaneiro não sustenta uma distribuição representativa. |
| `fig03_precos.{pdf,png}` | Índices anuais de preços reais internacionais, base 2000=100, soja/milho/carne; anos de preço 2000–2023 | **Figura incluída por outra versão**, em `resultados_h1`; linhas 58–72 | Tema atendido. O texto distingue dólares constantes de preços locais em reais e preços de retorno líquido. Não há ganho em incluir as duas versões simultaneamente. |
| `fig04_ibama.{pdf,png}` | Cobertura das contagens de Flora e média/mediana dos autos entre municípios com classificação completa | **Figura incluída por outra versão**, em `resultados_h1`; linhas 80–94 | Tema atendido. A versão principal troca cores e tipos de linha relativamente à original, com legendas correspondentes; não trocar o significado das séries ao comparar imagens. O texto delimita classificação completa, ausências, zeros e ambiguidade de fiscalização versus incidência. |
| `fig05_lavouras.{pdf,png}` | Área plantada, área colhida e produção de soja/milho, 2001–2024; duas amostras | **PDF incluído diretamente**; linhas 16–26; rendimento discutido na linha 28 | Tema atendido. As escalas são milhões de hectares ou toneladas. O texto explicita 66 municípios fixos da soja e 121 do milho e evita somar safras como expansão física da terra. O PNG é uma exportação alternativa, sem chamada própria. |
| `fig06_rendimento_agricola.{pdf,png}` | Rendimento realizado agregado, em t por hectare colhido; soja e milho; oscilações anuais | **Sem figura própria**, mas o cálculo e as pontas de 2001/2024 estão na linha 28; distinção em relação ao GAEZ nas linhas 120–125 | Cobertura textual parcial. A figura acrescentaria a trajetória intermediária, sobretudo as oscilações que uma comparação de pontas não resume. Seria a inclusão mais direta para aprofundar área versus rendimento; não mede capacidade predeterminada nem prova intensificação poupadora de terra. |
| `fig07_rebanho.{pdf,png}` | Estoque bovino em milhões de cabeças, 2001–2024, nas amostras disponível e fixa | **Sem figura própria**; crescimento discutido na linha 30 e níveis de 2001/2024 em `tab:h1-oferta-contexto` | Indicador atendido em prosa/tabela; a curva acrescentaria fases intermediárias de expansão e estabilização. Sua ausência gráfica não constitui lacuna do estoque bovino. Rebanho não equivale a pastagem, abate ou oferta anual de carne. |
| `fig08_abate_mt.{pdf,png}` | Bovinos abatidos sob inspeção e peso das carcaças; dois painéis estaduais, 2001–2024 | **Sem figura própria**; linha 30 e tabela de oferta | As duas medidas constam da tabela. A figura acrescentaria oscilações anuais e diferenças entre trajetórias, evitando reduzir tudo à variação entre pontas. O agregado é estadual e entra uma vez por ano; não deve ser somado sobre municípios. |
| `fig09_exportacoes.{pdf,png}` | Exportações de soja, milho e carne: valor FOB em US$ bilhões correntes e peso líquido em milhões de toneladas, 2001–2024 | **Sem figura própria**; valores FOB nas pontas estão na tabela e a interpretação na linha 30. **Peso líquido exportado não foi incorporado** | Cobertura parcial com ganho adicional claro: o painel físico permitiria apresentar separadamente quantidades e valores nominais. A tabela usa US$ milhões, enquanto a figura usa US$ bilhões; isso é conversão de unidade, não divergência. Domicílio fiscal não identifica origem municipal da produção. Quantidade e valor, isoladamente, não identificam lucro nem demanda causal por conversão. |

As quatro figuras sem chamada própria não foram classificadas como erros.
Sua incorporação depende do argumento e do espaço disponível. A tabela de
oferta evita repetir seis séries completas quando a finalidade é apenas
dimensionar as pontas; por outro lado, não permite visualizar mudanças de
trajetória ao longo do período.

## 5. Versões alternativas: mesma evidência, apresentação diferente

As quatro figuras iniciais aparecem em três conjuntos: `figuras/`,
`descritiva/resultados_h1/figuras/` e
`descritiva/resultados_h1_humanizado/figuras/`. Foram inspecionadas todas as
17 versões gráficas de H1, em PNG e PDF, sem presumir identidade pelo nome.

Foram comparados, com chaves identificadoras e tolerância numérica de
`1e-12`, os campos comuns de quatro CSV subjacentes:

| CSV | Chave da comparação | Linhas por conjunto | Comparações |
|---|---|---:|---|
| `conversao_anual.csv` | ano, destino, amostra | 96 | Original × principal; original × humanizado |
| `distribuicao_municipal.csv` | código IBGE, destino | 190 | Original × principal; original × humanizado |
| `precos_anuais.csv` | produto, ano do preço | 72 | Original × principal; original × humanizado |
| `ibama_anual.csv` | ano | 24 | Original × principal; original × humanizado |

**Resultado:** nenhuma diferença nas chaves, ausências e valores dos campos
comuns nas oito comparações. Foram harmonizados apenas os nomes `min/max`
para `minimo/maximo` na conferência; nenhum arquivo foi regravado.
Essa equivalência não significa que arquivos PDF/PNG sejam idênticos, nem
certifica novamente a origem geoespacial ou administrativa dos dados.

Diferenças observadas: dimensões e margens, posicionamento/cores dos pontos
de distribuição e codificação visual das séries IBAMA. Os PNG `fig01`,
`fig03` e `fig04` da pasta principal são cópias byte a byte dos respectivos
PNG humanizados, comprovadas por SHA-256. `fig02` não é cópia byte a byte:
as cores diferem, embora os dados comuns coincidam. Os PDF também não foram
classificados como cópias idênticas apenas por aparência.

**Implicação editorial:** o texto mistura conjuntos de exportação, mas essa
mistura não produziu divergência numérica detectada nos quatro temas
comparados. Eventual padronização visual deve escolher uma versão por tema,
preservando legendas, notas e rótulos; não é necessário adicionar as versões
alternativas como figuras novas.

## 6. Figuras da replicação de Simões: conteúdo adicional e limites

Diretório: `descritiva/simoes2020/outputs/figures/`. Nenhum dos oito arquivos
está chamado no `.tex`. A citação `SimoesEtAl2020`, na linha 100, é uma
referência bibliográfica e não incorpora automaticamente esses resultados.
A comparação abaixo se apoia nos arquivos locais, seu README e scripts;
não constitui nova verificação do artigo original ou dos downloads externos.

| Arquivo(s) | O que apresenta(m) | Relação com a seção atual | Avaliação |
|---|---|---|---|
| `fig5_area_comparison.{pdf,png}` | Áreas anuais de soja, milho, algodão e floresta, 2001–2017; mapas classificados versus PAM/IBGE e série derivada de PRODES | Complementaria expansão/cobertura; parte das culturas já aparece em `fig05_lavouras`, mas com outro período e outra cobertura | **Candidato secundário**, se a questão for comparação de medidas e fontes. A série PRODES-derived é ancorada na floresta classificada de 2007 e subtrai incrementos posteriores; o script a identifica como aproximação. Não é uma estimativa independente do estoque florestal inicial, nem a conversão bruta municipal de H1. |
| `fig6_land_use_2001_2017.{pdf,png}` | Painel cartográfico de uso/cobertura em 2001 e 2017, com 13 classes e sistemas de cultivo | Acrescentaria localização e configuração espacial à subseção de heterogeneidade, atualmente apoiada em agregados municipais | **Candidato prioritário entre as figuras novas**, caso se deseje acrescentar um mapa. Distinguir contexto 2001–2017 de análise H1 até 2024 e mapas de estoque de transições brutas. Não substitui a classificação municipal por bioma, nem informa efeitos heterogêneos. |
| `fig6_map_2001.png` | Mapa individual de 2001, com legenda, escala e norte | Mesmo conteúdo temporal do primeiro painel da figura combinada | Versão alternativa de apresentação. Preferir o painel combinado quando o argumento exigir comparação temporal; não incluir ambos sem ganho. |
| `fig6_map_2017.png` | Mapa individual de 2017, com legenda, escala e norte | Mesmo conteúdo temporal do segundo painel da figura combinada | Mesma avaliação do mapa de 2001. Não descreve a cobertura de 2024. |
| `demo_fig4_sinop_smoothing.png` | Demonstração de classificação SVM e suavização bayesiana em recorte de Sinop | Relaciona-se ao processamento de imagens, que não é o objeto desta descrição de H1 | **Manter fora da seção descritiva**, salvo discussão específica da replicação. O prefixo `demo_` e a documentação delimitam caráter demonstrativo; não é mapa completo do estado. O título do segundo painel aparece truncado na exportação inspecionada. |
| `demo_fig_som_map.png` | Organização de perfis NDVI em mapa SOM de demonstração, com quatro classes na legenda | Diagnóstico de qualidade/amostras de treinamento; não é mapa geográfico de uso da terra | **Manter fora da seção descritiva**. Não interpretar círculos/cores como localização territorial ou distribuição municipal. |

Os mapas/áreas de Simões e a conversão MapBiomas da seção são produtos
distintos. A classe `Forest` não corresponde, sozinha, a toda a vegetação
nativa; diferenças entre estoques não identificam destinos de conversão.
Antes de inserir esses materiais, suas fontes, classes, períodos e notas
precisam acompanhar a figura. A existência de saídas locais não autoriza
tratá-las como reprodução integral validada do estudo.

## 7. Capturas de dashboards e arquivos raster

As **16 capturas PNG** de `DASHBOARD/pt_h1/*/previews/` foram inspecionadas.
São visualizações de tabelas de coeficientes, modelos, resultados, metodologia,
absorção de regressores e diagnósticos; não curvas descritivas adicionais.

| Diretório sob `DASHBOARD/pt_h1/` | Arquivos PNG | Situação frente ao texto |
|---|---|---|
| `execucao_fe_candidatas/previews/` | `Absorção`, `Coeficientes`, `Comparação`, `Detalhes`, `Metodologia`, `Resultados` | Nenhum chamado. Resultados/diagnósticos econométricos exploratórios, sem correspondência direta às cinco figuras descritivas. |
| `execucao_ols_200/previews/` | `Coeficientes`, `Detalhes`, `Metodologia`, `Resultados` | Nenhum chamado. Capturas de tabelas de especificações OLS; não são evidência descritiva omitida. |
| `execucao_robustez_interacoes/previews/` | `Absorção`, `Coeficientes`, `Diagnósticos`, `Metodologia`, `Modelos`, `Robustez` | Nenhum chamado. Material de estimação/robustez, a ser avaliado na etapa pertinente; não transportar suas conclusões para a seção descritiva. |

Não se verificaram novamente coeficientes, testes ou decisões de especificação
dessas capturas. Sua classificação no inventário não certifica os resultados.

Os **59 GeoTIFF** estão todos sob `descritiva/simoes2020/`:

| Diretório | Quantidade | Natureza e correspondência |
|---|---:|---|
| `data/raw/pangaea/` | 17 | Mapas anuais `mt_2001_v3_1.tif` a `mt_2017_v3_1.tif`; insumos dos mapas e agregações. Não chamados diretamente. |
| `data/processed/classified/demo_sinop/` | 4 | Probabilidades/classes brutas e suavizadas da demonstração de Sinop. Não chamados. |
| `data/processed/masked/` | 19 | 17 `demo_stack_2001…2017.tif` e dois mapas `demo_mt_masked_2001/2005.tif`. Não chamados. |
| `data/processed/final/` | 17 | `demo_mt_2001.tif` a `demo_mt_2017.tif`. Produtos de demonstração, não equivalentes automaticamente aos mapas publicados. |
| `outputs/maps/` | 2 | `mt_2001_colored.tif` e `mt_2017_colored.tif`; exportações georreferenciadas coloridas dos anos também apresentados em PNG/PDF. Não chamadas no texto. |

Os TIFF foram inventariados por caminho e hash; não foi repetida uma auditoria
de pixels, projeções, classificação ou áreas. As figuras cartográficas prontas
foram inspecionadas em seus PNG/PDF.

## 8. Encaminhamentos propostos

| Prioridade | Achado | Encaminhamento sugerido, sem implementação |
|---|---|---|
| Relevante para seleção de evidência | O peso líquido das exportações aparece em `fig09`, mas não na tabela ou discussão atual | Se a finalidade for distinguir expansão física da valorização nominal, incorporar essa dimensão em uma figura selecionada ou tabela, com domicílio fiscal e unidades explícitos. |
| Relevante para caracterização territorial | A seção discute heterogeneidade e cita Simões, mas não contém mapa | Avaliar o painel `fig6_land_use_2001_2017`, delimitando o período e a diferença entre estoque e transição. É uma adição, não uma correção obrigatória. |
| Opcional | Rendimento, rebanho e abate têm séries completas disponíveis, mas o texto privilegia as pontas | Incluir somente a trajetória que sustentar um argumento específico. `fig06` é especialmente útil para não resumir rendimento apenas por 2001/2024; `fig07` e `fig08` podem permanecer representados pela tabela. |
| Menor, apresentação | Há versões alternativas com estilos distintos e três pares de PNG idênticos | Escolher uma convenção visual para futuras exportações e manter uma versão por tema no artigo; não apagar arquivos ou trocar caminhos automaticamente. |
| Fora da evidência descritiva | Capturas econométricas e demonstrações de classificação não estão no texto | Manter separadas da descrição de H1, sem apresentar sua ausência como falha de cobertura dos nove gráficos principais. |

Não se identificou falha de integração que exija trocar uma das cinco figuras
já chamadas. A decisão mais útil é selecionar qual dimensão adicional deve
ser mostrada — quantidades exportadas, trajetória de rendimento ou localização
espacial —, evitando multiplicar figuras que apenas repetem a tabela ou outra
versão do mesmo resultado.

## 9. Verificações, fontes locais e continuidade

- Todos os **39 PNG do projeto** foram inspecionados, incluindo versões e
  capturas; os **19 PDF** foram renderizados e comparados visualmente com seus
  PNG correspondentes. Não se observou divergência substantiva de conteúdo
  entre formatos do mesmo produto. A demonstração de Sinop tem o problema de
  título indicado na seção 6. Isso não afeta as cinco figuras incorporadas.
- A renderização dos PDF emitiu aviso de fonte `ArialUnicode`, mas terminou
  com código zero e produziu imagens legíveis. O aviso foi preservado no
  inventário; não foi atribuído a um erro novo do artigo.
- Cinco caminhos e cinco rótulos de figura conferidos; quatro inputs locais
  existentes; oito comparações de dados sem diferença nos campos comuns.
- Scripts consultados: `descritiva/fernando_h1/analise_descritiva_h1.R` e
  `analise_descritiva_h1v3.R`; README/config e scripts `10_fig5_area_comparison.R`
  e `11_fig6_maps.R` de `descritiva/simoes2020/`. O README original de
  `resultados_h1` ainda indica o caminho antigo do script antes de sua mudança
  para `fernando_h1`; a inspeção utilizou o caminho existente.
- A comparação foi local. Não foram executados scripts de análise,
  downloads, novas regressões ou regeneração de figuras. O LaTeX não foi
  recompilado nesta tarefa, pois nenhum `.tex` ou ativo incorporado foi
  alterado. Não foi reavaliada a sustentação bibliográfica de H1.
- As alterações locais encontradas no início, inclusive a reorganização de
  scripts e a revisão da literatura, foram preservadas. Somente este relatório
  e artefatos de auditoria foram criados. Nenhum commit, merge ou push.
- O diretório `stats/reports_analysis` foi usado por solicitação expressa.
  Continuidade e decisões desta comparação ficam centralizadas neste arquivo;
  registros técnicos permanecem em `2_INTI/audit/`.

Evidências técnicas, relativas a este relatório:

- [Inventário integral de arquivos visuais](../../../../audit/comparacao_figuras_mt_20261021/inventario_visual.json): caminhos, categorias, tamanhos, hashes e metadados de renderização; inclui os ativos de dependências identificados e excluídos.
- [Chamadas do texto](../../../../audit/comparacao_figuras_mt_20261021/chamadas_texto.json): caminhos, rótulos, legendas e linhas.
- [Comparação dos dados subjacentes](../../../../audit/comparacao_figuras_mt_20261021/comparacao_dados.json): oito comparações por chave.
- [Fontes monitoradas](../../../../audit/comparacao_figuras_mt_20261021/fontes_sha256.json) e [snapshot do texto](../../../../audit/comparacao_figuras_mt_20261021/texto_conferido.tex).
- [Índice de contatos visuais](../../../../audit/comparacao_figuras_mt_20261021/contatos.json) e prévias/renderizações na mesma pasta de auditoria.

## Anexo — catálogo dos arquivos PNG/PDF

O catálogo abaixo enumera todas as apresentações exportadas fora das
dependências. PDF e PNG com o mesmo caminho-base são agrupados na mesma linha;
o estado de inclusão refere-se ao arquivo exato, não apenas ao tema.

| Caminho-base relativo a `stats/` | Arquivos disponíveis | Inclusão no `.tex` |
|---|---|---|
| `DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Absorção` | [PNG](<../DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Absorção.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Coeficientes` | [PNG](<../DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Coeficientes.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Comparação` | [PNG](<../DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Comparação.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Detalhes` | [PNG](<../DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Detalhes.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Metodologia` | [PNG](<../DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Metodologia.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Resultados` | [PNG](<../DASHBOARD/pt_h1/execucao_fe_candidatas/previews/Resultados.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_ols_200/previews/Coeficientes` | [PNG](<../DASHBOARD/pt_h1/execucao_ols_200/previews/Coeficientes.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_ols_200/previews/Detalhes` | [PNG](<../DASHBOARD/pt_h1/execucao_ols_200/previews/Detalhes.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_ols_200/previews/Metodologia` | [PNG](<../DASHBOARD/pt_h1/execucao_ols_200/previews/Metodologia.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_ols_200/previews/Resultados` | [PNG](<../DASHBOARD/pt_h1/execucao_ols_200/previews/Resultados.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Absorção` | [PNG](<../DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Absorção.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Coeficientes` | [PNG](<../DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Coeficientes.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Diagnósticos` | [PNG](<../DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Diagnósticos.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Metodologia` | [PNG](<../DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Metodologia.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Modelos` | [PNG](<../DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Modelos.png>) | Nenhum arquivo chamado diretamente |
| `DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Robustez` | [PNG](<../DASHBOARD/pt_h1/execucao_robustez_interacoes/previews/Robustez.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/resultados_h1/figuras/fig01_conversao` | [PDF](<../descritiva/resultados_h1/figuras/fig01_conversao.pdf>); [PNG](<../descritiva/resultados_h1/figuras/fig01_conversao.png>) | PDF chamado: `fig:h1-conversao` |
| `descritiva/resultados_h1/figuras/fig02_distribuicao` | [PDF](<../descritiva/resultados_h1/figuras/fig02_distribuicao.pdf>); [PNG](<../descritiva/resultados_h1/figuras/fig02_distribuicao.png>) | PDF chamado: `fig:h1-distribuicao` |
| `descritiva/resultados_h1/figuras/fig03_precos` | [PDF](<../descritiva/resultados_h1/figuras/fig03_precos.pdf>); [PNG](<../descritiva/resultados_h1/figuras/fig03_precos.png>) | PDF chamado: `fig:h1-precos` |
| `descritiva/resultados_h1/figuras/fig04_ibama` | [PDF](<../descritiva/resultados_h1/figuras/fig04_ibama.pdf>); [PNG](<../descritiva/resultados_h1/figuras/fig04_ibama.png>) | PDF chamado: `fig:h1-ibama` |
| `descritiva/resultados_h1_humanizado/figuras/fig01_conversao` | [PDF](<../descritiva/resultados_h1_humanizado/figuras/fig01_conversao.pdf>); [PNG](<../descritiva/resultados_h1_humanizado/figuras/fig01_conversao.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/resultados_h1_humanizado/figuras/fig02_distribuicao` | [PDF](<../descritiva/resultados_h1_humanizado/figuras/fig02_distribuicao.pdf>); [PNG](<../descritiva/resultados_h1_humanizado/figuras/fig02_distribuicao.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/resultados_h1_humanizado/figuras/fig03_precos` | [PDF](<../descritiva/resultados_h1_humanizado/figuras/fig03_precos.pdf>); [PNG](<../descritiva/resultados_h1_humanizado/figuras/fig03_precos.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/resultados_h1_humanizado/figuras/fig04_ibama` | [PDF](<../descritiva/resultados_h1_humanizado/figuras/fig04_ibama.pdf>); [PNG](<../descritiva/resultados_h1_humanizado/figuras/fig04_ibama.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/simoes2020/outputs/figures/demo_fig4_sinop_smoothing` | [PNG](<../descritiva/simoes2020/outputs/figures/demo_fig4_sinop_smoothing.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/simoes2020/outputs/figures/demo_fig_som_map` | [PNG](<../descritiva/simoes2020/outputs/figures/demo_fig_som_map.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/simoes2020/outputs/figures/fig5_area_comparison` | [PDF](<../descritiva/simoes2020/outputs/figures/fig5_area_comparison.pdf>); [PNG](<../descritiva/simoes2020/outputs/figures/fig5_area_comparison.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/simoes2020/outputs/figures/fig6_land_use_2001_2017` | [PDF](<../descritiva/simoes2020/outputs/figures/fig6_land_use_2001_2017.pdf>); [PNG](<../descritiva/simoes2020/outputs/figures/fig6_land_use_2001_2017.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/simoes2020/outputs/figures/fig6_map_2001` | [PNG](<../descritiva/simoes2020/outputs/figures/fig6_map_2001.png>) | Nenhum arquivo chamado diretamente |
| `descritiva/simoes2020/outputs/figures/fig6_map_2017` | [PNG](<../descritiva/simoes2020/outputs/figures/fig6_map_2017.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig01_conversao` | [PDF](<../figuras/fig01_conversao.pdf>); [PNG](<../figuras/fig01_conversao.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig02_distribuicao` | [PDF](<../figuras/fig02_distribuicao.pdf>); [PNG](<../figuras/fig02_distribuicao.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig03_precos` | [PDF](<../figuras/fig03_precos.pdf>); [PNG](<../figuras/fig03_precos.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig04_ibama` | [PDF](<../figuras/fig04_ibama.pdf>); [PNG](<../figuras/fig04_ibama.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig05_lavouras` | [PDF](<../figuras/fig05_lavouras.pdf>); [PNG](<../figuras/fig05_lavouras.png>) | PDF chamado: `fig:h1-lavouras` |
| `figuras/fig06_rendimento_agricola` | [PDF](<../figuras/fig06_rendimento_agricola.pdf>); [PNG](<../figuras/fig06_rendimento_agricola.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig07_rebanho` | [PDF](<../figuras/fig07_rebanho.pdf>); [PNG](<../figuras/fig07_rebanho.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig08_abate_mt` | [PDF](<../figuras/fig08_abate_mt.pdf>); [PNG](<../figuras/fig08_abate_mt.png>) | Nenhum arquivo chamado diretamente |
| `figuras/fig09_exportacoes` | [PDF](<../figuras/fig09_exportacoes.pdf>); [PNG](<../figuras/fig09_exportacoes.png>) | Nenhum arquivo chamado diretamente |
