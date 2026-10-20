# Descritiva do artigo 1

Executar **da raiz do repositório**, em R:

```powershell
Rscript --vanilla 2_INTI/chapters/chap1/stats/descritiva/analise_descritiva_h1.R
```

O script usa arrow, dplyr, tidyr, ggplot2, readr e jsonlite já disponíveis no ambiente. As versões estão em `dependencias.txt`; `sessionInfo()` está em `2_INTI/audit/descritiva_chap1_20261020/sessionInfo.txt`. Não instala pacotes, não usa rede nem procedimentos aleatórios. O PDF vetorial usa o dispositivo nativo do R com codificação latina e sem fontes Dingbats; os PNG têm 320 dpi.

## Entradas e salvaguardas

- `../df_h1` e `../df_h1_proveniencia`: arquivos Parquet sem extensão; preservados.
- Painel identificado: `2_INTI/chapters/chap1/stats/EDA/paineis/painel_tese_chap1_pt.csv`, conferido contra a cópia canônica em `2_INTI/xdata/chap1/processed/harmonizacao/painel_notebook/paineis/`.
- Dicionário e cadastro municipal em `2_INTI/xdata/chap1/processed/`.

A exportação original descartou as chaves do MultiIndex. A recuperação exige igualdade das máscaras de ausência e dos valores das 176 colunas com o painel identificado ordenado por município e ano. O script interrompe se essa correspondência falhar. Diferenças de serialização numérica são toleradas até `1e-12` na comparação; valores analíticos vêm do Parquet.

Este fluxo reproduz os resultados a partir dos insumos locais fornecidos; não refaz downloads e extrações geoespaciais anteriores. A linhagem dessas etapas está documentada no dicionário e no relatório técnico.

## Produtos

- `dados/df_h1_selecionado.{rds,parquet,csv}`: 15 variáveis analíticas e quatro identificadores; nenhuma linha excluída.
- `dicionario_variaveis.csv`: definições, unidades, fórmulas, fontes, evidências, cobertura e justificativas.
- `candidatas_excluidas.csv`: escolhas e limites da seleção.
- `figuras/`: quatro figuras, cada uma em PDF vetorial e PNG.
- `tabelas/`: duas tabelas e macros numéricas LaTeX.
- `dados/`: estatísticas subjacentes e números usados no texto.
- Seção integrada: `2_INTI/chapters/chap1/text/2_mt_descriptive.tex`.
- Auditoria, diagnósticos, logs e relatório: `2_INTI/audit/descritiva_chap1_20261020/`.
- Pareceres independentes sequenciais: `2_INTI/audit/works/chap1/descritiva_20261020/`.

Para validar a integração, executar da raiz em PowerShell:

```powershell
python 2_INTI/audit_thesis.py --chapters chap1 --skip-compile
$build = Join-Path (Get-Location).Path '2_INTI/audit/descritiva_chap1_20261020/latex'
New-Item -ItemType Directory -Force -Path $build | Out-Null
Push-Location 2_INTI/chapters/chap1/text
latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir="$build" main.tex
Pop-Location
```

O auditor genérico exclui `stats` e PDFs da cópia temporária usada por sua compilação. Por isso, neste fluxo a auditoria estática e a compilação direta são etapas separadas; executar o auditor sem `--skip-compile` não reproduz a integração dos ativos desta seção. A compilação direta mantém os caminhos reais e grava PDF, logs e auxiliares na auditoria.

Os scripts regeneram somente os produtos desta pasta e os diagnósticos dedicados. Não modificam os dados originais, o notebook de origem, a introdução ou a revisão de literatura. O texto da seção é editado manualmente; os números são macros geradas pelo script.
