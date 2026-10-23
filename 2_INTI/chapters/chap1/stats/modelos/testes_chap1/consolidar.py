"""Valida coeficientes e perdas; consolida sem filtrar significância."""
from utilitarios import *
import subprocess
p=PASTA
coef=pd.concat([pd.read_csv(f) for f in sorted(p.glob('coef_*.csv'))],ignore_index=True)
assert coef.id.nunique()==24, coef.id.unique()
assert not coef.duplicated(['id','termo']).any()
assert np.isfinite(coef.coef).all()
assert np.isfinite(coef.se).all()
assert (coef.se>0).all()
assert (coef.N>coef.posto).all()
assert coef.p.dropna().between(0,1).all()
coef.to_csv(p/'modelos_coeficientes.csv',index=False)
modelos=coef.drop_duplicates('id').drop(columns=['termo','coef','se','se_two_way_bruto','ic95_inf','ic95_sup','p','interpretacao'])
modelos.to_csv(p/'modelos_resumo.csv',index=False)
status=modelos[['id','titulo','estimador','N']].copy();status['status']='estimado';status.to_csv(p/'status_modelos.csv',index=False)
perdas=pd.concat([pd.read_csv(f) for f in sorted(p.glob('perdas_*.csv'))],ignore_index=True)
assert (perdas.antes-perdas.excluidos==perdas.restantes).all()
for ident,g in perdas.groupby('id_modelo'):
 assert g.restantes.iloc[-1]==int(modelos.set_index('id').loc[ident,'N'])
perdas.to_csv(p/'amostras_perdas.csv',index=False)
for u in ['agricultura','pastagem']:
 assert modelos.set_index('id').loc['M01C_'+u,'N']==modelos.set_index('id').loc['M02_'+u,'N']
 assert modelos[modelos.id.isin(['P01_'+u,'P02_'+u,'P03_'+u])].N.nunique()==1
meta=json.loads((AUDIT/'metadados_estimacao.json').read_text())
assert hashlib.sha256(CSV.read_bytes()).hexdigest()==meta['csv_sha256']
assert all(hashlib.sha256((RAIZ/'2_INTI/chapters/chap1/text'/nome).read_bytes()).hexdigest()==h for nome,h in meta['hashes_textos'].items())
valid={'modelos':24,'coeficientes':len(coef),'csv_preservado':True,'textos_preservados':True,'perdas_consistentes':True,'amostras_comparaveis':True,'coeficientes_finitos':True,'se_ausentes':int(coef.se.isna().sum()),'git_status':subprocess.check_output(['git','status','--short'],cwd=RAIZ,text=True)}
(AUDIT/'validacao.json').write_text(json.dumps(valid,indent=2))
print(json.dumps(valid,indent=2))
# Verifica independentemente SE, IC e p a partir das matrizes salvas.
for ident,g in coef.groupby('id',sort=False):
 bruto=pd.read_csv(p/f'cov_bruta_{ident}.csv',index_col=0).loc[g.termo,g.termo].to_numpy()
 corrigido=cov_psd(bruto) if np.linalg.eigvalsh(bruto).min() < -1e-10 else bruto
 se=np.sqrt(np.maximum(np.diag(corrigido),0))
 assert np.allclose(se,g.se,rtol=1e-7,atol=1e-9)
 crit=st.t.ppf(.975,g.df_inferencia.to_numpy())
 assert np.allclose(g.ic95_inf,g.coef-crit*se,rtol=1e-7,atol=1e-9)
 assert np.allclose(g.ic95_sup,g.coef+crit*se,rtol=1e-7,atol=1e-9)
 assert np.allclose(g.p,2*st.t.sf(abs(g.coef/se),g.df_inferencia),rtol=1e-7,atol=1e-9)
sens=[]
for f in sorted(p.glob('sensibilidade_*.csv')):
 q=pd.read_csv(f);col=next(x for x in q.columns if x.startswith('se_'))
 q=q.rename(columns={col:'se_sensibilidade'});q['metodo_sensibilidade']=col
 q=q.merge(coef[['id','termo','coef','municipios','N','posto','se']],on=['id','termo'],validate='one_to_one')
 gl=q.N-q.posto if 'HAC' in col else q.municipios-1
 q['ic95_inf_sensibilidade']=q.coef-st.t.ppf(.975,gl)*q.se_sensibilidade
 q['ic95_sup_sensibilidade']=q.coef+st.t.ppf(.975,gl)*q.se_sensibilidade
 q['p_sensibilidade']=2*st.t.sf(abs(q.coef/q.se_sensibilidade),gl)
 q['df_sensibilidade']=gl
 sens.append(q)
pd.concat(sens,ignore_index=True).to_csv(p/'sensibilidades_covariancia.csv',index=False)
valid.update(se_ic_p_reconciliados=True,modelos_com_psd=int(modelos.cov_correcao.eq('PSD espectral').sum()),se_brutos_ausentes=int(coef.se_two_way_bruto.isna().sum()))
(AUDIT/'validacao.json').write_text(json.dumps(valid,indent=2))
