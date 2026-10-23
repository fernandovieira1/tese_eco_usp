"""Sensibilidades territoriais, mantendo hierarquia das interações."""
import numpy as np,pandas as pd
from metodos import projetar

def estimar(e,ident,y,s,bio):
 s=s.copy();x=['x_soja','x_milho','xh_soja','xh_milho','ph_soja','ph_milho']
 for c in ['soja','milho']:
  s['xh_'+c]=s['x_'+c]*s.h;s['ph_'+c]=s['lp_'+c]*s.h
 f=e.linear(ident,y,x,s=s,bioma_ano=bio,trend=not bio,familia='FEbioma' if bio else 'tendencias',joint=['xh_soja','xh_milho'])
 contrasts={'Incremento soja':{'xh_soja':1},'Incremento milho':{'xh_milho':1},'Incremento soja menos milho':{'xh_soja':1,'xh_milho':-1}}
 for name,w in contrasts.items():e.contraste(ident,name,x,f['b'],f['cov']['DK2'],w,f['s'],'pp por log-preço × DP aptidão','incrementos_formais')
 for c in ['soja','milho']:
  q=e.d.drop_duplicates('id')['z_a_'+c].quantile([.25,.75]);mult=np.log(1.1)*(q.loc[.75]-q.loc[.25]);e.contraste(ident,'Incremento misto; +10% '+c+'; aptidão P75−P25',x,f['b'],f['cov']['DK2'],{'xh_'+c:mult},f['s'],'pp','magnitudes')
 base,_,_=projetar(f['s'],x);ratio=(f['xx']**2).sum(axis=0)/(base**2).sum(axis=0)
 pd.DataFrame({'id':ident,'termo':x,'variancia_residual_retida':ratio}).to_csv(e.p/f'variacao_{ident}.csv',index=False)
 return f
