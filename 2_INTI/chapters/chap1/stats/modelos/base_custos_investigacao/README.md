# Custos: avaliação ampliada e candidatas regionais

O ponto de entrada atual é **[USO_CANDIDATOS](etapa_regional_v2/USO_CANDIDATOS/LEIA_ME.md)**: CUSTOS_MUNICIPAIS_CANDIDATOS.csv, dicionário e instruções. O dataframe usa referências regionais e, na ausência, estaduais publicadas compatíveis. A base principal H1 não foi alterada; incorporação depende de aprovação explícita.

[Resultados e limites](etapa_regional_v2/README.md): avaliação refeita com a seleção ampliada, referências por fonte/atividade/sistema/período e atribuições regionais somente onde há suporte. Pecuária permanece R$/arroba vendida. Replicar referências não cria observações municipais independentes.

A seleção mantém valores oficiais e exclui um conceito apenas com divergência estritamente acima de10% em comparação válida, ou incompatibilidade qualitativa demonstrada que o comprometa. Ambiguidade contábil e diferenças até10% permanecem flags. Conflitos de localização impedem atribuição regional, sem apagar o custo de origem.

- [Etapa atual e reprodução](etapa_regional_v2/README.md).
- [Builder da seleção revisada](processamento): preservado; os extratos usados estão congelados na etapa atual. A pasta BASE_PARA_USO removida pelo usuário não foi restaurada.
- [Auditoria da revisão](auditoria) e [universo completo de fontes/períodos](resultados).
- [Histórico v1](historico/v1_publicada): fontes e avaliações estritas anteriores intactas. Os modelos antigos continuam condicionais àquela seleção; a reavaliação atual está separada.

Não execute builders antigos sobre diretórios de trabalho manual. Para a etapa atual, use sempre `python etapa_regional_v2/executar.py --out /diretorio/novo`.
