from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,nbformat
from scipy import stats
from statsmodels.stats.multitest import multipletests
from linearmodels.panel import PanelOLS
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parent/'testes2'))
from metodos import dados
from apoio import preparar
c=pd.read_csv(p/'COEFICIENTES.csv');m=pd.read_csv(p/'MODELOS.csv');g=pd.read_csv(p/'MAGNITUDES.csv');j=pd.read_csv(p/'TESTES_CONJUNTOS.csv')
assert len(m)==16 and len(c)==76 and len(g)==84 and len(j)==16
assert c.titulo.notna().all() and m.convergiu.all()
assert not c.duplicated(['id','termo']).any()
assert np.allclose(c.p,2*stats.t.sf(abs(c.coef/c.se),c.df))
assert np.allclose(c.ic95_sup,c.coef+stats.t.ppf(.975,c.df)*c.se)
for tab in [c,g,j]:
 for family,a in tab.groupby('familia'):
  assert np.allclose(a.p_holm,multipletests(a.p,method='holm')[1])
# Verifica cada contraste a partir da matriz inteira, não da soma de variâncias.
for ident,a in g.groupby('id'):
 cov=pd.read_csv(p/f'cov_{ident}_DK2.csv',index_col=0);co=c[c.id.eq(ident)].set_index('termo').loc[cov.index]
 for _,z in a[a.familia.eq('contrastes_formais')].iterrows():
  name=z.contraste
  if name.startswith('Soja menos'):w={'x_soja':1,'x_milho':-1}
  elif name=='Incremento territorial soja':w={'xh_soja':1}
  elif name=='Incremento territorial milho':w={'xh_milho':1}
  else:w={'xh_soja':1,'xh_milho':-1}
  v=np.array([w.get(k,0) for k in cov.index]);assert np.isclose(v@co.coef,z.estimativa);assert np.isclose(np.sqrt(v@cov.to_numpy()@v),z.se)
# Estimador independente na especificação hierárquica com fração contínua.
d=preparar(dados(p));s=d.dropna(subset=['pp_agricultura','pp_pastagem','x_soja','x_milho',*d.filter(like='biome_').columns]);s=s.loc[s.biome_pantanal_share_i.le(1e-6)].copy()
for b in ['B61','B62','B63']:
 s['h']=s.biome_amazonia_share_i if b=='B63' else s.bioma.eq('Amazônia').astype(float)
 for k in ['soja','milho']:s['xh_'+k]=s['x_'+k]*s.h;s['ph_'+k]=s['lp_'+k]*s.h
 for y in ['agricultura','pastagem']:
  ident=b+'_'+y;terms=c[c.id.eq(ident)].termo.tolist();a=s.set_index(['id','ano']);kw={'entity_effects':True}
  if b=='B62':kw['other_effects']=pd.DataFrame({'bioyear':pd.factorize(s.bioma.astype(str)+'_'+s.ano.astype(str))[0]},index=a.index)
  else:kw['time_effects']=True
  fit=PanelOLS(a['pp_'+y],a[terms],**kw).fit();target=c[c.id.eq(ident)].set_index('termo').loc[terms].coef
  assert np.allclose(fit.params,target,rtol=1e-7,atol=1e-9)
for f,h in json.loads((p/'RODADAS_ANTERIORES_SHA256.json').read_text()).items():assert hashlib.sha256((p.parent/f).read_bytes()).hexdigest()==h,f
meta=json.loads((p/'METADADOS.json').read_text());assert hashlib.sha256((p/'ESTRATEGIA.md').read_bytes()).hexdigest()==meta['estrategia_sha256']
for name in json.loads((p/'ordem.json').read_text()):
 n=nbformat.read(p/(name+'.ipynb'),4);nbformat.validate(n)
 for cell in n.cells:
  if cell.cell_type=='code':assert cell.execution_count and not any(o.output_type=='error' for o in cell.outputs)
log=[json.loads(x) for x in (p/'tentativas.jsonl').read_text().splitlines()];assert sum(x['status']=='concluido' for x in log)==16
out={'notebooks_executados':4,'modelos':16,'coeficientes':76,'contrastes_formais':52,'magnitudes':32,'familias_coef':c.groupby('familia').size().to_dict(),'SE_IC_p_Holm_conferidos':True,'contrastes_matriz_completa':True,'seis_modelos_verificados_PanelOLS':True,'rodadas2_a5_preservadas':True,'estrategia_preservada':True,'publicacao':'não realizada; pendente autorização'}
(p/'VALIDACAO_FINAL.json').write_text(json.dumps(out,indent=2,ensure_ascii=False));print(json.dumps(out,indent=2,ensure_ascii=False))
