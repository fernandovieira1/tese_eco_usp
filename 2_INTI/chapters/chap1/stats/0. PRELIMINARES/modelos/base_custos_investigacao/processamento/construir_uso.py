"""Base larga de referências: divergência estritamente >10%, por conceito.
Não reestima modelos. Todos os valores oficiais permanecem literais.
"""
from pathlib import Path
from decimal import Decimal
import csv,json,hashlib,argparse,unicodedata
P=Path(__file__).resolve().parents[1];H=P/'historico/v1_publicada'
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rows,fields=None):
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def comparar(oficial,componentes):
 if oficial in ('',None) or componentes in ('',None):return {'excluir':False,'relativa':'','motivo':'comparacao_indisponivel'}
 o,c=Decimal(str(oficial)),Decimal(str(componentes))
 if o<0 or c<0:return {'excluir':True,'relativa':'','motivo':'valor_negativo_incompativel'}
 if o==0:return {'excluir':c!=0,'relativa':'','motivo':'oficial_zero_componentes_positivos' if c!=0 else 'ambos_zero'}
 delta=abs(c-o)/abs(o)
 return {'excluir':delta>Decimal('.10'),'relativa':str(delta),'motivo':'divergencia_acima_10pct' if delta>Decimal('.10') else 'divergencia_ate_10pct' if delta else 'concordante'}
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s).upper() if c.isalnum())
def construir(out=P):
 out=Path(out)
 # Validate every preserved non-cache file before deriving the current selection.
 for entry in read(P/'auditoria/mapa_reorganizacao.csv'):
  if '__pycache__' not in entry['depois'] and not entry['depois'].endswith('.pyc'):
   assert sha(P/entry['depois'])==entry['sha256'],entry['depois']
 for folder in ('BASE_PARA_USO','resultados','auditoria'): (out/folder).mkdir(parents=True,exist_ok=True)
 cross={norm(r['nome']):r for r in read(H/'regionalizacao/fontes/mt_regioes_141_compacto.csv')}
 def base(id,fonte,atividade,sistema,local,periodo,inicio,fim,ano,natureza,scope,unidade,aba,geoalert=''):
  c=cross.get(norm(local),{}) if not geoalert else {}
  return {'0_id_referencia':id,'0_fonte':fonte,'0_atividade':atividade,'0_sistema_tecnologia':sistema,'0_localidade_literal':local,'0_aba_origem':aba,'0_periodo_literal':periodo,'0_safra_inicio':inicio,'0_safra_fim':fim,'0_ano_rotulo':ano,'0_natureza':natureza,'0_unidade_custo':unidade,'0_snapshot':'2026-10-24','0_codigo_ibge_referencia':c.get('codigoIBGE',''),'0_mesorregiao_ibge':c.get('mesonome',''),'0_vintage_ibge':'DTB2016v2' if c else '', '0_regiao_imea':c.get('regiaoIMEA',''),'4_alerta_geografia':geoalert or ('referencia_estadual' if local=='MATO GROSSO' else ''),'4_recorte_2001_2024':scope,'4_custo_municipal_observado':False,'4_validacao_transferencia':False,'4_limites_territoriais_verificados':False}
 codes=['conab_'+x.lower() for x in 'ABCDEFGHIJ']+['imea_coe','imea_cot','imea_ct']
 def blank(r,codes):
  for c in codes:r.update({f'2_{c}_nominal':'',f'2_{c}_usd2024':'',f'4_{c}_elegivel_nominal':False,f'4_{c}_motivos':'conceito_nao_aplicavel_a_fonte',f'4_{c}_elegivel_usd2024':False})
 ag=[];audit=[];old={};by={};duplicatas=[]
 for r in read(H/'custos_referencia_completos.csv'):by.setdefault(r['0_id_serie'],{})[r['0_conceito_original']]=r
 meta={r['id_serie']:r for r in read(H/'fontes/metadados_series.csv')};comps={}
 for x in read(H/'auditoria_componentes.csv'):comps.setdefault(x['0_id_serie'],{})[x['0_bloco_conab']]=x
 # Recompute available sums with Decimal from the preserved item text, not prior float residuals.
 item_sums={}
 for item in read(H/'componentes_nominais.csv'):
  key=(item['0_id_serie'],item['0_bloco_conab'])
  if item['4_cabecalho_sem_valor_com_subitens']=='True':continue
  if item['4_valor_valido']!='True':continue
  raw=item['2_texto_original'].strip().replace(' ','')
  if ',' in raw:raw=raw.replace('.','').replace(',','.')
  item_sums[key]=item_sums.get(key,Decimal(0))+Decimal(raw)
 sacks={(r['id_serie'],r['conceito']):r['valor'] for r in read(H/'fontes/custos_agregados_longos.csv') if r['unidade']=='BRL_nominal/60kg'}
 for sid,values in by.items():
  m=meta[sid];sample=values['H'];r=base(sid,'CONAB',m['cultura'],m['tecnologia'],m['praca_cabecalho'],m['safra_texto']+' | '+m['data_base'],m['safra_inicio'],m['safra_fim'],m['ano_data_base'],'estimado/modal; ex-ant='+m['ex_ant'],m['elegivel_periodo_2001_2024']=='True','BRL nominal/ha',m['aba'],'localidade_ambigua' if m['conflito_praca']=='True' or m['praca_ambigua']=='True' else '')
  r['0_data_base']=m['data_base'];r['4_estrito_anterior']=sample['4_elegivel_estrito_nominal'];r['4_alertas_fonte']='';blank(r,codes)
  for concept,x in values.items():
   checks=[]
   leaves={'A':'A','B':'B','C':'C','D':'ABC','E':'E','F':'F','G':'EF','H':'ABCEF','I':'I','J':'ABCEFI'}[concept]
   eligible=all(comps[sid][k]['4_verificacao_completa']=='True' for k in leaves)
   total=sum(item_sums[sid,k] for k in leaves) if eligible else None
   checks.append(('folhas_exclusivas_'+leaves,comparar(x['2_custo_brl_nominal_ha'],total)))
   if concept in {'D':'ABC','G':'EF','H':'DG','J':'HI'}:
    terms={'D':'ABC','G':'EF','H':'DG','J':'HI'}[concept];s=sum(Decimal(values[k]['2_custo_brl_nominal_ha']) for k in terms);checks.append(('identidade_'+terms,comparar(x['2_custo_brl_nominal_ha'],s)))
   # Cross-unit comparison is audited separately; no arbitrary preference for rounded sack values.
   sack=sacks.get((sid,concept));unitcheck=(((Decimal(sack)*Decimal(m['produtividade_kg_ha']))/60) if sack is not None and m['produtividade_kg_ha'] else None)
   checks.append(('equivalencia_60kg_ha',comparar(x['2_custo_brl_nominal_ha'],unitcheck)))
   for method,ch in checks:audit.append({'fonte':'CONAB','id':sid,'conceito':concept,'comparacao':method,'oficial':x['2_custo_brl_nominal_ha'],'soma_componentes':str(total) if method.startswith('folhas') and total is not None else '',**ch})
   bad=[ch['motivo'] for _,ch in checks if ch['excluir']];flags=sorted({ch['motivo'] for _,ch in checks if ch['motivo'] not in ('concordante','ambos_zero')})
   code='conab_'+concept.lower();r[f'2_{code}_nominal']=x['2_custo_brl_nominal_ha'];r[f'2_{code}_usd2024']=x['2_custo_usd2024_ha'];r[f'4_{code}_elegivel_nominal']=not bad;r[f'4_{code}_motivos']=';'.join(flags);r[f'4_{code}_elegivel_usd2024']=not bad and bool(x['2_custo_usd2024_ha']);old[sid,code]=x['4_elegivel_estrito_nominal']=='True'
  ag.append(r)
 imea={}
 for x in read(H/'custos_imea_referencia.csv'):imea.setdefault(x['0_id_serie'],[]).append(x)
 for sid,values in imea.items():
  x=values[0];r=base(sid,'IMEA',x['0_cultura'],x['0_tecnologia_rotulo_original'],x['0_localidade_original'],x['0_safra_rotulo_original']+' | '+x['0_periodo_rotulo_original'],x['0_safra_inicio'],x['0_safra_fim'],x['0_ano_rotulo_original'],x['0_natureza_rotulo_original'],x['4_safra_alvo_2001_2024']=='True','R$/ha conforme fonte',x['0_aba']);r['0_data_base']=x['0_mes_referencia_rotulo'];r['4_estrito_anterior']=False;r['4_alertas_fonte']='sem_equivalencia_CONAB;data_nominal_consolidada_nao_confirmada;componentes_nao_conferidos'+(';asterisco_ambiguo' if x['4_rotulo_asterisco_ambiguo']=='True' else '');blank(r,codes)
  for x in values:
   c='imea_'+x['0_conceito_original'].lower();v=x['2_custo_brl_declarado_ha'];num=x['4_valor_numerico']=='True';negative=num and Decimal(v)<0
   r[f'2_{c}_nominal']=v if num else '';r[f'4_{c}_elegivel_nominal']=num and not negative;r[f'4_{c}_motivos']='valor_negativo_incompativel' if negative else 'NA_fonte' if not num else 'componentes_nao_conferidos;sem_comparabilidade_interfontes';old[sid,c]=x['4_candidato_descritivo_rotulo']=='True'
  ag.append(r)
 cattle=[]
 for x in read(H/'pecuaria/registros_periodo.csv'):
  sid=x['sheet_id']+'_'+x['column'];r=base(sid,'IMEA', 'pecuaria',x['system_key'],x['geography'],x['reference_period_from_labels'], '', '',x['year_label'],x['natureza_from_labels'],2001<=int(x['year_label'])<=2024,'R$/@ vendida',x['sheet_name'],x['geography_warning']);r['2_produtividade_modal_arrobas_vendidas_ha']=x['modal_productivity'];r['4_alertas_fonte']='notas_editoriais_preservadas;componentes_nao_extraidos;sem_conversao_ha';blank(r,['coe','cot','ct'])
  for c in ('coe','cot','ct'):
   v=x[c];num=x[c+'_type']=='n' and v!='';bad=num and Decimal(v)<0;r[f'2_{c}_nominal']=v;r[f'4_{c}_elegivel_nominal']=num and not bad;r[f'4_{c}_motivos']='valor_negativo_incompativel' if bad else 'NA_fonte' if not num else 'componentes_nao_extraidos;sem_conversao_usd2024'
  cattle.append(r)
 # Consolidate exact equivalent published references; source copies remain in all-period output.
 ag_uso=[];seen={}
 for r in ag:
  r['0_ids_origem']=r['0_id_referencia'];r['4_duplicata_consolidada']=False
  if not r['4_recorte_2001_2024']:continue
  key=tuple(r[k] for k in ('0_fonte','0_atividade','0_sistema_tecnologia','0_localidade_literal','0_periodo_literal'))
  if key in seen and all(seen[key][k]==r[k] for k in r if k.startswith('2_')):
   existing=seen[key];existing['0_ids_origem']+=';'+r['0_id_referencia'];existing['4_duplicata_consolidada']=True
   existing['4_alertas_fonte']+=';duplicata_identica_entre_abas_geografia_nao_resolvida';existing['0_aba_origem']+=' | '+r['0_aba_origem']
   existing['4_alerta_geografia']='duplicata_com_conflito_entre_aba_e_cabecalho'
   for k in ('0_codigo_ibge_referencia','0_mesorregiao_ibge','0_vintage_ibge','0_regiao_imea'):existing[k]=''
   duplicatas.append({'id_mantido':existing['0_id_referencia'],'id_copia':r['0_id_referencia'],'motivo':'metadados_de_referencia_e_todos_valores_monetarios_identicos;conflito_aba_preservado'})
  else:
   seen[key]=dict(r);ag_uso.append(seen[key])
 for rows,name in [(ag,'agricultura'),(cattle,'pecuaria')]:
  assert len({r['0_id_referencia'] for r in rows})==len(rows)
  write(out/'resultados'/f'{name}_todos_periodos.csv',rows)
  write(out/'BASE_PARA_USO'/f'CUSTOS_{name.upper()}.csv',ag_uso if name=='agricultura' else [r for r in rows if r['4_recorte_2001_2024']])
 write(out/'auditoria/comparacoes_por_conceito.csv',audit)
 write(out/'auditoria/duplicatas_consolidadas.csv',duplicatas,['id_mantido','id_copia','motivo'])
 differences=[]
 for r in ag:
  if not r['4_recorte_2001_2024']:continue
  for c in codes:
   if (r['0_id_referencia'],c) not in old:continue
   now=r[f'4_{c}_elegivel_nominal'];prev=old[r['0_id_referencia'],c]
   if now!=prev:differences.append({'fonte':r['0_fonte'],'id':r['0_id_referencia'],'conceito':c,'anterior':prev,'atual':now,'motivos':r[f'4_{c}_motivos']})
 write(out/'auditoria/diferencas_elegibilidade.csv',differences)
 summary={'regra':'abs(componentes-oficial)/abs(oficial) > 0.10; zero tratado separadamente','agricultura':{},'pecuaria':{},'nao_reestimado':True}
 for rows,name in [(ag,'agricultura'),(cattle,'pecuaria')]:
  selected=[r for r in rows if r['4_recorte_2001_2024']];cols=[k for k in rows[0] if k.startswith('2_') and k.endswith('_nominal')]
  summary[name]={'total_referencias':len(rows),'recorte_2001_2024':len(selected),'fora_recorte':len(rows)-len(selected),'conceitos_presentes_recorte':sum(r[k]!='' for r in selected for k in cols),'conceitos_elegiveis_recorte':sum(r[k.replace('2_','4_',1).replace('_nominal','_elegivel_nominal')] for r in selected for k in cols),'referencias_sem_custos':sum(not any(r[k]!='' for k in cols) for r in selected)}
 summary['agricultura']['linhas_principais_sem_duplicatas']=len(ag_uso);summary['duplicatas_consolidadas']=duplicatas
 summary['comparacoes_excludentes']=[x for x in audit if x['excluir']];summary['recuperados_por_fonte']={f:{'conceitos':sum(r['fonte']==f and r['atual'] for r in differences),'referencias':len({r['id'] for r in differences if r['fonte']==f and r['atual']})} for f in ('CONAB','IMEA')}
 (out/'auditoria/resumo.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 definitions={'a':'custeio da lavoura','b':'outras despesas/pós-colheita','c':'despesas financeiras','d':'custo variável A+B+C','e':'depreciações','f':'outros custos fixos','g':'custo fixo E+F','h':'custo operacional D+G','i':'renda dos fatores','j':'custo total H+I','coe':'custo operacional efetivo, definição IMEA','cot':'custo operacional total, definição IMEA','ct':'custo total, definição IMEA'}
 dictionary=[]
 for rows,name in [(ag,'agricultura'),(cattle,'pecuaria')]:
  for col in rows[0]:
   desc='Metadado literal de origem ou indicador de referência; não é observação municipal.'
   if col.startswith('2_'):
    concept=col.split('_')[-2];desc=definitions.get(concept,'produtividade modal em @vendida/ha, não converter custos')
    desc+='; valor oficial preservado; vazio é NA ou coluna não aplicável à fonte.'
    if col.endswith('_usd2024'):desc+=' USD de poder de compra2024; BRL/câmbio mensal×CPI2024/CPImês. Não aplicar a IMEA com data incerta.'
    elif col.endswith('_nominal'):desc+=' Unidade original porha (agricultura) ou por@vendida (pecuária), sem equivalência entre fontes.'
   if '_elegivel_' in col:desc='True se valor presente e sem incompatibilidade quantitativa >10% ou qualitativa demonstrada. USD exige conversão disponível. Não implica auditoria completa/transferência municipal.'
   if '_motivos' in col:desc='concordante/ambos_zero não geram restrição; divergencia_ate_10pct e comparacao_indisponivel são alertas; divergencia_acima_10pct/oficial_zero_componentes_positivos excluem somente o conceito afetado; NA_fonte é ausência; conceito_nao_aplicavel_a_fonte não é dado faltante daquela instituição.'
   if col=='0_id_referencia':desc='Chave única da linha de referência; inclui identidade do documento/aba/coluna. Não é código municipal.'
   if col=='0_ids_origem':desc='IDs originais separados por ponto e vírgula quando cópias documentais equivalentes são consolidadas.'
   if col=='4_estrito_anterior':desc='Seleção histórica rigorosa, preservada como robustez. Não determina elegibilidade atual.'
   if col=='4_recorte_2001_2024':desc='Safra agrícola integral dentro2001–2024; pecuária pelo ano literal. Fora do recorte não significa dado incorreto.'
   if col=='4_alerta_geografia':desc='Ambiguidade/conflito de geografia ou referência estadual; não resolver como município por inferência.'
   if col=='4_alertas_fonte':desc='Ressalvas metodológicas, componentes não conferidos, asterisco ou duplicata; não são exclusões automáticas.'
   dictionary.append({'arquivo':f'CUSTOS_{name.upper()}.csv','coluna':col,'descricao':desc,'grupo':col.split('_')[0]})
 write(out/'BASE_PARA_USO/DICIONARIO.csv',dictionary)
 (out/'auditoria/manifesto_build.json').write_text(json.dumps({'historico':'v1_publicada','outputs':{str(f.relative_to(out)):sha(f) for folder in ('BASE_PARA_USO','resultados','auditoria') for f in sorted((out/folder).glob('*.csv')) if f.name!='mapa_reorganizacao.csv'}},ensure_ascii=False,indent=2)+'\n')
 return summary
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=P);print(json.dumps(construir(ap.parse_args().out),ensure_ascii=False,indent=2))
