# Research Protocol — Tese

Este documento contém os protocolos operacionais do projeto de tese.
As regras aqui registradas devem ser tratadas como fonte de referência para execução de tarefas por agentes de IA.

## Convenção de relatórios e continuidade

- `2_INTI/reports/`: somente relatórios consolidados, decisões, validações e marcos relevantes. É versionado pelo Git.
- `2_INTI/xreports/`: logs, diffs, relatórios timestampados, saídas de testes e outros artefatos automáticos ou reproduzíveis. É local e ignorado pelo Git.
- `2_INTI/thread/`: registros relevantes para continuidade entre tarefas/agentes. É versionado pelo Git.

---

## Protocolo padrão para tarefas no Codex

Use este protocolo como base para tarefas executadas pelo Codex no repositório da tese.

### *Prompt-base*

*Execute esta tarefa no repositório da tese.*

*OBJETIVO
[descrever a tarefa]*

*REGRAS DE SEGURANÇA*

1. *Inspecione primeiro o estado atual e reutilize a estrutura existente.*
2. *Faça somente as alterações necessárias para cumprir o objetivo.*
3. *Não altere metodologia, fórmulas, dados originais, citekeys, estrutura científica ou arquivos fora do escopo sem necessidade demonstrável.*
4. *Não sobrescreva arquivos de dados brutos.*
5. *Preserve compatibilidade com o ambiente documentado do projeto.*
6. *Antes de alterar código existente, identifique testes e dependências relevantes.*
7. *Execute testes adequados após as alterações.*
8. *Compile LaTeX quando a tarefa afetar arquivos .tex ou .bib.*
9. *Mostre claramente qualquer teste que falhe e diferencie falha preexistente de regressão introduzida.*
10. *Não faça commit, merge ou push sem autorização explícita.*

*ENTREGA*

- *resumo do que foi alterado;*
- *arquivos modificados/criados;*
- *testes executados e resultados;*
- *limitações ou pendências;*
- *git diff/status final;*
- *relatório consolidado de execução em 2_INTI/reports e artefatos automáticos ou reproduzíveis em 2_INTI/xreports;*
- *quando a tarefa exigir continuidade, registro correspondente em 2_INTI/thread.*

### *Regra adicional*

*O Codex pode identificar e sugerir problemas científicos, econométricos ou metodológicos, mas não deve alterar silenciosamente hipóteses, especificações, equações, estratégia empírica, interpretação científica ou estrutura argumentativa. Essas alterações exigem decisão explícita do autor.*

---

## Protocolo padrão para auditorias no Work

O Work deve ser usado principalmente para auditorias científicas e estruturais que exijam leitura integrada de vários arquivos do projeto.

Por padrão, opere em MODO SOMENTE LEITURA.

Não altere arquivos `.tex`, `.bib`, dados, código, metodologia, hipóteses, equações ou estrutura científica sem autorização explícita do autor.

### Modos de auditoria

#### 1. ARQUITETURA

Avalie a coerência entre:

- problema de pesquisa;
- hipóteses;
- objetivos;
- dados;
- variáveis;
- estratégia empírica;
- resultados ou resultados esperados;
- discussão;
- conclusão.

Procure especialmente contradições, lacunas e mudanças silenciosas de escopo entre seções.

#### 2. CLAIM × EVIDÊNCIA

Avalie se as afirmações científicas estão adequadamente sustentadas pelas fontes utilizadas.

Considere, quando disponíveis:

- texto LaTeX;
- `CLAIMS_LEDGER.csv`;
- bibliografia;
- PDFs ou fontes vinculadas.

Para cada problema relevante, examine:

- consenso;
- divergência;
- limitação metodológica;
- ausência ou fragilidade de evidência;
- implicação para o argumento.

Não invente evidência e não substitua silenciosamente as fontes utilizadas pelo autor.

#### 3. MÉTODO × INFERÊNCIA

Avalie se o desenho empírico permite sustentar as inferências pretendidas.

Verifique, conforme aplicável:

- endogeneidade;
- simultaneidade;
- timing;
- identificação;
- efeitos fixos;
- clustering;
- seleção;
- spillovers;
- mensuração;
- contrafactual;
- robustez;
- validade externa.

Diferencie associação, interpretação causal e evidência descritiva.

#### 4. COESÃO

Avalie se conceitos, definições, hipóteses, mecanismos e interpretações permanecem consistentes ao longo do artigo.

Identifique:

- mudanças silenciosas de definição;
- contradições entre seções;
- redundâncias relevantes;
- conclusões que excedam o que foi estabelecido anteriormente.

### Formato padrão de entrega

Apresente:

1. achado;
2. evidência ou localização no projeto;
3. gravidade: CRÍTICA / RELEVANTE / MENOR;
4. recomendação;
5. pontos que exigem decisão do autor.

Não reescreva os arquivos da tese durante a auditoria.

Quando solicitado, gere relatório consolidado em `2_INTI/reports/`; grave outputs automáticos ou reproduzíveis em `2_INTI/xreports/`.

Use `2_INTI/thread/` apenas quando for necessário preservar contexto para continuidade entre tarefas.

---

## Protocolo de aperfeiçoamento textual — /fernando

Este protocolo corresponde à etapa de aperfeiçoamento textual posterior à crítica científica.

Ele não deve ser usado para decidir se uma afirmação é cientificamente correta, se uma fonte sustenta uma claim ou se uma inferência causal é válida. Essas questões devem estar resolvidas previamente no modo crítico.

### Ordem obrigatória

1. texto original;
2. crítica científica;
3. decisão explícita do autor sobre quais alterações aceitar;
4. aperfeiçoamento textual;
5. revisão final pelo autor.

Fluxo:

TEXTO ORIGINAL
→ /critica
→ DECISÃO DE FERNANDO
→ /fernando
→ REVISÃO FINAL DE FERNANDO

### Entrada esperada

O aperfeiçoamento deve receber, conforme aplicável:

- parágrafo ou trecho original;
- crítica previamente aprovada;
- alterações autorizadas pelo autor;
- evidências já autorizadas;
- `2_INTI/STYLE_GUIDE.md`.

### Instrução-base

/fernando

Revise o trecho abaixo aplicando somente as alterações aprovadas.

Preserve:

- meu argumento;
- minha voz;
- o máximo possível da estrutura original;
- o LaTeX;
- as citekeys;
- o significado científico;
- o grau de certeza das afirmações.

Não:

- acrescente evidências novas;
- crie ou substitua referências;
- introduza argumentos não aprovados;
- fortaleça silenciosamente causalidade;
- amplie silenciosamente a validade externa;
- aumente a força das conclusões;
- altere metodologia ou interpretação substantiva.

Se uma melhoria textual exigir mudança substantiva do argumento, indique-a separadamente em vez de implementá-la.

Consulte e siga `2_INTI/STYLE_GUIDE.md`.

### Princípio de intervenção mínima

Entre duas versões igualmente adequadas, prefira aquela que preserve mais do texto original.

O objetivo é aperfeiçoar a expressão de uma decisão intelectual já tomada pelo autor, e não produzir um novo argumento em seu lugar.

### Relação com /critica

`/critica`:

- avalia cientificamente;
- identifica problemas;
- não reescreve.

`/fernando`:

- trabalha somente depois da decisão do autor;
- aplica alterações aprovadas;
- aperfeiçoa redação e estilo;
- não introduz conteúdo científico novo.

### Fontes de estilo

A principal referência operacional é `2_INTI/STYLE_GUIDE.md`.

Exemplos reais da escrita do autor podem complementar o guia quando disponíveis por meio das fontes de estilo conectadas ao ChatGPT, mas devem ser tratados somente como evidência de estilo, nunca como fonte factual ou científica.

---

## Prompts operacionais — Work

As auditorias abaixo devem ser executadas separadamente. Não substituir as quatro auditorias por uma única revisão genérica.

Por padrão, todas operam em MODO SOMENTE LEITURA.

O Work pode ler os arquivos necessários do projeto, mas não deve modificar `.tex`, `.bib`, dados, código, hipóteses, metodologia ou interpretação científica sem autorização explícita do autor.

Os relatórios científicos consolidados desta etapa devem ser gravados em `2_INTI/reports/`.
Logs ou artefatos automáticos intermediários, se existirem, devem ficar em `2_INTI/xreports/`.

---

### WORK-A — Arquitetura argumentativa

Atue como revisor científico independente em MODO SOMENTE LEITURA.

ESCOPO
[chap1 / chap2 / artigo específico]

Leia de forma integrada os arquivos científicos relevantes do artigo.

OBJETIVO

Audite a arquitetura argumentativa do trabalho.

Verifique especialmente:

- progressão entre problema, pergunta, hipóteses e objetivos;
- coerência entre revisão de literatura, dados e estratégia empírica;
- correspondência entre hipóteses e variáveis;
- coerência entre método e contribuição pretendida;
- redundâncias;
- lacunas argumentativas;
- mudanças silenciosas de escopo;
- elementos introduzidos e depois abandonados;
- conclusões que não decorrem da estrutura anterior.

NÃO FAÇA

- não reescreva o artigo;
- não altere arquivos;
- não proponha novas hipóteses como se fossem decisões do autor;
- não substitua o desenho científico existente.

ENTREGA

Para cada achado relevante, informe:

1. localização;
2. problema;
3. gravidade: CRÍTICA / RELEVANTE / MENOR;
4. razão;
5. recomendação;
6. decisão que depende do autor.

Ao final, produza uma síntese:

- arquitetura consistente;
- pontos que exigem correção;
- pontos que apenas merecem atenção.

Salve o relatório consolidado em:

2_INTI/reports/WORK_A_arquitetura_[artigo].md

---

### WORK-B — Claim × evidência

Atue como revisor científico independente em MODO SOMENTE LEITURA.

ESCOPO
[chap1 / chap2 / artigo específico]

Considere, quando disponíveis:

- arquivos `.tex`;
- `2_INTI/CLAIMS_LEDGER.csv`;
- bibliografias;
- artigos/PDFs associados às referências.

OBJETIVO

Audite a correspondência entre afirmações científicas e evidências utilizadas.

Para cada claim ou afirmação relevante, examine:

1. CONSENSO
   O que a literatura utilizada sustenta com razoável robustez?
2. DIVERGÊNCIA
   Existem resultados diferentes ou contraditórios?
   A divergência pode decorrer de dados, escala, método, período ou contexto?
3. LIMITAÇÃO METODOLÓGICA
   Identificação causal, amostra, mensuração, contrafactual, validade externa, métricas ou outras limitações relevantes.
4. AUSÊNCIA OU FRAGILIDADE DE EVIDÊNCIA
   A afirmação excede o que as fontes realmente permitem concluir?
5. IMPLICAÇÃO
   O que isso significa para a redação, interpretação ou força da claim?

Verifique também:

- se a citação realmente sustenta a frase;
- se associação está sendo tratada como causalidade;
- se a linguagem está mais forte que a evidência;
- se há generalização geográfica ou temporal indevida;
- se diferentes fontes estão sendo tratadas como se mostrassem a mesma coisa.

NÃO FAÇA

- não invente evidência;
- não substitua silenciosamente referências;
- não acrescente literatura sem identificar claramente que é uma sugestão externa;
- não reescreva o texto.

ENTREGA

Para cada problema:

1. claim/trecho;
2. citekey(s);
3. avaliação;
4. gravidade: CRÍTICA / RELEVANTE / MENOR;
5. recomendação;
6. decisão que depende do autor.

Salve o relatório consolidado em:

2_INTI/reports/WORK_B_claim_evidencia_[artigo].md

---

### WORK-C — Método × inferência

Atue como revisor metodológico independente em MODO SOMENTE LEITURA.

ESCOPO
[chap1 / chap2 / artigo específico]

Leia conjuntamente hipóteses, descrição dos dados, construção das variáveis e estratégia econométrica.

OBJETIVO

Avalie se o desenho empírico permite sustentar as inferências pretendidas.

Examine, conforme aplicável:

- unidade de análise;
- período;
- timing das variáveis;
- precedência temporal;
- endogeneidade;
- simultaneidade;
- variável omitida;
- seleção;
- mensuração;
- efeitos fixos;
- clustering;
- tendências;
- choques comuns;
- spillovers;
- equilíbrio geral;
- contrafactual;
- identificação;
- heterogeneidade;
- robustez;
- validade externa.

Diferencie explicitamente:

DESCRITIVO
ASSOCIATIVO
CAUSAL

Verifique se a linguagem do artigo respeita essa distinção.

NÃO FAÇA

- não altere equações;
- não implemente nova especificação;
- não modifique código ou dados;
- não transforme recomendação metodológica em decisão já tomada.

ENTREGA

Para cada questão:

1. localização;
2. inferência pretendida;
3. problema metodológico;
4. consequência para interpretação;
5. gravidade: CRÍTICA / RELEVANTE / MENOR;
6. alternativa ou teste recomendado;
7. decisão que depende do autor.

Salve o relatório consolidado em:

2_INTI/reports/WORK_C_metodo_inferencia_[artigo].md

---

### WORK-D — Coesão e redação científica

Atue como revisor científico-editorial independente em MODO SOMENTE LEITURA.

ESCOPO
[chap1 / chap2 / artigo específico]

OBJETIVO

Audite a coesão global do artigo sem reescrevê-lo.

Verifique:

- consistência terminológica;
- definições que mudam ao longo do texto;
- hipótese formulada de maneiras incompatíveis;
- repetição desnecessária;
- transições frágeis;
- parágrafos deslocados;
- mudanças silenciosas de mecanismo;
- conceitos introduzidos sem definição;
- conclusões que usam linguagem diferente ou mais forte que o restante do artigo;
- inconsistências entre resumo, introdução, método, discussão e conclusão.

Preserve como referência estilística:

2_INTI/STYLE_GUIDE.md

NÃO FAÇA

- não reescreva os arquivos;
- não homogeneíze a voz autoral;
- não simplifique terminologia tecnicamente necessária;
- não faça mudanças científicas sob justificativa estilística.

ENTREGA

Para cada questão:

1. localização;
2. problema;
3. efeito sobre leitura/interpretação;
4. gravidade: CRÍTICA / RELEVANTE / MENOR;
5. recomendação.

Salve o relatório consolidado em:

2_INTI/reports/WORK_D_coesao_[artigo].md

---

## Ordem recomendada das auditorias Work

Executar, preferencialmente:

WORK-A — Arquitetura
→
WORK-B — Claim × evidência
→
WORK-C — Método × inferência
→
WORK-D — Coesão e redação

Não executar WORK-D antes de resolver problemas substantivos identificados em A, B e C.

A revisão final e qualquer alteração no texto permanecem sob decisão do autor.

---

## Política de armazenamento e fontes canônicas

O projeto deve evitar versões concorrentes do mesmo artefato.

### Princípio

Para cada tipo de informação existe uma única fonte canônica.
Google Drive, OneDrive, GitHub, Zotero e arquivos locais não devem manter versões ativas concorrentes do mesmo documento.

### Repositório local + Git/GitHub

Fonte canônica para:

- arquivos `.tex`;
- código;
- `CLAIMS_LEDGER.csv`;
- `RESEARCH_PROTOCOL.md`;
- `STYLE_GUIDE.md`;
- bibliografias `.bib` aprovadas;
- relatórios consolidados em `2_INTI/reports/`;
- continuidade em `2_INTI/thread/`;
- catálogo e metadados versionáveis.

Nunca editar uma cópia desses arquivos no Google Drive ou OneDrive como se fosse uma versão paralela.

### Zotero

Fonte canônica de gestão para:

- metadados bibliográficos;
- artigos;
- PDFs científicos;
- citation keys.

Os `library.bib` dos artigos permanecem artefatos científicos versionados no Git e só devem ser substituídos após validação.

### Dados

Os dados ativos permanecem exclusivamente em `2_INTI/xdata/`, que constitui a fonte canônica local dos dados da tese.

Arquivos grandes ou não versionáveis permanecem locais e são protegidos pelo sistema de backup.
Metadados, catálogo, proveniência e scripts necessários à reconstrução devem permanecer versionados quando apropriado.

### Google Drive

Usar principalmente para:

- documentos externos;
- arquivos recebidos;
- material colaborativo;
- corpus de exemplos reais de escrita;
- documentos que precisem ser acessados por ferramentas conectadas.

O corpus de estilo pode permanecer no Google Drive, enquanto `2_INTI/STYLE_GUIDE.md` é a referência operacional versionada.

Não manter no Google Drive uma segunda versão ativa dos arquivos científicos do repositório.

### OneDrive

Não usar como workspace ativo da tese.

Pode armazenar:

- documentos administrativos;
- arquivos pessoais;
- cópias de intercâmbio;
- materiais não pertencentes ao fluxo científico ativo.

Não usar OneDrive como mecanismo concorrente de versionamento ou backup do repositório.

### Backup

O mecanismo de backup do projeto é o Restic.

GitHub fornece versionamento e recuperação do conteúdo versionado, mas não substitui o backup integral.

Google Drive e OneDrive não são considerados backups canônicos do repositório.

### Diretórios locais iniciados por x

Diretórios sob `2_INTI/` cujo nome começa com `x` são locais e não canônicos.

Exemplos:

- `xreports/`;
- `xdiversos/`;
- outros `x*` que venham a ser criados.

Devem permanecer ignorados pelo Git e conter somente material temporário, reproduzível ou auxiliar.

### Escopo padrão do Work

Em auditorias científicas, o Work pode ler, por padrão:

- `2_INTI/chapters/`;
- `2_INTI/CLAIMS_LEDGER.csv`;
- `2_INTI/RESEARCH_PROTOCOL.md`;
- `2_INTI/STYLE_GUIDE.md`;
- `2_INTI/xdata/catalog/`, quando a auditoria exigir consulta explícita aos metadados locais;
- `2_INTI/reports/`.

`2_INTI/code/` pode ser consultado quando a auditoria metodológica exigir correspondência entre método descrito e implementação.

Não usar por padrão:

- `2_INTI/x*/`;
- `.venv/`;
- `2_INTI/xdata/`, salvo quando o acesso aos dados locais for explicitamente necessário;
- `1_SUYANA/`;
- diretórios de backup.

Esses locais só entram no escopo mediante solicitação explícita.

### Regra para documentos externos

Um documento externo permanece em Google Drive, OneDrive, Zotero ou outra origem até que exista razão concreta para incorporá-lo ao projeto.

Quando incorporado formalmente, deve existir apenas uma versão ativa e sua fonte canônica deve ser identificável.

### Regra final

Nunca criar sequências como:

`final.docx`
`final2.docx`
`final_final.docx`
`final_agora_vai.docx`

A evolução dos arquivos científicos ativos ocorre pelo Git.

---

## Camada de integração e controle

Esta seção consolida a arquitetura operacional do stack da tese.

O princípio geral é integrar somente componentes que reduzam trabalho, erro ou ambiguidade de forma demonstrável.

Não adicionar ferramentas, MCPs, scripts ou automações apenas porque tecnicamente são possíveis.

### Componentes centrais

#### AGENTS.md

Função:

- porta de entrada automática para agentes de código;
- identifica a fase ativa do projeto;
- direciona para `2_INTI/RESEARCH_PROTOCOL.md`;
- estabelece regras mínimas de segurança.

Não deve se transformar em manual extenso.

#### RESEARCH_PROTOCOL.md

Fonte canônica das regras operacionais do stack.

Contém, entre outros:

- protocolo Codex;
- protocolo Work;
- aperfeiçoamento `/fernando`;
- política de armazenamento;
- fontes canônicas;
- convenções de relatórios e diretórios locais.

#### STYLE_GUIDE.md

Fonte operacional estável para preservar a voz autoral.

Complementa, mas não substitui, exemplos reais de escrita recuperados por ferramentas de Writing Style.

#### CLAIMS_LEDGER.csv

Ponte mínima entre:

claim
→ evidência
→ método
→ limitação
→ status.

Não deve se transformar em uma base bibliométrica geral.

### Dados

A única fonte canônica local dos dados da tese é:

`2_INTI/xdata/`

Não duplicar datasets para notebooks, scripts ou outras ferramentas.

Os notebooks e scripts devem ler diretamente dessa estrutura.

`2_INTI/xdata/catalog/` contém metadados, logs de aquisição, proveniência e documentação dos dados.

O catálogo não constitui uma segunda fonte dos dados e não deve armazenar cópias redundantes dos datasets.

Não criar `DATA_CATALOG.csv` enquanto a estrutura existente cumprir adequadamente essa função.

### Notebooks

Notebooks analíticos futuros devem ser versionados pelo Git.

Local recomendado:

`2_INTI/code/notebooks/`

Esse diretório só precisa ser criado quando houver um notebook analítico real.

Os notebooks devem ler diretamente de `2_INTI/xdata/`.

Não sincronizar nem copiar os dados para uma pasta própria dos notebooks.

### Bibliografia

O Zotero é a fonte canônica de gestão bibliográfica.

Responsabilidades do Zotero:

- metadados;
- PDFs;
- citation keys;
- organização bibliográfica.

Os arquivos:

- `2_INTI/chapters/chap1/library.bib`
- `2_INTI/chapters/chap2/library.bib`

são artefatos científicos versionados pelo Git.

Não criar um `references.bib` global enquanto os artigos permanecerem bibliograficamente independentes.

### Zotero Local API

Manter habilitada.

A Local API demonstrou utilidade para:

- consultar coleções;
- verificar itens;
- validar citation keys;
- comparar bibliotecas;
- apoiar auditorias bibliográficas.

Não habilitar escrita automática por API como padrão.

Qualquer alteração bibliográfica deve permanecer controlada e auditável.

### Better BibTeX

Manter para:

- citation keys;
- exportação bibliográfica;
- interoperabilidade Zotero–BibTeX.

Autoexports devem apontar apenas para áreas locais de staging, nunca diretamente para os `library.bib` científicos versionados.

### Scripts Python

Criar scripts de integração somente quando houver problema concreto a resolver.

O stack atual utiliza, entre outros:

`2_INTI/code/audit_thesis.py`

para auditoria técnica dos artigos.

Não criar um orquestrador geral da tese enquanto as ferramentas atuais funcionarem adequadamente de forma modular.

### MCP

Nenhum MCP adicional é necessário neste momento.

Em particular, não instalar MCP para Zotero enquanto a Local API e o Better BibTeX atenderem ao fluxo com menor complexidade.

A adoção futura de MCP exige benefício concreto em:

- redução de trabalho manual;
- redução de erro;
- acesso atualmente impossível;
- ou simplificação mensurável do workflow.

### Automações adicionais

Não criar automações recorrentes por padrão.

A tese não necessita de execução periódica automática enquanto seu desenvolvimento permanecer orientado por etapas científicas e commits deliberados.

### Auditorias em marcos

Executar auditoria técnica e/ou científica em marcos relevantes, por exemplo:

- antes de enviar versão ao orientador;
- antes de qualificação;
- antes de submissão de artigo;
- após alteração bibliográfica importante;
- após alteração relevante de dados ou método;
- antes de considerar uma versão científica fechada.

Evitar auditoria completa após pequenas alterações textuais.

### Auditoria técnica

Usar:

`2_INTI/code/audit_thesis.py`

para verificações determinísticas de:

- LaTeX;
- BibTeX;
- citekeys;
- DOI;
- duplicatas;
- arquivos esperados;
- compilação;
- warnings relevantes.

Outputs automáticos:
`2_INTI/xreports/`

Relatórios consolidados relevantes:
`2_INTI/reports/`

### Auditoria científica

Usar Work em quatro modos independentes:

- WORK-A — arquitetura argumentativa;
- WORK-B — claim × evidência;
- WORK-C — método × inferência;
- WORK-D — coesão e redação científica.

As auditorias são somente leitura por padrão.

### Fluxo integrado mínimo

Concepção e escrita humana
→
claim relevante
→
LeapSpace adversarial
→
Zotero
→
CLAIMS_LEDGER
→
ChatGPT `/critica`
→
decisão do autor
→
ChatGPT `/fernando` + STYLE_GUIDE
→
LaTeX
→
Git
→
audit_thesis.py / Codex
→
Work
→
revisão final do autor.

### Princípio de complexidade

Adicionar um novo componente somente quando:

benefício operacional esperado

custo de configuração + manutenção + risco de inconsistência.

Se uma integração não superar esse critério, ela não entra no stack.
