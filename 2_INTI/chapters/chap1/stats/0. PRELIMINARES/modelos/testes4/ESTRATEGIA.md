# Rodada 4 — suporte, dinâmica sob controles e influência

Escrita após as rodadas2/3, antes dos ajustes abaixo. Há associação acumulada de exposição soja×aptidão para pastagem, mas sensibilidade do componente estático a choques específicos de bioma e à janela temporal. Esta rodada discrimina concentração em observações, restrições de forma funcional e definição do desfecho. Não remover observações para melhorar significância e não escolher o modelo vencedor pelo p.

## 1. Dinâmica condicionada — 6 modelos

C01: três lags de soja/milho×aptidão + tendências municipais (2 destinos). C02: mesmos lags + FE bioma×ano (2). C03: mesmos lags somente 2011–2024 (2). Mesma definição de lags da rodada3. Testes conjuntos dos seis termos e somas de três coeficientes por cultura com IC. Controlar se menor T/rank/colinearidade tornam a informação frágil. Não apresentar soma robusta em um controle como prova de exogeneidade. Hipóteses de soma nesta rodada compõem família cumulativos (12 contrastes).

## 2. Influência sistemática — diagnósticos, não novos modelos escolhidos

I00: núcleo amplo sem fiscalização em cada destino (2 referências). Reestimar a mesma equação excluindo, um de cada vez, todos municípios observados e todos anos da amostra (esperados 137×2 + 24×2 = 322 refits). Manter escala original, FE e inferência. Exportar cada tentativa e todos coeficientes/IC. Resumir faixas de coeficientes, mudanças de sinal, maior deslocamento e unidades excluídas. Nenhuma exclusão vira especificação preferida por seu resultado. Esses refits são dependentes e são classificados como diagnósticos; eventual p ajustado não equivale a 322 hipóteses científicas distintas.

## 3. Heterogeneidade territorial formal — 6 modelos

H00 núcleo na amostra Amazônia/Cerrado (2); H01 acrescenta interações exposições×indicador Amazônia (2); H02 mesma equação com FE bioma×ano (2). Pantanal excluído desse contraste pela cobertura de quatro municípios/um completo; registrar N perdido. Testar conjuntamente os dois coeficientes diferenciais e estimar slopes por grupo com IC e covariância completa. Bioma predominante permanece proxy territorial, não localização de cada conversão. Não confundir comparação de significâncias com diferença estatística.

## 4. Não linearidade e zeros — 4 modelos

N01: acrescentar preço z ao quadrado × aptidão z para soja e milho, mantendo os termos lineares (2 destinos). Teste conjunto dos dois termos quadráticos; derivadas em z=−1,0,+1 somente com suporte observado, IC por combinação linear. Sem busca de grau, nós ou limiares; pouca informação temporal limita forma funcional.

Z01: indicador de qualquer conversão agrícola (0 ou 100) em TWFE linear, objeto extensivo (1). Z02: log da taxa agrícola somente nos casos estritamente positivos (1), objeto intensivo condicionado à seleção. Zero não é imputado nem acrescido de constante. Não se interpreta seleção por VD positiva como efeito estrutural. Pastagem não tem zeros observados, logo não se estima margem extensiva degenerada. Ocorrência cartográfica não mede decisão consciente de conservação.

## 5. Denominador e painel fixo — 6 modelos

E01: núcleo com taxa corrente apenas nos municípios cujo estoque inicial de 2001 está observado (2). E02: mesma amostra, VD=100×conversão_ha/estoque_2001 (2), uma intensidade por estoque de referência e não taxa da vegetação atualmente disponível. Isola a mudança mecânica de denominador; estoque2001 continua selecionado/endógeno, não instrumento. E03: núcleo na amostra com conversão observada em todos 24 anos (2). Não presumir missing-at-random nem usar ponderação por probabilidade sem modelo de seleção defensável.

Total esperado: 22 ajustes substantivos + 2 referências de influência + 322 refits = 346 ajustes; número exato de refits determinado pelo suporte auditado, sem parada por significância. Todos publicados apenas em arquivos locais.

## Inferência, multiplicidade e encerramento

Principal DK Bartlett lag2, t(T−1), sensibilidades DK1/DK3, cluster municipal, two-way bruto. Não fazer correção PSD oculta. Famílias Holm: coeficientes dinâmica; coeficientes heterogeneidade; coeficientes não linearidade/zeros; coeficientes denominador; coeficientes refits (somente diagnóstico). Somas cumulativas: família separada de 12; slopes territoriais e derivadas: famílias próprias; todos testes conjuntos substantivos corrigidos entre si, mantendo diagnósticos de influência em família distinta. Sem teste de equivalência: não existe margem substantiva justificada antes dos resultados.

Classificar suporte associativo, sinal contrário, imprecisão e não identificação. Se a variação disponível não separar retorno, custos, políticas/atuação institucional e seleção, registrar esse limite e os dados que o resolveriam. Não inventar IV, momentos GMM, running variable, tratamento, coordenadas, custos, expectativas ou controles negativos. Não executar busca de milhares de especificações ou validação preditiva para substituir identificação causal. Encerrar a sequência quando esses ramos admissíveis cobrirem as questões não redundantes abertas, deixando explícito que regressões adicionais não criam informação ausente. Publicação proibida até autorização específica nova.
