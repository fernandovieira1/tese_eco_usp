# Resultados — rodada 2

19 ajustes concluídos. Amostra ampla: 2772 pares/137 municípios; fiscal: 1140/128. Para harmonização não linear, três municípios com uma única observação foram excluídos explicitamente: 2769 pares/134 municípios. Nenhum município tinha soma zero agrícola na amostra; todas as exclusões estão registradas. Modelos G00 na amostra harmonizada foram previstos condicionalmente e executados.

O núcleo amplo detecta associação positiva soja×aptidão na conversão para pastagem (0,1038 pp, IC95 [0,0385;0,1691], Holm 0,0128). Agricultura é imprecisa (0,0288 pp, IC inclui zero), não evidência de equivalência a zero. O teste direto da diferença pastagem−agricultura detecta diferenças positivas nas duas exposições sob a inferência principal; não compara significâncias separadas. Essa é evidência associativa sobre o destino imediato da conversão, não prova de que demanda por soja desloca pastagem: essa transição não é medida.

A restrição à amostra fiscal muda o coeficiente soja agrícola de 0,0288 para 0,0074 antes da inclusão de autos. Logo, parte da diferença da rodada1 decorre de composição observável; isso não identifica a causa da seleção. Adicionar autos na mesma amostra altera pouco esse coeficiente. Autuações não identificam efetividade institucional. Sob DK2, os IC dos autos e da interação preço×autos incluem zero; não se pode concluir inexistência do condicionamento institucional.

PPML com/sem offset e fracional com FE municipal/ano produzem objetos diferentes. Os coeficientes e testes conjuntos variam: isso é sensibilidade de escala/forma funcional, não uma votação entre modelos. Os testes individuais das alternativas não passam Holm da família de sensibilidades. Alguns testes conjuntos passam a correção; isso não valida exogeneidade. FE não linear com T curto continua sujeito a viés incidental, apesar de convergência, scores e predições finitas. O offset usa estoque endógeno e impõe sua elasticidade unitária.

A interpretação relevante seguinte é temporal: tendências de abertura de fronteira ou períodos específicos podem covariar com a aptidão. A rodada3 foi motivada por essa explicação alternativa e pela referência terras2010 do GAEZ, não pela busca de p menor. Não há limiar substantivo para teste de equivalência; intervalos amplos significam imprecisão. Todas as famílias e testes constam do protocolo anterior à execução.

## Todos os coeficientes substantivos

| id | termo | coef | se | ic95_inf | ic95_sup | p | p_holm | n_familia | N |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01_agricultura | expo_soja | 0.028791 | 0.016204 | -0.004729 | 0.062312 | 0.088833 | 0.177666 | 4 | 2772 |
| A01_agricultura | expo_milho | 0.003751 | 0.004968 | -0.006527 | 0.014028 | 0.45794 | 0.45794 | 4 | 2772 |
| A01_pastagem | expo_soja | 0.103806 | 0.031554 | 0.038532 | 0.16908 | 0.003208 | 0.012831 | 4 | 2772 |
| A01_pastagem | expo_milho | 0.058373 | 0.026811 | 0.00291 | 0.113836 | 0.039979 | 0.119937 | 4 | 2772 |
| A02_agricultura | expo_soja | 0.00743 | 0.00801 | -0.009181 | 0.024042 | 0.363673 | 1.0 | 38 | 1140 |
| A02_agricultura | expo_milho | 0.002915 | 0.003816 | -0.005 | 0.010829 | 0.453143 | 1.0 | 38 | 1140 |
| A02_pastagem | expo_soja | 0.068206 | 0.02985 | 0.006302 | 0.130111 | 0.032317 | 0.969521 | 38 | 1140 |
| A02_pastagem | expo_milho | 0.057444 | 0.019951 | 0.016069 | 0.09882 | 0.008709 | 0.28867 | 38 | 1140 |
| A03_agricultura | expo_soja | 0.007733 | 0.008455 | -0.009802 | 0.025268 | 0.370337 | 1.0 | 38 | 1140 |
| A03_agricultura | expo_milho | 0.002689 | 0.003667 | -0.004916 | 0.010293 | 0.471158 | 1.0 | 38 | 1140 |
| A03_agricultura | fiscal | 0.006249 | 0.003432 | -0.000868 | 0.013367 | 0.082264 | 1.0 | 38 | 1140 |
| A03_pastagem | expo_soja | 0.068627 | 0.030366 | 0.005652 | 0.131603 | 0.034063 | 0.987816 | 38 | 1140 |
| A03_pastagem | expo_milho | 0.05713 | 0.019765 | 0.016139 | 0.09812 | 0.00849 | 0.28867 | 38 | 1140 |
| A03_pastagem | fiscal | 0.008698 | 0.012602 | -0.017438 | 0.034834 | 0.49728 | 1.0 | 38 | 1140 |
| A04_agricultura | expo_soja | 0.009868 | 0.010948 | -0.012836 | 0.032573 | 0.37714 | 1.0 | 38 | 1140 |
| A04_agricultura | expo_milho | 0.00235 | 0.003416 | -0.004734 | 0.009434 | 0.498588 | 1.0 | 38 | 1140 |
| A04_agricultura | fiscal | 0.006181 | 0.003293 | -0.000649 | 0.01301 | 0.073861 | 1.0 | 38 | 1140 |
| A04_agricultura | preco_fiscal | 0.003484 | 0.004894 | -0.006666 | 0.013634 | 0.484042 | 1.0 | 38 | 1140 |
| A04_pastagem | expo_soja | 0.05192 | 0.037368 | -0.025575 | 0.129416 | 0.178599 | 1.0 | 38 | 1140 |
| A04_pastagem | expo_milho | 0.059775 | 0.018766 | 0.020857 | 0.098693 | 0.004278 | 0.149721 | 38 | 1140 |
| A04_pastagem | fiscal | 0.009237 | 0.011369 | -0.014341 | 0.032815 | 0.425247 | 1.0 | 38 | 1140 |
| A04_pastagem | preco_fiscal | -0.027253 | 0.015442 | -0.059278 | 0.004772 | 0.091467 | 1.0 | 38 | 1140 |
| A05_agricultura | x_rel_soja | 0.003201 | 0.010665 | -0.018861 | 0.025262 | 0.766771 | 1.0 | 38 | 2772 |
| A05_agricultura | x_rel_milho | -0.001557 | 0.005795 | -0.013545 | 0.010431 | 0.790586 | 1.0 | 38 | 2772 |
| A05_pastagem | x_rel_soja | 0.035003 | 0.036925 | -0.041381 | 0.111387 | 0.353002 | 1.0 | 38 | 2772 |
| A05_pastagem | x_rel_milho | 0.052945 | 0.02718 | -0.00328 | 0.109171 | 0.063723 | 1.0 | 38 | 2772 |
| D01_diferenca | expo_soja | 0.075015 | 0.026078 | 0.021068 | 0.128962 | 0.008524 | 0.017048 | 2 | 2772 |
| D01_diferenca | expo_milho | 0.054622 | 0.024107 | 0.004753 | 0.104491 | 0.033186 | 0.033186 | 2 | 2772 |
| F01_agricultura | expo_soja | 0.062133 | 0.061517 | -0.065124 | 0.18939 | 0.322993 | 1.0 | 38 | 2769 |
| F01_agricultura | expo_milho | 0.143223 | 0.055253 | 0.028924 | 0.257522 | 0.016294 | 0.505111 | 38 | 2769 |
| F01_pastagem | expo_soja | 0.06644 | 0.03035 | 0.003657 | 0.129224 | 0.038995 | 1.0 | 38 | 2769 |
| F01_pastagem | expo_milho | 0.078294 | 0.02961 | 0.017041 | 0.139547 | 0.014499 | 0.463958 | 38 | 2769 |
| G00_agricultura | expo_soja | 0.028791 | 0.016195 | -0.004711 | 0.062294 | 0.088671 | 1.0 | 38 | 2769 |
| G00_agricultura | expo_milho | 0.003751 | 0.004966 | -0.006521 | 0.014023 | 0.4577 | 1.0 | 38 | 2769 |
| G00_pastagem | expo_soja | 0.103806 | 0.031537 | 0.038567 | 0.169044 | 0.003194 | 0.114989 | 38 | 2769 |
| G00_pastagem | expo_milho | 0.058373 | 0.026796 | 0.00294 | 0.113806 | 0.039881 | 1.0 | 38 | 2769 |
| Q01_agricultura | expo_soja | 0.101756 | 0.05817 | -0.018578 | 0.22209 | 0.093577 | 1.0 | 38 | 2769 |
| Q01_agricultura | expo_milho | 0.218058 | 0.062277 | 0.089229 | 0.346887 | 0.001921 | 0.07301 | 38 | 2769 |
| Q01_pastagem | expo_soja | 0.039943 | 0.028896 | -0.019833 | 0.099719 | 0.180152 | 1.0 | 38 | 2769 |
| Q01_pastagem | expo_milho | 0.05279 | 0.024875 | 0.001331 | 0.104248 | 0.044807 | 1.0 | 38 | 2769 |
| Q02_agricultura | expo_soja | 0.085263 | 0.057601 | -0.033893 | 0.204419 | 0.152375 | 1.0 | 38 | 2769 |
| Q02_agricultura | expo_milho | 0.217186 | 0.062083 | 0.088758 | 0.345614 | 0.001936 | 0.07301 | 38 | 2769 |
| Q02_pastagem | expo_soja | 0.036814 | 0.029762 | -0.024753 | 0.098381 | 0.228586 | 1.0 | 38 | 2769 |
| Q02_pastagem | expo_milho | 0.049314 | 0.023778 | 0.000124 | 0.098503 | 0.04947 | 1.0 | 38 | 2769 |

## Testes conjuntos

| id | termos | F | p | p_holm |
| --- | --- | --- | --- | --- |
| A01_agricultura | expo_soja;expo_milho | 1.644235 | 0.215065 | 1.0 |
| A01_pastagem | expo_soja;expo_milho | 14.577886 | 8.1e-05 | 0.001286 |
| A02_agricultura | expo_soja;expo_milho | 0.570463 | 0.573405 | 1.0 |
| A02_pastagem | expo_soja;expo_milho | 5.726478 | 0.009951 | 0.109462 |
| A03_agricultura | expo_soja;expo_milho | 0.535386 | 0.592879 | 1.0 |
| A03_pastagem | expo_soja;expo_milho | 5.632803 | 0.010585 | 0.109462 |
| A04_agricultura | expo_soja;expo_milho | 0.494142 | 0.616705 | 1.0 |
| A04_pastagem | expo_soja;expo_milho | 5.267244 | 0.013517 | 0.121649 |
| A05_agricultura | x_rel_soja;x_rel_milho | 0.066455 | 0.935884 | 1.0 |
| A05_pastagem | x_rel_soja;x_rel_milho | 3.749303 | 0.038963 | 0.311702 |
| D01_diferenca | expo_soja;expo_milho | 19.191015 | 1.3e-05 | 0.000225 |
| F01_agricultura | expo_soja;expo_milho | 3.635045 | 0.042483 | 0.311702 |
| F01_pastagem | expo_soja;expo_milho | 21.821133 | 5e-06 | 9.2e-05 |
| G00_agricultura | expo_soja;expo_milho | 1.646016 | 0.21473 | 1.0 |
| G00_pastagem | expo_soja;expo_milho | 14.59368 | 8.1e-05 | 0.001286 |
| Q01_agricultura | expo_soja;expo_milho | 14.607439 | 8e-05 | 0.001286 |
| Q01_pastagem | expo_soja;expo_milho | 11.496068 | 0.000346 | 0.004497 |
| Q02_agricultura | expo_soja;expo_milho | 15.906778 | 4.6e-05 | 0.000782 |
| Q02_pastagem | expo_soja;expo_milho | 10.429219 | 0.000597 | 0.007169 |

## Magnitudes predefinidas

Cenários de +10% do preço médio, não margens de equivalência. No linear: contraste P75−P25 de aptidão em pp. No GLM: mudança média prevista via componente diferencial, mantendo FEano, sem identificar resposta comum ao choque.

| id | contraste | estimativa | ic95_inf | ic95_sup | unidade |
| --- | --- | --- | --- | --- | --- |
| A01_agricultura | P75-P25 aptidão; +10% preço médio soja | 0.021696 | -0.003564 | 0.046956 | pp |
| A01_agricultura | P75-P25 aptidão; +10% preço médio milho | 0.000965 | -0.00168 | 0.00361 | pp |
| A01_pastagem | P75-P25 aptidão; +10% preço médio soja | 0.078224 | 0.029036 | 0.127412 | pp |
| A01_pastagem | P75-P25 aptidão; +10% preço médio milho | 0.015023 | 0.000749 | 0.029297 | pp |
| A02_agricultura | P75-P25 aptidão; +10% preço médio soja | 0.005599 | -0.006919 | 0.018117 | pp |
| A02_agricultura | P75-P25 aptidão; +10% preço médio milho | 0.00075 | -0.001287 | 0.002787 | pp |
| A02_pastagem | P75-P25 aptidão; +10% preço médio soja | 0.051398 | 0.004749 | 0.098047 | pp |
| A02_pastagem | P75-P25 aptidão; +10% preço médio milho | 0.014784 | 0.004136 | 0.025433 | pp |
| A03_agricultura | P75-P25 aptidão; +10% preço médio soja | 0.005827 | -0.007386 | 0.019041 | pp |
| A03_agricultura | P75-P25 aptidão; +10% preço médio milho | 0.000692 | -0.001265 | 0.002649 | pp |
| A03_pastagem | P75-P25 aptidão; +10% preço médio soja | 0.051715 | 0.004259 | 0.099172 | pp |
| A03_pastagem | P75-P25 aptidão; +10% preço médio milho | 0.014703 | 0.004154 | 0.025253 | pp |
| A04_agricultura | P75-P25 aptidão; +10% preço médio soja | 0.007437 | -0.009673 | 0.024546 | pp |
| A04_agricultura | P75-P25 aptidão; +10% preço médio milho | 0.000605 | -0.001218 | 0.002428 | pp |
| A04_pastagem | P75-P25 aptidão; +10% preço médio soja | 0.039125 | -0.019272 | 0.097523 | pp |
| A04_pastagem | P75-P25 aptidão; +10% preço médio milho | 0.015384 | 0.005368 | 0.0254 | pp |
| D01_diferenca | P75-P25 aptidão; +10% preço médio soja | 0.056528 | 0.015876 | 0.097181 | pp |
| D01_diferenca | P75-P25 aptidão; +10% preço médio milho | 0.014058 | 0.001223 | 0.026892 | pp |
| G00_agricultura | P75-P25 aptidão; +10% preço médio soja | 0.021696 | -0.00355 | 0.046942 | pp |
| G00_agricultura | P75-P25 aptidão; +10% preço médio milho | 0.000965 | -0.001678 | 0.003609 | pp |
| G00_pastagem | P75-P25 aptidão; +10% preço médio soja | 0.078224 | 0.029063 | 0.127386 | pp |
| G00_pastagem | P75-P25 aptidão; +10% preço médio milho | 0.015023 | 0.000757 | 0.029289 | pp |
| Q01_agricultura | +10% preço médio soja; só componente diferencial | -7.068727 | -15.282281 | 1.144828 | ha |
| Q01_agricultura | +10% preço médio milho; só componente diferencial | -9.05832 | -14.577126 | -3.539513 | ha |
| Q01_pastagem | +10% preço médio soja; só componente diferencial | -18.023718 | -42.429849 | 6.382413 | ha |
| Q01_pastagem | +10% preço médio milho; só componente diferencial | -7.851527 | -16.705741 | 1.002686 | ha |
| Q02_agricultura | +10% preço médio soja; só componente diferencial | -5.953517 | -14.095298 | 2.188263 | ha |
| Q02_agricultura | +10% preço médio milho; só componente diferencial | -9.023115 | -14.507648 | -3.538582 | ha |
| Q02_pastagem | +10% preço médio soja; só componente diferencial | -16.661163 | -42.088147 | 8.765822 | ha |
| Q02_pastagem | +10% preço médio milho; só componente diferencial | -7.365017 | -15.812124 | 1.082089 | ha |
| F01_agricultura | +10% preço médio soja; só componente diferencial | -1.3e-05 | -3.9e-05 | 1.3e-05 | fração |
| F01_agricultura | +10% preço médio milho; só componente diferencial | -2.2e-05 | -4e-05 | -3e-06 | fração |
| F01_pastagem | +10% preço médio soja; só componente diferencial | 1.6e-05 | -2e-05 | 5.2e-05 | fração |
| F01_pastagem | +10% preço médio milho; só componente diferencial | -1.5e-05 | -3.2e-05 | 3e-06 | fração |

## Reprodução e limitações

Instalar requirements.txt em ambiente virtual externo e executar `python executar.py` neste diretório. Os notebooks são executados em kernels novos. Auditoria independente conferiu coeficientes e covariância linear DK2 contra PanelOLS. FE removidos por projeção iterativa, não double-demean simples. METADADOS.json registra protocolo, origem, hash dos dados e arquivos protegidos; VALIDACAO.json confirma preservação. Logs em ../../../../../audit/testes2 (caminho canônico na raiz: 2_INTI/audit/testes2). Não houve publicação.

## Escopo da multiplicidade e da adaptação

Holm aplica-se somente às famílias registradas nesta rodada, com tamanho em n_familia nos CSVs. As rodadas foram adaptadas aos diagnósticos anteriores e reutilizam os mesmos dados: a correção por família/rodada não controla integralmente o erro da busca sequencial nem converte exploração em teste confirmatório. Uma confirmação independente exige protocolo externo/prévio e dados novos ou identificação adicional.
