# Qualidade — base3 v1

Construção e validação em 24/10/2026. Duas reproduções geraram hashes idênticos para todos os CSVs e manifesto. Quatro testes automatizados passaram, com verificações por linha e cenários sintéticos.

| Verificação | Resultado |
|---|---:|
| Linhas / municípios / anos | 3384 / 141 / 24 |
| Colunas copiadas / derivadas | 41 / 1 |
| Duplicatas município-ano | 0 |
| Desfechos válidos (cada atividade) | 2772 |
| Desfechos ausentes (cada atividade) | 612 |
| Zeros registrados agricultura / pastagem | 265 / 0 |
| Autos contemporâneos elegíveis | 1526 |
| Autos anteriores elegíveis | 1444 |
| Amostra fiscal conjunta | 1140 |
| Amostra conversão + chuva | 2772 |

Os valores e ausências dos 41 campos de origem são textualmente idênticos à base2. A nova defasagem concorda com as máscaras publicadas. O teste inicial detectou diferença de capitalização dos booleanos originais; a função agora reconhece explicitamente FALSE/False, preservando o texto original. Ausência de parcialidade nunca equivale a False. O teste corrigido passou integralmente.

Todos os números observados são finitos; valores não negativos onde aplicável. As taxas observadas pertencem a [0,1] e coincidem com hectares/estoque inicial à tolerância numérica de 1e-12. O denominador é positivo. Chuva tem 12 meses válidos e cobertura conhecida, com 20 anos de referência histórica; anomalias podem ser negativas. Frações de bioma conservam aproximações cartográficas originais, sem renormalização.

Preços permanecem comuns por ano e já defasados segundo a fonte publicada. A relação outcome t / referência t−1 cobre 2000–2023; este teste não refaz a coleta mensal. As unidades diferentes entre carne e grãos permanecem explícitas no dicionário.

Consulte `qualidade_variaveis.csv` para observados, faltas, zeros, booleanos verdadeiros e extremos; `amostras.csv` para municípios/anos de cada máscara. Zeros numéricos não incluem booleanos False. Nenhuma linha foi removida, nenhum ausente foi imputado. Preservação de zeros não é certificação de sua origem absoluta. Cobertura completa não garante exogeneidade ou qualidade perfeita da mensuração.
