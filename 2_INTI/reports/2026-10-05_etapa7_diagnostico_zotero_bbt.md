# Etapa 7 — diagnóstico do Zotero e auditoria preliminar H1/H2

Data: 5 de outubro de 2026. Execução interrompida antes da integração bibliográfica.

## Resultado e decisão necessária

O Zotero está aberto no Windows, versão **9.0.6**, com Better BibTeX **9.0.68** ativo. A porta `127.0.0.1:23119` pertence ao processo principal do Zotero (PID 37968 na consulta). A leitura de `/api/users/0/collections?limit=1`, sem proxy, retornou **HTTP 200**, e `api.ready` confirmou ambas as versões.

As primeiras consultas ao endereço-base `/api/` terminaram prematuramente. O diagnóstico mudou o endpoint e desativou proxy somente no cliente de consulta; portanto, não isolou a causa dessas primeiras falhas. Nenhuma configuração do Zotero ou do Windows foi alterada, e não foi necessário iniciar ou reiniciar o aplicativo.

**Nenhuma das 64 entradas dos dois artigos foi localizada por DOI ou título normalizado nos itens ativos das bibliotecas locais acessíveis.** São **54 citekeys distintas**; dez aparecem nos dois artigos. Ausência aqui significa ausência de correspondência no inventário local consultado, não uma afirmação sobre referências eventualmente existentes fora dele.

A seção 5 do pedido exige: “Se houver incompatibilidade relevante: PARE esta subetapa, gere relatório e solicite decisão humana.” A seção 17 também impede prosseguir quando a divergência pode quebrar LaTeX. Assim, não houve importação, criação de coleções ou ativação de auto-export. As bibliografias atuais continuam intactas.

## Segurança Git

- Repositório: `C:/Users/ferna/Documents/dev/Tese USP/tese_eco_usp`.
- Remoto confirmado: `https://github.com/fernandovieira1/tese_eco_usp.git`.
- `git status` confirmou árvore limpa em `main`.
- `git fetch origin` foi executado na inspeção inicial e novamente antes da criação da branch.
- `main`, `origin/main` e HEAD inicial: `d08e90f1148c90e34e042371816e9373fa070f65`; divergência: `0 0`.
- Branch criada: `work/config-stack-tese-etapas-7-15`.
- Alterações desta execução limitadas a este relatório e ao registro de continuidade em `2_INTI/thread`.
- Nenhum merge, reset, rebase, exclusão ou modificação de dados.

## Inventário das bibliotecas

| Biblioteca | ID interno BBT | ID de grupo na API | Itens de topo | Registros bibliográficos |
| --- | --- | --- | --- | --- |
| Minha biblioteca | 1 | — | 122 | 106 |
| Artigo_ECO2_APS | 3 | 5841826 | 0 | 0 |
| Tese Fernando (USP) | 2 | 5553057 | 43 | 41 |

Foram consultados os **147 registros bibliográficos** das três bibliotecas, inclusive itens fora de coleções. Notas, anexos e anotações não foram tratados como referências. A enumeração foi paginada até `Total-Results`. Não foram consultados itens da lixeira ou conteúdo remoto ainda não sincronizado.

Na biblioteca “Tese Fernando (USP)” (grupo 5553057), já existem:

- `1_SUYANA` (`SWSRC8B5`), com estrutura histórica de capítulos e seções;
- `2_INTI` (`THQDCPZS`), sem itens diretos;
- outras coleções históricas, mantidas sem alterações.

Não foram encontradas coleções H1/H2 na estrutura local atual. A coleção pessoal `Microeconomia/Ambiental` (`GR6W6HB9`) contém sete itens diretos e também foi abrangida pela busca em toda a biblioteca pessoal.

## Citation keys, pin e auto-export

- Fórmula persistida: `auth.lower + shorttitle(3, 3) + year`.
- Campo nativo `citationKey` exposto pela API: os 147 valores coincidiram com a consulta somente de leitura `item.citationkey` do BBT.
- Nenhum conflito de citekeys foi encontrado dentro de cada biblioteca, inclusive na comparação sem distinguir maiúsculas/minúsculas.
- `fillKeyAfter=1`: preencher chaves ausentes após um segundo; isso não comprova pin de chaves legadas.
- `autoPinMigrated=true`: marcador de migração. Não equivale a auto-pin ativo.
- O pacote instalado não define preferência atual `autoPin`; a auditoria não atribuiu retrospectivamente estado “pinned” aos registros.
- `resetKeyOnChange` não aparece como sobrescrita nas preferências persistidas; o padrão do pacote instalado é `false`. O comportamento esperado é preservar chaves existentes em alterações de metadados. A consulta não acessou a tela de preferências nem sondou alterações ainda não persistidas.
- Nenhum registro `translators.better-bibtex.autoExport.<caminho>` foi encontrado em `prefs.js`. O último estado persistido de exportação contém `keepUpdated=false`.
- O modo global padrão `autoExport=immediate` não significa que haja um job registrado.
- Não foi invocada regeneração de chaves, exportação, importação, consolidação de duplicatas ou mudança de configuração.

As opções atuais de geração e preservação estão descritas nas [preferências oficiais do Better BibTeX](https://retorque.re/zotero-better-bibtex/preferences/). O mecanismo de consulta utilizado consta na [documentação JSON-RPC do BBT](https://retorque.re/zotero-better-bibtex/exporting/json-rpc/).

## Consistência LaTeX × BibTeX

| Verificação | H1 | H2 |
| --- | --- | --- |
| Entradas em `library.bib` | 39 | 25 |
| Citekeys usadas nos arquivos `.tex` | 39 | 25 |
| Chaves citadas ausentes no `.bib` | 0 | 0 |
| Chaves repetidas no mesmo `.bib` | 0 | 0 |
| Entradas do `.bib` não utilizadas | 0 | 0 |
| Correspondência bibliográfica exata no Zotero | 0 | 0 |
| Zotero identificado com chave diferente | 0 | 0 |
| Referência local não localizada no Zotero | 39 | 25 |

A extração excluiu comentários LaTeX e `\citeoption{config-citacoes-abnt}`. Os comandos científicos encontrados foram `\cite` e `\citeonline`. O projeto mantém BibTeX tradicional, `abntex2-alf` e `citation-options.bib` separado.

Os logs já existentes não mostraram citações undefined na inspeção inicial. Foram encontrados avisos de depreciação de `babel` para `brazil` e de `memoir` para `\settocpreprocessor`. Isso é uma leitura dos logs existentes, **não uma nova confirmação de compilação**.

Não houve alteração de LaTeX, BibTeX ou código Python. Não foram executados compilação nova, suíte Python ou resolução online de DOI nesta interrupção. A configuração e os testes automáticos da Etapa 10 permanecem pendentes.

## Tabela de correspondência

As chaves abaixo existem nos respectivos `library.bib` e estão usadas no LaTeX. “Não localizada” indica nenhuma correspondência por DOI, título normalizado, chave atual ou URL idêntica no inventário consultado. Não surgiram candidatos por similaridade de título com razão igual ou superior a 0,78; essa heurística não substitui identificação bibliográfica.

| Artigo | Citekey no BibTeX e LaTeX | Usada | Citekey correspondente no Zotero | Resultado |
| --- | --- | --- | --- | --- |
| H1 | `Angelsen2010` | sim | — | não localizada |
| H1 | `LubowskiEtAl2008` | sim | — | não localizada |
| H1 | `JungEtAl2022` | sim | — | não localizada |
| H1 | `ViallonEtAl2019` | sim | — | não localizada |
| H1 | `AssuncaoEtAl2023` | sim | — | não localizada |
| H1 | `Braganca2018` | sim | — | não localizada |
| H1 | `PachecoMeyer2022` | sim | — | não localizada |
| H1 | `HardingEtAl2021` | sim | — | não localizada |
| H1 | `ChomitzThomas2003` | sim | — | não localizada |
| H1 | `AnderssonEtAl2014` | sim | — | não localizada |
| H1 | `BermanEtAl2023` | sim | — | não localizada |
| H1 | `VanWeyEtAl2013` | sim | — | não localizada |
| H1 | `SimoesEtAl2020` | sim | — | não localizada |
| H1 | `Brady2015` | sim | — | não localizada |
| H1 | `Crossman2009` | sim | — | não localizada |
| H1 | `Gascoigne2011` | sim | — | não localizada |
| H1 | `Mann2012` | sim | — | não localizada |
| H1 | `Schwamback2024` | sim | — | não localizada |
| H1 | `Popin2025` | sim | — | não localizada |
| H1 | `SeidlMoraes2000` | sim | — | não localizada |
| H1 | `FairbrassEtAl2025` | sim | — | não localizada |
| H1 | `CampoliStivali2026` | sim | — | não localizada |
| H1 | `Pfaff1999` | sim | — | não localizada |
| H1 | `ProbstEtAl2020` | sim | — | não localizada |
| H1 | `Sousa2016` | sim | — | não localizada |
| H1 | `SticklerEtAl2013` | sim | — | não localizada |
| H1 | `SeidlEtAl2001` | sim | — | não localizada |
| H1 | `GoldsmithPinkhamEtAl2020` | sim | — | não localizada |
| H1 | `CallawaySantAnna2021` | sim | — | não localizada |
| H1 | `Conley1999` | sim | — | não localizada |
| H1 | `Brasil2012` | sim | — | não localizada |
| H1 | `IBGEBiomas2019` | sim | — | não localizada |
| H1 | `IBGEPAM2026` | sim | — | não localizada |
| H1 | `IBGEPPM2026` | sim | — | não localizada |
| H1 | `MapBiomas2026` | sim | — | não localizada |
| H1 | `FAOGAEZ2021` | sim | — | não localizada |
| H1 | `WorldBank2026` | sim | — | não localizada |
| H1 | `IBAMA2026` | sim | — | não localizada |
| H1 | `CONAB2026` | sim | — | não localizada |
| H2 | `Conley1999` | sim | — | não localizada |
| H2 | `IBGEPAM` | sim | — | não localizada |
| H2 | `MapBiomas101` | sim | — | não localizada |
| H2 | `CHIRPSv2` | sim | — | não localizada |
| H2 | `IBGEBiomas2019` | sim | — | não localizada |
| H2 | `SpracklenEtAl2012` | sim | — | não localizada |
| H2 | `JoshiGarkoti2023` | sim | — | não localizada |
| H2 | `RedheadEtAl2020` | sim | — | não localizada |
| H2 | `DellEtAl2014` | sim | — | não localizada |
| H2 | `XiaoEtAl2023` | sim | — | não localizada |
| H2 | `VanWeyEtAl2013` | sim | — | não localizada |
| H2 | `SimoesEtAl2020` | sim | — | não localizada |
| H2 | `Brady2015` | sim | — | não localizada |
| H2 | `Schwamback2024` | sim | — | não localizada |
| H2 | `Popin2025` | sim | — | não localizada |
| H2 | `SeidlMoraes2000` | sim | — | não localizada |
| H2 | `FairbrassEtAl2025` | sim | — | não localizada |
| H2 | `HuangEtAl2021` | sim | — | não localizada |
| H2 | `MorelEtAl2019` | sim | — | não localizada |
| H2 | `SilvaEtAl2019` | sim | — | não localizada |
| H2 | `NobregaEtAl2017` | sim | — | não localizada |
| H2 | `BaseEtAl2012` | sim | — | não localizada |
| H2 | `SchefflerEtAl2011` | sim | — | não localizada |
| H2 | `SeidlEtAl2001` | sim | — | não localizada |
| H2 | `CardosoEtAl2011` | sim | — | não localizada |

## Duplicatas e chaves compartilhadas

Não houve referência candidata duplicada para as 64 entradas auditadas. Foram identificados seis agrupamentos de DOI repetido na biblioteca pessoal, fora dessas correspondências; nenhuma referência foi mesclada ou removida.

A mesma fonte MapBiomas usa `MapBiomas2026` em H1 e `MapBiomas101` em H2, com DOI `10.58053/MapBiomas/SJZOLT`. A tabela 1612 do SIDRA é referenciada por `IBGEPAM2026` em H1 e `IBGEPAM` em H2, com a mesma URL de origem. A conciliação deve preservar as duas chaves de cada fonte e considerar os metadados próprios de cada artigo. Não se deve padronizar automaticamente essas chaves ou converter o projeto para biblatex/biber.

## Procedimento de leitura e reprodução

1. Confirmar Zotero aberto, versão e porta com `Get-Process`, `VersionInfo` do executável e `Get-NetTCPConnection -LocalPort 23119`.
2. Consultar um endpoint documentado, por exemplo:

   ```powershell
   curl.exe --noproxy localhost,127.0.0.1 --max-time 15 -H "Zotero-API-Version: 3" "http://localhost:23119/api/users/0/collections?limit=1"
   ```

3. Enumerar `/api/users/0/groups`, os `items/top` e `collections` da biblioteca pessoal e dos grupos. Paginar com `limit=100` e `start`, até `Total-Results`.
4. Consultar somente os métodos BBT `api.ready`, `user.groups` e `item.citationkey`. Os IDs internos BBT e IDs de grupo da API são distintos; usar o ID interno no prefixo `[libraryID]:[itemKey]`.
5. Extrair chaves de todos os oito `.tex` de cada artigo; ignorar comentários e opções ABNT. Ler as entradas BibTeX com campos entre chaves e balanceamento de delimitadores, conforme os arquivos atuais.
6. Comparar DOI sem prefixos `doi:`/`https://doi.org/` e sem distinção de caixa; alternativamente, normalizar título para caracteres alfanuméricos sem diacríticos e comandos TeX. Usar a chave ou URL como candidato adicional sujeito a validação.
7. Comparar os valores de `citationKey` da API com `item.citationkey`; contar conflitos por biblioteca.
8. Conferir a tabela acima e os SHA-256 abaixo. O inventário e a comparação foram executados em memória com Python 3.12.10 de `2_INTI/code/.venv`, usando apenas a biblioteca padrão e `ProxyHandler({})`, sem arquivos intermediários.

Uma tentativa de leitura SQLite com `mode=ro` retornou “database is locked”. Nenhum bloqueio foi contornado, nenhuma cópia de banco foi usada como estado atual e o Zotero permaneceu aberto. A auditoria bibliográfica utilizou a API.

A [documentação oficial da Local API](https://www.zotero.org/support/dev/web_api/v3/local_api) fundamenta os endpoints locais utilizados. **MCP não necessário neste momento:** API local, JSON-RPC do BBT e Python permitiram obter o inventário e fazer a comparação, sem novo serviço.

## Arquivos protegidos: SHA-256 anterior às alterações documentais

| Arquivo | SHA-256 |
| --- | --- |
| `2_INTI/chapters/chap1/0_introduction.tex` | `4ed6d36ce20882ba284d285307aecda8c73c2204b0c20e632e743de931e61f57` |
| `2_INTI/chapters/chap1/1_literature_review.tex` | `63f7bbadcc12b89b6ccf223ee5d48f82e6e5fc6e6a735d065ac492a0630814ba` |
| `2_INTI/chapters/chap1/2_mt_descriptive.tex` | `0905fb93540441077e630001513ed25215821b6890110ff9a2f6d0cfa6506cd2` |
| `2_INTI/chapters/chap1/3_econometrics_strategy.tex` | `6c0aa2f0af1165907ff9322c6e846070f78db1bb9fd5b8c1ea84bd002acc7fd1` |
| `2_INTI/chapters/chap1/4_discussion.tex` | `a32e296d32e3034e59f5c0775450b7e5cd676d25146675da676d2b19ff6b9d07` |
| `2_INTI/chapters/chap1/5_Final_Remarks.tex` | `c5c61a1bb5c2b1f9a69a104f3d6bde8823087b7821276440d2a8686da90cdfb9` |
| `2_INTI/chapters/chap1/_abstract.tex` | `727ed7428c6b17eeb174557bdbd8fe25d6371c180367cb949efdc3d19bb1bf45` |
| `2_INTI/chapters/chap1/citation-options.bib` | `2089c4e07592d77f7f7b2a356ed45f579d4eedc041a83ecfbb50caf3626f6275` |
| `2_INTI/chapters/chap1/library.bib` | `222ed882091ab9ea1514da6c025ba1ac3ab8b4ad07dce032cd97928395dd0797` |
| `2_INTI/chapters/chap1/main.tex` | `dd774ae2fe0a302522df346d0365f2c960424d648975e888d6a15266d586711c` |
| `2_INTI/chapters/chap2/0_introduction.tex` | `bff6473dd719a0e274771c8a84b842cb8b580150ec8eae4b374588fd61b839eb` |
| `2_INTI/chapters/chap2/1_literature_review.tex` | `83ab779d58cefc9e9410f39744ac7a978848636596dcb5121acc6a171bb7068e` |
| `2_INTI/chapters/chap2/2_mt_descriptive.tex` | `e18b05eac3f6d8d3f4613d15546ef2912d65c4ba129fa86d302b61475b042f83` |
| `2_INTI/chapters/chap2/3_econometrics_strategy.tex` | `6f48d37fe15f8f97385888dee1c1553bf83e22a7911392dff527ec38b27a4419` |
| `2_INTI/chapters/chap2/4_discussion.tex` | `f3a282023e957c29795a11db2e0c41d1aca5669c50b29331284927d9dd42018d` |
| `2_INTI/chapters/chap2/5_Final_Remarks.tex` | `3abb6ffbb93274add3eaf8de267d14475cf0a74521048e6d2f076a8168db8b5b` |
| `2_INTI/chapters/chap2/_abstract.tex` | `591de7bbbfc14fec255780db0004cc97271d01b638cd187dc26253e12413a90f` |
| `2_INTI/chapters/chap2/citation-options.bib` | `6371e0c60f748b349ce2b3249c11c5f2649a2dd07e2ba4760b52cc031534060f` |
| `2_INTI/chapters/chap2/library.bib` | `1f49fc8260f5d22bc291267b767a5507e51bc68c0853832cbc7e412effef67eb` |
| `2_INTI/chapters/chap2/main.tex` | `54eeffcb692c67315a3f7e20fbd3249c1f4d45b9b2018921bef0f91121ec456f` |

## Continuidade e decisões humanas

A integração da Etapa 7 está suspensa. As Etapas 8–15 não foram executadas nesta interrupção.

Decisão solicitada: autorizar a importação controlada das bibliografias atuais em coleções H1/H2, preferencialmente sob `2_INTI` da biblioteca de grupo já existente, preservando todas as chaves usadas. Antes de qualquer auto-export sobre os destinos canônicos, validar correspondência completa, diferenças de metadados, as chaves alternativas de fontes compartilhadas e uma exportação em arquivo separado.

Plano posterior: concluir Etapa 7 com revisão das correspondências; consolidar os artefatos mínimos e auditorias das Etapas 8–13 usando o catálogo existente; executar o piloto sem substituir texto científico na Etapa 14; produzir o fluxo operacional e a revisão de commits na Etapa 15.

Este relatório não certifica a stack como concluída. O commit e eventual backup remoto deste registro serão apresentados ao pesquisador após a verificação Git.

## Atualização de 6 de outubro de 2026 — coleções e primeira fonte integral

O pesquisador restringiu o trabalho à Etapa 7 e autorizou a organização das referências citadas em `Tese Fernando (USP)`, com coleções `chap1` e `chap2`, preservação das citekeys e captura das fontes originais pelo Zotero Connector do Edge ou do Chrome com perfil USP. Referências ainda não utilizadas terão coleção separada; nenhuma coleção histórica deve ser reorganizada automaticamente.

As coleções foram criadas manualmente pelo pesquisador e confirmadas na API local:

| Coleção | Chave Zotero | Coleção superior | Itens nesta consulta |
| --- | --- | --- | --- |
| `2_INTI` | `THQDCPZS` | raiz do grupo `5553057` | 0 |
| `chap1` | `SBUNZNZV` | `THQDCPZS` | 0 |
| `chap2` | `2PBN6A48` | `THQDCPZS` | 0 |

Não foram criadas coleções redundantes nem movidos itens existentes. A coleção de referências não utilizadas ainda está pendente. A ordem alfabética deverá ser configurada na visualização dos itens e comparada com a bibliografia compilada, sem alterar títulos ou citekeys para forçar ordenação.

### Fonte verificada: `PachecoMeyer2022` — H1

- Origem: [página da editora](https://www.nature.com/articles/s41467-022-33398-3), aberta pelo pesquisador no navegador embutido.
- Arquivo: [PDF da editora](https://www.nature.com/articles/s41467-022-33398-3.pdf), baixado pelo link `Download PDF` com o controle documentado do navegador.
- Autores: Andrea Pacheco e Carsten Meyer; publicação em 1 de outubro de 2022; Nature Communications, volume 13, artigo 5759.
- DOI: `10.1038/s41467-022-33398-3`, correspondente ao BibTeX de H1.
- Cópia local: `C:/Users/ferna/Downloads/s41467-022-33398-3.pdf`; 1.415.819 bytes, 10 páginas.
- SHA-256: `a63159e4096d2d7186ec109c135dea2cc99a71f964d594b777ebe4f1005b6439`.
- Validação: título, ambos os autores e DOI no conteúdo da primeira página conferidos com Python 3.12.10 da `.venv` canônica e `pypdf`; primeira página renderizada com o Poppler já disponível e inspecionada visualmente. O título nos metadados internos do PDF tem um apóstrofo com codificação defeituosa; o título impresso está correto. O arquivo não foi modificado.
- O leitor `pypdf` emitiu avisos sobre `fontTools` ausente durante a extração; não foi instalada dependência adicional. A renderização da página ocorreu normalmente.

| Citekey LaTeX/BibTeX | Fonte integral validada | Registro no Zotero | PDF anexado ao registro | Chave Zotero validada |
| --- | --- | --- | --- | --- |
| `PachecoMeyer2022` | sim, PDF da editora | pendente | pendente | pendente |

A nova consulta paginada encontrou 43 itens de nível superior no grupo da tese e 122 na biblioteca pessoal, sem correspondência por DOI ou título para este artigo. Esses totais incluem itens que não são referências bibliográficas e não substituem a contagem de 147 referências do diagnóstico inicial.

O download em `Downloads` não cumpre, sozinho, a exigência de fonte no Zotero. A captura só poderá ser considerada concluída depois da confirmação do registro na coleção `chap1`, do anexo integral legível e da chave `PachecoMeyer2022`. O navegador embutido permitiu consultar e baixar a fonte; a captura solicitada pelo Connector permanece destinada ao Edge ou ao Chrome autorizado.

### Limitações de controle observadas

O Zotero está aberto, com a janela principal intitulada `chap1 - Zotero`. O controle nativo falhou ao editar a caixa modal de criação de coleção: as ações de teclado retornavam o foco à janela principal. Por isso, o pesquisador criou as duas coleções. Em uma tentativa anterior de controlar a barra de extensões do Edge, o mecanismo de Computer Use interrompeu o controle por não conseguir identificar a URL atual com confiança suficiente para aplicar sua política. A interrupção foi respeitada; nenhuma captura foi declarada concluída ou substituída por um mecanismo oculto.

### Preservação e verificações desta atualização

`git status` confirmou a branch de trabalho limpa antes das alterações documentais; `git fetch origin` concluiu sem erro; `main...origin/main` retornou `0 0`. Os 20 SHA-256 LaTeX/BibTeX acima continuam iguais. Nenhum `.tex`, `.bib`, dado de pesquisa ou configuração de exportação foi alterado. Não houve compilação nova nem execução da suíte econométrica nesta atualização, pois somente a documentação foi alterada. A conferência de diferenças e `git diff --check` deve anteceder o commit.

Próximo passo: concluir a captura desta primeira fonte com o Connector e validar seu anexo e sua citekey pela API. Em seguida, repetir a conferência para as demais referências, resolver os dois pares de aliases sem mudar o LaTeX e validar exportações separadas antes de habilitar qualquer destino canônico. As Etapas 8–15 permanecem fora do escopo ativo.
