# Continuidade — stack da tese, Etapas 7–15

Registro inicial: 5 de outubro de 2026. Atualização: 6 de outubro de 2026.

Estado final: tarefa cancelada pelo pesquisador em 6 de outubro de 2026. Ele fará a integração bibliográfica manualmente. Não retomar a Etapa 7 nem iniciar as Etapas 8–15 sem novo pedido. A revisão e incorporação dos registros corretos da Etapa 7 em `main` foram explicitamente autorizadas no pedido de encerramento.

## Estado seguro

Repositório: `C:/Users/ferna/Documents/dev/Tese USP/tese_eco_usp`.
Branch de trabalho: `work/config-stack-tese-etapas-7-15`.
Base: `d08e90f1148c90e34e042371816e9373fa070f65`, igual a `origin/main` após fetch.
Árvore inicialmente limpa. Não houve merge durante a configuração; a incorporação documental em `main` foi autorizada no encerramento, após revisão.

Zotero **9.0.6** já estava aberto no Windows. Better BibTeX **9.0.68** ativo. A API local respondeu HTTP 200 por endpoint documentado, sem proxy. Nenhuma configuração do Zotero ou do Windows foi alterada.

## Diagnóstico inicial e estado atual

Ver [relatório da Etapa 7](../reports/2026-10-05_etapa7_diagnostico_zotero_bbt.md), que contém inventário, tabela completa de correspondência, verificações locais e SHA-256 dos 20 arquivos LaTeX/BibTeX protegidos.

H1: 39 entradas e 39 chaves usadas. H2: 25 entradas e 25 chaves usadas. São 54 citekeys distintas; todas existem nos respectivos arquivos bibliográficos, sem entradas não utilizadas ou chaves repetidas no mesmo arquivo.

No diagnóstico inicial, nenhuma das 64 entradas foi localizada nos 147 registros bibliográficos ativos das bibliotecas locais consultadas, inclusive “Tese Fernando (USP)”. A Etapa 7 parou antes de importação ou auto-export, conforme as seções 5 e 17 do pedido. O pesquisador posteriormente autorizou a busca das fontes originais e sua captura pelo Zotero Connector do Edge ou do Chrome com perfil USP, exigindo correspondência LaTeX → BibTeX → registro e arquivo fonte no Zotero.

O pesquisador criou manualmente `Tese Fernando (USP)/2_INTI/chap1` e `chap2`. Chaves confirmadas na Local API: `2_INTI=THQDCPZS`, `chap1=SBUNZNZV`, `chap2=2PBN6A48`; ambas as coleções de capítulo ainda estão vazias na última consulta. A janela principal do Zotero está em `chap1`. A coleção para referências não utilizadas ainda está pendente.

A página e o PDF integral da editora de `PachecoMeyer2022` foram verificados no navegador embutido: título, autores, ano e DOI `10.1038/s41467-022-33398-3` coincidem com H1. PDF de 10 páginas em `C:/Users/ferna/Downloads/s41467-022-33398-3.pdf`; SHA-256 e procedimentos estão no relatório. Não apagar essa cópia. Ainda não há registro correspondente no Zotero pessoal ou no grupo; anexo e chave Zotero permanecem pendentes. Um PDF em Downloads não equivale a fonte salva no Zotero.

Não alterar `library.bib`, citekeys ou `citation-options.bib` para resolver o bloqueio. Manter BibTeX tradicional e `abntex2-alf`. Não interpretar `autoPinMigrated=true` como configuração atual de auto-pin.

## Pendências para a execução manual

O pesquisador assumiu a execução manual. Permanecem pendentes a captura da primeira fonte validada em `chap1`, a conferência do registro, do anexo integral e da chave `PachecoMeyer2022`, seguida da conciliação das demais referências. Preservar chaves e metadados; validar exportações separadas antes de configurar os destinos canônicos. Este registro não autoriza executar essas ações automaticamente.

Limitações observadas: as ações de teclado na caixa modal do Zotero devolviam o foco à janela principal; o pesquisador criou as coleções. Uma tentativa anterior de controlar a barra de extensões do Edge foi interrompida por Computer Use, que não conseguiu identificar a URL atual com confiança suficiente para aplicar sua política. Não contornar esse controle com scripts de entrada nativa ou APIs ocultas de extensão. Se a captura continuar inacessível, solicitar somente a ação manual necessária ao pesquisador e validar o resultado pela Local API.

Atenção às fontes compartilhadas com chaves diferentes:
- `MapBiomas2026` (H1) e `MapBiomas101` (H2);
- `IBGEPAM2026` (H1) e `IBGEPAM` (H2).

As autorizações anteriores de diagnóstico, abertura do Zotero, captura e organização bibliográfica não mantêm a tarefa ativa após o cancelamento. O Zotero já estava aberto e não foi reiniciado. Nenhuma alteração adicional na biblioteca integra o encerramento.

## Resultado parcial e etapas não executadas

| Etapa | Estado | Próximo resultado necessário |
| --- | --- | --- |
| 7 | Execução automática cancelada; diagnóstico e primeiro PDF verificados, coleções criadas pelo pesquisador | Integração manual assumida pelo pesquisador; captura e auto-export não concluídos |
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

## Verificação e entrega do encerramento

Somente o relatório de diagnóstico e este registro documental devem integrar o commit desta atualização. Os 20 SHA-256 dos arquivos protegidos foram novamente conferidos e permanecem iguais. `git fetch origin` concluiu; `main...origin/main=0 0`; branch limpa antes das alterações documentais. Conferir `git diff --check` antes do commit. Não foram executadas compilação nova ou suíte Python, pois nenhum arquivo LaTeX/BibTeX/código foi alterado; os logs existentes foram apenas inspecionados. A validação do PDF utilizou dependências já disponíveis.

Commit do diagnóstico inicial: `7827ec488906111cf3f4d6d3a8fea66cc67dfbb7`, enviado à branch remota. Os commits posteriores são identificados pelo histórico da branch e pela resposta de entrega; não incorporar o próprio hash a um arquivo do mesmo commit.

Commit da atualização da primeira fonte: `29de1e8`, enviado à branch remota. A revisão para incorporação em `main` constatou somente dois documentos novos no conjunto da branch. O encerramento corrige a indicação de escopo ativo e preserva o diagnóstico histórico. Foram conferidos os 20 hashes protegidos, as 39 chaves de H1 e 25 de H2, a correspondência com as tabelas, UTF-8 e `git diff --check`, sem divergências. O estado posterior do Zotero não foi recertificado. Não excluir a branch de trabalho.

Identificar o commit destes registros com:

```powershell
git log --oneline d08e90f1148c90e34e042371816e9373fa070f65..main
git diff --stat d08e90f1148c90e34e042371816e9373fa070f65..main
git status
```

O pesquisador receberá os hashes e a situação da incorporação em `main` na resposta de entrega. A tarefa automática está encerrada; a integração bibliográfica e a stack permanecem incompletas.
