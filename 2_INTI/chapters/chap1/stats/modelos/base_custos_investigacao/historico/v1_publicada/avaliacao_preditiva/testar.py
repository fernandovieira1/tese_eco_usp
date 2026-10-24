import unittest,tempfile,json,hashlib
from pathlib import Path
import avaliar as a
class Test(unittest.TestCase):
 def test_ols_e_ridge_analiticos(self):
  train=[{'x':x,'y':10+3*x} for x in range(12)]
  par=a.fit(train,'M1_ols');self.assertAlmostEqual(a.predict(par,20),70)
  shr=a.fit(train,'M2_ridge');self.assertLess(abs(shr[1]),abs(par[1]))
  self.assertAlmostEqual(a.predict(shr,5.5),26.5)
 def test_linhagem_e_moeda(self):
  for crop,n in [('soja',32),('milho_1a',9),('milho_2a',44)]:
   rows=a.read(a.P/crop/'amostra.csv');self.assertEqual(len(rows),n)
   self.assertEqual(len({r['id'] for r in rows}),n)
   for r in rows:self.assertEqual(int(r['ano_origem_dap']),int(r['ano_data_base'])-1);self.assertEqual(int(r['n_meses']),12)
 def test_separacao_folds(self):
  for crop in ['soja','milho_2a']:
   rows=a.read(a.P/crop/'membros_folds.csv')
   for axis,block in {(r['eixo'],r['bloco']) for r in rows}:
    tr=[r for r in rows if r['eixo']==axis and r['bloco']==block and r['papel']=='treino'];te=[r for r in rows if r['eixo']==axis and r['bloco']==block and r['papel']=='teste']
    self.assertFalse({r['id'] for r in tr}&{r['id'] for r in te})
    if axis=='temporal':self.assertLess(max(int(r['ano']) for r in tr),min(int(r['ano']) for r in te))
    else:self.assertFalse({r['praca'] for r in tr}&{r['praca'] for r in te})
   pred=a.read(a.P/crop/'previsoes_holdout.csv')
   keys=[{(r['eixo'],r['bloco'],r['id']) for r in pred if r['modelo']==m} for m in ['B0_media_regional','M1_ols','M2_ridge']]
   self.assertEqual(keys[0],keys[1]);self.assertEqual(keys[1],keys[2])
 def test_holdout_nao_altera_parametros(self):
  for crop in ['soja','milho_2a']:
   sample=a.read(a.P/crop/'amostra.csv');lookup={r['id']:dict(r,x=float(r['x']),y=float(r['y'])) for r in sample}
   mem=a.read(a.P/crop/'membros_folds.csv')
   for p in a.read(a.P/crop/'parametros_treino.csv'):
    tr=[lookup[r['id']] for r in mem if r['eixo']==p['eixo'] and r['bloco']==p['bloco'] and r['papel']=='treino']
    par=a.fit(tr,p['modelo'])
    for x,key in zip(par,['intercepto','beta_x_padronizado','media_x_treino','sd_x_treino']):self.assertAlmostEqual(x,float(p[key]))
 def test_recusa_primeira_safra(self):
  self.assertEqual((a.P/'milho_1a/previsoes_holdout.csv').read_text(),'')
  self.assertFalse(json.loads((a.P/'milho_1a/resumo.json').read_text())['suporte_teste'])
 def test_preservacao(self):
  root=a.MODELOS.parents[4]
  # Locate repository explicitly from tracked AGENTS.md.
  root=next(p for p in a.P.parents if (p/'AGENTS.md').exists())
  for f,h in json.loads((a.BASE/'preservacao_publicacao.json').read_text()).items():self.assertEqual(a.sha(root/f),h,f)
 def test_reproducao_dupla(self):
  for crop in a.CROPS:
   expected=json.loads((a.P/crop/'manifesto.json').read_text())['outputs']
   for i in range(2):
    with tempfile.TemporaryDirectory() as d:
     a.run(crop,Path(d))
     self.assertEqual({f.name:a.sha(f) for f in Path(d).glob('*.csv')},expected)
if __name__=='__main__':unittest.main()
