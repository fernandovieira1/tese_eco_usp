# Base2 — plano anterior à construção

Autorização: construir segunda base com dados existentes; nenhuma regressão, coleta externa ou publicação. Fontes e rodadas1–7 intocadas. Pasta base2 inexistente na inspeção inicial, criada para esta entrega. Fetch origin/main concluído; HEAD e remoto df0a238d4ccb729fb3177b443251fbbaa0cabc93. O remoto não contém 2_INTI/xdata nem os custos CONAB referenciados; pendência não bloqueia os demais blocos.

## Escopo, chaves e camadas

Painel-mestre: preservar 3384 linhas/70 colunas originais, ordem e valores, 141 códigos municipais de sete dígitos,2001–2024. CSV pode representar números equivalentes com outra formatação; comparar valores e máscaras de faltantes, preservar fonte byte a byte. Junções um-para-um por código/ano, sem casar por nome nem recodificar141→140. Conferir IDs/nomes/frações e variáveis comuns entre painel principal e PT; divergências impedem certificação do bloco correspondente, nunca sobrescrevem original. GM não será incorporado, devido às falhas documentadas.

Camada de validação interna adicional: chuva anual CHIRPS, anomalia/z-score1981–2000 SOMENTE se fórmulas e suporte forem verificáveis, campos de cobertura12meses e pixels; relevo Copernicus com ordem min≤média≤max e invariância; defasagens próprias dos rendimentos observados com ano consecutivo e sem preenchimento. Clima anual não é calendário agrícola. Base1981–2000 é anterior à amostra; não usar normal1991–2020 como se fosse pré-tratamento. Validação interna/documental não certifica integralmente raster, geografia histórica ou exogeneidade.

Tabela candidatos_quarentena: alternativas GAEZ baixoinsumo/índices com flags; PAM histórico1991–2000 e flags de seleção/geografia; multas/autos temáticos informados/espaciais e respectivos flags/status/defasagens; estoques/participações de usos, rebanho/lotação e flags. Valores brutos mantidos com prefixo cand__ e acesso separado. Criar visões de elegibilidade temática de autos/multas apenas quando flags explicitamente completas, sem chamar isso efetividade, pagamento ou integridade total da fonte. Não incorporar embargos GM sem reconstrução verificável.

## Faltantes e zeros

Não imputar médias/medianas/zeros, não ffill/bfill/interpolar, não winsorizar. Preservar zero registrado e distinguir faltante/não finito/negativo. Zero de produção ou rendimento não comprova ausência estrutural da atividade; zero cartográfico não comprova conservação intencional; zero autos não comprova ausência de infração. Não certificar ausência de imputação na cadeia anterior sem fonte bruta. Flags de amostra indicam elegibilidade do registro, não removem linhas do mestre. Filtros de derivadas não modificam colunas originais.

Sem log de zero, receitas potenciais, lucro/margem fabricados ou conversão matéria seca→comercial. GAEZ é capacidade potencial, rendimento PAM é realizado e endógeno, custos não disponíveis. Rendimento lag1 usa apenas ano consecutivo observado; não redefine preços já lag1. Não calcular novas médias históricas com dados do futuro. Valores institucionais elegíveis permanecem candidatos por endogeneidade/cobertura/status.

## Produtos e testes

CSV e Parquet se engine disponível; script reproduzível; dicionário por coluna (origem,unidade,temporalidade,camada,cobertura e risco causal); manifestos SHA e joins; auditoria de faltantes/zeros por variável,ano,município,bioma; flags amostrais; comparação integral das colunas originais; tabelas de pendências e quarentena; logs e validação independente. Arquivos agregados volumosos podem ser CSV.gz determinísticos. Execução duas vezes e comparação de hashes de tabelas; sem regressões nem kernels anteriores. Proteger fontes/textos/rodadas1–7 por SHA. Dados derivados na base2, logs técnicos também em2_INTI/audit/base2.
