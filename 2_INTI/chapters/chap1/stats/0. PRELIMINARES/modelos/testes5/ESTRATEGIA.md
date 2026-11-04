# Rodada 5 — sensibilidade da inferência a poucos blocos temporais

Motivo anterior à execução: nas rodadas2–4, o sinal soja/pastagem não depende de unidade isolada, mas é sensível aos choques de bioma; a janela pós2010 tem apenas 14 anos e produziu Wald F muito altos. A lacuna restante desta rodada é a confiança na aproximação assintótica, não descobrir outra especificação significativa.

## Referências e contrastes (sem novas hipóteses econômicas)

Reestimar oito equações já consideradas: W01 núcleo estático amplo por destino (2); W02 lags1–3 amplos por destino (2); W03 lags1–3 com FE bioma×ano por destino (2); W04 lags1–3 na janela 2011–2024 por destino (2). Em W01 testar cada exposição soja/milho individualmente; em W02–W04 testar a soma de três lags por cultura. Total 16 restrições escalares, todas testadas, sem selecionar pelo p anterior. Estimandos, escalas, filtros e FE iguais às rodadas anteriores.

## Bootstrap wild restrito, com hipótese nula imposta

Inferência de referência permanece DK Bartlett lag2, t(T−1), IC95 e covariâncias alternativas. Sensibilidade adicional: resíduos do modelo restrito a a'β=0 multiplicados por pesos Rademacher constantes em blocos de três anos calendários consecutivos, ancorados no primeiro ano da amostra (último bloco pode ser menor). Todos os 2^G padrões de sinal serão enumerados; não há erro Monte Carlo. Reestimar FE e slopes em cada padrão, studentizar com DK2 idêntico ao original e calcular proporção de |t*|≥|t_observado|. A restrição é imposta por mínimos quadrados restritos; projetar novamente os resíduos ponderados para FE. Confirmar que o padrão de todos pesos +1 reproduz t observado.

A enumeração não torna o teste exato em amostra finita: requer condições de independência/simetria entre blocos, não demonstradas. Dependência acima de três anos, heterogeneidade e a escolha de blocos podem invalidar a aproximação. A janela de 14 anos fornece cinco blocos, só 32 padrões, com resolução muito limitada (simetria de dois lados). Não declarar ausência de efeito quando um p não puder ficar abaixo de 5%. Sensibilidade predefinida: blocos de dois anos, enumerados integralmente, sem escolher o tamanho pelo resultado.

Não tentar teste conjunto de seis coeficientes baseado em covariância de cinco blocos: posto/informação insuficiente. Os testes conjuntos assintóticos já foram exportados nas rodadas anteriores e permanecem limitados por T. A etapa nova é uma sensibilidade escalar complementar, não substituição seletiva de resultados.

## Famílias, registro e encerramento

Holm dos 16 p wild com blocos3; Holm separado dos mesmos 16 com blocos2. Reportar também p bruto, números de blocos/padrões, estatística observada, IC assintótico (claramente distinto de IC bootstrap), falhas/variâncias degeneradas. Não inverter bootstrap para chamar o IC DK de bootstrap. Todas estatísticas de cada padrão serão salvas em CSV comprimido, além de resumo uniforme, scripts, hashes e logs. Serão oito ajustes de referência e 32 exercícios bootstrap, não milhares de novas hipóteses econômicas.

Após essa etapa, sintetizar quais explicações foram discriminadas e quais são não identificadas. Foram examinados amostra/fiscalização, escala/denominador, FE não linear, dinâmica, tendências, choques de bioma, janelas, primeiras diferenças, influência, heterogeneidade formal, não linearidade, zeros e inferência. Outras regressões com os mesmos proxies não criam custos/expectativas, aptidão historicamente predeterminada, exposição de política ou instrumentos. RDD/DiD/IV/GMM/espacial/ML causal continuam sem pressupostos/dados verificados. Encerrar a busca por identificabilidade, sem declarar todas especificações matemáticas esgotadas ou H1 aceita/rejeitada causalmente. Sem equivalência porque não há margem substantiva justificada. Publicação permanece proibida.

Referências técnicas consultadas em 23/10/2026: [MacKinnon e Webb, poucos clusters](https://qed.econ.queensu.ca/pub/faculty/mackinnon/working-papers/qed_wp_1364.pdf), [Canay, Santos e Shaikh, condições com poucos clusters](https://faculty.wcas.northwestern.edu/iac879/wp/wildfewclusters.pdf), [manual técnico Stata wildbootstrap](https://www.stata.com/manuals/rwildbootstrap.pdf). A aplicação a blocos temporais adiciona hipóteses próprias; não se herda validade automática dos exemplos de clusters independentes.
