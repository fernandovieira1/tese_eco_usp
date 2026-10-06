# Ambiente computacional — fase INTI

Este documento registra o ambiente computacional adotado para a fase INTI da tese e as convenções necessárias para sua reprodução.

## 1. Python

### 1.1. Versão canônica

A versão canônica do projeto é:

**Python 3.12.10**

O ambiente virtual local do projeto deve ficar em:

`2_INTI/code/.venv`

O `.venv`:

- não é versionado pelo Git;
- foi criado sem acesso aos pacotes globais do sistema;
- deve ser utilizado pelo VSCode, pelo terminal integrado e pelas rotinas executadas pelo Codex no projeto.

### 1.2. Arquivos de dependências

O projeto utiliza três arquivos com funções distintas.

#### `requirements.txt`

Contém apenas as dependências diretamente utilizadas pelo código ativo da fase INTI.

Atualmente:

- `geopandas`
- `numpy`
- `openpyxl`
- `pandas`
- `pytest`
- `rasterio`
- `requests`
- `shapely`

#### `requirements-audit-lock.txt`

Contém o ambiente Python completo e congelado utilizado e validado nas rotinas de auditoria e processamento H1/H2.

Esse arquivo é a referência para reconstrução exata do ambiente computacional validado.

#### `requirements-optional.txt`

Contém dependências necessárias apenas para tarefas específicas e que não integram, por padrão, o ambiente principal.

Atualmente inclui:

- `cdsapi==0.7.7`

O `cdsapi` é utilizado exclusivamente quando houver necessidade de acessar o Copernicus Climate Data Store para aquisição de dados ERA5-Land.

### 1.3. Reconstrução do ambiente validado

A partir da raiz do repositório:

```powershell
py -3.12 -m venv "2_INTI\code\.venv"
& "2_INTI\code\.venv\Scripts\Activate.ps1"
python -m pip install -r "2_INTI\code\requirements-audit-lock.txt"
python -m pip check
```

Para instalar apenas as dependências diretas do código ativo:

```powershell
python -m pip install -r "2_INTI\code\requirements.txt"
```

Dependências opcionais devem ser instaladas somente quando a tarefa correspondente exigir:

```powershell
python -m pip install -r "2_INTI\code\requirements-optional.txt"
```

A instalação de dependências opcionais modifica temporariamente o ambiente em relação ao `requirements-audit-lock.txt`. Portanto, elas não devem ser instaladas no ambiente principal sem necessidade.

### 1.4. Credenciais e configurações externas

Credenciais, tokens, chaves de API e arquivos de autenticação devem permanecer fora do repositório.

No caso do Copernicus Climate Data Store, o arquivo de autenticação, inclusive `~/.cdsapirc`, não deve ser versionado.

---

## 2. Testes

O pytest é configurado pelo arquivo localizado na raiz:

`pytest.ini`

O cache do pytest é direcionado para:

`2_INTI/code/.pytest_cache`

Essa configuração evita o uso da pasta `.pytest_cache` existente na raiz do repositório, que apresentou problema de permissão no Windows.

### 2.1. Testes funcionais correntes

Para executar os testes funcionais atualmente validados:

```powershell
python -m pytest "2_INTI\code\test_h1_h2.py" -k "not checkpoint_originals_unchanged" -q
```

Estado validado em **05/10/2026**:

**12 testes aprovados e 1 teste histórico deliberadamente excluído.**

### 2.2. Teste histórico de integridade

O teste:

`test_checkpoint_originals_unchanged`

compara arquivos atuais do projeto com os hashes registrados em:

`2_INTI/xdata/catalog/baseline_repositorio_sha256.csv`

Esse arquivo constitui um checkpoint histórico do repositório e atualmente está defasado em relação a alterações posteriores e legítimas, incluindo reorganização de arquivos, evolução dos textos, bibliografia, código e artefatos de compilação.

Por esse motivo, o teste não deve ser utilizado como critério corrente de aprovação até que sua finalidade e seu baseline sejam revisados de forma controlada.

A execução completa dos testes é:

```powershell
python -m pytest "2_INTI\code\test_h1_h2.py" -q
```

Enquanto o checkpoint histórico não for revisado, é esperado que essa execução apresente uma falha exclusivamente em `test_checkpoint_originals_unchanged`.

---

## 3. R

A versão configurada para o projeto é:

**R 4.6.1**

O RStudio e o VSCode estão configurados para utilizar essa versão.

Na fase INTI, atualmente não existem scripts ativos com extensões:

- `.R`
- `.Rmd`
- `.qmd`

Por esse motivo, não foi criado um ambiente `renv`.

Caso R passe a integrar o pipeline analítico da tese, a gestão reproduzível de suas dependências deverá ser configurada antes da incorporação do código R ao fluxo principal.

---

## 4. VSCode

A configuração específica do projeto encontra-se em:

`.vscode/settings.json`

Ela fixa:

- Python: `2_INTI/code/.venv/Scripts/python.exe`;
- R: `C:\Program Files\R\R-4.6.1\bin\R.exe`;
- LaTeX: TeX Live 2025;
- codificação dos arquivos: UTF-8.

O interpretador Python selecionado no workspace deve ser sempre:

`2_INTI/code/.venv/Scripts/python.exe`

O terminal integrado do VSCode deve indicar o ambiente ativo por meio do prefixo:

`(.venv)`

---

## 5. LaTeX

A distribuição LaTeX canônica do projeto é:

**TeX Live 2025**

O LaTeX Workshop está configurado para utilizar explicitamente:

`C:\texlive\2025\bin\windows\latexmk.exe`

A receita principal do VSCode é:

`latexmk (TeX Live 2025)`

Os artigos ativos utilizam atualmente BibTeX tradicional com:

`abntex2-alf`

e não `biblatex/biber`.

Os arquivos auxiliares de compilação LaTeX não são versionados pelo Git.

Os PDFs compilados automaticamente dos artigos ativos:

- `2_INTI/chapters/chap1/main.pdf`
- `2_INTI/chapters/chap2/main.pdf`

também não são versionados, pois são produtos reproduzíveis a partir dos arquivos-fonte.

### 5.1. Auditoria técnica dos artigos ativos

Na raiz do repositório:

```powershell
& "2_INTI\code\.venv\Scripts\python.exe" "2_INTI\code\audit_thesis.py"
```

O auditor usa somente a biblioteca padrão, funciona offline e compila `chap1` e
`chap2` em cópias temporárias com `latexmk`. Não altera fontes científicas nem
artefatos existentes. Os relatórios detalhados e logs são gravados em
`2_INTI/xreports/audit_thesis_<timestamp>/`. Apenas `ERROR` produz exit code 1;
`WARNING` e `INFO` não impedem aprovação. Consulte `--help` para auditar um único
artigo ou usar `--skip-compile` (compilação não verificada). De outro diretório,
utilize os caminhos absolutos do interpretador e do script.

### 5.2. Convenção de relatórios e continuidade

- `2_INTI/reports/` contém somente relatórios consolidados, decisões, validações e marcos relevantes; é versionado pelo Git.
- `2_INTI/xreports/` contém logs, diffs, relatórios timestampados, saídas de testes e outros artefatos automáticos ou reproduzíveis; é local e ignorado pelo Git.
- `2_INTI/thread/` contém registros relevantes para continuidade entre tarefas/agentes; é versionado pelo Git.

---

## 6. Política geral de reprodutibilidade

O ambiente computacional da tese segue as seguintes regras:

1. o código-fonte e os arquivos de configuração são versionados;
2. ambientes virtuais não são versionados;
3. dependências diretas são declaradas em `requirements.txt`;
4. o ambiente validado completo é preservado em `requirements-audit-lock.txt`;
5. dependências opcionais são mantidas separadas;
6. credenciais e segredos permanecem fora do repositório;
7. dados brutos e processados não são armazenados no Git;
8. metadados de aquisição, hashes, linhagem e validações relevantes são versionados;
9. artefatos temporários ou reproduzíveis de Python e LaTeX não são versionados;
10. alterações no ambiente computacional devem ser documentadas e validadas por testes antes de serem incorporadas ao fluxo principal.
