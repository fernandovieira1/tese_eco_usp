# Custo operacional: milho_2a

Conceito H = A+B+C+E+F, exclui renda de fatores I. 44 séries, 4 praças, 21 anos de data-base. Moeda USD2024/ha. Perdas por preditor/moeda: 0.

Cobertura exata em cobertura.csv: ano da data-base não equivale necessariamente à safra. Tecnologias e ExAnt permanecem identificados. Componentes em componentes_suporte.csv não são novas unidades independentes.

| Eixo | Modelo | N | MAE | RMSE | Bias | Extrapola X |
|---|---|---:|---:|---:|---:|---:|
| espacial | B0_media_regional | 44 | 192.67 | 238.46 | 9.45 | 7 |
| espacial | M1_ols | 44 | 114.35 | 169.31 | -4.62 | 7 |
| espacial | M2_ridge | 44 | 114.17 | 168.85 | -4.00 | 7 |
| temporal | B0_media_regional | 26 | 181.84 | 233.96 | -74.56 | 0 |
| temporal | M1_ols | 26 | 108.34 | 158.63 | -43.28 | 0 |
| temporal | M2_ridge | 26 | 109.22 | 160.20 | -43.94 | 0 |

Decisão: gate_exploratorio_passou_sem_validacao_municipal. Gate municipal: NÃO VALIDADO.

As previsões são apenas holdouts dos polos. MAE/bias em USD2024/ha. B0 é média regional do treino, não OLS. Validação espacial retrospectiva e temporal prospectiva são eixos separados, não validação conjunta.

DAP é comum por ano, sem ajuste municipal. Choques compartilhados e somente 3–4 praças limitam a evidência; número de linhas não é número de choques independentes. Sem intervalos de confiança, causalidade, significância ou busca adicional. Modelos não aprovados ficam registrados. Nem eventual ganho autoriza extrapolar tecnologias, praças ou anos ausentes. IMEA não entra, por falta de comparabilidade validada.

O piloto antigo usava amostra anterior, produtividade modal e BRL/IPCA. Esta avaliação em USD com preditor transferível é novo desenho, não diferença causal de desempenho atribuível apenas à exclusão de duas planilhas. O piloto antigo foi preservado.
