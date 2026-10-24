from pathlib import Path
import csv,json,tempfile,hashlib,importlib.util,collections
P=Path(__file__).resolve().parent
REPO=P.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open()))
def module(folder):
 spec=importlib.util.spec_from_file_location(folder,P/folder/'integrar.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
checks=[]
for folder in ('pecuaria','regionalizacao'):
 m=module(folder)
 for repeat in range(2):
  with tempfile.TemporaryDirectory() as d:
   result=m.run(d)
   for name,h in result['outputs'].items():assert sha(Path(d)/name)==sha(P/folder/name),(folder,name)
 checks.append(folder+': duas reproduções isoladas idênticas')
r=read(P/'pecuaria/registros_periodo.csv');long=read(P/'pecuaria/custos_referencia.csv');notes=read(P/'pecuaria/fontes/imea_pecuaria_headers_notes.csv');idx={(x['sheet_id'],x['column']):x for x in r}
assert len(idx)==196 and len(long)==588
for x in long:
 sid,col=x['0_id_referencia'].split('_');original=idx[sid,col];metric=x['0_conceito'].lower();assert x['2_custo_nominal']==original[metric] and x['4_tipo_origem']==original[metric+'_type'];assert not x['2_custo_usd2024'];assert x['0_unidade']=='R$/@ vendida';assert x['4_uso_preditivo']=='False'
assert sum(x['4_tipo_origem']=='stored_blank' for x in long)==120
assert len(notes)==752 and any('algodão' in x['source_value'] for x in notes)
checks.append('588 valores/células reconciliados; 120 ausências, nenhuma conversão; 752 notas')
ids=read(P/'regionalizacao/identificacao_regional.csv');rr=read(P/'regionalizacao/referencias_identificadas.csv');cov=read(P/'regionalizacao/cobertura_mesorregiao_atividade_ano.csv')
assert len(ids)==141 and len({x['0_codigo_ibge'] for x in ids})==141
assert len(rr)==476 and sum(bool(x['mesocodigo']) for x in rr)==424
assert sum(int(x['n_referencias_periodo']) for x in cov)==424
assert len({x['mesocodigo'] for x in rr if x['mesocodigo']})==5
assert next(x for x in ids if x['0_codigo_ibge']=='5107008')['0_regiao_imea']=='NA'
assert all(not x['mesocodigo'] for x in rr if x['id_referencia'].startswith(('s14_','s17_')))
assert all(x['4_custo_atribuido']=='False' for x in ids)
checks.append('141 chaves, cinco mesorregiões, cobertura reconciliada; conflitos não resolvidos por inferência')
old=json.loads((P/'preservacao_publicacao.json').read_text());repo=next(x for x in P.parents if (x/'AGENTS.md').exists());changed=[n for n,h in old.items() if sha(repo/n)!=h];assert not changed,changed
checks.append(f'{len(old)} arquivos anteriores preservados por hash')
report={'result':'PASS','checks':checks,'agricultura':'resultados anteriores preservados; nenhuma reestimação regional','raw_access':'apenas pai; integração CSV reproduzida localmente'}
(P/'validacao_integracao_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
