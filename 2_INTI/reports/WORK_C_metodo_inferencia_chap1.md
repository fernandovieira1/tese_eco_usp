# WORK-C — Método × inferência — introdução do chap1

Data: 09/10/2026. Solicitação: `/tese_fndo /fernando -- Execute WORK-C somente na introdução do chap1 e no que for pertinente. Deixe o resto do texto intocado`.

## 1. Escopo e parecer

Auditoria metodológica em modo somente leitura, conforme `AGENTS.md`, `RESEARCH_PROTOCOL.md` e `STYLE_GUIDE.md`. Nenhuma recomendação foi implementada. A menção a `/fernando` não foi interpretada como autorização para modificar hipóteses, equações ou texto durante a WORK-C.

**A introdução é coerente como apresentação de um desenho candidato para qualificação, mas ainda não permite validar uma interpretação causal das estimativas futuras.** Ela distingue retorno esperado de seus determinantes observáveis, reconhece a endogeneidade institucional e declara pendências de amostra e mensuração. Não há resultados econométricos anunciados como obtidos.

Foram identificadas **oito questões RELEVANTES para a definição do método**. São decisões pendentes e limites de inferência, não oito erros de redação nem resultados empíricos de viés. Não foi identificado problema CRÍTICO na formulação introdutória examinada. Uma alegação futura de identificação causal sem resolver as condições abaixo mudaria esse diagnóstico.

Não é necessário inserir todos esses detalhes na introdução. A prioridade é desenvolvê-los na seção metodológica quando o autor definir o desenho. A auditoria não recomenda reescrita ampla nem troca automática de método.

### Material examinado

- Leitura integral de `chap1/0_introduction.tex`, inclusive comentários com equações candidatas; distinguem-se esses comentários do texto visível no PDF.
- Consulta de `chap1/2_mt_descriptive.tex` e `chap1/3_econometrics_strategy.tex`: ambos contêm, atualmente, títulos e texto provisório na linha 4. Não há neles descrição operacional suficiente para completar o desenho da introdução.
- Consulta pontual de `chap1/1_literature_review.tex`, linhas 20–26 e 38–46, somente para conferir se as ressalvas sobre preços, exposição e fiscalização já estavam reconhecidas.
- Consulta das referências metodológicas pertinentes em `chap1/library.bib` e do `CLAIMS_LEDGER.csv`; o ledger contém candidatos de suporte bibliográfico, não um protocolo de identificação.

As referências a backups nos comentários das seções provisórias não foram seguidas. Não foram examinados dados brutos, catálogos, código de estimação, chap2 ou versões históricas. Logo, não se certificam cobertura real, tamanho amostral, disponibilidade de variáveis, resultados de testes ou prontidão da base. As linhas citadas abaixo correspondem à versão corrente após as retificações das WORK-A e WORK-B.

## 2. Descritivo, associativo e causal

| Objeto anunciado | Nível que o desenho pode pretender | Condição ou limite atual |
|---|---|---|
| Conversão bruta para agricultura/pastagem, ll. 79 e 127 | **DESCRITIVO**: medir transições e sua participação no estoque nativo inicial. | Depende de harmonização territorial, classificação e construção das transições, declaradas pendentes na l. 205. |
| Preços × capacidade produtiva, ll. 135, 142–158 | **ASSOCIATIVO**: relação condicional entre exposição econômica e conversão. **CAUSAL**, apenas sob identificação justificável. | Efeitos fixos e precedência temporal não bastam. O estimando é uma resposta à exposição observável, não diretamente ao retorno líquido esperado. |
| Interação institucional, ll. 166–195 | **ASSOCIATIVO**: diferença de sensibilidade entre condições institucionais observadas. | Identificar causalmente a resposta ao preço em grupos não equivale a identificar o efeito de mudar as instituições. |
| Comparações por atividade/bioma, ll. 76 e 198 | **DESCRITIVO/ASSOCIATIVO**; eventual heterogeneidade causal depende do mesmo desenho de identificação. | Exige definição territorial, suporte comparável e testes de diferenças entre coeficientes. |
| Subsídios a políticas, l. 87 | Implicação aplicada condicionada às evidências futuras. | Não identifica automaticamente eficácia de políticas, efeitos de equilíbrio geral ou ganhos de bem-estar. O texto já evita prometer avaliação direta de mecanismos de mercado. |

Os verbos causais nas hipóteses expressam previsões a testar, não causalidade já demonstrada. As evidências de outros autores citadas na contextualização também não transferem suas estratégias de identificação para este artigo.

## 3. Questões metodológicas

### C01 — Fonte de identificação da exposição a preços ainda não está definida

- **Localização:** introdução, ll. 79, 113–124, 142–155 e 205; conferência pertinente na revisão, l. 24.
- **Inferência pretendida:** efeito de variações de preços, ponderadas pela capacidade produtiva local, sobre a conversão.
- **Problema metodológico:** o índice comentado combina variações de preços comuns e exposições territoriais. A seleção das exposições e os determinantes dos preços podem estar relacionados a fatores que também afetam a conversão. Choques de oferta, custos, crédito, infraestrutura ou políticas com incidência territorial desigual não são eliminados apenas por efeitos fixos de município e ano. Preços internacionais tampouco são automaticamente exógenos. A revisão já reconhece parte dessas ameaças; falta sua resolução operacional.
- **Consequência:** sem hipótese de identificação e comparação contrafactual justificadas, o coeficiente deve ser interpretado como associação condicional. Não se conclui que será necessariamente viesado, mas a interpretação causal permanece não demonstrada.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** especificar quais preços e exposições geram a variação utilizada; explicar a comparação entre territórios mais e menos expostos e a evolução esperada sem aquela variação. Examinar quais atividades dominam o índice, tendências diferenciais e sensibilidade a controles anteriores ao incentivo. Diagnósticos de antecipações e períodos anteriores podem revelar incompatibilidades, mas não provar exogeneidade. Separar controles de confundimento de variáveis potencialmente afetadas pelo próprio incentivo, como crédito ou área produzida contemporâneos, conforme o mecanismo.
- **Decisão do autor:** adotar inicialmente um objetivo associativo ou defender uma estratégia causal específica, com pressupostos sobre choques/exposições e canais alternativos. O índice não deve ser chamado de instrumento sem definir variável instrumentada e condição de exclusão.

### C02 — O índice agregado impõe restrições ao teste de H1-a

- **Localização:** introdução, ll. 106, 135, 142–156 e 158; revisão, l. 26.
- **Inferência pretendida:** maior resposta ao aumento de preço onde a capacidade produtiva para o uso beneficiado é maior; evidência sobre uma implicação de H1.
- **Problema metodológico:** o comentário propõe `ShockReturn_it = soma_k[Delta ln(P_k,t-1) × S_ik]`, com um coeficiente comum. Essa construção agrega atividades e impõe uma relação proporcional entre exposição e resposta. Soja, milho e pecuária não são automaticamente comparáveis em unidade de capacidade, formação de retorno ou margem de conversão. Preços também podem alterar custos de outros usos ou incentivar substituição entre atividades. Além disso, resposta a crescimento de preço não é o mesmo parâmetro que resposta ao seu nível ou a retorno persistentemente elevado.
- **Consequência:** um coeficiente positivo pode sustentar a previsão na parametrização restrita, mas não demonstra separadamente o mesmo mecanismo para toda atividade, nem identifica o efeito estrutural do retorno esperado. A distinção já feita na l. 158 é adequada e deve permanecer.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** definir produtos, unidades, normalização e interpretação dos pesos; justificar a agregação e comparar, se houver suporte, respostas por destino da conversão e exposições desagregadas. Escolher previamente o horizonte de resposta e a transformação dos preços. Uma ilustração algébrica, sem estimar dados: com um produto e `Q_it = g_t × S_i`, a inclinação em relação a `g_t` no modelo linear é `beta × S_i`. Estimar `beta` testa o sinal dessa relação restrita; não verifica livremente qualquer formato de heterogeneidade. O efeito de preço comum é absorvido por efeitos de ano, mas sua interação com exposição variável entre municípios pode continuar identificável.
- **Decisão do autor:** qual efeito será estimado — índice agregado, respostas por produto/destino ou ambos — e quais restrições econômicas da agregação são defensáveis. Nenhuma equação foi alterada.

### C03 — Moderador institucional endógeno e interpretação de sua interação

- **Localização:** introdução, ll. 166, 170–192, 195 e 205; revisão, ll. 44–46.
- **Inferência pretendida:** condições institucionais modificam a sensibilidade da conversão ao incentivo econômico.
- **Problema metodológico:** fiscalização e registros administrativos podem responder à conversão passada, à pressão prevista, à capacidade de detectar infrações e à composição territorial. Defasar a variável não elimina esses vínculos. Mesmo quando a medida representar efetividade de forma defensável, ela pode continuar endógena. Uma medida anterior ao choque pode definir grupos, mas diferenças entre esses grupos não identificam automaticamente o efeito de uma intervenção sobre a instituição.
- **Consequência:** o coeficiente da interação pode refletir moderação associativa e seleção territorial. Não autoriza, isoladamente, concluir que elevar a fiscalização reduziria a resposta ao preço. Esse limite é diferente do problema de mensuração de autos/multas, corretamente reconhecido na l. 195.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** escolher uma dimensão institucional por mecanismo, documentar cobertura e separar falta de registro de ausência de fiscalização. Definir se a medida será fixa no período de referência ou variável no tempo. Reportar a resposta marginal `beta_1 + beta_3 × I`, com intervalo de confiança e suporte observado. Conferir termos de menor ordem não absorvidos pelos efeitos fixos quando a interpretação envolver preço, aptidão e instituição separadamente; a adequação depende da parametrização escolhida, não de uma obrigação automática de adicionar termos. Identificação causal da instituição requer fonte adicional de variação defensável; não importar automaticamente instrumentos de outro artigo.
- **Decisão do autor:** investigar heterogeneidade segundo instituições observadas ou o efeito causal de uma mudança institucional. A hipótese ampla comporta a primeira etapa, desde que sua interpretação seja explícita.

### C04 — Calendário, defasagens e horizonte da resposta precisam corresponder à decisão

- **Localização:** introdução, ll. 109–116, 140–155, 171–174 e 205.
- **Inferência pretendida:** incentivos conhecidos antes da decisão explicam conversão posterior, no painel candidato 2001–2024.
- **Problema metodológico:** ainda não estão fixados a janela de observação da conversão, o calendário das atividades, a agregação dos preços e a data relevante dos registros institucionais. Uma média anual defasada pode não representar a informação disponível na decisão; também pode ignorar antecipação e respostas distribuídas no tempo. Ano de infração, detecção, autuação e pagamento não são intercambiáveis.
- **Consequência:** a mesma notação `t-1` pode produzir alinhamentos temporais distintos, alterando o significado do coeficiente e a amostra efetiva. Defasagem cronológica não constitui, por si, identificação causal.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** elaborar uma tabela de calendário por variável; justificar a janela principal com base na decisão econômica e no produto observado. Avaliar defasagens alternativas ou resposta acumulada conforme plausibilidade e suporte. No desenho comentado, conversão em 2001 requer estoque inicial compatível com 2000; se o incentivo for `Delta ln(P_2000)`, requer preços de 2000 e 1999. Isso é uma necessidade lógica da fórmula candidata, não constatação de ausência desses dados.
- **Decisão do autor:** qual decisão temporal será representada, qual horizonte de efeito interessa e qual período permanecerá após compatibilizar as séries.

### C05 — Capacidade produtiva predeterminada exige escolha e validação próprias

- **Localização:** introdução, ll. 79, 135, 139–142, 158 e 205.
- **Inferência pretendida:** a capacidade produtiva preexistente modifica a resposta a preços.
- **Problema metodológico:** aptidão biofísica, produtividade potencial e produtividade observada histórica representam conceitos diferentes. PAM/PPM podem refletir especialização, tecnologia, investimento e seleção de produtores, não apenas condições naturais. Uma superfície fixa tampouco se torna exógena por não variar anualmente: sua construção pode usar informações posteriores ao início do painel ou se relacionar com trajetórias omitidas.
- **Consequência:** a heterogeneidade estimada pode captar especialização prévia ou outras diferenças territoriais. Não é possível confirmar “predeterminada” sem identificar produto, versão, insumos e período de referência. Esta auditoria não verificou a composição dos arquivos locais de GAEZ ou das séries históricas.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** documentar a medida escolhida, sua base temporal e o mecanismo que representa; confrontar aptidão e produtividade observada apenas como alternativas conceitualmente distintas. Verificar se a aptidão é calculada sobre o território inteiro ou sobre as áreas nativas expostas à conversão e como entram áreas restritas ao uso. Uma medida construída com dados posteriores pode ser aceitável em certos casos de reconstrução biofísica, mas precisa de justificativa, não de aprovação automática ou rejeição apenas pelo ano de publicação.
- **Decisão do autor:** qual conceito de capacidade produtiva será testado e quais reconstruções temporais e agregações espaciais são compatíveis com ele.

### C06 — Conversão bruta, estoque em risco e destino do uso ainda precisam ser operacionalizados

- **Localização:** introdução, ll. 79, 109, 127, 138 e 205.
- **Inferência pretendida:** taxa de vegetação nativa convertida para agricultura ou pastagem em relação ao estoque nativo inicial.
- **Problema metodológico:** a definição conceitual é clara, mas ainda faltam regras para classes, transições, denominador zero ou muito pequeno e mudanças de classificação. Variação líquida do estoque não identifica, sozinha, conversão bruta. Uma trajetória vegetação → pastagem → lavoura difere de conversão direta para lavoura; o destino anual observado não revela necessariamente a motivação econômica original. Erros de classificação entre anos podem gerar transições aparentes.
- **Consequência:** medidas alternativas respondem a perguntas distintas. A taxa se refere ao estoque remanescente sujeito à conversão naquele período, não à conversão acumulada desde o início do painel. Estoques remanescentes pequenos e seleção histórica das áreas podem mudar a composição do conjunto observado. Isso não invalida a taxa, mas limita sua interpretação e sua comparação com efeitos sobre hectares totais.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** fixar uma tabela de transições admissíveis, com classes compatíveis entre biomas; definir agricultura/pastagem como destinos mutuamente exclusivos quando pertinente. Verificar coerência entre áreas convertidas e estoque inicial, distinguir ausências de zero e documentar casos sem denominador. Examinar sensibilidade a pequenas áreas, persistência de transições e métricas em hectares, sem substituir a taxa principal silenciosamente. Justificar ponderação: município médio e hectare nativo médio correspondem a alvos diferentes.
- **Decisão do autor:** conversão direta versus trajetória posterior, tratamento de regeneração/reconversão, população em risco e regras de inclusão. A introdução já admite que a construção está pendente; não é preciso preenchê-la com todos esses detalhes.

### C07 — Município–ano e heterogeneidade por bioma exigem compatibilização territorial

- **Localização:** introdução, ll. 71, 76, 79, 198 e 205.
- **Inferência pretendida:** comparar respostas entre atividades e biomas de Mato Grosso.
- **Problema metodológico:** limites municipais podem variar e um município pode abranger mais de um bioma. Uma variável municipal não é automaticamente uma variável de município × bioma. Desagregar áreas de conversão sem compatibilizar preços, exposição e instituições pode criar precisão aparente. Diferenças de disponibilidade de registros também podem selecionar a amostra de H1-b em relação à de H1-a.
- **Consequência:** a comparação pode refletir composição territorial, classificação de municípios ou mudança de amostra. Uma relação municipal não identifica decisões individuais de produtores. A ressalva sobre suporte amostral na l. 198 é pertinente, mas ainda não define como verificar essa comparabilidade.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** escolher geografia comparável no tempo e uma regra de atribuição a biomas, explicitando a perda de informação quando houver agregação. Tabular número de unidades, área nativa, exposição e dados ausentes por grupo/ano; distinguir queda amostral por cobertura de ausência econômica. Quando possível, comparar especificações numa amostra comum. Testar diferenças entre coeficientes diretamente: significância em um grupo e não em outro não demonstra diferença entre eles. Ponderar a multiplicidade de comparações exploratórias e apresentar magnitude e precisão.
- **Decisão do autor:** unidade efetiva, regra territorial, população à qual os resultados se aplicam e contrastes principais. Nenhuma subdivisão espacial ou exclusão amostral foi decidida nesta auditoria.

### C08 — Dependência dos erros e deslocamento da conversão são problemas distintos

- **Localização:** introdução, ll. 57, 113–120, 148–151, 183–186, 198 e 205.
- **Inferência pretendida:** quantificar magnitude e precisão das respostas, com possível relevância para conservação territorial.
- **Problema metodológico:** municípios podem compartilhar choques de preços, condições climáticas, mercados e políticas, além de apresentar persistência temporal. O número de observações município–ano não equivale ao número de choques independentes. Separadamente, a pressão econômica ou a fiscalização podem deslocar conversão entre municípios e usos; isso altera o parâmetro de interesse, não apenas o erro-padrão.
- **Consequência:** uma estrutura inadequada de covariância pode produzir intervalos pouco confiáveis. Corrigir erros-padrão espaciais não elimina viés por confundimento nem identifica efeitos indiretos. Um efeito local de contenção não demonstra redução agregada quando há deslocamento.
- **Gravidade:** RELEVANTE.
- **Alternativa/teste recomendado:** definir inferência compatível com a origem da variação e a dependência residual, considerando correlação serial, espacial e exposição a choques comuns. Agrupamento municipal, agrupamentos adicionais e covariância espacial são alternativas a justificar, não uma lista a aplicar mecanicamente; avaliar limitações de poucos grupos/choques. Se o objetivo abranger deslocamentos, definir exposição de vizinhança ou análises em agregações maiores e distinguir efeito direto, indireto e total. Não acrescentar automaticamente a conversão dos vizinhos como regressor, pois isso introduz novos problemas de simultaneidade.
- **Decisão do autor:** qual efeito territorial interessa e qual estrutura de inferência é compatível com o desenho e a amostra finais. A preocupação já mencionada na l. 205 precisa de implementação posterior.

## 4. Fundamentação metodológica consultada

As questões acima são diagnósticos do desenho escrito, não resultados extraídos das bases. Para conferir os pontos especializados, foram consultadas fontes primárias já presentes na biblioteca do capítulo; nenhuma referência foi acrescentada ao texto ou ao `.bib`.

- [Goldsmith-Pinkham, Sorkin e Swift (2020), resumo original da AER](https://www.aeaweb.org/articles?id=10.1257/aer.20181047): examina identificação por exposições na utilização típica de instrumentos Bartik. Fundamenta a cautela de C01 com exposições a choques comuns. Não implica que toda construção preço × aptidão seja automaticamente um instrumento, nem que exista apenas uma via possível de identificação.
- [Berman et al. (2023), passagens originais indexadas pela editora](https://www.sciencedirect.com/science/article/abs/pii/S0095069623000372), especialmente introdução e seção de endogeneidade: discute ameaças ligadas à oferta, preços e exposições e apresenta verificações próprias. Sustenta a necessidade de justificar essas condições em Mato Grosso, sem transferir a validade do desenho tropical para o painel proposto. A abertura direta retornou bloqueio de acesso; não se afirma leitura integral nesta tarefa.
- [Conley (1999), resumo e introdução originais indexados pela editora](https://www.sciencedirect.com/science/article/pii/S0304407698000840): trata de estimação da covariância sob dependência espacial. A distinção entre correção da covariância e identificação de efeitos de deslocamento em C08 é uma implicação metodológica aplicada ao desenho da tese, não um resultado empírico do artigo.

Não foram buscadas especificações prontas para substituir as propostas do autor, nem efetuados testes econométricos sem dados e desenho definidos.

## 5. Implicações para a introdução e sequência de decisões

**Preservar:** a distinção entre hipótese e resultado; a ressalva de que H1-a testa uma implicação observável; a não equivalência entre autos/multas e efetividade; os limites de interpretação de resultados nulos; o caráter candidato da unidade/período; as pendências de harmonização e conversões brutas; o limite da contribuição para políticas.

**Não exigir da introdução:** especificação completa de controles, todas as janelas temporais, regras de classificação, escolha de covariância ou demonstração técnica de identificação. A ausência desses detalhes numa introdução, isoladamente, não constitui erro. Aqui, a impossibilidade de validar o método resulta também de as seções operacionais atuais ainda serem provisórias.

**Ajuste introdutório eventualmente útil, sem aplicação:** ao consolidar a estratégia, explicitar no resumo metodológico da l. 205 qual nível de inferência será adotado se as condições causais não puderem ser defendidas. O objetivo da l. 79 já menciona esses limites; não é necessário antecipar uma promessa de causalidade nem enfraquecer as hipóteses apenas por estarem pendentes de teste.

**Ordem de resolução recomendada:** definir primeiro o efeito de interesse e as margens de conversão; em seguida, fixar unidade, amostra, calendário e exposição; então justificar identificação e moderação institucional; por fim, escolher inferência, contrastes e robustez compatíveis. Essas decisões não se resolvem apenas trocando verbos no texto.

## 6. Integridade e entrega

- Estado inicial: branch `main`; introdução já modificada pelas etapas anteriores; quatro relatórios anteriores não rastreados. Essas condições foram preservadas.
- Único arquivo criado nesta tarefa: `2_INTI/reports/WORK_C_metodo_inferencia_chap1.md`.
- Verificação por hashes SHA-256 dos `.tex` e `.bib` sob `2_INTI/chapters/` e do `CLAIMS_LEDGER.csv`, comparados antes/depois. Nenhum desses arquivos foi alterado.
- Conferência de whitespace e estado final do Git. Sem compilação LaTeX, pois nenhum arquivo de composição foi modificado; sem execução de código de dados ou estimação.
- Sem alteração de hipóteses, metodologia, equações, dados, citekeys, introdução ou demais seções; sem commit, merge ou push.
