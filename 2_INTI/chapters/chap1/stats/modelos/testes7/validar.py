from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,nbformat
from scipy import stats
from statsmodels.stats.multitest import multipletests
from linearmodels.panel import PanelOLS
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parent/'testes2'));sys.path.insert(0,str(p.parent/'testes6'))
from metodos import dados
from apoio import preparar
c=pd.read_csv(p/'COEFICIENTES.csv');m=pd.read_csv(p/'MODELOS.csv');g=pd.read_csv(p/'MAGNITUDES.csv');j=pd.read_csv(p/'TESTES_CONJUNTOS.csv')
assert (len(m),len(c),len(g),len(j))==(12,72,60,12)
assert m.N.eq(2623).all() and m.municipios.eq(126).all() and m.anos.eq(24).all()
assert c.titulo.notna().all() and m.convergiu.all()
assert np.allclose(c.p,2*stats.t.sf(abs(c.coef/c.se),c.df))
assert np.allclose(c.ic95_sup,c.coef+stats.t.ppf(.975,c.df)*c.se)
for tab in [c,g,j]:
 for family,a in tab.groupby('familia'):assert np.allclose(a.p_holm,multipletests(a.p,method='holm')[1])
for ident,a in g.groupby('id'):
 cov=pd.read_csv(p/f'cov_{ident}_DK2.csv',index_col=0);co=c[c.id.eq(ident)].set_index('termo').loc[cov.index]
 for _,z in a[a.familia.eq('incrementos_formais')].iterrows():
  weights={'xh_soja':1} if z.contraste=='Incremento soja' else ({'xh_milho':1} if z.contraste=='Incremento milho' else {'xh_soja':1,'xh_milho':-1});v=np.array([weights.get(k,0) for k in cov.index]);assert np.isclose(v@co.coef,z.estimativa);assert np.isclose(np.sqrt(v@cov.to_numpy()@v),z.se)
d=preparar(dados(p));s=d.dropna(subset=['pp_agricultura','pp_pastagem','x_soja','x_milho',*d.filter(like='biome_').columns]);s=s.loc[s.biome_pantanal_share_i.le(1e-6)].copy()
s['h']=s.filter(like='biome_').gt(1e-6).sum(axis=1).gt(1).astype(float)
for k in ['soja','milho']:s['xh_'+k]=s['x_'+k]*s.h;s['ph_'+k]=s['lp_'+k]*s.h
for prefix in ['G71','T71']:
 for y in ['agricultura','pastagem']:
  ident=prefix+'_'+y;terms=c[c.id.eq(ident)].termo.tolist();a=s.set_index(['id','ano']);target=c[c.id.eq(ident)].set_index('termo').loc[terms].coef
  if prefix.startswith('G'):
   effects=pd.DataFrame({'bioyear':pd.factorize(s.bioma.astype(str)+'_'+s.ano.astype(str))[0]},index=a.index);fit=PanelOLS(a['pp_'+y],a[terms],entity_effects=True,other_effects=effects).fit();estimate=fit.params
  else:
   fi=pd.get_dummies(s.id,dtype=float).to_numpy();ft=pd.get_dummies(s.ano,dtype=float).to_numpy();time=s.ano.to_numpy()-s.ano.mean();design=np.column_stack([s[terms].to_numpy(),fi,ft,fi*time[:,None]]);estimate=np.linalg.lstsq(design,s['pp_'+y],rcond=None)[0][:len(terms)]
  assert np.allclose(estimate,target,atol=1e-8,rtol=1e-7)
for f,h in json.loads((p/'RODADAS_ANTERIORES_SHA256.json').read_text()).items():assert hashlib.sha256((p.parent/f).read_bytes()).hexdigest()==h,f
meta=json.loads((p/'METADADOS.json').read_text());assert hashlib.sha256((p/'ESTRATEGIA.md').read_bytes()).hexdigest()==meta['estrategia_sha256']
for name in json.loads((p/'ordem.json').read_text()):
 n=nbformat.read(p/(name+'.ipynb'),4);nbformat.validate(n)
 for cell in n.cells:
  if cell.cell_type=='code':assert cell.execution_count and not any(o.output_type=='error' for o in cell.outputs)
assert len([x for x in (p/'tentativas.jsonl').read_text().splitlines() if json.loads(x)['status']=='concluido'])==12
out={'notebooks_executados':2,'modelos':12,'coeficientes':72,'contrastes_formais':36,'magnitudes':24,'SE_IC_p_Holm_conferidos':True,'FEbioma_PanelOLS_e_tendencias_dummies':True,'rodadas2_a6_preservadas':True,'estrategia_preservada':True,'publicacao':'não realizada; pendente autorização'}
(p/'VALIDACAO_FINAL.json').write_text(json.dumps(out,indent=2,ensure_ascii=False));print(json.dumps(out,indent=2,ensure_ascii=False))
