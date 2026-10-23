# Resultados — rodada 6

16 modelos executados em quatro notebooks. Todas as estimações são associações condicionais; bioma não é uma intervenção. Preço comum anual é absorvido pelas FE ano, atributos/bioma pelas FE municipais: os coeficientes identificam gradientes diferenciais. O preço em log já está defasado um ano. Uma unidade de x corresponde a uma unidade de log-preço × 1 DP de aptidão. VD em pontos percentuais da conversão por estoque nativo inicial.

Não há conversão nativa→soja/milho/algodão nos dados. Os resultados abaixo sobre soja e milho referem-se a incentivos dessas culturas associados à conversão agrícola agregada ou à pastagem, não ao destino específico da cultura. Não há variáveis de algodão nos dois schemas consultados. Área plantada não foi usada como substituta de conversão. Não se demonstra deslocamento ou mecanismo direto/indireto.

Pantanal: 4 municípios na grade, somente 3 com conversão válida e 54 linhas. Há 13 com alguma fração Pantanal, 8 acima de 5% e 7 acima de 10%; nenhuma regressão separada foi fabricada. Os modelos territoriais excluem qualquer fração Pantanal >1e−6, usando a mesma amostra e ambos os destinos observados. C61/C62 permitem examinar composição. Exclusão limita validade externa, não prova que Pantanal não importa.

Interfaces são municípios de composição mista, não ecótonos ecológicos. O JSON de referência contém somente código/nome; não foram encontrados arquivos .gpkg/.shp/.geojson na árvore ativa examinada. O painel não localiza as conversões em biomas ou faixas de transição. Frações originais preservadas: erro máximo de soma 0,001255. Não rateamos fluxos, não inferimos localização por predominância e não normalizamos frações silenciosamente.

## Inferência e multiplicidade
Principal DK Bartlett lag2, t(23) quando todos os 24 anos presentes; sensibilidades DK1, DK3, municipal e two-way bruto. Matrizes brutas não PSD não foram corrigidas; SE indefinidos são registrados. Mesmo 100+ municípios não criam mais choques anuais. IC95 pontuais, não simultâneos. Holm: coeficientes culturas8/biomas32/interfaces36; testes conjuntos16; contrastes formais52; magnitudes32 (reexpressões, não replicações). Correções destas famílias NÃO controlam integralmente busca adaptativa entre rodadas. As sensibilidades não autorizam escolher o menor p. O bootstrap da rodada5 revelou sensibilidade ao bloco e resolução discreta; não foi rebatizado como validação desta expansão.

## Suporte efetivo

| amostra | grupo | N | municipios | informativos | anos | ano_min | ano_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sem_Pantanal | Amazônia | 1301 | 70 | 70 | 24 | 2001 | 2024 |
| sem_Pantanal | Cerrado | 1322 | 56 | 56 | 24 | 2001 | 2024 |
| sem_Pantanal | misto_1e-06_False | 1634 | 77 | 77 | 24 | 2001 | 2024 |
| sem_Pantanal | misto_1e-06_True | 989 | 49 | 49 | 24 | 2001 | 2024 |
| sem_Pantanal | misto_0.05_False | 1888 | 90 | 90 | 24 | 2001 | 2024 |
| sem_Pantanal | misto_0.05_True | 735 | 36 | 36 | 24 | 2001 | 2024 |
| sem_Pantanal | misto_0.1_False | 1983 | 96 | 96 | 24 | 2001 | 2024 |
| sem_Pantanal | misto_0.1_True | 640 | 30 | 30 | 24 | 2001 | 2024 |

## Ajustes e perdas

| id | N | municipios | anos | perdas_grade | condicao | ajuste |
| --- | --- | --- | --- | --- | --- | --- |
| I61_agricultura | 2623 | 126 | 24 | 761 | 10.563 | 0.030456 |
| I61_pastagem | 2623 | 126 | 24 | 761 | 10.563 | 0.022692 |
| I62_agricultura | 2623 | 126 | 24 | 761 | 11.091 | 0.024871 |
| I62_pastagem | 2623 | 126 | 24 | 761 | 11.091 | 0.021752 |
| I63_agricultura | 2623 | 126 | 24 | 761 | 11.542 | 0.014614 |
| I63_pastagem | 2623 | 126 | 24 | 761 | 11.542 | 0.023254 |
| C61_agricultura | 2772 | 137 | 24 | 612 | 1.8965 | 0.013114 |
| C61_pastagem | 2772 | 137 | 24 | 612 | 1.8965 | 0.01716 |
| C62_agricultura | 2623 | 126 | 24 | 761 | 2.1079 | 0.012851 |
| C62_pastagem | 2623 | 126 | 24 | 761 | 2.1079 | 0.018847 |
| B61_agricultura | 2623 | 126 | 24 | 761 | 12.969 | 0.022062 |
| B61_pastagem | 2623 | 126 | 24 | 761 | 12.969 | 0.033386 |
| B62_agricultura | 2623 | 126 | 24 | 761 | 8.2075 | 0.017278 |
| B62_pastagem | 2623 | 126 | 24 | 761 | 8.2075 | 0.010502 |
| B63_agricultura | 2623 | 126 | 24 | 761 | 14.067 | 0.022704 |
| B63_pastagem | 2623 | 126 | 24 | 761 | 14.067 | 0.035673 |

## Gradientes de referência: todos, inclusive imprecisos

| id | termo | coef | se | ic95_inf | ic95_sup | p | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B61_agricultura | x_soja | 0.10309 | 0.041123 | 0.018017 | 0.18816 | 0.019697 | 0.55152 |
| B61_agricultura | x_milho | 0.090326 | 0.048424 | -0.0098469 | 0.1905 | 0.074946 | 1 |
| B61_pastagem | x_soja | -0.07343 | 0.068033 | -0.21417 | 0.067306 | 0.29163 | 1 |
| B61_pastagem | x_milho | 0.45614 | 0.10831 | 0.23207 | 0.6802 | 0.00033257 | 0.010109 |
| B62_agricultura | x_soja | 0.10369 | 0.041079 | 0.018715 | 0.18867 | 0.018951 | 0.54959 |
| B62_agricultura | x_milho | 0.090374 | 0.048558 | -0.010076 | 0.19082 | 0.075553 | 1 |
| B62_pastagem | x_soja | -0.07555 | 0.070054 | -0.22047 | 0.069368 | 0.29202 | 1 |
| B62_pastagem | x_milho | 0.45654 | 0.10821 | 0.2327 | 0.68039 | 0.0003261 | 0.010109 |
| B63_agricultura | x_soja | 0.073401 | 0.029337 | 0.012713 | 0.13409 | 0.019906 | 0.55152 |
| B63_agricultura | x_milho | 0.11503 | 0.057088 | -0.0030654 | 0.23312 | 0.055743 | 1 |
| B63_pastagem | x_soja | -0.16173 | 0.094959 | -0.35816 | 0.034709 | 0.10202 | 1 |
| B63_pastagem | x_milho | 0.44173 | 0.092193 | 0.25101 | 0.63244 | 7.832e-05 | 0.0025062 |
| C61_agricultura | x_soja | 0.12928 | 0.065636 | -0.0065022 | 0.26506 | 0.061045 | 0.25893 |
| C61_agricultura | x_milho | 0.019008 | 0.018211 | -0.018664 | 0.05668 | 0.30743 | 0.43301 |
| C61_pastagem | x_soja | 0.42659 | 0.12297 | 0.17219 | 0.68098 | 0.0020798 | 0.016639 |
| C61_pastagem | x_milho | 0.22081 | 0.093403 | 0.027588 | 0.41403 | 0.026899 | 0.1883 |
| C62_agricultura | x_soja | 0.12438 | 0.06424 | -0.0085092 | 0.25727 | 0.065227 | 0.25893 |
| C62_agricultura | x_milho | 0.035951 | 0.02829 | -0.022571 | 0.094474 | 0.2165 | 0.43301 |
| C62_pastagem | x_soja | 0.35103 | 0.15613 | 0.028056 | 0.67401 | 0.034435 | 0.20661 |
| C62_pastagem | x_milho | 0.44762 | 0.21821 | -0.0037682 | 0.89902 | 0.051787 | 0.25893 |
| I61_agricultura | x_soja | 0.027031 | 0.027942 | -0.030772 | 0.084834 | 0.34341 | 1 |
| I61_agricultura | x_milho | 0.072954 | 0.036719 | -0.0030046 | 0.14891 | 0.05898 | 1 |
| I61_pastagem | x_soja | 0.35022 | 0.20974 | -0.08366 | 0.7841 | 0.10852 | 1 |
| I61_pastagem | x_milho | 0.67178 | 0.22234 | 0.21184 | 1.1317 | 0.0060763 | 0.2066 |
| I62_agricultura | x_soja | 0.05971 | 0.037971 | -0.018839 | 0.13826 | 0.12949 | 1 |
| I62_agricultura | x_milho | 0.05986 | 0.032819 | -0.0080308 | 0.12775 | 0.08118 | 1 |
| I62_pastagem | x_soja | 0.34273 | 0.19672 | -0.06423 | 0.74968 | 0.094839 | 1 |
| I62_pastagem | x_milho | 0.60954 | 0.25456 | 0.082947 | 1.1361 | 0.025183 | 0.78068 |
| I63_agricultura | x_soja | 0.1099 | 0.059022 | -0.012192 | 0.232 | 0.075417 | 1 |
| I63_agricultura | x_milho | 0.043318 | 0.027631 | -0.013841 | 0.10048 | 0.1306 | 1 |
| I63_pastagem | x_soja | 0.35096 | 0.18615 | -0.034121 | 0.73603 | 0.072077 | 1 |
| I63_pastagem | x_milho | 0.62033 | 0.26135 | 0.079682 | 1.161 | 0.026352 | 0.78851 |

## Testes conjuntos das interações territoriais

| id | termos | F | p | p_holm |
| --- | --- | --- | --- | --- |
| B61_agricultura | xh_soja;xh_milho | 2.7116 | 0.087627 | 0.61339 |
| B61_pastagem | xh_soja;xh_milho | 0.32742 | 0.72408 | 1 |
| B62_agricultura | xh_soja;xh_milho | 2.6909 | 0.089106 | 0.61339 |
| B62_pastagem | xh_soja;xh_milho | 0.27646 | 0.76095 | 1 |
| B63_agricultura | xh_soja;xh_milho | 3.0757 | 0.065508 | 0.52406 |
| B63_pastagem | xh_soja;xh_milho | 0.39323 | 0.67932 | 1 |
| I61_agricultura | xh_soja;xh_milho | 3.7944 | 0.037662 | 0.33896 |
| I61_pastagem | xh_soja;xh_milho | 29.393 | 4.6134e-07 | 7.3815e-06 |
| I62_agricultura | xh_soja;xh_milho | 3.9379 | 0.033827 | 0.33827 |
| I62_pastagem | xh_soja;xh_milho | 18.02 | 1.9573e-05 | 0.00027403 |
| I63_agricultura | xh_soja;xh_milho | 4.8921 | 0.016972 | 0.18669 |
| I63_pastagem | xh_soja;xh_milho | 17.749 | 2.1763e-05 | 0.00028292 |
| C61_agricultura | x_soja;x_milho | 2.0672 | 0.14941 | 0.69327 |
| C61_pastagem | x_soja;x_milho | 15.129 | 6.4047e-05 | 0.00076856 |
| C62_agricultura | x_soja;x_milho | 2.1557 | 0.13865 | 0.69327 |
| C62_pastagem | x_soja;x_milho | 19.525 | 1.1051e-05 | 0.00016577 |

## Comparações formais soja−milho e incrementos territoriais

| id | contraste | estimativa | se | ic95_inf | ic95_sup | p | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I61_agricultura | Soja menos milho; gradiente base | -0.045923 | 0.035581 | -0.11953 | 0.027683 | 0.20965 | 1 |
| I61_agricultura | Incremento territorial soja | 0.51879 | 0.21128 | 0.081713 | 0.95586 | 0.022053 | 0.97035 |
| I61_agricultura | Incremento territorial milho | -0.3017 | 0.14282 | -0.59714 | -0.0062539 | 0.045714 | 1 |
| I61_agricultura | Diferença dos incrementos soja menos milho | 0.82048 | 0.35192 | 0.092478 | 1.5485 | 0.028853 | 1 |
| I61_pastagem | Soja menos milho; gradiente base | -0.32156 | 0.40701 | -1.1635 | 0.5204 | 0.43756 | 1 |
| I61_pastagem | Incremento territorial soja | 0.3068 | 0.46933 | -0.66408 | 1.2777 | 0.51979 | 1 |
| I61_pastagem | Incremento territorial milho | -0.85481 | 0.25817 | -1.3889 | -0.32074 | 0.0030484 | 0.14937 |
| I61_pastagem | Diferença dos incrementos soja menos milho | 1.1616 | 0.71668 | -0.32095 | 2.6442 | 0.11869 | 1 |
| I62_agricultura | Soja menos milho; gradiente base | -0.00015069 | 0.034652 | -0.071834 | 0.071532 | 0.99657 | 1 |
| I62_agricultura | Incremento territorial soja | 0.45959 | 0.20285 | 0.039974 | 0.87921 | 0.033193 | 1 |
| I62_agricultura | Incremento territorial milho | -0.25532 | 0.13814 | -0.54109 | 0.030453 | 0.077471 | 1 |
| I62_agricultura | Diferença dos incrementos soja menos milho | 0.71491 | 0.33899 | 0.013657 | 1.4162 | 0.046044 | 1 |
| I62_pastagem | Soja menos milho; gradiente base | -0.26681 | 0.42925 | -1.1548 | 0.62116 | 0.54033 | 1 |
| I62_pastagem | Incremento territorial soja | 0.2708 | 0.36888 | -0.49228 | 1.0339 | 0.47029 | 1 |
| I62_pastagem | Incremento territorial milho | -0.72246 | 0.25358 | -1.247 | -0.1979 | 0.0090825 | 0.42688 |
| I62_pastagem | Diferença dos incrementos soja menos milho | 0.99326 | 0.6121 | -0.27296 | 2.2595 | 0.11828 | 1 |
| I63_agricultura | Soja menos milho; gradiente base | 0.066587 | 0.052411 | -0.041834 | 0.17501 | 0.21662 | 1 |
| I63_agricultura | Incremento territorial soja | 0.19049 | 0.080215 | 0.024554 | 0.35643 | 0.026284 | 1 |
| I63_agricultura | Incremento territorial milho | -0.12851 | 0.077053 | -0.28791 | 0.030883 | 0.1089 | 1 |
| I63_agricultura | Diferença dos incrementos soja menos milho | 0.319 | 0.15551 | -0.0026849 | 0.64069 | 0.051786 | 1 |
| I63_pastagem | Soja menos milho; gradiente base | -0.26937 | 0.42401 | -1.1465 | 0.60776 | 0.5315 | 1 |
| I63_pastagem | Incremento territorial soja | 0.27968 | 0.30876 | -0.35904 | 0.9184 | 0.37443 | 1 |
| I63_pastagem | Incremento territorial milho | -0.79286 | 0.24609 | -1.3019 | -0.28378 | 0.0037763 | 0.18126 |
| I63_pastagem | Diferença dos incrementos soja menos milho | 1.0725 | 0.54289 | -0.050521 | 2.1956 | 0.060318 | 1 |
| C61_agricultura | Soja menos milho; gradiente base | 0.11027 | 0.062934 | -0.019921 | 0.24046 | 0.093076 | 1 |
| C61_pastagem | Soja menos milho; gradiente base | 0.20578 | 0.18363 | -0.17408 | 0.58564 | 0.27401 | 1 |
| C62_agricultura | Soja menos milho; gradiente base | 0.088431 | 0.062378 | -0.040608 | 0.21747 | 0.1697 | 1 |
| C62_pastagem | Soja menos milho; gradiente base | -0.096592 | 0.35212 | -0.82502 | 0.63183 | 0.78629 | 1 |
| B61_agricultura | Soja menos milho; gradiente base | 0.012761 | 0.041997 | -0.074117 | 0.099639 | 0.76397 | 1 |
| B61_agricultura | Incremento territorial soja | 0.37442 | 0.16591 | 0.031204 | 0.71764 | 0.033831 | 1 |
| B61_agricultura | Incremento territorial milho | -0.67827 | 0.29133 | -1.2809 | -0.075617 | 0.029053 | 1 |
| B61_agricultura | Diferença dos incrementos soja menos milho | 1.0527 | 0.45451 | 0.11248 | 1.9929 | 0.029814 | 1 |
| B61_pastagem | Soja menos milho; gradiente base | -0.52957 | 0.13714 | -0.81326 | -0.24587 | 0.0007929 | 0.040438 |
| B61_pastagem | Incremento territorial soja | -0.35253 | 0.44615 | -1.2755 | 0.57041 | 0.43751 | 1 |
| B61_pastagem | Incremento territorial milho | 1.1438 | 1.4527 | -1.8614 | 4.149 | 0.43911 | 1 |
| B61_pastagem | Diferença dos incrementos soja menos milho | -1.4964 | 1.8645 | -5.3534 | 2.3607 | 0.43045 | 1 |
| B62_agricultura | Soja menos milho; gradiente base | 0.013319 | 0.041881 | -0.073318 | 0.099955 | 0.75334 | 1 |
| B62_agricultura | Incremento territorial soja | 0.37476 | 0.1667 | 0.029922 | 0.71961 | 0.03445 | 1 |
| B62_agricultura | Incremento territorial milho | -0.68545 | 0.29553 | -1.2968 | -0.074108 | 0.029605 | 1 |
| B62_agricultura | Diferença dos incrementos soja menos milho | 1.0602 | 0.45942 | 0.10983 | 2.0106 | 0.030355 | 1 |
| B62_pastagem | Soja menos milho; gradiente base | -0.53209 | 0.13923 | -0.82011 | -0.24408 | 0.00087495 | 0.043748 |
| B62_pastagem | Incremento territorial soja | -0.28092 | 0.41589 | -1.1413 | 0.57941 | 0.50611 | 1 |
| B62_pastagem | Incremento territorial milho | 1.0366 | 1.3967 | -1.8527 | 3.926 | 0.46548 | 1 |
| B62_pastagem | Diferença dos incrementos soja menos milho | -1.3176 | 1.7741 | -4.9877 | 2.3525 | 0.46521 | 1 |
| B63_agricultura | Soja menos milho; gradiente base | -0.041628 | 0.047846 | -0.1406 | 0.057348 | 0.39326 | 1 |
| B63_agricultura | Incremento territorial soja | 0.41593 | 0.16973 | 0.064822 | 0.76703 | 0.022287 | 0.97035 |
| B63_agricultura | Incremento territorial milho | -0.72169 | 0.29164 | -1.325 | -0.11838 | 0.021146 | 0.96126 |
| B63_agricultura | Diferença dos incrementos soja menos milho | 1.1376 | 0.45873 | 0.18867 | 2.0866 | 0.020897 | 0.96126 |
| B63_pastagem | Soja menos milho; gradiente base | -0.60345 | 0.12572 | -0.86352 | -0.34338 | 7.6647e-05 | 0.0039856 |
| B63_pastagem | Incremento territorial soja | -0.37917 | 0.44793 | -1.3058 | 0.54746 | 0.40601 | 1 |
| B63_pastagem | Incremento territorial milho | 1.3675 | 1.5644 | -1.8688 | 4.6038 | 0.39109 | 1 |
| B63_pastagem | Diferença dos incrementos soja menos milho | -1.7467 | 1.9739 | -5.83 | 2.3366 | 0.38537 | 1 |

Após Holm na família de 52 contrastes formais: 3 rejeições a 5%. Isso não equivale a aceitar os demais nulos, tampouco identifica causalidade. Os intervalos mostram a precisão disponível. Não se compara significância de duas culturas como teste da diferença.

## Magnitudes de +10% preço com aptidão P75−P25

| id | contraste | estimativa | ic95_inf | ic95_sup |
| --- | --- | --- | --- | --- |
| I61_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.0045782 | -0.0052118 | 0.014368 |
| I61_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.0053958 | -0.00022223 | 0.011014 |
| I61_pastagem | +10% preço soja; aptidão P75−P25; grupo base | 0.059315 | -0.014169 | 0.1328 |
| I61_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.049687 | 0.015668 | 0.083705 |
| I62_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.010113 | -0.0031907 | 0.023416 |
| I62_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.0044274 | -0.00059398 | 0.0094488 |
| I62_pastagem | +10% preço soja; aptidão P75−P25; grupo base | 0.058046 | -0.010878 | 0.12697 |
| I62_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.045083 | 0.006135 | 0.084031 |
| I63_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.018614 | -0.002065 | 0.039293 |
| I63_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.0032039 | -0.0010237 | 0.0074314 |
| I63_pastagem | +10% preço soja; aptidão P75−P25; grupo base | 0.05944 | -0.005779 | 0.12466 |
| I63_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.045881 | 0.0058935 | 0.085869 |
| C61_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.021895 | -0.0011013 | 0.044892 |
| C61_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.0014059 | -0.0013804 | 0.0041922 |
| C61_pastagem | +10% preço soja; aptidão P75−P25; grupo base | 0.072249 | 0.029164 | 0.11534 |
| C61_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.016331 | 0.0020405 | 0.030622 |
| C62_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.021066 | -0.0014412 | 0.043574 |
| C62_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.002659 | -0.0016694 | 0.0069875 |
| C62_pastagem | +10% preço soja; aptidão P75−P25; grupo base | 0.059453 | 0.0047518 | 0.11415 |
| C62_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.033107 | -0.0002787 | 0.066493 |
| B61_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.01746 | 0.0030515 | 0.031868 |
| B61_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.0066807 | -0.0007283 | 0.01409 |
| B61_pastagem | +10% preço soja; aptidão P75−P25; grupo base | -0.012437 | -0.036273 | 0.011399 |
| B61_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.033737 | 0.017165 | 0.050309 |
| B62_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.017562 | 0.0031697 | 0.031955 |
| B62_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.0066843 | -0.00074525 | 0.014114 |
| B62_pastagem | +10% preço soja; aptidão P75−P25; grupo base | -0.012796 | -0.03734 | 0.011749 |
| B62_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.033767 | 0.017211 | 0.050323 |
| B63_agricultura | +10% preço soja; aptidão P75−P25; grupo base | 0.012432 | 0.0021531 | 0.02271 |
| B63_agricultura | +10% preço milho; aptidão P75−P25; grupo base | 0.0085078 | -0.00022673 | 0.017242 |
| B63_pastagem | +10% preço soja; aptidão P75−P25; grupo base | -0.027391 | -0.060661 | 0.0058785 |
| B63_pastagem | +10% preço milho; aptidão P75−P25; grupo base | 0.032671 | 0.018565 | 0.046777 |

## Decisão científica e próximos dados

H1 não pode ser aceita/rejeitada em bloco por estes testes. Há dimensões associativas mensuráveis e dimensões não identificadas: efetividade institucional, destinação específica de culturas, algodão, causalidade e ecótono localizado. Resultados territoriais distinguem composição e sensibilidade às FE, mas não removem custos omitidos, seleção de aptidão baseada em terras2010 ou estoque endógeno. Falta de rejeição não demonstra homogeneidade/equivalência.

Encerrada esta grade finita. As rodadas2–5 já investigaram composição fiscal, dinâmica, tendências, choques bioma×ano, não linearidades, zeros, denominadores, influência e inferência temporal. Esta ampliação investiga uma questão territorial distinta; novas variantes escolhidas pelo p não resolveriam as lacunas. Para discriminar os mecanismos restantes são necessários mapas de transições por cultura/ano, geometrias e definição externa de faixa ecotonal, incentivos/aptidão de algodão, mais suporte Pantanal e medida/desenho institucional exógeno. Preservadas as conclusões das rodadas anteriores. Publicação permanece pendente.

## Leitura substantiva dos resultados e continuidade

Preços log soja/milho correlacionam 0,9476; aptidões 0,5907. A inclusão conjunta tem posto completo, mas não torna os incentivos economicamente independentes. C61 ampla: diferença dos gradientes soja−milho na agricultura 0,1103 (IC95 −0,0199 a 0,2405); pastagem 0,2058 (−0,1741 a 0,5856), ambas imprecisas.

No grupo base Cerrado da amostra sem Pantanal, a diferença soja−milho para pastagem é −0,5296 em B61 (IC95 −0,8133 a −0,2459; Holm52 0,0404), −0,5321 em B62 (Holm52 0,0437) e −0,6035 em B63 no extremo fração Amazônia=0 (Holm52 0,0040). Trata-se de comparação de gradientes padronizados, não de conversão específica por cultura. Os testes conjuntos de diferenças Amazônia–Cerrado são imprecisos (Holm16 ≥0,524); isso não estabelece homogeneidade.

Interfaces/pastagem: testes conjuntos das duas interações rejeitam com DK2 nas três definições (Holm16 0,0000074; 0,000274; 0,000283). Para I61, incremento soja=0,3068 (IC95 −0,6641 a 1,2777), milho=−0,8548 (−1,3889 a −0,3207). A covariância entre os termos importa: forte teste conjunto não significa ambos individualmente precisos. Com cluster municipal, Holm16=0,108/0,148/0,065; two-way bruto=0,096/0,217/0,178. Portanto não é evidência robusta à inferência. CONJUNTOS_SENSIBILIDADE.csv contém todos, inclusive matrizes inadequadas; não houve PSD.

Próxima rodada7 motivada por este diagnóstico: verificar interfaces com FE bioma×ano e tendências municipais, com grade fixada antes dos novos resultados. É exploração adaptativa explícita, não procura de p baixo nem confirmação independente. Sem nova mensuração, não identifica ecótono ecológico ou causalidade.
