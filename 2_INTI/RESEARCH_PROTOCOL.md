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

Quando solicitado, gere relatório em `2_INTI/reports/`.

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
