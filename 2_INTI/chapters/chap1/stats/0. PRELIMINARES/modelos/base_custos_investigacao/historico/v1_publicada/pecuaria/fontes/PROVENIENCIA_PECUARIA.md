# IMEA pecuária — snapshot oficial de 24/10/2026

## Fonte e acesso

- Wrapper solicitado: https://imea.com.br/imea-site/arquivo-externo?categoria=relatorio-de-mercado&arquivo=cup-bovinoculturadecorte&numeropublicacao=1
- O wrapper apontou ao JS público `view/js/ArquivoExterno/ArquivoExterno.js?v=4`, cujo código monta a URL de `publicacoes.imea.com.br` pelos parâmetros categoria/arquivo/numeropublicacao.
- Download oficial resolvido: https://publicacoes.imea.com.br/relatorio-de-mercado/cup-bovinoculturadecorte/1
- Início da requisição: **2026-10-24T18:00:29.743009+00:00**. Este é o horário de coleta, não a data de publicação nem a referência dos valores.
- Resultado: HTTP 200, MIME XLSX, redirecionamento público normal para armazenamento do editor. Nenhuma autenticação, bloqueio de permissão ou contorno de restrição foi necessário.
- Raw: `imea_cup_bovinoculturadecorte_1.xlsx`, **495.467 bytes**.
- SHA256: `48fd4f37aad1dfa3fa9363120ce3e270cf4dd0a3dceae855afec2486d0bbd190`.
- Origem final sem query temporária: https://bucket-xiruexterno-2.s3.sa-east-1.amazonaws.com/2/696277432068079616/1252846777986392064-.xlsx
- O endpoint é vivo: uma nova coleta pode retornar outra publicação. Não é um endereço imutável de vintage. Não foi obtida uma data de publicação independente do conteúdo.
- `fetch_manifest.json` registra horários, fontes, tamanhos, tipos e hashes de raw, wrapper e JS. Os três estão preservados localmente.

## Escopo e unidades

O workbook contém **25 abas**: 17 de Cria, 6 de Recria e Engorda conjuntamente, e 2 de Ciclo Completo. Há três abas estaduais e abas municipais. Recria e Engorda não foram artificialmente separadas em sistemas distintos.

**A unidade dos custos em todas as abas é R$/@ vendida**, conforme A92. A91 apresenta produtividade modal em **@vendida/ha**. Ela permanece em campo separado. Não houve conversão para R$/ha, multiplicação por produtividade, cálculo de rentabilidade, agregação geográfica, modelagem ou publicação.

COE, COT e CT foram localizados pelos rótulos de origem: A71, A80 e A89. A produtividade é A91. Todos os registros preservam os endereços dos respectivos valores.

## Arquivos compactos

- `imea_pecuaria_sheets.csv`: mapa de IDs locais para nomes exatos das abas, sistema A3, localidade A4, unidades e alertas. **Os sheet_id são locais a este snapshot**, não identificadores municipais permanentes.
- `imea_pecuaria_costs_cria.csv`: 132 colunas-período da fonte.
- `imea_pecuaria_costs_recria_engorda.csv`: 48 colunas-período da fonte.
- `imea_pecuaria_costs_ciclo_completo.csv`: 16 colunas-período da fonte.
- Total: **196 registros com cabeçalhos de ano; 156 têm COE/COT/CT numéricos simultaneamente**. Os 40 demais preservam ausência de valores, não zeros imputados.
- `imea_pecuaria_headers_notes.csv`: 752 células de cabeçalhos, rótulos de métricas, unidades, fontes e notas, com sheet_id e endereço.
- `extraction_audit.json`: contagens por aba e regras de extração.
- `validation_report.json`: conferência independente com openpyxl de 784 campos de valores (COE/COT/CT/produtividade), além dos 196 pares de cabeçalhos ano/trimestre. **Todos conferem** com os caches do raw.

O script usa ZIP/XML e a biblioteca padrão do Python. Ele mantém a representação decimal armazenada, nomes com espaços finais, rótulos, zeros e células vazias. Não recalcula fórmulas. Os códigos `n` e `stored_blank` identificam, neste snapshot, valores numéricos e células armazenadas vazias. A verificação independente não é necessária para executar a extração, mas foi realizada nesta entrega.

## Períodos: não preencher lacunas

- As três abas estaduais têm 2020–2025 consolidados e 2º/3º trimestre de 2026. Isso **não** constitui uma série trimestral completa de 2020–2026.
- Rótulos literais `Consolidado` e `Consolidaddo` foram preservados. Apenas o campo descritivo de natureza reconhece ambos como consolidados; nenhum valor foi alterado.
- `reference_period_from_labels` usa `AAAA-Qn` somente quando ano e trimestre estão explícitos; consolidados explicitamente rotulados recebem apenas o ano. Cabeçalhos sem trimestre/natureza ficam sem período derivado.
- Não se declarou indiscriminadamente que os valores trimestrais são realizados ou estimados. Notas sobre estimativas permanecem separadas, sem inferir a qual coluna se aplicam.

## Inconsistências e ressalvas da própria fonte

1. **Guarantã do Norte** (`Cria_Guarantã_do_Norte `) traz A4=`MATO GROSSO`, cabeçalhos 2019–2023 e **nenhum COE/COT/CT numérico** nas sete colunas de ano. Não deve ser adotada como outra série estadual ou como histórico municipal preenchido.
2. **São José dos Quatro Marcos** (`Cria_São_José_dos_Quatro_Marcos`) traz A4=`CUSTO DE PRODUÇÃO`, conflitante com o nome da aba. Nome e A4 foram mantidos, sem resolver a localidade por inferência.
3. **Santo Antônio do Leste, Poxoréu e São José dos Quatro Marcos** têm cabeçalhos 2021–2025 sem rótulo de trimestre/consolidado e sem valores de custo; as duas colunas trimestrais 2026 têm valores. Não foram retropreenchidos.
4. **Barra do Garças, Paranatinga e Pedra Preta** anotam em A94 que deixaram a rota de painéis CPA a partir de 2026. Seus cabeçalhos ainda mostram 1º/2º tri.2026, mas não se inferiu disponibilidade numérica a partir deles. Consultar cada linha e `*_type`.
5. Várias abas têm A95 mencionando **safra 2025/26 de algodão**, apesar de este ser o workbook de pecuária. É uma aparente inconsistência editorial da fonte; texto preservado, não usado para reinterpretar custos.
6. A aba estadual de Cria, A95, informa ajustes técnicos do pacote tecnológico nos 1º, 2º e 3º trimestres de 2026. As abas estaduais de Recria e Engorda e de Ciclo Completo têm A94 com uma nota de segunda estimativa/primeiro trimestre de 2026 e suplementação. Essas notas não foram harmonizadas nem apagadas.
7. Algumas abas contêm dimensões de planilha de 1.048.576 linhas por formatação. O extrator percorre células XML armazenadas, não cria um milhão de linhas vazias. A validação independente foi limitada às linhas de conteúdo 1–95.

## Reproduzir

Extração deste raw, sem rede:

    python retrieve_extract_imea_pecuaria.py --out /caminho/pecuaria

Nova coleta em diretório separado:

    python retrieve_extract_imea_pecuaria.py --out /caminho/novo_snapshot --fetch

Não substituir o raw datado silenciosamente: o endpoint vivo pode mudar. O script não toca no repositório nem nos datasets do usuário; apenas escreve no diretório explicitamente informado. A integração posterior deve manter separado este bloco de pecuária em R$/@ vendida dos custos de lavoura em R$/ha.
