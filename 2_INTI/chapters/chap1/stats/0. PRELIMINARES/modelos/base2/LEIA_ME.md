# Base H1 v2 — entrega local

Painel-mestre: **3384 linhas × 108 colunas**,141 municípios,2001–2024. Todas as 70 colunas originais foram mantidas, inclusive os tokens originais no CSV, zeros e faltantes. As 38 adições são 15 campos de chuva/relevo,10 metadados cartográficos,2 rendimentos defasados e11 flags de elegibilidade. Não é uma amostra completa truncada; as flags permitem escolher amostras futuras explicitamente.

**candidatos_quarentena.csv:** mesmas 3.384 chaves,128 campos candidatos além de 4 identificadores. Contém alternativas GAEZ/PAMhistórica, registros institucionais e usos da terra com suas flags; não é um bloco pronto para regressão. GM e seu estoque de embargo não foram incorporados. Não há novas regressões/imputações.

## O que está validado e o que permanece aberto

Validação interna: unicidade de códigos/anos, junção 1:1, mesma grade de 141 municípios,16 campos compartilhados idênticos e rendimentos soja/milho conferidos por nomes equivalentes, domínio/cobertura da chuva, fórmulas das anomalias, ordem/invariância do relevo, defasagens por ano consecutivo, máscaras e preservação do núcleo. IDs foram lidos como códigos; não houve recodificação141→140 nem associação por nome. O painel PT não oferece todos os nomes para validação nominal independente; malha e frações foram conferidas. Não reextraímos mapas nem reconstruímos geografia histórica.

Fontes documentadas: CHIRPSv2 (ano civil), CopernicusGLO-90, MapBiomas10.1/malhaIBGE_MT_2023_141, IBGE/PAM e IBAMA. GAEZv4 é produtividade potencial em matéria seca; terras2010 limitam predeterminação; baixo/altoinsumo não são custos monetários. Rendimento observado é endógeno e não lucro. Instituições: autos/multas registrados não equivalem a pagamento, eficácia ou esforço fiscal exógeno. Flag temática completa não certifica cobertura total. Fontes brutas citadas em xdata estão ausentes nesta cópia: rastreabilidade documental não é autenticação integral.

## Resultados da auditoria

- 2.772 pares válidos de conversão;612 ausências coincidem exatamente com flag de cobertura cartográfica incompleta do PT.
- 265 zeros agrícolas registrados e0 zeros pastagem nos pares válidos; não imputados nesta construção.
- Chuva:12 meses válidos/registrados/com cobertura conhecida em todas as 3.384 linhas, normal1981–2000 com 20 anos por município. Isso não equivale a chuva na safra ou balanço hídrico.
- Amostra potencial conversão+chuva:2772; com fiscalização Flora válida defasada:1140; com rendimentos defasados de ambas culturas:2016. São flags de elegibilidade, não exclusões do mestre.
- Os estoques/lotação PT têm flags de geografia histórica e compatibilidade temporal não validadas; por isso permanecem em quarentena.
- Custos CONAB apenas referenciados em HIPOTESES TESE - CHAP1.txt; diretório 2_INTI/xdata/chap1/processed/tabular ausente e sem arquivos em origin/main. Não foram fabricados custos, margens, preçosBRL, crédito, algodão ou localização de ecótono.

## Arquivos de revisão

`dicionario_variaveis.csv`: fonte, unidade, temporalidade, camada, risco, cobertura por variável; `AUDITORIA_QUALIDADE.json`: hashes/commits/join; `FONTES_PROTEGIDAS_SHA256.json`: fontes/textos/rodadas1–7; `comparacao_original_v2.csv`: integridade das 70 colunas; `comparacao_principal_PT.csv`:16 campos comuns; `auditoria_chaves.csv`: grade1:1.

`missing_zeros_por_variavel.csv` e `missing_zeros_por_ano.csv.gz`, `...codigo_ibge.csv.gz`, `...bioma_predominante.csv.gz`: N,observados,missing,zeros,negativos e não finitos. Negativo pode ser legítimo em anomalias/variações; não é automaticamente inválido. Flags booleanas não são zeros econômicos.

`mascaras_mestre.csv.gz` / `mascaras_quarentena.csv.gz`:0=faltante,1=zero numérico registrado,2=outro observado,3=negativo numérico registrado,4=não finito. O significado estrutural/origem de todos os zeros não é certificado. Falso de flag booleana é categoria observada, não zero econômico. Ver flags cartográficas/institucionais para motivos documentados; não presumir censura/zero estrutural.

`TRATAMENTO_RODADAS1_7.md`: resposta auditada sobre faltantes/zeros anteriores; `SENSIBILIDADE_FUTURA.md`: proposta ainda não executada, sem promessa de ausência de viés ou identificação causal; `PLANO_DECISOES.md`: anterior à construção.

## Reprodução

Dependências:Python 3.12, numpy e pandas nas versões de VERSOES.json/requirements.txt. Use ambiente virtual externo ao repositório; nenhuma dependência foi instalada nesta tarefa. Parquet não foi produzido: pyarrow e fastparquet indisponíveis. O script gerará também Parquet se algum engine estiver disponível, sem instalação automática.

Na raiz:

```bash
OPENBLAS_NUM_THREADS=1 /tmp/chap1-notebooks-env/bin/python 2_INTI/chapters/chap1/stats/modelos/base2/reproduzir.py
```

Substitua o interpretador se necessário. Saídas derivadas da própria base2 são regeneradas; fontes e rodadas anteriores protegidas por hash. O script não acessa rede, não faz Gitfetch/push nem estima modelos. Se as fontes mudarem, a execução registra novos hashes e exige revisão científica da comparabilidade; a referência desta entrega está no manifesto. `validar.py` confere independentemente tokens originais, valores, lags porjoin, lacunas/zeros em exemplo artificial, máscaras, relatórios e dicionário.

Fetch origin/main foi feito uma vez antes da construção:HEAD e remoto df0a238d4ccb729fb3177b443251fbbaa0cabc93. Não foi necessário alterar checkout. Nenhum commit/push/publicação autorizado ou tentado. Logs em 2_INTI/audit/base2.

Ocorrências técnicas: erro de sintaxe inicial corrigido antes de ler os dados; advertências de desempenho/depreciação na primeira execução bem-sucedida motivaram ajustes de implementação. Testes finais e reprodução usam a versão corrigida; não houve alteração de dados para fazer testes passarem.
