# Regiões de MT: referência candidata, não harmonização territorial

**Arquivo:** `mt_regioes_141_compacto.csv`; 141 linhas, códigos como texto. Extração em 24/10/2026.

- **IBGE:** [DTB 2016 v2 oficial](https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2016/DTB_2016_v2.zip), membro `DTB_2016_v2/DTB_2016/DTB_BRASIL_MUNICIPIO.xls`, aba `DTB_2016_Municipio`, filtro UF=51. O diretório oficial registra versão modificada em 13/04/2018. Código mesorregional = UF + código de 2 dígitos da fonte; nomes apenas sem espaços externos. São 55/25/22/17/22 municípios em 5101/5102/5103/5104/5105, respectivamente.
- **IMEA:** [nota oficial de novembro/2017](https://www.imea.com.br/imea-site/view/uploads/metodologia/justificativamapa.pdf), segmentação realizada em 2008 segundo a nota. Classificação agroeconômica separada, **não equivalente às mesorregiões IBGE**. 140 matches por nome exato após normalizar acentos/pontuação/caixa; nenhum fuzzy match.
- **Pendências preservadas:** Poxoréu (5107008) recebe IMEA=`NA`: fonte escreve “Poxoréo”. “Monte Verde do Norte” consta adicionalmente na lista Norte, junto de Nova Monte Verde, mas não corresponde a código DTB2016; não foi inventada 142ª linha. Ambas as grafias foram conferidas visualmente no PDF. O próprio quadro IMEA indica 17 municípios Norte, apesar de 18 nomes na lista.
- **Limites:** referência IBGE **2016 v2**; compatibilidade com território fixo **2023 não presumida**. Não prova continuidade de limites, existência de 141 unidades em 2001 nem comparabilidade 2001–2024. A integração deve resolver predecessores/desmembramentos e eventual unidade composta. Boa Esperança do Norte (5101837) não existe nesta referência e não foi retroativamente incluída.
- **API atual:** endpoints IBGE atuais devolveram HTTP 503; nenhum JSON foi obtido. Não foi verificado se seus campos meso/micro são nulos para novos códigos.

Raw ZIP SHA-256: `d5ce045b0fe4a9f5316625c9922bb95013b0ed8113b39efe76340fce89fabdac`.

Raw XLS SHA-256: `bf7584d922c612d48669cc90f8d37c3b72a9b619a001291f093f72b70f759232`.

Raw IMEA PDF SHA-256: `179d92ea0e91ac22206eb862165dadc2840afa436c712782ceeca4703177275d`.

Fontes brutas, texto extraído, CSV bruto, script reprodutível e validações estão no mesmo diretório. Ao importar, fixar `codigoIBGE` e `mesocodigo` como texto; unir por código e auditar qualquer unidade não encontrada.
