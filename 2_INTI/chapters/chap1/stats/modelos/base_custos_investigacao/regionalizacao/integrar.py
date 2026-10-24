"""Identificação de referência e cobertura; não atribui custos aos municípios."""
from pathlib import Path
import csv,json,hashlib,unicodedata,argparse,collections
P=Path(__file__).resolve().parent;ROOT=P.parent
CROSS=P/'fontes/mt_regioes_141_compacto.csv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8',newline='')))
def norm(x):return ''.join(c for c in unicodedata.normalize('NFD',x).upper() if c.isalnum())
def write(p,rr):
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def run(out=P):
 out=Path(out);out.mkdir(exist_ok=True,parents=True)
 assert sha(CROSS)=='9c125980a292bba5e8d899155b048a4521250c15d40f564d1f8806912d37c1b1'
 cross=read(CROSS);bycode={r['codigoIBGE']:r for r in cross};byname={norm(r['nome']):r for r in cross};panelpath=ROOT.parent/'base3/painel_h1_base3_v4.csv';panel=read(panelpath);keys={r['0_codigo_ibge']:r['0_municipio'] for r in panel};assert set(keys)==set(bycode) and len(keys)==141
 ids=[]
 for k,name in sorted(keys.items()):
  c=bycode[k];ids.append({'0_codigo_ibge':k,'0_municipio_painel':name,'0_nome_dtb':c['nome'],'0_codigo_mesorregiao_ibge':c['mesocodigo'],'0_nome_mesorregiao_ibge':c['mesonome'],'0_vintage_ibge':'DTB_2016_v2','0_regiao_imea':c['regiaoIMEA'],'0_vintage_imea':'nota_2017_segmentacao_2008','4_status_match_imea':c['statusmatch'],'4_match_painel':'codigo_exato_nome_normalizado' if norm(name)==norm(c['nome']) else 'codigo_exato_divergencia_de_do_preservada','4_limites_2016_2023':'nao_verificados','4_custo_atribuido':False})
 write(out/'identificacao_regional.csv',ids)
 refs=[];inputs={str(CROSS):sha(CROSS),str(panelpath):sha(panelpath)}
 def add(source,activity,year,period,place,key,numeric,conflict='',qual=''):
  c=byname.get(norm(place)) if not conflict and place!='MATO GROSSO' else None
  refs.append({'fonte':source,'atividade':activity,'ano_rotulo':year,'periodo_literal':period,'id_referencia':key,'praca_literal':place,'codigo_ibge_referencia':c['codigoIBGE'] if c else '', 'mesocodigo':c['mesocodigo'] if c else '', 'mesonome':c['mesonome'] if c else '', 'regiao_imea':c['regiaoIMEA'] if c else '', 'status_geografia':'conflito_na_fonte' if conflict else 'estado_separado' if place=='MATO GROSSO' else 'nome_normalizado_exato' if c else 'sem_correspondencia','custos_numericos':numeric,'qualificacao':qual,'representatividade_regional_validada':False})
 for crop in ['soja','milho_1a','milho_2a']:
  path=ROOT/'avaliacao_preditiva'/crop/'amostra.csv';inputs[str(path)]=sha(path)
  for r in read(path):add('CONAB_estrita',crop,r['ano_data_base'],r['data_base'],r['praca'],r['id'],True,qual='ano_data_base_nao_ano_colheita')
 path=ROOT/'fontes/imea/imea_regional_key_costs.csv';inputs[str(path)]=sha(path)
 for r in read(path):
  numeric=True
  try:
   for m in ('coe','cot','ct'):float(r[m])
  except ValueError:numeric=False
  add('IMEA_agricola','soja_GMO' if 'soja' in r['source_file'] else 'milho_alta_tecnologia_safra_nao_harmonizada',r['year_label'],r['crop_year_label']+'|'+r['period_label'],r['geography_label'],r['sheet']+'_'+r['source_column'],numeric,qual='rotulo_original;quarentena_comparabilidade;marcadores_preservados')
 path=ROOT/'pecuaria/registros_periodo.csv';inputs[str(path)]=sha(path)
 for r in read(path):add('IMEA_pecuaria',r['system_key'],r['year_label'],r['reference_period_from_labels'],r['geography'],r['sheet_id']+'_'+r['column'],bool(r['coe']),r['geography_warning'],'R$/@ vendida;sem_conversao_ha')
 assert len(refs)==85+195+196
 write(out/'referencias_identificadas.csv',refs)
 coverage=[]
 # Complete years by source/activity and five mesoregions, including zero coverage.
 for source,activity in sorted({(r['fonte'],r['atividade']) for r in refs}):
  subset=[r for r in refs if (r['fonte'],r['atividade'])==(source,activity)]
  years=range(2001,2025) if source=='CONAB_estrita' else sorted({r['ano_rotulo'] for r in subset})
  for year in years:
   for code,name in sorted({(c['mesocodigo'],c['mesonome']) for c in cross}):
    rr=[r for r in subset if str(r['ano_rotulo'])==str(year) and r['mesocodigo']==code];vv=[r for r in rr if r['custos_numericos']]
    coverage.append({'fonte':source,'atividade':activity,'ano_rotulo':year,'mesocodigo':code,'mesonome':name,'vintage':'DTB_2016_v2','n_referencias_periodo':len(rr),'n_referencias_com_custos':len(vv),'n_pracas_com_custos':len({r['codigo_ibge_referencia'] for r in vv}),'pracas':';'.join(sorted({r['praca_literal'] for r in vv})),'modelo_regional_validado':False})
 write(out/'cobertura_mesorregiao_atividade_ano.csv',coverage)
 write(out/'referencias_sem_mesorregiao.csv',[r for r in refs if not r['mesocodigo']])
 report={'inputs':inputs,'chaves_painel':141,'mesorregioes':5,'match_imea':140,'divergencias_nome_painel':1,'referencias_total':len(refs),'referencias_com_mesorregiao':sum(bool(r['mesocodigo']) for r in refs),'custos_atribuidos':0,'limites_territoriais_nao_validados':True,'outputs':{p.name:sha(p) for p in sorted(out.glob('*.csv')) if 'pendente' not in p.name}}
 (out/'manifesto_integracao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=P);print(json.dumps(run(ap.parse_args().out),ensure_ascii=False,indent=2))
