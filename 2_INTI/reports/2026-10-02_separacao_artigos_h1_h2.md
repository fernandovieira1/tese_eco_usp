# Separação dos artigos da fase INTI

**Data:** 2 de outubro de 2026.

## Organização dos textos

O capítulo 1 passa a examinar H1, H1-a e H1-b: retornos esperados, capacidade produtiva, ambiente institucional e conversão da vegetação. O capítulo 2 passa a examinar H2 e H2-a: estoque prévio de vegetação, resposta da produtividade aos choques climáticos e heterogeneidade entre biomas. A numeração das hipóteses permanece vinculada à tese.

Os dois projetos mantêm a organização do artigo original: `main.tex`, `_abstract.tex`, introdução, revisão da literatura, contexto e dados, estratégia econométrica, discussão e considerações finais, além de bibliografia e opções de citação próprias. O capítulo 2 utiliza a mesma classe, margens e convenções de apresentação do capítulo 1.

A introdução e a revisão originais forneceram o texto de partida. Os parágrafos sobre incentivos, instituições e conversão foram destinados principalmente ao capítulo 1; aqueles sobre vegetação, clima e produtividade, ao capítulo 2. Os elementos de capital natural e heterogeneidade territorial pertinentes aos dois mecanismos foram mantidos nos dois artigos, com adaptação de escopo. As seções antes preenchidas com texto demonstrativo foram desenvolvidas como desenho de pesquisa para qualificação.

O README geral foi atualizado porque ainda apresentava H1 e H2 no primeiro artigo e o segundo artigo como indefinido. O terceiro artigo continua em aberto. A formulação da tese permanece mais ampla que os testes empíricos propostos para cada capítulo.

## Preservação do trabalho anterior

Antes das alterações, foram copiados os diretórios `chap1` e `chap2`, o README e o `.gitignore` para `2_INTI/backup/2026-10-02_separacao_h1_h2/`. A cópia inclui a alteração local que já existia em `0_introduction.tex`. Os hashes dos arquivos preservados constam de `hashes_originais.csv` nesse diretório.

O `.gitignore` do usuário não foi editado nesta tarefa. Não foram realizados commit, push ou troca de branch.

Para o estilo, a principal referência foi a prosa original fornecida no próprio capítulo. A habilidade Writing Style foi consultada, mas a busca não retornou o material específico do vínculo `browser-skill` indicado. Não foi atribuída ao conteúdo desse vínculo uma leitura que não ocorreu.

## Cuidados conceituais

1. **Hipóteses sujeitas a refutação.** A preocupação com os limites dos instrumentos ambientais orienta as perguntas. Evidências de eficácia institucional e resultados contrários às previsões também devem compor a análise.
2. **Regras e aplicação territorial.** A legislação não deve ser descrita como absolutamente uniforme. O art. 12 da [Lei nº 12.651/2012](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12651compilado.htm) já diferencia exigências de Reserva Legal por localização e formação vegetal, com exceções. Amazônia Legal e bioma Amazônia são recortes distintos. A construção empírica requer a regra vigente em cada período.
3. **Capital natural e externalidades.** A contribuição produtiva da vegetação pode coexistir com serviços cujos benefícios ultrapassam a propriedade. Tratar a natureza como elemento produtivo não elimina, por definição, as externalidades.
4. **Governança local.** Heterogeneidade territorial pode informar o desenho de políticas, mas os modelos propostos não identificam, por si só, a superioridade causal de uma escala de governança.
5. **Expectativas e intertemporalidade.** A ordenação temporal das variáveis preserva o mecanismo econômico, mas não equivale à estimação das expectativas dos agentes nem de um modelo dinâmico completo.
6. **Interação não é efeito causal automático.** Efeitos fixos e variáveis defasadas não eliminam toda a endogeneidade da fiscalização, da localização produtiva ou da vegetação. Os resultados precisam ser interpretados sob as condições de identificação efetivamente sustentadas.

## Condições que interferem na pesquisa

O período **2001–2024** foi preservado como janela candidata, conforme a escolha anterior do autor registrada na apresentação de 30 de setembro. A amostra efetiva dependerá da integração e validação das fontes.

| Questão | Consequência para os artigos |
|---|---|
| Conversão bruta ainda não construída | H1 depende de transições de uma mesma coleção; variação líquida do estoque não substitui a variável de interesse. |
| Geografia de 141 e 142 municípios | Os códigos e limites precisam ser harmonizados, inclusive para Boa Esperança do Norte, Sorriso e Nova Ubiratã. |
| GAEZ com base de terras de 2010 | Aptidão não é automaticamente predeterminada para todo o período candidato. |
| Preços locais e custos incompletos | Preços internacionais e capacidade produtiva são medidas candidatas; não equivalem diretamente ao retorno líquido esperado. |
| Autos, multas e embargos | Autuação não equivale a pagamento; fiscalização pode responder à conversão. Exige-se reconstrução temporal e interpretação institucional. |
| CHIRPS em ano civil | H2 requer compatibilizar os choques com o calendário agrícola e com a anterioridade do estoque vegetal. |
| Temperatura não adquirida | Não se devem anunciar análises de temperatura ou extremos diários como já viáveis. |
| Pantanal e municípios mistos | A cobertura agrícola e o pequeno número de unidades podem limitar a comparação entre biomas. |
| Serviços produtivos e instrumentos econômicos | Os dados atuais não permitem concluir diretamente sobre a eficácia de PSA, créditos de carbono ou green bonds. |

As seções de discussão e considerações finais apresentam o plano de interpretação e as contribuições esperadas. Não foram estimadas regressões nem produzidos resultados econométricos nesta tarefa.

## Fontes e dados

As tabelas de obras, pesquisadores, links primários, alcance da verificação e ajustes das citações estão em:

- [Auditoria das fontes do capítulo 1](auditoria_fontes_chap1.md).
- [Auditoria das fontes do capítulo 2](auditoria_fontes_chap2.md).

As sínteses de literatura anexadas serviram para localizar os estudos; não foram tratadas como substitutas das fontes originais. A auditoria distingue leitura de texto integral, resumo editorial e metadados. Essa distinção delimita o alcance de cada verificação.

A distribuição das bases, as cópias compartilhadas, os caminhos atualizados e a verificação de integridade estão descritos em [Organização dos dados por capítulo](organizacao_dados_chap1_chap2.md). Os registros históricos de aquisição permanecem em `data/catalog`, acompanhados de um mapa de relocação para os caminhos atuais.

## Validação final

| Verificação | Capítulo 1 | Capítulo 2 |
|---|---:|---:|
| Obras citadas e com linha de auditoria | 39 | 25 |
| Entradas na bibliografia do artigo | 39 | 25 |
| Citações sem entrada bibliográfica | 0 | 0 |
| Referências internas sem destino | 0 | 0 |
| Páginas do PDF compilado | 23 | 20 |
| Avisos de texto ultrapassando as margens | 0 | 0 |

Os projetos foram compilados com pdfLaTeX e BibTeX, por meio de `latexmk`, no TeX Live 2025. Os PDFs foram renderizados e suas 43 páginas inspecionadas. Foram mantidas as margens e convenções do projeto, acrescentando paginação contínua e abertura das referências sem impor uma folha vazia. Os arquivos SyncTeX foram regenerados para permitir a navegação entre fonte e PDF. A compilação final incorporou o refinamento do teste conjunto de H1-b; as cinco páginas afetadas foram novamente renderizadas e inspecionadas.

A revisão das equações completou os termos inferiores da interação entre preços, capacidade e instituições em H1. Em H2, distinguiu choques padronizados pela dispersão local de choques em escala comum de milímetros, além de separar razões de respostas, diferenças em pontos percentuais e tradução em quilogramas por hectare. Essas correções afetam a interpretação dos futuros resultados, sem antecipá-los.

A correspondência entre citações, bibliografia, tabelas de auditoria, entradas LaTeX e PDFs está registrada em [validacao_artigos_h1_h2.json](validacao_artigos_h1_h2.json). Os dez trabalhos com DOI presentes nas duas bibliotecas têm metadados bibliográficos concordantes. O conteúdo dos 18 arquivos do backup inicial permanece idêntico aos hashes registrados, incluindo a versão anterior do `.gitignore`.

Nos dados, foram verificados **3.009 destinos**, referentes a **1.512 arquivos realocados e 1.497 cópias compartilhadas**, sem divergências de SHA256. Os **12 testes substantivos de dados** passaram. O teste de imutabilidade de todo o checkpoint antigo foi excluído justificadamente, pois esta tarefa altera os artigos e os caminhos dos scripts; seu baseline não foi modificado.

A política automática bloqueou a remoção dos diretórios antigos vazios (`data/raw`, `data/interim` e `data/processed`). Eles foram mantidos. Essa limpeza não altera a localização dos dados nem a validação das novas pastas.
