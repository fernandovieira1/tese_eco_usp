# Relatório de execução e encaminhamento para revisão — H1 e H2

## 1. Data e ferramenta usada

**Data do relatório e da adaptação:** 30 de setembro de 2026  
**Período da execução relatada:** 29–30 de setembro de 2026  
**Ferramenta:** Codex, no repositório local, com PowerShell e scripts de aquisição, processamento e validação.  
**Repositório:** `C:\Users\ferna\Documents\dev\Tese USP\tese_eco_usp`  
**Finalidade:** registrar o trabalho realizado e fornecer contexto suficiente para uma avaliação crítica em outro chat.  
**Escopo deste documento:** síntese da execução anterior de auditoria, aquisição, preparação e validação. Os resultados de testes abaixo são daquela execução; este relatório não representa uma nova rodada de aquisição ou estimação.

## 2. Objetivo da tarefa

Auditar, adquirir, preparar e catalogar dados para H1 e H2, preservando os arquivos originais e tornando fontes, transformações, limitações e resultados verificáveis. Registrar o trabalho em Markdown para permitir feedback posterior.

### Hipóteses consideradas

**H1:** investigar se a conversão de vegetação nativa responde ao retorno agrícola esperado. A extensão H1-a considera respostas maiores onde a capacidade produtiva predeterminada é maior; a H1-b considera o papel das regras, monitoramento e sanções.

Uma construção candidata de choque de retorno combina variações defasadas dos preços dos produtos com medidas de capacidade produtiva municipal. Essa construção não foi concluída nem adotada como especificação definitiva.

**H2:** investigar se o estoque de vegetação anterior ao choque climático modera a resposta da produtividade agrícola ao clima. A extensão H2-a contempla heterogeneidade entre Amazônia, Cerrado, Pantanal e municípios mistos.

Foram mantidas duas distinções essenciais: anomalia climática depende de uma normal explicitamente definida; fiscalização pode responder ao próprio desmatamento e não se torna exógena apenas por ser defasada.

### Síntese do resultado

Foi auditado o repositório e seu histórico, preservado o checkpoint original, adquirido um conjunto amplo de fontes oficiais e construídas tabelas candidatas para as hipóteses H1 e H2. Também foram produzidos inventários, registros de aquisição, catálogo de variáveis, documentação de linhagem, perfis de qualidade e testes de integração.

**O resultado ainda não é um painel econométrico completo e validado.** Permanecem lacunas em conversão bruta de vegetação, preços locais, séries institucionais históricas e harmonização territorial. Há decisões científicas pendentes sobre calendário agrícola, normais climáticas, aptidão produtiva e classificação de biomas. Não foram estimadas regressões finais.

Principais números registrados ao término da execução:

| Indicador | Resultado |
|---|---:|
| Arquivos originais versionados protegidos por SHA256 | 210 |
| Commits alcançáveis examinados | 117 |
| Arquivos ZIP / membros inventariados | 28 / 363 |
| Arquivos no inventário de dados e documentação | 1.512 |
| Volume aproximado desses arquivos | 9 GiB |
| Entradas no catálogo | 1.737 |
| Tabelas processadas com perfis de validação | 19 |
| Requisições bem-sucedidas verificadas em replay | 822 |
| Erros no replay | 0 |
| Testes de integração | 13 aprovados |

Esses números são fotografias da execução anterior. As 1.737 entradas do catálogo não correspondem a 1.737 variáveis econômicas distintas. O inventário inclui fontes reutilizadas, documentação e intermediários, inclusive versões exploratórias preservadas.

## 3. Prompt ou instrução principal

A instrução inicial determinou confirmar `git status`, `git branch --show-current` e a existência e estrutura de `2_INTI/data` antes de qualquer alteração, usando o estado inicial como checkpoint de auditoria. Em seguida, executar as instruções do anexo `Texto colado.txt`, fornecido na conversa.

**Síntese da instrução do anexo:** atuar como econometrista aplicado, engenheiro de dados de pesquisa e auditor; examinar o repositório e seu histórico; reutilizar dados existentes; adquirir e preparar fontes para H1/H2; documentar linhagem, qualidade, lacunas e decisões; preservar os originais e não estimar regressões finais. Esta descrição é uma síntese, não uma transcrição integral do anexo.

**Instruções posteriores:** apresentar um relatório do trabalho em `INTI/reports`, interpretado conforme a estrutura existente como `2_INTI/reports`, e adaptá-lo aos 11 tópicos solicitados, mantendo informações adicionais necessárias.

## 4. Arquivos lidos

A lista abaixo destaca os arquivos consultados ou processados na execução; o inventário vinculado registra o escopo completo. Inventariar um arquivo não significa que todo o seu conteúdo tenha sido interpretado manualmente.

- Anexo de instruções: `C:\Users\ferna\.codex\attachments\023b3fe5-14b2-4ec5-bded-4de042b59038\Texto colado.txt`.
- Scripts anteriores em `2_INTI/code`: `audit_repository.py`, `discover_core.py` e `data_common.py`.
- Metadados e cadastro em `2_INTI/data/raw/tabular/ibge`: `pam1612_metadata.json`, `ppm3939_metadata.json` e `municipios_mt_consulta20260928.json`.
- Metadados MapBiomas: `collection10_1_metadata.json` e `statistics_page_20260928.html`.
- Arquivos geográficos anteriores: `biomes_directory.html` e `MT_Municipios_2024.zip`.
- Manifesto anterior: `2_INTI/data/catalog/acquisition_core.jsonl`.
- Planilha `1_SUYANA/data/carbon_emissions.xlsx`, notebooks, documentos e versões históricas descritos abaixo.
- Fontes adquiridas, tabelas processadas e evidências de validação relacionadas nas seções 5, 7 e 8.
- Para elaborar e adaptar este relatório: o próprio Markdown, `relatorio_final_h1_h2.md`, `verificacao_preservacao_h1_h2.json`, `validacao_catalogo_xlsx.json` e `testes_h1_h2.txt`.

### Achados da leitura e auditoria

A auditoria cobriu arquivos atuais, histórico Git, ZIPs, notebooks e dois objetos Git do tipo árvore não referenciados. Foram examinados 279 objetos históricos de texto, código, DOCX e ZIP, além de oito versões históricas de notebooks.

Foram identificados e reutilizados metadados de PAM, PPM e MapBiomas, cadastro municipal do IBGE, a malha municipal de Mato Grosso de 2024 e registros de aquisição já existentes. Havia sete arquivos brutos de metadados ou geografia, um manifesto e três scripts Python anteriores: `audit_repository.py`, `discover_core.py` e `data_common.py`.

Não foi encontrada evidência de um painel municipal H1/H2 consolidado, de um processamento validado no Google Earth Engine ou de uma correspondência territorial histórica que resolvesse a criação de Boa Esperança do Norte. Os seis notebooks atuais eram voltados a simulações, gráficos conceituais ou emissões.

A planilha anterior `1_SUYANA/data/carbon_emissions.xlsx` contém 86 observações anuais, de 1940 a 2025, sem anos duplicados ou ausentes, com valores entre 4,26 e 38,11 bilhões de toneladas métricas. Ela serve como contexto global, sem substituir dados municipais. Sua fonte não foi autenticada e o valor de 2025 tem uma nota específica.

O script de auditoria anterior continha afirmações textuais fixas incompatíveis com o inventário encontrado, incluindo a ausência de dados e scripts e um mínimo incorreto para emissões. O código original foi preservado; as correções foram documentadas na [auditoria atualizada](../data/catalog/auditoria_dados_h1_h2.md). Esse documento deve orientar a leitura do relatório histórico gerado pelo script antigo.

## 5. Arquivos criados/modificados

Os dados e seus intermediários estão em `2_INTI/data`, organizados em `raw`, `interim`, `processed` e `catalog`. Os scripts adicionados estão em `2_INTI/code`. O ambiente Python foi instalado fora do repositório; suas dependências foram registradas.

| Entregável | Link |
|---|---|
| Auditoria atualizada | [auditoria_dados_h1_h2.md](../data/catalog/auditoria_dados_h1_h2.md) |
| Matriz de necessidades e disponibilidade | [matriz_dados_h1_h2.csv](../data/catalog/matriz_dados_h1_h2.csv) |
| Relatório de validação | [validacao_dados_h1_h2.md](../data/catalog/validacao_dados_h1_h2.md) |
| Linhagem das transformações | [linhagem_dados_h1_h2.md](../data/catalog/linhagem_dados_h1_h2.md) |
| Catálogo CSV | [data_catalogo_variaveis_h1_h2.csv](../data/catalog/data_catalogo_variaveis_h1_h2.csv) |
| Catálogo Excel | [data_catalogo_variaveis_h1_h2.xlsx](../data/catalog/data_catalogo_variaveis_h1_h2.xlsx) |
| Relatório final detalhado da execução | [relatorio_final_h1_h2.md](../data/catalog/relatorio_final_h1_h2.md) |
| Inventário dos dados | [inventario_arquivos_dados_h1_h2.csv](../data/catalog/inventario_arquivos_dados_h1_h2.csv) |
| Lista das adições da execução anterior | [novos_arquivos_h1_h2.csv](../data/catalog/novos_arquivos_h1_h2.csv) |
| Guia de reprodução | [README_auditoria_h1_h2.md](../code/README_auditoria_h1_h2.md) |
| Dependências | [requirements-audit-lock.txt](../code/requirements-audit-lock.txt) |

Os scripts separam aquisição por fonte, preparação tabular e espacial, catálogo, relatórios, replay e testes. O guia de reprodução contém os pontos de entrada. Fontes remotas mutáveis podem deixar de fornecer os mesmos bytes no futuro; a preservação local dos originais e de seus hashes é parte central da rastreabilidade.

### Arquivos criados ou modificados nesta documentação

- Este relatório foi criado em `2_INTI/reports/2026-09-30_relatorio_auditoria_h1_h2_para_feedback.md` e posteriormente reorganizado nos 11 tópicos solicitados.
- A adaptação alterou somente este Markdown. Não houve nova aquisição, alteração dos dados ou execução de modelos.
- Na execução anterior, foram adicionados scripts, dados e relatórios; os 210 arquivos originais versionados permaneceram inalterados. A lista de adições vinculada acima corresponde àquela execução e antecede este relatório.

## 6. Decisões tomadas

- Preservar o checkpoint e os arquivos originais; acrescentar produtos e documentar correções sem sobrescrever as fontes anteriores.
- Manter versões de fontes separadas e identificar medidas como candidatas quando a definição científica ainda depende de revisão.
- Usar correspondência municipal exata e colocar nomes sem correspondência em quarentena.
- Preservar símbolos SIDRA e deixar temporariamente os não numéricos como ausentes, com revisão explícita do símbolo `-` pendente.
- Construir estoques e defasagens contíguas de vegetação, sem substituir conversão bruta por variação líquida do estoque.
- Produzir alternativas explícitas de normais climáticas e predominância de biomas, sem escolher a especificação final pela significância de resultados.
- Corrigir o recorte CHIRPS, a leitura de datas IBAMA e a geometria projetada identificada como inválida, mantendo rastreabilidade.
- Manter agregações IBAMA por município informado e por localização como alternativas distintas.
- Preservar intermediários superados e falhas de aquisição identificadas no catálogo.
- Não realizar regressões finais nem tratar as escolhas candidatas como decisões metodológicas aprovadas.

Os fundamentos e limites dessas decisões estão detalhados na seção 7. As escolhas ainda não resolvidas estão na seção 9.

## 7. Dados/fontes utilizados

As tabelas abaixo são candidatas para análise. A existência de uma variável processada não implica aprovação da sua definição econômica ou comparabilidade histórica.

| Fonte e versão | Cobertura e produto | Resultado e limite principal |
|---|---|---|
| IBGE PAM, tabela 1612 | Soja e milho, 1974–2025; 14.768 linhas, 142 códigos municipais | Área, produção e rendimento, com disponibilidade variável por município e ano. |
| IBGE PPM, tabela 3939 | Bovinos, 1974–2024; 7.191 linhas, 141 códigos | A consulta incluiu 2025, mas esse ano não foi retornado. |
| MapBiomas 10.1 | 1985–2024; 113.600 linhas de classes e 5.640 linhas de estoque nativo, 141 municípios | Estoque e participação de vegetação; conversões brutas ainda ausentes. |
| CHIRPS v2 | 540 rasters mensais, 1981–2025 | 76.680 observações municipais mensais e 6.390 anuais, em 142 municípios. |
| GAEZ v4 | Clima histórico 1961–1990; oito rasters | 1.136 linhas de aptidão e rendimento atingível, com variantes separadas. |
| IBGE biomas 2019 + malha 2024 | Interseções espaciais em 142 municípios | Frações por bioma e classificações candidatas de predominância. |
| Copernicus GLO-90 | 101 tiles originais | Estatísticas de elevação nos 142 municípios; modelo de superfície. |
| IBAMA, autos de infração | 52.991 eventos de MT, 1987–2026 | Contagens e valores candidatos; 2026 é parcial e fiscalização pode ser endógena. |
| World Bank Pink Sheet | Janeiro de 1960 a agosto de 2026 | 2.400 observações mensais de soja, milho e carne bovina em USD nominais. |
| CONAB | Três planilhas de custos | Células de MT extraídas com coordenadas de origem; séries ainda não harmonizadas. |
| ZARC | Portaria 372, soja MT, safra 2025/26 | Documento obtido; não estabelece calendário retrospectivo para toda a amostra. |

### 7.1. Produção e pecuária

Os símbolos originais do SIDRA foram preservados em colunas auxiliares. Na versão numérica, valores não numéricos ficaram ausentes, inclusive o símbolo `-`, que pode representar zero absoluto. **Essa decisão conservadora precisa ser revista antes da análise**, distinguindo os significados oficiais de cada símbolo.

O rendimento calculado usa produção em toneladas multiplicada por 1.000, dividida pela área colhida positiva. A maior diferença absoluta em relação ao rendimento publicado foi inferior a 1 kg/ha. Não houve imputação automática.

### 7.2. Vegetação e conversão

A aquisição da coleção 10.1 foi autenticada pelo MD5 oficial. A descrição do registro contém referência à coleção 10, enquanto título e arquivo indicam 10.1; a divergência foi registrada. A página atual já anunciava a coleção 11, que não foi incorporada silenciosamente. Um arquivo alternativo da coleção 9 foi mantido separado; apesar da descrição mencionar transições, as abas encontradas continham cobertura.

Nove linhas rotuladas como MT, com nomes Sonora, Aruanã e Nova Crixás, não tiveram correspondência exata no cadastro municipal utilizado e foram colocadas em quarentena.

O estoque nativo candidato soma as classes 3, 4, 5, 6, 49, 11, 12 e 50. O denominador da participação corresponde à soma de todas as classes mapeadas, incluindo água e áreas não observadas. A taxonomia e o denominador exigem aprovação científica. A defasagem só foi construída quando havia ano anterior contíguo.

**Não foram construídas as conversões brutas total, para agricultura e para pastagem.** Diferenças líquidas entre estoques anuais não foram usadas como substituto. A próxima etapa exige transições entre pixels de uma mesma coleção, com máscaras e classes coerentes.

### 7.3. Clima

Foram preservados os 540 arquivos mensais globais originais de CHIRPS v2. A agregação municipal utiliza centros de pixels e pesos proporcionais ao cosseno da latitude, sobre a malha de 2024, sem reamostragem do raster.

Uma versão exploratória do recorte podia truncar a borda leste por arredondamento da janela. O recorte foi corrigido com limites externos completos; os intermediários antigos foram preservados e identificados como superados. Valores negativos de ausência, incluindo −9999, foram excluídos explicitamente.

Os totais anuais exigem 12 meses válidos. Foram produzidas normais candidatas de 1981–2010 e 1991–2020, exigindo 30 anos completos; anomalias absolutas, escores padronizados e componentes de déficit e excesso foram calculados. São medidas de **ano civil**, não uma janela agrícola definida nem um balanço hídrico. O uso de normais que contêm anos posteriores às primeiras observações também precisa ser discutido.

Não foram adquiridos dados de temperatura ERA5-Land. Foram preparados documentação e pedido de aquisição, mas faltam configuração de acesso ao CDS e aceitação das condições aplicáveis. Médias mensais de temperatura tampouco permitiriam construir extremos diários.

### 7.4. Aptidão, biomas e relevo

O GAEZ v4 foi mantido separado de versões mais recentes. As oito variantes combinam soja ou milho, aptidão contínua ou rendimento atingível, e alto ou baixo nível de insumos, em sequeiro e sem fertilização por CO₂. A aptidão `sx` tem escala de 0 a 10.000; o rendimento `yx` está em kg de matéria seca por hectare. Não equivale ao rendimento observado da PAM.

Embora o clima de referência seja 1961–1990, a base de terras inclui 2010. Portanto, essas medidas não são automaticamente predeterminadas para uma análise iniciada em 1985. Não foi inventada uma proxy de aptidão para bovinos.

As interseções entre malha e biomas foram calculadas em projeção de área equivalente. Uma geometria tornou-se inválida após reprojeção e foi reparada apenas na cópia projetada, com alteração de aproximadamente 3,38 m² em uma área da ordem de 4,26 trilhões de m². As frações não foram renormalizadas para ocultar pequenos desencontros de borda.

Foram disponibilizados limiares de predominância de 70%, 80% e 90%. Com 80%, resultam 63 municípios amazônicos, 51 de Cerrado, 26 mistos e dois de Pantanal. Esses números dependem da regra candidata.

O Copernicus GLO-90 é um modelo digital de superfície, que pode incluir vegetação e construções. Não foram inferidas declividade ou rugosidade a partir da elevação média municipal.

### 7.5. Fiscalização, preços e custos

Na base de autos do IBAMA foram identificados 379 eventos sem identificador, nenhum identificador não vazio duplicado e 156 valores monetários ausentes. A leitura de datas foi corrigida para aceitar formatos mistos; ao final, não restaram datas sem interpretação.

A agregação pelo município informado contém 3.006 linhas e 141 códigos. A alternativa espacial contém 2.008 linhas e 138 códigos. Entre 25.345 coordenadas dentro da extensão de MT, 132 não intersectaram um polígono; houve 2.355 divergências entre município informado e espacial. O datum foi assumido como EPSG:4326 para essa alternativa, sem autenticação documental. Todos os status foram mantidos. Ausência de registros não foi convertida automaticamente em zero.

Os valores monetários são nominais registrados, sem representar multas pagas ou uma série real homogênea. Arquivos de coordenadas e histórico de embargos foram obtidos, mas não permitem, sem tratamento adicional, contar cada linha como embargo único ou estimar uma série histórica válida de área embargada.

Os preços internacionais estão em USD por tonelada para soja e milho e USD por kg para carne bovina. Foram calculados logaritmos e diferenças mensais. Carne bovina internacional não equivale ao preço local do boi gordo. Essas séries servem como candidatas a choques externos ou robustez, condicionadas à estratégia de identificação.

As planilhas CONAB abrangem soja de 1997–2026, milho de primeira safra de 1997–2025 e segunda safra de 2005–2025. Foram extraídas, respectivamente, 24.156, 2.975 e 18.229 células de MT, mantendo arquivo, aba, linha e coluna. Isso ainda não constitui uma série de custos comparável entre tecnologias, municípios e anos.

## 8. Testes e validações executados

Os 13 testes de integração passaram na execução registrada. Cobriram preservação de originais, autenticidade MapBiomas, chaves e rendimento PAM, símbolos SIDRA, estoque e defasagens de vegetação, quarentena, frações de biomas, transformações de preços, reconciliação de eventos IBAMA, variantes GAEZ, completude e identidades climáticas e cobertura dos rasters de chuva e elevação.

O replay verificou 822 requisições bem-sucedidas, sem erros, reutilizando e autenticando os arquivos locais. **Não foram realizados 822 novos downloads nessa verificação.** Os manifestos registram URL, horário, tamanho, hash e status das aquisições. Oito falhas de rede ou HTTP foram registradas; um endereço com extensão PDF retornou HTML e foi identificado como formato incorreto.

Os perfis de qualidade abrangem chaves, duplicações, ausências, cobertura temporal e espacial e estatísticas descritivas. Outliers foram sinalizados, sem exclusão automática.

O catálogo CSV e o XLSX foram comparados célula a célula: 1.737 linhas de dados, 19 colunas e nenhuma fórmula. O XLSX possui uma aba, filtro e congelamento em B2, e foi inspecionado visualmente. Para evitar conversão automática de timestamps em números de data do Excel, a representação textual recebeu o prefixo `UTC:`, preservando o timestamp completo. Os manifestos originais permaneceram intactos.

Evidências: [testes](../data/catalog/testes_h1_h2.txt), [perfis](../data/catalog/perfis_validacao_h1_h2.json), [replay](../data/catalog/replay_result.json) e [validação do XLSX](../data/catalog/validacao_catalogo_xlsx.json).

## 9. Pendências e riscos

### Acesso a fontes

- CEPEA: HTTP 403 impediu a aquisição pretendida de preços locais.
- IMEA: houve falha de certificado TLS e um endereço de metodologia retornou 404.
- CONAB: a consulta de preços exige código de segurança/CAPTCHA.
- ERA5-Land: aquisição depende de configuração da conta CDS e das condições de acesso.
- CAR: acesso retornou HTTP 401; estoque atual não foi retroagido como histórico.
- IBAMA: links principais de embargos em CSV e SHP retornaram 404; os arquivos alternativos exigem tratamento próprio.
- MMA: um suposto PDF histórico retornou HTML. A lista atual não foi tratada como histórico completo de entrada, saída e vigência das normas.

### Trabalho técnico ainda necessário

- Obter e processar transições brutas de vegetação de uma mesma coleção.
- Construir e validar a harmonização territorial histórica, com atenção a Boa Esperança do Norte, Sorriso e Nova Ubiratã.
- Resolver a diferença entre os 142 municípios da malha e os 141 presentes em MapBiomas e PPM.
- Consolidar preços locais e, se necessário, custos comparáveis.
- Reconstruir séries institucionais com vigência normativa e eventos únicos de embargos.
- Confirmar datum, regras de atribuição municipal e status dos eventos de fiscalização.
- Rever o significado dos símbolos SIDRA antes de tratar zeros e ausências.

### Decisões científicas pendentes

- Unidade territorial e período da amostra, incluindo tratamento de mudanças municipais.
- Definição de vegetação nativa, denominadores e destinos da conversão.
- Vintage e uso da aptidão produtiva, incluindo a restrição temporal do GAEZ e a eventual proxy para pecuária.
- Fonte, frequência, moeda, deflação e defasagem dos preços.
- Janela agrícola, normal climática, vintage CHIRPS e eventual inclusão de temperatura.
- Regra de classificação dos biomas e tratamento de municípios mistos.
- Estratégia de identificação para instituições e fiscalização potencialmente endógenas.

### Cobertura possível para H1 e H2

A disponibilidade de estoque de vegetação de 1985–2024 permite sua defasagem a partir de 1986. A chuva cobre 1981–2025. Assim, **1986–2024 é uma janela potencial**, condicionada à definição territorial, à disponibilidade efetiva de produção e às demais escolhas.

Essa janela não é uma amostra final. Para H1 faltam, em especial, conversões brutas e componentes de retorno e instituições. Para H2 com chuva, ainda faltam validação territorial e definição da janela climática agrícola. Se temperatura for obrigatória, também há uma lacuna de aquisição. A interseção de todas as variáveis centrais ainda não está disponível.

## 10. Próximo passo recomendado

1. Decidir a unidade territorial e validar a correspondência histórica antes de integrar as fontes.
2. Fixar a taxonomia de vegetação e obter conversões brutas coerentes com a coleção escolhida.
3. Aprovar calendário agrícola, normal climática e significado dos símbolos SIDRA.
4. Definir medidas de retorno esperado e avaliar a validade temporal do GAEZ.
5. Completar preços e séries institucionais prioritárias, com documentação de acesso e vigência.
6. Construir o painel integrado, medir perdas por junção e ausência e só então definir a amostra analítica.
7. Revisar a estratégia de identificação e registrar especificações antes das estimações finais.

Esses itens são recomendações para a próxima etapa; não são atividades já concluídas.

## 11. Estado final do Git

O checkpoint inicial foi confirmado em 29 de setembro de 2026:

- Branch `main`, sincronizada com `origin/main`, com working tree limpo no início.
- Commit de referência: `e5c8ece0c4516a79e2cef0b293ae2ce13f1259ce`.
- Existência e estrutura de `2_INTI/data` verificadas antes das alterações.
- Os 210 arquivos originais versionados foram inventariados com SHA256.

A verificação final registrou **nenhum original alterado e nenhum hash divergente**. Não houve commit, push, merge ou mudança de branch. As adições da tarefa ficaram disponíveis localmente para revisão. Na preparação deste relatório, a branch continuava `main` e a consulta de status dos arquivos rastreados não indicou alterações.

Evidências: [baseline de hashes](../data/catalog/baseline_repositorio_sha256.csv), [inventário original](../data/catalog/inventario_repositorio_original.csv) e [verificação de preservação](../data/catalog/verificacao_preservacao_h1_h2.json).

### Estado na adaptação deste relatório — 30 de setembro de 2026

- `git branch --show-current`: `main`.
- `git rev-parse HEAD`: `e5c8ece0c4516a79e2cef0b293ae2ce13f1259ce`.
- `git rev-list --left-right --count HEAD...origin/main`: `0 0`; sem commits à frente ou atrás da referência local `origin/main`. Não foi realizado `fetch` nesta adaptação.
- `git status --short`: somente entradas `??`, correspondentes a arquivos não rastreados em `2_INTI/code`, `2_INTI/data` e `2_INTI/reports`, incluindo caches Python.
- **O working tree final não está limpo:** há adições locais ainda não versionadas. Os arquivos já rastreados não apresentam modificações.
- Nenhum commit, push, merge ou troca de branch foi realizado. Antes de eventual versionamento, deve-se selecionar quais dados volumosos, intermediários e caches devem integrar o Git.

## Complemento — Questões para obter feedback em outro chat

Solicitar uma avaliação crítica dos seguintes pontos:

1. As medidas candidatas correspondem aos mecanismos econômicos de H1, H1-a, H1-b, H2 e H2-a?
2. Qual tratamento territorial permite comparar o período histórico sem atribuir retrospectivamente áreas de municípios recém-criados de forma indevida?
3. A base de terras de 2010 do GAEZ inviabiliza seu uso como capacidade predeterminada desde 1985? Quais alternativas são justificáveis?
4. Quais classes e denominadores devem definir estoque nativo e conversão bruta para agricultura e pastagem?
5. Como combinar preços internacionais ou locais com aptidão sem confundir unidades, exposição e mecanismos de transmissão?
6. Qual janela agrícola e normal climática são adequadas? Como tratar uma normal que inclui anos futuros em relação às primeiras observações?
7. Como usar autos, multas e embargos sem presumir exogeneidade ou equiparar valores registrados a sanções efetivas?
8. Como resolver os símbolos SIDRA, especialmente `-`, sem introduzir ausências artificiais ou zeros indevidos?
9. Quais lacunas impedem identificação e quais podem ser tratadas em análises de robustez?
10. Que evidências adicionais são indispensáveis antes de construir a amostra e estimar os modelos?

### Texto sugerido para iniciar a revisão

> Leia este relatório como registro de uma auditoria e preparação de dados para pesquisa econométrica municipal em Mato Grosso. Avalie a coerência entre hipóteses, variáveis, unidades, cobertura temporal e estratégia de identificação. Distinga problemas de dados, implementação e escolhas científicas. Não presuma que o painel esteja completo, que as medidas candidatas tenham sido aprovadas ou que fiscalização seja exógena. Priorize as pendências que impedem uma análise defensável e proponha decisões justificadas para cada uma. Quando uma conclusão depender dos arquivos de evidência vinculados e eles não estiverem disponíveis, indique exatamente o que precisa ser consultado.

## Conclusão

A execução estabeleceu uma base rastreável de fontes e transformações, preservou os arquivos originais e produziu validações reproduzíveis. O próximo avanço depende de resolver a geografia histórica, as conversões brutas e as escolhas de mensuração e identificação. Este relatório permite revisar essas decisões sem confundir disponibilidade de arquivos com prontidão para estimação.
