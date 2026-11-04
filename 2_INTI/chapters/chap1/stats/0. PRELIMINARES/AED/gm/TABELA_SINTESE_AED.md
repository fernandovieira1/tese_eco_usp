# Tabela Síntese dos 25 Notebooks de Análise Exploratória de Dados (AED)

**Projeto:** Tese de Doutorado — Economia Aplicada / Uso da Terra em Mato Grosso  
**Capítulo:** 1 — Modelo de Conversão de Vegetação Nativa para Usos Agropecuários  
**Diretório:** `2_INTI/chapters/chap1/stats/AED/gm/`  
**Referência:** `2_INTI/chapters/chap1/stats/HIPOTESES TESE - CHAP1.txt`  
**Protocolo:** Protocolo Padronizado de 6 Fases (Setup & Load, Cleaning & Wrangling, Descritiva, Univariada, Bivariada, Feature Engineering)

---

## Síntese das Variáveis Candidatas

| # | Nome do arquivo | Descrição breve do conteúdo | Fonte dos dados | Período dos dados | Periodicidade dos dados | Espacialidade dos dados | Unidade de medida |
|:---:|:---|:---|:---|:---|:---|:---|:---|
| 1 | [`Y_conv.ipynb`](./Y_conv.ipynb) | Estoques e dinâmica de conversão de vegetação nativa para agricultura e pastagem (destinos separados). | MapBiomas (Coleção 10.1) | 1985 a 2024 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT por bioma) | hectares (ha) |
| 2 | [`Y_tx-conv.ipynb`](./Y_tx-conv.ipynb) | Estoque remanescente de nativa e taxa de conversão sobre o estoque do início do período ($t-1$). | MapBiomas (Coleção 10.1) | 1985 a 2024 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT) | proporção (0 a 1) |
| 3 | [`x1_psoja-pmilho.ipynb`](./x1_psoja-pmilho.ipynb) | Preços internacionais de referência de soja e milho em USD/t (médias anuais e janelas pré-plantio). | Banco Mundial (Pink Sheet) | 1960 a 2026 *(painel: 2001 a 2024)* | Mensal *(anualizado no painel)* | Global / Internacional | USD/t |
| 4 | [`x1a_pcarne.ipynb`](./x1a_pcarne.ipynb) | Preço internacional de referência da carne bovina em USD/kg (benchmark do retorno pecuário). | Banco Mundial (Pink Sheet) | 1960 a 2026 *(painel: 2001 a 2024)* | Mensal *(anualizado no painel)* | Global / Internacional | USD/kg |
| 5 | [`x2_prodsoja-prodmilho.ipynb`](./x2_prodsoja-prodmilho.ipynb) | Produtividade agrícola observada (rendimento médio em kg/ha) nas áreas colhidas de soja e milho. | IBGE (PAM) | 1974 a 2025 *(painel: 2001 a 2024)* | Anual (ano-safra) | Municipal (141 municípios de MT) | kg/ha |
| 6 | [`x2a_hprodsoj-hprodmil.ipynb`](./x2a_hprodsoj-hprodmil.ipynb) | Produtividade média histórica pré-2001 de soja e milho como capacidade produtiva predeterminada. | IBGE (PAM) | 1974 a 2000 *(período pré-painel)* | Média histórica estática | Municipal (141 municípios de MT) | kg/ha |
| 7 | [`x2b_yield-sojamilho.ipynb`](./x2b_yield-sojamilho.ipynb) | Rendimento biofísico potencial agroecológico de soja e milho em sequeiro (kg matéria seca/ha). | FAO / IIASA (GAEZ v4) | Clima 1961–1990 / Solo 2010 | Estático (invariante no tempo) | Municipal (141 municípios de MT) | kg de matéria seca/ha (kg DW/ha) |
| 8 | [`x2c_aptid-sojamilho.ipynb`](./x2c_aptid-sojamilho.ipynb) | Índice biofísico adimensional de aptidão agroecológica de solo e clima para soja e milho (0 a 10.000). | FAO / IIASA (GAEZ v4) | Clima 1961–1990 / Solo 2010 | Estático (invariante no tempo) | Municipal (141 municípios de MT) | índice 0–10.000 (adimensional) |
| 9 | [`x3_infracoes.ipynb`](./x3_infracoes.ipynb) | Quantidade de autos de infração ambiental agregados pelo código municipal informado no registro. | IBAMA | 1987 a 2026 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT) | quantidade de autos (contagem) |
| 10 | [`x3a_infracoes.ipynb`](./x3a_infracoes.ipynb) | Quantidade de autos de infração do IBAMA atribuídos espacialmente pelas coordenadas (lat/long). | IBAMA | 1999 a 2026 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT) | quantidade de autos (contagem) |
| 11 | [`x3b_infracoes.ipynb`](./x3b_infracoes.ipynb) | Microdados de eventos individuais de autuação em MT (enquadramento flora, data do fato vs lavratura). | IBAMA | 1987 a 2026 *(painel: 2001 a 2024)* | Por evento individual | Pontual / Municipal (MT) | registros individuais (R$ nominais e ha) |
| 12 | [`x3c_infracoes.ipynb`](./x3c_infracoes.ipynb) | Auditoria de correspondência espacial e divergência entre código informado e geocodificado dos autos. | IBAMA | 1999 a 2026 *(painel: 2001 a 2024)* | Por evento / Anual | Municipal (MT) | taxa de divergência (0 a 1 / %) |
| 13 | [`x3d_infracoes.ipynb`](./x3d_infracoes.ipynb) | Montante financeiro nominal total das multas ambientais autuadas pelo IBAMA (em R$). | IBAMA | 1987 a 2026 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT) | R$ nominais |
| 14 | [`x3e_infracoes.ipynb`](./x3e_infracoes.ipynb) | Termos de embargo ambiental do IBAMA (contagem de termos e área interditada em hectares). | IBAMA | 1990 a 2026 *(série ampla pós-2005)* | Por evento individual (anualizado) | Pontual / Municipal (MT) | quantidade de termos e área (ha) |
| 15 | [`x4_pecuaria.ipynb`](./x4_pecuaria.ipynb) | Efetivo do rebanho bovino municipal (estoque de cabeças em 31 de dezembro). | IBGE (PPM) | 1974 a 2024 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT) | cabeças de gado |
| 16 | [`x4a_pecuaria.ipynb`](./x4a_pecuaria.ipynb) | Lotação aparente das pastagens (cabeças de bovinos por hectare de pastagem do MapBiomas). | IBGE (PPM) e MapBiomas (Col. 10.1) | 1985 a 2024 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT) | cabeças/ha de pastagem |
| 17 | [`x5_cobertura_terra.ipynb`](./x5_cobertura_terra.ipynb) | Estoque remanescente de vegetação nativa no ano $t-1$ (em ha e share da área municipal). | MapBiomas (Coleção 10.1) | 1985 a 2024 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT) | hectares (ha) e proporção (0 a 1) |
| 18 | [`x5a_cobertura_terra.ipynb`](./x5a_cobertura_terra.ipynb) | Áreas de pastagem e agricultura já instaladas (diferenciação entre conversão primária e substituição). | MapBiomas (Coleção 10.1) | 1985 a 2024 *(painel: 2001 a 2024)* | Anual | Municipal (141 municípios de MT por bioma) | hectares (ha) |
| 19 | [`x6_biomas.ipynb`](./x6_biomas.ipynb) | Fração territorial municipal em Amazônia, Cerrado e Pantanal e classes de predominância (70%, 80%, 90%). | IBGE (Biomas 2019 / Malha 2024) | Estático (malha de referência) | Estático (invariante no tempo) | Municipal (141 municípios de MT) | proporção territorial (0 a 1) |
| 20 | [`x7_custo-soja.ipynb`](./x7_custo-soja.ipynb) | Estrutura de custos operacionais de produção de soja (células de despesas e coeficientes em R$/ha). | CONAB | 1997 a 2026 | Anual / Safra | Regional (praças produtoras de MT) | R$/ha ou R$/saca (60 kg) |
| 21 | [`x7_custo-milho-s1.ipynb`](./x7_custo-milho-s1.ipynb) | Estrutura de custos operacionais de produção de milho 1ª safra (milho de verão). | CONAB | 1997 a 2013 | Anual / Safra | Regional (praças produtoras de MT) | R$/ha ou R$/saca (60 kg) |
| 22 | [`x7_custo-milho-s2.ipynb`](./x7_custo-milho-s2.ipynb) | Estrutura de custos operacionais de produção de milho 2ª safra (milho safrinha após a soja). | CONAB | 1997 a 2025 *(expansão pós-2005)* | Anual / Safra | Regional (praças produtoras de MT) | R$/ha ou R$/saca (60 kg) |
| 23 | [`x8_chuva.ipynb`](./x8_chuva.ipynb) | Precipitação acumulada mensal em mm (regime de chuva e ciclo sazonal em MT). | CHIRPS v2.0 (UCSB) | 1981 a 2025 *(painel: 2001 a 2024)* | Mensal *(anualizável por safra)* | Municipal (141 municípios de MT) | milímetros (mm) |
| 24 | [`x8_chuvaa.ipynb`](./x8_chuvaa.ipynb) | Precipitação anual total e choques climáticos em escore padronizado (z-score frente a 1981–2010 e 1991–2020). | CHIRPS v2.0 (UCSB) | 1981 a 2025 *(painel: 2001 a 2024)* | Anual (ano civil) | Municipal (141 municípios de MT) | milímetros (mm) e z-score |
| 25 | [`x9_relevo.ipynb`](./x9_relevo.ipynb) | Altimetria municipal (altitude média, mínima, máxima e amplitude como proxy de mecanização). | Copernicus DEM GLO-90 (ESA) | Estático (missão radar) | Estático (invariante no tempo) | Municipal (141 municípios de MT) | metros (m) |

---

## Salvaguarda Metodológica Territorial (141 Municípios)

Em todos os notebooks com agregação municipal de Mato Grosso, adota-se a restrição formal de **141 municípios históricos**:
- O 142º município recentemente criado (**Boa Esperança do Norte**, código IBGE `5101837`), desmembrado de Nova Ubiratã (`5106240`) e Sorriso (`5107925`), tem seus valores aglutinados em seu município de origem preponderante (**Nova Ubiratã - 5106240**).
- Essa padronização preserva o conceito econométrico de **Área Mínima Comparável (AMC)**, impedindo descontinuidades espaciais artificiais na composição do painel longitudinal 2001–2024.
