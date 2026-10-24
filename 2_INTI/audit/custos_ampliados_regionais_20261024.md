# Avaliação ampliada e regionalização candidata — 24/10/2026

Escopo autorizado: três etapas exclusivamente na base paralela, sem publicação ou incorporação. Política futura registrada em RESEARCH_PROTOCOL.md: atualização simultânea da base completa e grupo correspondente, grupo0 idêntico e reconstrução por chave/colunas. Custos dependem de aprovação futura explícita.

Entrada e decisão científica documentadas em ../chapters/chap1/stats/modelos/base_custos_investigacao/etapa_regional_v2/README.md. Estratégia fixada antes dos testes; seu SHA está em proveniencia.json. Seleção publicada reconstruída sem restaurar BASE_PARA_USO removida pelo usuário. Snapshot247 agrícolas/124 pecuárias;157 CONAB geograficamente resolvidas para avaliação. Seis conflitos não usados para localização. Regra>10% preservada, sem reativar filtro contábil estrito.

Etapa1 concluída: benchmark, OLS e ridge, folds por praça e temporais, parâmetros e previsões guardados. Soja por sistema não aprovada; milho2 OGM passa apenas diagnóstico dos polos, com16/20 casos temporais fora do domínioX. Milho1 e pecuária insuficientes. Etapas2/3 concluídas:183 referências regionais; painel3384×203,27 custos candidatos,22 com suporte em algum domínio, cincoNA completos. Medianas igualmente ponderadas por praça, mínimo duas para atribuição por conceito/moeda. Nenhuma previsão de modelo foi usada para preencher o painel. Fonte/sistema/moeda/conceitos separados; sem custos pecuários porha.

Validação final: cinco testes PASS, incluindo duas reproduções independentes em diretórios temporários contendo somente script, fontes e proveniência; manifestos CSV idênticos. Três notebooks executados PASS, saídas temporárias comparadas porhash. Todos3384 pares município-ano únicos; sete índices na ordem original; junção sem multiplicação; valores atribuídos idênticos à referência elegível; ausência preservada. Custos publicados em fontes inalterados. Sete arquivos H1 preservados porSHA; full a98dbe320efc784543cf43372a5903de32434be5871304178f2f9d49daaf1c3b.

Limites: correspondência de códigos não valida fronteiras históricas; regiõesIBGE2016 eIMEA2017 distintas; referências não são representativas probabilísticas; disponibilidade exante não demonstrada; medianas/IQR não são IC; resultados não causais. Coleta retrospectiva não deve ser tratada como informação conhecida antes da decisão. Estado publicado do repositório permanece inalterado: sem staging, commit oupush. Outputs locais novos estão sob etapa_regional_v2, ignorada peloGit; publicação futura requer seleção explícita.

## Revisão solicitada: referência única no cenário exploratório

Cenário principal agora>=1 praça válida com suporte_fraco_uma_praca; >=2 preservado como conservador. Os110 grupos de praça única não são erros oficiais. Painel candidato3384×34 (7 índices+27 custos alternativos), todos27 com algum valor; conservador22. Metadados91368 linhas por chave/variável separados foraUSO. Quatro arquivos no ponto de entrada. Cenário anterior guardado em historico_cenario_duas_pracas. Seleção10%, exclusões geográficas/períodos e valores de avaliação inalterados. Ver comparacao_cenarios.csv e COBERTURA_PRINCIPAL.md.

## Publicação autorizada do dataframe candidato com fallback

Autorização explícita para publicar etapa paralela completa e avaliação ampliada emmain; não incorporar custos à principal/grupo2. Arquivo ativo:USO_CANDIDATOS/CUSTOS_MUNICIPAIS_CANDIDATOS.csv,3384×34. Fallback apenasestadualpublicadaIMEA daabaestadual, matchingfonte/atividade/sistema/natureza/conceito/moeda/ano/duração. SemfallbackCONABcompatível; semproxyestadualderivada. Regionalprioritário mesmo n_pracas=1, suporte fraco. Fontes e seleção10% intactas; semnovas especificações econométricas. Referências e metadados foraUSO; originalapenasregionalpreservado. Teste adicional verifica prioridade, compatibilidade literal, valor publicado exato eNA. CI/commit/remoto serão registrados após publicação.

Verificação pré-publicação:6 testes PASS (61,587s), incluindo duas reproduções isoladas de todosCSVs e regrasfallback. Notebooks01–04 executadosPASS. ManifestoCSV e sete hashesH1 conferidos. LinksMDativos válidos. Nenhum workflow em.github no checkout.
