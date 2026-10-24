# Centralização da base3 v4 e recortes por grupo — 24/10/2026

Autorização: usuário solicitou pasta centralizadora, base completa movida e quatro recortes com todos os campos do grupo 0; autorizou publicação em main. Custos pausados, sem alterações nesta entrega.

Entrada publicada: painel_h1_base3_v4.csv, 3.384 linhas e 70 campos, SHA256 a98dbe320efc784543cf43372a5903de32434be5871304178f2f9d49daaf1c3b. Movida byte a byte para base3/BASES_PARA_USO/BASE_COMPLETA_H1.csv. Dicionário aprovado movido byte a byte para DICIONARIO.csv, SHA256 8e8a22d3d75742aaa355cfacbbe4d0eb1d16bc14c77fd4459d4db1daa620c4e5. Mapa de movimentação e manifesto permanecem fora da pasta de uso.

Pasta central contém somente sete arquivos: base completa, quatro grupos, dicionário e LEIA_ME. Cada grupo contém os sete campos 0_ na ordem original, seguidos apenas dos próprios campos na ordem original. Grupo 1: 22 variáveis, 29 colunas; grupo 2: 33 variáveis, 40 colunas; grupo 3: 5 variáveis, 12 colunas; grupo 4: 3 variáveis, 10 colunas. Todos têm 3.384 linhas, 141 unidades e anos 2001–2024, com chave única código IBGE/ano. Nenhum novo agrupamento conceitual ou seleção econométrica.

CSV lido como texto, sem inferência de tipos, conversão de NA/zeros ou recálculo de valores. Cobertura disjunta e exata dos grupos 1–4, identidade integral dos sete campos 0_, ordem das linhas e reconstrução pela chave testadas. Reconstrução também coincide byte a byte com o CSV completo. CSV não incorpora schema de tipos: dicionário e interpretação originais continuam necessários ao importar.

Builder, testes, notebook e README v4 usam os novos caminhos. Scripts validam arquivos gerados antes de escrever e recusam conteúdo divergente, protegendo edições manuais. O usuário deve salvar cópias de trabalho fora da pasta gerada; para reconstruir, usar checkout separado ou destino vazio. Não há sobrescrita forçada. Teste simula edição no grupo 2 e confirma interrupção sem modificar nenhum recorte.

Verificações: seis testes v4 e três testes dos grupos PASS; notebook v4 executado PASS. Duas reproduções em clones locais limpos com a alteração preparada, removendo os seis CSVs de uso antes da reconstrução: build PASS, nove testes PASS por clone, hashes idênticos para todos os sete arquivos. Evidência detalhada em centralizacao_base3_v4_validacao.json. Git diff --cached --check PASS. Teste histórico confirma arquivos v1–v3 publicados byte a byte. Custos não possuem diff. Nenhuma regressão foi estimada.

Apenas base3 v4, scripts/recortes associados e estas auditorias entram no commit. Não há workflows em .github/workflows. O hash remoto será confirmado após push normal, sem force. Limites científicos e territoriais são os já documentados no dicionário e README_V4; a divisão em arquivos não acrescenta validação de causalidade ou representatividade.
