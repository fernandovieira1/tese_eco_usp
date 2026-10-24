# Base paralela de investigação de custos — referências nominais e USD2024

Reprodução em checkout limpo e dependências publicadas: [PUBLICACAO.md](PUBLICACAO.md). Resultados posteriores: [avaliação agrícola](avaliacao_preditiva/README.md), [pecuária](pecuaria/README.md) e [regionalização](regionalizacao/README.md).

Construída localmente em 24/10/2026. Nenhuma regressão, imputação, atribuição municipal ou publicação. Base3 v1–v4 e complementos anteriores preservados.

## O que está utilizável

`custos_referencia_completos.csv`: 1.880 valores nominais de dez conceitos por 188 planilhas. São referências modais/estimadas de cultura × praça × tecnologia × safra, não 1.880 unidades independentes nem gastos municipais observados. `series_referencia.csv` tem uma linha por planilha (conceito H).

`custos_referencia_estritos.csv`: 850 valores de 85 planilhas; soja32 (3 praças), milho1ª9 (1 praça), milho2ª44 (4 praças). `custos_quarentena.csv`:1.030 valores de103 planilhas, preservados com motivos. Cobertura estrita por safra: soja2001–2024, milho1ª2001–2010, milho2ª2001–2024, descontínua; ver `cobertura.csv` e `series_referencia.csv` para suporte efetivo. Dos188 registros,158 (1.580 valores) são candidatos nominais no recorte2001–2024 do complemento anterior; os85 estritos são um subconjunto adicional, não sinônimo de158. Arquivos completos incluem1997–2027 e projeções, explicitamente sinalizados, não observações retrospectivas de2001–2024.

`componentes_nominais.csv`:7.027 linhas, das quais6.684 numéricas e343 cabeçalhos sem valor com subitens. Somente2.938 componentes passam a elegibilidade estrita atual. Não somar agregados D/G/H/J aos componentes folha A/B/C/E/F/I; tampouco adicionar frete ou juros outra vez.

## Decisão adicional de qualidade

A auditoria anterior aprovou87 planilhas. Esta versão exige também reconciliação dos seis blocos de componentes. As752 identidades entre agregados continuam aprovadas;1.124 de1.128 blocos detalhados passam. Tolerância0,05BRL/ha, mantida como tolerância contábil de arredondamento e não ajustada para aproveitar casos.

Duas planilhas anteriormente estritas foram retiradas apenas deste subconjunto novo: soja OGM Primavera do Leste2011 (`6a58c6f0f5837c30`) soma937,66 contra custeio976,78, diferença−39,12BRL/ha; soja OGM Sorriso2011 (`f121da66bd98194b`) contém sementes e royalties positivos em hierarquia ambígua. Outros dois casos de hierarquia em2012 já não eram estritos. A inspeção das células e do intervalo entre colunas R$/ha e R$/60kg descartou usar a coluna errada nessa comparação. Não corrigimos a fonte nem assumimos que royalties sejam aditivos. O indicador de aprovação anterior permanece disponível. Os arquivos antigos não foram modificados.

## Conceitos e moeda

A=custeio, B=outras despesas/pós-colheita, C=financeiras, D=A+B+C; E=depreciação, F=outros fixos, G=E+F; H=D+G operacional; I=renda dos fatores; J=H+I total. A padronização é interna à CONAB, sem equiparar H a COT/COE IMEA por nome. Produtividade modal não é produtividade PAM. Lavoura estabelecida não inclui automaticamente custo de conversão ou implantação.

Unidade preservada: BRL nominal/ha. Meta: `BRL_nominal / cambio_BRL_por_USD_mes × CPI_medio2024 / CPI_mes`. CPI-U base média2024=313,6888333333333, igual à convenção de receitas v4. Não usar os valores já deflacionados por IPCA do piloto como nominais. O ambiente principal recuperou a série oficial SGS3698, média mensal de venda em BRL/USD. JSON e CSV recebidos conferem exatamente os hashes informados;357 meses consecutivos, janeiro1997–setembro2026. Há câmbio para188 planilhas e CPI para179:1.790 valores foram convertidos, dos quais850 de85 séries estritas elegíveis. Os90 valores restantes permanecem sem USD por falta de CPI após2024. Valores convertidos em quarentena não ganham elegibilidade por terem moeda comparável. A conversão não estende o alvo para anos após2024. Com data diária, a média cambial mensal é aproximação explicitamente indicada, não cotação diária; para safra/data-base distintas, usa-se a data-base, nunca o ano da aba.

## Fontes e bloqueios

Os três extratos CONAB locais foram lidos integralmente:45.360 células. Cópias autossuficientes, fontes Drive e hashes estão em `fontes/manifesto_entradas.json` e `FONTES_DRIVE.json`; valores e referências de célula permitem voltar ao extrato, não equivalem à conferência dos XLS originais oficiais. CPI bruto copiado da fonte já auditada da base3.

Tentativas públicas dos XLSX soja/milho IMEA, metodologia e endpoint BCB SGS3698 retornaram HTTP403 do proxy, inclusive após execução com permissão ampliada. Foi falha de acesso, não negação da revisão automática. URLs/horários em `fontes/tentativas_acesso.json`. A coleta oficial do SGS3698 foi realizada em outro ambiente pelo parent após esse bloqueio; ver `fontes/proveniencia_bcb3698.json`, JSON e CSV com hashes conferidos. A documentação complementar confirma identidade por gráfico oficial SGS; limites de acesso aos metadados brutos estão em fontes/PROVENIENCIA_OFICIAL.md. O resultado local403 não foi interpretado como ausência da série. O extrato regional de custos principais foi incorporado em tabelas separadas após conferir CRC, tamanho e SHA256 da entradaCSV; não validamos o hash do ZIP inteiro nem alegamos XLSX bruto local. A página oficial registra ruptura setembro2020 CF/CV→COE/COT/CT: https://www.imea.com.br/imea-site/relatorios-mercado-detalhe?c=1&s=3 . Não afirmar harmonização sem acesso aos arquivos/método. O parent recuperou os XLSX IMEA. Dois primeiros pacotes truncados não foram usados; o CSV regional do último pacote teve hash exatamente conferido e foi utilizado. Os XLSX permanecem no parent; URLs são publicações correntes e podem mudar. Ver fontes/PROVENIENCIA_OFICIAL.md. Não há harmonização de conceitos com base em igualdade de nomes.

## IMEA: referência separada e quarentena de comparabilidade

`custos_imea_referencia.csv`:585 células COE/COT/CT de195 registros planilha×coluna em28 abas;525 numéricas,60 ausentes.14 registros são estaduais e181 são praças de referência; a existência de nome municipal não transforma custo modal em gasto médio municipal. O extrato não inclui componentes detalhados, produtividade ou dólar compra; não inventamos esses campos.

`custos_imea_candidatos_descritivos.csv`:195 valores de65 registros (34 soja,31 milho), sendo59 de praças e6 estaduais. Critério: safra inteira dentro2001–2024, valor finito não negativo, ordemCOE<=COT<=CT e ausência de*** no rótulo. Esse teste de ordem não valida identidades dos componentes. `custos_imea_quarentena.csv` mantém TODOS585 valores para usos que dependam de comparabilidade plena. As tabelas descritiva e quarentena se sobrepõem deliberadamente: descrevem permissões de uso distintas, não partição de uma amostra validada.

Consolidados não fornecem mês nominal suficiente: USD vazio. Agosto/setembro2026 referem-se à safra2026/27, fora do alvo e sem CPI2026 neste pacote; também não convertidos. O snapshot inclui cinco safras estaduais consolidadas2021/22–2025/26, mas rótulos regionais divergem: milho AltaFloresta omite2024/25, NovaMutum omite2022/23, Marcelândia começa2022/23. Preservamos inclusive2020/21 nos rótulos que o trazem, com valores vazios; não realinhamos colunas por posição. Soja Brasnorte2023/24*** e Marcelândia2022/23*** ficam ambíguas, sem inferir a aplicação da nota de mudança2025/26. Milho alta tecnologia não é convertido automaticamente em milho2ª: o sistema permanece não confirmado no extrato. Não houve ponteCOE/COT/CT↔H/JCONAB nem comparação de margens.

## Reprodução e limites

Python3.12, biblioteca padrão: `python construir.py`; `python -m unittest test_base_custos.py`. Notebook `construcao_auditoria.ipynb` executa construção e verificações, exige nbformat/nbclient/ipykernel apenas para reexecução Jupyter. A construção não exige rede nem os complementos externos após cópia das entradas. Duas execuções isoladas verificadas em `validacao_reproducao.json`; hashes em `manifesto.json`. `dicionario_variaveis.csv` documenta grupos0/2/4, e `candidatos_incorporacao.csv` separa referência utilizável de pendência. Ausência não vira zero; zero registrado é mantido sem certificar o fenômeno econômico absoluto. Seleção por qualidade pode alterar composição temporal/tecnológica; não resolve representatividade nem identifica causalidade. Ex-Ant é indicador da fonte; sua ausência não comprova gasto realizado. Não existem custos municipais inferidos nem validação fora da amostra nesta etapa.

## Documentação regional conferida

Os arquivos `fontes/imea/imea_regional_source_notes.csv` (143 notas) e `fontes/imea/imea_regional_audit.json` foram materializados e tiveram identidade binária confirmada com os SHA256 enviados pelo ambiente principal. O construtor confronta as 28 abas, 195 registros, praças e linhas de COE/COT/CT com o audit original. Nenhum valor de custo mudou.

A nota Milho_Safra_ALTA_afl!A81 confirma início do acompanhamento de Alta Floresta na safra 2025/26; os rótulos antigos vazios não representam custos históricos disponíveis. Milho_Safra_ALTA_nmt!A81 registra que Nova Mutum deixa de integrar o Projeto CPA-MT a partir de 2026. Indice!A85 descreve mudança de pacote tecnológico de soja em 2025/26; não permite associar automaticamente os asteriscos de Brasnorte 2023/24 e Marcelândia 2022/23. A produtividade modal é levantada no painel de produtores e pode diferir do boletim de safra. O arrendamento utiliza saca de soja e participação da área da cultura. Não foram deduzidos mês nominal, equivalência de conceitos ou valores ausentes dessas notas.

Os dez valores monetários por planilha CONAB e os três conceitos COE/COT/CT por coluna IMEA não são observações independentes. Agregados e componentes são relacionados contabilmente. As contagens de valores não aumentam o número de localidades, safras ou unidades de referência.

As duas exclusões adicionais e sua presença no piloto anterior estão detalhadas em [EXCLUSOES_CONAB_E_PILOTO.md](EXCLUSOES_CONAB_E_PILOTO.md).
