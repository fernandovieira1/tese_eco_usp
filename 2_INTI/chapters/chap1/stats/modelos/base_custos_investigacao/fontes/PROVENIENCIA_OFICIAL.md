# Fontes oficiais recuperadas no ambiente principal — 24/10/2026 UTC

## Câmbio BCB

SGS3698: dólar venda, média do período, mensal, unidades monetárias correntes por USD (BRL nesta amostra posterior a1994). Identidade conferida pelo parent na página oficial SGS, independentemente do JSON.

- Coleta2026-10-24T14:41:52.113660+00:00, HTTP200.
- Download: https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json&dataInicial=01/01/1997&dataFinal=30/09/2026
- Página de identidade: https://www3.bcb.gov.br/sgspub/consultarvalores/consultarValoresSeries.do?hdOidSeriesSelecionadas=3698&method=consultarGraficoPorId
- Entrada de metadados: https://www3.bcb.gov.br/sgspub/consultarmetadados/consultarMetadadosSeries.do?method=consultarMetadadosSeriesInternet&hdOidSerieSelecionada=3698
- JSON SHA256: dd618f8c7dc2e74f3be8bae947b72b9ea2a523ea35884c05427722c9511f90b9.
- CSV SHA256:1d1d250a3c4026bd5dfcfe7911852541e3e08c24ca2d3ed640113bfa38c7e906.

Os dois arquivos locais reproduzem exatamente esses hashes.357 meses únicos e consecutivos,1997-01 a2026-09; primeiro1,0429, último5,1447BRL/USD. As datas são meses de observação, não publicação. A API não retornou datas de publicação. Entrada de metadados acessível viaweb, mas iframes e requisições diretas de metadados/gráfico retornaram502; documento bruto integral de metadados não foi obtido. Não alegamos tê-lo localmente. A identificação independente vem do gráfico oficial. Bloqueios locais de proxy403 estão registrados separadamente; nenhum contorno de autenticação ou negação de autorização.

## IMEA — evidência recebida, transferência dos extratos pendente

Wrappers respondem HTML; JavaScript público ArquivoExterno.js?v=4 aponta aos endpoints abaixo, que o parent seguiu por redirecionamento normal, sem autenticação:

- Soja: https://publicacoes.imea.com.br/relatorio-de-mercado/cup-soja/8 ; coletado2026-10-24T14:42:36.882754+00:00;336.500bytes;SHA256 0a0595da15bebbcd001427c21398665f8dc2e3a4fd5b2a58b9290d6e943b08dc.
- Milho: https://publicacoes.imea.com.br/relatorio-de-mercado/cup-milho/6 ; coletado2026-10-24T14:42:36.883260+00:00;283.345bytes;SHA256 1bf6872ebf7626569610da3f1e1c42981f0fd149f9a8df591fe63d60735afbf0.

URLs são publicações correntes, não vintages imutáveis. Snapshot:2021/22–2025/26 consolidado e agosto/setembro2026 estimativas2026/27. Não é painel mensal histórico. Ano do cabeçalho não deve ser confundido com ano civil da colheita. Soja_GMO_MT:soja transgênica ponderada estadual; Milho_MT:alta tecnologia estadual. R$/ha. Dólar da planilha é COMPRA, distinto de SGS3698 VENDA. Produtividade modal vem de painel, não necessariamente do boletim de safra.

O parent conferiu924 células normalizadas B:H contra valores armazenados nos XLSX (tolerância relativa1e-14, absoluta1e-12). A:I bruto preserva notas e colunaI variação mensal, que não é nível de custo. Não recalculou fórmulas nem imputou lacunas. Os XLSX originais estão no ambiente principal, não nesta pasta. Até transferência íntegra, nenhuma dessas924 células é alegada como incorporada localmente. Os dois pacotesZIP enviados chegaram truncados e não foram decodificados ou reparados.

## Metodologia

Página oficial registra mudança CF/CV para COE/COT/CT em setembro2020, Excel substituindo PDF: https://www.imea.com.br/imea-site/relatorios-mercado-detalhe?c=1&s=3 . HTML preservado no parent com SHA256 e43c0265ae48c5e7de295b2d3e131e24db0d89a5e04325dc00f96bfd8ed7aec9; não copiado localmente.

https://www.imea.com.br/imea-site/view/uploads/metodologia/custos/CustosCustoProducao2020.pdf retornou404 no parent viaweb/executor. Recurso do editor ausente, não recusa de permissão. PDF integral não obtido, sem ponte de metodologia ou retroprojeção. Dados consolidados precisam de esclarecimento da data-base nominal antes de conversão monetária; não usar mês do download como data de preços históricos.

## Atualização de transferência regional
Arquivo imea/imea_regional_key_costs.csv recebido do último pacote regional;51.390bytes,SHA256808695e768d80ac8bcfa14ea66c880bebb29883b7b8ae59c04e3549dad05b6b9,CRC da entradaZIP conferido. Somente essa entrada foi materializada; não se alega verificação do hash do ZIP completo.195registros/28abas,585células de conceitos,525numéricas/60vazias. Não confundir com os924 valores de componentesMT previamente auditados no parent, não transferidos para esta base. Arquivos brutos e notas integrais não locais nesta versão.

## Documentação regional conferida

Os arquivos `fontes/imea/imea_regional_source_notes.csv` (143 notas) e `fontes/imea/imea_regional_audit.json` foram materializados e tiveram identidade binária confirmada com os SHA256 enviados pelo ambiente principal. O construtor confronta as 28 abas, 195 registros, praças e linhas de COE/COT/CT com o audit original. Nenhum valor de custo mudou.

A nota Milho_Safra_ALTA_afl!A81 confirma início do acompanhamento de Alta Floresta na safra 2025/26; os rótulos antigos vazios não representam custos históricos disponíveis. Milho_Safra_ALTA_nmt!A81 registra que Nova Mutum deixa de integrar o Projeto CPA-MT a partir de 2026. Indice!A85 descreve mudança de pacote tecnológico de soja em 2025/26; não permite associar automaticamente os asteriscos de Brasnorte 2023/24 e Marcelândia 2022/23. A produtividade modal é levantada no painel de produtores e pode diferir do boletim de safra. O arrendamento utiliza saca de soja e participação da área da cultura. Não foram deduzidos mês nominal, equivalência de conceitos ou valores ausentes dessas notas.

Os dez valores monetários por planilha CONAB e os três conceitos COE/COT/CT por coluna IMEA não são observações independentes. Agregados e componentes são relacionados contabilmente. As contagens de valores não aumentam o número de localidades, safras ou unidades de referência.
