# Base3 v2 — incremento econômico completo

## Estado da entrega

**Completa:** 3384 linhas,141 municípios,2001–2024,46 colunas. Os valores das 42 colunas da v1 permanecem idênticos, com nomes mapeados. Os quatro campos novos estão preenchidos, cada um com 24 valores anuais repetidos por município:

- `2_preco_real_usd2024_media_anual_lag1__dap`: média de 12 preços mensais deflacionados do ano anterior, USD2024/t.
- `2_razao_medias_reais_lag1__soja_dap`: média anual real soja / DAP, adimensional.
- `2_razao_medias_reais_lag1__milho_dap`: média anual real milho / DAP, adimensional.
- `2_selic_efetiva_anualizada_media_anual_lag1_pct_aa`: média temporal de 12 níveis mensais anualizados SGS4189, %a.a., ano anterior.

Sem imputação, modelos ou seleção por p-valores. A versão provisória foi preservada em `historico_v2_parcial`; seus documentos de bloqueio descrevem o estado anterior, não a entrega atual. As contagens/flags anuais em `economia_anual_v2.csv` mostram 12 meses para WB/CPI e Selic em todos os 24 anos; nenhuma incompletude.

## Auditoria antes do join

A auditoria foi executada e salva antes do apensamento. WB/CPI e SGS cobrem todos os 288 meses janeiro 2000–dezembro 2023, sem duplicatas e com valores finitos positivos. SGS contém também 12 meses 2024 no extrato bruto, excluídos dos regressores para outcomes 2001–2024.

A cópia Drive de setembro 2026 foi confrontada pelo ambiente de pesquisa com a versão oficial WB de outubro 2026:864 valores DAP/soja/milho numericamente idênticos. Os arquivos têm hashes distintos. Ambas as versões contêm Mismatch Details; isso não prova adulteração. Recebemos resumo e 288 valores oficiais DAP, reconferidos localmente sem diferença. Dois leitores locais concordam nas 864 células. A conferência não autentica os demais meses/campos. Detalhes em `fontes_v2/CONFRONTO_OFICIAL.md`.

Selic foi recuperada legitimamente pelo ambiente de pesquisa via POST no portal SGS, série 4189. Os CSVs mensal 300 linhas e anual 24 linhas foram recebidos e seus hashes coincidem exatamente. As 24 médias foram recalculadas aqui. O HTML bruto SGS e o XLSX oficial WB permanecem no ambiente pai: seus hashes são registrados, mas não alegamos cópias locais desses binários. As tentativas locais de download foram bloqueadas pelo proxy 403; a transferência das evidências resolveu a limitação dos dados, sem contornar o bloqueio.

CPI-U confere com manifesto, média 2024=313,6888333333333. Os 48 preços anuais soja/milho da v1 foram reproduzidos com diferença máxima 1,14 e−13; nenhum preço v1 foi alterado. Duas reproduções idênticas, testes estruturais e comparação byte a byte dos 10 arquivos v1 constam de `validacao_v2.json`.

## Definições e limitações

Deflação: `preço_real_m = preço_nominal_m × média(CPI2024) / CPI_m`. Média dos 12 meses de t−1. Relações são **razões das médias anuais reais**, não médias das razões. O CPI comum cancela numa razão mensal, mas não elimina automaticamente as diferenças de ponderação entre agregados anuais. A referência monetária 2024 é mudança de unidade; não significa informação disponível ao produtor histórico. Os vintages são retrospectivos, não bases de expectativas em tempo real. Nenhum preço ou juros de 2024 entra como incentivo de outcome 2024.

DAP é fosfato diamônico spot FOB US Gulf, preço internacional de um fertilizante. Não é cesta completa de insumos, preço pago em MT, custo por hectare ou margem. As razões são adimensionais (mesma moeda e massa): expressam preço relativo produto/insumo, sem coeficientes técnicos de uso ou custo municipal. Não se subtrai USD de BRL. IPCA não é necessário nesta construção em USD.

Selic 4189 mede nível efetivo anualizado (base 252); média temporal não é taxa anual acumulada. Não somar juros mensais, não misturar meta 432 ou acumulada 4390. A regra só admite ano com 12 meses. Preços, razões e juros nacionais são comuns por ano e absorvidos por FE anuais. Repetir 24 valores em 141 municípios não cria 3.384 choques independentes. Exposição financeira predeterminada ainda não existe; incluir Selic nos dados não identifica seu coeficiente isolado.

## Reprodução local

Python >=3.9; construção somente com biblioteca padrão. A verificação independente usa openpyxl já instalado (versão registrada). Os arquivos `fontes_v2` são cópias locais rastreadas; não há dependência operacional do complemento CONAB.

```bash
python 2_INTI/chapters/chap1/stats/modelos/base3/construir_base3_v2.py
python 2_INTI/chapters/chap1/stats/modelos/base3/construir_base3_v2.py --apensar
python 2_INTI/chapters/chap1/stats/modelos/base3/testar_base3_v2.py
```

A primeira chamada audita sem criar/alterar o painel v2. A segunda repete a auditoria antes do join many-to-one por ano. Erros de cobertura WB/CPI ou divergência de preços interrompem a construção; não se anualizam subconjuntos silenciosamente. A versão completa exige sequência SGS íntegra e aborta diante de fonte incompleta; não preenche ausentes. Nenhum arquivo v1 é escrito pelo script.

Os arquivos recebidos e seus hashes são insumos congelados. Novos vintages exigem auditoria antes de substituição. O construtor verifica os hashes SGS, cobertura mensal, confronto DAP e médias anuais recebidas antes de qualquer join. `verificar_leitores_v2.py` permite repetir o confronto OOXML/openpyxl.

Fontes: [World Bank Commodity Markets](https://www.worldbank.org/en/research/commodity-markets), [Pink Sheet Drive](https://drive.google.com/file/d/17mTzvQ0BhERZ1TGBc1IpdFXUYLibuzrD/view), [CPI-U/FRED](https://fred.stlouisfed.org/series/CPIAUCNS), [SGS4189](https://www3.bcb.gov.br/sgspub/consultarvalores/consultarValoresSeries.do?hdOidSeriesSelecionadas=4189&method=consultarGraficoPorId). URLs de download e hashes em `fontes_v2/proveniencia_v2.json`.

Publicação da v2 autorizada separadamente. O lote inclui somente a v2 completa e seus insumos/scripts/documentação; o histórico provisório e os demais trabalhos locais ficam fora do commit. A reprodução não depende deles.

O extrator `fontes_v2/extrair_sgs4189_html.py` registra o método recebido do coletor. O HTML bruto não está incluído; o script foi compilado localmente, mas não reexecutado contra esse bruto nesta sessão. Os CSVs incluídos e seus hashes são suficientes para reproduzir o painel.

## Prefixos por grupo — atualização de nomenclatura

Todas as 46 colunas do painel final recebem `grupo_nome_anterior`, sem mudar qualquer caractere do nome anterior. A ordem original permanece: o painel não foi reordenado por grupo. A v1 e os dados de origem mantêm os nomes originais. A publicação desta alteração de nomes foi autorizada separadamente; o escopo limita-se à renomeação e aos arquivos de apoio da base3 v2.

| Grupo | Conteúdo | Colunas |
|---|---|---:|
| 0 | Identificação e classificação territorial | 7 |
| 1 | Ambiental e qualidade específica | 22 |
| 2 | Econômico/produtivo, incluindo GAEZ | 9 |
| 3 | Institucional e qualidade específica dos autos | 5 |
| 4 | Máscaras amostrais combinadas | 3 |

O [mapeamento explícito](mapeamento_colunas_v2.csv) registra posição, grupo, nome anterior, nome novo e justificativa para todas as colunas. O [dicionário completo v2](dicionario_variaveis_v2.csv) contém as 46 definições e suas origens; o adendo descreve os quatro campos econômicos acrescentados. `v2__` preexistente foi preservado: por exemplo, `1_v2__precip_mm_anual`. Aptidão GAEZ ficou no grupo 2 por seu papel produtivo; biomas/frações, no grupo 0 como classificação territorial. Elegibilidade específica de autos acompanha o grupo 3; máscaras que combinam desfechos/covariáveis ficam no grupo 4.

O construtor calcula com nomes originais e aplica o mapa apenas ao painel final. Executá-lo novamente não duplica prefixos. As tabelas auxiliares mensais/anuais e a auditoria pré-join mantêm nomes de origem; não são o schema do painel final. A tabela de qualidade do incremento usa os nomes finais.

**Compatibilidade:** referências antigas de fórmulas precisam seguir o mapa. Nomes iniciados por dígito exigem acesso por string, como `df['0_codigo_ibge']`; em fórmulas Patsy, use `Q("1_taxa_conversao__agricultura")`. Nenhum modelo foi ajustado nesta mudança.

Os testes invertem o mapa para comparar com v1 e com a v2 publicada antes da renomeação. Além de células e ordem, verificam que todos os bytes após o cabeçalho do CSV permanecem iguais, incluindo ausências e zeros. Os dez arquivos da v1 continuam intactos.
