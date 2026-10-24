# Exclusões adicionais CONAB e relação com o piloto

A unidade é planilha/tecnologia/praça/safra. A classificação estrita passou de 87 para 85 séries (soja de 34 para 32; milho inalterado). Vinte valores agregados saem do conjunto estrito e permanecem no completo e na quarentena, sem correção dos valores originais. Todas as identidades entre agregados passam; a exigência nova é a reconciliação dos seis blocos de componentes A/B/C/E/F/I.

| ID e aba | Safra/data-base | Motivo exato |
|---|---|---|
| 6a58c6f0f5837c30 — OGM-P. do Leste-MT-2011 | 2011/12; maio de 2011 | Bloco A: soma dos 25 componentes R$937,66/ha versus agregado R$976,78/ha; resíduo −R$39,12/ha, acima da tolerância absoluta R$0,05/ha. |
| f121da66bd98194b — OGM-Sorriso-MT-2011 | 2011/12; maio de 2011 | Bloco A: item 8 Sementes R$118,00/ha (linha25,coluna10) e subitem 8.1 Royalties R$36,56/ha (linha26,coluna10) ambos positivos. Não está demonstrado se royalties são adicionais ou já incluídos. Por isso a soma fica não verificável, não é declarada divergência aritmética nem se escolhe uma soma. Agregado A original R$876,14/ha. |

Ambas aparecem em base2/complemento_conab/resultados_piloto/amostra_modal_piloto.csv (87 linhas), com conceito H original R$1.421,40/ha e R$1.280,61/ha, respectivamente. Os alvos usados naquele piloto são BRL reais de dezembro de 2024 via IPCA, não USD2024 desta base paralela.

Consulta somente de leitura confirmou cada ID nos holdouts espaciais de sua praça em previsoes_somente_holdouts.csv (B0_media_cultura, B1_media_tecnologia, M1 e M2) e ridge_previsoes_holdout.csv. São dez linhas de previsões que referenciam as duas unidades, não dez observações independentes. A amostra de soja do piloto contém essas séries que não satisfazem o critério ampliado atual. As métricas antigas continuam sendo resultados daquela amostra e não validam automaticamente o novo conjunto de 85 séries. Retirar só seus erros dos holdouts também não equivaleria a refazer a validação, pois a mudança de amostra pode alterar treinos e seleção interna. Não foi medido o impacto numérico em MAE, coeficientes ou gates, nem reestimado qualquer modelo. O piloto e suas decisões foram preservados integralmente; não se afirma melhora ou reversão do diagnóstico anterior.
