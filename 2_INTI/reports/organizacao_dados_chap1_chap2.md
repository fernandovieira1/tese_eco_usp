# Organização das bases dos capítulos 1 e 2

**Data:** 2 de outubro de 2026.  
**Etapa:** INTI, preparação dos artigos para a qualificação.  
**Diretório:** `2_INTI/data`.

## Resultado

As bases foram distribuídas em `data/chap1` e `data/chap2`, mantendo a estrutura interna `raw`, `interim`, `processed` e `catalog`, conforme aplicável. Os arquivos úteis aos dois artigos receberam cópias físicas independentes. Os nomes dos arquivos e os conteúdos dos dados foram preservados; os prefixos históricos `h1__` e `h2__` não impedem seu aproveitamento como controles no outro artigo.

Foram realocados **1.512 arquivos** e produzidas **1.497 cópias compartilhadas**. Cada destino foi confrontado com o tamanho e o SHA256 do arquivo anterior, sem divergências. A reorganização acrescentou 8.756.128.794 bytes, aproximadamente 8,15 GiB. Não houve aquisição de novas bases, mudança de coleção, estimação, imputação ou formação de um painel final.

| Localização | Brutos | Intermediários | Tabelas processadas | Total de arquivos de dados | Bytes |
|---|---:|---:|---:|---:|---:|
| `data/chap1` | 822 | 671 | 19 | 1.512 | 9.661.301.069 |
| `data/chap2` | 815 | 671 | 11 | 1.497 | 8.756.128.794 |
| Total físico após as cópias | 1.637 | 1.342 | 30 | 3.009 | 18.417.429.863 |

Esses números excluem os catálogos e seus documentos de auditoria. As 30 tabelas físicas correspondem a 19 tabelas distintas, das quais 11 foram copiadas. A existência de uma tabela candidata não equivale à disponibilidade de uma variável econométrica validada.

## Critério de distribuição

| Base ou conjunto de arquivos | Capítulo 1 — H1 | Capítulo 2 — H2 | Uso e limite |
|---|---|---|---|
| IBGE/PAM: soja e milho | Cópia | Cópia | Produção, áreas e rendimento; preservados os símbolos SIDRA. |
| IBGE/PPM: bovinos | Cópia | Cópia | Pressão e composição agropecuária em H1; contexto ou controle possível em H2, sem inclusão automática na especificação. |
| MapBiomas: coleções 10.1 e 9 separadas, classes e estoque nativo | Cópia | Cópia | Uso e cobertura em H1; estoque e defasagem em H2. A coleção 9 permanece alternativa; não foi combinada à 10.1. |
| IBGE: cadastro, malha municipal e biomas | Cópia | Cópia | Suporte territorial e heterogeneidade dos dois artigos; harmonização histórica ainda pendente. |
| GAEZ v4: rasters e agregados municipais | Cópia | Cópia | Capacidade produtiva candidata em H1; heterogeneidade física possível em H2. Base de terras de 2010 exige cuidado com sua predeterminação. |
| Copernicus GLO-90: 101 tiles, metadados e agregados | Cópia | Cópia | Controle físico possível nos dois artigos; DSM não equivale a relevo de terreno nu. |
| CHIRPS v2: 540 rasters mensais brutos | Cópia | Original realocado | 1981–2025. As duas pastas contêm os insumos que permitem reproduzir as medidas climáticas, centrais em H2 e possíveis controles em H1. |
| CHIRPS: 540 recortes corrigidos e 131 recortes exploratórios superados | Cópia | Original realocado | Os intermediários superados continuam preservados e separados. |
| CHIRPS: precipitação municipal mensal e anomalias anuais candidatas | Cópia | Cópia | Variável central de H2 e controle possível em H1; janelas de safra e normais ainda precisam de decisão científica. |
| IBAMA: autos, histórico e coordenadas de embargos; agregações candidatas | Original realocado | — | Instituições, fiscalização e sanções em H1. As tabelas disponíveis não resolvem a ausência da base principal de embargos. |
| Banco Mundial: preços internacionais e derivados | Original realocado | — | Candidatos para robustez em H1; não substituem preços locais nem constituem retorno esperado líquido. |
| CONAB: três planilhas e extração das células de MT | Original realocado | — | Custos em H1; extração ainda não constitui série homogênea. |
| Documentação das fontes, portaria ZARC e respostas consultadas | Cópia | Cópia | Preserva as evidências de consulta e de restrição. Documento presente não implica base analítica adquirida. |

## Rastreabilidade e catálogos

O diretório [`data/catalog`](../data/catalog) conserva os manifestos, inventários, baseline, relatórios e resultados da auditoria anterior. Seus caminhos `data/raw`, `data/interim` e `data/processed` descrevem a localização à época da coleta. Esses registros não foram reescritos para encobrir a reorganização.

O mapa completo entre localização anterior e atual está em [`relocacao_chap1_chap2_20261002.csv`](../data/catalog/relocacao_chap1_chap2_20261002.csv). Cada linha informa capítulo, operação, tamanho, SHA256 e instante de verificação. As 1.497 linhas de cópia têm o mesmo SHA256 da respectiva origem realocada.

Cada capítulo recebeu:

- `catalog/inventario_arquivos.csv`: localização atual e anterior, integridade, fonte, URL e status anterior;
- `catalog/catalogo_variaveis.csv`: visão do catálogo anterior com caminhos atuais, mantendo a hipótese e o status científico registrados na auditoria de origem;
- `catalog/acquisition*.jsonl`: visões dos manifestos pertinentes, com caminho anterior explícito. Os originais comuns permanecem em `data/catalog`.

Os catálogos são recortes documentais da execução anterior, produzidos em 2 de outubro de 2026. Seus marcadores de hipótese preservam a linhagem; o quadro acima explica o aproveitamento de controles pelo outro artigo. As lacunas relevantes para cada hipótese foram mantidas mesmo quando não há arquivo correspondente. As planilhas XLSX e suas imagens de validação anteriores permanecem como produtos históricos do catálogo comum.

## Compatibilidade dos scripts

[`code/data_paths.py`](../code/data_paths.py) centraliza a resolução dos caminhos. `data_path(caminho)` escolhe a cópia canônica: capítulo 2 para rasters climáticos e intermediários; capítulo 1 para as demais bases atuais. `data_path(caminho, chapter='chap2')` permite consultar uma cópia atribuída ao segundo artigo. Os arquivos compartilhados são cópias comuns, sem links simbólicos ou atalhos.

As rotinas de aquisição e preparação foram adaptadas para usar o caminho completo da fonte ou uma pasta homogênea. `prepare_h1_h2.save` também atualiza a cópia compartilhada de um produto regenerado. Em aquisições, `fetch` continua recusando um bruto existente que não corresponda à URL e ao hash do manifesto; a comparação reconhece os caminhos anteriores à realocação. A cópia de um bruto compartilhado divergente é recusada.

O gerador `catalog_h1_h2.py` reconhece a proveniência de arquivos realocados. Seu teste de preservação do checkpoint integral continua estrito. **Os geradores históricos de auditoria e relatório não foram reexecutados:** este pedido autoriza mudanças no texto e nos scripts, incompatíveis com a exigência antiga de que todo o repositório permanecesse idêntico ao checkpoint de setembro. O baseline anterior não foi redefinido. A preservação dos dados foi verificada de forma independente, para todos os arquivos realocados.

As versões dos scripts anteriores à mudança de caminhos foram copiadas para [`backup/2026-10-02_separacao_h1_h2/code_antes_reorganizacao_dados`](../backup/2026-10-02_separacao_h1_h2/code_antes_reorganizacao_dados).

## Verificações realizadas

| Verificação | Resultado |
|---|---|
| Destinos absolutos dentro de `2_INTI/data`, antes de mover | Todos validados |
| Tamanho e SHA256 dos 3.009 destinos contra os 1.512 arquivos anteriores | Nenhuma divergência |
| Correspondência das 822 aquisições bem-sucedidas com o mapa de realocação | Todas confirmadas |
| Reutilização de seis fontes pela função `fetch`, com acesso de rede desabilitado | Todas reutilizadas com proveniência reconhecida |
| Caminhos de arquivos nos dois catálogos de variáveis | Todos existentes |
| Sintaxe de todos os scripts Python | Válida |
| Testes substantivos de dados | 12 aprovados em 8,04 segundos |
| Teste histórico `checkpoint_originals_unchanged` | Excluído da execução porque o pedido atual modifica o projeto; baseline preservado |

Evidências: [`validacao_organizacao_chap1_chap2_20261002.json`](../data/catalog/validacao_organizacao_chap1_chap2_20261002.json) e [`validacao_caminhos_chap1_chap2_20261002.json`](../data/catalog/validacao_caminhos_chap1_chap2_20261002.json).

Para repetir a verificação da realocação, na raiz do repositório:

```powershell
python 2_INTI/code/organize_chapter_data.py --verify
python -m pytest 2_INTI/code/test_h1_h2.py -q -p no:cacheprovider -k 'not checkpoint_originals_unchanged'
```

O segundo comando pressupõe o ambiente documentado em `code/requirements-audit-lock.txt`. A primeira execução de `organize_chapter_data.py --apply` já foi concluída; o script recusa sua repetição sobre o mesmo manifesto.

## Limites para a qualificação

**H1:** continuam ausentes as conversões brutas anuais de vegetação para agricultura e pastagem, preços locais homologados, um índice definitivo de retorno esperado e séries institucionais históricas completas. Variação líquida do estoque de vegetação não substitui conversão bruta. Autos e multas registrados não medem automaticamente efetividade institucional, pagamento ou exogeneidade.

**H2:** a combinação de vegetação, chuva e rendimento já tem insumos candidatos. Ainda faltam a harmonização territorial, a definição das janelas agrícolas e da normal climática, além de temperatura quando exigida pela especificação. O pedido ERA5-Land continua preparado, sem dados de temperatura adquiridos. Defasagem do estoque nativo não assegura, isoladamente, identificação causal de sua interação com o clima.

**Ambos:** Boa Esperança do Norte e as diferenças entre 141 e 142 códigos municipais exigem tratamento antes da fusão. Os símbolos SIDRA, as variantes GAEZ, a escolha das classes nativas e a heterogeneidade de biomas permanecem decisões explícitas. A organização por capítulo torna os insumos acessíveis; ela não transforma alternativas em especificações aprovadas nem lacunas em resultados.
