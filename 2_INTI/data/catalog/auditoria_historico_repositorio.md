# Auditoria do histórico e dos arquivos originais

## Escopo e resultado

- Branch: `main`; HEAD original: `e5c8ece0c4516a79e2cef0b293ae2ce13f1259ce`.
- 210 arquivos originais com SHA-256 preservado em `baseline_repositorio_sha256.csv`.
- 117 commits alcançáveis em todos os refs locais; origem do histórico: fevereiro de 2025.
- 279 blobs históricos de texto, código, DOCX e ZIP examinados pelo conteúdo, incluindo 28 versões de ZIP e 8 versões de notebooks.
- 28 ZIPs atuais e 363 membros inventariados e lidos; nenhum dataset ou pipeline H1/H2 dentro desses arquivos.
- Duas árvores sem referência de commit examinadas por `git fsck --full --no-reflogs`; contêm versões do mesmo projeto documental, sem dados municipais adicionais.
- Não foi identificado pipeline removido de MapBiomas, CHIRPS, ERA5, PAM/PPM, RAMMT, GAEZ ou harmonização municipal nos objetos locais examinados.
- Nenhum checkout, merge, recuperação destrutiva, download ou modificação de arquivo original foi feito por esta auditoria.

## Evidências aproveitáveis

`2_INTI/chapters/chap1/0_introduction.tex` contém as definições e fontes candidatas de H1/H2. As menções identificadas são documentação metodológica, sem aquisição ou processamento implementado. Preservar integralmente esse texto como referência conceitual.

`1_SUYANA/chapters/qualificacao/qualificacao_fernando.tex` menciona MapBiomas. A imagem `assets/mapa_biomas_mt.png` é uma ilustração; não contém geometrias ou crosswalk que permitam recuperar classificação territorial validada.

Os seis notebooks atuais tratam de emissões globais, gráficos conceituais, simulações e uma comparação de modelos. Nenhum contém chamadas às fontes H1/H2 procuradas. Devem ser preservados, mas não reaproveitados como pipeline empírico municipal. O notebook de emissões usa `pd.read_excel('carbon_emissions.xlsx')`, caminho relativo que não aponta para a pasta `data` quando executado a partir de `code`.

## Única planilha de dados original

`1_SUYANA/data/carbon_emissions.xlsx`: uma aba, 86 observações anuais, 1940–2025, colunas `Characteristic` e `Emissions in billion metric tons`. Não há anos duplicados nem células vazias nos registros. Valor mínimo 4,85 e máximo 38,11 bilhões de toneladas métricas. O ano 2025 contém marcador de nota; sua condição observada/projetada não está documentada na planilha. A fonte original não foi autenticada pelo arquivo. Preservar como dado contextual; não integrar ao painel H1/H2.

## História relevante

- `c73c0fe` (2025-12-11): entrada da planilha e do gráfico de emissões.
- `0c1ab8d` (2026-09-04): separação SUYANA/INTI.
- `b0617bc` (2026-09-21): reorganização de seções e remoção de dois arquivos LaTeX; não removeu dados empíricos.
- `4ee8080` (2026-09-25): reconstrução de H1 no texto.
- `bf2d9cf` (2026-09-26): ajustes após reunião e detalhamento de H1/H2.

## Limites e recuperação

A auditoria cobre o repositório local, seus refs, objetos históricos e ZIPs, inclusive arquivos ocultos no inventário inicial. Ela não confirma a inexistência de trabalho em outros computadores, contas, pastas externas ou branches remotos ainda não conhecidos localmente. Não há componente empírico identificado que exija restauração a partir do histórico. Se surgir um caminho/commit externo adicional, a recuperação deverá ser aditiva e precedida de validação, sem substituir o conteúdo de `main`.

Os resultados detalhados, inclusive código-fonte dos notebooks, listas de blobs, refs, arquivos removidos e planilha, estão em `auditoria_historico_git.json`. Para verificar preservação dos originais, executar novamente `python 2_INTI/code/audit_repository.py`; o script recusa substituir o baseline quando seus hashes mudam.
