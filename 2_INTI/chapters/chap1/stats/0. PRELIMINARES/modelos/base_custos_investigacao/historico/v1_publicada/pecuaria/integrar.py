"""Integra apenas extratos com hashes verificados; nenhuma conversão monetária/ha."""
from pathlib import Path
import csv,json,hashlib,argparse
P=Path(__file__).resolve().parent
EXPECTED={'retrieve_extract_imea_pecuaria.py':'7823d7c0ddf1b590deef60f8cc49c23e9efe71fd9d6af1c1556d51f67d25512e','imea_pecuaria_costs_cria.csv':'e8da99d1f3c64c2385caaa03a400b7bdcf831f1e3f66d04b3c57cf0bbf25ad65','imea_pecuaria_costs_recria_engorda.csv':'ab7cf8b79cbb91339b398a0f08a03709126074ec943bafb2338750002bf14a2c','imea_pecuaria_costs_ciclo_completo.csv':'9eb8c280f8fabd0e84490b847f7a5934f164d0a0b8cb52d0530ec7d7bb2b036a','imea_pecuaria_sheets.csv':'d2521f9c396ce61b2523103f62579a7976c5df35f734210ab3bac7929cdb6043','imea_pecuaria_headers_notes.csv':'85586a9424433e0eb3b32ddeda79d1ba6e4228b6c7fed0fde4bb3675c00069fa','validation_report.json':'b35d7f06edc8e8042f5b22a22a54da4877fc4526b3b527ad7bf50747bddb268f','PROVENIENCIA_PECUARIA.md':'0ebf2b900c1b0f6bc4d21d2319e12bad99e9707e1a95a083ebc20e8c2c88343d'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8',newline='')))
def write(p,rows):
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(out=P):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 for n,h in EXPECTED.items():assert sha(P/'fontes'/n)==h,n
 sheets={r['sheet_id']:r for r in read(P/'fontes/imea_pecuaria_sheets.csv')};allrows=[];long=[]
 for system in ('cria','recria_engorda','ciclo_completo'):
  for r in read(P/'fontes'/f'imea_pecuaria_costs_{system}.csv'):
   s=sheets[r['sheet_id']];r={**r,'system_key':system,'geography':s['geography_label_A4'],'geography_warning':s['geography_warning'],'sheet_name':s['sheet_name_exact']};allrows.append(r)
   for metric in ('coe','cot','ct'):
    reasons=[]
    if r[metric]=='':reasons.append('valor_ausente')
    if s['geography_warning']:reasons.append('identidade_geografica_conflitante')
    if not r['reference_period_from_labels']:reasons.append('periodo_incompleto')
    if int(r['year_label'])>2024:reasons.append('fora_janela_2001_2024')
    long.append({'0_id_referencia':r['sheet_id']+'_'+r['column'],'0_sistema':system,'0_aba':r['sheet_name'],'0_geografia_literal':r['geography'],'0_escala':'nao_resolvida' if s['geography_warning'] else 'estado' if r['geography']=='MATO GROSSO' else 'praca_modal','0_ano_rotulo':r['year_label'],'0_trimestre_rotulo':r['quarter_label'],'0_periodo':r['reference_period_from_labels'],'0_conceito':metric.upper(),'0_unidade':'R$/@ vendida','2_custo_nominal':r[metric],'2_produtividade_modal':r['modal_productivity'],'0_unidade_produtividade':'@vendida/ha','2_custo_usd2024':'','4_celula':r[metric+'_cell'],'4_tipo_origem':r[metric+'_type'],'4_referencia_descritiva_2001_2024':not reasons,'4_motivos':';'.join(reasons),'4_uso_preditivo':False,'4_conversion_motivo':'data_precificacao_e_deflator_nao_validados','4_custo_municipal_observado':False})
 assert len(allrows)==196 and len(long)==588
 assert sum(bool(r['coe']) for r in allrows)==156
 write(out/'custos_referencia.csv',long);write(out/'registros_periodo.csv',allrows)
 cover=[]
 for sys in ('cria','recria_engorda','ciclo_completo'):
  for year in sorted({r['year_label'] for r in allrows}):
   rr=[r for r in allrows if r['system_key']==sys and r['year_label']==year];valid=[r for r in rr if r['coe'] and not r['geography_warning']]
   cover.append({'sistema':sys,'ano_rotulo':year,'n_registros_periodo':len(rr),'n_com_custos':sum(bool(r['coe']) for r in rr),'n_estado_validos':sum(r['geography']=='MATO GROSSO' for r in valid),'n_pracas_validas':len({r['geography'] for r in valid if r['geography']!='MATO GROSSO'}),'n_conflitos_identidade':sum(bool(r['geography_warning']) for r in rr)})
 write(out/'cobertura_sistema_ano.csv',cover)
 report={'inputs':EXPECTED,'registros_periodo':196,'registros_custos_numericos':156,'metricas_long':588,'valores_monetarios_numericos':468,'notas_celulas':752,'validacao_raw':'Realizada no pai; relatório original transferido e hash verificado. XLSX não disponível neste executor.','outputs':{n:sha(out/n) for n in ('custos_referencia.csv','registros_periodo.csv','cobertura_sistema_ano.csv')}}
 (out/'manifesto_integracao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=P);print(json.dumps(run(ap.parse_args().out),ensure_ascii=False,indent=2))
