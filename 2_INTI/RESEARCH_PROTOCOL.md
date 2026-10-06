# Research Protocol — Tese

Este documento contém os protocolos operacionais do projeto de tese.
As regras aqui registradas devem ser tratadas como fonte de referência para execução de tarefas por agentes de IA.

---

## Protocolo padrão para tarefas no Codex

Use este protocolo como base para tarefas executadas pelo Codex no repositório da tese.

### Prompt-base

Execute esta tarefa no repositório da tese.

OBJETIVO
[descrever a tarefa]

REGRAS DE SEGURANÇA
1. Inspecione primeiro o estado atual e reutilize a estrutura existente.
2. Faça somente as alterações necessárias para cumprir o objetivo.
3. Não altere metodologia, fórmulas, dados originais, citekeys, estrutura científica ou arquivos fora do escopo sem necessidade demonstrável.
4. Não sobrescreva arquivos de dados brutos.
5. Preserve compatibilidade com o ambiente documentado do projeto.
6. Antes de alterar código existente, identifique testes e dependências relevantes.
7. Execute testes adequados após as alterações.
8. Compile LaTeX quando a tarefa afetar arquivos .tex ou .bib.
9. Mostre claramente qualquer teste que falhe e diferencie falha preexistente de regressão introduzida.
10. Não faça commit, merge ou push sem autorização explícita.

ENTREGA
- resumo do que foi alterado;
- arquivos modificados/criados;
- testes executados e resultados;
- limitações ou pendências;
- git diff/status final;
- relatório de execução em 2_INTI/reports;
- quando a tarefa exigir continuidade, registro correspondente em 2_INTI/thread.

### Regra adicional

O Codex pode identificar e sugerir problemas científicos, econométricos ou metodológicos, mas não deve alterar silenciosamente hipóteses, especificações, equações, estratégia empírica, interpretação científica ou estrutura argumentativa. Essas alterações exigem decisão explícita do autor.
