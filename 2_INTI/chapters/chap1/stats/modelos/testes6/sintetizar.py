from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parent
names={'C61':'Incentivos soja/milho — amostra ampla','C62':'Incentivos — amostra territorial comum','B61':'Gradientes por predominância Amazônia/Cerrado','B62':'Gradientes com choques bioma×ano','B63':'Gradiente contínuo da fração Amazônia','I61':'Interface administrativa >1e−6','I62':'Interface administrativa >5%','I63':'Interface administrativa >10%'}
for f in ['COEFICIENTES','MODELOS']:
 d=pd.read_csv(p/(f+'.csv'));d['titulo']=d.id.str.split('_').str[0].map(names);d['transformacoes']='log preço lag1 centrado × aptidão z; interações hierárquicas conforme ESTRATEGIA; VD em pp';d['bioma_escopo']=d.id.map(lambda x:'todos' if x.startswith('C61') else 'fração Pantanal ≤1e−6; Amazônia/Cerrado')
 d.to_csv(p/(f+'.csv'),index=False)
c=pd.read_csv(p/'COEFICIENTES.csv');m=pd.read_csv(p/'MODELOS.csv');j=pd.read_csv(p/'TESTES_CONJUNTOS.csv');g=pd.read_csv(p/'MAGNITUDES.csv');a=pd.read_csv(p/'SUPORTE.csv')
def table(d):
 rows=[[format(v,'.5g') if isinstance(v,(float,int)) else str(v) for v in row] for row in d.to_numpy()]
 return '\n'.join(['| '+' | '.join(d.columns)+' |','| '+' | '.join(['---']*len(d.columns))+' |',*['| '+' | '.join(row)+' |' for row in rows]])
formal=g[g.familia.eq('contrastes_formais')];base=c[c.termo.isin(['x_soja','x_milho'])];sig=formal[formal.p_holm.lt(.05)]
text='''# Resultados — rodada 6

16 modelos executados em quatro notebooks. Todas as estimações são associações condicionais; bioma não é uma intervenção. Preço comum anual é absorvido pelas FE ano, atributos/bioma pelas FE municipais: os coeficientes identificam gradientes diferenciais. O preço em log já está defasado um ano. Uma unidade de x corresponde a uma unidade de log-preço × 1 DP de aptidão. VD em pontos percentuais da conversão por estoque nativo inicial.

Não há conversão nativa→soja/milho/algodão nos dados. Os resultados abaixo sobre soja e milho referem-se a incentivos dessas culturas associados à conversão agrícola agregada ou à pastagem, não ao destino específico da cultura. Não há variáveis de algodão nos dois schemas consultados. Área plantada não foi usada como substituta de conversão. Não se demonstra deslocamento ou mecanismo direto/indireto.

Pantanal: 4 municípios na grade, somente 3 com conversão válida e 54 linhas. Há 13 com alguma fração Pantanal, 8 acima de 5% e 7 acima de 10%; nenhuma regressão separada foi fabricada. Os modelos territoriais excluem qualquer fração Pantanal >1e−6, usando a mesma amostra e ambos os destinos observados. C61/C62 permitem examinar composição. Exclusão limita validade externa, não prova que Pantanal não importa.

Interfaces são municípios de composição mista, não ecótonos ecológicos. O JSON de referência contém somente código/nome; não foram encontrados arquivos .gpkg/.shp/.geojson na árvore ativa examinada. O painel não localiza as conversões em biomas ou faixas de transição. Frações originais preservadas: erro máximo de soma 0,001255. Não rateamos fluxos, não inferimos localização por predominância e não normalizamos frações silenciosamente.

## Inferência e multiplicidade
Principal DK Bartlett lag2, t(23) quando todos os 24 anos presentes; sensibilidades DK1, DK3, municipal e two-way bruto. Matrizes brutas não PSD não foram corrigidas; SE indefinidos são registrados. Mesmo 100+ municípios não criam mais choques anuais. IC95 pontuais, não simultâneos. Holm: coeficientes culturas8/biomas32/interfaces36; testes conjuntos16; contrastes formais52; magnitudes32 (reexpressões, não replicações). Correções destas famílias NÃO controlam integralmente busca adaptativa entre rodadas. As sensibilidades não autorizam escolher o menor p. O bootstrap da rodada5 revelou sensibilidade ao bloco e resolução discreta; não foi rebatizado como validação desta expansão.

'''
text += '## Suporte efetivo\n\n'+table(a[a.amostra.eq('sem_Pantanal')])+'\n\n'
text += '## Ajustes e perdas\n\n'+table(m[['id','N','municipios','anos','perdas_grade','condicao','ajuste']])+'\n\n'
text += '## Gradientes de referência: todos, inclusive imprecisos\n\n'+table(base[['id','termo','coef','se','ic95_inf','ic95_sup','p','p_holm']])+'\n\n'
text += '## Testes conjuntos das interações territoriais\n\n'+table(j[['id','termos','F','p','p_holm']])+'\n\n'
text += '## Comparações formais soja−milho e incrementos territoriais\n\n'+table(formal[['id','contraste','estimativa','se','ic95_inf','ic95_sup','p','p_holm']])+'\n\n'
text += f'Após Holm na família de 52 contrastes formais: {len(sig)} rejeições a 5%. Isso não equivale a aceitar os demais nulos, tampouco identifica causalidade. Os intervalos mostram a precisão disponível. Não se compara significância de duas culturas como teste da diferença.\n\n'
text += '## Magnitudes de +10% preço com aptidão P75−P25\n\n'+table(g[g.familia.eq('magnitudes_base')][['id','contraste','estimativa','ic95_inf','ic95_sup']])+'\n\n'
text += '''## Decisão científica e próximos dados

H1 não pode ser aceita/rejeitada em bloco por estes testes. Há dimensões associativas mensuráveis e dimensões não identificadas: efetividade institucional, destinação específica de culturas, algodão, causalidade e ecótono localizado. Resultados territoriais distinguem composição e sensibilidade às FE, mas não removem custos omitidos, seleção de aptidão baseada em terras2010 ou estoque endógeno. Falta de rejeição não demonstra homogeneidade/equivalência.

Encerrada esta grade finita. As rodadas2–5 já investigaram composição fiscal, dinâmica, tendências, choques bioma×ano, não linearidades, zeros, denominadores, influência e inferência temporal. Esta ampliação investiga uma questão territorial distinta; novas variantes escolhidas pelo p não resolveriam as lacunas. Para discriminar os mecanismos restantes são necessários mapas de transições por cultura/ano, geometrias e definição externa de faixa ecotonal, incentivos/aptidão de algodão, mais suporte Pantanal e medida/desenho institucional exógeno. Preservadas as conclusões das rodadas anteriores. Publicação permanece pendente.
'''
(p/'RESULTADOS.md').write_text(text)
(p/'SINTESE.md').write_text('# Síntese de revisão\n\nLeia RESULTADOS.md para todos os resultados, inclusive nulos e contrastes formais; ESTRATEGIA.md para decisões anteriores às estimações.\n\n16 ajustes associativos, 4 notebooks. Não se estimou conversão por cultura, algodão nem ecótono ecológico por ausência de mensuração apropriada. Pantanal apenas descritivo por suporte restrito. Rodadas2–5 preservadas; novas rodadas locais, sem publicação.\n')

# Sensibilidades dos testes conjuntos, calculadas com matrizes brutas completas.
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
rows=[]
for _,z in j.iterrows():
 terms=z.termos.split(';');co=c[c.id.eq(z.id)].set_index('termo').loc[terms].coef.to_numpy();mm=m[m.id.eq(z.id)].iloc[0]
 for name in ['DK1','DK2','DK3','municipio','two_way_bruto']:
  v=pd.read_csv(p/f'cov_{z.id}_{name}.csv',index_col=0).loc[terms,terms].to_numpy();eig=np.linalg.eigvalsh(v);ok=eig.min()>0;df=mm.municipios-1 if name=='municipio' else mm.anos-1
  f=float(co@np.linalg.solve(v,co)/len(terms)) if ok else np.nan
  rows.append(dict(id=z.id,covariancia=name,F=f,p=stats.f.sf(f,len(terms),df),df1=len(terms),df2=df,min_eigen=eig.min(),status='estimado' if ok else 'matriz não positiva'))
sens=pd.DataFrame(rows);sens['p_holm']=np.nan
for cov,a in sens.groupby('covariancia'):
 ix=a[a.p.notna()].index;sens.loc[ix,'p_holm']=multipletests(sens.loc[ix,'p'],method='holm')[1]
sens.to_csv(p/'CONJUNTOS_SENSIBILIDADE.csv',index=False)
with (p/'RESULTADOS.md').open('a') as f:
 f.write('''\n## Leitura substantiva dos resultados e continuidade\n\nPreços log soja/milho correlacionam 0,9476; aptidões 0,5907. A inclusão conjunta tem posto completo, mas não torna os incentivos economicamente independentes. C61 ampla: diferença dos gradientes soja−milho na agricultura 0,1103 (IC95 −0,0199 a 0,2405); pastagem 0,2058 (−0,1741 a 0,5856), ambas imprecisas.\n\nNo grupo base Cerrado da amostra sem Pantanal, a diferença soja−milho para pastagem é −0,5296 em B61 (IC95 −0,8133 a −0,2459; Holm52 0,0404), −0,5321 em B62 (Holm52 0,0437) e −0,6035 em B63 no extremo fração Amazônia=0 (Holm52 0,0040). Trata-se de comparação de gradientes padronizados, não de conversão específica por cultura. Os testes conjuntos de diferenças Amazônia–Cerrado são imprecisos (Holm16 ≥0,524); isso não estabelece homogeneidade.\n\nInterfaces/pastagem: testes conjuntos das duas interações rejeitam com DK2 nas três definições (Holm16 0,0000074; 0,000274; 0,000283). Para I61, incremento soja=0,3068 (IC95 −0,6641 a 1,2777), milho=−0,8548 (−1,3889 a −0,3207). A covariância entre os termos importa: forte teste conjunto não significa ambos individualmente precisos. Com cluster municipal, Holm16=0,108/0,148/0,065; two-way bruto=0,096/0,217/0,178. Portanto não é evidência robusta à inferência. CONJUNTOS_SENSIBILIDADE.csv contém todos, inclusive matrizes inadequadas; não houve PSD.\n\nPróxima rodada7 motivada por este diagnóstico: verificar interfaces com FE bioma×ano e tendências municipais, com grade fixada antes dos novos resultados. É exploração adaptativa explícita, não procura de p baixo nem confirmação independente. Sem nova mensuração, não identifica ecótono ecológico ou causalidade.\n''')
