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
- relatório consolidado de execução em 2_INTI/reports e artefatos automáticos ou reproduzíveis em 2_INTI/xreports;
- quando a tarefa exigir continuidade, registro correspondente em 2_INTI/thread.

### Regra adicional

O Codex pode identificar e sugerir problemas científicos, econométricos ou metodológicos, mas não deve alterar silenciosamente hipóteses, especificações, equações, estratégia empírica, interpretação científica ou estrutura argumentativa. Essas alterações exigem decisão explícita do autor.

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

Os dados ativos permanecem em `2_INTI/data/`.

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
- `2_INTI/data/catalog/`;
- `2_INTI/reports/`.

`2_INTI/code/` pode ser consultado quando a auditoria metodológica exigir correspondência entre método descrito e implementação.

Não usar por padrão:

- `2_INTI/x*/`;
- `.venv/`;
- `2_INTI/data/raw/`;
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
