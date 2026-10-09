# Retificação da introdução do chap1 após WORK-C

Data: 09/10/2026.

## Escopo

Aplicação dos ajustes textuais autorizados pelo autor em `/fernando`, com intervenção mínima na introdução. Foram seguidos `AGENTS.md`, `RESEARCH_PROTOCOL.md`, `STYLE_GUIDE.md` e o parecer `WORK_C_metodo_inferencia_chap1.md`.

A WORK-C distinguiu decisões metodológicas pendentes de problemas de redação e recomendou não transferir a especificação completa do método para a introdução. A retificação atende aos limites de interpretação que podem ser explicitados nesta etapa; não apresenta as oito questões metodológicas como resolvidas por alterações de prosa.

## Alterações

Somente duas linhas/parágrafos de `2_INTI/chapters/chap1/0_introduction.tex` foram modificados:

| Localização | Alteração | Relação com a WORK-C |
|---|---|---|
| Linha 195 — interpretação de H1-b | Acrescentada uma frase que distingue diferenças observadas de resposta entre condições institucionais dos efeitos causais de mudanças nessas instituições. | C03: a heterogeneidade observada não identifica automaticamente o efeito de uma intervenção institucional. |
| Linha 205 — resumo metodológico | Acrescentadas duas frases: ordenação temporal e efeitos fixos não asseguram identificação causal; quando suas condições não puderem ser sustentadas, os resultados terão interpretação de associações condicionais. | C01 e encaminhamento introdutório da seção 5 da auditoria: explicitar o nível de inferência admissível sem prometer identificação já estabelecida. |

Todo o texto anterior desses dois parágrafos foi preservado. Não foram acrescentadas referências, nem alteradas hipóteses, fórmulas, equações comentadas, objetivos, unidade/período candidatos ou demais seções. O escopo de cor cinza continua restrito ao resumo metodológico. As retificações das WORK-A e WORK-B permanecem intactas.

## Pendências metodológicas preservadas

- C02: definição do índice e de seu efeito de interesse. A linha 158 já distingue a implicação observável de H1 da estimação direta do retorno líquido esperado.
- C04–C05: calendário, defasagens e escolha/validação da exposição produtiva. Não foi selecionada uma alternativa apenas para preencher a introdução.
- C06–C07: construção das conversões, denominadores, harmonização territorial, regra para biomas e suporte amostral. As ressalvas já existentes nas linhas 127, 198 e 205 foram mantidas.
- C08: estrutura da inferência e possíveis deslocamentos territoriais. A menção à dependência espacial foi preservada; nenhum estimador de covariância ou modelo de efeitos indiretos foi fixado.

Essas decisões pertencem ao desenvolvimento da metodologia e exigem compatibilidade com os dados. O relatório da WORK-C permanece como registro das recomendações, sem declaração artificial de encerramento das pendências empíricas.

## Validação

- Compilação anterior com `latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex`: exit 0.
- Compilação posterior com `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`: exit 0; PDF mantido em 13 páginas.
- Sem citações/referências indefinidas ou caixas `Overfull`. Avisos preexistentes de depreciação de `babel`/`memoir` mantidos; ocorrências de `Underfull \\vbox` passaram de sete para seis. Nenhum novo aviso identificado.
- Inspeção visual das páginas 5, 6 e 10: trechos adicionados legíveis, sem cortes ou sobreposição; cor cinza encerrada antes da organização do artigo; redistribuição do texto sem perda de conteúdo.
- Comparação com a cópia anterior confirmou somente as linhas 195 e 205 alteradas, com todas as citações e comentários preservados.
- Hashes SHA-256 confirmaram que os demais `.tex` e `.bib` sob `2_INTI/chapters/` e o `CLAIMS_LEDGER.csv` permaneceram idênticos.
- `git diff --check` sem erros; PDF e artefatos de validação confirmados como ignorados pelo Git.

## Arquivos e estado

- Modificado: `2_INTI/chapters/chap1/0_introduction.tex`.
- Criado: `2_INTI/reports/retificacao_WORK_C_introducao_chap1.md`.
- Artefatos locais: `2_INTI/xreports/fernando_work_c_intro_20261009_155942/` — cópia anterior, hashes, logs, diff, texto extraído e imagens.
- Branch `main`; mudanças preexistentes e os cinco relatórios anteriores não rastreados preservados. Sem commit, merge ou push.
