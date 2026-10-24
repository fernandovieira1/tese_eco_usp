# Abra CUSTOS_MUNICIPAIS_CANDIDATOS.csv

Dataframe separado para avaliação: **3.384 linhas (141 municípios ×2001–2024), sete índices H1 idênticos e27 custos em colunas**. DICIONARIO.csv explica cada alternativa. Os27 custos não são27 variáveis independentes; sistemas, fontes, conceitos e moedas permanecem separados.

Hierarquia: referência regional válida, inclusive praça única com suporte fraco; faltando, referência estadual **publicada** compatível da mesma fonte, atividade, sistema, conceito, moeda e ano. Sem ambas, NA (célula vazia), nunca zero imputado. Nenhuma interpolação temporal ou multiplicador municipal. Não há fallback estadual CONAB compatível nas entradas.

Agricultura CONAB: R$/ha e USD2024/ha separados. IMEA agrícola: R$/ha nominal, milho sem harmonização automática em1ª/2ª safra. Pecuária: R$/arroba VENDIDA nominal, nunca por hectare. Ano agrícola é fim da safra explícita. Não são custos reais observados por município nem informações exante comprovadas.

[Metadados por município/ano/variável](../resultados/METADADOS_CUSTOS_MUNICIPAIS.csv): regional/estadual/ausente, fonte, sistema, conceito, moeda, ano, n_pracas e suporte. [Cobertura antes/depois](../resultados/COBERTURA_FALLBACK.csv). [Referências regionais](../resultados/REFERENCIAS_REGIONAIS.csv) e [estaduais publicadas](../resultados/REFERENCIAS_ESTADUAIS_PUBLICADAS.csv) permitem rastrear valores. O cenário conservador está fora desta pasta, em resultados/cenario_conservador.

**CANDIDATO, não aprovado para incorporação.** Nenhuma coluna foi incorporada à BASE_COMPLETA_H1.csv ou ao grupo2. A publicação desta pasta não constitui aprovação para incorporar. Faça cópia para trabalho manual; reconstrução usa diretório novo, sem sobrescrever edições.
