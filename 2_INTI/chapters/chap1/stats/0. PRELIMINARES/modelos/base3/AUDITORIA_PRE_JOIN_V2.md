# Auditoria anterior ao apensamento — base3 v2 completa

PASS: 288 meses completos janeiro2000–dezembro2023 para DAP/soja/milho/CPI/Selic, sem duplicatas, finitos e positivos. SGS bruto extraído contém300meses2000–24; os12meses2024 não entram nos outcomes. Hashes dos CSVs SGS mensal/anual coincidem exatamente com os transmitidos pelo coletor oficial. Recalculadas24médias anuais de12meses, diferença inferior a1e-12 frente ao extrato anual independente.

DAP oficial:288valores recebidos coincidem exatamente com o XLSX Drive local. Relatório de confronto externo documenta864células iguais (DAP/soja/milho) e zero divergências. Dois leitores locais também concordam nessas864células. Arquivos XLSX têm hashes/vintages diferentes, não bytes iguais. Ambos contêm Mismatch Details; isso não prova adulteração. Fontes, hashes e limites em fontes_v2/CONFRONTO_OFICIAL.md. XLSX oficial e HTML bruto SGS permanecem no ambiente pai; não afirmar que estão locais.

CPI-U confere com manifesto; base média2024=313.6888333333333. Média dos12preços mensais deflacionados no ano anterior. Preços soja/milho preservados da v1 reconciliados com diferença máxima 1.14e-13. Razões das médias anuais reais, não médias das razões; deflator comum cancela mensalmente, mas a ponderação anual importa. Selic4189 é média temporal do nível anualizado %a.a., não acumulada ou meta. Nenhuma imputação ou modelo.

Decisão: PASS para apensar quatro campos por ano (many-to-one), preservando42colunas e3384chaves. São24valores anuais repetidos, não3384choques. DAP é proxy parcial de insumos, não custo/ha. Preços e Selic comuns são absorvidos por FEano. Vintage retrospectivo não equivale à informação disponível em tempo real; CPI2024 fixa apenas a unidade monetária.
