# Complemento CONAB da base2 — entrega local

Os três extratos foram obtidos integralmente pelo conector Drive. Os tamanhos em bytes conferem com os metadados do download bruto; hashes, IDs e URLs estão em FONTES_DRIVE.json. O download HTTP direto teve erro de proxy 403; a transferência pelo texto integral do próprio conector funcionou. Não há bloqueio de acesso pendente.

## Resultado e alcance

Foram harmonizadas 188 planilhas: 99 de soja, 17 de milho primeira safra e 72 de milho segunda safra. A tabela longa tem 6.920 valores: 3.760 monetários (dez conceitos, duas unidades, por planilha) e 3.160 participações. Todos mantêm arquivo/aba via id_serie e coordenadas da célula. Os 45.360 registros de células das fontes permanecem intactos.

O auxiliar `custos_ha_candidatos.csv` tem **1.580 valores nominais em R$/ha**, correspondentes a **158 observações praça–tecnologia–safra**: soja 82, milho primeira 13, milho segunda 63. São candidatos para comparação descritiva dentro de 2001–2024, sujeitos a diferenças tecnológicas, calendário, seleção de praças e revisão histórica. Não são 158 municípios, amostra aleatória ou observações independentes. A soja termina na safra inicial 2023 nesse filtro: safras 2024/25 são retidas no arquivo integral, mas ficam fora do critério conservador de safra inteiramente dentro do período. Esse critério não define o alinhamento econômico futuro com conversão.

**Nenhuma coluna de custo foi acrescentada ao painel municipal.** A incorporação à base2 é relacional, por tabela auxiliar: não há regra espacial validada para transformar custos modais de quatro praças em custo observado de 141 municípios. Nem proximidade, bioma, média tecnológica ou interpolação foram inventados. O painel publicado continua com 3.384 linhas, 108 colunas, incluindo as 70 originais preservadas. Não foi criada uma falsa versão municipal de custos, receita ou lucro.

## Decisões e qualidade

- Dez agregados distintos: custeio; outras despesas/pós-colheita; despesas financeiras; custo variável; depreciações; outros fixos; custo fixo; operacional; renda de fatores; total. A variante de rótulo do bloco B permanece no texto original. Não tratar qualquer deles como sinônimo de margem ou lucro.
- As 1.504 identidades contábeis testadas (quatro por unidade e planilha) passaram na tolerância R$0,05. Não é prova de que os dados econômicos estão corretos: valores extraídos de fórmulas também podem fechar internamente.
- Das 1.880 comparações R$/60kg versus R$/ha×60/produtividade, **227 falham**, distribuídas em 73 planilhas, com tolerância R$0,02. Parte pode refletir somas arredondadas; não assumimos que todas sejam arredondamento. O maior desvio é aproximadamente R$1,04, soja OGM Sorriso 2007. Não substituir valores. O auxiliar candidato usa a unidade original R$/ha e não depende da conversão por saca; falhas permanecem consultáveis em validacoes.csv.
- Participações: 3.160 verificações, **12 não aprovadas**. Dez são a coluna genérica de milho segunda, Sorriso 2020: o total é 0,9784, e não 1 ou 100; não foi normalizada. As outras duas divergem da razão de custos além de 0,001. Escala inferida não comprova denominador; participações genéricas são explicitamente marcadas como CT inferido, e os testes confrontam essa interpretação.
- Cinco planilhas de soja, Campo Novo 2006–2010, identificam praça conjunta Sapezal/Campo Novo. Milho segunda, aba Sorriso 2014, identifica Primavera do Leste no cabeçalho. As seis ficam fora do auxiliar candidato, sem correção territorial presumida.
- Duas abas Primavera 1998 (soja e milho primeira) têm data-base em abril de 1999. Datas originais prevalecem; divergência fica sinalizada. 24 planilhas ficam fora do período conservador. Não há metadado de safra/data/produtividade faltante após tratar formatos documentados, inclusive data pontuada e produtividade média explícita junto de faixa.
- Milho primeira contém somente Primavera 1997–2013. Nota na planilha 2013, célula linha12/coluna21, informa mudança do pacote modal para milho segunda a partir de 2014. Não preencher esses anos como primeira safra. Milho segunda começa em 1997 apesar do nome indicar 2005; Primavera não tem 2011–2012 nesse arquivo.
- Tecnologia: 99 planilhas indicam OGM, três explicitam convencional e 86 não declaram essa distinção. Sistema de plantio e intensidade tecnológica são preservados no cabeçalho; não se transformam em custos monetários por suposição.
- Os agregados extraídos não têm valores ausentes, negativos ou zero. Isso **não se aplica às células de itens**, que contêm zeros; todas permanecem nos extratos. Zero registrado não foi convertido em missing, nem missing em zero. Ausência de praça/ano/tecnologia é falta de cobertura, não custo zero. Não há evidência suficiente para atribuir zeros de origem a ausência econômica ou preenchimento anterior.

## Uso econômico futuro

Valores são nominais e referidos à data-base. Não houve deflação: falta uma escolha de deflator e alinhamento documentados para esta integração. Não combinar diretamente esses reais nominais com preços em USD2024 já defasados. Produtividade modal CONAB, rendimento observado PAM e potencial GAEZ são objetos distintos. OGM/convencional, milho primeira/segunda e safra/data-base devem permanecer separados.

A indicação Ex-Ant é um atributo do relatório; não demonstra a data de divulgação ou que a versão histórica estava disponível na decisão de conversão. Antes de regressões, verificar vintage, defasagem, frequência de atualização tecnológica, representatividade da praça e unidade comparável de produto. Não foi calculada margem: faltam preços de venda comparáveis e escolhas explícitas de conceito de custo. Algodão não está nestes três arquivos. Sem novas regressões, imputações, coleta adicional de dados, commit ou push.

A [Norma CONAB 30.302](https://www.gov.br/conab/pt-br/acesso-a-informacao/institucional/atos-normativos/normas-da-organizacao/operacoes/30-302_norma_metodologia_de_custo_de_producao.pdf/@@download/file) descreve levantamentos técnicos que caracterizam a unidade produtiva modal regional. Esse fundamento impede interpretar automaticamente custos de praça como medidas individuais municipais.

## Arquivos e reprodução

Execute, a partir de qualquer diretório:

```bash
python /workspace/tese_eco_usp/2_INTI/chapters/chap1/stats/modelos/base2/complemento_conab/testar.py
```

Somente Python 3.12 e biblioteca padrão; sem instalação, download ou semente aleatória. O teste executa harmonizar.py duas vezes, compara hashes dos CSVs gerados, confere unicidade e proveniência célula a célula, igualdade das 70 colunas originais e preservação dos arquivos rastreados. O teste final de Git pressupõe checkout sem modificações rastreadas preexistentes, como nesta entrega; alterações futuras legítimas precisam ser avaliadas separadamente. TESTES.json registra commit, hashes e resultados. Reexecução sobrescreve apenas produtos deste complemento, nunca fontes ou painel publicado.

- PLANO_HARMONIZACAO.md: decisões anteriores à extração; ajustes de parser somente para formatos reais, sem alterar números.
- harmonizar.py / testar.py: construção e testes.
- fontes/ e FONTES_DRIVE.json: entrada intacta e rastreabilidade.
- metadados_series.csv / proveniencia_cabecalhos.csv: safra, data-base com precisão, produtividade, praça, tecnologia e evidência.
- custos_agregados_longos.csv: todos os agregados, inclusive casos problemáticos e anos fora do período.
- custos_ha_candidatos.csv: subconjunto nominal em ha, não painel municipal.
- validacoes.csv / validacoes_participacoes.csv: resultados integrais, inclusive falhas da fonte.
- cobertura.csv / cobertura_praca_ano.csv / missing_zeros.csv: suporte e qualidade; não inventam combinações ausentes.
- DICIONARIO.md / RESUMO.json / TESTES.json: definições, contagens e evidência de execução.

A documentação antiga da base2, que registrava custos ainda ausentes, permanece intacta como histórico da versão publicada. Este complemento supersede apenas essa pendência de disponibilidade: os custos agora estão harmonizados como auxiliares, não validados para regressão municipal.

## Revisão de qualidade: candidatos versus subconjunto estrito

Os 158 candidatos e seus 1.580 valores foram integralmente preservados. Cada linha agora traz flags explícitas de identidades, unidades, participações, território e verificação faltante, mais contagens de falhas, aprovação estrita e motivos de exclusão. A tabela candidata **não é integralmente validada**. Ela inclui 222 discrepâncias de unidade em 70 planilhas e todas as 12 falhas de participação em três planilhas, com sobreposição entre motivos.

`custos_ha_estritos.csv` contém **870 valores, dez conceitos em 87 observações**: soja 34, milho primeira nove e milho segunda 44. Além dos filtros candidatos, exige as oito identidades contábeis, dez verificações entre unidades e todas as dez ou vinte participações aplicáveis aprovadas, sem verificação faltante. Teste ausente/escala não identificada nunca conta como aprovação. Das 158 candidatas, 71 não passam; motivos não são mutuamente exclusivos. As contagens marginais por cultura, praça, tecnologia e início da safra estão em contagens_filtros.csv; qualidade_por_serie.csv fornece a combinação completa por safra e motivos para todas as 188 planilhas. Não houve flexibilização das tolerâncias.

A aprovação estrita é **consistência interna nos testes executados**, não validação econômica, territorial municipal ou de disponibilidade histórica. Pode selecionar tecnologias e períodos mais bem registrados; não usar como amostra representativa sem avaliar seleção. Seguem os limites de preços nominais, custo modal, vintage desconhecido e calendário. Safras e datas-base estritas permanecem dentro de 2001–2024; lacunas não foram preenchidas.

### Investigação das discrepâncias

`auditar_discrepancias.py` reconstrói 1.880 comparações com aritmética Decimal diretamente dos extratos, sem importar o parser. Confere as 188 produtividades declaradas e os cabeçalhos R$/ha e R$/60kg das colunas utilizadas. Todas as células monetárias coincidem com as fontes; as 227 falhas se reproduzem. Não foi detectada troca de unidade, coluna ou produtividade no parser. Isto não audita a extração original XLS→CSV, pois os XLS não foram obtidos nesta tarefa.

Um diagnóstico adicional considera um envelope amplo de arredondamento: 0,005×(1+60/produtividade)×número de itens numerados anteriores ao agregado. É uma referência exploratória deliberadamente permissiva para soma de arredondamentos ao centavo, não reconstrução das fórmulas Excel nem novo critério de aceitação. Das 227 falhas, 221 ficam dentro desse envelope: **compatibilidade não comprova arredondamento**. Seis ultrapassam até esse envelope: custeio de soja Primavera 2010 (com e sem indicação OGM), e custeio/variável/operacional/total de soja OGM Sorriso 2007. Casos dentro do envelope continuam excluídos do estrito quando falham na tolerância original.

Na aba OGM-Sorriso-MT-2007, linha12, coluna2, aluguel de máquinas/serviços é 0 R$/ha, enquanto coluna3 é 1 R$/60kg. A produtividade explícita é 3.000 kg/ha (linha5/coluna2). Essa incompatibilidade existe no extrato, não resulta de divisão inadequada do parser, e ajuda a localizar o desvio propagado aos totais. Não sabemos qual célula deve ser corrigida; nenhuma foi alterada. As demais discrepâncias exigem confrontar fórmulas/planilhas originais antes de atribuir causa definitiva.

Participações: milho segunda Sorriso 2020 tem total genérico 0,9784115656, cuja escala permanece não identificada (dez verificações faltantes/não aprovadas). As outras duas falhas são participação CV do custeio em soja Sorriso 2011 e participação CT de depreciações em soja OGM Sorriso 2012, desvios próximos de um ponto percentual frente às razões monetárias. Fonte numérica preservada; nenhum percentual foi recalibrado.

A reprodução agora também executa a auditoria independente, confere flags e composição estrita e exige que o hash da tabela longa integral permaneça igual ao da entrega anterior. Os testes adicionais não executam regressões.
