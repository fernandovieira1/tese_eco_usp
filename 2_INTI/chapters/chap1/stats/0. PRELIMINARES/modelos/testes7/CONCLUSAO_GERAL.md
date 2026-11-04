# Conclusão das rodadas locais 2–7

## O que os dados sustentam

Há evidência associativa de heterogeneidade na relação preços×aptidão e conversão, especialmente para pastagem. Ela não autoriza aceitar H1 em sua formulação causal completa: retornos esperados não se resumem a preços, a aptidão incorpora terras2010, estoque é endógeno e autuações não medem efetividade institucional. Não foi demonstrado mecanismo causal nem equivalência a zero para resultados imprecisos.

1. **Associação agregada parcial.** No núcleo amplo da rodada2, interação padronizada soja×aptidão para pastagem =0,1038 pp (IC95 0,0385–0,1691; Holm4 0,0128). Para agricultura=0,0288 (−0,0047–0,0623). Diferença formal entre destinos=0,0750 (0,0211–0,1290; Holm2 0,0170). Portanto não se inferiu diferença comparando significâncias. O cenário de +10% preço médio e aptidão P75−P25 corresponde a 0,0782 pp para pastagem (0,0290–0,1274), associação diferencial, não efeito médio causal.
2. **Composição amostral importa.** A interação soja/agricultura cai de aproximadamente 0,0288 na amostra ampla para0,0074 na amostra fiscal antes de acrescentar fiscalização; após incluí-la ≈0,0077. Essa comparação separa composição e associação condicional; não prova eficácia/ineficácia institucional. Fiscalização permanece endógena.
3. **Dinâmica não elimina confusão territorial.** A soma dos lags da exposição soja para pastagem é positiva (rodada3≈0,1627), persiste com tendências (rodada4≈0,1637), mas cai para≈0,0102 com choques bioma×ano, com IC cruzando zero; milho acumulado nessa especificação≈0,1287 (0,0533–0,2042). Isso mostra sensibilidade ao controle de choques territoriais. Não prova que bioma cause a conversão nem qual preço represente o mecanismo.
4. **Influência/escala não explicam sozinhas o padrão inicial.** Exclusões sistemáticas de municípios/anos preservam sinal positivo da exposição soja/pastagem; denominador congelado2001 não elimina a associação. Não linearidades, ocorrência de zeros e painel balanceado não fornecem validação uniforme adicional. Todos os ajustes estão registrados, não apenas os favoráveis.
5. **Inferência temporal é limitante.** Rodada5: a soma dinâmica soja/pastagem tem p bruto por blocos de 3 anos 0,0078125, Holm16=0,125; blocos de 2 anos p 0,001953, Holm16=0,03125. Com oito blocos Rademacher, p bilateral mínimo=2/256=0,0078125 e o primeiro limiar Holm16=0,003125: nenhuma rejeição ajustada é possível nessa configuração. Não rejeitar ali é parcialmente uma limitação de resolução, não evidência do nulo. Esses exercícios não são testes específicos dos novos modelos das rodadas6–7.

## Culturas e biomas: o que a ampliação acrescentou

O CSV distingue **agricultura agregada e pastagem**, não conversão específica para soja/milho/algodão. Preços soja e milho são altamente correlacionados (logs r=0,9476). Modelos conjuntos com posto completo permitem comparar gradientes condicionais, não separar causalmente mercados. Algodão está ausente nos schemas do painel exato e do auxiliar EDA consultado: não foi inventado nem rateado.

Rodada6, no grupo base Cerrado da amostra sem qualquer fração Pantanal relevante: diferença soja−milho do gradiente de pastagem é −0,5296 (IC95 −0,8133 a −0,2459; Holm52=0,0404), e −0,5321 com FE bioma×ano (Holm52=0,0437). Comparações usam mesma variação proporcional do preço e 1 DP de cada aptidão, não mesma produtividade física. Testes conjuntos Amazônia–Cerrado não são precisos após Holm; isso não estabelece homogeneidade.

**Interfaces administrativas revelam um padrão localizado.** Na rodada7, modelo G71_pastagem (FE município+bioma×ano, N=2623,126 municípios,24 anos), o incremento do gradiente milho nos municípios mistos é −1,1720 pp por log-preço×DP aptidão (SE DK2=0,2490; IC95 −1,6872 a −0,6568; Holm36=0,00329). Para +10% preço e P75−P25 aptidão, isso representa diferença de gradientes de −0,0867 pp (−0,1248 a −0,0486), ou cerca de −0,867 ha por 1000 ha nativos. Não é o efeito total do preço nem a diferença total entre grupos.

O teste conjunto das interações soja/milho nessa especificação permanece após Holm12 com DK2 (0,0000109), cluster municipal (0,0135) e two-way bruto (0,0297). Sinais e rejeições conjuntas persistem nos limiares 5% e10% com DK2 e municipal. Com tendências municipais, o incremento milho também é negativo, mas a rejeição conjunta é sensível à covariância. A diferença formal dos incrementos soja−milho em G71 tem Holm36=0,0573: não se declara diferença entre culturas a partir de significâncias individuais.

Isso é compatível com heterogeneidade territorial da associação incentivo×aptidão para pastagem. **Não discrimina o mecanismo** entre composição produtiva, custos, instituições, substituição de usos ou seleção territorial. Essas alternativas não foram comprovadas. A localização real das conversões não é conhecida dentro dos municípios. Mistura de frações de bioma é proxy administrativa; não se identificou efeito de ecótono ecológico.

Pantanal:4 municípios na grade,3 com conversão válida,54 observações;13 com alguma fração territorial. Sua análise ficou descritiva por suporte restrito. Excluí-lo das comparações territoriais limita generalização; não significa que seja irrelevante.

## Escopo realizado e validação

| Rodada | Notebooks executados | Ajustes | Pergunta |
| --- | --- | --- | --- |
| 2 | 4 | 19 | composição fiscal, núcleo TWFE, PPML/logit harmonizados |
| 3 | 3 | 15 | dinâmica, tendências e choques territoriais |
| 4 | 6 | 346 | influência, heterogeneidade, curvatura, zeros, denominadores |
| 5 | 1 | 8 | inferência por blocos,32 exercícios,36480 padrões |
| 6 | 4 | 16 | culturas/biomas/interfaces administrativas |
| 7 | 2 | 12 | interfaces com choques territoriais/tendências |

Total:20 notebooks,416 ajustes, dos quais322 são reestimações diagnósticas leave-one-out e94 são substantivos/referência. Não são416 testes independentes. Round1/testes_chap1 preservada e fora desta contagem. Todas as rodadas registram estratégia anterior às estimações, amostras/perdas, nulos, matrizes, dependências e reprodução. Testes numéricos conferem p/IC/Holm, contrastes com covariância completa, notebooks executados, hashes e estimadores independentes de FE/tendências. Reprodução end-to-end concluída; logs em 2_INTI/audit/testes2…testes7. Falha pontual de renderização Markdown por tabulate ausente foi corrigida sem instalar dependência; cálculos não foram afetados.

As famílias de Holm são explícitas em cada estratégia. Correção dentro da rodada/família **não controla toda busca adaptativa**. IC95 apresentados são pontuais, não simultâneos. Nenhuma margem de equivalência foi definida a posteriori; p>0,05 não foi tratado como aceitação da nula. Todos os ajustes das grades foram reportados, inclusive nulos. O avanço entre rodadas foi adaptativo e está documentado; não é uma pré-especificação global independente dos resultados.

## Por que encerrar agora

O encerramento decorre de limites de mensuração e identificação, após verificar os ramos admissíveis relevantes, não de uma contagem arbitrária ou de ter encontrado significância. Os dados atuais sustentam padrões associativos parciais e heterogêneos; não resolvem a hipótese causal completa. Variantes adicionais das mesmas regressoras não criariam conversão por cultura, localização ecológica, mais unidades Pantanal ou exogeneidade institucional.

Próximos dados necessários: transições anuais georreferenciadas para culturas/destinos específicos, definição externa de faixas ecotonais, preços/aptidão/exposição de algodão, suporte temporal/territorial Pantanal e um desenho institucional defensável com medida de implementação/efetividade e variação exógena. IV/RDD/DiD não são atalhos sem regra, exposição e controle válidos.

## Publicação

Tudo nas rodadas2–7 permanece local. Commit/push/publicação do escopo ampliado foi bloqueado pela revisão automática no chat principal e está pendente de autorização específica. Nenhuma tentativa foi feita nesta continuação. HEAD permaneceu df0a238d4ccb729fb3177b443251fbbaa0cabc93; o status rastreado é limpo porque essas pastas estão ignoradas. Dados/textos/rodada1 e rodadas anteriores foram preservados por hash.
