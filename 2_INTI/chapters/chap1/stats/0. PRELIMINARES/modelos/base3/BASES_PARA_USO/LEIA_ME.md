# Bases H1 para uso manual — base3 v4

| Arquivo | Conteúdo | Linhas × colunas |
|---|---|---:|
| [BASE_COMPLETA_H1.csv](BASE_COMPLETA_H1.csv) | Todos os grupos, na ordem original | 3.384 × 70 |
| [GRUPO_1_AMBIENTAIS.csv](GRUPO_1_AMBIENTAIS.csv) | Grupo 0 + 22 variáveis ambientais | 3.384 × 29 |
| [GRUPO_2_ECONOMICOS.csv](GRUPO_2_ECONOMICOS.csv) | Grupo 0 + 33 variáveis econômicas | 3.384 × 40 |
| [GRUPO_3_INSTITUCIONAIS.csv](GRUPO_3_INSTITUCIONAIS.csv) | Grupo 0 + 5 variáveis institucionais | 3.384 × 12 |
| [GRUPO_4_OUTROS.csv](GRUPO_4_OUTROS.csv) | Grupo 0 + 3 outras variáveis | 3.384 × 10 |
| [DICIONARIO.csv](DICIONARIO.csv) | Dicionário v4 aprovado, 70 variáveis | — |

Os sete campos `0_` são idênticos em todos os recortes, com a mesma ordem de linhas. Chave única: `0_codigo_ibge` + `0_ano`; 141 unidades territoriais, 2001–2024. Os demais campos conservam seus nomes, grupos e valores originais. Não foram adicionados custos nem estimados modelos. A base completa e o dicionário foram movidos sem alteração de bytes.

CSV UTF-8, separador vírgula e decimal ponto. Células vazias continuam ausentes; zero continua zero. Não há metadados de tipos embutidos em CSV: mantenha os tipos definidos no dicionário e importe o código IBGE como identificador, sem converter ausências em zero. Cada recorte contém apenas as colunas existentes do grupo; não representa seleção econométrica nova.

**Para editar manualmente, salve uma cópia de trabalho fora desta pasta gerada.** `../separar_grupos_v4.py` e o builder v4 recusam sobrescrever arquivos divergentes. Para reconstruir, preserve suas edições e use checkout separado ou destino vazio. Não há opção de sobrescrita forçada. Para reunir grupos, faça junções um a um pela chave, verificando unicidade e igualdade de todos os campos `0_`; não empilhe linhas.

Fontes, fórmulas, limites territoriais e de interpretação permanecem documentados em [README_V4](../README_V4.md) e no dicionário. Histórico v1–v3 intacto. Scripts, testes, hashes e mapa de movimentação ficam fora desta pasta.
