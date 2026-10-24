"""IMEA: extrato oficial por praça; sem equiparar COE/COT/CT aos conceitos CONAB."""
import csv,hashlib,json,math,re
from pathlib import Path
P=Path(__file__).resolve().parent
SOURCE=P/'fontes/imea/imea_regional_key_costs.csv'
EXPECTED='808695e768d80ac8bcfa14ea66c880bebb29883b7b8ae59c04e3549dad05b6b9'
def construir_imea():
 from construir import ler,out,js
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
 source=ler(SOURCE);assert len(source)==195
 assert len({(r['source_file'],r['sheet'],r['source_column']) for r in source})==195
 assert len({r['sheet'] for r in source})==28
 audit=json.loads((SOURCE.parent/'imea_regional_audit.json').read_text())
 notes=ler(SOURCE.parent/'imea_regional_source_notes.csv')
 assert audit['records']==len(source) and len(notes)==143
 for sheet in audit['sheets']:
  subset=[r for r in source if r['source_file']==sheet['source_file'] and r['sheet']==sheet['sheet']]
  assert len(subset)==sheet['records']
  assert all(r['geography_label']==sheet['geography'] for r in subset)
  assert all(int(r[k+'_cell'][1:])==sheet['metric_rows'][k] for r in subset for k in ['coe','cot','ct'])
 rows=[];checks=[]
 for r in source:
  sid='imea_'+hashlib.sha256((r['source_file']+'|'+r['sheet']+'|'+r['source_column']).encode()).hexdigest()[:16]
  match=re.fullmatch(r'(\d{4})/(\d{2})(\*+)?',r['crop_year_label']);assert match
  start=int(match[1]);end=start//100*100+int(match[2]);assert end==start+1
  ambiguous=bool(match[3]);target=2001<=start and end<=2024
  values=[float(r[k]) if r[k] else None for k in ['coe','cot','ct']]
  valid=all(v is not None and math.isfinite(v) and v>=0 for v in values)
  ordered=valid and values[0]<=values[1]<=values[2]
  assert r['unit']=='R$/ha'
  checks.append({'0_id_serie':sid,'0_aba':r['sheet'],'0_safra_rotulo_original':r['crop_year_label'],'4_tres_valores_numericos':valid,'4_ordem_coe_cot_ct':ordered,'4_nao_valida_soma_componentes':True})
  for concept in ['coe','cot','ct']:
   numeric=r[concept]!='' and math.isfinite(float(r[concept])) and float(r[concept])>=0
   reasons=['componentes_e_metodologia_integral_nao_conferidos','nominalidade_e_data_base_consolidados_nao_confirmadas' if not r['reference_month_from_labels'] else 'cpi_2026_indisponivel']
   if not target:reasons.append('safra_fora_alvo_2001_2024')
   if ambiguous:reasons.append('nota_asterisco_sem_associacao_documental_segura')
   if not numeric:reasons.append('valor_ausente_no_extrato')
   if not ordered:reasons.append('ordem_conceitos_nao_verificavel_ou_falha')
   rows.append({'0_id_registro':sid+'_'+concept,'0_id_serie':sid,'0_fonte':'IMEA','0_cultura':'soja' if 'soja' in r['source_file'] else 'milho','0_sistema_safra':'não confirmado no extrato' if 'milho' in r['source_file'] else 'soja','0_tecnologia_rotulo_original':r['crop_technology_label'],'0_localidade_original':r['geography_label'],'0_nivel_geografico':r['geography_level'],'0_safra_rotulo_original':r['crop_year_label'],'0_safra_inicio':start,'0_safra_fim':end,'0_ano_rotulo_original':r['year_label'],'0_periodo_rotulo_original':r['period_label'],'0_mes_referencia_rotulo':r['reference_month_from_labels'],'0_natureza_rotulo_original':r['natureza_from_period_label'],'0_conceito_original':concept.upper(),'0_unidade_original':r['unit'],'2_custo_brl_declarado_ha':r[concept],'2_custo_usd2024_ha':'','4_valor_numerico':numeric,'4_ordem_conceitos':ordered,'4_safra_alvo_2001_2024':target,'4_rotulo_asterisco_ambiguo':ambiguous,'4_candidato_descritivo_rotulo':numeric and ordered and target and not ambiguous,'4_estrito_comparavel':False,'4_data_nominal_suficiente':False,'4_custo_municipal_observado':False,'4_motivos_quarentena':';'.join(reasons),'0_arquivo_xlsx_origem':r['source_file'],'0_sha256_xlsx_origem':r['source_sha256'],'0_aba':r['sheet'],'0_celula':r[concept+'_cell'],'4_bruto_xlsx_local':False})
 assert len(rows)==585 and len({r['0_id_registro'] for r in rows})==585
 out('custos_imea_referencia.csv',rows)
 out('custos_imea_quarentena.csv',rows)
 out('custos_imea_candidatos_descritivos.csv',[r for r in rows if r['4_candidato_descritivo_rotulo']])
 out('auditoria_imea.csv',checks)
 cover=[]
 for crop in ['soja','milho']:
  for year in sorted({r['0_safra_rotulo_original'] for r in rows if r['0_cultura']==crop}):
   a=[r for r in rows if r['0_cultura']==crop and r['0_safra_rotulo_original']==year]
   cover.append({'0_cultura':crop,'0_safra_rotulo_original':year,'0_registros_planilha_coluna':len(a)//3,'0_valores':len(a),'0_valores_numericos':sum(r['4_valor_numerico'] for r in a),'0_valores_candidatos_descritivos':sum(r['4_candidato_descritivo_rotulo'] for r in a),'0_estaduais_planilha_coluna':sum(r['0_nivel_geografico']=='estado' for r in a)//3})
 out('cobertura_imea.csv',cover)
 summary={'registros_planilha_coluna':195,'abas':28,'celulas':585,'numericas':sum(r['4_valor_numerico'] for r in rows),'ausentes':sum(not r['4_valor_numerico'] for r in rows),'candidatos_descritivos':sum(r['4_candidato_descritivo_rotulo'] for r in rows),'registros_safra_ambigua':len({r['0_id_serie'] for r in rows if r['4_rotulo_asterisco_ambiguo']}),'comparaveis_estritos':0,'usd2024':0,'nota':'585 células são195 unidades planilha/coluna; não585 amostras independentes. Quarentena integral para comparabilidade; subset descritivo não aprovação plena.'}
 js('resumo_imea.json',summary)
 return summary
if __name__=='__main__':print(json.dumps(construir_imea(),ensure_ascii=False))
