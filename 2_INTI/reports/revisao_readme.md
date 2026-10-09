# Revisão do README

Data: 9 de outubro de 2026.

## Escopo e alterações

Revisão editorial de `README.md`, com base na versão local e no texto anexado pelo autor. Foram preservadas as alterações locais preexistentes, inclusive o título e a organização da apresentação.

- Corrigido o nome do doutorando para Fernando Souza de Vieira, conforme `AGENTS.md` e `STYLE_GUIDE.md`.
- Ajustada a redação sobre a definição posterior do Artigo 3. Removido o ordinal ambíguo de “segundo desenvolvimento teórico”, mantendo as alternativas apresentadas pelo autor.
- Atualizada a tabela de diretórios: dados em `2_INTI/xdata/`, distinção entre `reports/`, `xreports/` e `thread/` e identificação de `1_SUYANA/` como material histórico.
- Alinhada a descrição do backup ao mecanismo definido em `RESEARCH_PROTOCOL.md` (Restic), sem auditoria de sua execução.
- Corrigidos os caminhos dos documentos operacionais e acrescentados links relativos.

## Validação e limites

- Comparação com o anexo, normalizando apenas as quebras de linha: o trecho entre “Eixo geral da pesquisa” e “Artigo 3” permaneceu integralmente igual, incluindo hipóteses, estratégias e ressalvas metodológicas.
- Todos os caminhos e links locais citados no README existem.
- `git diff --check -- README.md`: aprovado. O Git emitiu apenas o aviso de conversão de LF para CRLF.
- Os hashes SHA-256 da introdução de H1 e de sua cópia de backup permaneceram iguais aos registrados antes da edição.
- Não foram alterados arquivos LaTeX, bibliografias, código ou dados nesta tarefa; não foi necessária compilação.

## Estado do repositório

Branch: `main`. Esta tarefa alterou `README.md` e criou este relatório. Permanecem as alterações preexistentes em `2_INTI/chapters/chap1/0_introduction.tex` e o arquivo não rastreado `2_INTI/backup/chap1/0_introduction_09101981.tex`, ambos preservados. Nenhum commit, merge ou push foi realizado.
