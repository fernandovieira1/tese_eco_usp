# Auditoria dos dados de H1 e H2

## Checkpoint e escopo

Em 29/09/2026, antes de alterações: `git status` limpo, branch `main`, sincronizada com `origin/main`, HEAD `e5c8ece0c4516a79e2cef0b293ae2ce13f1259ce`. A execução atravessou a mudança de dia; os manifestos usam UTC. Não houve checkout, criação de branch, merge, commit, push, alteração das hipóteses ou estimação de modelos finais.

O inventário inicial registra 210 arquivos, 117 commits alcançáveis, 28 ZIPs e 363 membros. Foram examinados conteúdos de 279 blobs históricos de texto/código/DOCX/ZIP e oito versões históricas de notebooks. Foram inspecionados os dois conjuntos de árvores sem referência encontrados pelo script existente. O escopo é o repositório local, incluindo refs e objetos disponíveis, sem afirmar inexistência de trabalho externo.

Evidências: `baseline_repositorio_sha256.csv`, `inventario_repositorio_original.csv`, `inventario_zip_membros.csv` e `auditoria_historico_git.json`. O primeiro arquivo autentica todos os originais; `verificacao_preservacao_h1_h2.json` compara seus hashes após o trabalho. README, textos metodológicos, backups, notebooks antigos e scripts existentes foram preservados.

## O que existia e decisão por componente

| Componente / caminho | Decisão | Justificativa e validação |
|---|---|---|
| `2_INTI/chapters/chap1/0_introduction.tex`, README e demais textos | APROVEITAR INTEGRALMENTE | Referência conceitual; não são prova de implementação empírica. H1/H2 e sub-hipóteses preservadas. |
| `2_INTI/code/data_common.py` | APROVEITAR COM AJUSTES | Função reutilizada por importação, sem editar o original. Manifestos separados e validação posterior de conteúdo adicionados: HTTP 200 não garante formato correto. Dependência `requests` ausente no Python padrão. |
| `2_INTI/code/discover_core.py` | APROVEITAR INTEGRALMENTE | URLs e parâmetros dos sete arquivos originais reutilizados. Não foi necessário repetir seus downloads. |
| `2_INTI/code/audit_repository.py` | APROVEITAR COM AJUSTES | Executado como evidência mecânica; prosa fixa exige as correções abaixo. Original preservado. |
| `raw/tabular/ibge/pam1612_metadata.json` | APROVEITAR INTEGRALMENTE | Agregado1612, periodicidade anual, produtos2711/2713 e variáveis109/216/214/112 autenticados; não contém observações da PAM. |
| `raw/tabular/ibge/ppm3939_metadata.json` | APROVEITAR INTEGRALMENTE | Agregado3939, variável105, categoria2670. Cobertura efetivamente retornada deve prevalecer sobre período solicitado. |
| `raw/tabular/ibge/municipios_mt_consulta20260928.json` | APROVEITAR COM AJUSTES | Cadastro corrente com142 códigos. Usado para associação nominal exata normalizada; não é crosswalk histórico. |
| `raw/tabular/mapbiomas/collection10_1_metadata.json` | APROVEITAR INTEGRALMENTE | DOI SJZOLT, arquivo535, versão10.1, cobertura1985–2024 e licença CC BY4.0; MD5 oficial confrontado com XLSX adquirido. A descrição menciona10, enquanto título/arquivo dizem10.1; inconsistência mantida documentada. |
| `raw/tabular/mapbiomas/statistics_page_20260928.html` | APROVEITAR COM AJUSTES | Snapshot da página já anuncia coleção11; não substituir10.1 com links correntes. |
| `raw/vector/ibge/biomes_directory.html` | APROVEITAR COM AJUSTES | Lista vintages2019 e2025. Baixado2019 como alternativa explicitamente identificada, sem declarar versão consolidada. |
| `raw/vector/ibge/MT_Municipios_2024.zip` | APROVEITAR COM AJUSTES |142 feições, EPSG 4674, originais válidos. Adequado para agregação espacial candidata; comparabilidade histórica depende de harmonização. |
| `data/catalog/acquisition_core.jsonl` | APROVEITAR INTEGRALMENTE | Sete URLs, datas, tamanhos e hashes preservados; aquisições novas em manifestos próprios. |
| `1_SUYANA/data/carbon_emissions.xlsx` | NÃO APROVEITAR no painel H1/H2 |86 observações globais1940–2025; chave ano única, sem missing nas duas colunas; mínimo4,26 e máximo38,11 bilhões de toneladas. Fonte não autenticada;2025 possui nota. Preservar como contexto. |
| Seis notebooks atuais e backups de `1_SUYANA` | NÃO APROVEITAR como pipeline municipal |Gráficos, emissões e simulações conceituais; nenhuma rotina empírica H1/H2 recuperável encontrada. Preservados. |
| Figura `mapa_biomas_mt.png` | NÃO APROVEITAR como dado vetorial |Ilustração não fornece geometrias ou classificação municipal auditável. |

Os caminhos abreviados de dados nesta tabela são relativos a `2_INTI/data`. O inventário geral identifica os arquivos individuais dos grupos documentais, seus hashes e extensões. Não havia suíte de testes, requirements, pipeline GEE, harmonização validada de Boa Esperança do Norte, unidade composta ou painel consolidado identificado no checkpoint.

## Correções da prosa produzida pelo script antigo

`auditoria_historico_repositorio.md` é a saída preservada de um script preexistente com parágrafos fixos. Não deve ser lido como relatório atualizado sem esta errata:

- A planilha de emissões não era o único dado do checkpoint: já havia a malha municipal e os seis arquivos de metadados/páginas.
- O mínimo efetivo da planilha é4,26, não4,85 como consta na prosa fixa.
- Havia três scripts de auditoria/descoberta, embora não houvesse processamento analítico municipal.
- Números e afirmações históricas devem ser conferidos no JSON calculado; não inferidos de trechos fixos.

## Problemas materiais encontrados

1. **Território:** malha/cadastro com142 municípios e cobertura MapBiomas com141 municípios de MT. Não existe crosswalk validado. Não ligar silenciosamente geometrias pós-desmembramento às séries anteriores de Sorriso/Nova Ubiratã. Unidade composta envolvendo Boa Esperança do Norte é uma alternativa a avaliar, não implementada por presunção.
2. **Taxonomia:** vegetação candidata inclui3,4,5,6,49,11,12,50. Exclui afloramento rochoso, apicum, água e aquicultura. Denominador é toda área mapeada. Preservadas legenda e áreas por classe para permitir outras definições.
3. **Associação municipal:** nove linhas MapBiomas marcadas MT têm nomes Sonora, Aruanã e Nova Crixás. Preservadas na quarentena, sem associação aproximada ou correção silenciosa.
4. **Transições:** arquivo da coleção9 anunciado como cobertura/transições tem apenas abas de cobertura. Não produzir `conv_*` com diferença líquida de estoque nem combinar coleção9 e10.1.
5. **Biomas:** uma geometria amazônica torna-se inválida após projeção. `make_valid` aplicado apenas à cópia projetada; mudança de área de cerca3,38 m² em4,26 trilhões de m² registrada. Lacunas de fronteira permanecem nas frações, sem normalização artificial.
6. **IBAMA:** identificadores ausentes, coordenadas zero, divergências entre município declarado e geocodificado, todos os status e valores nominais. Datas ISO com/sem horário exigiram parser misto. As versões declarada e espacial são separadas. Datum das coordenadas é hipótese provisória EPSG 4326, ainda não autenticada.
7. **Fontes:** CEPEA403; CAR401; IMEA falha de certificado; tabela e vetor principais de embargos404; link PDF histórico MMA devolveu HTML. Falhas preservadas com URL e resposta, sem contornar controles de acesso.
8. **GAEZ:** base de terras2010 não se torna predeterminada para todo o painel apenas por usar clima1961–1990. Índice0–10000 e rendimento alcançável da melhor classe têm significados diferentes. Pecuária não recebeu “aptidão bovina” inventada.

## Estado da entrega

Há dados e derivados candidatos auditáveis, mas o painel completo de H1/H2 não está homologado nem pronto para a estimação final. A matriz enumera lacunas reais e escolhas pendentes. O relatório final e a validação atualizam quantidades e cobertura após terminar as aquisições.
