# Correção da citação de Alston — capítulo 1

- A citação em `0_introduction.tex:46` já usa a chave correta; a entrada faltava na bibliografia ativa indicada por `main.tex`.
- Incorporada a entrada `alstonTitlesConflictLand1999` do backup indicado pelo autor em `2_INTI/chapters/chap1/library.bib`, mantendo a chave e os metadados, com `date = {1999}` adaptado para `year = {1999}` para compatibilidade com BibTeX/abntex2.
- O texto da introdução e o backup não foram alterados nesta tarefa. Ambos já tinham alterações locais na branch `main` antes da execução.
- Compilação em cópia isolada: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`, código 0. BibTeX sem warnings; nenhuma citação indefinida. Texto extraído do PDF confirma `ALSTON; LIBECAP; MUELLER, 1999` e a referência completa.
- Avisos de depreciação do babel (`brazil`) e memoir (`settocpreprocessor`) dizem respeito à configuração existente, sem relação com a entrada incorporada.
- Artefatos: `2_INTI/xreports/citacao_alston_20261008/build/`, confirmado como ignorado pelo Git.
- Sem commit, merge ou push.
