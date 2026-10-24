# H1 — base para trabalho manual

**Use esta pasta: base3 v4, com receitas estimadas e sem custos.** Há um único conjunto ativo; versões anteriores ficam fora daqui.

| Arquivo | Conteúdo | Linhas × colunas |
|---|---|---:|
| BASE_COMPLETA_H1.csv | Todos os grupos | 3.384 × 70 |
| GRUPO_1_AMBIENTAIS.csv | Índices + ambientais | 3.384 × 29 |
| GRUPO_2_ECONOMICOS.csv | Índices + econômicos, incluindo receitas | 3.384 × 40 |
| GRUPO_3_INSTITUCIONAIS.csv | Índices + institucionais | 3.384 × 12 |
| GRUPO_4_OUTROS.csv | Índices + outros | 3.384 × 10 |
| DICIONARIO.csv | Definição das 70 variáveis | — |

Os sete campos `0_` são idênticos em cada grupo, na mesma ordem de linhas. Chave única: `0_codigo_ibge` + `0_ano`; 141 unidades, 2001–2024. Nomes, valores, zeros e ausências foram preservados. CSV UTF-8, vírgula e decimal ponto; vazio significa ausência. Siga os tipos e unidades do dicionário ao importar. Para reunir os grupos, junte pela chave verificando unicidade; não empilhe linhas.

Fonte: base3 v4 publicada no commit `668b099becfe82ec7fc341ec6b9dc391146a57a5`, preservada em `../../modelos/base3/BASES_PARA_USO`. Base completa SHA256 `a98dbe320efc784543cf43372a5903de32434be5871304178f2f9d49daaf1c3b`; dicionário SHA256 `8e8a22d3d75742aaa355cfacbbe4d0eb1d16bc14c77fd4459d4db1daa620c4e5`.

Salve suas edições em cópias de trabalho. O gerador em `../processamento/separar_grupos_h1.py` recusa sobrescrever conteúdo divergente. A separação não estima modelos nem muda os limites científicos da v4; receitas estimadas não são lucro ou custos.
