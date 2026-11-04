# Custo operacional: soja

Conceito H = A+B+C+E+F, exclui renda de fatores I. 32 séries, 3 praças, 18 anos de data-base. Moeda USD2024/ha. Perdas por preditor/moeda: 0.

Cobertura exata em cobertura.csv: ano da data-base não equivale necessariamente à safra. Tecnologias e ExAnt permanecem identificados. Componentes em componentes_suporte.csv não são novas unidades independentes.

| Eixo | Modelo | N | MAE | RMSE | Bias | Extrapola X |
|---|---|---:|---:|---:|---:|---:|
| espacial | B0_media_regional | 32 | 198.73 | 246.50 | 3.43 | 8 |
| espacial | M1_ols | 32 | 147.20 | 183.96 | -20.46 | 8 |
| espacial | M2_ridge | 32 | 139.43 | 177.80 | -18.58 | 8 |
| temporal | B0_media_regional | 20 | 208.96 | 284.47 | -103.82 | 0 |
| temporal | M1_ols | 20 | 155.83 | 205.26 | -83.97 | 0 |
| temporal | M2_ridge | 20 | 156.72 | 207.37 | -84.17 | 0 |

Decisão: nao_passou_gate_preditivo. Gate municipal: NÃO VALIDADO.

As previsões são apenas holdouts dos polos. MAE/bias em USD2024/ha. B0 é média regional do treino, não OLS. Validação espacial retrospectiva e temporal prospectiva são eixos separados, não validação conjunta.

DAP é comum por ano, sem ajuste municipal. Choques compartilhados e somente 3–4 praças limitam a evidência; número de linhas não é número de choques independentes. Sem intervalos de confiança, causalidade, significância ou busca adicional. Modelos não aprovados ficam registrados. Nem eventual ganho autoriza extrapolar tecnologias, praças ou anos ausentes. IMEA não entra, por falta de comparabilidade validada.

O piloto antigo usava amostra anterior, produtividade modal e BRL/IPCA. Esta avaliação em USD com preditor transferível é novo desenho, não diferença causal de desempenho atribuível apenas à exclusão de duas planilhas. O piloto antigo foi preservado.
