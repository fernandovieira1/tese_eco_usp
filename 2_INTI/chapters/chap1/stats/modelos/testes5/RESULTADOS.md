# Resultados — rodada 5

Oito equações de referência (já estudadas, reestimadas para a inferência), 16 restrições escalares em dois tamanhos de bloco: 32 exercícios wild bootstrap e 36.480 padrões de sinais enumerados. Nenhuma variância degenerada. A hipótese nula foi imposta, os FE foram reestimados via projeção e padrões selecionados foram conferidos contra reestimação direta. O padrão com todos pesos +1 reproduz a estatística observada. Não houve erro Monte Carlo; isso não torna o teste exato nem valida independência/simetria de blocos.

A soma dinâmica soja/pastagem, sem choques específicos de bioma, tem p wild bruto 0,0078125 e Holm 0,125 com blocos de três anos; com dois anos, p bruto 0,0019531 e Holm 0,03125. Não escolher dois anos porque rejeita. A associação estática soja/pastagem tem p wild 0,08594 (blocos3) e 0,04639 (blocos2), ambos sem rejeição após Holm. O resultado dinâmico milho/pastagem sob FE bioma×ano tem p wild 0,015625/0,03125, mas Holm 0,234375/0,4375. Assim, há sinal associativo em especificações, mas sua força inferencial depende de pressupostos temporais e família de testes.

Na janela de 14 anos, três anos por bloco geram somente cinco blocos e 32 padrões. Num teste bilateral com simetria, a resolução mínima é 2/32=0,0625. A falta de rejeição em 5% nessa janela não pode ser interpretada como ausência de efeito. O IC95 exportado é DK assintótico, não IC bootstrap; não foi feita inversão de bootstrap nem teste de equivalência. Nem a enumeração nem a multiplicidade removem confundimento.

Não serão abertas novas rodadas de busca de especificação. As etapas anteriores examinaram questões econômicas/estatísticas distintas; esta etapa mostrou que a força dos p-valores também depende de poucos blocos temporais. Permanecem associações condicionais e limites de mensuração/identificação, não H1 aceita ou rejeitada causalmente. CONCLUSAO_RODADAS.md integra o que foi discriminado, o que permanece aberto e os dados necessários.

## Todos os exercícios

| id | contraste | estimativa | se_DK2 | ic95_DK_inf | ic95_DK_sup | p_DK2 | bloco_anos | blocos | padroes | p_wild | p_wild_holm | N | anos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W01_agricultura | soja | 0.028791 | 0.016204 | -0.004729 | 0.062312 | 0.088833 | 3 | 8 | 256 | 0.367188 | 1.0 | 2772 | 24 |
| W01_agricultura | soja | 0.028791 | 0.016204 | -0.004729 | 0.062312 | 0.088833 | 2 | 12 | 4096 | 0.228027 | 1.0 | 2772 | 24 |
| W01_agricultura | milho | 0.003751 | 0.004968 | -0.006527 | 0.014028 | 0.45794 | 3 | 8 | 256 | 0.679688 | 1.0 | 2772 | 24 |
| W01_agricultura | milho | 0.003751 | 0.004968 | -0.006527 | 0.014028 | 0.45794 | 2 | 12 | 4096 | 0.337402 | 1.0 | 2772 | 24 |
| W01_pastagem | soja | 0.103806 | 0.031554 | 0.038532 | 0.16908 | 0.003208 | 3 | 8 | 256 | 0.085938 | 1.0 | 2772 | 24 |
| W01_pastagem | soja | 0.103806 | 0.031554 | 0.038532 | 0.16908 | 0.003208 | 2 | 12 | 4096 | 0.046387 | 0.603027 | 2772 | 24 |
| W01_pastagem | milho | 0.058373 | 0.026811 | 0.00291 | 0.113836 | 0.039979 | 3 | 8 | 256 | 0.140625 | 1.0 | 2772 | 24 |
| W01_pastagem | milho | 0.058373 | 0.026811 | 0.00291 | 0.113836 | 0.039979 | 2 | 12 | 4096 | 0.09668 | 1.0 | 2772 | 24 |
| W02_agricultura | soja | 0.043254 | 0.022958 | -0.00449 | 0.090997 | 0.07348 | 3 | 8 | 256 | 0.25 | 1.0 | 2539 | 22 |
| W02_agricultura | soja | 0.043254 | 0.022958 | -0.00449 | 0.090997 | 0.07348 | 2 | 11 | 2048 | 0.125977 | 1.0 | 2539 | 22 |
| W02_agricultura | milho | 0.004091 | 0.008937 | -0.014494 | 0.022677 | 0.651802 | 3 | 8 | 256 | 0.929688 | 1.0 | 2539 | 22 |
| W02_agricultura | milho | 0.004091 | 0.008937 | -0.014494 | 0.022677 | 0.651802 | 2 | 11 | 2048 | 0.730469 | 1.0 | 2539 | 22 |
| W02_pastagem | soja | 0.162741 | 0.02199 | 0.117011 | 0.208472 | 0.0 | 3 | 8 | 256 | 0.007812 | 0.125 | 2539 | 22 |
| W02_pastagem | soja | 0.162741 | 0.02199 | 0.117011 | 0.208472 | 0.0 | 2 | 11 | 2048 | 0.001953 | 0.03125 | 2539 | 22 |
| W02_pastagem | milho | 0.050238 | 0.023407 | 0.001561 | 0.098914 | 0.043689 | 3 | 8 | 256 | 0.078125 | 1.0 | 2539 | 22 |
| W02_pastagem | milho | 0.050238 | 0.023407 | 0.001561 | 0.098914 | 0.043689 | 2 | 11 | 2048 | 0.125977 | 1.0 | 2539 | 22 |
| W03_agricultura | soja | 0.03852 | 0.01884 | -0.00066 | 0.0777 | 0.053637 | 3 | 8 | 256 | 0.257812 | 1.0 | 2539 | 22 |
| W03_agricultura | soja | 0.03852 | 0.01884 | -0.00066 | 0.0777 | 0.053637 | 2 | 11 | 2048 | 0.151367 | 1.0 | 2539 | 22 |
| W03_agricultura | milho | 0.0111 | 0.01282 | -0.015561 | 0.03776 | 0.39637 | 3 | 8 | 256 | 0.828125 | 1.0 | 2539 | 22 |
| W03_agricultura | milho | 0.0111 | 0.01282 | -0.015561 | 0.03776 | 0.39637 | 2 | 11 | 2048 | 0.665039 | 1.0 | 2539 | 22 |
| W03_pastagem | soja | 0.010221 | 0.025866 | -0.043571 | 0.064012 | 0.696724 | 3 | 8 | 256 | 0.664062 | 1.0 | 2539 | 22 |
| W03_pastagem | soja | 0.010221 | 0.025866 | -0.043571 | 0.064012 | 0.696724 | 2 | 11 | 2048 | 0.699219 | 1.0 | 2539 | 22 |
| W03_pastagem | milho | 0.128728 | 0.036286 | 0.053267 | 0.20419 | 0.001906 | 3 | 8 | 256 | 0.015625 | 0.234375 | 2539 | 22 |
| W03_pastagem | milho | 0.128728 | 0.036286 | 0.053267 | 0.20419 | 0.001906 | 2 | 11 | 2048 | 0.03125 | 0.4375 | 2539 | 22 |
| W04_agricultura | soja | 0.005982 | 0.001866 | 0.001952 | 0.010013 | 0.006878 | 3 | 5 | 32 | 0.125 | 1.0 | 1635 | 14 |
| W04_agricultura | soja | 0.005982 | 0.001866 | 0.001952 | 0.010013 | 0.006878 | 2 | 7 | 128 | 0.046875 | 0.603027 | 1635 | 14 |
| W04_agricultura | milho | -0.007516 | 0.001364 | -0.010463 | -0.004568 | 0.000101 | 3 | 5 | 32 | 0.0625 | 0.875 | 1635 | 14 |
| W04_agricultura | milho | -0.007516 | 0.001364 | -0.010463 | -0.004568 | 0.000101 | 2 | 7 | 128 | 0.015625 | 0.234375 | 1635 | 14 |
| W04_pastagem | soja | 0.124614 | 0.038628 | 0.041163 | 0.208065 | 0.006628 | 3 | 5 | 32 | 0.125 | 1.0 | 1635 | 14 |
| W04_pastagem | soja | 0.124614 | 0.038628 | 0.041163 | 0.208065 | 0.006628 | 2 | 7 | 128 | 0.234375 | 1.0 | 1635 | 14 |
| W04_pastagem | milho | 0.011403 | 0.035711 | -0.065747 | 0.088553 | 0.754562 | 3 | 5 | 32 | 0.9375 | 1.0 | 1635 | 14 |
| W04_pastagem | milho | 0.011403 | 0.035711 | -0.065747 | 0.088553 | 0.754562 | 2 | 7 | 128 | 0.78125 | 1.0 | 1635 | 14 |

## Reprodução

Instalar requirements.txt em ambiente externo e executar `python reproduzir.py`. Usa metodos.py e executar.py de testes2, sem editar a rodada1. bootstrap_blocos.py contém a restrição e projeção explicitamente. CSVs comprimidos guardam todos os padrões; sinal 0 na assinatura binária significa −1 e sinal 1 significa +1. BOOTSTRAP.csv registra cada restrição, tamanho de bloco, p e verificações. Estratégia, hashes e execução estão em ESTRATEGIA.md/METADADOS.json/EXECUCAO.json/VALIDACAO.json; log em 2_INTI/audit/testes5. Sem commit/push/publicação.

## Escopo da multiplicidade e da adaptação

Holm aplica-se somente às famílias registradas nesta rodada, com tamanho em n_familia nos CSVs. As rodadas foram adaptadas aos diagnósticos anteriores e reutilizam os mesmos dados: a correção por família/rodada não controla integralmente o erro da busca sequencial nem converte exploração em teste confirmatório. Uma confirmação independente exige protocolo externo/prévio e dados novos ou identificação adicional.
