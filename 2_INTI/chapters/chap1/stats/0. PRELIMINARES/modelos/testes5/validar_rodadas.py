"""Verificação integrada de preservação, execução, amostras e inferência."""
from pathlib import Path
import sys,json,hashlib,subprocess
import numpy as np,pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
p=Path(__file__).resolve().parent;base=p.parent
raiz=next(q for q in base.parents if (q/'AGENTS.md').exists())
rel=[]
for i,esperado in [(2,19),(3,15),(4,346),(5,8)]:
 q=base/f'testes{i}';c=pd.read_csv(q/'COEFICIENTES.csv');m=pd.read_csv(q/'MODELOS.csv');s=pd.read_csv(q/'SENSIBILIDADES.csv');l=pd.read_csv(q/'PERDAS.csv');meta=json.loads((q/'METADADOS.json').read_text())
 assert len(m)==esperado and not c.duplicated(['id','termo']).any()
 assert np.isfinite(c[['coef','se','p']]).all().all() and c.se.gt(0).all()
 assert (c.N_apos_pre_filtros-c.perdas_casos_completos==c.N).all()
 assert (c.N_grade-c.perdas_pre_filtros==c.N_apos_pre_filtros).all()
 for ident,g in l.groupby('id'):
  assert (g.antes-g.excluidos==g.restantes).all()
  assert g.restantes.iloc[-1]==m.set_index('id').loc[ident,'N']
 z=c.merge(s[s.covariancia.eq('DK2')][['id','termo','se','p']],on=['id','termo'],suffixes=('','_sens'),validate='one_to_one')
 assert np.allclose(z.se,z.se_sens) and np.allclose(z.p,z.p_sens)
 assert np.allclose(c.p,2*stats.t.sf(abs(c.coef/c.se),c.df))
 cr=stats.t.ppf(.975,c.df)
 assert np.allclose(c.ic95_inf,c.coef-cr*c.se) and np.allclose(c.ic95_sup,c.coef+cr*c.se)
 for family,g in c.groupby('familia'):
  assert np.allclose(g.p_holm,multipletests(g.p,method='holm')[1]) and g.n_familia.eq(len(g)).all()
 for f,h in meta['hashes_protegidos'].items():assert hashlib.sha256((raiz/f).read_bytes()).hexdigest()==h
 assert hashlib.sha256((q/'ESTRATEGIA.md').read_bytes()).hexdigest()==meta['estrategia_sha256']
 nbc=0
 for f in q.glob('*.ipynb'):
  nb=json.loads(f.read_text());cells=[x for x in nb['cells'] if x['cell_type']=='code'];assert all(x['execution_count'] is not None for x in cells)
  assert not any(o['output_type']=='error' for x in cells for o in x['outputs']);nbc+=1
 baseline=Path('/tmp/rodadas_baseline')/f'testes{i}.csv'
 if baseline.exists():
  b=pd.read_csv(baseline);z=b.merge(c,on=['id','termo'],suffixes=('_antes',''),validate='one_to_one');assert len(z)==len(b)
  for v in ['coef','se','p']:assert np.allclose(z[v],z[v+'_antes'],rtol=1e-7,atol=1e-9)
 rel.append({'rodada':i,'modelos':len(m),'coeficientes':len(c),'notebooks':nbc,'familias':c.groupby('familia').size().to_dict(),'dados_textos_rodada1_preservados':True,'estrategia_preservada':True,'SE_IC_p_Holm_reconciliados':True,'reexecucao_estavel':True})
 # Manifesto de arquivos entregues; não inclui cache nem o próprio manifesto.
 manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in q.iterdir() if f.is_file() and f.name!='ARQUIVOS_SHA256.json'}
 (q/'ARQUIVOS_SHA256.json').write_text(json.dumps(manifest,indent=2))
b=pd.read_csv(p/'BOOTSTRAP.csv');assert len(b)==32 and b.variancias_degeneradas.eq(0).all()
for row in b.itertuples():
 f=p/f'bootstrap_{row.id}_{row.contraste}_b{row.bloco_anos}.csv.gz';draw=pd.read_csv(f)
 assert len(draw)==2**row.blocos==row.padroes and np.isfinite(draw.t_boot).all()
 pv=(abs(draw.t_boot)>=abs(row.t_observado)-1e-10).mean();assert np.isclose(pv,row.p_wild)
 assert np.isclose(draw.t_boot.iloc[-1],row.t_observado)
for size,g in b.groupby('bloco_anos'):assert np.allclose(g.p_wild_holm,multipletests(g.p_wild,method='holm')[1])
# Checagem independente dos FE de tendência e bioma-ano por dummies explícitas.
sys.path.insert(0,str(base/'testes2'))
from metodos import dados
x=dados(base/'testes2').dropna(subset=['pp_agricultura','expo_soja','expo_milho'])
cc=pd.read_csv(base/'testes3/COEFICIENTES.csv')
for ident,trend in [('B03_agricultura',True),('B04_agricultura',False)]:
 idmat=pd.get_dummies(x.id,dtype=float).to_numpy();group=x.ano if trend else x.bioma.astype(str)+'_'+x.ano.astype(str);tm=pd.get_dummies(group,dtype=float).to_numpy()
 matrices=[idmat,tm]
 if trend:matrices.append(idmat*(x.ano-x.groupby('id').ano.transform('mean')).to_numpy()[:,None])
 xx=x[['expo_soja','expo_milho']].to_numpy();a=np.column_stack([*matrices,xx]);coef=np.linalg.lstsq(a,x.pp_agricultura,rcond=None)[0][-2:]
 reference=cc[cc.id.eq(ident)].set_index('termo').loc[['expo_soja','expo_milho'],'coef'].to_numpy();assert np.allclose(coef,reference,atol=1e-8)
out={'rodadas':rel,'bootstrap_exercicios':len(b),'bootstrap_padroes':int(b.padroes.sum()),'bootstrap_p_reconciliados':True,'FE_tendencias_bioma_conferidos_dummies':True,'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=raiz,text=True).strip(),'git_status':subprocess.check_output(['git','status','--short'],cwd=raiz,text=True),'publicacao':'não realizada; autorização pendente'}
(p/'VALIDACAO_INTEGRADA.json').write_text(json.dumps(out,indent=2));(raiz/'2_INTI/audit/testes5/validacao_integrada.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
