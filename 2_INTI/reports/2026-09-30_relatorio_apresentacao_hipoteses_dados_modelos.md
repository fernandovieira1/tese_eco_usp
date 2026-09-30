# Relatório de execução — apresentação de hipóteses, dados e modelos

**Data:** 30/09/2026  
**Ferramenta:** Codex, pdfLaTeX (TeX Live 2025), Poppler  
**Objetivo:** preparar uma nova apresentação Beamer para discussão acadêmica do desenho empírico, sem estimar regressões nem tratar especificações candidatas como finais.

## Fontes consultadas

- Introdução e revisão em 2_INTI/chapters/chap1/0_introduction.tex e 1_literature_review.tex, para formulação vigente das hipóteses e mecanismo.
- Relatório 2_INTI/reports/2026-09-30_relatorio_auditoria_h1_h2_para_feedback.md, para disponibilidade, períodos e pendências.
- Código e PDF da apresentação anterior em 2_INTI/presentations/topicos_micro/Apresentacao 24092026 - Hipoteses e RL/, para identidade visual.
- Arquivos processados e brutos relativos a PAM, PPM, MapBiomas 10.1, CHIRPS v2, GAEZ v4, IBAMA, Pink Sheet e topografia em 2_INTI/data/.
- A revisão de literatura fundamentou as menções discretas a Redhead et al. (2020) e Dell et al. (2014).

## Arquivos produzidos

- 2_INTI/presentations/topicos_micro/topicos_micro_dados_modelos.tex
- 2_INTI/presentations/topicos_micro/topicos_micro_dados_modelos.pdf
- Este relatório.
- 2_INTI/thread/2026-09-30_codex_apresentacao_hipoteses_dados_modelos.md

Nenhum arquivo preexistente foi modificado. A compilação também criou arquivos auxiliares com o mesmo prefixo e extensões .aux, .log, .nav, .out, .snm e .toc. A tentativa de removê-los foi rejeitada pela política automática da ferramenta. Esses arquivos permanecem no diretório e são ignorados pelo Git.

## Estrutura final

**Nove slides:** 1 capa; 2 problema e mecanismo em Mato Grosso; 3 H1, H1-a, H1-b e variáveis; 4 dados de H1; 5 modelos candidatos de H1; 6 H2, H2-a e variáveis; 7 dados de H2; 8 modelo de H2 e estado dos dados; 9 fechamento.

As variáveis centrais apresentadas são conversão bruta de vegetação para usos agropecuários, retorno econômico esperado e seus determinantes observáveis, ambiente institucional, rendimento de soja, choque climático, estoque vegetal prévio e bioma. As interações explicitam H1-a, H1-b, H2 e H2-a.

## Dados, períodos e decisões

| Fonte | Período ou referência confirmado | Papel e limite |
|---|---|---|
| IBGE/PAM | 1974–2025 | Produção de soja e milho; rendimento de soja candidato. Cobertura municipal variável e símbolos SIDRA por revisar. |
| IBGE/PPM | 1974–2024 | Bovinos; 2025 não retornou. |
| MapBiomas 10.1 | 1985–2024 | Estoque nativo candidato. Conversões brutas total, agricultura e pastagem ainda não construídas. |
| CHIRPS v2 | 1981–2025, 540 meses | Chuva, anomalia, déficit, excesso e z-score candidatos, por ora em ano civil. |
| FAO/GAEZ v4 | Clima 1961–1990 | Aptidão/rendimento potencial candidatos. Base de terras inclui 2010, impedindo tratar a medida como automaticamente predeterminada desde 1985. |
| World Bank Pink Sheet | Jan. 1960–ago. 2026 | Preços internacionais mensais em USD nominais; transmissão local por definir. |
| IBAMA | 1987–2026; 2026 parcial | 52.991 autos de MT; medida institucional e interpretação causal pendentes. |
| IBGE biomas 2019 / malha 2024 | Corte espacial | Predominância de 80% candidata; sensibilidades de 70% e 90%. |
| Copernicus GLO-90 | Corte espacial | Elevação disponível; declividade e rugosidade não inferidas. |
| ZARC/MAPA/CONAB | Documento safra 2025/26 | Não oferece calendário histórico completo. |

CEPEA e IMEA permanecem sem aquisição útil de preços locais. A consulta de preços CONAB depende de CAPTCHA; planilhas de custos foram extraídas, mas ainda não formam série comparável. MMA/CAR carecem de cobertura histórica útil. ERA5-Land não foi adquirida. O intervalo **1986–2024** aparece apenas como janela potencial de vegetação defasada e precipitação, não como amostra econométrica final.

## Pendências preservadas

Harmonização territorial histórica; transições brutas entre classes MapBiomas; taxonomia e denominador da conversão; fonte, frequência e defasagem dos retornos; validade temporal do GAEZ; construção e vigência das medidas institucionais; janela agrícola e definição do choque climático; interpretação dos símbolos SIDRA; suporte amostral de Pantanal e municípios mistos. Fiscalização pode reagir ao desmatamento. As especificações de painel e erros agrupados por município são pontos de partida, e a identificação causal continua aberta.

## Compilação e inspeção

O PDF foi compilado com pdfLaTeX em duas passagens, sem erro, e contém **9 páginas 16:9**. Restaram dois avisos tipográficos de caixa horizontal inferiores a 5 pt nos slides 3 e 6; as renderizações não mostram texto cortado. As nove páginas foram renderizadas com Poppler e inspecionadas visualmente quanto a legibilidade, tabelas, equações, rodapé, numeração, símbolos e alinhamento. O slide 4 e o slide 7 foram compactados para preservar as fontes e os períodos sem cortar conteúdo.

## Estado do Git

Branch inicial e final: main. O git status --short inicial estava vazio. O status final mostra quatro entradas não rastreadas: o .tex, o PDF, este relatório e o diretório 2_INTI/thread/ contendo apenas o registro desta tarefa. Os auxiliares LaTeX são ignorados pelo Git. Nenhum commit, push, merge ou troca de branch foi executado.
