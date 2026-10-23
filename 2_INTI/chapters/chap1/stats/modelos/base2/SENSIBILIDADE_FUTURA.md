# Proposta futura — tratamentos de faltantes e zeros

Somente planejamento; nenhum tratamento imputado ou regressão executado nesta construção. Comparações propostas são sensibilidades de mensuração/amostra, não contrafactuais causais identificados. Não há método que garanta ausência de viés independentemente das hipóteses.

## Primeiro: distinguir estados e mecanismos

- Zero registrado: manter inicialmente. Conversão zero pode indicar nenhum pixel de transição observado, não conservação deliberada; PAM zero não certifica ausência estrutural da atividade; autos zero não prova ausência de infração.
- Faltante por cobertura cartográfica: flags do PT identificam612 pares incompletos, associados às612 ausências do desfecho. Não imputar conversão automaticamente. Recuperar fonte/mapa seria preferível se autorizado em etapa própria.
- Faltante de fonte/produção: distinguir símbolo SIDRA, não divulgação, não ocorrência e falta de registro apenas quando documentação individual permitir. O painel atual não retém todos esses motivos; não recodificar todos como zero.
- Registro institucional parcial: conservar bruto e flag; somente completude temática não garante cobertura geral. Não imputar autos parciais ou tratar seu valor parcial como total verdadeiro.
- Valor inválido: registrar violação concreta de domínio/unidade/denominador; não transformar em zero. Valores negativos podem ser válidos em variações/anomalias, portanto não eliminar genericamente.
- Zero estrutural e censura: somente classificar quando há evidência externa/documental; não foram certificados globalmente nesta base. Não presumir que todo zero é estrutural nem que todo faltante é censura.

## Comparações admissíveis a predefinir antes dos próximos ajustes

1. Referência de casos completos por especificação, perdas por motivo e suporte municipal/ano/bioma. Comparar equações na mesma amostra e na amostra ampliada para separar composição de transformação, como na rodada2.
2. Preservar zeros nos modelos adequados a desfechos não negativos/fracionais; modelos de ocorrência e positivos respondem a perguntas diferentes e devem ser explicitados. Não log(y+1) automático, não troca de zeros por valor pequeno.
3. Investigar padrões de ausência e associações com covariáveis observadas, sem decretar MCAR/MAR/MNAR por testes simples. A escolha exige argumento sobre coleta e seleção; ausência não aleatória é plausível em produção e fiscalização.
4. Se imputação múltipla de covariáveis vier a ser justificada, especificar antes: quais variáveis, mecanismo suposto, limites/domínios, estrutura municipal e temporal, interações, blocos de bioma, conjuntos de treinamento/validação quando aplicável, número de imputações e combinação da incerteza. Manter valores observados intactos, máscaras e identificador da imputação. Não aplicar média/mediana como correção automática; isso pode distorcer variância e relações.
5. Não imputar automaticamente o desfecho, registro institucional parcial, zero estrutural ou atributo territorial. Valores auxiliares escolhidos precisam respeitar temporalidade; não usar futuro para definir expectativa anterior ou escapar de perda por defasagem.
6. Ponderação por observabilidade ou análises de seleção só com justificativa de modelo/positividade e avaliação de suporte; não prometem resolver MNAR. Sensibilidades a desvios das hipóteses devem ser previstas quando viáveis, sem inventar limites substantivos.
7. Comparar coeficientes, magnitudes, IC, perda/amostra efetiva e testes formais pertinentes, não escolher o tratamento pelo menor p. Declarar famílias de multiplicidade e caráter exploratório adaptativo.

O objetivo é avaliar quanto as conclusões dependem de hipóteses explícitas sobre mensuração e seleção. Isso pode fortalecer a transparência e delimitar robustez, sem transformar associação em causalidade ou garantir resultados sem viés.
