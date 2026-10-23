"""Conferência independente de integridade, junções, máscaras e derivadas."""
from pathlib import Path
import csv,json,hashlib
import numpy as np,pandas as pd
from construir import lag
P=Path(__file__).resolve().parent;B=P.parent;R=next(x for x in P.parents if (x/'AGENTS.md').exists());key=['codigo_ibge','ano']
original=B/'painel_municipal_descritiva_h1.csv';master=P/'painel_h1_v2.csv'
a=list(csv.DictReader(original.open()));b=list(csv.DictReader(master.open()))
assert len(a)==len(b)==3384
assert all(all(x[c]==y[c] for c in x) for x,y in zip(a,b)),'Token original alterado'
d=pd.read_csv(original,dtype={'codigo_ibge':'string'});v=pd.read_csv(master,dtype={'codigo_ibge':'string'});q=pd.read_csv(P/'candidatos_quarentena.csv',dtype={'codigo_ibge':'string'});pt=pd.read_csv(B.parent/'EDA/paineis/painel_tese_chap1_pt.csv',dtype={'codigo_ibge':'string'})
assert not v.duplicated(key).any() and not q.duplicated(key).any()
assert v.codigo_ibge.nunique()==141 and v.groupby('codigo_ibge').ano.nunique().eq(24).all()
pd.testing.assert_frame_equal(d,v[d.columns],check_exact=True)
pd.testing.assert_frame_equal(v[key],q[key])
pt=d[key].merge(pt,on=key,validate='one_to_one',sort=False)
for col in q:
 if not col.startswith('cand__') or col.endswith('__somente_completos'):continue
 x=pt[col[6:]];y=q[col];assert x.isna().eq(y.isna()).all()
 if pd.api.types.is_numeric_dtype(x):assert np.allclose(x,y,equal_nan=True)
 else:assert x.astype('string').fillna('<NA>').eq(y.astype('string').fillna('<NA>')).all()
for crop in ['soja','milho']:
 source='rendimento_medio_kg_ha__'+crop;col='v2__rendimento_observado_lag1_kg_ha__'+crop
 # Join ao ano anterior: implementação diferente de groupby.shift.
 prev=d[key+[source]].copy();prev.ano+=1;expected=d[key].merge(prev,on=key,how='left',validate='one_to_one')[source]
 assert np.allclose(v[col],expected,equal_nan=True);assert v.loc[v.ano.eq(2001),col].isna().all()
# Não atravessar lacunas, não substituir missing nem eliminar zero em lag.
toy=pd.DataFrame({'codigo_ibge':['5100001']*5,'ano':[2001,2002,2004,2005,2006]});values=pd.Series([0.,2.,np.nan,5.,9.]);got=lag(values,toy)
assert np.allclose(got,[np.nan,0.,np.nan,np.nan,5.],equal_nan=True)
assert v.v2__flag_amostra_conversao_ambos.sum()==2772
assert v.v2__flag_amostra_fiscal_lag1.sum()==1140
assert v.v2__flag_zero_conversao_registrado__agricultura.sum()==265
assert v.v2__flag_zero_conversao_registrado__pastagem.sum()==0
assert v.v2__flag_desfecho_ausente_cobertura_par.sum()==612
profile=pd.read_csv(P/'missing_zeros_por_variavel.csv')
for group in ['ano','codigo_ibge','bioma_predominante']:
 detail=pd.read_csv(P/f'missing_zeros_por_{group}.csv.gz');summed=detail.groupby(['camada','variavel'])[['N','missing','zero_registrado','negativo_registrado','nao_finito','observado']].sum().sort_index();target=profile.set_index(['camada','variavel'])[summed.columns].sort_index();pd.testing.assert_frame_equal(summed,target,check_dtype=False)
for layer,frame in [('mestre',v),('quarentena',q)]:
 masks=pd.read_csv(P/f'mascaras_{layer}.csv.gz',dtype={'codigo_ibge':'string'})
 for c in masks.columns:
  if c in key:continue
  assert masks[c].eq(0).eq(frame[c].isna()).all()
  if pd.api.types.is_numeric_dtype(frame[c]) and not pd.api.types.is_bool_dtype(frame[c]):assert masks[c].eq(1).eq(frame[c].eq(0)&frame[c].notna()).all()
for rel,h in json.loads((P/'FONTES_PROTEGIDAS_SHA256.json').read_text()).items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==h,rel
meta=json.loads((P/'AUDITORIA_QUALIDADE.json').read_text());assert meta['plano_sha256']==hashlib.sha256((P/'PLANO_DECISOES.md').read_bytes()).hexdigest()
dictionary=pd.read_csv(P/'dicionario_variaveis.csv');assert not dictionary.variavel.duplicated().any();assert set(dictionary.variavel)==set(v.columns)|set(q.columns)
assert dictionary[['unidade','temporalidade','risco_causal','arquivo_origem','observado']].notna().all().all()
result={'aprovado':True,'linhas':len(v),'colunas':len(v.columns),'candidatos_separados':len(q.columns)-4,'original_tokens_e_valores_exatos':True,'chaves141_e_join_um_para_um':True,'defasagens_conferidas_join_e_lacunas':True,'zeros_faltantes_mascaras_relatorios_reconciliados':True,'fontes_rodadas1_7_preservadas':True,'dicionario_completo':True,'regressoes_executadas':0,'imputacoes_executadas':0}
(P/'VALIDACAO_FINAL.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print(json.dumps(result,indent=2,ensure_ascii=False))
