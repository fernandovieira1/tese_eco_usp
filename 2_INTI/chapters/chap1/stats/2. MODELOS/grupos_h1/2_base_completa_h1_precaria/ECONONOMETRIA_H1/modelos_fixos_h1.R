#........................................
#### 0. CONFIGURAR AMBIENTE ####
#........................................

setwd("C:/Users/ferna/Documents/dev/Tese USP/tese_eco_usp/2_INTI/chapters/chap1/stats/2. MODELOS/grupos_h1/2_base_completa_h1_precaria")

## Dfs, tabelas e gráficos
library(tidyverse)
library(summarytools)  # Resumos descritivos de dados
library(kableExtra)    # Tabelas HTML/LaTeX bonitas
library(stargazer)     # Gerar tabelas resumo
library(hrbrthemes)    # Temas gráficos para ggplot2
library(ggcorrplot)    # Gráficos de correlação


# Efeitos fixos simples ou two-way
library(plm)

## Efeitos fixos within
library(fixest)


#........................................
#### 1. DATAFRAME PRINCIPAL ####
#........................................

df <- read.csv("2_BASE_COMPLETA_H1_PRECARIA.csv")

