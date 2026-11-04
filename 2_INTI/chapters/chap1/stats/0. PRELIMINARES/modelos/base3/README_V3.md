# Base3 v3 — oferta produtiva de soja e milho

Entrega: **3.384 linhas, 141 municípios, 2001–2024 e 54 colunas**. A v3 conserva os valores, nomes e ordem das 46 colunas da v2 publicada e acrescenta oito campos contemporâneos do grupo 2. Nenhuma regressão, imputação ou defasagem adicional. A publicação deste lote v3 foi autorizada separadamente, sem incluir outros trabalhos locais.

## Campos incorporados

Cada nome é `2_` seguido literalmente pelo nome da fonte. Área plantada estava disponível e foi incluída.

| Tipo | Milho | Soja | Unidade |
|---|---|---|---|
| Área plantada | `2_area_plantada_ha__milho` | `2_area_plantada_ha__soja` | ha |
| Área colhida | `2_area_colhida_ha__milho` | `2_area_colhida_ha__soja` | ha |
| Produção | `2_producao_t__milho` | `2_producao_t__soja` | t |
| Rendimento observado | `2_rendimento_medio_kg_ha__milho` | `2_rendimento_medio_kg_ha__soja` | kg/ha |

Fonte operacional: `../base2/painel_h1_v2.csv`, publicada no commit `1cbab8246114ecef0d2a80b55a068ea1cf4cf1c3`. A cópia local foi conferida byte a byte com esse commit. O construtor exige seu hash congelado e confere a igualdade textual dos oito campos com `../painel_municipal_descritiva_h1.csv`. Fonte primária conforme dicionário publicado: IBGE/PAM, SIDRA 1612. Não houve nova coleta nem uso de dados GM.

## Auditoria anterior ao apensamento

As chaves código IBGE/ano são únicas e coincidem integralmente entre fonte e destino; os nomes municipais também coincidem. Nenhuma perda no join. Isso demonstra compatibilidade com o suporte do painel de 141 municípios, mas **não reconstrói limites municipais históricos da PAM**. Não foram misturadas tabelas com 142 municípios, nem feitos rateios ou recodificações.

Cada campo de soja tem **2.615 valores válidos, 769 ausentes e cobertura de 136 municípios**. Cada campo de milho tem **3.318 valores válidos, 66 ausentes e cobertura de 141 municípios**. Nenhum zero numérico, negativo ou valor não finito foi encontrado nesses oito campos. As contagens por variável e por ano estão em [qualidade_produtiva_v3.csv](qualidade_produtiva_v3.csv); presença de algum dado por município não significa cobertura contínua em todos os anos.

Não se encontrou área colhida superior à plantada. O rendimento foi comparado a `1000 × produção(t) / área colhida(ha)`, com tolerância de **1 kg/ha + 1e−9 numérico**, compatível com sua apresentação em unidades inteiras. Isso admite arredondamento/truncamento, sem afirmar qual regra foi efetivamente adotada na origem. Diferenças máximas: soja aproximadamente 0,99970 kg/ha; milho 0,99879 kg/ha. Nenhum caso excedeu a tolerância. O rendimento informado foi preservado, não substituído pelo quociente.

O relatório [AUDITORIA_PRE_JOIN_V3.md](AUDITORIA_PRE_JOIN_V3.md) é gravado antes do painel. O arquivo de inconsistências tem cabeçalho e nenhuma ocorrência nesta versão. Inconsistências futuras não devem ser apagadas ou corrigidas silenciosamente; valores inválidos interrompem a construção.

## Ausências e suporte

As colunas publicadas já representam símbolos SIDRA como NA. Não retêm o símbolo bruto nem a razão da ausência por célula. Portanto, esta entrega não permite separar todas as situações de ausência de atividade, falta de cobertura ou outros motivos. Não converter NA em zero. A ausência de zeros observados neste bloco não certifica integralmente a cadeia histórica de tratamento da fonte.

| Disponibilidade conjunta | Linhas | Municípios |
|---|---:|---:|
| Painel-mestre | 3.384 | 141 |
| Quatro campos de soja | 2.615 | 136 |
| Quatro campos de milho | 3.318 | 141 |
| Oito campos produtivos | 2.590 | 136 |
| Oito campos + ambos desfechos de conversão válidos | 2.123 | 130 |

Essas são contagens de suporte, não filtros aplicados ao painel. Nenhuma linha foi removida. Incluir os oito campos numa futura regressão completa pode mudar substancialmente a composição da amostra; não atribuir essa mudança automaticamente ao efeito das covariáveis.

## Interpretação econômica

Produção, áreas e rendimento realizados são candidatos descritivos contemporâneos. Podem responder à conversão, aos preços e ao clima; não são controles exógenos automáticos. Rendimento observado não é aptidão GAEZ, lucro ou rentabilidade. Área plantada/colhida não é conversão de vegetação nativa para a cultura. Soja e milho podem ocupar a mesma terra em safras sucessivas: **não somar suas áreas como área física única**. Não foram acrescentadas culturas, pecuária, crédito ou novas defasagens.

## Reprodução e testes

Python >=3.9, somente biblioteca padrão. Dependências de dados: painel v2, base2 e painel original já publicados; nenhum complemento local não publicado é necessário.

```bash
python 2_INTI/chapters/chap1/stats/modelos/base3/construir_base3_v3.py
python 2_INTI/chapters/chap1/stats/modelos/base3/testar_base3_v3.py
```

Duas reproduções devem gerar hashes idênticos. Os testes verificam as 46 colunas anteriores célula a célula, as oito novas contra a fonte, as chaves/ordem, faltas/zeros, metadados e a preservação byte a byte de todos os arquivos de base3 publicados no commit `253d059c473d3d5efe1fe74a3c37a46f2ea41678`, incluindo v1/v2. Para a comparação histórica, manter o histórico Git disponível. Sem aleatoriedade ou semente aplicável.

[Dicionário completo](dicionario_variaveis_v3.csv), [adendo dos oito campos](dicionario_adendo_v3.csv), [manifesto](manifesto_v3.json), [suporte](suporte_produtivo_v3.csv) e [validação](validacao_v3.json).
