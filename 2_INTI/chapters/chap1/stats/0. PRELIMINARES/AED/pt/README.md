# AED do capítulo 1

São 25 notebooks, um por nome literal do dicionário `../../HIPOTESES TESE - CHAP1.txt`, com as seis fases solicitadas. O gerador extrai automaticamente nomes, todos os caminhos CSV, notas específicas e pendências. Os tratamentos por tipo de medida ficam explícitos em `gerar_notebooks.py` e `aed_features.py`; candidatos novos sem tratamento conhecido geram erro para revisão.

O recorte confirmado por Fernando é **2001–2024, com referência de 141 municípios**. Anos anteriores são preservados para denominadores, climatologias e exposições históricas. As variantes soja/milho, agricultura/pastagem e cenários GAEZ permanecem separadas.

## Usar no VS Code

### Painel integrado e estatística descritiva

Abra [painel_anual_2001_2024.ipynb](painel_anual_2001_2024.ipynb). Ele já contém os resultados de execução e pode ser reexecutado de cima para baixo no mesmo kernel. São 256 células, com cada tabela, comando de construção e gráfico em célula própria. O notebook reconstrói a grade de 141 municípios × 24 anos (3.384 linhas e 296 colunas), confere os 48 CSVs derivados e os 25 manifestos e compara os valores com o painel anterior. Não requer nova aquisição nem autenticação Earth Engine.

As 155 medidas são descritas com N válido, ausências, zeros, média, desvio, percentis e extremos. Preços comuns são resumidos por ano; atributos fixos, por município. Há cobertura por ano/município, 54 gráficos, 58 tabelas, comparações por composição de bioma, variação dentro/entre municípios, correlações em amostra comum e cobertura conjunta. As 25 candidatas aparecem no inventário: 20 contribuem para colunas analíticas compartilhadas, uma é diagnóstico auxiliar e quatro permanecem adiadas. Isso não define uma especificação causal.

O DataFrame integrado chama-se `painel`; as fontes preservadas ficam em `fontes`. Os novos CSVs são gravados em `2_INTI/xdata/chap1/processed/harmonizacao/painel_notebook/`, incluindo `painel_2001_2024_141.csv`, `dicionario_painel.csv` e `descritiva_medidas.csv`. Os derivados anteriores e os 25 notebooks de variáveis não são sobrescritos.

O gerador reproduzível é `gerar_painel_anual_notebook.py`; `--sobrescrever` substitui somente o notebook integrado, apagando seus outputs e edições manuais. `painel_anual_fontes.py` lê e reúne as fontes; `painel_anual_descritiva.py` contém as estatísticas e gráficos. Para validar a estrutura dos notebooks de variáveis que já têm resultados salvos, use `validar_notebooks.py --permitir-saidas`.

Abra o repositório no VS Code, abra um `.ipynb`, selecione um kernel Python com as dependências e execute as células na ordem. As funções da AED inicial estão incorporadas nos notebooks. A seção nova **Passos 1 e 2 — Construção executada das variáveis**, no fim da fase 6, importa os módulos `harmonizacao_*.py` desta pasta; mantenha os arquivos juntos.

O ambiente usado e disponível nesta entrega é `2_INTI/audit/aed_chap1_20261013/venv/Scripts/python.exe`. Ele contém todas as dependências. Para criar um ambiente próprio, execute na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r "2_INTI/chapters/chap1/stats/AED/pt/requirements-territorio.txt"
```

Depois selecione `.venv/Scripts/python.exe` no seletor de kernel do VS Code. `requirements.txt` contém apenas as dependências da AED; `requirements-territorio.txt` acrescenta as bibliotecas da reconstrução espacial.

## Gerar novamente

```powershell
python "2_INTI/chapters/chap1/stats/AED/pt/gerar_notebooks.py"
```

Notebooks idênticos são mantidos. O gerador recusa substituir notebooks diferentes; se quiser descartar edições manuais e resultados salvos, acrescente `--sobrescrever`. Edite os modelos Python para mudanças que devam sobreviver à regeneração.

Cada notebook de variável registra o hash do TXT, caminhos, notas, período e referência territorial. O gerador valida formato e sintaxe antes de escrever e gera os 25 candidatos sem outputs; execuções posteriores podem ter resultados salvos. O notebook integrado é entregue executado. Logs de validação ficam na auditoria.

## Referência territorial de 141 municípios

Boa Esperança do Norte tem origem legal em partes de Sorriso e Nova Ubiratã, segundo o [IBGE](https://educa.ibge.gov.br/criancas/voce-sabia/22741-novo-municipio.html). A [malha IBGE 2023](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/UFs/MT/MT_Municipios_2023.zip) oferece os 141 territórios de referência. Não foi feita soma integral do novo município em um único município, nem rateio de médias por percentuais de área.

Na fase 1, cada notebook lê os CSVs exatos do TXT. Na fase 2, a transformação territorial usa os derivados em `2_INTI/xdata/chap1/processed/territorio_141/`, com conferência de hashes. As fontes permanecem em `bases_brutas` e `bases_fontes_limpas`.

| Fonte | Tratamento para a referência de 141 |
| --- | --- |
| GAEZ | Nova extração dos pixels; média ponderada por `cos(latitude)`, separada por raster. |
| CHIRPS | Nova extração mensal dos pixels; recomposição de totais e anomalias, sem somar médias municipais de chuva. |
| Biomas | Interseção com a malha 2023; áreas e frações recalculadas; limiares 70/80/90 preservados. |
| Relevo | Nova extração dos pixels; média, mínimo, máximo e contagem recalculados. |
| IBAMA espacial | Reatribuição dos pontos e nova contagem por identidade válida e município/ano. |
| PAM | Boa Esperança só tem medidas em 2025, fora do painel; seus registros anteriores são ausentes e não são somados. |
| MapBiomas, vegetação nativa e PPM | Já contêm os 141 códigos; valores preservados. |

A referência fixa 2023 também contém diferenças de limites em outros municípios. A sobreposição das malhas inclui parcelas de Boa Esperança atribuídas a Vera e Paranatinga em 2023, além dos dois municípios de origem legal. A reconstrução usa a geometria inteira de 2023, sem um mapa artificial de origem única.

Isso resolve a incompatibilidade de 141/142 nos derivados espaciais. Códigos iguais não certificam toda a comparabilidade histórica de PAM, PPM ou município declarado do IBAMA. Outras mudanças de limites e códigos continuam indicadas na fase 6.

Para reconstruir os derivados a partir dos rasters, vetores e eventos locais:

```powershell
.\.venv\Scripts\python.exe "2_INTI/chapters/chap1/stats/AED/pt/reconstruir_territorio141.py"
```

O script baixa a malha oficial de 2023 somente se ela estiver ausente, reextrai os dados e atualiza o manifesto territorial. Não modifica os CSVs de origem. Os dados continuam exclusivamente em `2_INTI/xdata/`.

## Interpretação e limites

- `Y_conv`: constrói conversão direta nativa→agricultura/pastagem com mapas 10.1 e malha 2023. Ano t representa a transição entre os mapas t−1 e t; estoques continuam disponíveis para diagnóstico.
- `Y_tx-conv`: divide cada conversão pelo estoque nativo inicial na mesma máscara. No painel, o denominador efetivamente usado é `y_nativa_inicial_ha`; o estoque candidato anterior permanece distinto.
- `x2a`: constrói média de 1991–2000 com pelo menos sete anos válidos, preserva a cobertura e sinaliza a comparabilidade territorial histórica pendente.
- Custos CONAB: os gráficos atuais mostram cobertura de células/abas. Uma série de custos exige mapear unidade, localidade, tecnologia, categoria e safra.
- Embargos: os gráficos mostram registros históricos; linhas de histórico e coordenadas não são embargos únicos.
- Zeros registrados, células vazias, combinações sem linha, ausência de cultivo e medidas não construídas são situações diferentes.
- Os gráficos mostram até seis grupos por padrão e até vinte municípios por mapa de calor. Aumente `MAX_GRUPOS_GRAFICOS` na primeira célula para exibir mais grupos; as tabelas incluem todos.
- Preços anuais usam média; a exposição usa o ano civil anterior, com correspondência exata do calendário. Chuva anual usa soma, com doze meses válidos e cobertura mínima de pixels de 95%.
- Foram implementados os parâmetros operacionais descritos abaixo. Não foram escolhidos controles simultâneos, limiar de predominância de bioma, índice de retorno líquido ou identificação causal.

## Construção dos passos 1 e 2

A execução de cada notebook salva suas tabelas, dicionário, cobertura e manifesto em `2_INTI/xdata/chap1/processed/harmonizacao/<nome_do_notebook>/`. Os comentários e o Markdown explicam fórmula, unidade, motivo e limite. `features_construidas` é a tabela principal em memória; `tabelas_derivadas` contém também alternativas e diagnósticos. Os esqueletos da primeira parte da fase 6 foram preservados; a nova seção executa a implementação autorizada.

| Tratamento | Parâmetro aplicado e interpretação |
|---|---|
| Conversão e taxa | MapBiomas 10.1, mapas 2000–2024, grade nativa e 141 territórios de 2023. Área em ha por `pixelArea`; destinos separados. Área sem classe válida é medida diretamente. Qualquer lacuna real mantém Y ausente; tolerância numérica de conservação não libera lacunas. |
| Preços reais | CPI-U BLS/FRED mensal, sem ajuste sazonal; USD de poder de compra médio de 2024. A deflação precede a média anual. Mantêm-se as versões nominais. |
| Exposição de preço | Média de 12 meses de t−1, logs de preços positivos e diferenças logarítmicas explicitamente nomeadas. Não são surpresas exógenas por definição. |
| PAM histórica | 1991–2000, pelo menos 7 anos válidos. Média aritmética entre anos; z fixo por cultura, `ddof=1`. Sem usar informação posterior a 2000 para completar capacidade. |
| GAEZ | Cada raster é cenário separado; sx/10.000 e z fixo. Validade temporal da base 2010 e umidade comercial permanecem sinalizadas. |
| Multas reais | IPCA Brasil mensal, base dezembro de 2024, aplicado ao valor do auto antes da soma. Valores autuados não são multas pagas. |
| Temas IBAMA | Flora e Desmatamento/Desmatamento e Queimada, como seleções alternativas. Ano da lavratura; status atual não reconstrói situação histórica. |
| Usos da terra | Classes exclusivas; participações sobre área mapeada de referência fixa em 2000. Classes residuais e áreas não observadas são sinalizadas. |
| Chuva | Ano civil completo; referência principal 1981–2000 (20 anos), alternativas retrospectivas 1981–2010 e 1991–2020. |
| Interações | Preço anterior × capacidade padronizada, por produto/cenário. Biomas: Cerrado e Pantanal interagidos, Amazônia como referência. São alternativas disponíveis, não uma especificação única. |

O uso de CPI-U/IPCA gerais não representa índice de custos agropecuários. A base histórica disponível é seletiva: na aplicação inicial, a regra PAM produziu capacidade válida para 47 municípios de soja e 117 de milho. No IBAMA, a cobertura temática e espacial varia fortemente entre 2001 e 2024; as flags precisam acompanhar as contagens, inclusive defasadas.

Para reconstruir todas as tabelas e a grade candidata:

```powershell
& "2_INTI/audit/aed_chap1_20261013/venv/Scripts/python.exe" "2_INTI/chapters/chap1/stats/AED/pt/construir_painel.py"
```

O resultado é `2_INTI/xdata/chap1/processed/harmonizacao/painel_candidato_2001_2024_141.csv`, com 3.384 chaves, 296 colunas de candidatas/alternativas/qualidade e ausências preservadas. `manifesto_painel.json`, `origens_colunas_painel.csv` e `cobertura_painel.csv` documentam o conteúdo. O manifesto agora registra `y_construido: true`; isso não seleciona casos completos nem define uma especificação causal.

Y tem medidas válidas em **2.772 pares município–ano**, para cada destino; **612 pares** permanecem ausentes por cobertura incompleta. **95 municípios** têm os 24 anos completos. A regra integral é conservadora: a fração territorial inválida máxima é 0,129%. A cobertura acompanha Y nas colunas `y_*`. Relaxar essa regra exigiria explicitar que a taxa descreve apenas a área observável e avaliar a seleção da amostra; os valores atuais não extrapolam pixels ausentes.

Os deflatores foram adquiridos uma vez e ficam em `raw/tabular/deflatores_harmonizacao_20261014/`, com URLs, datas e hashes. Notebooks não acessam a rede para atualizá-los. Uma aquisição explícita pode ser feita por `harmonizacao_economia.py --obter-deflatores <pasta>`, conforme `--help`.

## Transições MapBiomas 10.1 e Earth Engine

O download público examinado correspondia à Coleção 10.0. A API pública da plataforma também não ofereceu o par coleção/território necessário. A aquisição foi concluída pelo Earth Engine autenticado: 3.384 pares e 324.273 linhas de matriz, incluindo permanências. Não foram usados saldos de estoque como conversão.

O cliente `earthengine-api` está instalado somente no ambiente local da AED. Para outro ambiente, use `requirements-harmonizacao.txt`. O projeto Google Cloud precisa estar habilitado no Earth Engine, e o usuário precisa autenticar o Python. O ID aparece no seletor de projetos do [Google Cloud Console](https://console.cloud.google.com/); a situação pode ser conferida na [configuração Earth Engine](https://console.cloud.google.com/earth-engine/configuration). [Documentação de autenticação](https://developers.google.com/earth-engine/guides/auth).

```powershell
# Login interativo somente se necessário; concluído neste computador em 14/10/2026.
& "2_INTI/audit/aed_chap1_20261013/venv/Scripts/python.exe" -c "import ee; ee.Authenticate(auth_mode='localhost')"

# Primeiro, verificar um município e um ano no projeto autenticado.
& "2_INTI/audit/aed_chap1_20261013/venv/Scripts/python.exe" "2_INTI/chapters/chap1/stats/AED/pt/obter_transicoes_mapbiomas.py" --executar-gee --projeto grand-icon-237222 --ano-inicio 2001 --ano-fim 2001 --codigo 5107909

# Depois do piloto válido, obter ou revalidar o cache dos 141 municípios e 24 intervalos.
& "2_INTI/audit/aed_chap1_20261013/venv/Scripts/python.exe" "2_INTI/chapters/chap1/stats/AED/pt/obter_transicoes_mapbiomas.py" --executar-gee --projeto grand-icon-237222 --workers 8
```

Em 14/10/2026, foram validados a autenticação local, o projeto `grand-icon-237222`, o piloto de Sinop/2001 e a aquisição completa. `autenticacao_gee.json`, `piloto_gee_comparacao_independente.json` e `conferencia_transicoes_reais.json`, na auditoria de harmonização, registram essas etapas.

O script usa a malha 2023, a grade nativa dos mapas e `pixelArea`, salva cache local por município–ano e verifica conservação de áreas. O protocolo atual usa `raw/tabular/mapbiomas/transicoes_col10_1_141/v2_cobertura_explicita/`; o primeiro piloto permanece preservado fora dessa subpasta. O cache permite retomada e o parâmetro `--workers` admite de 1 a 8 processos, sem alterar a resolução. Resultados de piloto têm sufixo `_parcial` e não substituem os insumos completos. As saídas completas são `transicoes_reais_10_1_141.csv`, `cobertura_transicoes_10_1_141.csv` e `conversao_taxas_10_1_141.csv`. Os históricos anteriores sem Y estão identificados como `historico_situacao_sem_transicoes.csv` nas duas pastas de Y.

Embargos e as três bases CONAB permanecem adiados conforme o plano. Suas seções novas exportam diagnóstico e pendências, não uma contagem/área/custo final inventado.

## Validação

```powershell
& "2_INTI/audit/aed_chap1_20261013/venv/Scripts/python.exe" -m unittest discover -s "2_INTI/chapters/chap1/stats/AED/pt" -p "test*.py" -v
& "2_INTI/audit/aed_chap1_20261013/venv/Scripts/python.exe" "2_INTI/chapters/chap1/stats/AED/pt/validar_notebooks.py" --executar --saida "2_INTI/audit/aed_chap1_20261013/harmonizacao/execucao"
```

A validação confere nomes, seis fases, notas, caminhos e sintaxe; executa todos os notebooks com os CSVs reais e verifica hashes das fontes. Cópias executadas, logs, figuras e relatório estão em `2_INTI/audit/aed_chap1_20261013/`. Os testes sintéticos cobrem taxas, ausências, zeros, meses incompletos, janela histórica e junções duplicadas.

Na entrega inicial dos passos 1 e 2, os 25 notebooks foram executados. Após a integração de Y, foram aprovados 66 testes, validadas as estruturas dos 25 notebooks e reexecutados os dois notebooks alterados. As saídas incluem 21 candidatos construídos com ressalvas e quatro adiados. A conferência independente comparou os 3.384 JSONs com Y e o painel. O [relatório de harmonização](../../../../../audit/aed_chap1_20261013/harmonizacao/RELATORIO_HARMONIZACAO.md) registra resultados, cobertura e continuidade.
