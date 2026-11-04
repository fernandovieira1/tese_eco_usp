# Rodada 3 — temporalidade, tendências e mecanismos concorrentes

Protocolo escrito após a rodada2 e antes de executar esta rodada. Rodada2: associação de exposição soja×aptidão mais forte em pastagem e diferença formal entre destinos; composição amostral relevante e sensibilidade à escala. A questão nova é se essas associações estão concentradas no tempo, confundidas com tendências municipais ou choques específicos de bioma. Não perseguir significância; nenhuma variável instrumental ou causalidade presumida.

## Grade predefinida

Todos os modelos lineares têm VD em pp e FE município/ano, salvo indicação. Duas VDs (agricultura, pastagem) por Bxx; Dxx modelam diretamente pastagem−agricultura. Preços no CSV já são t−1; os adicionais t−2 e t−3 são shifts de um/dois anos com conferência de consecutividade, nunca preenchimento de lacunas.

- B01: núcleo de dois preços×aptidão apenas t−1 na amostra onde t−1,t−2,t−3 estão disponíveis (2 ajustes).
- B02: exposições de soja e milho em t−1,t−2,t−3 conjuntamente, na mesma amostra B01 (2). Teste conjunto seis termos, teste da soma de três coeficientes por cultura e IC. As somas representam um aumento persistente na escala padronizada; colinearidade entre lags deve ser reportada. Não incluir VD defasada sem resolver viés Nickell ou alegar instrumentos internos válidos.
- B03: núcleo amplo + tendências lineares municipais (2). Comparação contra rodada2 A01; registrar perda da variação residual e precisão. Pode absorver mecanismo econômico genuíno; não é teste definitivo contra H1.
- B04: núcleo amplo com FE município e bioma×ano (2). Distingue choques médios do bioma de exposição diferencial dentro dele. Nenhuma regressão própria do Pantanal.
- B05: núcleo somente em 2011–2024 (2). Sensibilidade à referência terras2010 do GAEZ, não prova de aptidão exógena; menor T prejudica inferência.
- B06: primeiras diferenças anuais de taxas e exposições, somente anos consecutivos com ambas VDs observadas, com FE município e ano nas diferenças (2). Objeto: variação da taxa associada à variação de exposição, controlando mudanças médias por município; não equivale ao efeito em níveis.
- D02: diferença entre destinos no modelo de lags distribuídos (1), com contrastes acumulados por cultura.
- D03 e D04: diferenças entre destinos com tendências municipais e FE bioma×ano, respectivamente (2).

Total: 15 ajustes, sem expansões por p-valores. Exposições a preços em níveis são padronizadas com as mesmas médias/DP da rodada2; lags adicionais não são reescalados. Não estima lead como controle negativo: antecipação e autocorrelação de preços invalidariam a interpretação de placebo. Não repetir ITS de datas sem controle como mecanismo causal.

## Inferência e famílias

Mesma inferência principal predefinida: scores agregados por ano, Bartlett lag2, referência t(T−1), ajuste N/(N−Ktotal). Sensibilidades DK1, DK3, cluster municipal e two-way bruto. Menos anos não torna DK exato; reportar T. Wald F para testes conjuntos sob covariância de posto pleno. Holm: coeficientes dos lags B02 em família dinamica; demais coeficientes B em robustez_temporal; coeficientes D em diferencas; contrastes cumulativos B02/D02 em cumulativos; testes conjuntos em conjuntos. Não usar p>0,05 como ausência e não testar equivalência sem limiar justificado.

Magnitudes: somas por cultura e resposta diferencial P75−P25 à alta persistente de 10% do preço médio, com IC. Tendências e bioma×ano podem remover confundimento e também exposição relevante; registrar fração da variância após cada absorção, condição da matriz, suporte e datas. A janela pós2010 não determina separação causal pré/pós.

## Critério da próxima etapa

Se resultados forem sensíveis ao período/tendências, investigar influência e heterogeneidade com suporte para saber se poucos territórios/anos explicam o padrão, além de zeros, denominador e não linearidade predefinida. Mesmo estabilidade não demonstra identificação causal. Os próximos ramos devem responder questões diferentes; não repetir até p<0,05. Rodadas locais: nenhum commit/push/publicação.
