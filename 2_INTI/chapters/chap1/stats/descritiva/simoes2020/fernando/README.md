# Nova Figura 6 (Simoes et al., 2020) — Mato Grosso: 2001 vs. 2024

Este diretório (`2_INTI/chapters/chap1/stats/descritiva/simoes2020/fernando/`) contém o script completo em R, os rasters reprojetados e reclassificados, as tabelas de áreas e as figuras finais (PDF e PNG) que atualizam a **Figura 6 de Simoes et al. (2020)** (*Scientific Data*, 7, 34) para o intervalo **2001 vs. 2024**.

---

## 1. Aquisição de Dados via Google Earth Engine (`rgee`)

O script [`gerar_fig6_2001_2024.R`](file:///c:/Users/ferna/Documents/dev/Tese%20USP/tese_eco_usp/2_INTI/chapters/chap1/stats/descritiva/simoes2020/fernando/gerar_fig6_2001_2024.R) conecta-se diretamente ao Google Earth Engine (via `rgee` / `reticulate`) utilizando as credenciais locais autenticadas e consulta a coleção oficial consolidada mais recente do **MapBiomas Brasil (Coleção 10.1)**, que cobre o período **1985–2024**:

1. **Cobertura e Uso da Terra (Coleção 10.1, 1985–2024):**
   - Asset GEE: `projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1`
   - Bandas utilizadas: `classification_2001` e `classification_2024`
2. **Segunda Safra Agrícola (Coleção 10, 2000–2024):**
   - Asset GEE: `projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_agriculture_second_crop_v1`
   - Distingue dentro das áreas de soja (`39`) aquelas com **segunda safra de grãos/milho (`1` -> `Soy_Corn`)**, **segunda safra de algodão (`62` -> `Soy_Cotton`)** e **safra única (`0` -> `Soy_Fallow`)**.
3. **Idade da Vegetação Secundária (Coleção 10.1, 1985–2024):**
   - Asset GEE: `projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_degradation_secondary_vegetation_age_v1`
   - Identifica áreas de regeneração florestal (`age > 0` -> `Secondary Vegetation`).
4. **Bloco `tryCatch` com Fallback Automático (2024 $\rightarrow$ 2023):**
   - Caso o asset consultado no GEE não contenha a banda de 2024 (por exemplo, se utilizado o asset da Coleção 9 `mapbiomas_collection90_integration_v1`), o bloco `tryCatch` captura a exceção, emite um `warning()` explícito no console do R e realiza o download automático da camada de **2023**.

---

## 2. Matriz de Reclassificação (`terra::classify`)

As 13 classes originais da legenda de Simoes et al. (2020) (e todos os códigos equivalentes do MapBiomas) são agregadas rigorosamente nas **7 classes em português**:

| Código Final | Legenda em Português | Classes Originais Incluídas (Simoes et al., 2020 / MapBiomas) | Cor Hex |
| :---: | :--- | :--- | :---: |
| **1** | **Soja e Milho** | **Exclusivamente** `5: Soy_Corn` (Soja + 2ª safra de grãos/milho: `cov == 39 & second_crop == 1`) | `#E66101` |
| **2** | **Pecuária** | `4: Pasture` (Pastagem: `cov == 15`) | `#F4DE9C` |
| **3** | **Floresta** | `3: Forest` (Formação Florestal / Floresta Alagável primária: `cov %in% c(3, 5, 6, 49)`) | `#1B7837` |
| **4** | **Cerrado** | `1: Cerrado` (Formação Savânica, Campestre e Áreas Úmidas nativas: `cov %in% c(4, 11, 12, 29, 32, 50)`) | `#8CCD65` |
| **5** | **Área Urbana** | `13: Urban Area` (Infraestrutura Urbana: `cov == 24`) | `#D7191C` |
| **6** | **Áreas Alagadas** | `11: Water` (Corpos d'água — rios, lagos e aquicultura: `cov %in% c(26, 31, 33)`) | `#2B5C8F` |
| **7** | **Outras Culturas** | `6: Soy_Cotton`, `7: Soy_Fallow`, `8: Soy_Millet`, `9: Soy_Sunflower`, `12: Sugarcane`, `2: Fallow_Cotton`, `10: Secondary Vegetation` e todas as demais classes restantes | `#B266B2` |

---

## 3. Correção da Projeção e Fronteiras dos Biomas

- **Remoção da Inclinação (~30–40°):** Os rasters originais de Simoes et al. (2020) utilizavam a projeção Sinusoidal MODIS (`+proj=sinu`), que causa forte cisalhamento oblíquo na longitude de Mato Grosso ($\sim 55^\circ\text{W}$). Todos os rasters e vetores neste projeto estão estritamente reprojetados para **SIRGAS 2000 Geográfico (`EPSG:4674`)**, alinhando o estado perfeitamente a $0^\circ$ no eixo Norte–Sul.
- **Biomas (`geobr::read_biomes`):** Os limites oficiais dos biomas são sobrepostos com linhas tracejadas (`linetype = "dashed"`) e cores específicas por bioma — **Amazônia** em verde escuro (`#005824`), **Cerrado** em marrom terroso (`#7F3B08`) e **Pantanal** em azul profundo (`#084594`) — acompanhados de halo claro para contraste e rótulos posicionados **exclusivamente do lado de fora (bordas externas)** do polígono de Mato Grosso (verificados geometricamente via `!sf::st_intersects()`).

---

## 4. Como Executar

A partir da raiz do repositório:

```powershell
& "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" "2_INTI\chapters\chap1\stats\descritiva\simoes2020\fernando\gerar_fig6_2001_2024.R"
```

