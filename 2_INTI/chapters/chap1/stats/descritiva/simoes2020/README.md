# Replicação de Simoes et al. (2020) — Uso e Cobertura do Solo em Mato Grosso (2001–2017)

Replicação integral do pipeline metodológico, tratamento de dados, agregações tabulares e visualizações do artigo:

> **Simoes, R., Picoli, M. C. A., Câmara, G., Maciel, A., Santos, L., Andrade, P. R., Sánchez, A., Ferreira, K., & Carvalho, A. (2020).** *Land use and cover maps for Mato Grosso State in Brazil from 2001 to 2017.* **Scientific Data**, 7, 34. https://doi.org/10.1038/s41597-020-0371-4

* **Código-fonte original (Zenodo):** [`10.5281/zenodo.3354379`](https://doi.org/10.5281/zenodo.3354379) (`v1.0.2`, arquivo `main.R`)
* **Dataset oficial (PANGAEA):** [`10.1594/PANGAEA.899706`](https://doi.org/10.1594/PANGAEA.899706) (17 GeoTIFFs anuais em projeção senoidal MODIS, `training_dataset_v3.csv` com 1.892 amostras e `QGIS_style_mt_v3.qml`)

---

## 1. Estrutura de Diretórios

Gerada automaticamente por `setup_project.R`:

```text
simoes2020/
├── setup_project.R                 # Cria a árvore de pastas de forma idempotente
├── run_all.R                       # Orquestrador ponta a ponta do pipeline
├── README.md                       # Documentação e ordem de execução
├── data/
│   ├── raw/
│   │   ├── MANIFEST.csv            # Proveniência, URLs, tamanhos e hashes SHA-256
│   │   ├── zenodo/                 # Código-fonte original (main.R v1.0.2)
│   │   ├── pangaea/                # 17 GeoTIFFs (mt_2001..2017_v3_1.tif), CSV (1.892 amostras) e QML
│   │   ├── ancillary/              # IBGE/SIDRA (Tabela 1612), PRODES (TerraBrasilis WFS) e malha de MT
│   │   └── masks/                  # Máscaras temáticas (urbano, água, cana Canasat, PRODES 2001/2000)
│   └── processed/
│       ├── classified/             # Probabilidades e mapas pós-suavização Bayesiana (sits)
│       ├── masked/                 # Mapas após máscaras temáticas e regras do mapa-base 2001
│       └── final/                  # Mapas finais pós-LUC Calculus (2001–2017)
├── scripts/
│   ├── config.R                    # Parâmetros globais, classes (1..13), cores Hex e hiperparâmetros
│   ├── utils.R                     # Funções auxiliares de download, manifesto, blocos raster e QML
│   ├── luc_rules.R                 # Regras puras da Tabela 3 (mapa-base 2001) e Tabela 4 (LUC Calculus)
│   ├── 01_download_core.R          # Baixa Zenodo (10.5281/zenodo.3354379) e PANGAEA (10.1594/PANGAEA.899706)
│   ├── 02_download_reference.R     # Baixa IBGE/PAM (SIDRA 1612), PRODES (WFS) e malha estadual de MT
│   ├── 03_extract_timeseries.R     # Extrai/carrega séries temporais MOD13Q1 e gera Tabela 1
│   ├── 04_som_quality_control.R    # Controle de qualidade com Self-Organizing Maps (SOM, Tabela 2)
│   ├── 05_train_svm.R              # Treinamento SVM (RBF, C=1, gamma=1/92) e CV de 5 folds (Tabela 5)
│   ├── 06_classify_smooth.R        # Classificação de cubos MOD13Q1 + suavização Bayesiana (sigma^2=10)
│   ├── 07_apply_masks.R            # Máscaras (urbano=11, cana=10, água=12) e mapa-base 2001 (Tabela 3)
│   ├── 08_luc_calculus.R           # Regras temporais LUC Calculus (Tabela 4, regras 1–10, Veg. Secundária)
│   ├── 09_area_tables.R            # Agregação dos rasters em dataframes tabulares (ha por classe, 2001–2017)
│   ├── 10_fig5_area_comparison.R   # Reprodução da Figura 5 e correlações de Pearson (IBGE e PRODES)
│   └── 11_fig6_maps.R              # Reprodução da Figura 6 (mapas 2001 e 2017 com paleta oficial QML)
├── tests/
│   └── test_luc_rules.R            # 31 testes unitários determinísticos das regras Tabelas 3 e 4
└── outputs/
    ├── maps/                       # GeoTIFFs com tabela de cores embutida (mt_2001/2017_colored.tif)
    ├── figures/                    # Figuras 4 (demo Sinop), SOM, Figura 5 e Figura 6 (PNG e PDF)
    └── tables/                     # Dataframes CSV de áreas anuais, correlações e diagnósticos
```

> **Conformidade com `RESEARCH_PROTOCOL.md`:** caso deseje armazenar os arquivos brutos/processados em `2_INTI/xdata/`, basta definir a variável de ambiente `SIMOES_DATA_ROOT` antes de rodar os scripts.

---

## 2. Ordem Correta de Execução do Pipeline

Execute a partir da pasta `2_INTI/chapters/chap1/stats/descritiva/simoes2020`:

```powershell
# 0. Criar estrutura de diretórios
Rscript setup_project.R

# 1. Aquisição do código Zenodo, mapas/amostras/QML PANGAEA e dados auxiliares IBGE/PRODES
Rscript scripts/01_download_core.R
Rscript scripts/02_download_reference.R

# 2. Testes unitários das regras de pós-processamento (Tabelas 3 e 4)
Rscript tests/test_luc_rules.R

# 3. Pipeline de processamento com `sits` (SOM -> SVM RBF -> Suavização Bayesiana -> Máscaras -> LUC Calculus)
#    Para execução rápida offline (usando amostras MODIS de MT e o cubo MOD13Q1 de Sinop-MT embutidos no sits):
$env:SIMOES_DEMO="1"
Rscript scripts/03_extract_timeseries.R
Rscript scripts/04_som_quality_control.R
Rscript scripts/05_train_svm.R
Rscript scripts/06_classify_smooth.R
Rscript scripts/07_apply_masks.R
Rscript scripts/08_luc_calculus.R
Remove-Item Env:\SIMOES_DEMO

# 4. Análise descritiva e dataframes de área (ha por classe, 2001–2017)
Rscript scripts/09_area_tables.R

# 5. Reprodução da Figura 5 (séries temporais vs. IBGE/PRODES) e Figura 6 (mapas 2001 e 2017)
Rscript scripts/10_fig5_area_comparison.R
Rscript scripts/11_fig6_maps.R
```

Ou, em um único comando:

```powershell
Rscript run_all.R
```

---

## 3. Notas Metodológicas e Equivalência de API (`sits` 2019 vs. `sits` >= 1.5)

1. **API do pacote `sits`:** O script original de 2019 (`main.R` no Zenodo) utilizava funções da versão 0.9 do `sits` (`sits_coverage`, `sits_select_bands_`, `sits_classify_cubes`, `sits_bayes_postprocess`) e pacotes internos hoje arquivados (`inSitu`, `lucCalculus`, `sits.validate`, serviço `WTSS`/`EOCUBES`). Os scripts `03` a `08` traduzem todo o fluxo para a API atual do `sits` (`sits_cube`, `sits_get_data`, `sits_som_map`, `sits_som_clean_samples`, `sits_train`, `sits_svm`, `sits_kfold_validate`, `sits_classify`, `sits_smooth`, `sits_label_classification`) e `terra`, preservando integralmente a lógica científica e os hiperparâmetros ($C = 1$, $\gamma = 1/92 = 0{,}01086957$, $\sigma^2 = 10$).
2. **Cálculo de área em hectares (`09_area_tables.R`):** Os mapas publicados no PANGAEA estão na projeção senoidal MODIS (`+proj=sinu`), que é **equivalente em área**. Cada pixel tem resolução exata de $231{,}6563 \times 231{,}6563\text{ m} = 5{,}366468\text{ ha}$, totalizando $16.894.363$ pixels válidos em Mato Grosso ($90{,}663\text{ milhões de ha}$).
3. **Agregações para a Figura 5 (`10_fig5_area_comparison.R`):**
   * **Soja:** soma das 5 classes com soja (`Soy_Corn` [5], `Soy_Cotton` [6], `Soy_Fallow` [7], `Soy_Millet` [8], `Soy_Sunflower` [9]) — $r = 0{,}972$ contra IBGE (artigo: $0{,}97$).
   * **Milho:** classe `Soy_Corn` [5] — $r = 0{,}975$ contra IBGE (artigo: $0{,}98$).
   * **Algodão:** soma de `Fallow_Cotton` [2] + `Soy_Cotton` [6] — $r = 0{,}853$ contra IBGE (artigo: $0{,}85$).
   * **Girassol:** classe `Soy_Sunflower` [9] — $r = 0{,}782$ contra IBGE (artigo: $0{,}80$; IBGE reporta girassol a partir de 2005).
   * **Total das culturas:** $r = 0{,}977$ (área plantada) e $r = 0{,}980$ (área colhida) contra IBGE (artigo: $0{,}98$).
   * **Floresta (PRODES):** o WFS público do TerraBrasilis (`prodes-legal-amz:yearly_deforestation`) disponibiliza incrementos anuais desagregados a partir de 2008 (o período 1988–2007 encontra-se consolidado na máscara `accumulated_deforestation_2007`). Por padrão, `10_fig5_area_comparison.R` ancora a série derivada do PRODES na área florestal de 2007 e subtrai os incrementos anuais de 2008 a 2017; caso o usuário adicione `data/raw/ancillary/prodes_mt_rates_km2.csv` (`year,increment_km2`) com as taxas pré-2008, a série passa automaticamente a cobrir 2001–2017.
4. **Legenda oficial da Figura 6 (`11_fig6_maps.R`):** As 13 classes e códigos hexadecimais são validados diretamente contra o arquivo `QGIS_style_mt_v3.qml` do PANGAEA antes da plotagem.

