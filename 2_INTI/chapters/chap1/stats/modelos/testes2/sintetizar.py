from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parent
c=pd.read_csv(p/'COEFICIENTES.csv');m=pd.read_csv(p/'MODELOS.csv');j=pd.read_csv(p/'TESTES_CONJUNTOS.csv');g=pd.read_csv(p/'MAGNITUDES.csv')
def table(d):
 return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in d.round(6).itertuples(index=False,name=None))+'\n'
text='''# Resultados — rodada 2

19 ajustes concluídos. Amostra ampla: 2772 pares/137 municípios; fiscal: 1140/128. Para harmonização não linear, três municípios com uma única observação foram excluídos explicitamente: 2769 pares/134 municípios. Nenhum município tinha soma zero agrícola na amostra; todas as exclusões estão registradas. Modelos G00 na amostra harmonizada foram previstos condicionalmente e executados.

O núcleo amplo detecta associação positiva soja×aptidão na conversão para pastagem (0,1038 pp, IC95 [0,0385;0,1691], Holm 0,0128). Agricultura é imprecisa (0,0288 pp, IC inclui zero), não evidência de equivalência a zero. O teste direto da diferença pastagem−agricultura detecta diferenças positivas nas duas exposições sob a inferência principal; não compara significâncias separadas. Essa é evidência associativa sobre o destino imediato da conversão, não prova de que demanda por soja desloca pastagem: essa transição não é medida.

A restrição à amostra fiscal muda o coeficiente soja agrícola de 0,0288 para 0,0074 antes da inclusão de autos. Logo, parte da diferença da rodada1 decorre de composição observável; isso não identifica a causa da seleção. Adicionar autos na mesma amostra altera pouco esse coeficiente. Autuações não identificam efetividade institucional. Sob DK2, os IC dos autos e da interação preço×autos incluem zero; não se pode concluir inexistência do condicionamento institucional.

PPML com/sem offset e fracional com FE municipal/ano produzem objetos diferentes. Os coeficientes e testes conjuntos variam: isso é sensibilidade de escala/forma funcional, não uma votação entre modelos. Os testes individuais das alternativas não passam Holm da família de sensibilidades. Alguns testes conjuntos passam a correção; isso não valida exogeneidade. FE não linear com T curto continua sujeito a viés incidental, apesar de convergência, scores e predições finitas. O offset usa estoque endógeno e impõe sua elasticidade unitária.

A interpretação relevante seguinte é temporal: tendências de abertura de fronteira ou períodos específicos podem covariar com a aptidão. A rodada3 foi motivada por essa explicação alternativa e pela referência terras2010 do GAEZ, não pela busca de p menor. Não há limiar substantivo para teste de equivalência; intervalos amplos significam imprecisão. Todas as famílias e testes constam do protocolo anterior à execução.

## Todos os coeficientes substantivos

'''+table(c[['id','termo','coef','se','ic95_inf','ic95_sup','p','p_holm','n_familia','N']])+'''\n## Testes conjuntos\n\n'''+table(j[['id','termos','F','p','p_holm']])+'''\n## Magnitudes predefinidas\n\nCenários de +10% do preço médio, não margens de equivalência. No linear: contraste P75−P25 de aptidão em pp. No GLM: mudança média prevista via componente diferencial, mantendo FEano, sem identificar resposta comum ao choque.\n\n'''+table(g[['id','contraste','estimativa','ic95_inf','ic95_sup','unidade']])+'''\n## Reprodução e limitações\n\nInstalar requirements.txt em ambiente virtual externo e executar `python executar.py` neste diretório. Os notebooks são executados em kernels novos. Auditoria independente conferiu coeficientes e covariância linear DK2 contra PanelOLS. FE removidos por projeção iterativa, não double-demean simples. METADADOS.json registra protocolo, origem, hash dos dados e arquivos protegidos; VALIDACAO.json confirma preservação. Logs em ../../../../../audit/testes2 (caminho canônico na raiz: 2_INTI/audit/testes2). Não houve publicação.\n'''
(p/'RESULTADOS.md').write_text(text)

# A família de Holm não engloba automaticamente a busca sequencial.
with (p/'RESULTADOS.md').open('a') as f:
 f.write('\n## Escopo da multiplicidade e da adaptação\n\nHolm aplica-se somente às famílias registradas nesta rodada, com tamanho em n_familia nos CSVs. As rodadas foram adaptadas aos diagnósticos anteriores e reutilizam os mesmos dados: a correção por família/rodada não controla integralmente o erro da busca sequencial nem converte exploração em teste confirmatório. Uma confirmação independente exige protocolo externo/prévio e dados novos ou identificação adicional.\n')
