"""Avaliação e referências candidatas paralelas, sem escrita na H1. Python stdlib."""
import csv,json,hashlib,math,statistics as st,argparse,re,unicodedata
from pathlib import Path
from collections import defaultdict,Counter
P=Path(__file__).resolve().parent;F=P/'fontes'
def read(f):
 with Path(f).open(encoding='utf-8',newline='') as s:return list(csv.DictReader(s))
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def slug(x):return re.sub(r'[^a-z0-9]+','_',unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().lower()).strip('_')
def ident(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False).encode()).hexdigest()[:12]
def write(p,rows,fields=None):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as s:
  w=csv.DictWriter(s,fieldnames=fields or (list(rows[0]) if rows else ['status']),lineterminator='\n');w.writeheader();w.writerows(rows)
def js(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def sources():
 m=json.loads((P/'proveniencia.json').read_text())
 for f,h in m['inputs'].items():assert sha(F/f)==h,f
 return read(F/'CUSTOS_AGRICULTURA.csv'),read(F/'CUSTOS_PECUARIA.csv')
def predictors():
 cp={r['observation_date'][:7]:float(r['CPIAUCNS']) for r in read(F/'cpi.csv')};base=st.mean(v for k,v in cp.items() if k.startswith('2024-'));dap=read(F/'dap.csv');out={}
 for y in range(2000,2024):
  r=[r for r in dap if r['date'].startswith(str(y))];assert len(r)==12
  out[y+1]=math.log(st.mean(float(x['value'])*base/cp[x['date'][:7]] for x in r))
 return out
MODELS=['B0_media_regional','M1_ols','M2_ridge']
def estimate(rows,model):
 xm=st.mean(r['x'] for r in rows);ym=st.mean(r['y'] for r in rows);sd=st.pstdev(r['x'] for r in rows);assert sd>0
 z=[(r['x']-xm)/sd for r in rows];b=0 if model==MODELS[0] else sum(z*(r['y']-ym) for z,r in zip(z,rows))/(sum(z*z for z in z)+(model==MODELS[2]))
 return ym,b,xm,sd
def evaluate(a,label):
 folds=[];pred=[];members=[];params=[]
 support=len(a)>=24 and len({r['place'] for r in a})>=3 and len({r['year'] for r in a})>=10
 if support:
  specs=[('espacial',place,[r for r in a if r['place']!=place],[r for r in a if r['place']==place]) for place in sorted({r['place'] for r in a})]
  specs += [('temporal',f'{cut+1}-{end}',[r for r in a if r['year']<=cut],[r for r in a if cut<r['year']<=end]) for cut,end in [(2015,2019),(2019,2021),(2021,2024)]]
  for axis,block,tr,te in specs:
   reasons=[]
   for ok,name in [(len(tr)>=12,'treino12'),(len({r['place'] for r in tr})>=2,'duas_pracas'),(len(te)>=4,'teste4'),(len({r['x'] for r in tr})>=2,'variancia_x')]:
    if not ok:reasons.append(name)
   folds.append(dict(analise=label,eixo=axis,bloco=block,n_treino=len(tr),n_teste=len(te),admissivel=not reasons,motivos=';'.join(reasons)))
   if reasons:continue
   assert not {r['id'] for r in tr}&{r['id'] for r in te}
   if axis=='temporal':assert max(r['year'] for r in tr)<min(r['year'] for r in te)
   else:assert not {r['place'] for r in tr}&{r['place'] for r in te}
   members.extend(dict(analise=label,eixo=axis,bloco=block,papel=role,id=r['id'],ano=r['year'],praca=r['place']) for role,rr in [('treino',tr),('teste',te)] for r in rr)
   for model in MODELS:
    ym,b,xm,sd=estimate(tr,model);params.append(dict(analise=label,eixo=axis,bloco=block,modelo=model,media_y=ym,beta=b,media_x=xm,sd_x=sd))
    for r in te:
     yh=ym+b*(r['x']-xm)/sd
     pred.append(dict(analise=label,eixo=axis,bloco=block,modelo=model,id=r['id'],observado=r['y'],previsto=yh,erro=yh-r['y'],negativo=yh<0,extrapola=not min(x['x'] for x in tr)<=r['x']<=max(x['x'] for x in tr)))
 metrics=[];gates=[]
 for axis in ['espacial','temporal']:
  for block in ['TODOS']+sorted({r['bloco'] for r in pred if r['eixo']==axis}):
   for model in MODELS:
    b=[r for r in pred if r['eixo']==axis and r['modelo']==model and (block=='TODOS' or r['bloco']==block)]
    if not b:continue
    metrics.append(dict(analise=label,eixo=axis,bloco=block,modelo=model,n=len(b),folds=len({r['bloco'] for r in b}),mae=st.mean(abs(r['erro']) for r in b),rmse=math.sqrt(st.mean(r['erro']**2 for r in b)),bias=st.mean(r['erro'] for r in b),sd_erro=st.pstdev(r['erro'] for r in b),media_alvo=st.mean(r['observado'] for r in b),negativos=sum(r['negativo'] for r in b),extrapola=sum(r['extrapola'] for r in b)))
  for model in MODELS[1:]:
   by={(r['bloco'],r['modelo']):r for r in metrics if r['eixo']==axis};m=by.get(('TODOS',model));b=by.get(('TODOS',MODELS[0]));checks={}
   if m:
    checks={'dois_folds':m['folds']>=2,'ganho10':m['mae']<=.9*b['mae'],'mae20':m['mae']<=.2*m['media_alvo'],'bias10':abs(m['bias'])<=.1*m['media_alvo'],'negativos0':m['negativos']==0,'pior_fold125':all(r['mae']<=1.25*by[r['bloco'],MODELS[0]]['mae'] for r in metrics if r['eixo']==axis and r['modelo']==model and r['bloco']!='TODOS')}
   gates.append(dict(analise=label,eixo=axis,modelo=model,passou=bool(checks) and all(checks.values()),falhas=';'.join(k for k,v in checks.items() if not v) if checks else 'suporte_ou_folds_insuficientes'))
 approved=[m for m in MODELS[1:] if all(g['passou'] for g in gates if g['modelo']==m)]
 summary=dict(analise=label,n=len(a),pracas=len({r['place'] for r in a}),anos=len({r['year'] for r in a}),suporte=support,aprovados=';'.join(approved),municipal_validado=False,decisao='suporte_insuficiente' if not support else 'gate_passou_somente_polos' if approved else 'gate_nao_passou')
 return summary,folds,pred,members,params,metrics,gates

def etapa1(out):
 ag,pec=sources();x=predictors();samples=[];losses=[]
 for r in ag:
  if r['0_fonte']!='CONAB':continue
  reasons=[];year=int(r['0_data_base'][:4])
  if not r['0_codigo_ibge_referencia'] or r['4_alerta_geografia']:reasons.append('geografia_nao_resolvida')
  if r['4_conab_h_elegivel_usd2024']!='True' or not r['2_conab_h_usd2024']:reasons.append('USD_H_indisponivel')
  if year not in x:reasons.append('preditor_indisponivel')
  if reasons:losses.append(dict(id=r['0_id_referencia'],cultura=r['0_atividade'],motivos=';'.join(reasons)));continue
  assert f'{year-1}-12'<r['0_data_base'][:7]
  samples.append(dict(id=r['0_id_referencia'],crop=r['0_atividade'],technology=r['0_sistema_tecnologia'],place=r['0_codigo_ibge_referencia'],year=year,x=x[year],y=float(r['2_conab_h_usd2024']),strict=r['4_estrito_anterior']=='True',nature=r['0_natureza']))
 allout=[[] for _ in range(7)]
 for crop in ['soja','milho_1a','milho_2a']:
  a=[r for r in samples if r['crop']==crop]
  sets=[('ampliada_comparativa_pooled',a),('estrita_robustez_pooled',[r for r in a if r['strict']])]
  sets += [('ampliada_sistema_'+tech,[r for r in a if r['technology']==tech]) for tech in sorted({r['technology'] for r in a})]
  for name,rows in sets:
   outputs=evaluate(rows,crop+'__'+name)
   allout[0].append(outputs[0])
   for i,items in enumerate(outputs[1:],1):allout[i].extend(items)
 dest=out/'resultados/avaliacao';write(dest/'amostra.csv',samples);write(dest/'perdas.csv',losses)
 for name,rows in zip(['resumo','folds','previsoes','membros','parametros','metricas','gates'],allout):write(dest/(name+'.csv'),rows)
 ps=[]
 for system in sorted({r['0_sistema_tecnologia'] for r in pec}):
  a=[r for r in pec if r['0_sistema_tecnologia']==system and r['0_codigo_ibge_referencia'] and not r['4_alerta_geografia'] and r['2_coe_nominal'] and r['0_natureza']=='consolidado_conforme_rotulo']
  ps.append(dict(sistema=system,n=len(a),pracas=len({r['0_codigo_ibge_referencia'] for r in a}),anos=len({r['0_ano_rotulo'] for r in a}),unidade='R$/arroba vendida',decisao='nao_estimar: menos10anos e sem preditor pecuario validado'))
 write(dest/'pecuaria_suporte.csv',ps)
 return allout[0],ps

# Concepts kept separate in columns; no cross-source equivalence.
CONCEPTS={'CONAB':['conab_h'],'IMEA_agricola':['imea_coe','imea_cot','imea_ct'],'IMEA_pecuaria':['coe','cot','ct']}
METRICS=['mediana','n_referencias','n_pracas','minimo','maximo','iqr','atribuivel','confiabilidade']
def etapa23(out):
 ag,pec=sources();cross={r['codigoIBGE']:r for r in read(F/'regioes.csv')};idx=read(F/'indices_h1.csv');assert len(idx)==3384
 assert len({(r['0_codigo_ibge'],r['0_ano']) for r in idx})==3384 and len({r['0_codigo_ibge'] for r in idx})==141
 assert all(r['0_codigo_ibge'] in cross for r in idx)
 groups=defaultdict(list);excluded=[];catalog={}
 for kind,rows in [('agricola',ag),('pecuaria',pec)]:
  for r in rows:
   source=r['0_fonte'] if r['0_fonte']=='CONAB' else 'IMEA_'+kind
   activity=r['0_atividade'] if not (kind=='agricola' and r['0_fonte']=='IMEA' and r['0_atividade']=='milho') else 'milho_safra_nao_harmonizada'
   # Separate source, system, nature and agricultural season length. Ex-Ant provenance is retained, not a separate technology.
   nature='estimado_modal' if source=='CONAB' else r['0_natureza']
   start=r['0_safra_inicio'];end=r['0_safra_fim'];year=end if kind=='agricola' else r['0_ano_rotulo']
   duration=int(end)-int(start) if start and end else 0
   key=(source,activity,r['0_sistema_tecnologia'],nature,duration)
   sid=ident(key);catalog[sid]=dict(serie=sid,fonte=source,atividade=activity,sistema=r['0_sistema_tecnologia'],natureza=nature,duracao_safra=duration,unidade='R$/ha e USD2024/ha quando disponível' if kind=='agricola' else 'R$/arroba vendida',regra_ano='fim_da_safra' if kind=='agricola' else 'ano_consolidado')
   reasons=[];code=r['0_codigo_ibge_referencia']
   if not code or r['4_alerta_geografia']:reasons.append('sem_geografia_inequivoca_ou_estadual')
   if code and code not in cross:reasons.append('codigo_sem_crosswalk')
   if 'asterisco_ambiguo' in r['4_alertas_fonte']:reasons.append('safra_asterisco_ambiguo_nao_alinhar')
   if kind=='pecuaria' and nature!='consolidado_conforme_rotulo':reasons.append('periodo_nao_anual_consolidado')
   if not year or not 2001<=int(year)<=2024:reasons.append('ano_nao_suportado')
   if reasons:excluded.append(dict(id=r['0_id_referencia'],serie=sid,motivos=';'.join(reasons)));continue
   meso=cross[code]['mesocodigo'];groups[sid,meso,int(year)].append(r)
 refs=[];lineage=[];statscols=sorted({c+'_'+currency for concepts in CONCEPTS.values() for c in concepts for currency in ['nominal','usd2024']})
 for (sid,meso,year),rows in sorted(groups.items()):
  cat=catalog[sid];refid=ident([sid,meso,year]);ref={'id_referencia_regional':refid,**cat,'mesocodigo':meso,'ano_alinhado':year,'safras_originais':'|'.join(sorted({r['0_safra_inicio']+'/'+r['0_safra_fim'] for r in rows if r['0_safra_inicio']})),'data_base_min':min((r.get('0_data_base','') for r in rows),default=''),'data_base_max':max((r.get('0_data_base','') for r in rows),default=''),'n_referencias_total':len(rows),'n_pracas_total':len({r['0_codigo_ibge_referencia'] for r in rows}),'metodo':'mediana_das_medianas_por_praca_peso_igual','ids_origem':'|'.join(r['0_ids_origem'] if r.get('0_ids_origem') else r['0_id_referencia'] for r in rows),'naturezas_originais':'|'.join(sorted({r['0_natureza'] for r in rows})),'alertas_origem':'|'.join(sorted({r['4_alertas_fonte'] for r in rows})),'disponivel_exante_validado':False,'limites_territoriais_verificados':False}
  for metric in statscols:
   for stat in METRICS:ref[metric+'_'+stat]=''
  for concept in CONCEPTS[cat['fonte']]:
   for currency in ['nominal','usd2024']:
    col=concept+'_'+currency;places=defaultdict(list);n=0
    for r in rows:
     val=r['2_'+col];ok=r.get('4_'+concept+'_elegivel_'+currency)=='True'
     if not val or not ok:continue
     assert math.isfinite(float(val)) and float(val)>=0
     places[r['0_codigo_ibge_referencia']].append(float(val));n+=1
     lineage.append(dict(id_referencia_regional=refid,serie=sid,id_origem=r['0_id_referencia'],praca=r['0_codigo_ibge_referencia'],mesocodigo=meso,ano_alinhado=year,conceito=concept,moeda=currency,valor=val,flag_qualidade=r['4_'+concept+'_motivos']))
    values=sorted(st.median(v) for v in places.values());np=len(values)
    if not np:continue
    q=st.quantiles(values,n=4,method='inclusive') if np>1 else [values[0]]*3
    vals=dict(mediana=st.median(values),n_referencias=n,n_pracas=np,minimo=min(values),maximo=max(values),iqr=q[2]-q[0],atribuivel=np>=2,confiabilidade='limitada_duas_pracas' if np==2 else 'mais_pracas_nao_representatividade' if np>=3 else 'pontual_nao_atribuir')
    ref.update({col+'_'+k:v for k,v in vals.items()})
  refs.append(ref)
 write(out/'USO_CANDIDATOS/REFERENCIAS_REGIONAIS.csv',refs)
 write(out/'resultados/linhagem_regional.csv',lineage);write(out/'resultados/nao_regionalizados.csv',excluded)
 lookup={(r['serie'],r['mesocodigo'],r['ano_alinhado']):r for r in refs};mesos=sorted({r['mesocodigo'] for r in cross.values()});coverage=[];candidates=[];panel=[]
 eligible_series={sid:cat for sid,cat in catalog.items() if any(r['serie']==sid for r in refs)}
 for sid,cat in sorted(eligible_series.items()):
  for concept in CONCEPTS[cat['fonte']]:
   for currency in ['nominal','usd2024']:
    if currency=='usd2024' and cat['fonte']!='CONAB':continue
    cname='2_custo_'+slug(cat['fonte']+'_'+cat['atividade']+'_'+cat['sistema'])+'_safra'+str(cat['duracao_safra'])+'_'+concept+'_'+currency
    cells=0
    for meso in mesos:
     nmun=sum(r['mesocodigo']==meso for r in cross.values())
     for year in range(2001,2025):
      ref=lookup.get((sid,meso,year));metric=concept+'_'+currency
      ok=bool(ref and ref[metric+'_atribuivel'] is True);np=ref[metric+'_n_pracas'] if ref else 0
      cells+=ok*nmun
      coverage.append(dict(variavel=cname,serie=sid,atividade=cat['atividade'],sistema=cat['sistema'],fonte=cat['fonte'],conceito=concept,moeda=currency,mesocodigo=meso,ano=year,municipios_alvo=nmun,municipios_atribuidos=nmun if ok else 0,cobertura_pct=100 if ok else 0,n_pracas=np or 0,status='referencia_atribuivel' if ok else 'referencia_pontual_ou_sem_valor' if ref else 'sem_referencia'))
    candidates.append(dict(variavel=cname,**cat,conceito=concept,moeda=currency,municipio_anos_atribuidos=cells,total=3384,cobertura_pct=100*cells/3384,recomendacao='candidata_descritiva_requer_aprovacao' if cells else 'nao_incorporar_sem_suporte',limite='proxy_regional_nao_observado;sem_validacao_exante;sem_validacao_municipal'))
 for original in idx:
  r=dict(original);code=r['0_codigo_ibge'];meso=cross[code]['mesocodigo'];year=int(r['0_ano'])
  r.update({'4_mesorregiao_ibge2016_codigo':meso,'4_mesorregiao_ibge2016_nome':cross[code]['mesonome'],'4_regiao_imea2017_informativa':cross[code]['regiaoIMEA'],'4_aproximacao_regional':True,'4_incorporacao_aprovada':False,'4_limites_territoriais_verificados':False,'4_disponivel_exante_validado':False})
  for c in candidates:
   sid=c['serie'];metric=c['conceito']+'_'+c['moeda'];name=c['variavel'];ref=lookup.get((sid,meso,year));ok=bool(ref and ref[metric+'_atribuivel'] is True);suffix=name[2:]
   r[name]=ref[metric+'_mediana'] if ok else ''
   r['4_'+suffix+'_status']='aproximacao_regional' if ok else 'suporte_insuficiente' if ref else 'sem_referencia'
   r['4_'+suffix+'_id_ref']=ref['id_referencia_regional'] if ref else ''
   for field in ['n_pracas','n_referencias','iqr','confiabilidade']:r['4_'+suffix+'_'+field]=ref[metric+'_'+field] if ref else ''
  panel.append(r)
 write(out/'USO_CANDIDATOS/PAINEL_MUNICIPAL_CANDIDATO.csv',panel);write(out/'resultados/cobertura_regiao_atividade_ano.csv',coverage);write(out/'resultados/lista_candidatas.csv',candidates)
 dictionary=[]
 for c in candidates:dictionary.append(dict(variavel=c['variavel'],fonte=c['fonte'],atividade=c['atividade'],sistema=c['sistema'],conceito=c['conceito'],moeda=c['moeda'],unidade='USD2024/ha' if c['moeda']=='usd2024' else 'R$/arroba vendida' if c['atividade']=='pecuaria' else 'R$/ha',ano=c['regra_ano'],descricao='Mediana regional; >=2 praças; NA sem suporte; fonte/sistema distintos; prefixo4 correspondente registra status/id_ref/n_pracas/n_referencias/iqr/confiabilidade. Identidade regional IBGE2016, não bioma. Não é observação municipal.'))
 for col in panel[0]:
  if col.startswith('2_'):continue
  dictionary.append(dict(variavel=col,fonte='H1 v4' if col.startswith('0_') else 'derivado',atividade='',sistema='',conceito='',moeda='',unidade='',ano='',descricao='Índice original preservado' if col.startswith('0_') else 'Flag ou metadado da atribuição; id_ref aponta à tabela regional; n_pracas são unidades informativas, municípios replicados não são independentes; IQR mesma unidade do custo.'))
 for col in refs[0]:
  description='Metadado da referência: fonte, sistema, natureza, período e linhagem preservados; mesocodigo corresponde a IBGE DTB2016v2.'
  if col.endswith('_mediana'):description='Mediana das medianas por praça; unidade e moeda definidas pelo conceito e sufixo. Não ponderada por produção.'
  elif col.endswith('_n_pracas'):description='Número de praças com valor numérico elegível neste conceito/moeda; não número de municípios que recebem a referência.'
  elif col.endswith('_n_referencias'):description='Número de referências de origem elegíveis neste conceito/moeda, antes da mediana por praça.'
  elif col.endswith(('_minimo','_maximo','_iqr')):description='Dispersão das medianas por praça, na mesma unidade do custo; IQR inclusivo, não intervalo de confiança.'
  elif col.endswith('_atribuivel'):description='True somente com pelo menos duas praças numéricas; vazio sem valores, False para praça única.'
  elif col.endswith('_confiabilidade'):description='Suporte descritivo; não valida representatividade, disponibilidade exante ou transferência municipal.'
  elif col in ('n_pracas_total','n_referencias_total'):description='Contagem bruta do grupo, incluindo linhas sem custo; usar contagens específicas por conceito/moeda para suporte.'
  dictionary.append(dict(variavel='REFERENCIAS_REGIONAIS::'+col,fonte='derivado',atividade='',sistema='',conceito='',moeda='',unidade='',ano='',descricao=description))
 write(out/'USO_CANDIDATOS/DICIONARIO.csv',dictionary)
 summary={'referencias_regionais':len(refs),'linhas_painel':len(panel),'colunas_painel':len(panel[0]),'series_regionais':len(eligible_series),'variaveis_custo':len(candidates),'variaveis_com_suporte':sum(c['municipio_anos_atribuidos']>0 for c in candidates),'nao_regionalizados':len(excluded),'ids_H1_mapeados':141,'municipal_validado':False,'incorporacao_aprovada':False}
 js(out/'resultados/resumo_regional.json',summary)
 return summary,candidates

def main(out=P):
 out=Path(out);a,pec=etapa1(out);region,candidates=etapa23(out)
 text='# Avaliação ampliada e referências regionais candidatas\n\nNenhuma incorporação à H1 autorizada. Resultados descritivos e preditivos não causais.\n\n| Análise | N | Praças | Anos | Decisão |\n|---|---:|---:|---:|---|\n'
 for r in a:text+=f"| {r['analise']} | {r['n']} | {r['pracas']} | {r['anos']} | {r['decisao']} |\n"
 text+='\nPooled é apenas comparação ao desenho anterior, não mistura tecnológica para atribuição. Avaliação primária é separada por sistema. Estrita é robustez; geografia não resolvida não define folds. Métricas e perdas completas em resultados/avaliacao. Nenhum resultado aprova previsão municipal. Pecuária não foi estimada: cinco anos consolidados no máximo, sistemas separados, sem preditor específico validado.\n\n'+json.dumps(region,ensure_ascii=False,indent=2)+'\n\n| Candidata | Cobertura município-ano % | Recomendação |\n|---|---:|---|\n'
 for c in candidates:text+=f"| {c['fonte']} / {c['atividade']} / {c['sistema']} / {c['conceito']} / {c['moeda']} | {c['cobertura_pct']:.2f} | {c['recomendacao']} |\n"
 text+='\nO painel tem todas as chaves H1, mas custos somente nos domínios com suporte. Anos de fim de safra são convenção explícita e não data de informação. Fontes retrospectivas, sistemas e moedas não intercambiáveis. Mínimo de duas praças é suporte operacional, não prova de representatividade. Mediana e IQR não são intervalo de confiança. Pequeno número de regiões exige inferência cautelosa agrupada por região e tempo; replicar custos não multiplica unidades informativas. Não usar estas colunas como custos municipais observados ou como variáveis conhecidas exante. Aprovação do autor é necessária para incorporar qualquer candidata.\n'
 (out/'RESULTADOS.md').write_text(text)
 (out/'USO_CANDIDATOS/LEIA_ME.md').write_text('# Custos candidatos — não incorporados à H1\n\nREFERENCIAS_REGIONAIS.csv contém referências por fonte, atividade, sistema, mesorregião e período, com conceitos/moedas separados. PAINEL_MUNICIPAL_CANDIDATO.csv repete referências apenas onde há pelo menos duas praças, sobre as 3.384 chaves e sete índices originais. DICIONARIO.csv identifica campos e unidades.\n\nAgricultura: R$/ha e USD2024/ha somente onde válido; pecuária R$/arroba vendida. Células vazias são NA, não zero. Custos são aproximações regionais retrospectivas, não observações municipais, bioma ou informações exante. Uma praça não autoriza atribuição. Ano agrícola é fim da safra explícita. Não misture fonte, sistema, conceito ou moedas; consulte ../RESULTADOS.md e ../resultados/lista_candidatas.csv.\n\nSomente candidatas para aprovação; a base principal não foi alterada. Faça cópias para trabalho manual: reconstrução deve usar destino vazio (--out), sem sobrescrever edições.\n')
 js(out/'manifesto_saidas.json',{str(f.relative_to(out)):sha(f) for f in sorted(out.rglob('*.csv')) if 'fontes' not in f.parts})
 return region
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=P);args=ap.parse_args()
 # All analysis outputs are only generated in a new output destination; rerun comparisons in temp directories.
 if (args.out/'USO_CANDIDATOS/PAINEL_MUNICIPAL_CANDIDATO.csv').exists():raise SystemExit('Saídas existentes: preserve suas edições; reexecute com --out em diretório vazio.')
 print(json.dumps(main(args.out),ensure_ascii=False,indent=2))
