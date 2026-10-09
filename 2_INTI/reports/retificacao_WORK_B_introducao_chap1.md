# Retificação da introdução do chap1 após WORK-B

Data: 09/10/2026.

## Escopo e autorização

Aplicação das correções da WORK-B autorizadas pelo autor, com intervenção mínima na introdução e uso exclusivo de referências já contidas em `2_INTI/chapters/chap1/library.bib`. Atendida a preferência por uma referência por trecho: todas as chamadas de citação têm uma única citekey.

Foram seguidos `AGENTS.md`, `RESEARCH_PROTOCOL.md` e `STYLE_GUIDE.md`. A auditoria `WORK_B_claim_evidencia_chap1.md` permanece como registro da versão anterior. A autorização para retificar com base na biblioteca existente permitiu reposicionar citações e utilizar `BermanEtAl2023`, já presente no arquivo, sem acrescentar entradas bibliográficas.

## Alterações aplicadas

| Achado | Localização em `0_introduction.tex` | Retificação |
|---|---|---|
| B01 — alcance de Bragança | Linhas 51, 54 e 57 | Retiradas as duas atribuições do mecanismo econômico-institucional completo a Bragança. As frases de síntese foram preservadas como elaboração do argumento apoiado pela fundamentação circundante. A referência passou ao trecho de realocação produtiva, explicitando preços relativos *crop-to-beef*, substituição de pastagens por lavouras e menor desmatamento local no Tapajós. |
| B02 — extrapolação de Viallon | Linha 57 | Retirada a atribuição de diferenças agropecuárias entre biomas ao estudo suíço. Em seu lugar, a passagem territorial trata das associações amazônicas entre condições biofísicas, acesso e uso agropecuário, fundamentadas em Chomitz e Thomas. Viallon permanece na biblioteca. |
| B03 — espaço versus resposta a preços | Linha 57 | Chomitz e Thomas ficaram restritos à heterogeneidade espacial. A resposta heterogênea do desmatamento a preços passou a ser sustentada por Berman, com o recorte dos trópicos explícito. Não foi atribuída a esse artigo a validação antecipada de H1-a. |
| B04 — lista excessiva de mecanismos | Linha 54 | Atribuição a Harding restringida à pressão dos preços agropecuários e ao condicionamento por políticas, com efeitos diferentes conforme instrumento e usos afetados. Retirados dessa frase preços fundiários, mudanças de acesso e incentivos positivos, cuja verificação individual não estava estabelecida. |
| B05 — atribuições específicas não confirmadas | Linhas 48 e 51 | Alston ficou associado à definição/proteção de direitos de propriedade e aos incentivos de uso. Assunção ficou associado ao monitoramento e à fiscalização do desmatamento na Amazônia. Foram retiradas as comparações condicionais específicas que não haviam sido verificadas. |
| B06 — alcance biofísico de VanWey | Linha 60 | Mantidos o contexto agropecuário e a presença dos três biomas; retirada a enumeração de diferenças de clima, disponibilidade hídrica e condições produtivas atribuída à mesma fonte. |

Corrigido também o erro de digitação “noo qual” na linha 48. Nenhuma outra mudança editorial foi aplicada.

O texto mantém a sequência argumentativa e os cinco parágrafos de contextualização. As alterações alcançaram somente as linhas 48, 51, 54, 57 e 60. Pergunta, objetivos, contribuição, hipóteses, equações comentadas, definições e metodologia ficaram idênticos à versão imediatamente anterior. As retificações da WORK-A foram preservadas.

## Fundamentação e limites

As correções utilizam o alcance documental registrado na WORK-B. A evidência específica de monitoramento/fiscalização foi novamente conferida no [resumo original de Assunção et al.](https://www.aeaweb.org/articles?id=10.1257/app.20200196). A heterogeneidade da resposta a preços foi conferida no [conteúdo original indexado de Berman et al.](https://www.sciencedirect.com/science/article/pii/S0095069623000372), que identifica diferenças relacionadas à inserção comercial e às condições econômicas locais. A abertura direta deste último retornou bloqueio de acesso; não se afirma nova leitura integral.

As limitações de acesso integral descritas na auditoria continuam registradas. Para Alston e Assunção, a solução foi restringir a atribuição ao conteúdo confirmado, sem presumir que as obras integrais não contenham outros argumentos. As duas frases de síntese antes acompanhadas de Bragança não são apresentadas como novos resultados empíricos.

O achado B07 diz respeito à consolidação do ledger, não a um erro de redação da introdução. O `CLAIMS_LEDGER.csv` foi preservado: continuam pendentes a organização do suporte por desdobramento de H1 e a avaliação das demais candidatas. O uso de Berman na linha 57 fica documentado neste relatório; seu registro no ledger permanece `candidate`, sem promoção automática de status. As três referências ausentes da biblioteca não foram incorporadas.

## Validação

- Compilação anterior: `latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex`, exit 0.
- Compilação posterior: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`, exit 0.
- PDF mantido em 13 páginas; sem citações/referências indefinidas e sem caixas `Overfull` no log final.
- Mantidos os avisos preexistentes de depreciação de `babel`/`memoir` e as sete ocorrências de `Underfull \\vbox`, com a mesma sequência de valores de badness. Nenhum novo aviso de compilação identificado.
- Inspeção visual das páginas 1 e 2, que contêm os trechos alterados: sem cortes ou sobreposição; citações e itálico renderizados corretamente.
- Conferência das citações ativas: 11 chamadas, 11 chaves distintas, nenhuma chamada agrupada e nenhuma chave ausente de `library.bib`. Antes havia 12 chamadas e 11 chaves distintas.
- Comparação com a cópia anterior confirmou apenas cinco linhas alteradas e preservação de todo o restante da introdução.
- Hashes SHA-256 confirmaram preservação dos demais `.tex` e `.bib` do diretório do chap1 e do ledger.
- `git diff --check` sem erros. Artefatos de validação e PDF confirmados como ignorados pelo Git.

## Arquivos e estado

- Modificado: `2_INTI/chapters/chap1/0_introduction.tex`.
- Criado: `2_INTI/reports/retificacao_WORK_B_introducao_chap1.md`.
- Artefatos locais: `2_INTI/xreports/fernando_work_b_intro_20261009_152926/` — cópia anterior, hashes, logs, diff, extração textual e imagens.
- Branch `main`; alterações preexistentes na introdução e os três relatórios anteriores não rastreados preservados. Sem commit, merge ou push.
