# Validação dos dados H1/H2

## Integridade e preservação

Branch `main`; HEAD `e5c8ece0c4516a79e2cef0b293ae2ce13f1259ce`. Originais alterados: 0. Hashes divergentes: 0.

Hashes/tamanhos e formato por arquivo estão no inventário; estatísticas por coluna (mínimo, máximo, média, desvio, mediana, p1/p25/p75/p99), missing, chaves e anos ausentes internos estão em `perfis_validacao_h1_h2.json`. Outliers IQR apenas sinalizados, sem remoção ou imputação. Nenhum período foi escolhido por significância.

## Tabelas finais e intermediárias auditadas

| Arquivo | Linhas | Municípios | Período presente | Repetições de chave |
|---|---:|---:|---|---:|
| h1__autos_ibama__espacial_municipio_anual_candidato.csv | 2008 | 138 | 1999-2026 | 0 |
| h1__autos_ibama__eventos_MT.csv | 52991 | 141 | 1987-2026 | 378 |
| h1__autos_ibama__geocodificacao_candidata.csv | 25345 | 140 | 1999-2026 | 369 |
| h1__autos_multas_ibama__municipio_anual_candidato.csv | 3006 | 141 | 1987-2026 | 0 |
| h1__costs_conab__milho_1a_safra_serie_historica_1997-2025__MT_celulas.csv | 2975 | n/a | soja 1997-2026; milho 1997-2025 e 2005-2025 nos nomes oficiais | 0 |
| h1__costs_conab__milho_2a_safra_serie_historica_2005-2025__MT_celulas.csv | 18229 | n/a | soja 1997-2026; milho 1997-2025 e 2005-2025 nos nomes oficiais | 0 |
| h1__costs_conab__serie-historica-custos-soja-1997-a-2026__MT_celulas.csv | 24156 | n/a | soja 1997-2026; milho 1997-2025 e 2005-2025 nos nomes oficiais | 0 |
| h1__prices__worldbank__mensal_robustez.csv | 2400 | n/a | 1960-01-01 a 2026-08-01 | 0 |
| h1__suitability_yield__gaez_v4_6190__candidatos.csv | 1136 | 142 | clima 1961-1990; base de terras v4 de 2010 | 0 |
| h1_h2__mapbiomas_classes__col10_1__municipio_bioma_anual.csv | 113600 | 141 | 1985-2024 | 0 |
| h1_h2__pam_soja_milho__ibge__municipio_anual.csv | 14768 | 142 | 1974-2025 | 0 |
| h1_h2__ppm_bovinos__ibge__municipio_anual.csv | 7191 | 141 | 1974-2024 | 0 |
| h2__biome_share__ibge2019_malha2024__candidato.csv | 142 | 142 | biomas2019 / malha2024 | 0 |
| h2__native_veg__mapbiomas_col10_1__candidato.csv | 5640 | 141 | 1985-2024 | 0 |
| h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv | 6390 | 142 | 1981-2025 | 0 |
| h2__precip_mm__chirps_v2__mensal_candidato.csv | 76680 | 142 | 1981-2025 | 0 |
| mapbiomas_col10_1__MT_sem_correspondencia_IBGE__quarentena.csv | 9 | 0 | 1985-2024; lag 1986-2024 | 0 |
| territorio__cobertura_fontes__sem_harmonizacao.csv | 142 | 142 | nao aplicavel | 0 |
| topography__copdem90__municipio_candidato.csv | 142 | 142 | estatica | 0 |

Repetições nos eventos/geocodificação IBAMA são identificadores vazios: não foram apagadas. Tabelas agregadas têm chaves únicas. Linhas PAM incluem símbolos sem valor numérico; presença da linha não equivale a observação válida. O CSV de custos é uma transcrição indexada de células, não uma série de custos homologada.

## Verificações substantivas

- PAM: produção(t) ×1000 / área colhida(ha) comparada ao rendimento publicado; discrepância absoluta máxima inferior a1 kg/ha. Área zero não gera divisão válida.
- MapBiomas 10.1: MD5 oficial do XLSX conferido; chaves classe/bioma/município/ano únicas; fração nativa entre0e1; defasagem por município/ano consecutivo; nove linhas não associadas preservadas separadamente.
- Biomas: CRS originalEPSG:4674; áreaEPSG:5880; frações não renormalizadas; soma municipal mínima0,998745. Correção projetada documentada separadamente.
- IBAMA: 52991 eventos MT, 379 IDs ausentes, 0 repetições de IDs não vazios, 0 datas não interpretadas e 156 valores monetários ausentes. A agregação reconcilia com eventos elegíveis.
- Geocodificação IBAMA: 25345 coordenadas dentro do bbox, 132 sem polígono e 2355 divergências de código. CRS das coordenadas é hipótese provisória. Nenhuma substituição automática do código informado.
- GAEZ: oito variantes sequeiro/1961–1990/semCO₂; índices sx limitados a0–10000; valores yx em matéria seca. Não confundir classes categóricas com índices contínuos.
- Copernicus:101 tiles originais, cobertura dos 142 municípios; média entre mínimo/máximo. DSM não equivale a terreno nu.
- CHIRPS: integridadeGZIP, CRS/resolução/bandas/extent registrados; negativos inclusiveNoData-9999 excluídos; recorte final expande bordas para conter integralmente o bbox. Anos exigem12 meses; climatologias exigem30 anos; zscore exige desvio positivo. Nenhuma anomalia é calculada com normal incompleta.

## Falhas e restrições preservadas

- O suposto PDF histórico MMA é HTML de redirecionamento e não serve como documento normativo. Permanece com status FORMATO_INCORRETO_PRESERVADO.
- Metadados MapBiomas da coleção9 anunciam transições, mas a planilha contém somente cobertura. Não há taxa de conversão válida entregue.
- CEPEA403, CAR401, IMEA_TLS, embargos404, URLSTAC404; a alternativaDEM via listagem oficial funcionou. Consultar `falhas_aquisicao_h1_h2.json`.
- Um download CHIRPS foi interrompido tecnicamente para permitir aquisição concorrente. Eventual arquivo `.interrupted` não é raster válido de análise e permanece catalogado como incompleto.
- Coleta de temperatura CDS não executada: não há configuração `.cdsapirc`; pedido público preparado, sem segredos.

## Testes

No checkpoint não havia suíte de testes identificada. Foi executado o script de auditoria preexistente antes dos downloads. Foram adicionados testes de integridade do original, MD5MapBiomas, chaves, símbolosSIDRA, produtividade, defasagem, taxonomia/quarentena, biomas, preços, reconciliação IBAMA, GAEZ, climatologias e coberturaDEM. Resultado da execução final: `testes_h1_h2.txt`. A inspeção visual do catálogo XLSX cobre a única aba; CSV/XLSX são confrontados célula a célula.
