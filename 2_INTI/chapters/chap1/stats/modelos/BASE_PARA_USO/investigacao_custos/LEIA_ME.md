# Arquivos para uso

- **CUSTOS_AGRICULTURA.csv**: 247 referências, CONAB e IMEA separadas pelo campo fonte e por colunas de conceitos; custos por hectare.
- **CUSTOS_PECUARIA.csv**: 124 referências IMEA, cria/recria-engorda/ciclo completo; custos por arroba vendida. Não converter para hectare com estoque de rebanho.
- **DICIONARIO.csv**: definição das colunas e conceitos.

Uma linha por referência publicada, com chave `0_id_referencia`; COE/COT/CT e A–J são colunas, não observações independentes. Os dois identificadores de uma duplicata agrícola estão em `0_ids_origem`. Períodos sem custo permanecem: 17 referências agrícolas e 31 pecuárias têm todos os custos ausentes. Não conte essas linhas como observações monetárias.

Recorte: safras agrícolas inteiras entre 2001 e 2024; pecuária pelo ano literal. Não confundir safra com data-base/ano de colheita. Os períodos posteriores estão apenas em ../resultados. Consolidados/estimativas não são gastos municipais realizados.

Use cada `2_*_nominal` com sua flag `4_*_elegivel_nominal`. Uma divergência válida só exclui quando `abs(componentes − oficial)/abs(oficial) > 0,10`. Exatamente 10% permanece. Oficial zero com componentes positivos é incompatível, sem percentual finito inventado. Valores oficiais não foram corrigidos. Ambiguidade e comparações indisponíveis ficam em flags; elegibilidade não significa conferência integral.

Colunas CONAB A–J não equivalem automaticamente a COE/COT/CT IMEA. Não some agregados e componentes. USD2024 consta apenas onde data/câmbio/CPI estavam disponíveis e validados; nunca preencha vazios com zero. IMEA preserva valores e unidade declarados, sem presumir data de precificação dos consolidados. Na agricultura, colunas não aplicáveis à fonte também ficam vazias. Regiões não validam limites territoriais, representatividade municipal ou bioma. Modelos antigos usam outra amostra e não autorizam previsões para esta base.
