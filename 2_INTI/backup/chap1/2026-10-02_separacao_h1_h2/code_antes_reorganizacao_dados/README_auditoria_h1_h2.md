# Reprodução da auditoria H1/H2

## Ambiente e preservação

Trabalhar em `main`. Dados novos devem permanecer em `2_INTI/data`. Os scripts originais não foram editados. O ambiente usado foi Python 3.12, com dependências exatas em `requirements-audit-lock.txt`; ele foi instalado em um ambiente virtual temporário separado do repositório e das dependências internas do aplicativo.

Instalação reproduzível, em ambiente virtual escolhido pelo pesquisador:

```powershell
python -m venv "$env:TEMP/inti-audit-env"
& "$env:TEMP/inti-audit-env/Scripts/python.exe" -m pip install -r 2_INTI/code/requirements-audit-lock.txt
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

Os comandos abaixo usam `python` do ambiente virtual ativado. Executar na raiz do repositório. Não refazer downloads já autenticados: `fetch` verifica hash e URL e recusa substituir arquivos existentes. Os manifestos usam snapshots específicos; uma atualização futura precisa de novo nome/vintage. Falhas de transporte ficam registradas. HTTP200 deve ser acompanhado de validação de conteúdo.

## Auditoria inicial

```powershell
git status
git branch --show-current
python 2_INTI/code/audit_repository.py
```

O baseline contém o checkpoint de 29/09/2026. Após um futuro commit, não executar o auditor antigo para redefinir esse baseline: ele deliberadamente recusa diferenças. Consultar a errata em `auditoria_dados_h1_h2.md` para os trechos de prosa fixa do script original.

## Aquisição

```powershell
python 2_INTI/code/acquire_h1_h2.py --stage core
python 2_INTI/code/acquire_h1_h2.py --stage pages
python 2_INTI/code/acquire_h1_h2.py --stage extra
python 2_INTI/code/acquire_candidates.py
python 2_INTI/code/acquire_followups.py
python 2_INTI/code/acquire_selected_resources.py
python 2_INTI/code/acquire_raster_candidates.py
python 2_INTI/code/acquire_gaez.py
python 2_INTI/code/acquire_dem.py
python 2_INTI/code/acquire_chirps.py
python 2_INTI/code/acquire_era5land.py
```

A ordem resolve dependências entre documentos e URLs de recursos. A criação do pedido ERA5 não inicia download. `--download` exige conta CDS, aceite da licença e `cdsapi` configurado fora do Git. Os dados de temperatura ainda não foram adquiridos.

Para reproduzir **todas** as requisições efetivamente registradas, inclusive documentos obtidos na investigação interativa, usar `python 2_INTI/code/replay_acquisitions.py`. Por padrão, ele autentica/reutiliza aquisições bem-sucedidas; `--retry-failures` repete também falhas. Fontes mutáveis podem não reproduzir bytes de um snapshot antigo: divergências são explicitamente rejeitadas. Por isso é necessário preservar os brutos, e não apenas as URLs.

CHIRPS usa seis trabalhadores independentes, cada ano com manifesto próprio. DEM usa quatro trabalhadores, com manifesto por tile. São paralelizações de download, sem agentes externos. Arquivos `.interrupted` preservam transferências interrompidas; não são inputs analíticos. Se surgir um novo `.part` após falha, preservar com nome de tentativa antes de repetir; não substituir o bruto validado.

## Preparação e catálogo

```powershell
python 2_INTI/code/prepare_h1_h2.py --stage sidra
python 2_INTI/code/prepare_h1_h2.py --stage mapbiomas
python 2_INTI/code/prepare_h1_h2.py --stage prices
python 2_INTI/code/prepare_h1_h2.py --stage vectors
python 2_INTI/code/prepare_ibama.py
python 2_INTI/code/prepare_supplements.py
python 2_INTI/code/prepare_static_rasters.py
python 2_INTI/code/prepare_chirps.py
python 2_INTI/code/territorial_coverage.py
python 2_INTI/code/catalog_h1_h2.py
python -m pytest 2_INTI/code/test_h1_h2.py -q -p no:cacheprovider
python 2_INTI/code/report_h1_h2.py
```

Os derivados desta auditoria são regeneráveis; os brutos são imutáveis. `catalog_h1_h2.py` compara todos os arquivos do checkpoint e os hashes de aquisição. O baseline não é redefinido. Não interpretar arquivo parcial de processamento como conclusão da coleta: a validação deve confirmar 540 meses CHIRPS e 101 tiles DEM antes de homologar cobertura.

`build_catalog_xlsx.mjs` converte o CSV canônico em XLSX usando `@oai/artifact-tool`, a biblioteca disponibilizada no ambiente Codex. Executar em diretório temporário com acesso à dependência, sem instalar pacotes Node no repositório:

```powershell
node build_catalog_xlsx.mjs CAMINHO_CSV CAMINHO_XLSX CAMINHO_PREVIEW_PNG
```

Os três destinos devem apontar para `2_INTI/data/catalog`. Para esta execução foram usados `data_catalogo_variaveis_h1_h2.csv`, `data_catalogo_variaveis_h1_h2.xlsx` e `catalogo_preview.png`. Não há fórmulas no catálogo: o XLSX é uma visão tabelada dos metadados. A comparação final reabre o XLSX com openpyxl apenas para leitura e compara cada célula com o CSV.

O catálogo também gera `data_catalogo_variaveis_h1_h2.values.json`, entrada do builder. Timestamps de acesso recebem o prefixo textual `UTC: ` para impedir que a biblioteca os converta em datas seriais do Excel, que perderiam a representação original com fuso e microssegundos. O timestamp ISO completo permanece preservado no campo e, sem prefixo, no manifesto original.

## Limites deliberados

Não existe painel final fundido. Alternativas de geometria, coleção, capacidade produtiva, janela climática, normal e identificação continuam separadas. Nenhum índice de retorno, regressão, imputação ou instituição automaticamente exógena foi criado. Ver `relatorio_final_h1_h2.md` e a matriz de requisitos para os bloqueios e decisões restantes.
