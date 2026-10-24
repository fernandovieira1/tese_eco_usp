# Avaliação agrícola de custos operacionais

Sequência executada: soja, milho primeira safra e milho segunda safra. Resultados, folds, unidades, tecnologias e suporte estão nos três subdiretórios e notebooks numerados. O protocolo foi gravado antes de estimar. Os critérios são de triagem exploratória, não garantia de generalização ou testes de H1.

Soja: 32 referências em Primavera do Leste (17), Campo Novo do Parecis (8) e Sorriso (7), 18 anos de data-base entre 2001 e 2023. Sem cobertura completa anual. Safra pode terminar em 2024; não confundir com data-base 2024. OLS e ridge passam no eixo espacial, mas falham no temporal por deterioração superior a 25% frente ao benchmark no bloco 2016–2019 (MAE OLS 107,70, ridge 105,07 e benchmark 73,58 USD2024/ha). Não flexibilizamos o limiar após observar o resultado.

Milho primeira safra: 9 referências em Primavera do Leste, data-base 2001–2009. Estimação recusada: não permite deixar localidade inteira fora nem satisfaz o mínimo temporal/amostral.

Milho segunda safra: 44 referências em Primavera do Leste (15), Campo Novo do Parecis (10), Sorriso (10), Campo Verde (9), 21 anos de data-base entre 2001 e 2024. OLS e ridge passam pelos gates exploratórios espaciais e temporais. Isso não valida o custo de qualquer município externo às praças. Não selecionamos um vencedor pela pequena diferença de MAE.

O único preditor é o logDAP real médio do ano civil anterior à data-base. A fonte mensal original auditada foi usada, sem defasar novamente campo já lagado. A média/regra do CPI2024 é normalização ex post de moeda, não informação para decisões históricas. O vintage atual impede chamar os resultados de backtest em tempo real. Não há produtividade modal como proxy municipal. O DAP é comum por ano e não produz ajuste espacial municipal.

A validação espacial é retrospectiva entre praças e pode usar anos posteriores no treino; somente a validação temporal impede anos futuros de custo no treino. Não se trata de teste conjunto espaço-temporal. Todos os modelos usam os mesmos folds admissíveis. Intervalos de X excedidos são reportados por fold e por observação; não há previsões negativas. Os erros e o bias são em USD2024/ha e B0 é a média regional do treino, não OLS.

Sete testes cobrem solução analítica, linhagem temporal, separação das amostras, parâmetros calculados exclusivamente no treino, recusa por suporte, preservação de 190 arquivos e duas reproduções de cada cultura em diretórios isolados. Dependência de execução: Python stdlib; notebooks executados no ambiente já instalado nbformat/nbclient/ipykernel. Nenhuma nova dependência de modelagem. Os manifestos registram os inputs e outputs, inclusive o hash do protocolo.

Não houve modelos H1, painel municipal, modificação das bases anteriores, alteração do piloto ou publicação. A amostra e moeda mudaram em relação ao piloto antigo, assim como a exclusão da produtividade modal; diferenças de resultados não isolam efeito de uma única decisão. IMEA permanece fora da estimação. O destino segue autorização específica do usuário para a base paralela, sem reorganizar fontes canônicas existentes.

Artefatos: modelos/base_custos_investigacao/avaliacao_preditiva.
test_holdout_nao_altera_parametros (testar.Test.test_holdout_nao_altera_parametros) ... ok
test_linhagem_e_moeda (testar.Test.test_linhagem_e_moeda) ... ok
test_ols_e_ridge_analiticos (testar.Test.test_ols_e_ridge_analiticos) ... ok
test_preservacao (testar.Test.test_preservacao) ... ok
test_recusa_primeira_safra (testar.Test.test_recusa_primeira_safra) ... ok
test_reproducao_dupla (testar.Test.test_reproducao_dupla) ... ok
test_separacao_folds (testar.Test.test_separacao_folds) ... ok

----------------------------------------------------------------------
Ran 7 tests in 1.393s

OK
