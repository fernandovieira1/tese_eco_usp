# Dicionário da avaliação preditiva

Estes são arquivos de diagnóstico, não colunas novas do painel municipal. Os nomes da base de referência permanecem intactos.

| Campo | Definição / unidade |
|---|---|
| id | ID original da série CONAB, uma planilha/cultura/safra/praça/tecnologia |
| praca | Localidade modal da fonte, não unidade validada para todos os municípios |
| ano_data_base, data_base | Ano e data de referência de preços dos custos |
| safra_inicio, safra_fim | Safra original, separada do ano da data-base |
| tecnologia | Rótulo original, inclusive não declarada |
| ex_ant | Indicador original de pacote ExAnt; ausência não certifica gasto realizado |
| y | H operacional em USD2024/ha, herdado da base estrita |
| ano_alvo | Ano da data-base para alinhamento do preditor |
| ano_origem_dap | Ano civil anterior ao ano_alvo |
| n_meses | 12 meses obrigatórios para a média do preditor |
| dap_usd2024_t | Média dos preços mensais DAP previamente deflacionados, USD2024/t |
| x | Log natural de dap_usd2024_t |
| eixo, bloco | Esquema de validação e localidade ou janela temporal retida |
| papel | Treino ou teste, explícito em membros_folds.csv |
| previsto | Previsão somente da observação retida, USD2024/ha |
| observado | Valor de referência modal retido, não gasto municipal observado |
| erro, bias | Previsto menos observado, por linha e média assinada, USD2024/ha |
| mae, rmse | Erro absoluto médio e raiz do erro quadrático médio, USD2024/ha |
| media_alvo | Média dos custos retidos usados para normalizar erro e bias |
| negativo, n_negativos | Previsão abaixo de zero; nenhum truncamento automático |
| extrapola_x, n_extrapola_x | Preditor retido fora do intervalo do treino; não certifica suporte tecnológico ou territorial |
| media_x_treino, sd_x_treino | Média e desvio populacional de x apenas no treino |
| intercepto | Média de y no treino, regressão com x centrado |
| beta_x_padronizado | Coeficiente sobre x padronizado pelo treino |
| lambda | 1 para ridge fixo, 0 para OLS/benchmark; benchmark usa coeficiente zero |
| passou, motivo | Resultado e critérios não satisfeitos do gate pré-fixado |

Não tratar os resultados espaciais e temporais da mesma observação como duplicação de amostra independente. As métricas TODOS agrupam somente um eixo de cada vez, ponderando observações igualmente; médias por fold também estão disponíveis. Os folds temporais de teste são disjuntos. A saída vazia de milho primeira safra significa teste recusado, não erro igual a zero.
