# Avaliação ampliada e referências regionais candidatas

Nenhuma incorporação à H1 autorizada. Resultados descritivos e preditivos não causais.

| Análise | N | Praças | Anos | Decisão |
|---|---:|---:|---:|---|
| soja__ampliada_comparativa_pooled | 82 | 3 | 23 | gate_passou_somente_polos |
| soja__estrita_robustez_pooled | 32 | 3 | 18 | gate_nao_passou |
| soja__ampliada_sistema_OGM | 44 | 3 | 17 | gate_nao_passou |
| soja__ampliada_sistema_convencional explícita | 3 | 3 | 1 | suporte_insuficiente |
| soja__ampliada_sistema_não declarada | 35 | 3 | 17 | gate_nao_passou |
| milho_1a__ampliada_comparativa_pooled | 13 | 1 | 13 | suporte_insuficiente |
| milho_1a__estrita_robustez_pooled | 9 | 1 | 9 | suporte_insuficiente |
| milho_1a__ampliada_sistema_não declarada | 13 | 1 | 13 | suporte_insuficiente |
| milho_2a__ampliada_comparativa_pooled | 62 | 4 | 24 | gate_passou_somente_polos |
| milho_2a__estrita_robustez_pooled | 43 | 4 | 21 | gate_passou_somente_polos |
| milho_2a__ampliada_sistema_OGM | 41 | 4 | 12 | gate_passou_somente_polos |
| milho_2a__ampliada_sistema_não declarada | 21 | 4 | 15 | suporte_insuficiente |

Pooled é apenas comparação ao desenho anterior, não mistura tecnológica para atribuição. Avaliação primária é separada por sistema. Estrita é robustez; geografia não resolvida não define folds. Métricas e perdas completas em resultados/avaliacao. Nenhum resultado aprova previsão municipal. Pecuária não foi estimada: cinco anos consolidados no máximo, sistemas separados, sem preditor específico validado.

{
  "referencias_regionais": 183,
  "linhas_painel": 3384,
  "colunas_painel": 34,
  "series_regionais": 11,
  "variaveis_custo": 27,
  "variaveis_com_suporte": 27,
  "nao_regionalizados": 48,
  "ids_H1_mapeados": 141,
  "municipal_validado": false,
  "incorporacao_aprovada": false
}

| Candidata | Cobertura município-ano % | Recomendação |
|---|---:|---|
| CONAB / soja / não declarada / conab_h / nominal | 28.93 | candidata_descritiva_requer_aprovacao |
| CONAB / soja / não declarada / conab_h / usd2024 | 28.93 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / recria_engorda / coe / nominal | 14.63 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / recria_engorda / cot / nominal | 14.63 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / recria_engorda / ct / nominal | 14.63 | candidata_descritiva_requer_aprovacao |
| CONAB / milho_2a / OGM / conab_h / nominal | 25.68 | candidata_descritiva_requer_aprovacao |
| CONAB / milho_2a / OGM / conab_h / usd2024 | 25.68 | candidata_descritiva_requer_aprovacao |
| IMEA_agricola / soja / SOJA GMO / imea_coe / nominal | 10.99 | candidata_descritiva_requer_aprovacao |
| IMEA_agricola / soja / SOJA GMO / imea_cot / nominal | 10.99 | candidata_descritiva_requer_aprovacao |
| IMEA_agricola / soja / SOJA GMO / imea_ct / nominal | 10.99 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / ciclo_completo / coe / nominal | 3.25 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / ciclo_completo / cot / nominal | 3.25 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / ciclo_completo / ct / nominal | 3.25 | candidata_descritiva_requer_aprovacao |
| CONAB / soja / OGM / conab_h / nominal | 38.68 | candidata_descritiva_requer_aprovacao |
| CONAB / soja / OGM / conab_h / usd2024 | 38.68 | candidata_descritiva_requer_aprovacao |
| IMEA_agricola / milho_safra_nao_harmonizada / MILHO ALTA TECNOLOGIA / imea_coe / nominal | 10.99 | candidata_descritiva_requer_aprovacao |
| IMEA_agricola / milho_safra_nao_harmonizada / MILHO ALTA TECNOLOGIA / imea_cot / nominal | 10.99 | candidata_descritiva_requer_aprovacao |
| IMEA_agricola / milho_safra_nao_harmonizada / MILHO ALTA TECNOLOGIA / imea_ct / nominal | 10.99 | candidata_descritiva_requer_aprovacao |
| CONAB / soja / convencional explícita / conab_h / nominal | 2.28 | candidata_descritiva_requer_aprovacao |
| CONAB / soja / convencional explícita / conab_h / usd2024 | 2.28 | candidata_descritiva_requer_aprovacao |
| CONAB / milho_1a / não declarada / conab_h / nominal | 8.45 | candidata_descritiva_requer_aprovacao |
| CONAB / milho_1a / não declarada / conab_h / usd2024 | 8.45 | candidata_descritiva_requer_aprovacao |
| CONAB / milho_2a / não declarada / conab_h / nominal | 16.58 | candidata_descritiva_requer_aprovacao |
| CONAB / milho_2a / não declarada / conab_h / usd2024 | 16.58 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / cria / coe / nominal | 14.98 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / cria / cot / nominal | 14.98 | candidata_descritiva_requer_aprovacao |
| IMEA_pecuaria / pecuaria / cria / ct / nominal | 14.98 | candidata_descritiva_requer_aprovacao |

O painel tem todas as chaves H1, mas custos somente nos domínios com suporte. Anos de fim de safra são convenção explícita e não data de informação. Fontes retrospectivas, sistemas e moedas não intercambiáveis. Cenário principal aceita uma praça válida com suporte fraco; cenário conservador exige duas. Nenhum deles prova representatividade. Mediana e IQR não são intervalo de confiança. Pequeno número de regiões exige inferência cautelosa agrupada por região e tempo; replicar custos não multiplica unidades informativas. Não usar estas colunas como custos municipais observados ou como variáveis conhecidas exante. Aprovação do autor é necessária para incorporar qualquer candidata.
