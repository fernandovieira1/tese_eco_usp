from pathlib import Path
import sys
p=Path(__file__).resolve().parent;sys.path.insert(0,str(p.parent/'testes2'))
from metodos import *
c=pd.read_csv(p/'COEFICIENTES.csv');m=pd.read_csv(p/'MODELOS.csv');g=pd.read_csv(p/'MAGNITUDES.csv');j=pd.read_csv(p/'TESTES_CONJUNTOS.csv')
def table(d):return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in d.round(6).itertuples(index=False,name=None))+'\n'
rows=[]
for ident in ['B02_agricultura','B02_pastagem','D02_diferenca']:
 sub=c[c.id.eq(ident)].set_index('termo');mm=m[m.id.eq(ident)].iloc[0]
 for metodo in ['DK1','DK2','DK3','municipio','two_way_bruto']:
  cv=pd.read_csv(p/f'cov_{ident}_{metodo}.csv',index_col=0)
  for cultura in ['soja','milho']:
   names=[f'expo_{cultura}_l{l}' for l in [1,2,3]];value=sub.loc[names,'coef'].sum();var=cv.loc[names,names].to_numpy().sum();se=np.sqrt(var) if var>=0 else np.nan;df=mm.municipios-1 if metodo=='municipio' else mm.anos-1;crit=stats.t.ppf(.975,df)
   rows.append(dict(id=ident,cultura=cultura,covariancia=metodo,soma=value,se=se,ic95_inf=value-crit*se,ic95_sup=value+crit*se,p=2*stats.t.sf(abs(value/se),df)))
s=pd.DataFrame(rows)
s['p_holm']=np.nan
for name,ix in s.groupby('covariancia').groups.items():s.loc[ix,'p_holm']=multipletests(s.loc[ix,'p'],method='holm')[1]
s.to_csv(p/'SENSIBILIDADE_CUMULATIVOS.csv',index=False)
text='''# Resultados — rodada 3

15 ajustes executados. A soma de lags1–3 da exposição soja×aptidão para pastagem é positiva: 0,1627 pp, IC95 [0,1170;0,2085], p Holm≈0,000002 na família de seis somas. A diferença acumulada entre pastagem e agricultura também é positiva. Agricultura permanece imprecisa; não é equivalência a zero. A soma representa mudança persistente na escala padronizada, não efeito causal de uma inovação exógena.

O coeficiente estático soja/pastagem permanece positivo com tendências municipais (0,0864 pp), mas cai para 0,0178 pp com FE bioma×ano (IC95 [−0,0530;0,0885]). O coeficiente milho/pastagem aumenta nesse controle. Isso mostra que o desenho não separa de modo estável os componentes comuns de bioma da exposição aos produtos; não prova que políticas ou choques de bioma sejam a causa. FE bioma×ano retém cerca de 67% e 61% da variância residual das exposições soja/milho; portanto a mudança não pode ser descrita apenas como absorção total de identificação.

A janela 2011–2024 contém somente 14 anos; os IC do núcleo incluem zero. GAEZ terras2010 não se torna exógeno por esse recorte. As primeiras diferenças não reproduzem com precisão o padrão de níveis; são outro estimando e não refutam automaticamente uma resposta lenta. Os contrastes por atividade foram conferidos numericamente como diferença entre coeficientes das equações separadas na mesma amostra.

O resultado dinâmico ainda precisa ser confrontado com FE bioma×ano e tendências, além de influência de observações e suporte. Essa motivação define a rodada4, e não a busca de novos resultados significativos. Falta de precisão e instabilidade não permitem aceitar H1 nem sua negação de maneira causal.

## Coeficientes integrais

'''+table(c[['id','termo','coef','ic95_inf','ic95_sup','p','p_holm','N','anos']])+'''\n## Testes conjuntos\n\n'''+table(j[['id','F','p','p_holm']])+'''\n## Contrastes acumulados e reexpressões econômicas\n\nA magnitude em 10% do preço é reexpressão da soma, não teste independente adicional.\n\n'''+table(g[['id','contraste','estimativa','ic95_inf','ic95_sup','p','p_holm','unidade']])+'''\n## Sensibilidade das somas\n\n'''+table(s)+'''\n## Reprodução\n\nCom dependências instaladas em ambiente externo: `python reproduzir.py`. Reutiliza utilitários auditáveis de testes2 sem alterar a rodada1. ESTRATEGIA.md foi gravada antes da execução; hashes e logs em METADADOS.json/EXECUCAO.json/VALIDACAO.json e 2_INTI/audit/testes3. Sem commit/push/publicação.\n'''
(p/'RESULTADOS.md').write_text(text)

# A família de Holm não engloba automaticamente a busca sequencial.
with (p/'RESULTADOS.md').open('a') as f:
 f.write('\n## Escopo da multiplicidade e da adaptação\n\nHolm aplica-se somente às famílias registradas nesta rodada, com tamanho em n_familia nos CSVs. As rodadas foram adaptadas aos diagnósticos anteriores e reutilizam os mesmos dados: a correção por família/rodada não controla integralmente o erro da busca sequencial nem converte exploração em teste confirmatório. Uma confirmação independente exige protocolo externo/prévio e dados novos ou identificação adicional.\n')
