import unittest, subprocess, hashlib, json
from pathlib import Path
import construir as c
class TestCustos(unittest.TestCase):
 def test_chaves_e_particao(self):
  a=c.ler(c.P/'custos_referencia_completos.csv');s=c.ler(c.P/'custos_referencia_estritos.csv');q=c.ler(c.P/'custos_quarentena.csv')
  key=lambda x:{r['0_id_registro'] for r in x}
  self.assertEqual((len(a),len(s),len(q)),(1880,850,1030));self.assertEqual(len(key(a)),1880)
  self.assertFalse(key(s)&key(q));self.assertEqual(key(a),key(s)|key(q))
  self.assertEqual(len({r['0_id_serie'] for r in a if r['4_estrito_auditoria_anterior']=='True'}),87)
  self.assertEqual(len({r['0_id_serie'] for r in s}),85)
  self.assertEqual(len([r for r in a if r['4_candidato_nominal']=='True']),1580)
  self.assertTrue(all(r['4_componentes_serie_reconciliados']=='True' for r in s))
 def test_valores_originais(self):
  old={(r['id_serie'],r['conceito']):r for r in c.ler(c.F/'custos_agregados_longos.csv') if r['unidade']=='BRL_nominal/ha'}
  for r in c.ler(c.P/'custos_referencia_completos.csv'):
   src=old[r['0_id_serie'],r['0_conceito_original']]
   self.assertEqual(r['2_custo_brl_nominal_ha'],src['valor']);self.assertEqual(r['2_valor_original_texto'],src['valor_original'])
 def test_contabilidade_e_moeda(self):
  a=c.ler(c.P/'auditoria_identidades.csv');self.assertEqual(len(a),752);self.assertTrue(all(r['4_aprovado']=='True' for r in a))
  b=c.ler(c.P/'auditoria_componentes.csv');self.assertEqual(sum(r['4_soma_aprovada']=='True' for r in b),1124)
  for r in c.ler(c.P/'custos_referencia_completos.csv'):
   self.assertGreater(float(r['2_cambio_brl_usd']),0)
   if r['2_cpi_u_mes']:
    esperado=float(r['2_custo_brl_nominal_ha'])/float(r['2_cambio_brl_usd'])*313.6888333333333/float(r['2_cpi_u_mes'])
    self.assertAlmostEqual(float(r['2_custo_usd2024_ha']),esperado,places=9)
   else:self.assertEqual(r['2_custo_usd2024_ha'],'')
  self.assertEqual(c.converter(100,5,100,200),40);self.assertIsNone(c.converter(100,None,100,200))
 def test_componentes(self):
  a=c.ler(c.P/'componentes_nominais.csv');self.assertEqual(len(a),7027)
  self.assertEqual(len({r['0_id_componente'] for r in a}),7027)
  self.assertEqual(sum(r['4_elegivel_componente_nominal']=='True' for r in a),2938)
  self.assertEqual(sum(r['4_cabecalho_sem_valor_com_subitens']=='True' for r in a),343)
  self.assertTrue(all(k[:2] in ['0_','1_','2_','3_','4_'] for k in a[0]))
 def test_imea_preserva_celulas(self):
  src=c.ler(c.F/'imea/imea_regional_key_costs.csv')
  lookup={(r['source_file'],r['sheet'],r[k+'_cell']):r[k] for r in src for k in ['coe','cot','ct']}
  out=c.ler(c.P/'custos_imea_referencia.csv');self.assertEqual(len(out),585)
  for r in out:
   self.assertEqual(r['2_custo_brl_declarado_ha'],lookup[r['0_arquivo_xlsx_origem'],r['0_aba'],r['0_celula']])
   self.assertEqual(r['2_custo_usd2024_ha'],'');self.assertEqual(r['4_estrito_comparavel'],'False')
  self.assertEqual(sum(r['2_custo_brl_declarado_ha']=='' for r in out),60)
 def test_imea_suporte(self):
  a=c.ler(c.P/'custos_imea_candidatos_descritivos.csv');self.assertEqual(len(a),195)
  self.assertEqual(len({r['0_id_serie'] for r in a}),65)
  self.assertTrue(all(r['4_rotulo_asterisco_ambiguo']=='False' and int(r['0_safra_fim'])<=2024 for r in a))
  q=c.ler(c.P/'custos_imea_quarentena.csv');self.assertEqual(len(q),585)
  self.assertEqual(len({r['0_id_serie'] for r in q if r['4_rotulo_asterisco_ambiguo']=='True'}),2)
 def test_preservacao_fontes_e_base3(self):
  root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=c.P,text=True).strip())
  for r in json.loads((c.F/'manifesto_entradas.json').read_text()):
   self.assertEqual(c.sha(c.P/r['arquivo']),r['sha256'])
   # origens locais históricas não são dependências: a cópia publicada acima é verificada.
  for name,h in json.loads((c.P/'preservacao_publicacao.json').read_text()).items():
   self.assertEqual(c.sha(root/name),h,name)
if __name__=='__main__':unittest.main()
