# Experimentos econométricos de H1 — execução local

O CSV solicitado chegou em `origin/main` no commit `7ff33b9a5bef1d727aafd9defe3a8241599ba58c`: 3.384 linhas, 70 colunas, 141 municípios e 2001–2024. SHA-256: `bc396a4f394ae60d6883205f2ca6e8d33b59a4fb419fc5d667591374c8f1c730`. Não foi utilizado painel substituto. Os dados e textos originais foram preservados.

Foram executados 24 ajustes, sem seleção por p-valores, em sete notebooks. Consulte `SINTESE.md` e `modelos_resumo.csv` para resultados, amostras e limitações; `modelos_coeficientes.csv` contém todos os 220 coeficientes, inclusive interceptos e controles de bioma/ano. Esses experimentos são associativos e não substituem uma estratégia validada da tese. `3_econometrics_strategy.tex` continua sendo placeholder, sem alterações.

## Ordem de execução e grade

| Notebook | Conteúdo | Ajustes |
|---|---|---:|
| auditoria.ipynb | Chaves, distribuição, taxas, suporte, faltantes e absorção | 0 |
| ols_simples.ipynb | Soja→agricultura; boi→pastagem, associações brutas | 2 |
| ols_multiplo.ipynb | M01: preços/aptidões/bioma; M01C: mesma fórmula na amostra M02; M02: adiciona fiscalização | 6 |
| painel.ipynb | P01: FE municipal; P02: TWFE com exposições; P03: adiciona preço soja×fiscalização | 6 |
| alternativas.ipynb | Q01: PPML hectares; F01: logit fracional; FE ano/bioma | 4 |
| quebras_temporais.ipynb | ITS 2007, 2013 e placebo 2010, cada destino | 6 |
| avaliacao_desenho.ipynb | RDD/DiD não identificados com a informação disponível | 0 |

A grade original de 22 ajustes foi acrescida de duas repetições M01C antes das estimações para separar alteração de amostra da inclusão de fiscalização. Nenhuma busca de melhores cortes, controles, transformações ou significâncias. Sensibilidades de covariância não constituem novos modelos substantivos. Não foram estimadas regressões por bioma: Pantanal tem suporte insuficiente.

## Variáveis e amostras

As fórmulas ficam visíveis nos notebooks. `utilitarios.py` concentra leitura, filtros, padronização, ajuste e exportação. `dicionario_alias.csv` relaciona nomes reais do CSV e nomes curtos. As VDs são conversão bruta em hectares e taxas por destino; não são perda líquida nem mudança entre pastagem e lavoura. Taxas são frações de vegetação nativa inicial; modelos lineares usam pontos percentuais, logit fracional usa [0,1]. Estoque inicial é endógeno à trajetória de conversão.

Os preços reais em USD2024 são médias anuais já defasadas no CSV. Grãos são cotados por tonelada, carne por kg. Não houve uma segunda defasagem. Preços são padronizados sobre 24 valores anuais, aptidões sobre 141 municípios (média e desvio populacional registrados em `escalas.csv`). Não há log de conversão, log de zero ou winsorização. O produto preço padronizado×aptidão padronizada mede exposição diferencial, não receita comercial por hectare.

GAEZ soja/milho mede kg de matéria seca/ha, com clima 1961–1990 e terras de 2010; não assegura predeterminação. Rendimento PAM não foi usado como aptidão. Não existe aptidão pecuária validada: a exposição agrícola na equação de pastagem é associação cruzada de usos, não produtividade da pecuária.

Fiscalização usa autos Flora válidos, flag parcial explicitamente falsa, defasados em um ano consecutivo e divididos por 10. Valores ausentes e contagens parciais não viram zero. A fiscalização é endógena; defasagem não elimina resposta às infrações. Nenhuma medida de autuação é tratada como efetividade institucional.

Há 2.772 pares de conversão válidos, em 137 municípios. Agricultura tem 265 zeros; pastagem não tem zeros na amostra válida. Os modelos com fiscalização usam 1.140 observações, 128 municípios e 23 anos. As perdas por variável são exportadas sequencialmente, sem contagem duplicada, em `amostras_perdas.csv`. Comparação M01C/M02 e P01/P02/P03 usa as mesmas observações por destino. A amostra fixa das ITS tem 95 municípios (39 Amazônia, 55 Cerrado e 1 Pantanal).

Bioma é predominância municipal, não localização de cada conversão. O CSV não contém flags completas da integridade dos pares MapBiomas nem séries mensais de preços: consistência interna e invariância são verificadas, mas a auditoria não reconstrói cobertura geográfica original, deflação ou alinhamento temporal a partir das fontes primárias. Essas limitações não são corrigidas silenciosamente.

## Inferência, absorção e diagnósticos

OLS, painel e GLM usam agrupamento município/ano, com correções de amostra dos respectivos estimadores e referência t com min(G_mun,G_ano)−1 graus de liberdade. Também são exportados SE com cluster municipal. Há apenas 23–24 anos; inferência assintótica continua frágil. Clustering não elimina viés, tendências omitidas, dependência espacial geral ou choques comuns serialmente correlacionados. Não há correção por múltiplos testes; não interpretar resultados isolados como confirmação de H1.

A covariância two-way bruta foi não positiva semidefinida em cinco modelos (quatro GLM e P03 agricultura). Aplicou-se projeção espectral, zerando autovalores negativos, determinada pelo diagnóstico, não pelo p-valor. Matrizes brutas estão em `cov_bruta_*.csv`, SE brutos na coluna `se_two_way_bruto` (ausente quando a variância bruta é negativa), e a coluna `cov_correcao` identifica o ajuste. SE, IC e p principais usam a matriz corrigida; os efeitos marginais usam a mesma regra. A correção não valida o desenho nem resolve poucos clusters; a forte diferença entre covariâncias é parte da incerteza. Referência: [Cameron e Miller, guia de inferência com clusters](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf) e [documentação técnica de vcovCL](https://sandwich.r-forge.r-project.org/reference/vcovCL.html), consultadas em 23/10/2026.

Sob TWFE, preços comuns anuais são absorvidos pelo FE de ano; aptidões e bioma invariantes pelo FE municipal. A auditoria faz projeções alternadas até convergência no painel desbalanceado e verifica a variação residual das interações. Esses termos absorvidos não são reportados como efeitos identificados. P03 inclui fiscalização e preço×fiscalização, além das exposições; preço isolado fica absorvido. Todos os ajustes têm posto completo nas variáveis identificadas. O R² do painel é do modelo transformado por FE; não é comparável diretamente ao R² pooled.

PPML/logit fracional incluem ano e bioma, não FE municipal. Convergência, predições finitas, extremos, resíduos e ajuste são registrados. Convergência e coeficientes finitos não são prova formal de ausência de separação nem de especificação correta. Pseudo-ajuste reportado é 1−deviance/null_deviance, distinto de R². `marginais_*.csv` apresenta o componente diferencial médio de um aumento de 1 DP de preço via aptidão; o efeito comum do preço é absorvido por ano. Esses efeitos não incluem uma resposta agregada ao choque comum identificada separadamente.

## Políticas, ITS e inviabilidade de RDD

A Moratória começou em 24/07/2006; a data-limite de desmatamento foi posteriormente alinhada a 22/07/2008. Abrange soja no bioma Amazônia. Fonte oficial: [requerimento do Senado](https://legis.senado.leg.br/sdleg-getter/documento?disposition=inline&dm=9955925&ts=1750773421654). Esse documento sustenta o contexto, não uma estimativa causal.

O Código Florestal é a [Lei 12.651 de 25/05/2012](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12651.htm). O art. 3, IV, usa 22/07/2008 na definição de área rural consolidada. Isso não transforma ano municipal em variável de atribuição quase aleatória. Amazônia Legal difere do bioma Amazônia.

O [PPCDAm começou em 2004](https://www.fundoamazonia.gov.br/pt/fundo-amazonia/politicas-publicas-orientadoras/); a janela teria apenas três anos anteriores. PPCDAm/DETER são políticas concorrentes à Moratória. Terra Legal (2009) e Paris (2015) aparecem na revisão, mas não foram convertidos automaticamente em tratamentos adicionais. Fontes consultadas em 23/10/2026.

ITS usam razão entre somas de hectares e estoque inicial na amostra fixa, tendência linear, mudança de nível e inclinação. Primeiro ano completo pós-Moratória: 2007, omitindo 2006; pós-Código: 2013, omitindo 2012. Placebo predefinido em 2010 é comparação de segmentação, não período comprovadamente sem intervenção. SE HAC lag 1, com lag 2 exportado como sensibilidade, e t com N−K graus de liberdade. Políticas concorrentes, antecipação e poucos anos impedem atribuição causal; a série estadual tampouco isola o bioma tratado.

Não existe running variable/regra de atribuição/cutoff válido verificado no CSV; não foi criado `rdd.ipynb` estimado. Frações de bioma e conversão agrícola agregada não demonstram exposição municipal à Moratória. Não há controle plausível validado; deslocamento para Cerrado, diferenças de tendências e antecipação impedem tratar biomas como grupos DiD automaticamente. DiD/event study não foram estimados. Essas decisões estão no notebook de avaliação.

## Reprodução e verificação

Na raiz do repositório, com Python 3.12:

```bash
python -m venv /tmp/chap1-env
/tmp/chap1-env/bin/pip install --index-url https://pypi.org/simple -r 2_INTI/chapters/chap1/stats/modelos/testes_chap1/requirements.txt
/tmp/chap1-env/bin/python 2_INTI/chapters/chap1/stats/modelos/testes_chap1/executar_tudo.py
```

O executor abre kernels novos, executa todas as células, valida notebooks e consolida CSVs e síntese. Deve ser executado com o CSV exato no diretório pai. Semente 20261023 registrada; não há simulação aleatória na estimação. Dependências ficam fora do repositório. Arquivos por modelo permitem rastreio; arquivos consolidados são a entrada recomendada para revisão.

Logs, hashes dos textos e CSV, versões, validação e histórico ficam em `2_INTI/audit/testes_chap1_20261023`. A preparação anterior à chegada do CSV foi preservada em `antes_csv/`. O script `reproduzir_avaliacao.py` antigo foi substituído por um redirecionamento ao executor completo; use `executar_tudo.py`.

O usuário autorizou commit e push diretamente para main em 23/10/2026. O pacote de resultados e os logs finais foram selecionados explicitamente para versionamento, sem caches ou ambientes de dependências e sem alterar o `.gitignore`. O histórico do Git registra o commit de publicação. Antes do empacotamento, foram incorporadas por fast-forward as alterações do usuário até `7714c75e77fd2bb20b3666feaa0e0ccac0b924a3`; o CSV permaneceu idêntico.
