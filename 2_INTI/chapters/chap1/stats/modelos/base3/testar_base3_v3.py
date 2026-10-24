"""Verifica preservação, oferta e compatibilidade, sem novos modelos."""
import json
import subprocess
import unittest
import construir_base3_v3 as b

class Oferta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v2=b.ler(b.V2);cls.v3=b.ler(b.P/'painel_h1_base3_v3.csv');cls.source={b.key(r):r for r in b.ler(b.FONTE)}
    def test_chaves_e_preservacao(self):
        self.assertEqual(len(self.v3),3384);self.assertEqual(len(self.v3[0]),54)
        self.assertEqual(len({b.key(r,'0_') for r in self.v3}),3384)
        self.assertEqual(list(self.v3[0]),list(self.v2[0])+['2_'+c for c in b.NOVAS])
        for a,r in zip(self.v2,self.v3):
            self.assertEqual(a,{k:r[k] for k in a})
            for c in b.NOVAS:self.assertEqual(r['2_'+c],self.source[b.key(r,'0_')][c])
    def test_bases_publicadas_intactas(self):
        root=b.P.parents[5]
        prefix='2_INTI/chapters/chap1/stats/modelos/base3/'
        commit='253d059c473d3d5efe1fe74a3c37a46f2ea41678'
        files=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--',prefix],cwd=root,text=True).splitlines()
        self.assertTrue(files)
        for file in files:
            expected=subprocess.check_output(['git','show',commit+':'+file],cwd=root)
            self.assertEqual((root/file).read_bytes(),expected,file)
        self.assertEqual(b.sha(b.FONTE),b.HASH_FONTE);self.assertEqual(b.sha(b.ORIGINAL),b.HASH_ORIGINAL)
    def test_cobertura_e_diagnosticos(self):
        for crop,observados in [('soja',2615),('milho',3318)]:
            for t in b.TIPOS:
                values=[r[f'2_{t}__{crop}'] for r in self.v3]
                self.assertEqual(sum(bool(v) for v in values),observados)
                self.assertEqual(sum(float(v)==0 for v in values if v),0)
        q=b.ler(b.P/'qualidade_produtiva_v3.csv');self.assertEqual(len(q),8*25)
        for c in b.NOVAS:
            rows=[r for r in q if r['variavel']=='2_'+c]
            total=next(r for r in rows if r['ano']=='TODOS')
            self.assertEqual(sum(int(r['validos']) for r in rows if r['ano']!='TODOS'),int(total['validos']))
        for r in b.ler(b.P/'diagnosticos_produtivos_v3.csv'):
            self.assertEqual(int(r['area_colhida_maior_plantada']),0)
            self.assertEqual(int(r['diferencas_acima_1']),0)
            self.assertLessEqual(float(r['max_diferenca_abs_kg_ha']),b.TOL)
        self.assertEqual(b.ler(b.P/'inconsistencias_produtivas_v3.csv'),[])
    def test_metadados(self):
        dic=b.ler(b.P/'dicionario_variaveis_v3.csv')
        self.assertEqual([r['variavel'] for r in dic],list(self.v3[0]))
        self.assertTrue(all(r['grupo']=='2' for r in dic[-8:]))
        m=json.loads((b.P/'manifesto_v3.json').read_text())
        self.assertEqual(m['sha256_painel'],b.sha(b.P/'painel_h1_base3_v3.csv'))
        self.assertEqual(m['auditoria_pre_join_sha256'],b.sha(b.P/'auditoria_pre_join_v3.json'))
if __name__=='__main__':unittest.main(verbosity=2)
