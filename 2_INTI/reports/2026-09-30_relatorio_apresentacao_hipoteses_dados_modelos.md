# Relatório de execução — apresentação de hipóteses, dados e modelos

**Data:** 30/09/2026  
**Ferramenta:** Codex, pdfLaTeX (TeX Live 2025), Poppler  
**Objetivo:** preparar e revisar uma apresentação Beamer para discussão acadêmica do desenho empírico, sem estimar regressões nem tratar especificações candidatas como finais.

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

Na revisão solicitada pelo autor, foram modificados o .tex, o PDF, este relatório e o registro de continuidade. Os demais arquivos do projeto foram preservados. A compilação também mantém auxiliares com o mesmo prefixo e extensões .aux, .log, .nav, .out, .snm e .toc, ignorados pelo Git. A tentativa anterior de removê-los foi rejeitada pela política automática da ferramenta.

## Estrutura final

**Nove slides:** 1 capa; 2 problema e dois mecanismos segundo as linhas 81–87 da introdução; 3 H1 e H1-a com a ideia intuitiva de como investigá-las; 4 H1-b, comparação proposta e cautela sobre fiscalização; 5 conversão, produção e capacidade da terra; 6 preços e instituições; 7 H2 e H2-a com as comparações propostas; 8 dados de H2; 9 síntese das tarefas necessárias para responder às perguntas.

Os slides 5 e 6 mantêm a coluna explicativa logo após **Variável / insumo**, agora intitulada **O que significa** e redigida para uma audiência que não acompanha a pesquisa. O quadro técnico de modelos foi retirado: a lógica das comparações aparece sob cada hipótese. A frase de fonte no slide 2 e o box **Escopo da apresentação** foram removidos. O fechamento usa dois blocos análogos aos das hipóteses, sem fixar o período econométrico.

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

CEPEA e IMEA permanecem sem aquisição útil de preços locais. A consulta de preços CONAB depende de CAPTCHA; planilhas de custos foram extraídas, mas ainda não formam série comparável. MMA/CAR carecem de cobertura histórica útil. ERA5-Land não foi adquirida. Os períodos nos slides descrevem a cobertura de cada fonte. Nenhuma data de início ou fim da amostra econométrica foi escolhida.

## Pendências preservadas

Harmonização territorial histórica; transições brutas entre classes MapBiomas; taxonomia e denominador da conversão; fonte, frequência e defasagem dos retornos; validade temporal do GAEZ; construção e vigência das medidas institucionais; janela agrícola e definição do choque climático; interpretação dos símbolos SIDRA; suporte amostral de Pantanal e municípios mistos. Fiscalização pode reagir ao desmatamento. As especificações de painel e erros agrupados por município são pontos de partida, e a identificação causal continua aberta.

## Compilação e inspeção

O PDF revisado foi compilado com pdfLaTeX em duas passagens, sem erro nem avisos de transbordamento, e contém **9 páginas 16:9**. As nove páginas foram renderizadas com Poppler e inspecionadas visualmente quanto a legibilidade, tabelas, rodapé, numeração, símbolos e alinhamento. Os quadros de dados preservam fonte, período e situação de cada variável, com descrições mais diretas.

## Estado do Git

Branch inicial e final da revisão: main. O git status --short estava vazio no início desta revisão. O estado final deve mostrar apenas o .tex, o PDF, este relatório e o registro de continuidade modificados. Os auxiliares LaTeX são ignorados pelo Git. Nenhum commit, push, merge ou troca de branch foi executado nesta revisão.
