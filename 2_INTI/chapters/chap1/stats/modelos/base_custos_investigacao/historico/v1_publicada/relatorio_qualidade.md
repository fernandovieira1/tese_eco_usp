# Qualidade — núcleo CONAB/BCB concluído, IMEA com referência separada

Foram lidas integralmente45.360 células dos três extratos CONAB. Chave de agregado:planilha×conceito; dez conceitos por planilha.188 planilhas/1.880 valores no universo,158/1.580 candidatas temporais/territoriais,85/850 estritas após a auditoria adicional dos componentes. Não são observações de gastos municipais.

-752/752 identidades entre agregados em R$/ha passam. Critérios herdados de unidades e participações constam em flags e fontes/validacoes*.csv.
-1.124/1.128 blocos de componentes reconciliados. Uma diferença de−39,12BRL/ha e três hierarquias sementes/royalties ambíguas; dois desses quatro registros eram estritos anteriormente. Não alteramos dados nem critérios antigos.
-7.027 linhas de componentes:6.684 numéricas,343 cabeçalhos sem valor com subitens;2.905 zeros numéricos preservados.2.938 componentes elegíveis no estrito atual. Não interpretar cabeçalho vazio como zero nem somar agregados e subitens duas vezes.
-Agregados nominais sem ausentes/negativos/zeros; isso descreve os valores existentes, não cobertura completa de localidades ou anos. Ausência de planilha não gera linha de custo zero.
-188 datas-base:128 mensais,60 diárias; cotação usada é média mensal de venda mesmo para referência diária (aproximação documentada).
-126 planilhas marcadas Ex-Ant no completo;60 no estrito. Ausência do marcador não transforma custo modal em gasto realizado.
-SGS3698:357 meses positivos consecutivos; JSON/CSV iguais e hashes do parent conferidos.188 planilhas com mês cambial;179 com CPI.1.790 custos convertidos,90NA sem CPI posterior a2024.850 valores estritos convertidos. O mês de preços determina moeda; safra e ano da aba são preservados separadamente.
-CPI-U médio2024=313,6888333333333 e arquivo hash iguais à rotina publicada de receitasbase3v4. Não há uso de IPCA na conversão.
-Sete testes aprovados, notebook com oito células de código executadas sem erro, duas construções isoladas iguais byte a byte. Ver validacao_reproducao.json e manifesto.json.
-Todos os arquivos base3 publicados no commit4afd654700f666e773a2bf931575fc1cdba0ecbb conferidos byte a byte; complementos/fontes copiados preservados. Sem regressão, imputação, commit ou push.

## IMEA incorporado com limites

Extrato regional oficial195 registros/28 abas,585 células,525numéricas/60ausentes,hashCSV conferido.65 registros/195valores elegíveis apenas para descrição no alvo, após testar número,ordemCOE<=COT<=CT,safra e ausência***.Todos585 permanecem em quarentena para comparabilidade:componentes/método integral/data nominal não confirmados. NenhumUSDIMEA calculado. A coluna de mês dos consolidados fica vazia; não usar data do download. Safras regionais não são realinhadas por posição. Dois casos*** não associados arbitrariamente à nota de2025/26.

Dois pacotes anteriores truncados não foram usados. Do último pacote foi materializado o CSV regional íntegro, verificado por CRC/tamanho/SHA256; hashZIP inteiro não foi certificado localmente. BrutosXLSX no parent, não locais. PDF metodológico404; downloadlocalXLSX403. São limites de acesso documentados, não autorização recusada. Não há equivalência contábil CONAB/IMEA nem custo municipal estimado.

## Documentação regional conferida

Os arquivos `fontes/imea/imea_regional_source_notes.csv` (143 notas) e `fontes/imea/imea_regional_audit.json` foram materializados e tiveram identidade binária confirmada com os SHA256 enviados pelo ambiente principal. O construtor confronta as 28 abas, 195 registros, praças e linhas de COE/COT/CT com o audit original. Nenhum valor de custo mudou.

A nota Milho_Safra_ALTA_afl!A81 confirma início do acompanhamento de Alta Floresta na safra 2025/26; os rótulos antigos vazios não representam custos históricos disponíveis. Milho_Safra_ALTA_nmt!A81 registra que Nova Mutum deixa de integrar o Projeto CPA-MT a partir de 2026. Indice!A85 descreve mudança de pacote tecnológico de soja em 2025/26; não permite associar automaticamente os asteriscos de Brasnorte 2023/24 e Marcelândia 2022/23. A produtividade modal é levantada no painel de produtores e pode diferir do boletim de safra. O arrendamento utiliza saca de soja e participação da área da cultura. Não foram deduzidos mês nominal, equivalência de conceitos ou valores ausentes dessas notas.

Os dez valores monetários por planilha CONAB e os três conceitos COE/COT/CT por coluna IMEA não são observações independentes. Agregados e componentes são relacionados contabilmente. As contagens de valores não aumentam o número de localidades, safras ou unidades de referência.
