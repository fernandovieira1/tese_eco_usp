library(tidyverse)
library(arrow)
setwd("C:/Users/ferna/Documents/dev/Tese USP/tese_eco_usp/2_INTI/chapters/chap1/stats/descritiva")

h1 <- read_parquet("df_h1")
view(h1)

## CONVERSÃO DE FLORESTAS
# Mata nativa
# Mata convertida
# Terra cultivável

## PREÇOS
# Soja
# Algodão
# Carne
# Terra


## PRODUTIVIDADE
# Rendimento médio
# Soja
# Algodão
# Carne
# Terra

h1prov <- read_parquet("df_h1_proveniencia")
view(h1prov)
