# Inventário de fontes e suporte

| Fonte | Material local | Cobertura utilizada e limite |
|---|---|---|
| CONAB | Metadados, agregados e 45.360 células extraídas, com hashes e origem no complemento auditado | 188 planilhas; 158 candidatas no alvo; 85 estritas. Referências modais, não gastos municipais observados. |
| BCB SGS3698 | JSON oficial e CSV mensal com hashes exatos | 357 meses, janeiro de 1997 a setembro de 2026; venda, média mensal, BRL/USD. Só data-base aplicável. |
| CPI-U CPIAUCNS | CSV auditado da base3 | Até dezembro de 2024; média de 2024 como base, mesma regra da receita v4. |
| IMEA | Extrato regional com 195 registros, hash exato; URLs e hashes dos XLSX | 28 abas; safras e períodos originais preservados. Consolidados sem data nominal suficiente e estimativas futuras separados. XLSX brutos no ambiente principal, não locais. |
| Metodologia IMEA | Proveniência da página oficial e relato de ruptura em setembro de 2020 | PDF oficial retornou 404 no ambiente principal; não foi construída ponte metodológica. |

Os hashes de cada entrada estão em fontes/manifesto_entradas.json. A reprodução das tabelas usa apenas os extratos locais, sem acesso à rede. A reconstrução dos extratos desde os XLSX IMEA permanece dependente dos brutos preservados no ambiente principal; os endpoints públicos fornecem a publicação corrente, não um vintage imutável. Os arquivos originais de notas e auditoria regionais já estão materializados e conferidos por hash. Os alertas transmitidos sobre rótulos e asteriscos foram conservadoramente registrados, sem inferir sua associação a notas com associação ambígua.

## Documentação regional conferida

Os arquivos `fontes/imea/imea_regional_source_notes.csv` (143 notas) e `fontes/imea/imea_regional_audit.json` foram materializados e tiveram identidade binária confirmada com os SHA256 enviados pelo ambiente principal. O construtor confronta as 28 abas, 195 registros, praças e linhas de COE/COT/CT com o audit original. Nenhum valor de custo mudou.

A nota Milho_Safra_ALTA_afl!A81 confirma início do acompanhamento de Alta Floresta na safra 2025/26; os rótulos antigos vazios não representam custos históricos disponíveis. Milho_Safra_ALTA_nmt!A81 registra que Nova Mutum deixa de integrar o Projeto CPA-MT a partir de 2026. Indice!A85 descreve mudança de pacote tecnológico de soja em 2025/26; não permite associar automaticamente os asteriscos de Brasnorte 2023/24 e Marcelândia 2022/23. A produtividade modal é levantada no painel de produtores e pode diferir do boletim de safra. O arrendamento utiliza saca de soja e participação da área da cultura. Não foram deduzidos mês nominal, equivalência de conceitos ou valores ausentes dessas notas.

Os dez valores monetários por planilha CONAB e os três conceitos COE/COT/CT por coluna IMEA não são observações independentes. Agregados e componentes são relacionados contabilmente. As contagens de valores não aumentam o número de localidades, safras ou unidades de referência.
