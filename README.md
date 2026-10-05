<!-- 
SUYANA: Esperança
INTI: Sol 
-->

# Tese de Doutorado — Fase INTI

> Programa de Pós-Graduação em Economia — FEARP/USP
> **Doutorando:** Fernando Souza da Vieira
> **Orientador:** Prof. Dr. Alexandre Chibebe Nicolella
> **Período:** 2025–2028

## Apresentação

Este repositório reúne os textos, dados, códigos e demais materiais de trabalho da tese de doutorado em Economia na FEARP/USP. A pesquisa encontra-se atualmente na fase **INTI** e está sendo estruturada no formato de três artigos.

Nesta etapa, o esforço está concentrado no desenvolvimento de dois artigos empíricos, que servirão de base à qualificação. O **Artigo 1 examina H1**, sobre retornos econômicos, instituições e conversão da vegetação. O **Artigo 2 examina H2**, sobre vegetação previamente existente, choques climáticos e produtividade agrícola. O **Artigo 3 permanece a definir**, a partir dos mecanismos e questões que emergirem dessas investigações.

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

O terceiro artigo também dependerá dos resultados do Artigo 1 e de sua articulação com o Artigo 2. As alternativas atualmente consideradas são um segundo desenvolvimento teórico ou uma análise normativa voltada ao desenho e à focalização territorial de políticas de conservação.

## Organização do repositório

| Diretório    | Conteúdo                                       |
| ------------- | ----------------------------------------------- |
| `1_SUYANA/` | Materiais produzidos no Projeto da pesquisa     |
| `2_INTI/` | Materiais da fase atual de pesquisa e da qualificação |
| `2_INTI/chapters/chap1/` | Artigo relativo a H1 e bibliografia própria |
| `2_INTI/chapters/chap2/` | Artigo relativo a H2 e bibliografia própria |
| `2_INTI/data/chap1/` | Dados e cópias compartilhadas pertinentes a H1 |
| `2_INTI/data/chap2/` | Dados e cópias compartilhadas pertinentes a H2 |
| `2_INTI/data/catalog/` | Registros históricos de aquisição e rastreabilidade |
| `2_INTI/reports/` | Auditorias das fontes, organização dos dados e pendências |

## Estado dos artigos e compilação

Os textos constituem projetos para qualificação. As seções finais apresentam o plano de análise e os limites da contribuição; não contêm resultados econométricos produzidos nesta etapa. A disponibilidade de arquivos não equivale à existência de uma amostra pronta para estimação. As lacunas de dados e identificação estão explicitadas em cada artigo e nos relatórios.

Cada capítulo tem projeto independente, com a mesma estrutura de arquivos e configuração ABNT. Na pasta do respectivo capítulo, compile com:

```powershell
latexmk -pdf -synctex=1 -interaction=nonstopmode -halt-on-error main.tex
```

As fontes citadas estão documentadas em `2_INTI/reports/auditoria_fontes_chap1.md` e `2_INTI/reports/auditoria_fontes_chap2.md`. A versão anterior à separação, incluindo as alterações locais que já existiam, foi preservada em `2_INTI/backup/2026-10-02_separacao_h1_h2/`.

Títulos, estratégias empíricas e a composição do Artigo 3 poderão ser revistos conforme o avanço das duas investigações e as discussões de orientação.


<!-- ***
SUYANA: Esperança
INTI  : Sol
-->
