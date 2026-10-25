# Base H1 para uso

Abra **BASE_COMPLETA_H1.csv**: 3.384 linhas (141 unidades × 2001–2024), 97 colunas. Base v4 com receitas e 27 custos incorporados mediante aprovação do autor em 25/10/2026.

Os quatro grupos repetem os mesmos sete índices: ambientais 29 colunas; econômicos 67; institucionais 12; outros 10. A união por `0_codigo_ibge` e `0_ano`, deduplicando os índices, recompõe a base completa. Consulte DICIONARIO.csv para as 97 variáveis.

Custos são aproximações regionais ou estaduais publicadas compatíveis, não observações municipais independentes. As 27 colunas são alternativas por fonte/conceito/sistema/moeda. Agricultura mantém R$/ha e USD2024/ha separados; pecuária mantém R$/arroba vendida nominal. Ausência permanece vazia, não zero; não houve interpolação. Uma praça significa suporte fraco. Uso econométrico requer considerar informação regional compartilhada e disponibilidade temporal, sem interpretação causal automática.

[Proveniência e qualidade por chave/variável](../../modelos/base_custos_investigacao/etapa_regional_v2/resultados/METADADOS_CUSTOS_MUNICIPAIS.csv). O campo de aprovação desse snapshot refere-se à etapa candidata anterior; a incorporação atual está autorizada. [Fonte literal dos 27 custos](../../modelos/base_custos_investigacao/etapa_regional_v2/USO_CANDIDATOS/CUSTOS_MUNICIPAIS_CANDIDATOS.csv), commit 72c3e6b531881762b821547015cb916ecc3951c9.

Histórico v4 sem custos preservado em `../../modelos/base3/BASES_PARA_USO`. Construção: `../processamento/incorporar_custos_h1.py`; separação: `../processamento/separar_grupos_h1.py`. Para reproduzir, use diretório vazio. Edições manuais coerentes da base e do respectivo grupo são preservadas; colisões diferentes nos custos interrompem a incorporação. A separação recusa sobrescrever arquivos divergentes. Guarde suas edições antes de executar rotinas.
