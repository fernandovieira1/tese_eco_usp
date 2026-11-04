# O que as rodadas 2–5 permitem concluir sobre H1

**H1 permanece não identificada como afirmação causal global. Há suporte associativo parcial para respostas diferenciais a preços conforme a aptidão, sobretudo na conversão para pastagem, mas a atribuição ao produto e a força inferencial não são estáveis diante de controles e dependência temporal.** Não é correto aceitar H1, rejeitá-la integralmente ou aceitar sua nula com estes exercícios.

As novas rodadas foram locais, com estratégia registrada antes de cada execução. Reutilizam os mesmos dados e foram adaptadas aos diagnósticos anteriores: são exploração estruturada, não confirmação independente. Holm controla famílias delimitadas dentro da rodada, não toda a busca adaptativa. Os coeficientes de várias equações referem-se a objetos distintos.

## Trabalho efetivamente realizado

| Pasta | Notebooks executados | Ajustes | Questão |
|---|---:|---:|---|
| testes2 | 4 | 19 | Amostra ampla/fiscal, autos, preços relativos, diferenças formais entre atividades, PPML/fracional com FE municipais |
| testes3 | 3 | 15 | Lags, somas, tendências, choques bioma×ano, 2011–2024 e primeiras diferenças |
| testes4 | 6 | 24 + 322 diagnósticos | Dinâmica sob controles, influência de cada município/ano, diferenças entre biomas, curvatura, zeros, estoque2001 e painel fixo |
| testes5 | 1 | 8 referências | 32 exercícios wild bootstrap restrito, 36.480 padrões enumerados |

Total novo: **14 notebooks; 66 ajustes substantivos/de referência e 322 refits de influência (388 ajustes ao todo)**. Vários são repetições deliberadas em amostra comum ou para inferência, não hipóteses novas independentes. Os 24 modelos da rodada1 permanecem intactos e não entram nesse total. Não foram usados dados substitutos ou instrumentos inventados.

## Explicações efetivamente discriminadas

### 1. Composição amostral tem importância mensurável

Na equação agrícola, soja×aptidão passa de 0,0288 pp na amostra ampla para 0,0074 pp ao restringir aos casos com fiscalização, antes de adicionar autos. A amostra cai de 2772 para 1140 pares. Assim, comparar modelos com/sem fiscalização sem manter a amostra mistura seleção de observações com o condicionamento adicional. Isso não identifica por que os registros faltam nem autoriza assumir seleção aleatória.

### 2. A associação de referência não depende de um único município ou ano

Para soja×aptidão/pastagem, retirar cada ano individualmente produz coeficientes entre 0,0912 e 0,1202 pp; retirar cada município produz 0,0932 a 0,1161. Nenhuma exclusão individual troca o sinal. Isso contraria a explicação restrita de que uma única observação territorial/temporal gera o padrão de referência. Não elimina confundimento compartilhado, influência conjunta ou dependência espacial.

### 3. O denominador anual, sozinho, não explica o sinal de referência

Fixar o estoque de referência de 2001 muda soja×aptidão/pastagem de 0,1038 para 0,0998 pp na mesma amostra. O estoque2001 continua endógeno e selecionado, e a VD deixa de ser a parcela da vegetação atualmente disponível. O exercício discrimina um componente mecânico da medida; não identifica efeito causal do estoque.

### 4. Atribuição a soja ou milho depende dos choques territoriais controlados

Na amostra ampla, a soma de três lags soja×aptidão/pastagem é 0,1627 pp (IC95 DK [0,1170;0,2085]). Com tendências municipais fica em 0,1637; com FE bioma×ano cai para 0,0102 (IC [−0,0436;0,0640]), enquanto a soma de milho sobe para 0,1287 (IC [0,0533;0,2042]). A versão estática mostra mudança semelhante. Os FE bioma×ano ainda retêm aproximadamente 67% e 61% da variância residual de soja/milho; não há simples absorção completa.

Isso mostra sensibilidade à variação compartilhada dentro dos biomas. Não comprova que uma política específica, custo, clima ou efeito indireto da soja seja o mecanismo. Essas variáveis não foram identificadas por uma regra de atribuição exógena. A passagem agricultura→pastagem ou pastagem→lavoura tampouco é observada pelas VDs de conversão bruta usadas aqui.

### 5. Magnitude econômica existe como cenário condicional, não efeito identificado

No núcleo amplo, uma alta de preço da soja igual a 10% de sua média histórica implica diferença prevista de **0,0782 pp** entre municípios nos percentis 75 e 25 de aptidão, para conversão em pastagem (IC95 DK [0,0290;0,1274]). Isso corresponde a aproximadamente 0,78 ha por 1000 ha de vegetação inicial, na comparação diferencial modelada. Não inclui o efeito comum do preço absorvido por FEano e não é uma previsão causal de política.

Para agricultura, o cenário equivalente é 0,0217 pp, IC [−0,0036;0,0470]. O intervalo admite aumentos positivos; não permite chamar a resposta de economicamente zero. Não houve teste de equivalência porque uma margem de irrelevância substantiva não foi previamente justificada.

### 6. A força inferencial depende de poucos choques temporais

Para a soma soja/pastagem, bootstrap com blocos3 dá p bruto 0,0078125 e Holm 0,125; com blocos2, p bruto 0,0019531 e Holm 0,03125. Não escolher o tamanho de bloco pela rejeição. Independência/simetria entre blocos não está demonstrada. Há apenas 24, 22 ou 14 anos conforme a equação.

Com oito blocos Rademacher, o menor p bilateral é 2/256=0,0078125; Holm para 16 testes exige inicialmente 0,003125. Logo a ausência de rejeição ajustada em blocos3 também resulta da resolução matemática desse procedimento. Com cinco blocos, o mínimo é 0,0625. Isso não demonstra nulidade; expõe o limite da inferência disponível. Os IC reportados são DK, não IC bootstrap.

## Classificação por implicação de H1

| Implicação/questão | Classificação sustentável |
|---|---|
| Resposta diferencial preços×aptidão na conversão para pastagem | Suporte associativo em algumas especificações, sensível à atribuição por produto/choques de bioma e à inferência temporal |
| Resposta agrícola uniformemente positiva | Não sustentada de forma estável; combina imprecisão, forma funcional e sinais condicionais contrários em certas janelas, sem refutação causal |
| Resposta de pastagem maior que agricultura | Diferenças formais positivas no núcleo e em lags; não estáveis para soja sob FE bioma×ano |
| Autos representando efetividade institucional | Não identificação: proxy endógena e incompleta; IC dos termos condicionais não equivalem a ausência do mecanismo institucional |
| Diferenças entre Amazônia e Cerrado | Comparações formais imprecisas após multiplicidade; não prova de homogeneidade; Pantanal sem suporte suficiente |
| Curvatura/margens extensiva e intensiva agrícola | Exploração inconclusiva após multiplicidade, com seleção explícita na amostra positiva |
| Confirmação/negação causal da hipótese global | Não identificada pelos dados e desenhos disponíveis |

## Por que encerrar estas rodadas

O encerramento não decorre de obter ou deixar de obter significância, nem de um número escolhido de rodadas. Foram investigados os ramos admissíveis que respondiam às questões abertas: composição, variáveis institucionais observadas, preços relativos, efeitos municipais/temporais, escalas e distribuições, dinâmica, tendências, choques de bioma, período, influência, heterogeneidade, curvatura, zeros, denominador e dependência temporal. Os resultados distinguem algumas explicações estatísticas e deixam claro o limite de identificação.

Novas combinações dos mesmos regressores poderiam gerar outros p-valores, mas não criariam retorno líquido esperado, aptidão estritamente predeterminada, fiscalização exógena ou mais choques independentes. Não se afirma que toda especificação matemática possível foi testada. Correções adicionais de pequenos T, diferentes pesos bootstrap ou modelos preditivos poderiam ser extensões metodológicas, sem resolver esses vazios de informação. Não seriam evidência nova de causalidade por si sós.

RDD/DiD/IV/GMM não foram executados sem running variable, atribuição, exposição/controle ou condições de momentos verificadas. Não houve teste espacial sem coordenadas/pesos validados neste painel, nem uso de previsão/ML como substituto de identificação. Não foram construídos controles negativos cuja validade não pudesse ser defendida.

## Próximos dados que podem mudar a conclusão

1. Capacidade produtiva anterior ao painel baseada em solo/clima, sem incorporar uso da terra de 2010, e validação de capacidade pecuária.
2. Preços locais, câmbio relevante, custos de produção/conversão/transporte, crédito e medidas defensáveis de expectativas, para aproximar retorno líquido esperado.
3. Esforço de fiscalização e sua alocação, cobertura dos registros e alguma fonte de variação institucional plausivelmente exógena, distinta do número de infrações autuadas.
4. Transições georreferenciadas por uso/cultura e exposição prévia às políticas, com grupo-controle e suporte justificáveis; bioma predominante é insuficiente.
5. Proveniência completa de cobertura dos pares de mapas, denominadores e preços mensais/ano-safra, para auditar a seleção e a temporalidade original.
6. Mais informação temporal independente e/ou desenho com comparação exógena; validação em novos dados sob protocolo definido previamente.

## Arquivos, validação e publicação

Cada pasta contém ESTRATEGIA.md, RESULTADOS.md, notebooks executados, tabelas integrais, sensibilidades, perdas, magnitudes, requisitos e metadados. Os utilitários mínimos compartilhados ficam em testes2. METADADOS.json preserva hashes da base/textos/rodada1; VALIDACAO_INTEGRADA.json confere execução, SE/IC/p/Holm, amostras, somas/contrastes e reprodução do bootstrap. O painel original tem SHA256 `bc396a4f394ae60d6883205f2ca6e8d33b59a4fb419fc5d667591374c8f1c730`.

As novas rodadas **não foram commitadas nem publicadas**. O bloqueio de publicação do escopo ampliado encaminhado pela revisão automática permanece pendente de nova autorização no chat principal. A análise local foi concluída independentemente desse bloqueio.
