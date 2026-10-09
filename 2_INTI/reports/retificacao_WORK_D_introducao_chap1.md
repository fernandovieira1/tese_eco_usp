# Retificação da introdução do chap1 após WORK-D

Data: 09/10/2026.

## Escopo e alterações

Aplicação dos cinco ajustes locais autorizados pelo autor em `/fernando`, seguindo `AGENTS.md`, `RESEARCH_PROTOCOL.md`, `STYLE_GUIDE.md` e `WORK_D_coesao_chap1.md`.

A intervenção ficou restrita a cinco parágrafos e dois comentários de `2_INTI/chapters/chap1/0_introduction.tex`. Foram feitas oito substituições locais nas linhas 24, 54, 57, 75, 82, 195 e 205, sem reorganizar parágrafos.

| Achado | Localização | Retificação mínima |
|---|---|---|
| D01 — renda da terra | Linha 57 | Retirada somente a alternativa “ou na renda da terra”. A frase passou a retomar os preços agropecuários, mantendo a definição de retorno esperado e o mecanismo econômico nos demais trechos. Não se equiparou renda fundiária a retorno esperado, nem se acrescentou variável. |
| D02 — sínteses sobrepostas | Linha 54 | Encurtada a última frase para remeter às diferenças de resposta apresentadas na frase anterior. Preservada a síntese conceitual da linha 51 e toda a evidência citada. |
| D03 — encadeamento e repetição | Linha 82 | Substituído o encadeamento “e porque, por sua vez” por um novo período iniciado por “Por sua vez”. Na apresentação da intertemporalidade, retirada a repetição de “as condições produtivas”, já explicitada na relação de retroação. Mantidos os três eixos, o mecanismo e o limite sobre efeitos econômicos futuros. |
| D04 — formulações repetidas | Linhas 195 e 205 | A segunda ocorrência próxima de “por si sós” foi substituída pela formulação “evidência suficiente”, preservando a ressalva causal. No resumo metodológico, “Esses procedimentos” retoma a ordenação temporal, os efeitos fixos e os controles da frase anterior. Mantida a interpretação associativa quando não houver identificação defensável. |
| D05 — comentários desatualizados | Linhas 24 e 75 | Corrigida a enumeração dos biomas para Amazônia, Cerrado e Pantanal e alinhado o comentário às três dimensões da pergunta. Mantidos os dois desdobramentos H1-a e H1-b. |

Hipóteses, equações comentadas, objetivos, referências, citekeys, metodologia candidata e demais seções foram preservados. As citações mantêm uma referência por chamada. Não houve adição de evidência ou alteração do grau de certeza. As pendências metodológicas registradas na WORK-C continuam pendentes; esta etapa foi editorial.

## Validação

- Compilação anterior: `latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex`, exit 0.
- Compilação posterior: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`, exit 0; PDF mantido em 13 páginas.
- Sem citações/referências indefinidas e sem caixas `Overfull` no log final.
- Avisos preexistentes: depreciações de `babel`/`memoir` e seis ocorrências de `Underfull \\vbox`.
- Efeito novo de diagramação: uma ocorrência adicional de `Underfull \\vbox`, badness 1248, na página 10, após a redistribuição do texto. A página foi inspecionada; há espaçamento vertical entre blocos, sem corte ou sobreposição. Não foram alteradas regras globais de paginação ou outras seções para eliminar o aviso.
- Inspeção visual das páginas 2, 3, 4, 5 e 10: texto legível, hipóteses preservadas, citações renderizadas e cor cinza encerrada antes da organização do artigo.
- Comparação com a cópia anterior confirmou somente as sete linhas indicadas e preservação integral das chamadas de citação.
- Hashes SHA-256 confirmaram que os demais `.tex` e `.bib` sob `2_INTI/chapters/` e o `CLAIMS_LEDGER.csv` ficaram idênticos.
- `git diff --check` sem erros. Artefatos de validação e PDF permanecem ignorados pelo Git.

## Arquivos e estado final

- Modificado: `2_INTI/chapters/chap1/0_introduction.tex`.
- Criado: `2_INTI/reports/retificacao_WORK_D_introducao_chap1.md`.
- Artefatos locais: `2_INTI/xreports/fernando_work_d_intro_20261009_161154/` — cópia anterior, hashes, logs, diff, extração textual e imagens.
- Branch `main`; alterações preexistentes e os sete relatórios anteriores não rastreados preservados. Sem commit, merge ou push.
