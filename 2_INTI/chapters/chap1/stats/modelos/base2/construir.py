"""Base2 local: junção 1:1, camadas separadas, sem imputação ou regressões."""
from pathlib import Path
import hashlib,json,subprocess,sys,importlib.util,gzip
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent;B=P.parent;R=next(x for x in P.parents if (x/'AGENTS.md').exists());S=B.parent
KEY=['codigo_ibge','ano'];SOURCE=B/'painel_municipal_descritiva_h1.csv';PT=S/'EDA/paineis/painel_tese_chap1_pt.csv'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def load(f):return pd.read_csv(f,dtype={'codigo_ibge':'string'})
def save(d,name):
 f=P/name
 if name.endswith('.gz'):
  with f.open('wb') as raw:
   with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:gz.write(d.to_csv(index=False).encode())
 else:d.to_csv(f,index=False)
def assert_keys(d):
 assert not d.duplicated(KEY).any() and d.codigo_ibge.str.fullmatch(r'\d{7}').all()
 assert d[KEY].notna().all().all()
def boolean(s):return s.astype('string').str.lower().map({'true':True,'false':False}).astype('boolean')
def complete(s):return boolean(s).eq(False).fillna(False)  # Elegibilidade, não preenchimento do dado.
def finite(s):return s.notna() & np.isfinite(s)
def lag(s,df):
 order=df[KEY].sort_values(KEY).index;ss=s.loc[order];ids=df.loc[order,'codigo_ibge'];year=df.loc[order,'ano']
 return ss.groupby(ids).shift(1).where(year.eq(year.groupby(ids).shift(1)+1)).reindex(df.index)

def main():
 plan_hash=sha(P/'PLANO_DECISOES.md')
 protected=[SOURCE,PT,*list((R/'2_INTI/chapters/chap1/text').glob('*.tex'))]
 for name in ['testes_chap1',*[f'testes{k}' for k in range(2,8)]]:
  protected += [f for f in (B/name).rglob('*') if f.is_file() and '__pycache__' not in str(f)]
 before={str(f.relative_to(R)):sha(f) for f in protected}
 d=load(SOURCE);t=load(PT);assert_keys(d);assert_keys(t)
 assert d.shape==(3384,70) and t.shape==(3384,296)
 assert d.codigo_ibge.nunique()==141 and set(d.ano)==set(range(2001,2025))
 keys=d[KEY].merge(t[KEY],on=KEY,how='outer',indicator=True,validate='one_to_one')
 assert keys._merge.eq('both').all();save(keys,'auditoria_chaves.csv')
 t=d[KEY].merge(t,on=KEY,how='left',validate='one_to_one',sort=False)
 compare=[]
 for c in [c for c in d if c in t and c not in KEY]:
  a,b=d[c],t[c];same_na=a.isna().eq(b.isna());ok=(np.isclose(a,b,equal_nan=True,rtol=1e-10,atol=1e-12) if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b) else a.astype('string').fillna('<NA>').eq(b.astype('string').fillna('<NA>')))
  compare.append(dict(coluna=c,divergencias=int((~ok).sum()),divergencias_missing=int((~same_na).sum())))
 save(pd.DataFrame(compare),'comparacao_principal_PT.csv');assert all(x['divergencias']==0 for x in compare),'Divergência entre fontes: revisar antes do join.'
 dictionary=[];original_dict={}
 for file in [S/'descritiva/resultados_h1/dicionario_variaveis.csv',S/'descritiva/resultados_h1_humanizado/dados/dicionario_oferta.csv']:
  for z in pd.read_csv(file).to_dict('records'):original_dict[z['nome_final']]=z
 def entry(c,layer,source_col,source_path,unit,time,risk,definition='',primary=''):
  dictionary.append(dict(variavel=c,camada=layer,coluna_origem=source_col,arquivo_origem=str(source_path.relative_to(R)) if isinstance(source_path,Path) else source_path,fonte_primaria=primary,unidade=unit,temporalidade=time,definicao=definition,risco_causal=risk,tratamento_missing='preservado; sem imputação',interpretacao_zero='zero registrado; significado estrutural e imputação herdada não certificados integralmente'))
 for c in d:
  z=original_dict.get(c,{})
  entry(c,'nucleo_original_preservado',c,SOURCE,z.get('unidade','identificador/flag conforme coluna'),z.get('cobertura','municipal anual2001–2024; estáticos/preços repetidos conforme dicionário original'),z.get('limitacao_adicional','Preservado; sem certificação adicional da cadeia de origem.'),z.get('definicao',z.get('rotulo',c)),z.get('fonte_primaria','arquivo original; dicionário não individualiza'))
 out=d.copy()
 coverage=['y_colecao','y_malha','y_mascara_id','y_area_total_ha','y_area_valida_par_ha','y_area_nao_valida_par_ha','y_cobertura_completa','y_fracao_area_valida_par','y_flag_denominador_zero','y_flag_denominador_ausente']
 assert t.y_malha.eq('IBGE_MT_2023_141').all()
 assert boolean(t.y_cobertura_completa).eq(d.conversao_ha__agricultura.notna()).all()
 assert boolean(t.y_cobertura_completa).eq(d.conversao_ha__pastagem.notna()).all()
 for c in coverage:
  name='v2__'+c;out[name]=t[c]
  unit='ha' if c.endswith('_ha') else ('fração' if 'fracao' in c else ('flag' if 'flag' in c or 'completa' in c else 'metadado'))
  entry(name,'metadado_qualidade_fonte',c,PT,unit,'par anual t−1,t; malha2023','Flag herdada auditada internamente; não reconstrói os mapas.','Cobertura e identificador do par cartográfico','MapBiomas10.1/IBGE_MT_2023_141')
 for crop,orig in [('soja','Soja (em grão)'),('milho','Milho (em grão)')]:
  a=d['rendimento_medio_kg_ha__'+crop];b=t['rendimento_medio_kg_ha__'+orig]
  assert a.isna().eq(b.isna()).all() and np.allclose(a,b,equal_nan=True)

 climate=['precip_mm_anual','meses_registrados','meses_validos','meses_cobertura_conhecida','fracao_pixels_minima','flag_ano_incompleto','media_1981_2000','desvio_1981_2000','count_1981_2000','precip_anomaly_1981_2000','precip_zscore_1981_2000']
 assert t.meses_validos.eq(12).all() and t.meses_registrados.eq(12).all() and t.meses_cobertura_conhecida.eq(12).all()
 assert complete(t.flag_ano_incompleto).all() and t.fracao_pixels_minima.between(0,1).all() and t.precip_mm_anual.ge(0).all()
 assert t.count_1981_2000.ge(7).all() and t.desvio_1981_2000.gt(0).all()
 # Conserva climatologia histórica existente; nenhuma média é estimada novamente.
 assert np.allclose(t.precip_anomaly_1981_2000,t.precip_mm_anual-t.media_1981_2000)
 assert np.allclose(t.precip_zscore_1981_2000,(t.precip_mm_anual-t.media_1981_2000)/t.desvio_1981_2000)
 relief=['elevation_mean_m','elevation_min_m','elevation_max_m','flag_ordem_invalida']
 assert t.elevation_min_m.le(t.elevation_mean_m).all() and t.elevation_mean_m.le(t.elevation_max_m).all()
 assert t.groupby('codigo_ibge')[relief[:3]].nunique().max().eq(1).all()
 for c in climate+relief:
  name='v2__'+c;out[name]=t[c]
  unit='flag' if c.startswith('flag_') else ('m' if c.startswith('elevation') else ('contagem' if c.startswith(('meses','count')) else ('adimensional' if c in ['fracao_pixels_minima','precip_zscore_1981_2000'] else 'mm')))
  entry(name,'validacao_interna_documental',c,PT,unit,'estático' if c in relief else 'ano civil; normal1981–2000 quando indicada','Geometria/raster não reextraídos; chuva anual não é calendário agrícola; relevo não é acesso/custo.',c,'Copernicus GLO-90' if c in relief else 'CHIRPS v2')
 for crop in ['soja','milho']:
  c='rendimento_medio_kg_ha__'+crop;name='v2__rendimento_observado_lag1_kg_ha__'+crop
  assert d[c].dropna().ge(0).all();out[name]=lag(d[c],d)
  entry(name,'derivada_auditada',c,SOURCE,'kg/ha','t−1 somente ano consecutivo observado','Rendimento realizado endógeno; não aptidão exógena/lucro; defasagem não elimina seleção.','shift1 sem imputação','IBGE/PAM')
 # Quarentena em arquivo separado: valores e flags originais PT, sem GM.
 candidates=[]
 for c in t:
  if c in KEY or c in climate+relief:continue
  if ('__ibama_' in c or c.startswith(('capacidade_valor__','flag_cobertura_historica','flag_geografia_historica','flag_temporalidade','flag_umidade','flag_capacidade_fora','flag_desvio_capacidade')) or c in ['agricultura_ha','pastagem_ha','agricultura_share','pastagem_share','agricultura_ha_lag1','pastagem_ha_lag1','agricultura_share_lag1','pastagem_share_lag1','lotacao_cabecas_ha','flag_pastagem_zero','flag_rebanho_ausente','flag_pastagem_ausente','flag_bovinos_sem_pastagem','compatibilidade_datas_estoques_validada','geografia_historica_validada','completude_classes_fora_grade_certificada','grade_fonte_completa','flag_area_nao_observada','flag_sem_registro_uso','flag_classe_residual_13']):
   if c not in d:candidates.append(c)
 q=d[KEY+['municipio','bioma_predominante']].copy()
 for c in candidates:
  name='cand__'+c
  if len(q.columns)%40==0:q=q.copy()
  q[name]=t[c]
  if '__ibama_' in c:source='IBAMA snapshot2026-09-30';risk='Autuação não é pagamento/efetividade; endogeneidade, parcialidade, status e deflator requerem conferência.';unit='flag' if c.startswith('flag_') else ('BRL reais; mês-base consultar fonte ausente' if 'multas_' in c and 'reais' in c else ('BRL nominais' if 'multas_' in c else 'contagem'));time='ano de lavratura; lag1 quando indicado; status atual não é histórico'
  elif 'gaez_' in c:source='FAO/IIASA GAEZ v4';risk='Clima1961–1990,terras2010; alto/baixoinsumo não é custo; matéria seca não convertida.';unit='flag' if c.startswith('flag_') else ('kg matéria seca/ha' if '_yx' in c else 'índice de aptidão; escala requer fonte');time='estático repetido'
  elif 'pam_' in c:source='IBGE/PAM1991–2000';risk='Seleção municípios produtores e geografia histórica pendente; não exógeno.';unit='flag' if c.startswith('flag_') else 'kg/ha';time='histórico1991–2000, mínimo7anos segundo documentação; estático'
  else:source='MapBiomas/IBGE PPM';risk='Trajetória de uso endógena; compatibilidade de datas/geografia não validada; lotação não produtividade.';unit='flag' if c.startswith('flag_') or 'validada' in c or 'certificada' in c or c=='grade_fonte_completa' else ('cabeças/ha' if 'lotacao' in c else ('fração' if 'share' in c else 'ha'));time='anual, t−1 onde indicado'
  entry(name,'candidato_quarentena',c,PT,unit,time,risk,c,source)
 for c,flag in [('n_autos_desmatamento__ibama_espacial','flag_contagem_desmatamento_parcial__ibama_espacial'),('multas_flora_reais_observadas__ibama_espacial','flag_soma_flora_parcial__ibama_espacial')]:
  name='cand__'+c+'__somente_completos';q[name]=t[c].where(complete(t[flag]) & finite(t[c]) & t[c].ge(0))
  entry(name,'candidato_quarentena',c+'; '+flag,PT,'contagem' if c.startswith('n_') else 'BRL reais; base pendente','ano de lavratura','Completude temática não certifica cobertura da fonte, exogeneidade, pagamento ou deflator.','valor se flag parcial=false, finito e não negativo; senão NA','IBAMA')
 # Flags: nenhuma elimina linhas; False significa não elegível para esta regra.
 flags={}
 for u in ['agricultura','pastagem']:
  flags['v2__flag_conversao_valida__'+u]=finite(d['conversao_ha__'+u]) & finite(d['taxa_conversao__'+u]) & d['conversao_ha__'+u].ge(0) & d['taxa_conversao__'+u].between(0,1) & d.y_nativa_inicial_ha.gt(0)
  flags['v2__flag_zero_conversao_registrado__'+u]=d['conversao_ha__'+u].eq(0)&flags['v2__flag_conversao_valida__'+u]
  ok=flags['v2__flag_conversao_valida__'+u];assert np.allclose(d.loc[ok,'conversao_ha__'+u]/d.loc[ok,'y_nativa_inicial_ha'],d.loc[ok,'taxa_conversao__'+u])
 flags['v2__flag_desfecho_ausente_cobertura_par']=d.conversao_ha__agricultura.isna() & boolean(t.y_cobertura_completa).eq(False)
 flags['v2__flag_amostra_conversao_ambos']=flags['v2__flag_conversao_valida__agricultura'] & flags['v2__flag_conversao_valida__pastagem']
 autos=d.n_autos_flora__ibama_espacial.where(complete(d.flag_contagem_flora_parcial__ibama_espacial)&finite(d.n_autos_flora__ibama_espacial)&d.n_autos_flora__ibama_espacial.ge(0))
 flags['v2__flag_autos_flora_elegivel_t']=autos.notna();flags['v2__flag_autos_flora_elegivel_lag1']=lag(autos,d).notna()
 flags['v2__flag_amostra_fiscal_lag1']=flags['v2__flag_amostra_conversao_ambos'] & flags['v2__flag_autos_flora_elegivel_lag1']
 flags['v2__flag_amostra_conversao_chuva']=flags['v2__flag_amostra_conversao_ambos'] & out.v2__precip_mm_anual.notna()
 flags['v2__flag_amostra_conversao_rendimentos_lag1']=flags['v2__flag_amostra_conversao_ambos'] & out.filter(like='v2__rendimento_observado_lag1').notna().all(axis=1)
 for name,val in flags.items():
  out[name]=val.astype(bool);entry(name,'flag_elegibilidade','regra em construir.py','construir.py','booleano','t/lag1 conforme nome','Elegibilidade não prova MAR/MCAR, zero estrutural ou validade causal.','Não trunca painel; False inclui condições desconhecidas/inválidas.')
 assert flags['v2__flag_amostra_conversao_ambos'].sum()==2772 and flags['v2__flag_amostra_fiscal_lag1'].sum()==1140
 pd.testing.assert_frame_equal(out[d.columns],d)
 # Preserva também a representação textual dos70campos originais no CSV.
 serial=pd.concat([pd.read_csv(SOURCE,dtype=str,keep_default_na=False),out.drop(columns=d.columns)],axis=1)
 save(serial,'painel_h1_v2.csv');save(q,'candidatos_quarentena.csv')
 parquet='não disponível; nenhum pacote instalado'
 engine='pyarrow' if importlib.util.find_spec('pyarrow') else ('fastparquet' if importlib.util.find_spec('fastparquet') else None)
 if engine:
  out.to_parquet(P/'painel_h1_v2.parquet',index=False,engine=engine);q.to_parquet(P/'candidatos_quarentena.parquet',index=False,engine=engine);parquet=engine
 # Relatórios por camada: indicadores booleanos não são contados como zeros econômicos.
 profile=[];by_group={'ano':[],'codigo_ibge':[],'bioma_predominante':[]}
 for layer,frame in [('mestre',out),('quarentena',q)]:
  mask=frame[KEY].copy()
  for c in frame:
   if c in KEY+['municipio','bioma_predominante']:continue
   v=frame[c];num=pd.api.types.is_numeric_dtype(v) and not pd.api.types.is_bool_dtype(v)
   miss=v.isna();zero=v.eq(0)&v.notna() if num else pd.Series(False,index=v.index);negative=v.lt(0)&v.notna() if num else pd.Series(False,index=v.index);inf=v.notna()&~np.isfinite(v) if num else pd.Series(False,index=v.index)
   # Códigos de estado observado; negativo pode ser legítimo (anomalias/variações).
   if len(mask.columns)%40==0:mask=mask.copy()
   mask[c]=np.select([miss,inf,zero,negative],[0,4,1,3],default=2).astype('int8')
   stats=pd.DataFrame({'N':np.ones(len(v),dtype=int),'missing':miss.astype(int),'zero_registrado':zero.astype(int),'negativo_registrado':negative.astype(int),'nao_finito':inf.astype(int),'observado':v.notna().astype(int)})
   item={'camada':layer,'variavel':c,'tipo':str(v.dtype),**stats.sum().to_dict(),'municipios_observados':frame.loc[v.notna(),'codigo_ibge'].nunique(),'ano_min_observado':frame.loc[v.notna(),'ano'].min(),'ano_max_observado':frame.loc[v.notna(),'ano'].max()};profile.append(item)
   for group in by_group:
    tab=stats.groupby(frame[group],dropna=False).sum().reset_index();tab.insert(0,'variavel',c);tab.insert(0,'camada',layer);by_group[group].append(tab)
  save(mask,f'mascaras_{layer}.csv.gz')
 prof=pd.DataFrame(profile);save(prof,'missing_zeros_por_variavel.csv')
 for group,tabs in by_group.items():save(pd.concat(tabs,ignore_index=True),f'missing_zeros_por_{group}.csv.gz')
 dic=pd.DataFrame(dictionary).merge(prof[['variavel','observado','missing','zero_registrado','municipios_observados','ano_min_observado','ano_max_observado']],on='variavel',how='left',validate='one_to_one')
 # IDs também recebem cobertura explícita.
 for c in KEY+['municipio','bioma_predominante']:
  ix=dic.variavel.eq(c);dic.loc[ix,['observado','missing','zero_registrado','municipios_observados','ano_min_observado','ano_max_observado']]=[out[c].notna().sum(),out[c].isna().sum(),0,141,2001,2024]
 assert dic.observado.notna().all();save(dic,'dicionario_variaveis.csv')
 save(pd.DataFrame([{'coluna':c,'valores_e_missing_preservados':True,'n_original':len(d),'n_v2':len(out)} for c in d]),'comparacao_original_v2.csv')
 eligibility=pd.DataFrame([{'flag':c,'elegiveis':int(v.sum()),'nao_elegiveis':int((~v).sum())} for c,v in flags.items()]);save(eligibility,'amostras_elegibilidade.csv')
 for f,h in before.items():assert sha(R/f)==h,'Fonte/rodada alterada: '+f
 assert sha(P/'PLANO_DECISOES.md')==plan_hash
 status={'linhas_mestre':len(out),'colunas_mestre':len(out.columns),'colunas_originais':70,'colunas_adicionadas':len(out.columns)-70,'linhas_quarentena':len(q),'colunas_candidatas':len(q.columns)-4,'municipios':141,'anos':[2001,2024],'join':'one_to_one, todas as3384chaves em ambos','colunas_comuns_conferidas':len(compare),'colunas_originais_preservadas':True,'fontes_rodadas_preservadas':True,'imputacao_nos_dados':False,'regressoes':False,'parquet':parquet,'plano_sha256':plan_hash,'csv_original_sha256':sha(SOURCE),'pt_sha256':sha(PT),'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'origin_main':subprocess.check_output(['git','rev-parse','origin/main'],cwd=R,text=True).strip(),'custos':'fontes CONAB referenciadas ausentes localmente e em origin/main','limitacao':'Validação interna/documental; fonte bruta não reconstituída; origem estrutural dos zeros não certificada.'}
 (P/'AUDITORIA_QUALIDADE.json').write_text(json.dumps(status,indent=2,ensure_ascii=False));(P/'FONTES_PROTEGIDAS_SHA256.json').write_text(json.dumps(before,indent=2))
 versions={'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__,'pyarrow':__import__('pyarrow').__version__ if importlib.util.find_spec('pyarrow') else None};(P/'VERSOES.json').write_text(json.dumps(versions,indent=2))
 print(json.dumps(status,indent=2,ensure_ascii=False));print(eligibility.to_string(index=False))
if __name__=='__main__':main()
