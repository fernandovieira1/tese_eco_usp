# Base3 v4 — receitas brutas estimadas e defasagens

Entrega: **3.384 linhas, 141 municípios, 2001–2024 e 70 colunas**. As 54 colunas da v3 publicada permanecem com valores, nomes e ordem idênticos. Acrescentamos 16 campos do grupo 2: duas culturas × duas medidas × quatro versões. Nenhuma regressão, imputação, nova cultura ou custo. A publicação deste lote v4 foi autorizada separadamente; outros trabalhos locais não integram a entrega.

## Estratégia, fórmulas e nomes

A estratégia foi registrada em [ESTRATEGIA_V4.md](ESTRATEGIA_V4.md) antes da construção. Para cada município, cultura e ano t:

- Receita total: `R(t) = P(t) × produção_toneladas(t)`, em USD2024.
- Receita por hectare colhido: `Rha(t) = R(t) / área_colhida_ha(t)`, somente com denominador positivo, em USD2024/ha colhido.
- Lag1: receita do mesmo município em t−1; lag2: em t−2. Busca por ano exato, nunca pelo deslocamento cego das linhas.
- Média: `(lag1 + lag2) / 2`, somente quando ambos estão disponíveis, incluindo zeros observados.

Preço P(t) é a média dos 12 preços mensais internacionais contemporâneos em USD/t, após deflação de cada mês pelo CPI-U (base média de 2024). **Não usamos o preço lag1 da base para multiplicar a produção do próprio ano.** As receitas são calculadas primeiro e depois defasadas. A receita por hectare usa área colhida, não área plantada.

Padrão dos nomes, com `cultura = soja ou milho`:

| Medida | Contemporânea | Versões históricas |
|---|---|---|
| Total | `2_receita_bruta_estimada_usd2024_total__cultura` | `_total_lag1__cultura`, `_total_lag2__cultura`, `_total_media_lag1_lag2__cultura` |
| Por hectare | `2_receita_bruta_estimada_usd2024_por_ha_colhido__cultura` | `_por_ha_colhido_lag1__cultura`, `_por_ha_colhido_lag2__cultura`, `_por_ha_colhido_media_lag1_lag2__cultura` |

As terminações na terceira coluna complementam o mesmo prefixo `2_receita_bruta_estimada_usd2024`. O [dicionário completo](BASES_PARA_USO/DICIONARIO.csv) registra todos os 70 nomes e o [adendo](dicionario_adendo_v4.csv), os 16 novos, fórmulas e origens. Nenhuma coluna anterior foi renomeada.

## Auditoria das fontes e do calendário

Fonte municipal: v3 no commit `0a2cd309ab6b724ccd9266a54deb0f086843e3b9`, hash congelado no manifesto. Produção e área colhida PAM são as já auditadas na v3.

Preços: XLSX Pink Sheet e CPI-U já incluídos em `fontes_v2`, com hashes verificados. Foram obtidos 288 meses por cultura em 2001–2024, sem duplicatas e com valores positivos/finito. A regra mensal reproduz os preços contemporâneos do painel PT existente; o extrato de conferência de 24 anos, seu hash e a origem ficam em `fontes_v4`. O PT é uma conferência local derivada da mesma fonte, não evidência independente de preços recebidos.

**2024 está disponível:** 12 meses de soja e milho. Dois leitores independentes (OOXML e openpyxl) concordam nas 576 células de 2001–2024. Preço real médio contemporâneo de 2024: soja aproximadamente USD2024 462,713236/t; milho 190,618649/t. O confronto externo com o XLSX oficial documentado anteriormente cobre até 2023; 2024 foi conferido localmente em dois leitores e PT, sem novo confronto externo oficial. Não se atribui ao novo ano uma certificação não realizada.

**Produção anterior a 2001:** não encontrada em tabela local já harmonizada. As bases municipais publicadas e o PT começam em 2001. Não reconstruímos produção por diferenças anuais, não fizemos backfill e não usamos informação futura para preencher bordas. Consequências: lag1 em 2001 e lag2/média em 2001–2002 são NA. Obter esses valores exigiria recuperar e harmonizar a PAM histórica, inclusive limites territoriais; não é necessário para a presente entrega com ausência explícita.

A auditoria é registrada antes do painel em [auditoria_pre_construcao_v4.json](auditoria_pre_construcao_v4.json). As tabelas mensais e anuais auxiliares mantêm nomes de metadados, sem confundi-los com os campos finais do grupo 2.

## Identidades e cobertura

A identidade receita total/área colhida é exata, salvo aritmética de ponto flutuante. Também comparamos receita por hectare com `P(t) × rendimento_informado_kg_ha(t) / 1000`. Como o rendimento é informado em unidades inteiras, admitimos a precisão já auditada de 1 kg/ha, convertida para USD2024/ha por `P(t)/1000`, mais tolerância numérica. Nenhum caso excedeu esse limite. Máximas diferenças: soja 0,75830 USD2024/ha e milho 0,31798 USD2024/ha. O rendimento original não foi alterado.

Contagens válidas — iguais para receita total e por hectare nesta base:

| Cultura | Contemporânea | Lag1 | Lag2 | Média estrita lag1/lag2 |
|---|---:|---:|---:|---:|
| Soja | 2.615 | 2.484 | 2.356 | 2.295 |
| Milho | 3.318 | 3.178 | 3.040 | 3.020 |

O complemento de cada contagem até 3.384 é ausência. Não há zeros observados nas receitas deste recorte, pois a fonte produtiva observada não contém zeros; o algoritmo preserva zeros legítimos, testados em casos sintéticos. Faltas de produção/área e bordas temporais são propagadas. A média exige os dois lags, não usa somente um. Nenhuma linha foi removida. A [cobertura por campo e ano](cobertura_receitas_v4.csv) mostra também municípios válidos e zeros.

## Limitações econômicas

São **receitas brutas internacionais de referência**, não receitas efetivamente recebidas pelos produtores, lucro ou margem. Não contemplam preço local, câmbio, custos, qualidade, frete ou calendário real de comercialização. O total mistura escala e preço; por hectare reduz a escala, mas continua refletindo diferenças de produtividade e composição produtiva.

Receitas contemporâneas podem responder à conversão. Seus lags e a média são proxies retrospectivas de informação, não medidas observadas das expectativas nem garantia de exogeneidade. Usar defasagens não resolve simultaneidade histórica, seleção ou confundimento. Os vintages são retrospectivos; a escala monetária de 2024 não equivale à informação disponível ao produtor no passado. Os testes garantem que os lags não utilizam meses ou receitas posteriores ao seu ano de referência, não que todos os dados sejam vintages em tempo real.

Não somar as áreas de soja e milho como terra física única. Rendimento observado não é GAEZ. Novas regressões devem distinguir estimandos e amostras; não selecionar lag1, lag2 ou média pela significância posterior.

## Reprodução

Construção e testes: Python >=3.9, somente biblioteca padrão, com o leitor OOXML publicado em `construir_base3_v2.py`. Fontes: v3, dicionário v3, XLSX/CPI de `fontes_v2` e extrato de conferência em `fontes_v4`. Não requer complementos CONAB ou dados GM.

```bash
python 2_INTI/chapters/chap1/stats/modelos/base3/construir_base3_v4.py
python 2_INTI/chapters/chap1/stats/modelos/base3/testar_base3_v4.py
```

O [notebook executado](construcao_receitas_v4.ipynb) tem seis seções numeradas, explicações, auditoria de cobertura e testes. Para reexecutá-lo, usar Jupyter com `nbformat`, `nbclient` e `ipykernel` (versões em `ambiente_v4.json`); dependências foram instaladas somente em ambiente temporário a partir do PyPI oficial, sem versionar pacotes. O script funciona sem Jupyter. Os testes de preservação requerem o histórico Git dos commits anteriores.

Duas reproduções isoladas e hashes em [validacao_v4.json](validacao_v4.json). Não há aleatoriedade. Dados, dicionários, fontes e versões v1–v3 permanecem preservados; os testes comparam todos os arquivos já publicados de base3 byte a byte.

## Verificação explícita contra dupla defasagem

A [tabela de rastreabilidade](rastreamento_anos_receitas_v4.csv) registra 384 combinações de variável/ano, com o ano do preço e da quantidade de cada componente. Receita t usa P(t) e Q(t); lag1 usa P(t−1)×Q(t−1); lag2 usa P(t−2)×Q(t−2); a média usa esses dois produtos completos. Nenhuma versão trata o preço lag1 da base como contemporâneo. Os testes conferem os anos, a igualdade dos preços recuperados com o lag1 no outcome seguinte e NA nas bordas sem produção. As colunas de rastreabilidade são metadados auxiliares, não novos regressores.

## Pasta central para uso manual

A base completa foi movida, sem alteração de bytes, para [BASES_PARA_USO/BASE_COMPLETA_H1.csv](BASES_PARA_USO/BASE_COMPLETA_H1.csv). Os grupos 1–4 repetem todas as sete colunas de índice do grupo 0. Veja [LEIA_ME](BASES_PARA_USO/LEIA_ME.md). `separar_grupos_v4.py` gera os recortes sem inferência de tipos e recusa sobrescrever conteúdo divergente. O builder v4 usa os novos caminhos e faz a mesma proteção; trabalhe em cópias para edições manuais. Versões v1–v3 não foram movidas.
