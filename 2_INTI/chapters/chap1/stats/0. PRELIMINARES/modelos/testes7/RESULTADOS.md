# Rodada7 — Resultados integrais de sensibilidade das interfaces

12 modelos executados em dois notebooks; mesma amostra 2623 linhas,126 municípios,24 anos. Referências preservadas na rodada6, sem duplicar contagem. Interface mista é proxy administrativa, não localização de conversão nem ecótono ecológico. Não há estimação específica de algodão ou conversão por cultura. Modelo inclui seis termos hierárquicos; preço×misto permanece identificável com FE bioma×ano porque misto não é igual a bioma.

Principal DK2 com t23. Famílias: 36 coeficientes por classe,12 testes conjuntos,36 contrastes formais,24 magnitudes incrementais. Holm por família não protege busca adaptativa entre rodadas; IC95 pontuais. Sensibilidades de covariância mantidas, matrizes brutas não positivas explicitadas sem PSD. Não escolher a que rejeita. Tendências/FE adicionais removem também possível resposta econômica: mudança de coeficiente não demonstra causalmente explicação concorrente.

## Ajustes

| id | N | municipios | anos | K_total | condicao | ajuste |
| --- | --- | --- | --- | --- | --- | --- |
| G71_agricultura | 2623 | 126 | 24 | 178 | 9.4853 | 0.029111 |
| G71_pastagem | 2623 | 126 | 24 | 178 | 9.4853 | 0.01442 |
| G72_agricultura | 2623 | 126 | 24 | 178 | 9.8135 | 0.022479 |
| G72_pastagem | 2623 | 126 | 24 | 178 | 9.8135 | 0.013464 |
| G73_agricultura | 2623 | 126 | 24 | 178 | 10.151 | 0.012032 |
| G73_pastagem | 2623 | 126 | 24 | 178 | 10.151 | 0.014593 |
| T71_agricultura | 2623 | 126 | 24 | 280 | 9.3522 | 0.011922 |
| T71_pastagem | 2623 | 126 | 24 | 280 | 9.3522 | 0.017276 |
| T72_agricultura | 2623 | 126 | 24 | 280 | 9.8109 | 0.01066 |
| T72_pastagem | 2623 | 126 | 24 | 280 | 9.8109 | 0.016621 |
| T73_agricultura | 2623 | 126 | 24 | 280 | 10.211 | 0.0061721 |
| T73_pastagem | 2623 | 126 | 24 | 280 | 10.211 | 0.017321 |

## Testes conjuntos das duas interações com interface

| id | covariancia | F | p | p_holm | status |
| --- | --- | --- | --- | --- | --- |
| G71_agricultura | DK1 | 3.5945 | 0.043812 | 0.17525 | estimado |
| G71_agricultura | DK2 | 3.3118 | 0.054454 | 0.21782 | estimado |
| G71_agricultura | DK3 | 3.3465 | 0.053011 | 0.21204 | estimado |
| G71_agricultura | municipio | 1.8806 | 0.15678 | 0.94071 | estimado |
| G71_agricultura | two_way_bruto | 1.4587 | 0.25325 | 1 | estimado |
| G71_pastagem | DK1 | 22.378 | 4.0176e-06 | 3.2141e-05 | estimado |
| G71_pastagem | DK2 | 26.434 | 1.0944e-06 | 1.0944e-05 | estimado |
| G71_pastagem | DK3 | 38.445 | 4.6279e-08 | 5.5535e-07 | estimado |
| G71_pastagem | municipio | 6.9697 | 0.0013499 | 0.013499 | estimado |
| G71_pastagem | two_way_bruto | 7.3997 | 0.0033021 | 0.029719 | estimado |
| G72_agricultura | DK1 | 4.2524 | 0.026826 | 0.15147 | estimado |
| G72_agricultura | DK2 | 3.7597 | 0.038658 | 0.19329 | estimado |
| G72_agricultura | DK3 | 3.744 | 0.039118 | 0.19559 | estimado |
| G72_agricultura | municipio | 1.2029 | 0.30377 | 1 | estimado |
| G72_agricultura | two_way_bruto | 1.1157 | 0.34478 | 1 | estimado |
| G72_pastagem | DK1 | 23.031 | 3.2257e-06 | 2.9032e-05 | estimado |
| G72_pastagem | DK2 | 27.788 | 7.3118e-07 | 8.043e-06 | estimado |
| G72_pastagem | DK3 | 38.148 | 4.9567e-08 | 5.5535e-07 | estimado |
| G72_pastagem | municipio | 7.4232 | 0.00089881 | 0.0098869 | estimado |
| G72_pastagem | two_way_bruto | 8.2419 | 0.0020001 | 0.022001 | estimado |
| G73_agricultura | DK1 | 4.3358 | 0.025245 | 0.15147 | estimado |
| G73_agricultura | DK2 | 4.3238 | 0.025466 | 0.15279 | estimado |
| G73_agricultura | DK3 | 4.3727 | 0.024577 | 0.14746 | estimado |
| G73_agricultura | municipio | 1.0699 | 0.34616 | 1 | estimado |
| G73_agricultura | two_way_bruto | 0.96432 | 0.39613 | 1 | estimado |
| G73_pastagem | DK1 | 20.296 | 8.3321e-06 | 5.8325e-05 | estimado |
| G73_pastagem | DK2 | 26.175 | 1.1841e-06 | 1.0944e-05 | estimado |
| G73_pastagem | DK3 | 37.253 | 6.1098e-08 | 6.1098e-07 | estimado |
| G73_pastagem | municipio | 8.0213 | 0.00052782 | 0.0063338 | estimado |
| G73_pastagem | two_way_bruto | 8.8149 | 0.0014394 | 0.017272 | estimado |
| T71_agricultura | DK1 | 2.8466 | 0.078599 | 0.2358 | estimado |
| T71_agricultura | DK2 | 2.9888 | 0.07017 | 0.21782 | estimado |
| T71_agricultura | DK3 | 3.0242 | 0.068227 | 0.21204 | estimado |
| T71_agricultura | municipio | 1.8673 | 0.15882 | 0.94071 | estimado |
| T71_agricultura | two_way_bruto | 1.2786 | 0.29749 | 1 | estimado |
| T71_pastagem | DK1 | 26.142 | 1.1963e-06 | 1.1963e-05 | estimado |
| T71_pastagem | DK2 | 25.57 | 1.4264e-06 | 1.0944e-05 | estimado |
| T71_pastagem | DK3 | 31.223 | 2.7888e-07 | 2.231e-06 | estimado |
| T71_pastagem | municipio | 4.045 | 0.019852 | 0.14722 | estimado |
| T71_pastagem | two_way_bruto | 6.4332 | 0.006039 | 0.042273 | estimado |
| T72_agricultura | DK1 | 2.8377 | 0.079163 | 0.2358 | estimado |
| T72_agricultura | DK2 | 2.6427 | 0.092664 | 0.21782 | estimado |
| T72_agricultura | DK3 | 2.5671 | 0.098555 | 0.21204 | estimado |
| T72_agricultura | municipio | 1.2567 | 0.28816 | 1 | estimado |
| T72_agricultura | two_way_bruto | 1.0816 | 0.35568 | 1 | estimado |
| T72_pastagem | DK1 | 27.737 | 7.4228e-07 | 8.165e-06 | estimado |
| T72_pastagem | DK2 | 25.872 | 1.2995e-06 | 1.0944e-05 | estimado |
| T72_pastagem | DK3 | 28.027 | 6.82e-07 | 4.774e-06 | estimado |
| T72_pastagem | municipio | 4.1257 | 0.018402 | 0.14722 | estimado |
| T72_pastagem | two_way_bruto | 6.853 | 0.004628 | 0.037024 | estimado |
| T73_agricultura | DK1 | 1.784 | 0.19043 | 0.2358 | estimado |
| T73_agricultura | DK2 | 1.7222 | 0.20093 | 0.21782 | estimado |
| T73_agricultura | DK3 | 1.7451 | 0.19697 | 0.21204 | estimado |
| T73_agricultura | municipio | 0.82182 | 0.44199 | 1 | estimado |
| T73_agricultura | two_way_bruto | 0.8735 | 0.43089 | 1 | estimado |
| T73_pastagem | DK1 | 30.811 | 3.1172e-07 | 3.7407e-06 | estimado |
| T73_pastagem | DK2 | 31.461 | 2.616e-07 | 3.1392e-06 | estimado |
| T73_pastagem | DK3 | 35.502 | 9.3037e-08 | 8.3734e-07 | estimado |
| T73_pastagem | municipio | 5.2458 | 0.0064913 | 0.058422 | estimado |
| T73_pastagem | two_way_bruto | 8.0556 | 0.0022305 | 0.022305 | estimado |

## Comparação dos incrementos com a referência da rodada6

| id | termo | coef_base | ic95_inf_base | ic95_sup_base | coef | ic95_inf | ic95_sup | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T71_agricultura | xh_soja | 0.51879 | 0.081713 | 0.95586 | 0.32605 | 0.048297 | 0.6038 | 0.70187 |
| T71_agricultura | xh_milho | -0.3017 | -0.59714 | -0.0062539 | -0.19651 | -0.36425 | -0.028776 | 0.70187 |
| T71_pastagem | xh_soja | 0.3068 | -0.66408 | 1.2777 | 0.050819 | -0.6553 | 0.75694 | 1 |
| T71_pastagem | xh_milho | -0.85481 | -1.3889 | -0.32074 | -0.682 | -1.0495 | -0.31454 | 0.029319 |
| T72_agricultura | xh_soja | 0.45959 | 0.039974 | 0.87921 | 0.30797 | 0.030851 | 0.58509 | 0.866 |
| T72_agricultura | xh_milho | -0.25532 | -0.54109 | 0.030453 | -0.18389 | -0.35394 | -0.013841 | 0.95223 |
| T72_pastagem | xh_soja | 0.2708 | -0.49228 | 1.0339 | -0.0051712 | -0.54448 | 0.53414 | 1 |
| T72_pastagem | xh_milho | -0.72246 | -1.247 | -0.1979 | -0.60678 | -0.97626 | -0.2373 | 0.084151 |
| T73_agricultura | xh_soja | 0.19049 | 0.024554 | 0.35643 | 0.12701 | -0.014573 | 0.2686 | 1 |
| T73_agricultura | xh_milho | -0.12851 | -0.28791 | 0.030883 | -0.090584 | -0.19777 | 0.016604 | 1 |
| T73_pastagem | xh_soja | 0.27968 | -0.35904 | 0.9184 | -0.037734 | -0.47334 | 0.39787 | 1 |
| T73_pastagem | xh_milho | -0.79286 | -1.3019 | -0.28378 | -0.64604 | -0.98562 | -0.30646 | 0.02376 |
| G71_agricultura | xh_soja | 0.51879 | 0.081713 | 0.95586 | 0.55269 | 0.055217 | 1.0502 | 0.8363 |
| G71_agricultura | xh_milho | -0.3017 | -0.59714 | -0.0062539 | -0.32374 | -0.65658 | 0.0090917 | 1 |
| G71_pastagem | xh_soja | 0.3068 | -0.66408 | 1.2777 | 0.83918 | 0.15371 | 1.5246 | 0.55817 |
| G71_pastagem | xh_milho | -0.85481 | -1.3889 | -0.32074 | -1.172 | -1.6872 | -0.65684 | 0.0032918 |
| G72_agricultura | xh_soja | 0.45959 | 0.039974 | 0.87921 | 0.46372 | 0.016283 | 0.91116 | 1 |
| G72_agricultura | xh_milho | -0.25532 | -0.54109 | 0.030453 | -0.25889 | -0.56539 | 0.047614 | 1 |
| G72_pastagem | xh_soja | 0.2708 | -0.49228 | 1.0339 | 0.67292 | 0.078206 | 1.2676 | 0.79199 |
| G72_pastagem | xh_milho | -0.72246 | -1.247 | -0.1979 | -1.0329 | -1.4821 | -0.58378 | 0.0029828 |
| G73_agricultura | xh_soja | 0.19049 | 0.024554 | 0.35643 | 0.17986 | 0.0052231 | 0.3545 | 1 |
| G73_agricultura | xh_milho | -0.12851 | -0.28791 | 0.030883 | -0.12044 | -0.28723 | 0.046339 | 1 |
| G73_pastagem | xh_soja | 0.27968 | -0.35904 | 0.9184 | 0.55326 | 0.018245 | 1.0883 | 1 |
| G73_pastagem | xh_milho | -0.79286 | -1.3019 | -0.28378 | -1.0294 | -1.4657 | -0.5931 | 0.0022568 |

## Contrastes formais e magnitudes, incluindo nulos

| id | contraste | estimativa | se | ic95_inf | ic95_sup | p | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G71_agricultura | Incremento soja | 0.55269 | 0.24048 | 0.055217 | 1.0502 | 0.030974 | 0.68043 |
| G71_agricultura | Incremento milho | -0.32374 | 0.16089 | -0.65658 | 0.0090917 | 0.056059 | 0.78483 |
| G71_agricultura | Incremento soja menos milho | 0.87644 | 0.39933 | 0.050367 | 1.7025 | 0.038539 | 0.6937 |
| G71_agricultura | Incremento misto; +10% soja; aptidão P75−P25 | 0.093608 | 0.04073 | 0.0093519 | 0.17786 | 0.030974 | 0.433 |
| G71_agricultura | Incremento misto; +10% milho; aptidão P75−P25 | -0.023945 | 0.0119 | -0.048562 | 0.00067245 | 0.056059 | 0.47123 |
| G71_pastagem | Incremento soja | 0.83918 | 0.33136 | 0.15371 | 1.5246 | 0.018606 | 0.50235 |
| G71_pastagem | Incremento milho | -1.172 | 0.24904 | -1.6872 | -0.65684 | 9.6818e-05 | 0.0032918 |
| G71_pastagem | Incremento soja menos milho | 2.0112 | 0.5718 | 0.82834 | 3.1941 | 0.0018483 | 0.057299 |
| G71_pastagem | Incremento misto; +10% soja; aptidão P75−P25 | 0.14213 | 0.056121 | 0.026034 | 0.25822 | 0.018606 | 0.3349 |
| G71_pastagem | Incremento misto; +10% milho; aptidão P75−P25 | -0.086685 | 0.018419 | -0.12479 | -0.048582 | 9.6818e-05 | 0.00213 |
| G72_agricultura | Incremento soja | 0.46372 | 0.21629 | 0.016283 | 0.91116 | 0.042839 | 0.72826 |
| G72_agricultura | Incremento milho | -0.25889 | 0.14817 | -0.56539 | 0.047614 | 0.093927 | 0.91622 |
| G72_agricultura | Incremento soja menos milho | 0.72261 | 0.36258 | -0.027447 | 1.4727 | 0.058261 | 0.78483 |
| G72_agricultura | Incremento misto; +10% soja; aptidão P75−P25 | 0.078539 | 0.036633 | 0.0027577 | 0.15432 | 0.042839 | 0.47123 |
| G72_agricultura | Incremento misto; +10% milho; aptidão P75−P25 | -0.019148 | 0.010959 | -0.041818 | 0.0035217 | 0.093927 | 0.56259 |
| G72_pastagem | Incremento soja | 0.67292 | 0.28749 | 0.078206 | 1.2676 | 0.028285 | 0.65057 |
| G72_pastagem | Incremento milho | -1.0329 | 0.21712 | -1.4821 | -0.58378 | 8.5223e-05 | 0.0029828 |
| G72_pastagem | Incremento soja menos milho | 1.7059 | 0.49604 | 0.67971 | 2.732 | 0.002237 | 0.064874 |
| G72_pastagem | Incremento misto; +10% soja; aptidão P75−P25 | 0.11397 | 0.048691 | 0.013246 | 0.2147 | 0.028285 | 0.42428 |
| G72_pastagem | Incremento misto; +10% milho; aptidão P75−P25 | -0.076398 | 0.016059 | -0.10962 | -0.043178 | 8.5223e-05 | 0.0019601 |
| G73_agricultura | Incremento soja | 0.17986 | 0.084421 | 0.0052231 | 0.3545 | 0.044043 | 0.72826 |
| G73_agricultura | Incremento milho | -0.12044 | 0.080624 | -0.28723 | 0.046339 | 0.14879 | 0.91622 |
| G73_agricultura | Incremento soja menos milho | 0.30031 | 0.16346 | -0.037838 | 0.63845 | 0.079139 | 0.91622 |
| G73_agricultura | Incremento misto; +10% soja; aptidão P75−P25 | 0.030463 | 0.014298 | 0.00088463 | 0.060041 | 0.044043 | 0.47123 |
| G73_agricultura | Incremento misto; +10% milho; aptidão P75−P25 | -0.0089083 | 0.0059631 | -0.021244 | 0.0034273 | 0.14879 | 0.59518 |
| G73_pastagem | Incremento soja | 0.55326 | 0.25863 | 0.018245 | 1.0883 | 0.043261 | 0.72826 |
| G73_pastagem | Incremento milho | -1.0294 | 0.2109 | -1.4657 | -0.5931 | 6.2689e-05 | 0.0022568 |
| G73_pastagem | Incremento soja menos milho | 1.5826 | 0.45832 | 0.63454 | 2.5307 | 0.002161 | 0.06483 |
| G73_pastagem | Incremento misto; +10% soja; aptidão P75−P25 | 0.093704 | 0.043803 | 0.0030901 | 0.18432 | 0.043261 | 0.47123 |
| G73_pastagem | Incremento misto; +10% milho; aptidão P75−P25 | -0.076135 | 0.015599 | -0.1084 | -0.043867 | 6.2689e-05 | 0.0015045 |
| T71_agricultura | Incremento soja | 0.32605 | 0.13427 | 0.048297 | 0.6038 | 0.023396 | 0.58752 |
| T71_agricultura | Incremento milho | -0.19651 | 0.081084 | -0.36425 | -0.028776 | 0.023643 | 0.58752 |
| T71_agricultura | Incremento soja menos milho | 0.52256 | 0.21379 | 0.080302 | 0.96482 | 0.022597 | 0.58752 |
| T71_agricultura | Incremento misto; +10% soja; aptidão P75−P25 | 0.055222 | 0.02274 | 0.0081799 | 0.10226 | 0.023396 | 0.39773 |
| T71_agricultura | Incremento misto; +10% milho; aptidão P75−P25 | -0.014534 | 0.0059972 | -0.026941 | -0.0021283 | 0.023643 | 0.39773 |
| T71_pastagem | Incremento soja | 0.050819 | 0.34134 | -0.6553 | 0.75694 | 0.88295 | 1 |
| T71_pastagem | Incremento milho | -0.682 | 0.17764 | -1.0495 | -0.31454 | 0.00083769 | 0.026806 |
| T71_pastagem | Incremento soja menos milho | 0.73282 | 0.50171 | -0.30504 | 1.7707 | 0.15764 | 0.91622 |
| T71_pastagem | Incremento misto; +10% soja; aptidão P75−P25 | 0.008607 | 0.057812 | -0.11099 | 0.1282 | 0.88295 | 1 |
| T71_pastagem | Incremento misto; +10% milho; aptidão P75−P25 | -0.050443 | 0.013138 | -0.077621 | -0.023264 | 0.00083769 | 0.016754 |
| T72_agricultura | Incremento soja | 0.30797 | 0.13396 | 0.030851 | 0.58509 | 0.030929 | 0.68043 |
| T72_agricultura | Incremento milho | -0.18389 | 0.082202 | -0.35394 | -0.013841 | 0.035268 | 0.68043 |
| T72_agricultura | Incremento soja menos milho | 0.49186 | 0.21472 | 0.047676 | 0.93604 | 0.031478 | 0.68043 |
| T72_agricultura | Incremento misto; +10% soja; aptidão P75−P25 | 0.05216 | 0.022689 | 0.0052251 | 0.099095 | 0.030929 | 0.433 |
| T72_agricultura | Incremento misto; +10% milho; aptidão P75−P25 | -0.013601 | 0.0060799 | -0.026178 | -0.0010237 | 0.035268 | 0.433 |
| T72_pastagem | Incremento soja | -0.0051712 | 0.2607 | -0.54448 | 0.53414 | 0.98435 | 1 |
| T72_pastagem | Incremento milho | -0.60678 | 0.17861 | -0.97626 | -0.2373 | 0.002475 | 0.069301 |
| T72_pastagem | Incremento soja menos milho | 0.60161 | 0.42642 | -0.28051 | 1.4837 | 0.17168 | 0.91622 |
| T72_pastagem | Incremento misto; +10% soja; aptidão P75−P25 | -0.00087582 | 0.044155 | -0.092217 | 0.090465 | 0.98435 | 1 |
| T72_pastagem | Incremento misto; +10% milho; aptidão P75−P25 | -0.044879 | 0.01321 | -0.072207 | -0.017551 | 0.002475 | 0.047026 |
| T73_agricultura | Incremento soja | 0.12701 | 0.068443 | -0.014573 | 0.2686 | 0.076352 | 0.91622 |
| T73_agricultura | Incremento milho | -0.090584 | 0.051815 | -0.19777 | 0.016604 | 0.093765 | 0.91622 |
| T73_agricultura | Incremento soja menos milho | 0.2176 | 0.11839 | -0.02732 | 0.46251 | 0.079029 | 0.91622 |
| T73_agricultura | Incremento misto; +10% soja; aptidão P75−P25 | 0.021512 | 0.011592 | -0.0024683 | 0.045492 | 0.076352 | 0.53446 |
| T73_agricultura | Incremento misto; +10% milho; aptidão P75−P25 | -0.0066998 | 0.0038324 | -0.014628 | 0.0012281 | 0.093765 | 0.56259 |
| T73_pastagem | Incremento soja | -0.037734 | 0.21057 | -0.47334 | 0.39787 | 0.85935 | 1 |
| T73_pastagem | Incremento milho | -0.64604 | 0.16415 | -0.98562 | -0.30646 | 0.00066 | 0.02178 |
| T73_pastagem | Incremento soja menos milho | 0.60831 | 0.36128 | -0.13905 | 1.3557 | 0.10575 | 0.91622 |
| T73_pastagem | Incremento misto; +10% soja; aptidão P75−P25 | -0.006391 | 0.035664 | -0.080168 | 0.067386 | 0.85935 | 1 |
| T73_pastagem | Incremento misto; +10% milho; aptidão P75−P25 | -0.047783 | 0.012141 | -0.072898 | -0.022667 | 0.00066 | 0.01386 |

## Variação residual retida por classe e regressor

| classe | termo | min | max |
| --- | --- | --- | --- |
| G | ph_milho | 0.9876 | 0.99574 |
| G | ph_soja | 0.98802 | 0.99567 |
| G | x_milho | 0.92088 | 0.92088 |
| G | x_soja | 0.70437 | 0.70437 |
| G | xh_milho | 0.9735 | 0.98216 |
| G | xh_soja | 0.97699 | 0.99223 |
| T | ph_milho | 0.77441 | 0.77888 |
| T | ph_soja | 0.73884 | 0.74457 |
| T | x_milho | 0.79404 | 0.79404 |
| T | x_soja | 0.75496 | 0.75496 |
| T | xh_milho | 0.78703 | 0.78967 |
| T | xh_soja | 0.73836 | 0.74957 |

## Fechamento admissível

Esta rodada encerra a comparação planejada dos gradientes territoriais com controles de choques e tendências. Nenhum novo modelo será escolhido pela direção ou pelo p. As evidências associativas e suas sensibilidades são descritas em CONCLUSAO_GERAL.md; não aceitam nem rejeitam toda H1 causal. Ausência de rejeição pode refletir imprecisão; não foi predefinida margem de equivalência. Mais combinações da mesma amostra não criariam conversão localizada por cultura, dados de algodão, suporte Pantanal ou um desenho exógeno para fiscalização. Esses são os próximos dados necessários.

Resultados locais; publicação pendente de autorização específica para o escopo ampliado.

## Achado e alcance

G71_pastagem (interface >1e−6, FE município+bioma×ano): incremento milho −1,1720 pp por unidade log-preço×DP aptidão (SE DK2 0,2490; IC95 −1,6872 a −0,6568; p bruto 0,0000968; Holm36 0,00329). Na escala +10% preço e P75−P25 aptidão, a diferença do gradiente entre mistos e não mistos é −0,0867 pp (IC95 −0,1248 a −0,0486), aproximadamente −0,867 ha por 1000 ha nativos. É diferença de gradientes, não diferença total de conversão entre grupos ou efeito médio do preço.

Teste conjunto G71 das duas interações: Holm12 DK2 0,0000109, municipal 0,0135, two-way bruto 0,0297; também rejeita nas outras duas definições com DK2 e municipal. A interação milho permanece negativa nas três definições e com tendências; T71 estimativa −0,6820 (IC95 −1,0495 a −0,3145). Contudo, os testes conjuntos das tendências não rejeitam após Holm com cluster municipal (0,147/0,147/0,058). Portanto há padrão associativo localizado e persistência de sinal, com robustez inferencial parcial, não validação uniforme de H1.

Diferença formal entre os incrementos soja e milho em G71: 2,0112, IC95 0,8283 a 3,1941; Holm36 0,0573. Não inferir que culturas diferem apenas porque milho rejeita e soja não. Não rejeitar após Holm também não demonstra igualdade. Interações xh retêm cerca de 98–99% da variação residual com FE bioma×ano; tendências retêm cerca de 75–79%. A alteração da estimativa não pode ser atribuída apenas a desaparecimento de todo suporte.

Esses resultados são compatíveis com heterogeneidade territorial da associação incentivo×aptidão na conversão para pastagem. Não identificam qual mecanismo a produz: custos, composição produtiva, instituições, substituição de uso ou seleção territorial continuam alternativas, não explicações comprovadas. A classificação municipal é uma medição imperfeita de interface; não permite alegar mecanismo ecológico de ecótono.
