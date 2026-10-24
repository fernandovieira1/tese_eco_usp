"""Validação independente por chaves, unidades, máscaras e preservação textual."""
import csv
import hashlib
import json
import math
import unittest
import construir_base3 as b

def ler(path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

class Base3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origem=ler(b.ORIGEM); cls.dados=ler(b.PASTA/'painel_h1_base3_v1.csv')

    def test_integridade(self):
        d=self.dados
        self.assertEqual(hashlib.sha256(b.ORIGEM.read_bytes()).hexdigest(),b.HASH)
        self.assertEqual(len(d),3384); self.assertEqual(len(d[0]),42)
        self.assertEqual(len({(r['codigo_ibge'],r['ano']) for r in d}),3384)
        self.assertEqual(len({r['codigo_ibge'] for r in d}),141)
        self.assertEqual({int(r['ano']) for r in d},set(range(2001,2025)))
        for a,r in zip(self.origem,d):
            self.assertEqual({c:r[c] for c in b.COLUNAS},{c:a[c] for c in b.COLUNAS})
            self.assertTrue(len(r['codigo_ibge'])==7 and r['codigo_ibge'].isdigit())

    def test_unidades_e_dominios(self):
        for r in self.dados:
            for c,v in r.items():
                if not v or v.lower() in ('true','false') or c in ('municipio','bioma_predominante'): continue
                self.assertTrue(math.isfinite(float(v)),c)
                if c!='v2__precip_anomaly_1981_2000': self.assertGreaterEqual(float(v),0,c)
            estoque=float(r['y_nativa_inicial_ha']); self.assertGreater(estoque,0)
            for atividade in ['agricultura','pastagem']:
                h=r['conversao_ha__'+atividade]; t=r['taxa_conversao__'+atividade]
                self.assertEqual(bool(h),bool(t))
                if h:
                    self.assertTrue(0<=float(t)<=1)
                    self.assertAlmostEqual(float(h)/estoque,float(t),places=12)
            shares=[float(r['biome_'+x+'_share_i']) for x in ['amazonia','cerrado','pantanal']]
            self.assertTrue(all(0<=v<=1.00000001 for v in shares))
            self.assertLess(abs(sum(shares)-1),0.002)  # Tolerância cartográfica, sem normalização.
            for c in ['v2__y_fracao_area_valida_par','v2__fracao_pixels_minima']:
                self.assertTrue(0<=float(r[c])<=1.00000001)
            self.assertEqual(r['v2__meses_validos'],'12')
            self.assertEqual(r['v2__meses_cobertura_conhecida'],'12')
            self.assertEqual(r['v2__count_1981_2000'],'20')
            self.assertAlmostEqual(float(r['v2__precip_mm_anual'])-float(r['v2__media_1981_2000']),float(r['v2__precip_anomaly_1981_2000']),places=9)
        for c in [x for x in b.COLUNAS if x.startswith('preco_')]:
            for ano in range(2001,2025):
                vals={r[c] for r in self.dados if int(r['ano'])==ano}
                self.assertEqual(len(vals),1); self.assertGreater(float(next(iter(vals))),0)
        self.assertEqual({int(r['ano'])-1 for r in self.dados},set(range(2000,2024)))

    def test_faltas_zeros_mascaras_lag(self):
        d=self.dados; por_chave={(r['codigo_ibge'],int(r['ano'])):r for r in d}
        for r in d:
            prev=por_chave.get((r['codigo_ibge'],int(r['ano'])-1))
            esperado=''
            if prev and prev[b.AUTO] and float(prev[b.AUTO])>=0 and prev[b.PARCIAL].lower()=='false': esperado=prev[b.AUTO]
            self.assertEqual(r[b.LAG],esperado)
            for nome,valor in [('autos_flora_elegivel_t',b.elegivel(r)),('autos_flora_elegivel_lag1',bool(esperado)),('amostra_fiscal_lag1',bool(esperado) and r['v2__flag_amostra_conversao_ambos']=='True')]:
                self.assertEqual(r['v2__flag_'+nome],str(valor))
        for atividade,zeros in [('agricultura',265),('pastagem',0)]:
            vals=[r['conversao_ha__'+atividade] for r in d]
            self.assertEqual(vals.count(''),612)
            self.assertEqual(sum(float(v)==0 for v in vals if v),zeros)
        for nome,n in [('amostra_conversao_ambos',2772),('autos_flora_elegivel_t',1526),('autos_flora_elegivel_lag1',1444),('amostra_fiscal_lag1',1140),('amostra_conversao_chuva',2772)]:
            self.assertEqual(sum(r['v2__flag_'+nome]=='True' for r in d),n)

    def test_lacunas_parcialidade_zero(self):
        def r(m,a,v,p):return {'codigo_ibge':m,'ano':str(a),b.AUTO:v,b.PARCIAL:p}
        dados=[r('a',2001,'0','False'),r('a',2002,'9','True'),r('a',2003,'4',''),r('a',2004,'2','False'),r('a',2006,'1','False'),r('b',2002,'3','False')]
        self.assertEqual(b.defasar(dados),['','0','','','',''])
        for valor,flag in [('', 'False'),('-1','False'),('NaN','False'),('1','')]:
            self.assertFalse(b.elegivel(r('a',2000,valor,flag)))

if __name__=='__main__': unittest.main(verbosity=2)
