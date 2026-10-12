# AGENTS.md — Tese

Este repositório contém a tese de doutorado de Fernando Souza de Vieira.

## Escopo ativo

- A fase ativa do projeto é `2_INTI/`.
- `1_SUYANA/` é material histórico/legado e não deve ser alterado salvo instrução explícita.
- Antes de executar tarefas no projeto, leia e cumpra `2_INTI/RESEARCH_PROTOCOL.md`.

## Regras gerais

- Inspecione o estado atual antes de modificar arquivos.
- Reutilize a estrutura existente e faça somente alterações necessárias.
- Preserve dados brutos, metodologia, fórmulas, citekeys e decisões científicas salvo autorização explícita.
- Não faça commit, merge ou push sem autorização explícita.
- Para tarefas técnicas, execute os testes adequados e informe regressões separadamente de falhas preexistentes.
- Grave relatórios técnicos, logs, diffs e saídas de testes em `2_INTI/audit/`.
- Use `2_INTI/audit/works/[artigo]/` para relatórios WORK-A, WORK-B, WORK-C e WORK-D e `2_INTI/audit/zotero/` para conferências bibliográficas.
- Registre decisões e contexto de continuidade no relatório pertinente, conforme `2_INTI/RESEARCH_PROTOCOL.md`.
- Esses relatórios são locais, ignorados pelo Git e protegidos pelo backup Restic. Não recrie os diretórios antigos preservados em `2_INTI/xlegado/` como estruturas ativas por padrão.
