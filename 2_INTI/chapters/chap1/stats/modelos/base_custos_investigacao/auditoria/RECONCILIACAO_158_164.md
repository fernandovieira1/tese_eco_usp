# Reconciliação de 158 candidatas com 164 referências CONAB

Não houve mudança de recorte temporal. A flag preservada `elegivel_periodo_2001_2024` foi conferida independentemente para todas as 188 referências: safra inicial >= 2001, final <= 2024, início <= final. Resultado: 164 dentro e 24 fora. Não se seleciona apenas pelo início, pelo ano da aba nem pela data-base. Safra 2000/01 e 2024/25 ficam fora. Data-base determina a conversão monetária disponível, não substitui a safra.

O número 158 era o conjunto `candidato_descritivo_periodo`, já filtrado além do período. Seus seis registros a menos têm conflito de praça; todos têm `identidades_ha_ok=True`. Portanto, chamá-lo simplesmente de universo temporal era impreciso. A recuperação bruta de 79 referências versus 85 estritas compreende 73 das 158 candidatas anteriores e essas seis referências com problema de identificação. Não houve recuperação por ampliação temporal.

| ID | Aba | Safra | Data-base | Ressalva |
|---|---|---|---|---|
| 50293165740cd776 | C. Novo do Parecis-MT-2006 | 2006/2007 | 2006-05-31 | Cabeçalho Sapezal/Campo Novo do Parecis ambíguo |
| 6a59ce79df2ccf1e | C. Novo do Parecis-MT-2007 | 2007/2008 | 2007-05-31 | Cabeçalho Sapezal/Campo Novo do Parecis ambíguo |
| f6d4c28f6be7fe2c | C. Novo do Parecis-MT-2008 | 2008/2009 | 2008-03-31 | Cabeçalho Sapezal/Campo Novo do Parecis ambíguo |
| 50f3228c7ba40f87 | C. Novo do Parecis-MT-2009 | 2009/2010 | 2009-05-31 | Cabeçalho Sapezal/Campo Novo do Parecis ambíguo |
| c097dd0338204e46 | C. Novo do Parecis-MT-2010 | 2010/2011 | 2010-05-31 | Cabeçalho Sapezal/Campo Novo do Parecis ambíguo |
| ce710ff2093a555b | Sorriso-MT-2014 | 2014/2014 | 2014-03 | Cópia documental consolidada; cabeçalho Primavera |

As cinco referências de soja não recebem município/região resolvidos. A referência Sorriso-MT-2014 (`ce710ff2093a555b`, Ex-Ant=True) possui cabeçalho Primavera do Leste e valores monetários idênticos à referência `b622ffb932346f2b`. Ambas têm safra 2014/14 e data-base março/2014; uma linha documental é consolidada na apresentação principal, com ambos IDs e conflito geográfico. Ex-Ant não foi convertido em gasto realizado: é orçamento modal estimado para safra no recorte, explicitamente identificado. Referências futuras não entram por esse motivo.

| Universo | Linhas de referência | Valores monetários nominais presentes |
|---|---:|---:|
| CONAB, todos os períodos | 188 | 1.880 |
| CONAB, recorte antes de consolidar cópia | 164 | 1.640 |
| CONAB, arquivo principal | 163 | 1.630 |
| IMEA agricultura, todos os períodos | 195 | 525 |
| IMEA agricultura, recorte e arquivo principal | 84 | 201 |
| IMEA pecuária, todos os períodos | 196 | 468 |
| IMEA pecuária, recorte e arquivo principal | 124 | 279 |

Valores monetários são conceitos, não observações independentes: A–J e COE/COT/CT não multiplicam N. IMEA agricultura contém 585 posições de conceitos em todos os períodos, das quais 525 numéricas; 60 ausentes. Pecuária contém 588 posições, 468 numéricas e 120 ausentes. No recorte agrícola IMEA são 252 posições, 201 numéricas e 51 ausentes; pecuária 372 posições, 279 numéricas e 93 ausentes.

A raiz contém apenas README.md e as pastas BASE_PARA_USO, processamento, auditoria, resultados e historico. BASE_PARA_USO contém os dois CSVs largos, dicionário e LEIA_ME; nenhuma tabela auxiliar. O histórico anterior permanece integral, com mapa de realocação e hashes.

Correspondências geográficas usam nomes normalizados exatos e referência IBGE DTB2016v2, separada de regiões IMEA. Conflitos não recebem código por inferência. Isso identifica a praça de referência quando resolvida, não valida limites territoriais 2023, unidades compostas do painel, representatividade regional, custo municipal ou bioma. Flags territoriais continuam False. Nenhum dado foi juntado à base3.

Verificação adicional: os 188 indicadores temporais foram rederivados e todos coincidem. Nenhuma seleção, dado ou código precisou ser alterado; os seis testes, duas reproduções limpas e notebook previamente aprovados continuam aplicáveis. Esta reconciliação acrescenta documentação, sem commit/push nem reestimação.
