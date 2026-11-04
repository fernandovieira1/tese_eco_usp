from pathlib import Path
import numpy as np,pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
p=Path(__file__).resolve().parent
for file in ['COEFICIENTES','MODELOS']:
 d=pd.read_csv(p/(file+'.csv'));d['titulo']=d.id.map(lambda x:'Interface '+{'1':'>1e−6','2':'>5%','3':'>10%'}[x[2]]+(' com choques bioma×ano' if x.startswith('G') else ' com tendências municipais'));d['transformacoes']='log preço lag1 centrado × aptidão z; interações x×misto e logpreço×misto; VD pp';d['bioma_escopo']='fração Pantanal ≤1e−6; amostra comum';d.to_csv(p/(file+'.csv'),index=False)
c=pd.read_csv(p/'COEFICIENTES.csv');m=pd.read_csv(p/'MODELOS.csv');j=pd.read_csv(p/'TESTES_CONJUNTOS.csv');g=pd.read_csv(p/'MAGNITUDES.csv');base=pd.read_csv(p.parent/'testes6/COEFICIENTES.csv');rows=[]
for _,z in j.iterrows():
 terms=z.termos.split(';');co=c[c.id.eq(z.id)].set_index('termo').loc[terms].coef.to_numpy();mm=m[m.id.eq(z.id)].iloc[0]
 for name in ['DK1','DK2','DK3','municipio','two_way_bruto']:
  v=pd.read_csv(p/f'cov_{z.id}_{name}.csv',index_col=0).loc[terms,terms].to_numpy();eig=np.linalg.eigvalsh(v);ok=eig.min()>0;df=mm.municipios-1 if name=='municipio' else mm.anos-1;f=float(co@np.linalg.solve(v,co)/len(terms)) if ok else np.nan
  rows.append(dict(id=z.id,covariancia=name,F=f,p=stats.f.sf(f,len(terms),df),df1=len(terms),df2=df,min_eigen=eig.min(),status='estimado' if ok else 'matriz não positiva'))
sens=pd.DataFrame(rows);sens['p_holm']=np.nan
for name,a in sens.groupby('covariancia'):
 ix=a[a.p.notna()].index;sens.loc[ix,'p_holm']=multipletests(sens.loc[ix,'p'],method='holm')[1]
sens.to_csv(p/'CONJUNTOS_SENSIBILIDADE.csv',index=False)
v=pd.concat([pd.read_csv(f) for f in p.glob('variacao_*.csv')],ignore_index=True);v.to_csv(p/'VARIACAO_RETIDA.csv',index=False)
compare=c[c.termo.isin(['xh_soja','xh_milho'])].copy();compare['id_base']=compare.id.map(lambda x:'I6'+x[2]+x[3:]);lookup=base.set_index(['id','termo']);compare['coef_base']=[lookup.loc[(z.id_base,z.termo),'coef'] for _,z in compare.iterrows()];compare['ic95_inf_base']=[lookup.loc[(z.id_base,z.termo),'ic95_inf'] for _,z in compare.iterrows()];compare['ic95_sup_base']=[lookup.loc[(z.id_base,z.termo),'ic95_sup'] for _,z in compare.iterrows()];compare.to_csv(p/'COMPARACAO_RODADA6.csv',index=False)
def table(d):
 rows=[[format(v,'.5g') if isinstance(v,(float,int)) else str(v) for v in row] for row in d.to_numpy()]
 return '\n'.join(['| '+' | '.join(d.columns)+' |','| '+' | '.join(['---']*len(d.columns))+' |',*['| '+' | '.join(row)+' |' for row in rows]])
text='''# Rodada7 — Resultados integrais de sensibilidade das interfaces

12 modelos executados em dois notebooks; mesma amostra 2623 linhas,126 municípios,24 anos. Referências preservadas na rodada6, sem duplicar contagem. Interface mista é proxy administrativa, não localização de conversão nem ecótono ecológico. Não há estimação específica de algodão ou conversão por cultura. Modelo inclui seis termos hierárquicos; preço×misto permanece identificável com FE bioma×ano porque misto não é igual a bioma.

Principal DK2 com t23. Famílias: 36 coeficientes por classe,12 testes conjuntos,36 contrastes formais,24 magnitudes incrementais. Holm por família não protege busca adaptativa entre rodadas; IC95 pontuais. Sensibilidades de covariância mantidas, matrizes brutas não positivas explicitadas sem PSD. Não escolher a que rejeita. Tendências/FE adicionais removem também possível resposta econômica: mudança de coeficiente não demonstra causalmente explicação concorrente.

'''
text+='## Ajustes\n\n'+table(m[['id','N','municipios','anos','K_total','condicao','ajuste']])+'\n\n'
text+='## Testes conjuntos das duas interações com interface\n\n'+table(sens[['id','covariancia','F','p','p_holm','status']])+'\n\n'
text+='## Comparação dos incrementos com a referência da rodada6\n\n'+table(compare[['id','termo','coef_base','ic95_inf_base','ic95_sup_base','coef','ic95_inf','ic95_sup','p_holm']])+'\n\n'
text+='## Contrastes formais e magnitudes, incluindo nulos\n\n'+table(g[['id','contraste','estimativa','se','ic95_inf','ic95_sup','p','p_holm']])+'\n\n'
text+='## Variação residual retida por classe e regressor\n\n'+table(v.assign(classe=v.id.str[0]).groupby(['classe','termo']).variancia_residual_retida.agg(['min','max']).reset_index())+'\n\n'
text+='''## Fechamento admissível

Esta rodada encerra a comparação planejada dos gradientes territoriais com controles de choques e tendências. Nenhum novo modelo será escolhido pela direção ou pelo p. As evidências associativas e suas sensibilidades são descritas em CONCLUSAO_GERAL.md; não aceitam nem rejeitam toda H1 causal. Ausência de rejeição pode refletir imprecisão; não foi predefinida margem de equivalência. Mais combinações da mesma amostra não criariam conversão localizada por cultura, dados de algodão, suporte Pantanal ou um desenho exógeno para fiscalização. Esses são os próximos dados necessários.

Resultados locais; publicação pendente de autorização específica para o escopo ampliado.
'''
(p/'RESULTADOS.md').write_text(text)
with (p/'RESULTADOS.md').open('a') as f:
 f.write('''\n## Achado e alcance\n\nG71_pastagem (interface >1e−6, FE município+bioma×ano): incremento milho −1,1720 pp por unidade log-preço×DP aptidão (SE DK2 0,2490; IC95 −1,6872 a −0,6568; p bruto 0,0000968; Holm36 0,00329). Na escala +10% preço e P75−P25 aptidão, a diferença do gradiente entre mistos e não mistos é −0,0867 pp (IC95 −0,1248 a −0,0486), aproximadamente −0,867 ha por 1000 ha nativos. É diferença de gradientes, não diferença total de conversão entre grupos ou efeito médio do preço.\n\nTeste conjunto G71 das duas interações: Holm12 DK2 0,0000109, municipal 0,0135, two-way bruto 0,0297; também rejeita nas outras duas definições com DK2 e municipal. A interação milho permanece negativa nas três definições e com tendências; T71 estimativa −0,6820 (IC95 −1,0495 a −0,3145). Contudo, os testes conjuntos das tendências não rejeitam após Holm com cluster municipal (0,147/0,147/0,058). Portanto há padrão associativo localizado e persistência de sinal, com robustez inferencial parcial, não validação uniforme de H1.\n\nDiferença formal entre os incrementos soja e milho em G71: 2,0112, IC95 0,8283 a 3,1941; Holm36 0,0573. Não inferir que culturas diferem apenas porque milho rejeita e soja não. Não rejeitar após Holm também não demonstra igualdade. Interações xh retêm cerca de 98–99% da variação residual com FE bioma×ano; tendências retêm cerca de 75–79%. A alteração da estimativa não pode ser atribuída apenas a desaparecimento de todo suporte.\n\nEsses resultados são compatíveis com heterogeneidade territorial da associação incentivo×aptidão na conversão para pastagem. Não identificam qual mecanismo a produz: custos, composição produtiva, instituições, substituição de uso ou seleção territorial continuam alternativas, não explicações comprovadas. A classificação municipal é uma medição imperfeita de interface; não permite alegar mecanismo ecológico de ecótono.\n''')
