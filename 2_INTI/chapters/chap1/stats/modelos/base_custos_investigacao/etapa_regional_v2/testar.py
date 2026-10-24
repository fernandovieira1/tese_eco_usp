import unittest,tempfile,subprocess,sys,json,math,statistics as st
from pathlib import Path
from collections import defaultdict
import executar as e
class Validacao(unittest.TestCase):
 def test_preservacao_principal_fontes_e_amostra(self):
  e.sources();root=next(p for p in e.P.parents if (p/'.git').exists())
  for name,h in json.loads((e.P/'preservacao_principal.json').read_text()).items():self.assertEqual(e.sha(root/name),h)
  ag,pec=e.sources();self.assertEqual((len(ag),len(pec)),(247,124))
  self.assertEqual(sum(r['0_fonte']=='CONAB' for r in ag),163)
  self.assertEqual(len({r['0_id_referencia'] for r in ag}),247)
  selected={r['id'] for r in e.read(e.P/'resultados/avaliacao/amostra.csv')}
  self.assertIn('6a58c6f0f5837c30',selected) # Primavera~4% retained.
  self.assertIn('f121da66bd98194b',selected) # Sorriso accounting ambiguity is not a quality exclusion.
  loss=e.read(e.P/'resultados/avaliacao/perdas.csv');self.assertEqual(len(loss),6);self.assertTrue(all(r['motivos']=='geografia_nao_resolvida' for r in loss))
 def test_folds_sem_vazamento_e_mesma_avaliacao(self):
  membership=defaultdict(lambda:defaultdict(list))
  for r in e.read(e.P/'resultados/avaliacao/membros.csv'):membership[r['analise'],r['eixo'],r['bloco']][r['papel']].append(r)
  for (_,axis,_),roles in membership.items():
   tr,te=roles['treino'],roles['teste'];self.assertFalse({r['id'] for r in tr}&{r['id'] for r in te})
   if axis=='temporal':self.assertLess(max(int(r['ano']) for r in tr),min(int(r['ano']) for r in te))
   else:self.assertFalse({r['praca'] for r in tr}&{r['praca'] for r in te})
  models=defaultdict(lambda:defaultdict(set))
  for r in e.read(e.P/'resultados/avaliacao/previsoes.csv'):models[r['analise'],r['eixo'],r['bloco']][r['modelo']].add(r['id'])
  for g in models.values():self.assertEqual(g[e.MODELS[0]],g[e.MODELS[1]]);self.assertEqual(g[e.MODELS[0]],g[e.MODELS[2]])
  a=e.read(e.P/'resultados/avaliacao/amostra.csv');lookup={r['id']:{**r,'x':float(r['x']),'y':float(r['y'])} for r in a}
  for par in e.read(e.P/'resultados/avaliacao/parametros.csv'):
   tr=[lookup[r['id']] for r in membership[par['analise'],par['eixo'],par['bloco']]['treino']];ym,b,xm,sd=e.estimate(tr,par['modelo'])
   self.assertAlmostEqual(xm,float(par['media_x']));self.assertAlmostEqual(sd,float(par['sd_x']));self.assertAlmostEqual(b,float(par['beta']))
 def test_referencias_e_pesos_e_suporte(self):
  lineage=defaultdict(lambda:defaultdict(list))
  cross={r['codigoIBGE']:r['mesocodigo'] for r in e.read(e.F/'regioes.csv')}
  for r in e.read(e.P/'resultados/linhagem_regional.csv'):
   self.assertEqual(cross[r['praca']],r['mesocodigo'])
   lineage[r['id_referencia_regional'],r['conceito']+'_'+r['moeda']][r['praca']].append(float(r['valor']))
  refs=e.read(e.P/'resultados/REFERENCIAS_REGIONAIS.csv');self.assertEqual(len({r['id_referencia_regional'] for r in refs}),len(refs))
  for r in refs:
   for c in e.CONCEPTS[r['fonte']]:
    for currency in ['nominal','usd2024']:
     m=c+'_'+currency;byplace=lineage.get((r['id_referencia_regional'],m),{})
     if not byplace:self.assertEqual(r[m+'_mediana'],'');continue
     vals=[st.median(x) for x in byplace.values()]
     self.assertAlmostEqual(float(r[m+'_mediana']),st.median(vals));self.assertEqual(int(r[m+'_n_pracas']),len(vals));self.assertEqual(r[m+'_atribuivel'],str(len(vals)>=1))
   self.assertEqual(r['disponivel_exante_validado'],'False')
  excluded={r['id'] for r in e.read(e.P/'resultados/nao_regionalizados.csv')}
  for sid in ['50293165740cd776','6a59ce79df2ccf1e','f6d4c28f6be7fe2c','50f3228c7ba40f87','c097dd0338204e46','b622ffb932346f2b']:self.assertIn(sid,excluded)
 def test_painel_chaves_na_cobertura(self):
  indices=e.read(e.F/'indices_h1.csv');cross={r['codigoIBGE']:r['mesocodigo'] for r in e.read(e.F/'regioes.csv')}
  counts=[]
  for folder,minimum in [(e.P,1),(e.P/'resultados/cenario_conservador',2)]:
   panel=e.read(folder/'resultados/PAINEL_SOMENTE_REGIONAL.csv');candidates=e.read(folder/'resultados/lista_candidatas.csv');refs={r['id_referencia_regional']:r for r in e.read(folder/'resultados/REFERENCIAS_REGIONAIS.csv')}
   meta=e.read(folder/'resultados/METADADOS_SOMENTE_REGIONAL.csv');lookup={(r['0_codigo_ibge'],r['0_ano'],r['variavel']):r for r in meta}
   self.assertEqual(len(lookup),3384*27);self.assertEqual(len(panel),3384);self.assertEqual(len(panel[0]),34)
   self.assertTrue(all(k.startswith(('0_','2_')) for k in panel[0]))
   for i,r in zip(indices,panel):self.assertEqual(i,{k:r[k] for k in i})
   count={}
   for c in candidates:
    name=c['variavel'];metric=c['conceito']+'_'+c['moeda'];n=0
    for row in panel:
     m=lookup[row['0_codigo_ibge'],row['0_ano'],name];ref=refs.get(m['id_ref']);ok=ref is not None and int(ref[metric+'_n_pracas'] or 0)>=minimum
     self.assertEqual(bool(row[name]),ok);self.assertEqual(m['4_incorporacao_aprovada'],'False')
     if ok:
      self.assertEqual(row[name],ref[metric+'_mediana']);self.assertEqual(cross[row['0_codigo_ibge']],ref['mesocodigo']);self.assertEqual(row['0_ano'],ref['ano_alinhado']);n+=1
      if m['n_pracas']=='1':self.assertEqual(m['confiabilidade'],'suporte_fraco_uma_praca')
    self.assertEqual(n,int(c['municipio_anos_atribuidos']));count[name]=n
   counts.append(count)
  self.assertTrue(all(counts[0][k]>=v for k,v in counts[1].items()))
  self.assertTrue(any(counts[0][k]>v for k,v in counts[1].items()))
 def test_fallback_publicado_compativel_e_prioridade(self):
  panel=e.read(e.P/'USO_CANDIDATOS/CUSTOS_MUNICIPAIS_CANDIDATOS.csv');regional=e.read(e.P/'resultados/PAINEL_SOMENTE_REGIONAL.csv');indices=e.read(e.F/'indices_h1.csv')
  states={(r['variavel'],r['ano']):r for r in e.read(e.P/'resultados/REFERENCIAS_ESTADUAIS_PUBLICADAS.csv')}
  metadata={(r['0_codigo_ibge'],r['0_ano'],r['variavel']):r for r in e.read(e.P/'resultados/METADADOS_CUSTOS_MUNICIPAIS.csv')}
  self.assertEqual(len(panel),3384);self.assertEqual(len(panel[0]),34);self.assertEqual(len(metadata),3384*27)
  counts=defaultdict(lambda:defaultdict(int))
  for row,old,idx in zip(panel,regional,indices):
   self.assertEqual({k:row[k] for k in idx},idx)
   for var in row:
    if not var.startswith('2_'):continue
    m=metadata[row['0_codigo_ibge'],row['0_ano'],var];state=states.get((var,row['0_ano']))
    scope='regional' if old[var] else 'estadual_publicada' if state else 'ausente'
    self.assertEqual(m['origem_atribuicao'],scope);self.assertEqual(m['incorporacao_aprovada'],'False')
    self.assertEqual(row[var],old[var] if old[var] else state['valor'] if state else '')
    if scope=='estadual_publicada':
     for k in ['fonte','atividade','sistema','conceito','moeda','natureza']:self.assertEqual(m[k],state[k])
     self.assertEqual(m['ano_referencia'],row['0_ano']);self.assertEqual(m['id_referencia'],state['id_fonte']);self.assertEqual(m['n_pracas'],'')
    if m['fonte']=='CONAB':self.assertNotEqual(scope,'estadual_publicada')
    counts[var][scope]+=1
  for r in e.read(e.P/'resultados/COBERTURA_FALLBACK.csv'):
   for key,scope in [('n_regional','regional'),('n_estadual','estadual_publicada'),('n_vazio','ausente')]:self.assertEqual(int(r[key]),counts[r['variavel']][scope])
  ag,pec=e.sources();src={r['0_id_referencia']:r for r in ag+pec}
  for r in states.values():
   original=src[r['id_fonte']];self.assertEqual(original['4_alerta_geografia'],'referencia_estadual');self.assertEqual(original['0_localidade_literal'],'MATO GROSSO')
   self.assertEqual(r['valor'],original['2_'+r['conceito']+'_'+r['moeda']])
 def test_duas_reproducoes_limpas(self):
  import shutil
  expected=json.loads((e.P/'manifesto_saidas.json').read_text())
  for _ in range(2):
   with tempfile.TemporaryDirectory() as d:
    p=Path(d);shutil.copytree(e.F,p/'fontes');shutil.copy2(e.P/'proveniencia.json',p/'proveniencia.json');shutil.copy2(e.P/'executar.py',p/'executar.py');shutil.copy2(e.P/'incorporar_fallback.py',p/'incorporar_fallback.py')
    x=subprocess.run([sys.executable,str(p/'executar.py')],capture_output=True,text=True);self.assertEqual(x.returncode,0,x.stderr)
    self.assertEqual(json.loads((p/'manifesto_saidas.json').read_text()),expected)
    # Published outputs are protected from an accidental rerun by CLI.
    x=subprocess.run([sys.executable,str(p/'executar.py')],capture_output=True,text=True);self.assertNotEqual(x.returncode,0)
if __name__=='__main__':unittest.main(verbosity=2)
