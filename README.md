<!--
SUYANA: Esperança
INTI: Sol
-->

# Tese de Doutorado

> Programa de Pós-Graduação em Economia — FEARP/USP
> **Doutorando:** Fernando Souza de Vieira
> **Orientador:** Prof. Dr. Alexandre Chibebe Nicolella
> **Período:** 2025–2028

## Apresentação

Este repositório reúne os textos, dados, códigos e demais materiais de trabalho da tese de doutorado em Economia na FEARP/USP.

Na etapa INTI, o esforço está concentrado no desenvolvimento de dois artigos empíricos, que servirão de base à qualificação. O **Artigo 1 examina H1**, sobre retornos econômicos, instituições e conversão da vegetação. O **Artigo 2 examina H2**, sobre vegetação previamente existente, choques climáticos e produtividade agrícola.

O **Artigo 3 será definido em etapa posterior**, a partir dos mecanismos e questões que emergirem dessas investigações.

## Eixo geral da pesquisa

A tese investiga a interdependência entre economia e meio ambiente. Sua ideia central é que o estado ambiental não constitui apenas uma consequência da atividade econômica: ele também pode modificar as condições produtivas, os retornos econômicos e, por essa via, decisões posteriores dos agentes.

O mecanismo geral pode ser sintetizado em duas direções complementares:

1. retornos econômicos e instituições influenciam as decisões de conversão ou conservação da vegetação e, portanto, a evolução do estoque ambiental; e
2. o estoque de vegetação pode alterar as condições biofísicas da produção e a resposta da produtividade agrícola a choques climáticos, afetando os resultados econômicos que fundamentam decisões subsequentes.

Essa relação envolve três dimensões transversais: a **endogeneidade ambiental**, pois economia e meio ambiente se afetam mutuamente; a **governança territorial**, uma vez que regras, fiscalização e incentivos operam sobre agentes e territórios heterogêneos; e a **intertemporalidade**, porque decisões presentes de uso da terra modificam condições ambientais relevantes para a produção futura.

## Estrutura prevista da tese

### Artigo 1 — H1: retornos, instituições e conversão

O artigo investiga como retornos econômicos e instituições se relacionam com as decisões de conversão da vegetação em Mato Grosso. Seu projeto LaTeX está em `2_INTI/chapters/chap1/main.tex`.

**H1:** a taxa de conversão de vegetação nativa para usos agropecuários aumenta quando se eleva o retorno econômico esperado desses usos.

- **H1-a:** a resposta da conversão aos preços depende da capacidade produtiva local da terra.
- **H1-b:** o ambiente institucional condiciona a resposta da conversão aos retornos esperados.

As diferenças entre atividades e biomas integram a análise de heterogeneidade. A estratégia prevê dados em painel, exposição territorial aos preços, medidas institucionais e suas interações. A interpretação causal depende da identificação e não decorre automaticamente da inclusão de efeitos fixos ou defasagens.

### Artigo 2 — H2: vegetação, clima e produtividade

O artigo investiga se o estoque prévio de vegetação modifica a resposta da produtividade agrícola aos choques climáticos em Mato Grosso. Seu projeto LaTeX está em `2_INTI/chapters/chap2/main.tex`.

**H2:** a resposta da produtividade agrícola aos choques climáticos varia, em magnitude economicamente relevante, conforme o estoque de vegetação previamente existente no território.

- **H2-a:** a magnitude dessa modificação é heterogênea entre biomas.

Não se impõe previamente que a vegetação atenue os efeitos dos choques. A estratégia prevê interações entre clima e vegetação anterior, efeitos fixos e análises de heterogeneidade e robustez. A anterioridade da vegetação não resolve, por si só, sua endogeneidade.

Os artigos examinam elos complementares da relação entre economia e meio ambiente. Sua separação permite explicitar os problemas de mensuração e identificação de cada mecanismo; não equivale à estimação conjunta de todo o circuito de retroalimentação.

### Artigo 3 — a definir

O terceiro artigo, cuja realização e escopo ainda estão em aberto, é pensado como uma investigação teórica de natureza dedutiva, voltada à formulação de proposições econômicas e ao exame de suas implicações a partir de pressupostos explícitos. Sua execução está condicionada ao que artigos 1 e 2 demonstrarão, bem como a articulação teórica e empírica entre eles.

## Organização do repositório

| Diretório                 | Conteúdo                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------- |
| `1_SUYANA/`              | Materiais históricos da etapa de elaboração do projeto de pesquisa               |
| `2_INTI/`                | Materiais da fase atual de pesquisa e da qualificação                             |
| `2_INTI/chapters/chap1/` | Artigo relativo a H1 e bibliografia própria                                        |
| `2_INTI/chapters/chap2/` | Artigo relativo a H2 e bibliografia própria                                        |
| `2_INTI/xdata/chap1/`    | Dados locais pertinentes a H1                                                       |
| `2_INTI/xdata/chap2/`    | Dados locais pertinentes a H2                                                       |
| `2_INTI/xdata/catalog/`  | Metadados, registros de aquisição e proveniência dos dados                       |
| `2_INTI/reports/`        | Relatórios consolidados, decisões, validações e marcos relevantes               |
| `2_INTI/xreports/`       | Logs e outros artefatos automáticos ou reproduzíveis, locais e ignorados pelo Git |
| `2_INTI/thread/`         | Registros de continuidade entre tarefas e agentes                                   |

Os dados ativos permanecem em `2_INTI/xdata/`, a fonte canônica local dos dados da tese.

Cada capítulo tem um projeto LaTeX independente, com a mesma estrutura de arquivos e configuração ABNT.

Na pasta do respectivo capítulo, compile com:

```powershell
latexmk -pdf -synctex=1 -interaction=nonstopmode -halt-on-error main.tex
```

O histórico de evolução dos arquivos versionados pode ser consultado nos commits. O mecanismo de backup integral do projeto é o Restic, conforme definido no protocolo de pesquisa.

As diretrizes para o uso de IA neste trabalho estão documentadas em [AGENTS.md](AGENTS.md), no [protocolo de pesquisa](2_INTI/RESEARCH_PROTOCOL.md) e no [guia de estilo](2_INTI/STYLE_GUIDE.md).

<!-- ***
SUYANA: Esperança
INTI  : Sol
-->
