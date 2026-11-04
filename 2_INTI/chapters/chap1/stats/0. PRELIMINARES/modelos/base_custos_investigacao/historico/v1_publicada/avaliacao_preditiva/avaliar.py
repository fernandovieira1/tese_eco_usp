"""Validação de custos modais; stdlib, sem alterar fontes ou gerar painel municipal."""
from pathlib import Path
import argparse,csv,json,math,hashlib,statistics as st
P=Path(__file__).resolve().parent;BASE=P.parent;MODELOS=BASE.parent
CROPS=['soja','milho_1a','milho_2a']
def read(f):
 with Path(f).open(newline='') as h:return list(csv.DictReader(h))
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(p,name,rows):
 f=p/name
 if not rows:f.write_text('');return
 with f.open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(p,name,a):(p/name).write_text(json.dumps(a,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def predictors():
 cpi={r['observation_date'][:7]:float(r['CPIAUCNS']) for r in read(BASE/'fontes/bls_fred_CPIAUCNS_1960_2024.csv')}
 base=st.mean(v for k,v in cpi.items() if k.startswith('2024-'))
 dap=read(MODELOS/'base3/fontes_v2/dap_official_2000_2023.csv')
 assert len(dap)==288 and len({r['date'] for r in dap})==288
 out={}
 for year in range(2000,2024):
  rows=[r for r in dap if r['date'].startswith(str(year))]
  assert {r['date'][:7] for r in rows}=={f'{year}-{m:02d}' for m in range(1,13)}
  assert all(r['unit']=='USD/metric tonne' and float(r['value'])>0 for r in rows)
  mean=st.mean(float(r['value'])*base/cpi[r['date'][:7]] for r in rows)
  out[year+1]={'ano_alvo':year+1,'ano_origem_dap':year,'n_meses':12,'dap_usd2024_t':mean,'x':math.log(mean)}
 return out

def fit(train,model):
 y=st.mean(r['y'] for r in train);xm=st.mean(r['x'] for r in train)
 sd=math.sqrt(st.mean((r['x']-xm)**2 for r in train));assert sd>0
 if model=='B0_media_regional':return y,0,xm,sd
 z=[(r['x']-xm)/sd for r in train]
 beta=sum(a*(r['y']-y) for a,r in zip(z,train))/(sum(a*a for a in z)+(1 if model=='M2_ridge' else 0))
 return y,beta,xm,sd
def predict(params,x):
 y,b,xm,sd=params;return y+b*(x-xm)/sd

def run(crop,dest):
 dest=Path(dest);dest.mkdir(parents=True,exist_ok=True);pred=predictors()
 original=[r for r in read(BASE/'custos_referencia_estritos.csv') if r['0_cultura_sistema']==crop and r['0_conceito_original']=='H']
 a=[];excluded=[]
 for r in original:
  year=int(r['0_ano_data_base'])
  if year not in pred or not r['2_custo_usd2024_ha']:excluded.append({'id':r['0_id_serie'],'motivo':'sem_preditor_ou_moeda'});continue
  q=pred[year]
  assert q['ano_origem_dap']<year and f"{q['ano_origem_dap']}-12"<r['0_data_base'][:7]
  a.append({'id':r['0_id_serie'],'cultura':crop,'praca':r['0_localidade_aba'],'ano_data_base':year,'data_base':r['0_data_base'],'safra_inicio':r['0_safra_inicio'],'safra_fim':r['0_safra_fim'],'tecnologia':r['0_tecnologia'],'ex_ant':r['4_flag_ex_ant'],'y':float(r['2_custo_usd2024_ha']),**q})
 a.sort(key=lambda r:(r['ano_data_base'],r['praca'],r['id']))
 write(dest,'amostra.csv',a);write(dest,'perdas.csv',excluded)
 coverage=[]
 for place in sorted({r['praca'] for r in a}):
  for year in sorted({r['ano_data_base'] for r in a if r['praca']==place}):
   b=[r for r in a if r['praca']==place and r['ano_data_base']==year]
   coverage.append({'praca':place,'ano_data_base':year,'n':len(b),'tecnologias':'|'.join(sorted({r['tecnologia'] for r in b})),'n_ex_ant':sum(r['ex_ant']=='True' for r in b)})
 write(dest,'cobertura.csv',coverage)
 ids={r['id'] for r in a}
 components=[r for r in read(BASE/'componentes_nominais.csv') if r['0_id_serie'] in ids]
 blocks=[]
 for code in ['A','B','C','E','F','I']:
  b=[r for r in components if r['0_bloco_conab']==code];v=[float(r['2_valor_brl_nominal_ha']) for r in b if r['2_valor_brl_nominal_ha']]
  blocks.append({'bloco':code,'incluido_em_H':code!='I','linhas':len(b),'valores':len(v),'zeros':sum(x==0 for x in v),'unidade':'BRL nominal/ha; valores originais, não somados entre séries'})
 write(dest,'componentes_suporte.csv',blocks)
 support=len(a)>=24 and len({r['praca'] for r in a})>=3 and len({r['ano_data_base'] for r in a})>=10
 summary={'cultura':crop,'conceito':'H operacional D+G','unidade':'USD2024/ha','n_estrito':len(original),'n_modelavel':len(a),'perdas':len(excluded),'pracas':sorted({r['praca'] for r in a}),'anos_data_base':sorted({r['ano_data_base'] for r in a}),'n_anos':len({r['ano_data_base'] for r in a}),'suporte_teste':support,'gate_municipal':False}
 folds=[];predictions=[];params=[];membership=[]
 if support:
  specs=[]
  for place in summary['pracas']:specs.append(('espacial',place,[r for r in a if r['praca']!=place],[r for r in a if r['praca']==place]))
  for cut,end in [(2015,2019),(2019,2021),(2021,2024)]:specs.append(('temporal',f'{cut+1}-{end}',[r for r in a if r['ano_data_base']<=cut],[r for r in a if cut<r['ano_data_base']<=end]))
  for axis,block,tr,te in specs:
   reasons=[]
   if len(tr)<12:reasons.append('treino_menor12')
   if len({r['praca'] for r in tr})<2:reasons.append('treino_menos2pracas')
   if len(te)<4:reasons.append('teste_menor4')
   if len({r['x'] for r in tr})<2:reasons.append('sem_variancia_x')
   folds.append({'eixo':axis,'bloco':block,'n_treino':len(tr),'n_teste':len(te),'admissivel':not reasons,'motivo':'|'.join(reasons)})
   if reasons:continue
   if axis=='temporal':assert max(r['ano_data_base'] for r in tr)<min(r['ano_data_base'] for r in te)
   else:assert not {r['praca'] for r in tr}&{r['praca'] for r in te}
   assert not {r['id'] for r in tr}&{r['id'] for r in te}
   for role,rows in [('treino',tr),('teste',te)]:
    membership.extend({'eixo':axis,'bloco':block,'papel':role,'id':r['id'],'ano':r['ano_data_base'],'praca':r['praca']} for r in rows)
   for model in ['B0_media_regional','M1_ols','M2_ridge']:
    par=fit(tr,model);params.append({'eixo':axis,'bloco':block,'modelo':model,'intercepto':par[0],'beta_x_padronizado':par[1],'media_x_treino':par[2],'sd_x_treino':par[3],'lambda':1 if model=='M2_ridge' else 0})
    for r in te:
     yhat=predict(par,r['x'])
     predictions.append({'eixo':axis,'bloco':block,'modelo':model,'id':r['id'],'ano':r['ano_data_base'],'praca':r['praca'],'observado':r['y'],'previsto':yhat,'erro':yhat-r['y'],'negativo':yhat<0,'extrapola_x':not min(s['x'] for s in tr)<=r['x']<=max(s['x'] for s in tr)})
 metrics=[]
 for axis in ['espacial','temporal']:
  for block in ['TODOS']+sorted({r['bloco'] for r in predictions if r['eixo']==axis}):
   for model in ['B0_media_regional','M1_ols','M2_ridge']:
    b=[r for r in predictions if r['eixo']==axis and r['modelo']==model and (block=='TODOS' or r['bloco']==block)]
    if not b:continue
    metrics.append({'eixo':axis,'bloco':block,'modelo':model,'n':len(b),'n_folds':len({r['bloco'] for r in b}),'mae':st.mean(abs(r['erro']) for r in b),'rmse':math.sqrt(st.mean(r['erro']**2 for r in b)),'bias':st.mean(r['erro'] for r in b),'media_alvo':st.mean(r['observado'] for r in b),'n_negativos':sum(r['negativo'] for r in b),'n_extrapola_x':sum(r['extrapola_x'] for r in b)})
 gates=[]
 for model in ['M1_ols','M2_ridge']:
  for axis in ['espacial','temporal']:
   m=next((r for r in metrics if r['modelo']==model and r['eixo']==axis and r['bloco']=='TODOS'),None)
   b=next((r for r in metrics if r['modelo']=='B0_media_regional' and r['eixo']==axis and r['bloco']=='TODOS'),None)
   if not m:gates.append({'modelo':model,'eixo':axis,'passou':False,'motivo':'suporte_ou_folds_insuficientes'});continue
   worst=max(r['mae']/next(z['mae'] for z in metrics if z['eixo']==axis and z['bloco']==r['bloco'] and z['modelo']=='B0_media_regional') for r in metrics if r['eixo']==axis and r['modelo']==model and r['bloco']!='TODOS')
   checks={'dois_folds':m['n_folds']>=2,'ganho10pct':m['mae']<=.9*b['mae'],'erro20pct':m['mae']/m['media_alvo']<=.2,'bias10pct':abs(m['bias'])/m['media_alvo']<=.1,'pior_fold125pct':worst<=1.25,'sem_negativos':m['n_negativos']==0}
   gates.append({'modelo':model,'eixo':axis,'passou':all(checks.values()),'motivo':'|'.join(k for k,v in checks.items() if not v)})
 summary['modelos_aprovados_dois_eixos']=[m for m in ['M1_ols','M2_ridge'] if all(r['passou'] for r in gates if r['modelo']==m)]
 summary['decisao']='insuficiente_para_teste' if not support else ('gate_exploratorio_passou_sem_validacao_municipal' if summary['modelos_aprovados_dois_eixos'] else 'nao_passou_gate_preditivo')
 for name,rows in [('folds.csv',folds),('membros_folds.csv',membership),('parametros_treino.csv',params),('previsoes_holdout.csv',predictions),('metricas.csv',metrics),('gates.csv',gates)]:write(dest,name,rows)
 js(dest,'resumo.json',summary)
 text=f'# Custo operacional: {crop}\n\n'+f"Conceito H = A+B+C+E+F, exclui renda de fatores I. {len(a)} séries, {len(summary['pracas'])} praças, {summary['n_anos']} anos de data-base. Moeda USD2024/ha. Perdas por preditor/moeda: {len(excluded)}.\n\n"+'Cobertura exata em cobertura.csv: ano da data-base não equivale necessariamente à safra. Tecnologias e ExAnt permanecem identificados. Componentes em componentes_suporte.csv não são novas unidades independentes.\n\n'
 text+='| Eixo | Modelo | N | MAE | RMSE | Bias | Extrapola X |\n|---|---|---:|---:|---:|---:|---:|\n'
 for r in metrics:
  if r['bloco']=='TODOS':text+=f"| {r['eixo']} | {r['modelo']} | {r['n']} | {r['mae']:.2f} | {r['rmse']:.2f} | {r['bias']:.2f} | {r['n_extrapola_x']} |\n"
 text+='\nDecisão: '+summary['decisao']+'. Gate municipal: NÃO VALIDADO.\n\n'+ ('Não houve estimação: suporte abaixo dos mínimos pré-fixados.\n' if not support else 'As previsões são apenas holdouts dos polos. MAE/bias em USD2024/ha. B0 é média regional do treino, não OLS. Validação espacial retrospectiva e temporal prospectiva são eixos separados, não validação conjunta.\n')
 text+='\nDAP é comum por ano, sem ajuste municipal. Choques compartilhados e somente 3–4 praças limitam a evidência; número de linhas não é número de choques independentes. Sem intervalos de confiança, causalidade, significância ou busca adicional. Modelos não aprovados ficam registrados. Nem eventual ganho autoriza extrapolar tecnologias, praças ou anos ausentes. IMEA não entra, por falta de comparabilidade validada.\n\nO piloto antigo usava amostra anterior, produtividade modal e BRL/IPCA. Esta avaliação em USD com preditor transferível é novo desenho, não diferença causal de desempenho atribuível apenas à exclusão de duas planilhas. O piloto antigo foi preservado.\n'
 (dest/'README.md').write_text(text)
 js(dest,'manifesto.json',{'protocolo_sha256':sha(P/'ESTRATEGIA_ANTES_DOS_RESULTADOS.md'),'inputs':{str(f.relative_to(MODELOS)):sha(f) for f in [BASE/'custos_referencia_estritos.csv',BASE/'componentes_nominais.csv',BASE/'fontes/bls_fred_CPIAUCNS_1960_2024.csv',MODELOS/'base3/fontes_v2/dap_official_2000_2023.csv']},'outputs':{f.name:sha(f) for f in sorted(dest.iterdir()) if f.suffix in ['.csv']}})
 return summary
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('cultura',choices=CROPS);ap.add_argument('--out',type=Path);args=ap.parse_args();print(json.dumps(run(args.cultura,args.out or P/args.cultura),ensure_ascii=False,indent=2))
