# Retificação da introdução do chap1 após WORK-A

Data: 9 de outubro de 2026.

## Escopo e autorização

Aplicação do protocolo `/fernando`, conforme solicitação do autor para retificar os achados da WORK-A com o mínimo necessário e suficiente. Referências operacionais: `RESEARCH_PROTOCOL.md`, `STYLE_GUIDE.md` e `WORK_A_arquitetura_chap1.md`.

A intervenção científica ficou restrita a três parágrafos de `2_INTI/chapters/chap1/0_introduction.tex`. O relatório da auditoria foi preservado como registro do texto anterior. A árvore inicial estava na branch `main`, com apenas esse relatório de auditoria ainda não versionado.

## Alterações

| Achado | Localização | Retificação |
| --- | --- | --- |
| A01 — preços da terra | Linha 76 | Retirada somente a expressão “e da terra” do desdobramento empírico da pergunta, alinhando-o ao objetivo específico e a H1-a. As referências aos preços fundiários na contextualização foram mantidas. |
| A02 — contribuição | Linha 84 | Explicitada a questão a esclarecer: magnitude da relação e sua variação entre atividades e biomas. Mantida a contribuição pretendida ao debate teórico, indicando a evidência empírica como meio de esclarecer seu alcance, sem alegar ineditismo ou inexistência de estudos. |
| A03 — unidade de análise | Linha 205 | Tornado visível o município–ano como unidade candidata, já indicada nos comentários. Mantidos o período candidato, as pendências de harmonização territorial e a obtenção das conversões brutas. |
| A04 — sobreposição | Linha 84 | Substituída a repetição das tarefas analíticas pela explicação do conhecimento pretendido. Objetivos e parágrafo dos eixos conceituais foram preservados. |

Não foram acrescentadas evidências, fontes, hipóteses, equações ou novas especificações. A unidade territorial continua candidata: a alteração não resolve a harmonização nem transforma uma intenção em definição metodológica final. O trecho metodológico permanece cinza, com o escopo de cor restrito ao parágrafo.

## Validação

- Leitura integral da introdução antes da edição e conferência final do diff.
- Comparação com o texto anterior: somente as linhas 76, 84 e 205 mudaram; todas as outras linhas, inclusive hipóteses, citekeys e comentários com equações, permaneceram idênticas.
- Compilação anterior: `latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex`, exit 0.
- Compilação posterior: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`, exit 0. PDF mantido em 13 páginas.
- Sem caixas `Overfull` ou referências/citações indefinidas no log final.
- Inspeção visual das páginas 2, 3 e 5, que contêm as alterações, e das páginas 6, 10 e 11 para conferir a redistribuição do texto. Sem cortes ou sobreposição. A cor cinza termina antes do parágrafo de organização do artigo.
- Avisos preexistentes: depreciações de `babel`/`memoir` e seis ocorrências de `Underfull \\vbox`.
- Efeito novo de diagramação: uma ocorrência adicional de `Underfull \\vbox` (badness 10000) na página 10, com espaçamento vertical ampliado entre blocos após a redistribuição do texto. A página foi inspecionada; não há perda de conteúdo. Não foram alteradas outras seções ou regras globais de paginação para eliminar esse aviso.
- `git diff --check` aprovado. `git check-ignore` confirmou que os artefatos de validação em `xreports/` e o PDF compilado permanecem ignorados.

## Arquivos e estado final

- Modificado: `2_INTI/chapters/chap1/0_introduction.tex` — três linhas substituídas, correspondentes aos três parágrafos.
- Criado: `2_INTI/reports/retificacao_WORK_A_introducao_chap1.md`.
- Preservado, ainda não versionado: `2_INTI/reports/WORK_A_arquitetura_chap1.md`.
- Logs, texto anterior, extração do PDF e imagens de validação: `2_INTI/xreports/fernando_work_a_intro_20261009_150856/`.
- Nenhum commit, merge ou push. A revisão final da redação permanece com o autor.
