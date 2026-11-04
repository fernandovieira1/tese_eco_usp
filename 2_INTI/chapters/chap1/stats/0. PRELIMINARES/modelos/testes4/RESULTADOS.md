# Resultados — rodada 4

346 ajustes: 22 substantivos, 2 referências e 322 refits diagnósticos leave-one-out. Não são 346 desenhos independentes. Todas as reestimações e exclusões foram registradas, sem escolha de observação pelo resultado. Seis notebooks concluídos; a rodada1 e fontes foram preservadas.

## O que os diagnósticos discriminam

A associação estática soja×aptidão/pastagem mantém o sinal em todas exclusões individuais de município/ano. Nas exclusões anuais, o coeficiente varia entre 0,0912 e 0,1202 pp; nas municipais, entre 0,0932 e 0,1161. Isso afasta a explicação estrita de que um único município ou ano produz o sinal da especificação de referência; não elimina confundimento comum nem valida causalidade. Milho/agricultura pode trocar de sinal em exclusões isoladas e permanece impreciso.

A soma dinâmica de soja/pastagem é 0,1637 com tendências municipais (IC95 [0,0985;0,2290]), mas 0,0102 com FE bioma×ano (IC95 [−0,0436;0,0640]). Nesse segundo controle, milho/pastagem soma 0,1287 (IC95 [0,0533;0,2042]). Portanto, é instável atribuir a co-movimentação diferencial a um produto específico. Isso é compatível com confundimento/heterogeneidade de choques, mas não identifica quais políticas, custos ou mecanismos os geraram. Na janela pós2010, a soma milho/agricultura é negativa sob inferência DK, contraponto à versão universal de resposta positiva; T=14 e o resultado exige cautela adicional de inferência.

Os testes conjuntos das diferenças de slopes Amazônia−Cerrado não rejeitam após multiplicidade e seus IC são amplos. Isso não demonstra homogeneidade entre biomas. A classificação por predominância municipal limita qualquer interpretação de geografia do desmatamento. Pantanal não foi forçado a fornecer um efeito próprio.

A evidência de curvatura agrícola não passa a correção dos testes conjuntos substantivos; não escolher um limiar de preço a posteriori. As margens de ocorrência e taxa estritamente positiva são imprecisas. Ausência de rejeição não implica ausência de mecanismo ou conservação ativa. O modelo condicionado a positivos tem seleção pela VD e é apenas descritivo.

Fixar o estoque de referência de 2001 altera pouco a associação soja/pastagem no núcleo. Assim, o movimento anual do denominador, sozinho, não explica esse coeficiente nessa especificação. O estoque2001 continua endógeno/selecionado. O painel fixo mantém sinais de pastagem, mas a precisão individual se reduz após multiplicidade. Isso não justifica assumir missing-at-random.

## Por que mais uma rodada

Alguns Wald F das equações com seis lags ficaram extremamente elevados na janela de 14 anos. A etapa5 terá foco exclusivo em inferência sob poucos blocos temporais, não novos regressores. Testes assintóticos fortes não tornam o desenho identificado. A validade de independência/simetria entre blocos também precisará ser explicitada; não há teste finito exato garantido por estes dados observacionais.

## Resumo da influência

| eixo | destino | termo | referencia | min_coef | max_coef | sinais_contrarios | maior_deslocamento_abs | unidade_maior_deslocamento | refits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ano | agricultura | expo_milho | 0.003751 | -0.000835 | 0.007565 | 1 | 0.004586 | 2004 | 24 |
| ano | agricultura | expo_soja | 0.028791 | 0.012369 | 0.032468 | 0 | 0.016422 | 2003 | 24 |
| ano | pastagem | expo_milho | 0.058373 | 0.044362 | 0.075214 | 0 | 0.016841 | 2012 | 24 |
| ano | pastagem | expo_soja | 0.103806 | 0.091169 | 0.120156 | 0 | 0.01635 | 2022 | 24 |
| id | agricultura | expo_milho | 0.003751 | -0.003246 | 0.006566 | 1 | 0.006997 | 5102678 | 137 |
| id | agricultura | expo_soja | 0.028791 | 0.020161 | 0.035639 | 0 | 0.008631 | 5104526 | 137 |
| id | pastagem | expo_milho | 0.058373 | 0.039181 | 0.08238 | 0 | 0.024007 | 5106505 | 137 |
| id | pastagem | expo_soja | 0.103806 | 0.093185 | 0.116092 | 0 | 0.012286 | 5100805 | 137 |

## Coeficientes substantivos (refits integrais no CSV)

| id | termo | coef | ic95_inf | ic95_sup | p | p_holm | N | anos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E01_agricultura | expo_soja | 0.028791 | -0.004729 | 0.062312 | 0.088833 | 0.444166 | 2772 | 24 |
| E01_agricultura | expo_milho | 0.003751 | -0.006527 | 0.014028 | 0.45794 | 1.0 | 2772 | 24 |
| E02_agricultura | expo_soja | 0.027901 | -0.00249 | 0.058293 | 0.070159 | 0.420952 | 2772 | 24 |
| E02_agricultura | expo_milho | 0.003258 | -0.005799 | 0.012314 | 0.464318 | 1.0 | 2772 | 24 |
| E01_pastagem | expo_soja | 0.103806 | 0.038532 | 0.16908 | 0.003208 | 0.035287 | 2772 | 24 |
| E01_pastagem | expo_milho | 0.058373 | 0.00291 | 0.113836 | 0.039979 | 0.359812 | 2772 | 24 |
| E02_pastagem | expo_soja | 0.099843 | 0.039088 | 0.160598 | 0.002461 | 0.029532 | 2772 | 24 |
| E02_pastagem | expo_milho | 0.04453 | 0.0001 | 0.088961 | 0.049528 | 0.359812 | 2772 | 24 |
| E03_agricultura | expo_soja | 0.026554 | -0.004761 | 0.057869 | 0.092718 | 0.444166 | 2280 | 24 |
| E03_agricultura | expo_milho | 0.00709 | -0.008209 | 0.022388 | 0.347695 | 1.0 | 2280 | 24 |
| E03_pastagem | expo_soja | 0.079162 | 0.006739 | 0.151585 | 0.033515 | 0.335155 | 2280 | 24 |
| E03_pastagem | expo_milho | 0.100342 | 0.003313 | 0.197371 | 0.043254 | 0.359812 | 2280 | 24 |
| I00_agricultura | expo_soja | 0.028791 | -0.004729 | 0.062312 | 0.088833 | 1.0 | 2772 | 24 |
| I00_agricultura | expo_milho | 0.003751 | -0.006527 | 0.014028 | 0.45794 | 1.0 | 2772 | 24 |
| I00_pastagem | expo_soja | 0.103806 | 0.038532 | 0.16908 | 0.003208 | 1.0 | 2772 | 24 |
| I00_pastagem | expo_milho | 0.058373 | 0.00291 | 0.113836 | 0.039979 | 1.0 | 2772 | 24 |
| H00_agricultura | expo_soja | 0.027672 | -0.005281 | 0.060625 | 0.095734 | 0.861603 | 2718 | 24 |
| H00_agricultura | expo_milho | 0.006648 | -0.0083 | 0.021595 | 0.367102 | 1.0 | 2718 | 24 |
| H00_pastagem | expo_soja | 0.087385 | 0.005949 | 0.168821 | 0.036573 | 0.694879 | 2718 | 24 |
| H00_pastagem | expo_milho | 0.110978 | -0.003878 | 0.225835 | 0.057582 | 0.845011 | 2718 | 24 |
| H01_agricultura | expo_soja | 0.026023 | -0.000763 | 0.052808 | 0.056334 | 0.845011 | 2718 | 24 |
| H01_agricultura | expo_milho | 0.01852 | -0.005759 | 0.042798 | 0.128226 | 1.0 | 2718 | 24 |
| H01_agricultura | expo_soja_amazonia | 0.088213 | -0.00267 | 0.179097 | 0.056543 | 0.845011 | 2718 | 24 |
| H01_agricultura | expo_milho_amazonia | -0.183216 | -0.367781 | 0.001349 | 0.051561 | 0.830313 | 2718 | 24 |
| H01_pastagem | expo_soja | 0.040194 | -0.095793 | 0.17618 | 0.546909 | 1.0 | 2718 | 24 |
| H01_pastagem | expo_milho | 0.087823 | -0.0118 | 0.187446 | 0.081229 | 0.845011 | 2718 | 24 |
| H01_pastagem | expo_soja_amazonia | -0.032707 | -0.202796 | 0.137381 | 0.694449 | 1.0 | 2718 | 24 |
| H01_pastagem | expo_milho_amazonia | 0.32384 | 0.001789 | 0.645892 | 0.048842 | 0.830313 | 2718 | 24 |
| H02_agricultura | expo_soja | 0.02331 | 0.001195 | 0.045425 | 0.039708 | 0.714748 | 2718 | 24 |
| H02_agricultura | expo_milho | 0.019801 | -0.006377 | 0.04598 | 0.131308 | 1.0 | 2718 | 24 |
| H02_agricultura | expo_soja_amazonia | 0.083858 | -0.005319 | 0.173035 | 0.064066 | 0.845011 | 2718 | 24 |
| H02_agricultura | expo_milho_amazonia | -0.179 | -0.366137 | 0.008136 | 0.059944 | 0.845011 | 2718 | 24 |
| H02_pastagem | expo_soja | -0.011904 | -0.050329 | 0.026522 | 0.527962 | 1.0 | 2718 | 24 |
| H02_pastagem | expo_milho | 0.1113 | 0.048425 | 0.174174 | 0.001297 | 0.025945 | 2718 | 24 |
| H02_pastagem | expo_soja_amazonia | -0.043419 | -0.27112 | 0.184282 | 0.696875 | 1.0 | 2718 | 24 |
| H02_pastagem | expo_milho_amazonia | 0.291991 | -0.56817 | 1.152153 | 0.489583 | 1.0 | 2718 | 24 |
| C01_agricultura | expo_soja_l1 | 0.012281 | -0.021006 | 0.045569 | 0.451469 | 1.0 | 2539 | 22 |
| C01_agricultura | expo_soja_l2 | 0.00124 | -0.036964 | 0.039444 | 0.946821 | 1.0 | 2539 | 22 |
| C01_agricultura | expo_soja_l3 | 0.021605 | -0.001588 | 0.044797 | 0.066285 | 1.0 | 2539 | 22 |
| C01_agricultura | expo_milho_l1 | 0.004865 | -0.007553 | 0.017284 | 0.424345 | 1.0 | 2539 | 22 |
| C01_agricultura | expo_milho_l2 | -0.011558 | -0.033821 | 0.010705 | 0.292535 | 1.0 | 2539 | 22 |
| C01_agricultura | expo_milho_l3 | 0.001437 | -0.014442 | 0.017315 | 0.852562 | 1.0 | 2539 | 22 |
| C01_pastagem | expo_soja_l1 | 0.006934 | -0.101525 | 0.115394 | 0.89549 | 1.0 | 2539 | 22 |
| C01_pastagem | expo_soja_l2 | 0.05025 | -0.028881 | 0.12938 | 0.200848 | 1.0 | 2539 | 22 |
| C01_pastagem | expo_soja_l3 | 0.106558 | 0.039207 | 0.173909 | 0.003489 | 0.115536 | 2539 | 22 |
| C01_pastagem | expo_milho_l1 | 0.056568 | 0.01002 | 0.103116 | 0.019587 | 0.587613 | 2539 | 22 |
| C01_pastagem | expo_milho_l2 | 0.034798 | -0.001594 | 0.07119 | 0.059943 | 1.0 | 2539 | 22 |
| C01_pastagem | expo_milho_l3 | -0.070221 | -0.134681 | -0.005762 | 0.034178 | 0.956985 | 2539 | 22 |
| C02_agricultura | expo_soja_l1 | 0.01212 | -0.014143 | 0.038382 | 0.348138 | 1.0 | 2539 | 22 |
| C02_agricultura | expo_soja_l2 | 0.001874 | -0.024589 | 0.028337 | 0.884342 | 1.0 | 2539 | 22 |
| C02_agricultura | expo_soja_l3 | 0.024526 | 0.011399 | 0.037654 | 0.000854 | 0.029887 | 2539 | 22 |
| C02_agricultura | expo_milho_l1 | 0.014667 | -0.01008 | 0.039414 | 0.231381 | 1.0 | 2539 | 22 |
| C02_agricultura | expo_milho_l2 | -0.010056 | -0.035325 | 0.015214 | 0.417233 | 1.0 | 2539 | 22 |
| C02_agricultura | expo_milho_l3 | 0.006489 | -0.017042 | 0.030019 | 0.572419 | 1.0 | 2539 | 22 |
| C02_pastagem | expo_soja_l1 | 0.01694 | -0.074678 | 0.108558 | 0.704463 | 1.0 | 2539 | 22 |
| C02_pastagem | expo_soja_l2 | 0.081869 | -0.134129 | 0.297867 | 0.439369 | 1.0 | 2539 | 22 |
| C02_pastagem | expo_soja_l3 | -0.088588 | -0.236653 | 0.059476 | 0.227117 | 1.0 | 2539 | 22 |
| C02_pastagem | expo_milho_l1 | 0.10787 | -0.050698 | 0.266438 | 0.171811 | 1.0 | 2539 | 22 |
| C02_pastagem | expo_milho_l2 | 0.067325 | -0.021685 | 0.156335 | 0.130673 | 1.0 | 2539 | 22 |
| C02_pastagem | expo_milho_l3 | -0.046467 | -0.132917 | 0.039984 | 0.276285 | 1.0 | 2539 | 22 |
| C03_agricultura | expo_soja_l1 | -0.00209 | -0.012944 | 0.008764 | 0.684196 | 1.0 | 1635 | 14 |
| C03_agricultura | expo_soja_l2 | -0.010904 | -0.027228 | 0.00542 | 0.172667 | 1.0 | 1635 | 14 |
| C03_agricultura | expo_soja_l3 | 0.018976 | 0.007017 | 0.030936 | 0.004495 | 0.14383 | 1635 | 14 |
| C03_agricultura | expo_milho_l1 | -0.001591 | -0.008241 | 0.005059 | 0.613847 | 1.0 | 1635 | 14 |
| C03_agricultura | expo_milho_l2 | 0.001824 | -0.005237 | 0.008885 | 0.586336 | 1.0 | 1635 | 14 |
| C03_agricultura | expo_milho_l3 | -0.007748 | -0.011183 | -0.004312 | 0.000305 | 0.010974 | 1635 | 14 |
| C03_pastagem | expo_soja_l1 | -0.043676 | -0.199625 | 0.112274 | 0.555568 | 1.0 | 1635 | 14 |
| C03_pastagem | expo_soja_l2 | 0.083905 | -0.037902 | 0.205712 | 0.160567 | 1.0 | 1635 | 14 |
| C03_pastagem | expo_soja_l3 | 0.084385 | 0.029681 | 0.139089 | 0.005399 | 0.167379 | 1635 | 14 |
| C03_pastagem | expo_milho_l1 | 0.048356 | -0.034239 | 0.130951 | 0.228146 | 1.0 | 1635 | 14 |
| C03_pastagem | expo_milho_l2 | 0.055261 | 0.021855 | 0.088666 | 0.003398 | 0.115536 | 1635 | 14 |
| C03_pastagem | expo_milho_l3 | -0.092213 | -0.174442 | -0.009985 | 0.030749 | 0.891714 | 1635 | 14 |
| N01_agricultura | expo_soja | 0.031109 | 0.005631 | 0.056586 | 0.018881 | 0.188814 | 2772 | 24 |
| N01_agricultura | expo_milho | 0.01574 | 1.7e-05 | 0.031463 | 0.04977 | 0.447932 | 2772 | 24 |
| N01_agricultura | quadrado_soja | -0.027258 | -0.0467 | -0.007816 | 0.008066 | 0.088729 | 2772 | 24 |
| N01_agricultura | quadrado_milho | -0.00629 | -0.014089 | 0.00151 | 0.108824 | 0.761766 | 2772 | 24 |
| N01_pastagem | expo_soja | 0.103203 | 0.040885 | 0.165522 | 0.002309 | 0.027711 | 2772 | 24 |
| N01_pastagem | expo_milho | 0.072858 | -0.001678 | 0.147394 | 0.054949 | 0.447932 | 2772 | 24 |
| N01_pastagem | quadrado_soja | -0.010199 | -0.071072 | 0.050674 | 0.732052 | 1.0 | 2772 | 24 |
| N01_pastagem | quadrado_milho | -0.012863 | -0.05965 | 0.033924 | 0.575043 | 1.0 | 2772 | 24 |
| Z01_agricultura | expo_soja | 0.040629 | -1.114995 | 1.196253 | 0.94265 | 1.0 | 2772 | 24 |
| Z01_agricultura | expo_milho | -0.119429 | -1.28123 | 1.042371 | 0.833472 | 1.0 | 2772 | 24 |
| Z02_agricultura | expo_soja | -0.018128 | -0.211442 | 0.175186 | 0.847889 | 1.0 | 2507 | 24 |
| Z02_agricultura | expo_milho | 0.069448 | -0.045859 | 0.184756 | 0.225335 | 1.0 | 2507 | 24 |

## Somas dinâmicas

| id | contraste | estimativa | ic95_inf | ic95_sup | p | p_holm |
| --- | --- | --- | --- | --- | --- | --- |
| C01_agricultura | Soma lags1–3 soja | 0.035126 | 0.000305 | 0.069947 | 0.0482 | 0.337397 |
| C01_agricultura | Soma lags1–3 milho | -0.005256 | -0.017305 | 0.006793 | 0.374598 | 1.0 |
| C01_pastagem | Soma lags1–3 soja | 0.163742 | 0.098486 | 0.228997 | 3.6e-05 | 0.00043 |
| C01_pastagem | Soma lags1–3 milho | 0.021144 | -0.030339 | 0.072628 | 0.402687 | 1.0 |
| C02_agricultura | Soma lags1–3 soja | 0.03852 | -0.00066 | 0.0777 | 0.053637 | 0.337397 |
| C02_agricultura | Soma lags1–3 milho | 0.0111 | -0.015561 | 0.03776 | 0.39637 | 1.0 |
| C02_pastagem | Soma lags1–3 soja | 0.010221 | -0.043571 | 0.064012 | 0.696724 | 1.0 |
| C02_pastagem | Soma lags1–3 milho | 0.128728 | 0.053267 | 0.20419 | 0.001906 | 0.019059 |
| C03_agricultura | Soma lags1–3 soja | 0.005982 | 0.001952 | 0.010013 | 0.006878 | 0.059649 |
| C03_agricultura | Soma lags1–3 milho | -0.007516 | -0.010463 | -0.004568 | 0.000101 | 0.001108 |
| C03_pastagem | Soma lags1–3 soja | 0.124614 | 0.041163 | 0.208065 | 0.006628 | 0.059649 |
| C03_pastagem | Soma lags1–3 milho | 0.011403 | -0.065747 | 0.088553 | 0.754562 | 1.0 |

## Testes conjuntos substantivos

| id | termos | F | p | p_holm |
| --- | --- | --- | --- | --- |
| C01_agricultura | expo_soja_l1;expo_soja_l2;expo_soja_l3;expo_milho_l1;expo_milho_l2;expo_milho_l3 | 14.633304 | 2e-06 | 3.1e-05 |
| C01_pastagem | expo_soja_l1;expo_soja_l2;expo_soja_l3;expo_milho_l1;expo_milho_l2;expo_milho_l3 | 27.970828 | 0.0 | 0.0 |
| C02_agricultura | expo_soja_l1;expo_soja_l2;expo_soja_l3;expo_milho_l1;expo_milho_l2;expo_milho_l3 | 3.397988 | 0.016775 | 0.205767 |
| C02_pastagem | expo_soja_l1;expo_soja_l2;expo_soja_l3;expo_milho_l1;expo_milho_l2;expo_milho_l3 | 6.728738 | 0.000438 | 0.006132 |
| C03_agricultura | expo_soja_l1;expo_soja_l2;expo_soja_l3;expo_milho_l1;expo_milho_l2;expo_milho_l3 | 24.715108 | 2e-06 | 4.1e-05 |
| C03_pastagem | expo_soja_l1;expo_soja_l2;expo_soja_l3;expo_milho_l1;expo_milho_l2;expo_milho_l3 | 129.08945 | 0.0 | 0.0 |
| E01_agricultura | expo_soja;expo_milho | 1.644235 | 0.215065 | 1.0 |
| E02_agricultura | expo_soja;expo_milho | 1.833556 | 0.182451 | 1.0 |
| E01_pastagem | expo_soja;expo_milho | 14.577886 | 8.1e-05 | 0.001303 |
| E02_pastagem | expo_soja;expo_milho | 14.564363 | 8.2e-05 | 0.001303 |
| E03_agricultura | expo_soja;expo_milho | 1.654831 | 0.213081 | 1.0 |
| E03_pastagem | expo_soja;expo_milho | 17.870742 | 2.1e-05 | 0.000353 |
| H00_agricultura | expo_soja;expo_milho | 1.662815 | 0.211599 | 1.0 |
| H00_pastagem | expo_soja;expo_milho | 19.097304 | 1.3e-05 | 0.000233 |
| H01_agricultura | expo_soja_amazonia;expo_milho_amazonia | 2.111621 | 0.1439 | 1.0 |
| H01_pastagem | expo_soja_amazonia;expo_milho_amazonia | 2.262277 | 0.126791 | 1.0 |
| H02_agricultura | expo_soja_amazonia;expo_milho_amazonia | 1.961777 | 0.163436 | 1.0 |
| H02_pastagem | expo_soja_amazonia;expo_milho_amazonia | 0.328914 | 0.723034 | 1.0 |
| N01_agricultura | quadrado_soja;quadrado_milho | 4.991835 | 0.015828 | 0.205767 |
| N01_pastagem | quadrado_soja;quadrado_milho | 0.645541 | 0.533619 | 1.0 |
| Z01_agricultura | expo_soja;expo_milho | 0.022646 | 0.97763 | 1.0 |
| Z02_agricultura | expo_soja;expo_milho | 0.794771 | 0.463703 | 1.0 |

## Reprodução

`python reproduzir.py` com requirements.txt em ambiente externo. COEFICIENTES.csv/MODELOS.csv/TESTES_CONJUNTOS.csv contêm tudo; RESUMO_INFLUENCIA.csv e auditoria_retiradas.csv permitem rastrear exclusões. MAGNITUDES.csv contém slopes, derivadas e contrastes; SENSIBILIDADE_CUMULATIVOS.csv usa a covariância completa das somas. Protocolos, hashes e validação registrados antes/depois; logs em 2_INTI/audit/testes4. Nenhum commit/push/publicação.

## Escopo da multiplicidade e da adaptação

Holm aplica-se somente às famílias registradas nesta rodada, com tamanho em n_familia nos CSVs. As rodadas foram adaptadas aos diagnósticos anteriores e reutilizam os mesmos dados: a correção por família/rodada não controla integralmente o erro da busca sequencial nem converte exploração em teste confirmatório. Uma confirmação independente exige protocolo externo/prévio e dados novos ou identificação adicional.
