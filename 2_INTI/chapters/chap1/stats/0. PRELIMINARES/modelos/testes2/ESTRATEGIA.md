# Rodada 2 — protocolo anterior à execução

Objetivo: discriminar composição amostral, condicionamento institucional observado, escala da VD e heterogeneidade municipal. Não aceitar/rejeitar H1 pelo p-valor. Esta rodada é planejada a partir dos diagnósticos exploratórios da rodada1; não é uma análise confirmatória independente. Dados e textos originais, bem como testes_chap1, serão preservados. Sem commit/push/publicação.

## Auditoria e temporalidade

CSV exato do diretório pai; registrar SHA256, commit e hashes dos textos. Verificar IDs, unicidade, anos, faltantes, taxa=ha/estoque inicial, taxas em [0,1], estoque positivo, preço positivo e constante no ano, aptidão constante por município. O lag1 do preço já corresponde a t−1; não defasar de novo. Fontes mensais não estão no arquivo: alinhamento original/deflação não verificáveis integralmente. GAEZ incorpora terras de 2010 e não é estritamente predeterminado. Fiscalização: somente flag parcial falsa, lag de um ano consecutivo, por dez autos; nenhuma imputação. Bioma predominante não localiza conversão. Auditar perda de suporte, unidades e amostras; não forçar Pantanal.

## Estimandos e grade finita

Cada equação separa agricultura e pastagem, salvo a diferença direta.

1. A01: taxa em pp ~ preço soja×aptidão soja + preço milho×aptidão milho + FE município/ano, amostra ampla (2 ajustes). Preços e aptidões em z na mesma escala da rodada1.
2. A02: mesma equação, somente amostra com fiscalização válida (2). Comparação A01/A02 isola composição; A02/A03 isola associação condicional adicional.
3. A03: A02 + fiscalização lag1 (2).
4. A04: A03 + preço soja×fiscalização lag1 (2). Não tratar autos como efetividade institucional. Termo direto de preço é absorvido por FEano; todas aptidões/biomas invariantes por FEmuni.
5. A05: substituir exposições por log(preço grão/(1000×preço boi)) padronizado × aptidão do grão (2). Converte carne USD/kg para USD/t antes da razão. É contraste de incentivos relativos, não teste da transição pastagem→lavoura, ausente no CSV. Não inventar aptidão pecuária.
6. D01: VD=(taxa pastagem−taxa agricultura) em pp, mesma amostra/FE/exposições de A01 (1). Os coeficientes são diferenças formais dos coeficientes por destino; a covariância é estimada dos resíduos da diferença, não supondo independência entre atividades. Teste conjunto de ambas diferenças.
7. Q01: PPML hectares ~ exposições + FE município/ano (2). Q02: mesmo modelo com offset log(estoque inicial) (2). F01: logit fracional taxa ~ exposições + FE município/ano (2). Todos na amostra comum que exclui explicitamente municípios com somatório zero em qualquer destino ou séries de apenas uma observação, caso existentes; registrar perdas. Se essa amostra diferir da A01, incluir G00 linear nela (2 condicionais).

Total 17 ajustes planejados, até 19 se G00 necessário. Não acrescentar modelos por resultados de significância. PPML sem offset mede hectares; com offset modela a intensidade sob elasticidade unitária imposta ao estoque e ponderação distinta; estoque é endógeno, logo não há efeito causal do denominador. Logit fracional é QMLE com FE, sujeito a viés de parâmetros incidentais com T curto; não usar logit condicional para dados fracionais. Avaliar separação, convergência, predições, scores, Hessiana, número de observações por município; não interpretar simplesmente concordância de sinais como equivalência entre estimandos.

## Inferência definida antes dos resultados

Principal: sandwich HAC dos scores agregados por ano, Bartlett lag 2 (Driscoll–Kraay para linear), com ajuste N/(N−Ktotal), referência t com T−1 g.l. Ktotal inclui FE identificados. Para GLM, usar scores e Hessiana do QMLE. Sensibilidades: lag 1 e lag 3; cluster municipal CR1; two-way município/ano bruto (sem projetar silenciosamente para PSD; IC indisponíveis se variância negativa). Não escolher pelo p. DK é assintótico em T; 23–24 anos não asseguram boa cobertura, e todos os resultados são condicionais/exploratórios.

Testes conjuntos de ambas exposições: Wald F(q,T−1), somente quando a submatriz é definida positiva e de posto pleno. Holm na família primária A01 (4 coeficientes); Holm separado para diferença D01 (2) e para todos coeficientes substantivos das sensibilidades (inclui fiscais); Holm separado para os testes conjuntos por modelo. Sempre exportar p bruto e ajustado, IC95 e número de testes por família. Não inferir equivalência com p>0,05: não há limiar de irrelevância econômica previamente justificado.

Magnitude linear: diferença na resposta entre aptidão P75 e P25 para alta de preço igual a 10% de sua média real, incluindo IC. É cenário transparente, não margem de equivalência. GLM: mudança média prevista na taxa/ha para esse mesmo choque diferencial, com delta method; FE ano mantido, portanto não inclui resposta comum ao choque absorvida pelo ano.

Fontes técnicas: https://bashtage.github.io/linearmodels/panel/panel/linearmodels.panel.covariance.DriscollKraay.html ; https://www.statsmodels.org/devel/pitfalls.html ; https://pages.stern.nyu.edu/~wgreene/nonlinearfixedeffects.pdf (consulta 23/10/2026). A implementação será confrontada com PanelOLS em pelo menos um ajuste linear.

## Decisão após a rodada

Classificar cada implicação como suporte associativo, evidência de sinal contrário, imprecisão ou não identificação; não transformar classificação estatística em causalidade. Questões subsequentes admissíveis: dinâmica temporal/GAEZ-2010, tendências e biomas; depois influência, suporte, zeros e não linearidades se ainda relevantes. Estratégia da próxima rodada será escrita antes de suas estimações. Parar quando os caminhos admissíveis não redundantes tiverem sido investigados ou limitações dos dados impedirem discriminar H1, e não ao alcançar p baixo. Nenhuma lista de modelos pode provar que todas as especificações matemáticas foram esgotadas.
