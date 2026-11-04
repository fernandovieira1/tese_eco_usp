"""Prepara suporte territorial sem inventar correspondências regionais."""
from pathlib import Path
import csv,json,hashlib,argparse
P=Path(__file__).resolve().parent
ROOT=P.parent
PANEL=ROOT.parent/'base3/painel_h1_base3_v4.csv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(out,name,rows):
 with (out/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 panel=list(csv.DictReader(PANEL.open())); keys={r['0_codigo_ibge']:r['0_municipio'] for r in panel}
 assert len(panel)==3384 and len(keys)==141
 assert len({(r['0_codigo_ibge'],r['0_ano']) for r in panel})==3384
 rows=[{'0_codigo_ibge':k,'0_municipio':name,'0_suporte_painel':'IBGE_MT_2023_141','0_codigo_mesorregiao_ibge':'','0_nome_mesorregiao_ibge':'','0_vintage_mesorregiao_ibge':'','0_regiao_imea':'','0_vintage_regiao_imea':'','4_status':'pendente_crosswalk_oficial_e_compatibilidade_territorial','4_custo_atribuido':False} for k,name in sorted(keys.items())]
 write(out,'identificacao_regional_pendente.csv',rows)
 coverage=[]
 inputs={str(PANEL):sha(PANEL)}
 for crop in ['soja','milho_1a','milho_2a']:
  src=ROOT/'avaliacao_preditiva'/crop/'amostra.csv';inputs[str(src)]=sha(src)
  sample=list(csv.DictReader(src.open()))
  for year in range(2001,2025):
   s=[r for r in sample if int(r['ano_data_base'])==year]
   coverage.append({'0_atividade':crop,'0_ano_data_base':year,'0_codigo_mesorregiao_ibge':'','0_nome_mesorregiao_ibge':'','4_status_regiao':'nao_identificada_pendente_crosswalk','4_n_referencias_estritas_sem_regiao':len(s),'4_n_pracas_sem_regiao':len({r['praca'] for r in s}),'4_pracas':';'.join(sorted({r['praca'] for r in s})),'4_interpretacao':'contagem de planos modais; ausência de região não é região geográfica'})
 write(out,'cobertura_atividade_ano_regiao_pendente.csv',coverage)
 (out/'manifesto.json').write_text(json.dumps({'inputs':inputs,'outputs':{f.name:sha(f) for f in sorted(out.glob('*.csv'))},'n_chaves_preservadas':141,'n_regioes_verificadas':0,'n_custos_atribuidos':0,'sem_mudanca_base3':True},indent=2)+'\n')
 return rows,coverage
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',default=P,type=Path);args=ap.parse_args();run(args.out)
