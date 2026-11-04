import unittest,tempfile,subprocess,shutil,json,csv,hashlib,sys
from pathlib import Path
from decimal import Decimal
import construir_uso as c
class TestUso(unittest.TestCase):
 def test_fronteira_estrita_e_zeros(self):
  for amount in ('90','110','109.9999'):self.assertFalse(c.comparar('100',amount)['excluir'])
  for amount in ('89.9999','110.0001'):self.assertTrue(c.comparar('100',amount)['excluir'])
  self.assertEqual(c.comparar(0,0)['motivo'],'ambos_zero');self.assertFalse(c.comparar(0,0)['excluir'])
  z=c.comparar(0,1);self.assertTrue(z['excluir']);self.assertEqual(z['relativa'],'')
  self.assertFalse(c.comparar('100',None)['excluir']);self.assertEqual(c.comparar('100',None)['relativa'],'')
 def test_preservacao_integral_historico(self):
  for r in c.read(c.P/'auditoria/mapa_reorganizacao.csv'):
   if '__pycache__' not in r['depois'] and not r['depois'].endswith('.pyc'):self.assertEqual(c.sha(c.P/r['depois']),r['sha256'],r['antes'])
 def test_formato_chaves_e_deduplicacao(self):
  for crop,n in [('AGRICULTURA',247),('PECUARIA',124)]:
   r=c.read(c.P/'BASE_PARA_USO'/f'CUSTOS_{crop}.csv');self.assertEqual(len(r),n);self.assertEqual(len({x['0_id_referencia'] for x in r}),n)
   self.assertTrue(all(x['4_recorte_2001_2024']=='True' for x in r));self.assertNotIn('0_conceito',r[0])
  r=c.read(c.P/'BASE_PARA_USO/CUSTOS_AGRICULTURA.csv');self.assertEqual(sum(x['4_duplicata_consolidada']=='True' for x in r),1)
  duplicate=next(x for x in r if x['4_duplicata_consolidada']=='True');self.assertEqual(len(duplicate['0_ids_origem'].split(';')),2);self.assertFalse(duplicate['0_codigo_ibge_referencia'])
 def test_valores_oficiais_e_eligibilidade_por_conceito(self):
  original={}
  for x in c.read(c.H/'custos_referencia_completos.csv'):original[x['0_id_serie'],x['0_conceito_original']]=x
  for x in c.read(c.P/'BASE_PARA_USO/CUSTOS_AGRICULTURA.csv'):
   if x['0_fonte']!='CONAB':continue
   for code in 'ABCDEFGHIJ':
    src=original[x['0_id_referencia'],code];self.assertEqual(x[f'2_conab_{code.lower()}_nominal'],src['2_custo_brl_nominal_ha']);self.assertEqual(x[f'2_conab_{code.lower()}_usd2024'],src['2_custo_usd2024_ha'])
  r={x['0_id_referencia']:x for x in c.read(c.P/'BASE_PARA_USO/CUSTOS_AGRICULTURA.csv')}
  self.assertEqual(r['6a58c6f0f5837c30']['2_conab_a_nominal'],'976.78');self.assertEqual(r['6a58c6f0f5837c30']['4_conab_a_elegivel_nominal'],'True')
  self.assertIn('comparacao_indisponivel',r['f121da66bd98194b']['4_conab_a_motivos']);self.assertEqual(r['f121da66bd98194b']['4_conab_h_elegivel_nominal'],'True')
  self.assertTrue(c.comparar('100','120')['excluir']);self.assertFalse(c.comparar('100','100')['excluir'])
 def test_ausencias_fontes_moedas(self):
  for crop,missing in [('AGRICULTURA',17),('PECUARIA',31)]:
   rows=c.read(c.P/'BASE_PARA_USO'/f'CUSTOS_{crop}.csv');cols=[k for k in rows[0] if k.startswith('2_') and k.endswith('_nominal')]
   self.assertEqual(sum(not any(x[k] for k in cols) for x in rows),missing)
   for r in rows:
    if r['0_fonte']=='IMEA':self.assertTrue(all(r[k]=='' for k in r if k.endswith('_usd2024') and k.startswith('2_')))
    for k in cols:
     if not r[k]:self.assertEqual(r[k.replace('2_','4_',1).replace('_nominal','_elegivel_nominal')],'False')
 def test_duas_reproducoes_limpas(self):
  expected=json.loads((c.P/'auditoria/manifesto_build.json').read_text())['outputs']
  for _ in range(2):
   with tempfile.TemporaryDirectory() as d:
    root=Path(d);(root/'auditoria').mkdir();shutil.copy2(c.P/'auditoria/mapa_reorganizacao.csv',root/'auditoria/mapa_reorganizacao.csv');shutil.copytree(c.H,root/'historico/v1_publicada',ignore=shutil.ignore_patterns('__pycache__','*.pyc'));(root/'processamento').mkdir();shutil.copy2(Path(c.__file__),root/'processamento/construir_uso.py')
    subprocess.run([sys.executable,str(root/'processamento/construir_uso.py')],check=True,capture_output=True)
    actual=json.loads((root/'auditoria/manifesto_build.json').read_text())['outputs'];self.assertEqual(actual,expected)
if __name__=='__main__':unittest.main()
