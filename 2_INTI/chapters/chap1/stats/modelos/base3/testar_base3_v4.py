"""Testes de receitas, temporalidade e preservação; sem regressões."""
import json
import math
import subprocess
import unittest
import construir_base3_v4 as b

class Receitas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=b.ler(b.V3);cls.data=b.ler(b.P/'painel_h1_base3_v4.csv')
        cls.lookup={(r['0_codigo_ibge'],int(r['0_ano'])):r for r in cls.data}
        cls.prices={(int(r['ano']),r['cultura']):float(r['preco_contemporaneo_usd2024_t']) for r in b.ler(b.P/'precos_anuais_receitas_v4.csv')}
    def test_preservacao_publicados_e_chaves(self):
        self.assertEqual(len(self.data),3384);self.assertEqual(len(self.lookup),3384)
        self.assertEqual(len(self.data[0]),70);self.assertEqual(len({r['0_codigo_ibge'] for r in self.data}),141)
        self.assertEqual(list(self.data[0]),list(self.original[0])+b.NOVAS)
        for a,r in zip(self.original,self.data):self.assertEqual(a,{c:r[c] for c in a})
        root=b.P.parents[5];commit='0a2cd309ab6b724ccd9266a54deb0f086843e3b9'
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--','2_INTI/chapters/chap1/stats/modelos/base3'],cwd=root,text=True).splitlines()
        for p in paths:self.assertEqual((root/p).read_bytes(),subprocess.check_output(['git','show',commit+':'+p],cwd=root),p)
    def test_identidades_e_precos_contemporaneos(self):
        for r in self.data:
            year=int(r['0_ano'])
            for crop in b.CULTURAS:
                price=self.prices[year,crop];q=b.numero(r['2_producao_t__'+crop]);area=b.numero(r['2_area_colhida_ha__'+crop])
                expected=b.receitas(price,q,area)
                for measure,value in zip(b.MEDIDAS,expected):
                    got=b.numero(r[b.campo(crop,measure)])
                    if value is None:self.assertIsNone(got)
                    else:self.assertTrue(math.isclose(got,value,rel_tol=1e-13,abs_tol=1e-9))
                # Preço contemporâneo t coincide com preço lag1 no outcome t+1.
                if year<2024:
                    nextrow=self.lookup[r['0_codigo_ibge'],year+1]
                    self.assertAlmostEqual(price,float(nextrow['2_preco_real_usd2024_media_anual_lag1__'+crop]),places=9)
        self.assertEqual(len(self.prices),48)
    def test_temporalidade_e_media_estrita(self):
        for r in self.data:
            mun=r['0_codigo_ibge'];year=int(r['0_ano'])
            for crop in b.CULTURAS:
                for measure in b.MEDIDAS:
                    vals=[]
                    for lag in [1,2]:
                        prev=self.lookup.get((mun,year-lag));expected=prev[b.campo(crop,measure)] if prev else ''
                        self.assertEqual(r[b.campo(crop,measure,'lag'+str(lag))],expected)
                        vals.append(b.numero(expected))
                    mean=r[b.campo(crop,measure,'media_lag1_lag2')]
                    if None in vals:self.assertEqual(mean,'')
                    else:self.assertAlmostEqual(float(mean),sum(vals)/2,places=7)
    def test_anos_origem_preco_quantidade(self):
        rows=b.ler(b.P/'rastreamento_anos_receitas_v4.csv');self.assertEqual(len(rows),16*24)
        for r in rows:
            y=int(r['ano_resultado']);c=r['variavel']
            offsets=[1,2] if 'media_lag1_lag2' in c else ([2] if '_lag2__' in c else ([1] if '_lag1__' in c else [0]))
            for component,offset in enumerate(offsets,1):
                self.assertEqual(int(r[f'ano_preco_componente{component}']),y-offset)
                self.assertEqual(r[f'ano_preco_componente{component}'],r[f'ano_quantidade_componente{component}'])
            self.assertEqual(r['usa_coluna_preco_lag1_como_contemporanea'],'False')
            self.assertEqual(r['receita_formada_antes_de_defasar'],'True')
            if any(y-offset<2001 for offset in offsets):
                self.assertTrue(all(x[c]=='' for x in self.data if int(x['0_ano'])==y))

    def test_zeros_lacunas_sem_vazamento(self):
        self.assertEqual(b.receitas(10,0,2),(0,0));self.assertEqual(b.receitas(10,None,2),(None,None))
        self.assertEqual(b.receitas(10,1,0),(10,None))
        values={('A',2001):0,('A',2003):30,('B',2002):99,('A',2005):9999}
        self.assertEqual(b.anteriores(values,'A',2003),(None,0,None))
        self.assertEqual(b.anteriores(values,'A',2004),(30,None,None))
        values['A',2002]=20
        self.assertEqual(b.anteriores(values,'A',2003),(20,0,10))
        values['A',2003]=999999;values['A',2005]=-100
        self.assertEqual(b.anteriores(values,'A',2003),(20,0,10))
    def test_cobertura_metadados(self):
        coverage=b.ler(b.P/'cobertura_receitas_v4.csv');self.assertEqual(len(coverage),16*25)
        for c in b.NOVAS:
            rows=[r for r in coverage if r['variavel']==c];total=next(r for r in rows if r['ano']=='TODOS')
            self.assertEqual(sum(int(r['validos']) for r in rows if r['ano']!='TODOS'),int(total['validos']))
        dic=b.ler(b.P/'dicionario_variaveis_v4.csv');self.assertEqual([r['variavel'] for r in dic],list(self.data[0]))
        self.assertTrue(all(r['grupo']=='2' for r in dic[-16:]))
        m=json.loads((b.P/'manifesto_v4.json').read_text());self.assertEqual(m['sha256_painel'],b.sha(b.P/'painel_h1_base3_v4.csv'))
if __name__=='__main__':unittest.main(verbosity=2)
