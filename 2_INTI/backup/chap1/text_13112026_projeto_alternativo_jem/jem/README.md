# Versão JEM em português

Os documentos desta pasta são cópias editoriais do artigo 1 para revisão do autor. O working paper em `../text/`, os dados, os modelos e suas saídas foram preservados.

- `manuscript_JEM.pdf` e `manuscript_JEM.tex`: manuscrito principal, com quatro tabelas e três figuras.
- `supplementary_material_JEM.pdf` e `supplementary_material_JEM.tex`: suplemento, com Textos S1–S5, Tabelas S1–S17 e Figuras S1–S6.
- `assets/`, `tables/`, `preamble.tex` e os arquivos `.bib` são dependências dos dois fontes. As tabelas e imagens reproduzem os arquivos existentes sem alteração de conteúdo.

Mantenha os PDFs juntos para utilizar seus links cruzados. A compilação auditada fica em `2_INTI/audit/jem_20261112/producao/compilacao/`: o script `verificar_e_compilar.py`, no diretório acima, copia os fontes para esse destino e executa LaTeX/BibTeX nas duas ordens necessárias às referências entre documentos. Os auxiliares não são gravados no working paper original. Após a primeira compilação, os dois PDFs podem ser recompilados com `latexmk -pdf` na mesma pasta de trabalho, alternando suplemento, principal e suplemento até resolver todas as referências.

A redação e a apresentação bibliográfica atuais são destinadas à revisão em português. Tradução, adequação formal definitiva e itens administrativos da submissão ao JEM permanecem para a etapa seguinte. O log editorial e a contagem estão em `2_INTI/audit/works/chap1/jem_20261112/RELATORIO_REESTRUTURACAO_PT.md`.
