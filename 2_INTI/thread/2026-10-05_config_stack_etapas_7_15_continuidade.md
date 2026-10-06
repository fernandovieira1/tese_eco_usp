# Continuidade — stack da tese, Etapas 7–15

Data: 5 de outubro de 2026.

## Estado seguro

Repositório: `C:/Users/ferna/Documents/dev/Tese USP/tese_eco_usp`.
Branch de trabalho: `work/config-stack-tese-etapas-7-15`.
Base: `d08e90f1148c90e34e042371816e9373fa070f65`, igual a `origin/main` após fetch.
Árvore inicialmente limpa. Nenhum merge em main.

Zotero **9.0.6** já estava aberto no Windows. Better BibTeX **9.0.68** ativo. A API local respondeu HTTP 200 por endpoint documentado, sem proxy. Nenhuma configuração do Zotero ou do Windows foi alterada.

## Evidência e bloqueio atual

Ver [relatório da Etapa 7](../reports/2026-10-05_etapa7_diagnostico_zotero_bbt.md), que contém inventário, tabela completa de correspondência, verificações locais e SHA-256 dos 20 arquivos LaTeX/BibTeX protegidos.

H1: 39 entradas e 39 chaves usadas. H2: 25 entradas e 25 chaves usadas. São 54 citekeys distintas; todas existem nos respectivos arquivos bibliográficos, sem entradas não utilizadas ou chaves repetidas no mesmo arquivo.

Nenhuma das 64 entradas foi localizada nos 147 registros bibliográficos ativos das bibliotecas locais consultadas, inclusive “Tese Fernando (USP)”. A Etapa 7 parou antes de importação ou auto-export, conforme as seções 5 e 17 do pedido.

Não alterar `library.bib`, citekeys ou `citation-options.bib` para resolver o bloqueio. Manter BibTeX tradicional e `abntex2-alf`. Não interpretar `autoPinMigrated=true` como configuração atual de auto-pin.

## Próxima intervenção

Solicitar decisão humana sobre a importação controlada dos arquivos atuais para coleções H1/H2 sob a biblioteca de tese existente. Preservar chaves e metadados; validar uma exportação separada antes de configurar os destinos canônicos.

Atenção às fontes compartilhadas com chaves diferentes:
- `MapBiomas2026` (H1) e `MapBiomas101` (H2);
- `IBGEPAM2026` (H1) e `IBGEPAM` (H2).

A autorização para diagnosticar e abrir Zotero se fechado já foi concedida. Ele estava aberto; não foi reiniciado. Essa autorização não elimina a necessidade de decisão sobre a incompatibilidade bibliográfica.

## Trabalho restante

| Etapa | Estado | Próximo resultado necessário |
| --- | --- | --- |
| 7 | Inventário feito; integração suspensa | Correspondências aprovadas, coleções e exportação validadas |
| 8 | Pendente | Fluxo adversarial e ledger com sete colunas |
| 9 | Pendente | Modos Crítica e Aperfeiçoamento separados |
| 10 | Pendente | AGENTS.md e auditorias, aproveitando os testes existentes |
| 11 | Pendente | Quatro protocolos de auditoria Work |
| 12 | Pendente | Inventário de armazenamento e política canônica |
| 13 | Pendente | RESEARCH_PROTOCOL.md e STYLE_GUIDE.md mínimos |
| 14 | Pendente | Piloto em proposta separada, sem troca do texto canônico |
| 15 | Pendente | FLUXO_OPERACIONAL_TESE.md e revisão final dos commits |

Já existem `2_INTI/data/catalog`, `2_INTI/reports`, `2_INTI/thread`, scripts de dados e `2_INTI/code/test_h1_h2.py`. Não criar DATA_CATALOG.csv ou reexecutar geradores históricos para sobrescrever o baseline. O README da auditoria contém instruções históricas de trabalhar em main, superadas pelo pedido atual.

MCP não necessário neste momento: as consultas existentes foram realizadas com Local API, JSON-RPC BBT e Python. Não instalar serviços ou software para reproduzir este diagnóstico.

## Verificação e entrega desta interrupção

Somente o relatório de diagnóstico e este registro documental devem integrar o commit desta interrupção. Conferir SHA-256 dos arquivos protegidos e `git diff --check` antes do commit. Não foram executadas compilação nova ou suíte Python, pois a integração parou e nenhum arquivo LaTeX/BibTeX/código foi alterado; os logs existentes foram apenas inspecionados.

Identificar o commit destes registros com:

```powershell
git log --oneline main..work/config-stack-tese-etapas-7-15
git diff --stat main...work/config-stack-tese-etapas-7-15
git status
```

O pesquisador receberá o hash do commit e a situação do backup remoto na resposta de entrega. Não confundir o registro desta pausa com a conclusão da stack.
