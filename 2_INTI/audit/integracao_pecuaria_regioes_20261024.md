# Integração de pecuária e regiões — 24/10/2026

Concluída a transferência em texto: oito arquivos pecuários e dois geográficos conferidos nos SHA256 informados. Nenhum ZIP incompleto foi usado. As entidades XML do envelope foram decodificadas na proveniência e no extrator; os hashes finais confirmam identidade byte a byte. Valores decimais, CRLF dos CSVs, notas e lacunas preservados.

Pecuária: 196 registros de período, 156 com três custos numéricos, 588 campos monetários longos, 468 numéricos e 120 ausentes. 752 células de notas. Unidade original R$/@ vendida. Sem conversão para hectare ou USD, imputação, modelo ou municipalização. Relatório independente do pai: 784 campos e196 cabeçalhos conferidos; não repetido contra XLSX neste executor.

Regiões: DTB2016v2, 141 códigos coincidem com painel, cinco mesorregiões. Um nome difere (de/do Leverger), ambos preservados. IMEA2017 separado,140 matches,PoxoréuNA. Limites territoriais/predecessores/unidadescompostas não validados; identificação por código não é harmonização espacial. 476 referências,424 identificadas;38estaduais e14 com conflito geográfico permanecem fora da classificação mesorregional. A contagem usa coluna-período e não conceitos monetários repetidos.

Cobertura das praças numéricas no conjunto de períodos, não em cada ano: CONAB soja Norte2/Sudeste1; milho1Sudeste1; milho2Norte2/Sudeste2. IMEA soja Norte10/Nordeste2/Sudeste1/Sudoeste1;milhoNorte9/Nordeste1/Sudeste1/Sudoeste1. Pecuária cria Centro-Sul2/Nordeste5/Norte5/Sudeste2;recria-engordaNorte1/Sudeste1/Sudoeste3;ciclo completoSudoeste1. Consultar CSV por ano para suporte efetivo; não confundir cobertura conjunta com cobertura anual.

Conclusão agrícola preservada: soja falha estabilidade temporal; milho1amostra insuficiente;milho2passa critérios entre praças/tempo mas não valida transferência municipal. Nenhum novo modelo regional foi ajustado em grupos pequenos. As fontes sustentam referências localizadas, não custos representativos de regiões inteiras ou biomas.

Testes: duas reproduções isoladas por integração comCSVshashesidênticos; reconciliação588valores e tipos; ausências e conflitos preservados; cobertura424reconciliada;190arquivosanteriores preservados. Dois notebooks executados, três células de código cada. Lista completa em avaliacao_preditiva/ARQUIVOS_NOVOS.md e hashes em manifesto_etapa.json.

Bloqueio de acesso delimitado: XLSX pecuário e raws geográficos permanecem apenas no pai. A tentativa ao endereço público S3 verificado retornou proxy Tunnel403; não houve recusa de aprovação. Não impede reprodução local da integração a partir dos extratos conferidos. Reextração do raw exige disponibilizar o XLSX datado; não é tratada como executada localmente.

Sem commit/push e sem alteração base3 ou piloto. Relatórios e bases paralelas são ignorados pelo Git; git status limpo não significa ausência desses arquivos locais.
