# Síntese dos experimentos executados

Foram estimados 24 modelos, com todos os resultados preservados, incluindo associações compatíveis com zero e de sinais contrários. A informação disponível não identifica causalidade nem permite uma decisão isolada de confirmar/rejeitar H1.

## Dados e seleção

3.384 pares na grade, 2.772 conversões válidas em 137 municípios. A inclusão de fiscalização defasada reduz a amostra a 1.140 pares em 128 municípios (23 anos). M01C e M02 compartilham a amostra; P01–P03 também. A cobertura não é aleatória. Pantanal: quatro municípios na grade e apenas um na amostra fixa; sem regressões próprias. Os 265 zeros agrícolas foram mantidos. O CSV não permite reconstruir a validade geográfica dos mapas ou as médias mensais de preços.

## O que os ajustes mostram

OLS simples associa preços mais elevados a menores taxas de conversão; tendências e omissões impedem interpretar isso como resposta causal. OLS múltipla e sua versão em amostra comum mostram que acrescentar fiscalização muda também quais observações são utilizáveis. As tabelas preservam as duas comparações.

No TWFE P02, as exposições soja×aptidão e milho×aptidão da agricultura têm IC que incluem zero. Na pastagem, a exposição soja×aptidão é positiva com intervalo próximo de zero; ao acrescentar preço×fiscalização (P03), seu IC passa a incluir zero. Isso evidencia sensibilidade à especificação, não prova de ausência ou presença do mecanismo. A associação positiva das autuações com conversão agrícola pode refletir resposta às infrações, e não efeito de fiscalização aumentando conversão.

PPML e logit fracional preservam zeros e a escala apropriada, mas não incluem FE municipal; não são testes equivalentes ao TWFE. Hectares, frações e suas ligações respondem a perguntas diferentes. As quatro covariâncias GLM precisaram de correção PSD; comparar com SE brutos e cluster municipal e evitar inferência forte. Efeitos marginais são apenas o componente diferencial por aptidão, sem efeito comum anual identificado.

As ITS estimam queda de nível na segmentação pós-2006 e mudança positiva na segmentação pós-2012, mas as séries estão sujeitas a políticas concorrentes, antecipação e tendência. O placebo 2010 também apresenta mudanças de inclinação. Nenhuma dessas estimativas mede o efeito causal da Moratória ou do Código Florestal. Não houve RDD, DiD ou event study estimado.

## Grade integral e amostras

ITS têm 95 municípios agregados, não 95 clusters independentes do choque temporal. Seus N são anos, e clusters ficam em zero porque a inferência usa HAC. R² de OLS, R² transformado de painel e pseudo-ajuste GLM não são critérios intercambiáveis de seleção.

| id | N | municipios | clusters_ano | ajuste_tipo | ajuste | cov_correcao |
| --- | --- | --- | --- | --- | --- | --- |
| F01_agricultura | 2772 | 137 | 24 | 1-deviance/null_deviance | 0.3222 | PSD espectral |
| F01_pastagem | 2772 | 137 | 24 | 1-deviance/null_deviance | 0.3501 | PSD espectral |
| M01C_agricultura | 1140 | 128 | 23 | R2 | 0.0396 | nenhuma |
| M01C_pastagem | 1140 | 128 | 23 | R2 | 0.0655 | nenhuma |
| M01_agricultura | 2772 | 137 | 24 | R2 | 0.0562 | nenhuma |
| M01_pastagem | 2772 | 137 | 24 | R2 | 0.1272 | nenhuma |
| M02_agricultura | 1140 | 128 | 23 | R2 | 0.0404 | nenhuma |
| M02_pastagem | 1140 | 128 | 23 | R2 | 0.0681 | nenhuma |
| P01_agricultura | 1140 | 128 | 23 | R2 transformado FE | 0.0276 | nenhuma |
| P01_pastagem | 1140 | 128 | 23 | R2 transformado FE | 0.0124 | nenhuma |
| P02_agricultura | 1140 | 128 | 23 | R2 transformado FE | 0.0041 | nenhuma |
| P02_pastagem | 1140 | 128 | 23 | R2 transformado FE | 0.0122 | nenhuma |
| P03_agricultura | 1140 | 128 | 23 | R2 transformado FE | 0.0047 | PSD espectral |
| P03_pastagem | 1140 | 128 | 23 | R2 transformado FE | 0.0141 | nenhuma |
| Q01_agricultura | 2772 | 137 | 24 | 1-deviance/null_deviance | 0.3796 | PSD espectral |
| Q01_pastagem | 2772 | 137 | 24 | 1-deviance/null_deviance | 0.3216 | PSD espectral |
| S01_agricultura | 2772 | 137 | 24 | R2 | 0.0185 | nenhuma |
| S01_pastagem | 2772 | 137 | 24 | R2 | 0.0364 | nenhuma |
| T01_agricultura | 23 | 95 | 0 | R2 | 0.8011 | nenhuma |
| T01_pastagem | 23 | 95 | 0 | R2 | 0.8635 | nenhuma |
| T02_agricultura | 23 | 95 | 0 | R2 | 0.6133 | nenhuma |
| T02_pastagem | 23 | 95 | 0 | R2 | 0.696 | nenhuma |
| T03_agricultura | 24 | 95 | 0 | R2 | 0.6109 | nenhuma |
| T03_pastagem | 24 | 95 | 0 | R2 | 0.6949 | nenhuma |

## Coeficientes TWFE de interesse

Taxas em pontos percentuais; exposições usam preço e aptidão em DP; fiscalização representa 10 autos anteriores válidos. IC95 e p usam covariância two-way com correção PSD quando necessária e t com 22 graus de liberdade. Sem ajuste de multiplicidade; nenhum modelo foi escolhido pelo p-valor.

| id | termo | coef | ic95_inf | ic95_sup | p |
| --- | --- | --- | --- | --- | --- |
| P02_agricultura | expo_soja | 0.00773 | -0.00848 | 0.02395 | 0.33338 |
| P02_agricultura | expo_milho | 0.00269 | -0.0033 | 0.00868 | 0.36225 |
| P02_agricultura | fiscal | 0.00625 | 0.00149 | 0.01101 | 0.01236 |
| P02_pastagem | expo_soja | 0.06863 | 0.00025 | 0.13701 | 0.04925 |
| P02_pastagem | expo_milho | 0.05713 | -0.02735 | 0.14161 | 0.17472 |
| P02_pastagem | fiscal | 0.0087 | -0.01539 | 0.03279 | 0.4619 |
| P03_agricultura | expo_soja | 0.00987 | -0.00935 | 0.02908 | 0.29839 |
| P03_agricultura | expo_milho | 0.00235 | -0.0032 | 0.0079 | 0.38896 |
| P03_agricultura | fiscal | 0.00618 | 0.00145 | 0.01091 | 0.01276 |
| P03_agricultura | preco_fiscal | 0.00348 | -0.0052 | 0.01217 | 0.41434 |
| P03_pastagem | expo_soja | 0.05192 | -0.02614 | 0.12998 | 0.18165 |
| P03_pastagem | expo_milho | 0.05977 | -0.024 | 0.14355 | 0.15311 |
| P03_pastagem | fiscal | 0.00924 | -0.01395 | 0.03243 | 0.41765 |
| P03_pastagem | preco_fiscal | -0.02725 | -0.06822 | 0.01371 | 0.18155 |

## Entregáveis e verificação

`modelos_coeficientes.csv`: 220 coeficientes, SE/IC/p, interpretação, alertas, ajustes e metadados. `modelos_resumo.csv`: 24 ajustes. `amostras_perdas.csv`: exclusões sequenciais. `marginais_*.csv`: efeitos diferenciais GLM. `auditoria_*.csv`: distribuição, suporte, taxa e absorção. `sensibilidade_*.csv`: cluster municipal ou HAC lag2. `cov_bruta_*.csv`: matrizes anteriores à correção PSD.

A correção PSD foi necessária em cinco ajustes; não foi acionada por significância. Os 90 SE brutos associados a variâncias negativas permanecem ausentes nessa coluna, com alerta; os SE principais corrigidos são finitos. Dados, textos e demais arquivos rastreados foram preservados. Os sete notebooks foram executados integralmente em kernels novos, e N, perdas, amostras comuns, coeficientes e hashes foram conferidos. Logs e versões: `2_INTI/audit/testes_chap1_20261023`.

Commit e push para main autorizados pelo usuário em 23/10/2026. Consulte o histórico do Git para a publicação do pacote. Limitações metodológicas e fontes oficiais estão em LEIA_ME.md. A estratégia .tex não foi validada nem alterada.

## Pergunta sobre significância

7 de 52 coeficientes de preços, fiscalização e interações têm p<0,05 na inferência principal, sem correção por múltiplas comparações. Não inclui interceptos, dummies FE, aptidões isoladas ou quebras temporais. O arquivo resultados_H1.csv preserva todo o recorte, inclusive resultados não significativos. A coluna p_sensibilidade usa cluster municipal. Nenhum desses resultados, isoladamente, confirma H1 ou causalidade.

| id | termo | coef | se | ic95_inf | ic95_sup | p | N | cov_correcao | p_sensibilidade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F01_pastagem | expo_soja | 0.072318 | 0.033066 | 0.003915 | 0.140721 | 0.039166 | 2772 | PSD espectral | 0.007351 |
| M01_pastagem | z_p_boi | -0.234461 | 0.103951 | -0.449499 | -0.019423 | 0.033919 | 2772 | nenhuma | 0.0 |
| P02_agricultura | fiscal | 0.006249 | 0.002293 | 0.001493 | 0.011005 | 0.012363 | 1140 | nenhuma | 0.079752 |
| P02_pastagem | expo_soja | 0.068627 | 0.032972 | 0.000247 | 0.137008 | 0.049246 | 1140 | nenhuma | 0.036062 |
| P03_agricultura | fiscal | 0.006181 | 0.00228 | 0.001453 | 0.010908 | 0.012758 | 1140 | PSD espectral | 0.079327 |
| Q01_agricultura | expo_soja | 0.062691 | 0.030116 | 0.000391 | 0.124991 | 0.048694 | 2772 | PSD espectral | 0.117114 |
| S01_pastagem | z_p_boi | -0.272611 | 0.106569 | -0.493065 | -0.052158 | 0.01758 | 2772 | nenhuma | 0.0 |
