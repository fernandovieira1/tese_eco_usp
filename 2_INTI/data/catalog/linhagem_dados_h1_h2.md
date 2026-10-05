# Linhagem dos dados H1/H2

Todos os novos dados estão em `2_INTI/data`. Fontes e downloads são identificados por URL, instante UTC, SHA 256, bytes, status e versão nos manifestos `acquisition*.jsonl`. `inventario_arquivos_dados_h1_h2.csv` reúne arquivos brutos e derivados. O catálogo distingue OBSERVADA, AGREGADA e DERIVADA; documentos auxiliares são NAO_APLICAVEL.

## PAM e PPM

IBGE API v3 → metadados originais1612/3939 → consultas por blocos de até10 anos, municípios de UF51 → JSON bruto → extração da categoria e série territorial → chave código IBGE/ano/produto → CSV amplo.

- PAM: produtos2711(milho) e2713(soja); variáveis109,216,214,112.
- PPM: categoria79[2670], variável105.
- `h1_h2__pam_soja_milho__ibge__municipio_anual.csv` conserva área plantada/colhida(ha), produção(t), rendimento publicado(kg/ha) e símbolos originais.
- `yield_calculado_kg_ha = 1000 * producao_t / area_colhida_ha`, apenas quando área>0; `yield_diferenca_kg_ha` confronta o publicado. `yield_soja_kg_ha_it` recebe o rendimento publicado apenas na soja.
- Símbolos `-`, `...`, `..`, `X` não se transformam automaticamente em observações numéricas. `-` pode indicar zero absoluto no SIDRA, mas foi mantido explicitamente como símbolo e numeric missing nesta etapa conservadora; não interpretar todos esses missing como ausência aleatória. Nenhuma imputação.
- Não foram preenchidos municípios/anos não devolvidos nem harmonizados limites retroativamente.

Código: `prepare_h1_h2.py --stage sidra`.

## MapBiomas

DOI10.58053/MapBiomas/SJZOLT → metadados10.1 → datafile535 → XLSX bruto autenticado por MD5 oficial → abaCOVERAGE_10.1 → filtro state_acronym=MT → nome normalizado exato no cadastro IBGE de MT → quarentena dos não correspondentes → tabela classe/bioma/município/ano → soma entre biomas → estoque e fração candidatos → defasagem estritamente de um ano.

- `h1_h2__mapbiomas_classes__col10_1__municipio_bioma_anual.csv`: áreas originais em hectares, sem somar níveis taxonômicos pai e filho.
- `native_veg_ha_it`: soma de classes3,4,5,6,49,11,12,50.
- `native_veg_share_it`: estoque / soma de todas as classes mapeadas do município no ano. Água e não observado permanecem no denominador.
- `*_lag1`: valor de t-1 dentro do mesmo código, apenas anos consecutivos;1985 fica missing.
- Ausência de transições: `conv_total_it`, `conv_agric_it`, `conv_past_it` não construídas. Fórmula requerida: área de pixels nativos em t-1 que entram no uso alvo em t / área nativa t-1, na mesma coleção, suporte espacial e máscara válida.
- Coleção9 foi mantida separada após verificar que o XLSX não contém as transições anunciadas. Não alimenta os derivados10.1.

Código: `prepare_h1_h2.py --stage mapbiomas`. Legenda e regra: `mapbiomas_legenda_taxonomia.json`.

## Preços e custos

Página Banco Mundial → URL XLSX nela identificada → snapshot nominal → abaMonthly Prices → soja, milho e carne bovina → CSV mensal → log natural se preço>0 → diferença do log entre meses consecutivos.

`price_carne_bovina` internacional não é `price_boi_t` local. Sem câmbio, deflator, índice anual ou `ShockReturn` definitivo. Características comerciais exatas estão na abaDescription do XLSX. Anos incompletos não foram agregados.

CONAB → página de custos → arquivos XLS de soja, milho1ª e2ªsafra → planilhas brutas preservadas → seleção de abas que indicam MT → CSV de células não vazias com arquivo/aba/linha/coluna. A extração preserva o conteúdo e sua localização; não é ainda uma série homogênea `cost_*`. Não comparar valores antes de verificar unidade, ano/safra, tecnologia e metodologia de cada aba.

Código: `prepare_h1_h2.py --stage prices`; `prepare_supplements.py`.

## GAEZ

FAO/IIASA v4 → guia e inventários oficiais → listagem do bucket por prefixos → res05/CRUTS32/Hist/6190H ou6190L → rasters `sxHr0`, `sxLr0`, `yxHr0`, `yxLr0`, culturassoy/mze → máscara municipal2024 → média ponderada por cos(latitude) dos centros de pixels válidos → CSV longo de oito variantes.

- Clima1961–1990, sequeiro, alto/baixo insumo, sem fertilizaçãoCO₂; resolução e CRS lidos dos arquivos.
- `sx`: índice contínuo0–10000 sobre todas as terras da célula. Não é o índice categórico `si`.
- `yx`: rendimento alcançável da melhor classe de aptidão na célula, kg de matéria seca/ha; não é produtividade contemporânea PAM.
- Não há base pecuária escolhida, padronização entre produtos nem soma do choque de retornos.

Código: `acquire_gaez.py`; `prepare_static_rasters.py`. Documentação: guia, planilha de variáveis e inventário oficial preservados.

## Fiscalização IBAMA

CKAN oficial → URL de recurso → ZIP nacional original → partições CSV por ano → registros comUF=MT → tabela de eventos preservando datas, coordenadas, tipo, valor, status, identificadores e enquadramento → data de lavratura ISO com/sem horário → chave municipal declarada → soma nominal e contagem dos eventos com identificador não vazio/único e data interpretável.

Nenhum status é excluído silenciosamente. Identificadores ausentes permanecem na tabela de eventos. Anos sem registro não recebem zero. Valores não deflacionados não equivalem a multas pagas nem a intensidade institucional exógena.

Variante espacial: longitude/latitude numéricas dentro do bbox MT → hipóteseEPSG:4326 → ponto dentro do polígono municipal2024 → comparação com código declarado → agregação separada. Não se substitui a associação informada. Geometrias originais em outros campos continuam disponíveis no ZIP.

Embargos: coordenadas e histórico adquiridos separadamente. A tabela principal retornou404 e não foi possível obter geometria no link SHP indicado pelo catálogo. Não contar linhas de histórico/coordenadas como embargos únicos nem somar área sem unidade e identidade autenticadas.

Código: `prepare_ibama.py`; `prepare_supplements.py`.

## Biomas

ZIPIBGE2019 + malhaMT2024 original → validação de feições/CRS → projeçãoEPSG:5880 para áreas → correção documentada de uma geometria projetada → interseção → área de cada bioma / área municipal inteira → frações → classes de predominância70%,80%,90%; abaixo do limiar=misto.

Não foi renormalizada a soma das frações quando há pequenas lacunas de fronteira. Não foi adotado um limiar definitivo nem substituído um crosswalk consolidado.

Código: `prepare_h1_h2.py --stage vectors`. Evidências: `validacao_vetores.json` e `reparo_geometria_projecao.json`.

## CHIRPS

Diretório oficialv2 → nomes observados na listagem → todos os meses dos anos completos1981–2025 → GeoTIFF.gz original → descompressão em memória → recorte retangular MT em GeoTIFF, sem reprojetar ou reamostrar → rasterização municipal por centro do pixel → média dos valoresmm com peso cos(latitude) → tabela mensal → soma anual apenas com12 meses válidos.

Alternativas exploratórias:

- `precip_anomaly_1981_2010` = total anual − média dos30 totais anuais1981–2010.
- `precip_anomaly_1991_2020` = total anual − média dos30 totais anuais1991–2020.
- `precip_zscore_*` = anomalia / desvio-padrão amostral(ddof=1), apenas se desvio>0 e os30 anos existem.
- `precip_deficit_*` = máximo entre menos anomalia e zero; `precip_excess_*` = máximo entre anomalia e zero, preservando missing. São desvios de precipitação, não medidas de balanço hídrico.

Não são choques da safra da soja homologados. Baseline com anos futuros em relação a observações antigas exige decisão metodológica antes de uso causal. Déficit hídrico exige balanço, não apenas sinal de anomalia. ERA5-Land não foi substituído por CHIRPS.

Código: `acquire_chirps.py`; `prepare_chirps.py`. Insumos e recortes geoespaciais preservados. A interrupção técnica de um download inicial deixou arquivo `.interrupted`, explicitamente não utilizado.

## Topografia

Distribuição públicaCopernicus GLO-90 → listagem oficial de cada tile que intersecta MT →101COGs originais → centros dos pixels dentro de cada município2024 → média, mínimo e máximo em metros e número de pixels.

O produto éDSM, contendo efeitos de vegetação/edificações; média simples dos pixels do próprio raster, sem ajuste adicional de latitude. Não foram inventadas declividade ou rugosidade a partir de médias de elevação. Esses derivados dependem de método, reprojeção e vizinhança documentados.

Código: `acquire_dem.py`; `prepare_static_rasters.py`.

## Instituições, CAR, calendário, temperatura e demais controles

Páginas oficiais e respostas → snapshots/documentos → avaliação de disponibilidade → matriz de lacunas. Não há painel histórico MMA reconstruído, CAR retrocedido, janela agrícola definitiva, validação INMET nem crédito incluído automaticamente.

ZARC 2025/26 é documento válido preservado; seus limites por cultura/solo/ciclo/município não definem automaticamente janelas de anos anteriores. ERA5-Land: pedido reproduzível em `era5land_request_candidate.json`, sem conta/credencial CDS disponível; extremos diários requerem pedido horário específico.
