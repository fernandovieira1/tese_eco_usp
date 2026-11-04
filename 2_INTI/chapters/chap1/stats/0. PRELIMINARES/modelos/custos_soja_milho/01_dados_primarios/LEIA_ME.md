# Etapa 1 — referências originais de custos de soja e milho

Abra **[CUSTOS_ORIGINAIS_SOJA_MILHO.csv](CUSTOS_ORIGINAIS_SOJA_MILHO.csv)**. São 4.345 registros em formato longo, extraídos dos arquivos já preservados no repositório: uma linha por série, conceito e unidade. O [dicionário](DICIONARIO.csv) descreve os campos. Vazio significa NA; os 60 valores ausentes do IMEA foram mantidos.

| Fonte e cultura | Referências de origem | Conceitos | Registros |
|---|---:|---|---:|
| CONAB soja | 99 abas | A–J, cada um em R$/ha e R$/60 kg | 1.980 |
| CONAB milho 1ª safra | 17 abas | A–J, cada um em R$/ha e R$/60 kg | 340 |
| CONAB milho 2ª safra | 72 abas | A–J, cada um em R$/ha e R$/60 kg | 1.440 |
| IMEA soja GMO | 105 colunas de período | COE, COT e CT, R$/ha | 315 |
| IMEA milho alta tecnologia | 90 colunas de período | COE, COT e CT, R$/ha | 270 |

Por conceito e unidade, CONAB tem 99 registros de soja, 17 de milho 1ª e 72 de milho 2ª. Cada conceito IMEA tem 105 registros de soja (95 numéricos) e 90 de milho (80 numéricos). As referências não são observações independentes de cada conceito. Custos em ha e por saca são apresentações distintas da mesma planilha; não devem ser somados. A–J incluem blocos contábeis e totais sobrepostos: não somar os dez conceitos. Componentes individuais e participações percentuais não integram este CSV.

## O que foi preservado

Valores monetários originais, sem conversão para USD, deflação, mediana regional, fallback, interpolação ou previsão dos nossos modelos. Não há atribuição municipal, pecuária, margem ou alteração da base H1. Referências estaduais IMEA são publicadas pela instituição, não agregações nossas. Milho IMEA permanece sem classificação automática em primeira/segunda safra.

O inventário não foi filtrado ao painel 2001–2024: as safras preservadas abrangem 1997–2027 no conjunto. Referências modais/estimadas e marcadores Ex-Ant da CONAB, estimativas com asterisco do IMEA e períodos posteriores a 2024 permanecem explicitamente identificados. São publicações originais das instituições, não previsões municipais geradas pelo projeto. Inclusão nesta pasta não valida uso econométrico ou informação disponível ex ante.

A–J são os códigos já classificados no extrato CONAB; `conceito_rotulo_original` e a flag `formula_letra_inconsistente` preservam casos de letra impressa divergente. Nenhuma nova correção foi feita. H = custo operacional; J = total, incluindo renda dos fatores. COE/COT/CT são conceitos IMEA, sem equivalência presumida com CONAB. O rótulo nominal CONAB foi mantido; no IMEA, R$/ha é a unidade declarada, mas a data nominal dos consolidados não foi confirmada.

## Rastreabilidade e limites

Cada registro aponta para o arquivo e a linha do extrato, série, aba e célula de origem. CONAB também conserva localidade da aba e do cabeçalho separadamente. Flags históricas, ambiguidades geográficas e notas de origem permanecem nos campos JSON. As flags CONAB são da avaliação histórica da série em hectare e não constituem uma nova auditoria de elegibilidade de cada valor por saca. Não foram aplicadas para excluir registros.

Conferimos os 3.760 valores CONAB, texto e número, contra os extratos de células; os 585 campos IMEA, inclusive 60 vazios, contra o extrato regional de COE/COT/CT. Os XLS/XLSX originais não estão nesta entrega e não foram reextraídos. Portanto, a validação comprova fidelidade aos extratos preservados, não uma nova conferência independente das planilhas oficiais. Hashes das planilhas IMEA são os documentados na origem. Notas integrais disponíveis por aba/índice foram preservadas no CSV.

Fontes: [extratos históricos](../../base_custos_investigacao/historico/v1_publicada/fontes/), [proveniência oficial documentada](../../base_custos_investigacao/historico/v1_publicada/fontes/PROVENIENCIA_OFICIAL.md). Snapshot Git de entrada: `94073c485e892ca158bef8721fba803a4361ccb7`.

Reprodução e verificações: `python ../processamento/separar_referencias.py --out /diretorio/novo` (caminho do script relativo a esta pasta). O destino deve ser inexistente. A rotina confere células, chaves, culturas e lacunas, imprime contagens e hashes, e recusa sobrescrita. Relatório técnico local: `2_INTI/audit/custos_soja_milho/validacao_01.json`.
